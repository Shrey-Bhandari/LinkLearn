import json
import logging
from typing import List, Optional
from .models import MCQ, Note, PipelineResult
from .scraper import PageContent, URLScraper, ScraperError
from .chunker import SemanticChunker
from .semantic import EmbeddingStore
from .graph import KnowledgeGraphBuilder
from .groq_client import GroqClient
from .concept_extractor import ConceptExtractor, ConceptExtractionMode, chunks_to_flashcards


logger = logging.getLogger("link2learn")
logging.basicConfig(level=logging.INFO)


class Link2LearnPipeline:
    """Pipeline for converting educational web links into learning artifacts."""

    def __init__(
        self,
        use_groq: bool = False,
        similarity_threshold: float = 0.78,
        groq_model: Optional[str] = None,
    ):
        self.scraper = URLScraper()
        self.chunker = SemanticChunker()
        self.embedding_store = EmbeddingStore()
        self.graph_builder = KnowledgeGraphBuilder(self.embedding_store, similarity_threshold)
        self.use_groq = use_groq and bool(GroqClient().api_key)
        self.groq_client = None
        if self.use_groq:
            self.groq_client = GroqClient(model=groq_model)
            logger.info("Groq API enabled for note, flashcard, and MCQ generation")
        else:
            if use_groq:
                logger.warning("Groq API key not found; falling back to heuristic generation")

    def process_urls(self, urls: List[str]) -> PipelineResult:
        """Process a set of educational URLs into structured learning artifacts."""
        if not urls:
            raise ValueError("At least one URL is required")

        pages: List[PageContent] = []
        all_chunks = []
        errors = []

        for url in urls:
            try:
                page = self.scraper.scrape_url(url)
                pages.append(page)
                all_chunks.extend(self.chunker.chunk(page))
            except ScraperError as exc:
                logger.error("Failed to scrape %s: %s", url, exc)
                errors.append({"url": url, "error": str(exc)})

        if not all_chunks:
            raise ValueError("No semantic chunks could be constructed from provided URLs")

        self.embedding_store.index_chunks(all_chunks)
        graph = self.graph_builder.build(all_chunks)
        notes = self._build_notes(pages)
        flashcards = self._build_flashcards(all_chunks)
        mcqs = self._build_mcqs(notes)

        pipeline_result = PipelineResult(
            notes=notes,
            graph=graph,
            flashcards=flashcards,
            mcqs=mcqs,
        )

        if errors:
            logger.warning("Some URLs failed to process: %s", errors)

        return pipeline_result

    def process_html(self, html: str, source_url: str = "https://source.local") -> PipelineResult:
        """Process raw HTML and return the Link2Learn pipeline result."""
        if not html or not html.strip():
            raise ValueError("HTML content cannot be empty")

        page = self.scraper.extract_content(html)
        page.url = source_url
        all_chunks = self.chunker.chunk(page)
        if not all_chunks:
            raise ValueError("No semantic chunks could be constructed from provided HTML")

        self.embedding_store.index_chunks(all_chunks)
        graph = self.graph_builder.build(all_chunks)
        notes = self._build_notes([page])
        flashcards = self._build_flashcards(all_chunks)
        mcqs = self._build_mcqs(notes)

        return PipelineResult(notes=notes, graph=graph, flashcards=flashcards, mcqs=mcqs)

    def _build_notes(self, pages: List[PageContent]) -> List[Note]:
        notes: List[Note] = []
        for page in pages:
            structured = self._extract_structured_concepts(page)
            notes.extend(self._notes_from_concepts(structured, page))
        return notes

    def _extract_structured_concepts(self, page: PageContent):
        extractor = ConceptExtractor("", mode=ConceptExtractionMode.HEURISTIC)
        sections = [
            {"heading": section.heading, "content": section.content}
            for section in page.sections
        ]
        return extractor.extract(sections=sections)

    def _notes_from_concepts(self, structured, page: PageContent) -> List[Note]:
        notes: List[Note] = []
        for concept in structured.concepts:
            heading = concept.name.strip()
            if not heading or not concept.definition:
                continue

            topic_hierarchy = [page.title] if page.title else []
            notes.append(
                Note(
                    heading=heading,
                    definition=concept.definition,
                    key_points=concept.key_points,
                    example=concept.example,
                    source_url=page.url,
                    topic_hierarchy=topic_hierarchy,
                )
            )
        return notes

    def _build_flashcards(self, chunks: List) -> List:
        if self.use_groq and self.groq_client:
            try:
                return self._generate_flashcards_with_groq(chunks)
            except Exception as exc:
                logger.warning("Groq flashcard generation failed: %s", exc)
        return chunks_to_flashcards([chunk.model_dump() for chunk in chunks])["flashcards"]

    def _build_mcqs(self, notes: List[Note]) -> List[MCQ]:
        if self.use_groq and self.groq_client:
            try:
                return self._generate_mcqs_with_groq(notes)
            except Exception as exc:
                logger.warning("Groq MCQ generation failed: %s", exc)
        return self._build_mcqs_heuristic(notes)

    def _build_mcqs_heuristic(self, notes: List[Note]) -> List[MCQ]:
        mcqs: List[MCQ] = []
        candidates = [note for note in notes if note.definition and len(note.definition.split()) >= 8]

        for note in candidates:
            correct_text = note.definition
            pool = [other.definition for other in notes if other.heading != note.heading and other.definition]
            if len(pool) < 3:
                pool.extend(["No analogous concept was found."])

            distractors = sorted(pool, key=lambda text: abs(len(text) - len(correct_text)))[:3]
            if len(distractors) < 3:
                continue

            options = [correct_text] + distractors
            options = sorted(options, key=str)
            correct_key = "ABCD"[options.index(correct_text)]
            difficulty = self._estimate_difficulty(note)
            mcqs.append(
                MCQ(
                    question=f"Which statement best describes {note.heading}?",
                    options=options,
                    correct=correct_key,
                    difficulty=difficulty,
                )
            )
            if len(mcqs) >= 12:
                break

        return mcqs

    def _estimate_difficulty(self, note: Note) -> str:
        if len(note.key_points) >= 3 or note.example:
            return "Hard"
        if len(note.key_points) >= 1 or len(note.definition) > 120:
            return "Medium"
        return "Easy"

    def _generate_flashcards_with_groq(self, chunks: List) -> List[dict]:
        prompt = self._build_flashcard_prompt(chunks)
        response = self.groq_client.request(prompt, max_tokens=600)
        return self._parse_json_array(response)

    def _generate_mcqs_with_groq(self, notes: List[Note]) -> List[MCQ]:
        prompt = self._build_mcq_prompt(notes)
        response = self.groq_client.request(prompt, max_tokens=800)
        raw_mcqs = self._parse_json_array(response)
        mcqs: List[MCQ] = []
        for item in raw_mcqs:
            if not item:
                continue
            mcqs.append(MCQ(**item))
        return mcqs

    def _build_flashcard_prompt(self, chunks: List) -> str:
        chunk_text = "\n\n".join(
            f"Concept: {chunk.concept}\nContent: {chunk.content}" for chunk in chunks[:10]
        )
        return f"""
Generate exam-oriented flashcards from the following concept chunks.

Return valid JSON in the format:
{{"flashcards": [{{"question":"...","answer":"...","type":"definition"}}]}}

Avoid trivial Q/A. Use definition, concept, and application styles.

{chunk_text}
""".strip()

    def _build_mcq_prompt(self, notes: List[Note]) -> str:
        notes_text = "\n\n".join(
            f"Concept: {note.heading}\nDefinition: {note.definition}\nKey points: {', '.join(note.key_points)}"
            for note in notes[:8]
        )
        return f"""
Generate exam-quality multiple-choice questions from the following notes.

For each concept, create one MCQ with exactly one correct answer, three plausible distractors, and a difficulty label.
Return valid JSON in the format:
{{"mcqs": [{{"question":"...","options":["A","B","C","D"],"correct":"A","difficulty":"Easy"}}]}}

{notes_text}
""".strip()

    def _parse_json_array(self, text: str) -> list:
        try:
            return json.loads(text).get("flashcards") or json.loads(text).get("mcqs") or []
        except json.JSONDecodeError:
            try:
                body = text[text.index("{"):]
                parsed = json.loads(body)
                return parsed.get("flashcards") or parsed.get("mcqs") or []
            except Exception:
                return []
