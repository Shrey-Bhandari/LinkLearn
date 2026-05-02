# Quick Start Guide

## 30-Second Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the API

```bash
python main.py
```

The API is now running at `http://localhost:8000`

### 3. Extract Content

**Using cURL:**

```bash
curl -X POST "http://localhost:8000/extract" \
  -H "Content-Type: application/json" \
  -d '{"html": "<h1>Title</h1><p>Content</p>"}'
```

**Using Python:**

```python
import requests

response = requests.post(
    "http://localhost:8000/extract",
    json={"html": "<h1>Title</h1><p>Content</p>"}
)
print(response.json())
```

## Common Tasks

### Extract from an HTML File

```bash
python client.py --file mypage.html --output result.json
```

### Extract from a Website

```bash
python client.py --url https://example.com/article --output result.json
```

### Run Tests

```bash
# Test the extractor
pytest test_extractor.py -v

# Test the API
pytest test_api.py -v

# Run all tests
pytest -v
```

### See Interactive API Docs

Open your browser to: `http://localhost:8000/docs`

## Test It Immediately

Run the example script to see how it works:

```bash
python example_usage.py
```

This will extract content from two sample HTML documents and show the output.

## API Endpoints

| Method | Endpoint   | Purpose                             |
| ------ | ---------- | ----------------------------------- |
| POST   | `/extract` | Extract content from HTML           |
| GET    | `/health`  | Check API health                    |
| GET    | `/docs`    | Interactive documentation (Swagger) |
| GET    | `/redoc`   | Alternative documentation (ReDoc)   |

## Request Format

```json
{
  "html": "<html>...</html>"
}
```

## Response Format

```json
{
  "title": "Page Title",
  "sections": [
    {
      "heading": "Section Heading",
      "content": "Section content..."
    }
  ]
}
```

## What Gets Removed

- Navigation menus
- Footers
- Ads and sponsored content
- Scripts and styles
- Embedded frames
- Forms and buttons

## Troubleshooting

### "Connection refused"

Make sure the API is running:

```bash
python main.py
```

### "No educational content found"

The HTML may contain only ads/navigation. Try with content that has headings and paragraphs.

### Module not found errors

Install dependencies:

```bash
pip install -r requirements.txt
```

## Next Steps

- Read [README.md](README.md) for full documentation
- Check [test_extractor.py](test_extractor.py) for more examples
- Explore the API docs at http://localhost:8000/docs
- Customize [config.py](config.py) for your needs

## Architecture Overview

```
Client Code (Python/cURL)
         ↓
    main.py (FastAPI)
         ↓
   extractor.py (BeautifulSoup)
         ↓
   Cleaned JSON Response
```

1. **Client** sends HTML to the API
2. **API** validates input and creates extractor
3. **Extractor** parses HTML and removes unwanted elements
4. **Response** returns structured JSON with content

That's it! You're ready to extract clean educational content from any HTML.
