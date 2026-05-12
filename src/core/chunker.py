import re
from hashlib import sha256
from typing import List
from .models import ConceptChunk
from .scraper import PageContent, SectionData


class SemanticChunker:
    """Convert extracted page sections into semantic concept chunks."""

    def chunk(self, page_content: PageContent) -> List[ConceptChunk]:
        chunks: List[ConceptChunk] = []
        heading_stack: List[SectionData] = []

        for section in page_content.sections:
            if section.level is not None:
                while heading_stack and heading_stack[-1].level >= section.level:
                    heading_stack.pop()
                heading_stack.append(section)

            topic_hierarchy = [node.heading for node in heading_stack[:-1]]
            chunks.extend(self._chunk_section(section, page_content.url, topic_hierarchy))

        return chunks

    def _chunk_section(
        self,
        section: SectionData,
        source_url: str,
        topic_hierarchy: List[str],
    ) -> List[ConceptChunk]:
        content = self._normalize_content(section.content)
        if not content:
            return []

        concept_name = section.heading or content.split('.')[0].strip()
        if not concept_name:
            return []

        chunk_id = sha256(f"{source_url}|{concept_name}|{content[:120]}".encode("utf-8")).hexdigest()[:16]

        return [
            ConceptChunk(
                id=chunk_id,
                heading=section.heading,
                concept=concept_name,
                content=content,
                source_url=source_url,
                topic_hierarchy=topic_hierarchy,
            )
        ]

    def _normalize_content(self, content: str) -> str:
        if not content:
            return ""
        normalized = re.sub(r"\s+", " ", content).strip()
        return normalized
