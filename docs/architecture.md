# Link2Learn Architecture

Link2Learn is designed as a modular education-content pipeline with clear boundaries for extraction, semantic processing, graph construction, and UI presentation.

## Directory Layout

- `src/`
  - `__init__.py` - package entrypoint
  - `api.py` - FastAPI service exposing extraction and concept endpoints
  - `ui.py` - Streamlit user interface for interactive artifact generation
  - `core/` - implementation modules
    - `extractor.py` - HTML cleaning and section extraction
    - `concept_extractor.py` - academic concept structuring and flashcard conversion
    - `scraper.py` - URL fetching and sanitized HTML extraction
    - `chunker.py` - semantic chunk generation and topic hierarchy
    - `semantic.py` - SentenceTransformer embeddings and FAISS retrieval
    - `graph.py` - NetworkX knowledge graph builder and similarity merge
    - `groq_client.py` - Groq API client with caching and retry behavior
    - `models.py` - shared Pydantic models for notes, flashcards, MCQs, and graphs
    - `pipeline.py` - orchestration of the Link2Learn pipeline
- `scripts/`
  - `run_api.py` - start the FastAPI server
  - `run_pipeline.py` - command-line pipeline runner
  - `example_usage.py` - sample extraction usage script
- `tests/`
  - `test_api.py`
  - `test_extractor.py`
  - `test_concept_extractor.py`
  - `test_link2learn_pipeline.py`
- `docs/`
  - `architecture.md`
- `requirements.txt`
- `README.md`

## High-Level Flow

1. URL scraping and HTML cleaning
2. Educational section extraction
3. Semantic chunking and embeddings indexing
4. Knowledge graph building with hierarchy and related concept edges
5. Flashcard and MCQ output generation
6. Optional Groq integration for enhanced exam-friendly artifacts
