# Academic Structuring Engine - Implementation Guide

## Overview

The Academic Structuring Engine transforms cleaned educational content into atomic academic concepts with structured metadata (definitions, key points, examples, prerequisites, and relationships).

## Architecture

The system has three extraction modes:

### 1. Heuristic Mode (Default)

- **Speed**: Fast (pattern-based)
- **Dependencies**: None
- **Accuracy**: Good for well-structured content
- **Use Case**: Local processing, no API keys needed

**Pattern Matching:**

- Definitions: `"is a|is an|is defined as|refers to|means"`
- Examples: `"for example|such as|e.g.|like"`
- Prerequisites: `"requires|prerequisite|before|first"`
- Key Points: Lists with numbers/bullets

### 2. LLM Mode (AI-Powered)

- **Speed**: Slower (API call)
- **Dependencies**: Anthropic or OpenAI API key
- **Accuracy**: Excellent (understands context)
- **Use Case**: Production systems, complex content

**Supported Providers:**

- Claude (Anthropic) - Recommended
- GPT-4 (OpenAI)

### 3. Hybrid Mode (Smart Fallback)

- **Behavior**: Tries LLM first, falls back to heuristic
- **Advantage**: Best of both worlds
- **Configuration**: Set via `/modes` endpoint

## API Endpoints

### 1. Extract Content

```
POST /extract
```

Extract educational content from HTML:

```bash
curl -X POST http://localhost:8000/extract \
  -H "Content-Type: application/json" \
  -d '{"html": "<html>...</html>"}'
```

### 2. Structure Concepts

```
POST /structure-concepts
```

Extract concepts from pre-extracted sections:

```bash
curl -X POST http://localhost:8000/structure-concepts \
  -H "Content-Type: application/json" \
  -d '{
    "sections": [
      {"heading": "Photosynthesis", "content": "..."},
      {"heading": "Light Reactions", "content": "..."}
    ],
    "mode": "heuristic"
  }'
```

### 3. Extract & Structure (Pipeline)

```
POST /extract-and-structure
```

Complete pipeline in one call:

```bash
curl -X POST http://localhost:8000/extract-and-structure \
  -H "Content-Type: application/json" \
  -d '{"html": "<html>...</html>"}'
```

### 4. Get Available Modes

```
GET /modes
```

See available extraction modes and their descriptions.

## Output Format

### Response Structure

```json
{
  "concepts": [
    {
      "name": "Concept Name",
      "definition": "Clear one-sentence definition",
      "key_points": ["Main idea 1", "Main idea 2", "Main idea 3"],
      "example": "Concrete example from the content or null",
      "prerequisites": ["Prior knowledge needed"],
      "related_concepts": ["Connected concepts"]
    }
  ],
  "source_title": "Title of source material",
  "total_concepts": 5
}
```

## Concept Quality Metrics

### Atomicity ✓

- One idea per concept
- Concept names < 150 characters
- Single aspect of knowledge

### Exam Relevance ✓

- Foundational knowledge included
- Key facts extracted
- Exam-typical formulations

### No Loose Summarization ✓

- Direct extraction, not paraphrase
- Original terminology preserved
- No information synthesis

### Definitions

- Extracted from content
- Clear and concise
- 1-2 sentences maximum

### Key Points

- 2-5 points per concept
- Bulleted/numbered list format
- Specific facts or procedures

## Configuration

### Environment Variables (for LLM mode)

```bash
# Anthropic Claude
export ANTHROPIC_API_KEY="sk-ant-..."

# OpenAI GPT
export OPENAI_API_KEY="sk-..."
```

### Mode Selection

```python
from concept_extractor import ConceptExtractor, ConceptExtractionMode

# Heuristic (fast, no API)
extractor = ConceptExtractor(content, mode=ConceptExtractionMode.HEURISTIC)

# LLM-based (slow, better quality, requires API)
extractor = ConceptExtractor(content, mode=ConceptExtractionMode.LLM)

# Hybrid (tries LLM, falls back to heuristic)
extractor = ConceptExtractor(content, mode=ConceptExtractionMode.HYBRID)
```

## Python Usage

### Basic Extraction

```python
from extractor import ContentExtractor
from concept_extractor import ConceptExtractor, ConceptExtractionMode

# Step 1: Extract content
content_extractor = ContentExtractor(html_content)
extracted = content_extractor.extract()

# Step 2: Structure concepts
sections = [
    {"heading": s.heading, "content": s.content}
    for s in extracted.sections
]

concept_extractor = ConceptExtractor("", mode=ConceptExtractionMode.HEURISTIC)
concepts = concept_extractor.extract(sections=sections)

# Step 3: Access results
for concept in concepts.concepts:
    print(f"Name: {concept.name}")
    print(f"Definition: {concept.definition}")
    print(f"Key Points: {', '.join(concept.key_points)}")
```

### Using the API Client

```python
import requests

# Extract from URL
response = requests.post(
    "http://localhost:8000/extract-and-structure",
    json={"html": "<html>...</html>"}
)

result = response.json()
concepts = result["structured_concepts"]["concepts"]
```

## Test Coverage

**37 Total Tests** - All Passing ✓

### Concept Extractor Tests (19)

- Initialization and configuration
- Heuristic extraction accuracy
- Definition, example, prerequisite extraction
- Atomicity verification
- Response format validation
- Exam relevance checking
- No-summarization verification
- Multiple extraction modes

### API Integration Tests (18)

- Concept structuring endpoints
- Response format validation
- Error handling
- Mode validation
- Pipeline testing
- Atomicity verification
- Exam relevance checking

## Constraints Met

✅ **Atomic Concepts** - One idea per concept
✅ **Exam Relevance** - Foundational knowledge
✅ **No Loose Summarization** - Direct extraction
✅ **Structured Output** - JSON with required fields
✅ **Multiple Modes** - Heuristic, LLM, Hybrid
✅ **Advanced Features** - Prerequisites & relationships
✅ **API Integration** - Full REST API
✅ **Comprehensive Testing** - 37 tests

## Performance Considerations

| Mode      | Speed    | API Calls | Accuracy  | Cost   |
| --------- | -------- | --------- | --------- | ------ |
| Heuristic | ~10ms    | 0         | Good      | Free   |
| LLM       | ~1-2s    | 1         | Excellent | $$$    |
| Hybrid    | ~10ms-2s | 0-1       | Excellent | Varies |

## Example Concepts Extracted

### From Photosynthesis Content

```json
{
  "name": "Photosynthesis",
  "definition": "process used by plants to convert light energy into chemical energy",
  "key_points": [
    "Occurs in leaves of plants",
    "Essential for life on Earth",
    "Happens in two main stages"
  ],
  "example": "Plants use sunlight to make glucose",
  "prerequisites": ["Understanding of energy"],
  "related_concepts": ["Light reactions", "Calvin cycle"]
}
```

### From Machine Learning Content

```json
{
  "name": "Supervised Learning",
  "definition": "machine learning approach using labeled training data",
  "key_points": [
    "Requires both inputs and outputs",
    "Algorithm learns input-to-output mapping",
    "Used for classification and regression"
  ],
  "example": "Predicting house prices from historical data",
  "prerequisites": ["Basic ML concepts"],
  "related_concepts": ["Unsupervised learning", "Reinforcement learning"]
}
```

## Troubleshooting

### No concepts extracted

- **Heuristic Mode**: Content may lack clear definitions. Try LLM mode.
- **LLM Mode**: Check API key and network connectivity.
- **Solution**: Verify content has clear definitions and explanations.

### Low-quality concepts

- **Issue**: Vague or overly broad concepts
- **Solution**: Use LLM mode for better understanding of context
- **Alternative**: Improve source content structure

### API timeout

- **Heuristic Mode**: < 100ms per request (should not timeout)
- **LLM Mode**: 1-5s depending on content length
- **Solution**: Increase timeout for LLM mode

## Future Enhancements

- [ ] Table extraction and structure
- [ ] Formula and equation preservation
- [ ] Code block identification
- [ ] Citation and reference extraction
- [ ] Concept relationship mapping
- [ ] Pre-requisite chain generation
- [ ] Difficulty level classification
- [ ] Multi-language support
- [ ] Custom extraction rules
- [ ] Export to Anki/Quizlet formats

## Data Model

### Concept

```python
class Concept(BaseModel):
    name: str                      # Concept title
    definition: str                # Clear definition
    key_points: list[str]          # Main ideas
    example: Optional[str]         # Example from content
    prerequisites: list[str]       # Prior knowledge
    related_concepts: list[str]    # Connected ideas
```

### StructuredConcepts

```python
class StructuredConcepts(BaseModel):
    concepts: list[Concept]        # List of concepts
    source_title: Optional[str]    # Source material title
    total_concepts: int            # Count of concepts
```

## License

MIT

## Support

For issues or questions:

- Check README.md for detailed documentation
- Review test files for usage examples
- See QUICKSTART.md for common tasks
