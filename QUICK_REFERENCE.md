# Quick Reference Card

## Start the API Server

```bash
cd LinkLearn
python main.py
# API at http://localhost:8000/docs
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Run Tests

```bash
pytest -v              # All tests
pytest -q              # Quiet mode
pytest test_api.py     # API only
```

---

## API Endpoints

### Extract & Structure (Complete Pipeline)

```
POST /extract-and-structure
{
  "html": "<html>...</html>"
}
```

### Extract Content Only

```
POST /extract
{
  "html": "<html>...</html>"
}
```

### Structure Concepts Only

```
POST /structure-concepts
{
  "sections": [{"heading": "...", "content": "..."}],
  "mode": "heuristic"
}
```

### Get Available Modes

```
GET /modes
```

### Health Check

```
GET /health
```

---

## Response Formats

### Extraction Response

```json
{
  "title": "Page Title",
  "sections": [
    {
      "heading": "Heading",
      "content": "Content text..."
    }
  ]
}
```

### Concept Response

```json
{
  "concepts": [
    {
      "name": "Concept Name",
      "definition": "Definition here",
      "key_points": ["point1", "point2"],
      "example": "Example text",
      "prerequisites": ["prior knowledge"],
      "related_concepts": ["related concept"]
    }
  ],
  "total_concepts": 5
}
```

---

## Extraction Modes

### Heuristic (Default - No API)

```bash
curl -X POST http://localhost:8000/structure-concepts \
  -H "Content-Type: application/json" \
  -d '{
    "sections": [...],
    "mode": "heuristic"
  }'
```

### LLM Mode (AI-Powered - Requires API Key)

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
curl -X POST http://localhost:8000/structure-concepts \
  -H "Content-Type: application/json" \
  -d '{
    "sections": [...],
    "mode": "llm"
  }'
```

### Hybrid Mode (Smart Fallback)

```bash
curl -X POST http://localhost:8000/structure-concepts \
  -H "Content-Type: application/json" \
  -d '{
    "sections": [...],
    "mode": "hybrid"
  }'
```

---

## Python Usage

### Direct Extraction

```python
from extractor import ContentExtractor

extractor = ContentExtractor(html)
result = extractor.extract()
print(result.title)
for section in result.sections:
    print(f"{section.heading}: {section.content}")
```

### Concept Extraction

```python
from concept_extractor import ConceptExtractor, ConceptExtractionMode

sections = [{"heading": "...", "content": "..."}]
extractor = ConceptExtractor("", mode=ConceptExtractionMode.HEURISTIC)
result = extractor.extract(sections=sections)
for concept in result.concepts:
    print(f"{concept.name}: {concept.definition}")
```

### API Client

```python
import requests

response = requests.post(
    "http://localhost:8000/extract-and-structure",
    json={"html": html_content}
)
result = response.json()
```

---

## CLI Commands

### Extract from URL

```bash
python client.py --url https://example.com/article --output result.json
```

### Extract from File

```bash
python client.py --file article.html --output result.json
```

### Display Result

```bash
cat result.json | python -m json.tool
```

---

## Files Overview

| File                 | Purpose             | Lines  |
| -------------------- | ------------------- | ------ |
| extractor.py         | Content extraction  | 180    |
| concept_extractor.py | Concept structuring | 320    |
| main.py              | FastAPI service     | 120    |
| client.py            | CLI client          | 150    |
| config.py            | Configuration       | 40     |
| test\_\*.py          | Tests (3 files)     | 700    |
| example\_\*.py       | Examples (2 files)  | 370    |
| Total                | Production code     | ~2,400 |

---

## Test Coverage

- **48 total tests** - All passing ✓
- Extraction tests: 11
- Concept tests: 19
- API tests: 18

Run: `pytest -v`

---

## Features

### Content Extraction

- ✓ HTML parsing
- ✓ Ad removal
- ✓ Navigation removal
- ✓ Footer removal
- ✓ Heading preservation
- ✓ Whitespace normalization

### Concept Extraction

- ✓ Definition identification
- ✓ Example extraction
- ✓ Prerequisite detection
- ✓ Key point identification
- ✓ Related concept linking
- ✓ Atomic concepts

### API Service

- ✓ 6 endpoints
- ✓ Auto-documentation
- ✓ Error handling
- ✓ Request validation
- ✓ Multiple modes

---

## Common Tasks

### Extract from Website

```bash
python client.py --url https://wikipedia.org/wiki/Photosynthesis --output photosynthesis.json
```

### Extract from Local File

```bash
python client.py --file course.html --output concepts.json
```

### Run All Tests

```bash
pytest -v
```

### Start API in Development Mode

```bash
python main.py
```

### Check API Status

```bash
curl http://localhost:8000/health
```

### Get Available Modes

```bash
curl http://localhost:8000/modes
```

---

## Troubleshooting

### API Won't Start

```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000
# Start on different port:
# Modify main.py line: uvicorn.run(app, host="0.0.0.0", port=8080)
```

### Tests Failing

```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
# Run tests again
pytest -v
```

### No Concepts Extracted

- Try LLM mode for better accuracy
- Check content has clear definitions
- Verify section format is correct

### API Timeout

- Heuristic mode should be fast
- LLM mode takes 1-2 seconds
- Check ANTHROPIC_API_KEY is set

---

## Documentation Links

- **README.md** - Full documentation
- **QUICKSTART.md** - 30-second setup
- **CONCEPT_EXTRACTOR_GUIDE.md** - Detailed guide
- **PROJECT_SUMMARY_V2.md** - Complete overview
- **DELIVERY_SUMMARY.md** - What was delivered

---

## Status

✓ Production Ready
✓ All Tests Passing (48/48)
✓ Full Documentation
✓ Multiple Modes
✓ API Service
✓ CLI Tools

Ready for immediate use!

---

_Last Updated: May 2, 2026_
_Project: LinkLearn - Content Extraction & Academic Structuring Engine_
