"""Academic concept structuring engine."""

import re
from typing import Optional
from pydantic import BaseModel
from enum import Enum


class ConceptExtractionMode(str, Enum):
    """Available extraction modes."""
    HEURISTIC = "heuristic"
    LLM = "llm"
    HYBRID = "hybrid"


class KeyPoint(BaseModel):
    """A key point within a concept."""
    text: str
    order: int = 0


class Concept(BaseModel):
    """Represents an academic concept."""
    name: str
    definition: str
    key_points: list[str] = []
    example: Optional[str] = None
    prerequisites: list[str] = []
    related_concepts: list[str] = []


class StructuredConcepts(BaseModel):
    """Collection of extracted concepts."""
    concepts: list[Concept] = []
    source_title: Optional[str] = None
    total_concepts: int = 0


class ConceptExtractor:
    """Extract academic concepts from educational content."""
    
    # Patterns for identifying definitions
    DEFINITION_PATTERNS = [
        r'is\s+(?:a|an)\s+(.+?)(?:\.|;|,)',
        r'can\s+be\s+defined\s+as\s+(.+?)(?:\.|;)',
        r'refers\s+to\s+(.+?)(?:\.|;)',
        r'means\s+(.+?)(?:\.|;)',
        r'is\s+(.+?)(?:\.|;)',
    ]
    
    # Patterns for identifying examples
    EXAMPLE_PATTERNS = [
        r'(?:for\s+)?example[:\s]+(.+?)(?:\.|$)',
        r'(?:such\s+as|like)[:\s]+(.+?)(?:\.|$)',
        r'(?:e\.g\.|etc\.)[:\s]+(.+?)(?:\.|$)',
        r'examples?[:\s]+(.+?)(?:\.|$)',
    ]
    
    # Patterns for identifying prerequisites
    PREREQUISITE_PATTERNS = [
        r'(?:requires|requires knowledge of|prerequisite)[:\s]+(.+?)(?:\.|;)',
        r'(?:before|prior to)[:\s]+(.+?)(?:,|;)',
        r'(?:first|initially)[:\s]+(.+?)(?:\.|;)',
    ]
    
    # Sentence enders
    SENTENCE_ENDERS = r'(?<=[.!?;])\s+'
    
    def __init__(self, content: str, mode: ConceptExtractionMode = ConceptExtractionMode.HEURISTIC):
        """Initialize concept extractor."""
        self.content = content
        self.mode = mode
        self.concepts: dict[str, Concept] = {}
    
    def _extract_sentences(self) -> list[str]:
        """Split content into sentences."""
        sentences = re.split(self.SENTENCE_ENDERS, self.content)
        return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
    
    def _extract_concept_name(self, sentence: str) -> Optional[str]:
        """Extract potential concept name from sentence."""
        # Look for capitalized words or terms in bold/emphasis
        words = sentence.split()
        
        # First word (often topic)
        if words and words[0][0].isupper():
            return words[0].rstrip('.,;:')
        
        # Look for all-caps terms (acronyms)
        caps_terms = [w for w in words if w.isupper() and len(w) > 1]
        if caps_terms:
            return caps_terms[0]
        
        # Look for multi-word capitalized phrases
        if len(words) >= 2:
            phrase = ' '.join([w for w in words[:3] if w[0].isupper()])
            if phrase:
                return phrase.rstrip('.,;:')
        
        return None
    
    def _extract_definition(self, text: str, concept_name: Optional[str] = None) -> Optional[str]:
        """Extract definition from text."""
        for pattern in self.DEFINITION_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                definition = match.group(1).strip()
                # Remove excessive content after definition
                if len(definition) > 300:
                    definition = definition[:297] + '...'
                return definition
        return None
    
    def _extract_examples(self, text: str) -> list[str]:
        """Extract examples from text."""
        examples = []
        for pattern in self.EXAMPLE_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                example = match.group(1).strip()
                # Clean up example
                example = re.sub(r'[\s]+', ' ', example)
                if 10 < len(example) < 500:
                    examples.append(example)
        return examples
    
    def _extract_prerequisites(self, text: str) -> list[str]:
        """Extract prerequisites from text."""
        prerequisites = []
        for pattern in self.PREREQUISITE_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                prereq = match.group(1).strip()
                if prereq and len(prereq) < 100:
                    prerequisites.append(prereq)
        return prerequisites
    
    def _extract_key_points(self, concept_sentences: list[str], concept_name: str) -> list[str]:
        """Extract key points about a concept."""
        key_points = []
        
        # Handle both list of sentences and single string
        if isinstance(concept_sentences, str):
            concept_sentences = concept_sentences.split('.')
        
        # Look for lists with bullets or numbers
        for sentence in concept_sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Check for numbered or bulleted lists
            if re.match(r'^\d+\)|^[-•*]\s|^\d+\)', sentence):
                point = re.sub(r'^[\d.)•*-]\s*', '', sentence).strip()
                if point:
                    key_points.append(point)
            # Check for descriptive statements
            elif len(sentence) > 20 and len(key_points) < 5:
                # Avoid definition sentences
                if not any(p in sentence.lower() for p in ['is ', 'are ', 'refers to', 'means']):
                    key_points.append(sentence)
        
        return key_points[:5]  # Limit to 5 key points
    
    def _identify_concepts_from_headings(self, sections: list[dict]) -> list[str]:
        """Identify concepts from section headings."""
        concepts = []
        for section in sections:
            heading = section.get('heading', '').strip()
            if heading and len(heading) < 100:
                concepts.append(heading)
        return concepts
    
    def extract_heuristic(self, sections: Optional[list[dict]] = None) -> StructuredConcepts:
        """Extract concepts using heuristic-based approach."""
        result = StructuredConcepts()
        
        # If sections are provided, use them directly
        if sections:
            result.source_title = sections[0].get('heading') if sections else None
            
            for section in sections:
                heading = section.get('heading', '').strip()
                content = section.get('content', '').strip()
                
                if not heading or not content:
                    continue
                
                # Use heading as concept name
                concept_name = heading
                
                # Extract definition from content
                definition = self._extract_definition(content, concept_name)
                if not definition:
                    # Use first sentence as definition
                    sentences = content.split('.')
                    if sentences and sentences[0]:
                        definition = sentences[0].strip() + '.'
                
                # Extract examples and prerequisites
                examples = self._extract_examples(content)
                prerequisites = self._extract_prerequisites(content)
                
                # Extract key points
                key_points = self._extract_key_points(content.split('.'), concept_name)
                
                # Build concept
                if definition:
                    concept = Concept(
                        name=concept_name,
                        definition=definition,
                        key_points=key_points,
                        example=examples[0] if examples else None,
                        prerequisites=prerequisites
                    )
                    
                    self.concepts[concept_name] = concept
                    result.concepts.append(concept)
        else:
            # Process raw content without sections
            sentences = self._extract_sentences()
            concept_names = set()
            
            for i, sentence in enumerate(sentences):
                # Try to extract concept name
                concept_name = self._extract_concept_name(sentence)
                if not concept_name or concept_name in concept_names:
                    continue
                
                concept_names.add(concept_name)
                
                # Extract definition
                definition = self._extract_definition(sentence, concept_name)
                if not definition:
                    # Look in nearby sentences
                    nearby = ' '.join(sentences[max(0, i-1):min(len(sentences), i+2)])
                    definition = self._extract_definition(nearby, concept_name)
                
                if definition:
                    # Extract examples and prerequisites
                    examples = self._extract_examples(sentence)
                    prerequisites = self._extract_prerequisites(sentence)
                    
                    # Build concept
                    concept = Concept(
                        name=concept_name,
                        definition=definition,
                        key_points=self._extract_key_points(sentences[i:i+3], concept_name),
                        example=examples[0] if examples else None,
                        prerequisites=prerequisites
                    )
                    
                    self.concepts[concept_name] = concept
                    result.concepts.append(concept)
        
        result.total_concepts = len(result.concepts)
        return result
    
    def extract_with_llm(self, sections: list[dict]) -> StructuredConcepts:
        """Extract concepts using LLM (requires API configuration)."""
        # This requires external LLM configuration
        # For now, fall back to heuristic
        import os
        
        # Check for API configuration
        has_openai = os.getenv('OPENAI_API_KEY')
        has_anthropic = os.getenv('ANTHROPIC_API_KEY')
        
        if has_anthropic:
            return self._extract_with_anthropic(sections)
        elif has_openai:
            return self._extract_with_openai(sections)
        else:
            # Fall back to heuristic
            return self.extract_heuristic(sections)
    
    def _extract_with_anthropic(self, sections: list[dict]) -> StructuredConcepts:
        """Extract using Anthropic Claude API."""
        try:
            from anthropic import Anthropic
        except ImportError:
            # Fall back if library not installed
            return self.extract_heuristic(sections)
        
        client = Anthropic()
        
        # Build context from sections
        context = '\n\n'.join(
            f"# {s.get('heading', 'Content')}\n{s.get('content', '')}"
            for s in sections[:5]  # Limit to 5 sections for context
        )
        
        prompt = f"""
Analyze the following educational content and extract atomic academic concepts.

For each concept, provide:
1. Concept name (concise, single idea)
2. Definition (one sentence)
3. Key points (2-4 bullet points)
4. Example (if present in content)
5. Prerequisites (if any)
6. Related concepts (if any)

Content:
{context}

Return as valid JSON with this structure:
{{
  "concepts": [
    {{
      "name": "...",
      "definition": "...",
      "key_points": ["...", "..."],
      "example": "...",
      "prerequisites": ["..."],
      "related_concepts": ["..."]
    }}
  ]
}}

Rules:
- Each concept must be atomic (one idea only)
- Definitions should be clear and exam-relevant
- Key points should be concise facts
- Do not summarize; extract directly
- Do not invent information not in content
"""
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Parse response
        import json
        try:
            response_text = response.content[0].text
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                result = StructuredConcepts(**data)
                result.source_title = sections[0].get('heading') if sections else None
                return result
        except (json.JSONDecodeError, KeyError, IndexError):
            # Fall back to heuristic if parsing fails
            pass
        
        return self.extract_heuristic(sections)
    
    def _extract_with_openai(self, sections: list[dict]) -> StructuredConcepts:
        """Extract using OpenAI GPT API."""
        try:
            from openai import OpenAI
        except ImportError:
            return self.extract_heuristic(sections)
        
        client = OpenAI()
        
        # Build context
        context = '\n\n'.join(
            f"# {s.get('heading', 'Content')}\n{s.get('content', '')}"
            for s in sections[:5]
        )
        
        prompt = f"""
Extract atomic academic concepts from this educational content:

{context}

Return JSON:
{{
  "concepts": [
    {{
      "name": "Concept name",
      "definition": "Definition",
      "key_points": ["point1", "point2"],
      "example": "Example or null",
      "prerequisites": ["prereq"],
      "related_concepts": ["related"]
    }}
  ]
}}

Requirements:
- Atomic concepts only (one idea each)
- Exam-relevant content
- No summarization
- No invented information
"""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        
        # Parse response
        import json
        try:
            response_text = response.choices[0].message.content
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                result = StructuredConcepts(**data)
                result.source_title = sections[0].get('heading') if sections else None
                return result
        except (json.JSONDecodeError, KeyError, IndexError, AttributeError):
            pass
        
        return self.extract_heuristic(sections)
    
    def extract(self, sections: Optional[list[dict]] = None) -> StructuredConcepts:
        """Main extraction method."""
        if self.mode == ConceptExtractionMode.LLM:
            if sections:
                return self.extract_with_llm(sections)
            else:
                # Can't use LLM without structured sections
                return self.extract_heuristic()
        elif self.mode == ConceptExtractionMode.HYBRID:
            # Try LLM first, fall back to heuristic
            if sections:
                try:
                    return self.extract_with_llm(sections)
                except Exception:
                    return self.extract_heuristic(sections)
            else:
                return self.extract_heuristic()
        else:
            # Heuristic mode (default)
            return self.extract_heuristic(sections)
