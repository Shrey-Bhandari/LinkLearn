# Content Extraction Engine

A Python-based web API service that extracts meaningful educational content from HTML webpages, removing navigation, ads, footers, and other non-educational elements.

## Features

- **Clean Content Extraction**: Extracts only meaningful educational content (titles, headings, paragraphs)
- **Intelligent Filtering**: Automatically removes:
  - Navigation menus
  - Advertisements and sponsored content
  - Footers
  - Scripts and styles
  - Common ad patterns (banners, sidebars, widgets)
- **Structured Output**: Returns clean JSON with title and organized sections
- **RESTful API**: Easy-to-use FastAPI endpoints
- **Comprehensive Tests**: Full test coverage with realistic examples

## Installation

1. **Clone or navigate to the project directory**:

```bash
cd LinkLearn
```

2. **Create a virtual environment** (recommended):

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. **Install dependencies**:

```bash
pip install -r requirements.txt
```

## Usage

### Starting the API Server

```bash
python main.py
```

The server will start at `http://localhost:8000`

### API Documentation

Interactive API documentation available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Making Requests

#### Extract Content Endpoint

**POST** `/extract`

Request body:

```json
{
  "html": "<html>...your html content...</html>"
}
```

**Response** (Success - 200):

```json
{
  "title": "Introduction to Machine Learning",
  "sections": [
    {
      "heading": "Introduction to Machine Learning",
      "content": "Machine learning is a subset of artificial intelligence..."
    },
    {
      "heading": "Key Concepts",
      "content": "Machine learning can be divided into three main categories..."
    }
  ]
}
```

**Error Responses**:

- `400 Bad Request`: HTML content is empty
- `422 Unprocessable Entity`: No educational content found in HTML
- `500 Internal Server Error`: Processing error

#### Health Check Endpoint

**GET** `/health`

Response:

```json
{
  "status": "healthy"
}
```

### Example: Using with Python

```python
import requests

html_content = """
<html>
    <head><title>Python Basics</title></head>
    <body>
        <nav><a href="/">Home</a></nav>
        <h1>Python Basics</h1>
        <p>Python is a high-level programming language.</p>
        <h2>Getting Started</h2>
        <p>Install Python from python.org</p>
        <div class="ad">Buy our course!</div>
    </body>
</html>
"""

response = requests.post("http://localhost:8000/extract", json={"html": html_content})
result = response.json()
print(result)
```

### Example: Using with cURL

```bash
curl -X POST "http://localhost:8000/extract" \
  -H "Content-Type: application/json" \
  -d '{
    "html": "<html><head><title>Test</title></head><body><h1>Test</h1><p>Content</p></body></html>"
  }'
```

## Running Tests

### Test the extraction engine:

```bash
pytest test_extractor.py -v
```

### Test the API service:

```bash
pytest test_api.py -v
```

### Run all tests:

```bash
pytest -v
```

### Test Coverage:

```bash
pytest --cov=.
```

## How It Works

### Content Extraction Process

1. **HTML Parsing**: Parses raw HTML using BeautifulSoup
2. **Unwanted Element Removal**:
   - Removes structural tags (nav, footer, aside, etc.)
   - Removes scripts and styles
   - Removes elements with ad-related classes/IDs
3. **Content Organization**:
   - Extracts title from `<title>` tag or first `<h1>`
   - Groups paragraphs under their heading
   - Preserves heading hierarchy (H1, H2, H3)
4. **Text Cleaning**:
   - Normalizes whitespace
   - Joins related paragraphs under headings
   - Removes empty sections

### Removed Elements

**By Tag**:

- `<nav>` - Navigation
- `<footer>` - Footer content
- `<header>` - Header sections
- `<aside>` - Side content
- `<script>` - JavaScript
- `<style>` - CSS styles
- `<iframe>` - Embedded content
- `<form>` - Forms
- `<button>` - Buttons

**By Class/ID Patterns**:

- ad, advertisement
- banner, sponsor
- promo, popup
- modal, sidebar
- widget, social

## Output Format

The API always returns data in the following JSON structure:

```json
{
  "title": "string or null",
  "sections": [
    {
      "heading": "string",
      "content": "string"
    }
  ]
}
```

## Architecture

### Files

- `extractor.py` - Core extraction logic
- `main.py` - FastAPI web service
- `test_extractor.py` - Unit tests for extractor
- `test_api.py` - Integration tests for API
- `requirements.txt` - Python dependencies

### Key Classes

**ContentExtractor**

- Main class for HTML content extraction
- Methods:
  - `__init__(html: str)` - Initialize with HTML
  - `extract() -> ExtractedContent` - Perform extraction
  - `_remove_unwanted_elements()` - Clean up HTML
  - `_is_ad_element()` - Check for ad patterns
  - `_extract_text()` - Clean text extraction

**Data Models** (Pydantic)

- `Section` - Heading + content pair
- `ExtractedContent` - Title + list of sections
- `HTMLInput` - API request format

## Constraints & Features

✅ **Preserves logical flow** - Content order maintained
✅ **No summarization** - Returns complete text
✅ **No new information** - Pure extraction
✅ **Intelligent filtering** - Removes ads and navigation
✅ **Handles various HTML structures** - Robust parsing
✅ **Clean output format** - Structured JSON
✅ **API service** - Easy integration

## Performance Considerations

- Efficient HTML parsing with BeautifulSoup
- Handles large HTML documents
- Minimal dependencies
- Fast content extraction

## Limitations

- Only processes H1-H3 headings (can be extended)
- Groups consecutive paragraphs under headings
- Requires valid HTML (handles malformed HTML gracefully)
- Pattern-based ad detection (not ML-based)

## Future Enhancements

- Support for more heading levels (H4-H6)
- Table and list extraction
- Code block preservation
- Image alt-text extraction
- Multi-language support
- Custom filtering rules

## License

MIT

## Support

For issues or feature requests, please refer to the repository documentation.
