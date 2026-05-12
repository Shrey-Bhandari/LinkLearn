"""FastAPI web service for content extraction."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from .core.extractor import ContentExtractor, ExtractedContent
from .core.concept_extractor import (
    ConceptExtractor,
    StructuredConcepts,
    ConceptExtractionMode,
    KnowledgeGraph,
    FlashcardsResponse,
    chunks_to_flashcards,
)


app = FastAPI(
    title="Content Extraction & Academic Structuring Engine",
    description="Extract educational content from HTML and structure it into academic concepts",
    version="2.0.0"
)


class HTMLInput(BaseModel):
    """Request model for HTML content."""
    html: str


class ConceptExtractionRequest(BaseModel):
    """Request model for concept extraction."""
    sections: list[dict]  # From extracted content
    mode: str = "heuristic"  # heuristic, llm, or hybrid


class ConceptChunk(BaseModel):
    """Response model for a semantic concept chunk."""
    concept: str
    content: str
    topic: Optional[str] = None


class ConceptFlashcardRequest(BaseModel):
    """Request model for concept flashcard generation."""
    chunks: list[ConceptChunk]


class ConceptChunksResponse(BaseModel):
    """Response model containing semantic chunks."""
    chunks: list[ConceptChunk]


@app.post("/extract", response_model=ExtractedContent)
async def extract_content(request: HTMLInput) -> ExtractedContent:
    """
    Extract educational content from HTML.
    
    Args:
        request: Contains raw HTML text
        
    Returns:
        Structured JSON with title and sections
        
    Raises:
        HTTPException: If HTML is empty or extraction fails
    """
    if not request.html or not request.html.strip():
        raise HTTPException(status_code=400, detail="HTML content cannot be empty")
    
    try:
        extractor = ContentExtractor(request.html)
        result = extractor.extract()
        
        if not result.title and not result.sections:
            raise HTTPException(
                status_code=422, 
                detail="No educational content found in provided HTML"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing HTML: {str(e)}"
        )


@app.post("/structure-concepts", response_model=StructuredConcepts)
async def structure_concepts(request: ConceptExtractionRequest) -> StructuredConcepts:
    """
    Structure extracted educational content into atomic academic concepts.
    
    Args:
        request: Contains extracted sections and extraction mode
        
    Returns:
        Structured concepts with definitions, key points, and examples
        
    Raises:
        HTTPException: If extraction fails
    """
    if not request.sections:
        raise HTTPException(status_code=400, detail="No sections provided")
    
    try:
        # Validate mode
        try:
            mode = ConceptExtractionMode(request.mode)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid mode. Use: {', '.join([m.value for m in ConceptExtractionMode])}"
            )
        
        extractor = ConceptExtractor("", mode=mode)
        result = extractor.extract(sections=request.sections)
        
        if not result.concepts:
            raise HTTPException(
                status_code=422,
                detail="No concepts could be extracted from provided sections"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error structuring concepts: {str(e)}"
        )


@app.post("/concept-graph", response_model=KnowledgeGraph)
async def concept_graph(request: ConceptExtractionRequest) -> KnowledgeGraph:
    """Build a concept knowledge graph from extracted sections."""
    if not request.sections:
        raise HTTPException(status_code=400, detail="No sections provided")

    try:
        try:
            mode = ConceptExtractionMode(request.mode)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid mode. Use: {', '.join([m.value for m in ConceptExtractionMode])}"
            )

        extractor = ConceptExtractor("", mode=mode)
        structured = extractor.extract(sections=request.sections)

        if not structured.concepts:
            raise HTTPException(
                status_code=422,
                detail="No concepts could be extracted from provided sections"
            )

        return structured.to_graph()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error building concept graph: {str(e)}"
        )


@app.post("/chunk-concepts", response_model=ConceptChunksResponse)
async def chunk_concepts(request: ConceptExtractionRequest) -> ConceptChunksResponse:
    """Structure content into semantic chunks for one concept per chunk."""
    if not request.sections:
        raise HTTPException(status_code=400, detail="No sections provided")

    try:
        try:
            mode = ConceptExtractionMode(request.mode)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid mode. Use: {', '.join([m.value for m in ConceptExtractionMode])}"
            )

        extractor = ConceptExtractor("", mode=mode)
        chunks_data = extractor.extract_chunks(sections=request.sections)
        return ConceptChunksResponse(**chunks_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error chunking concepts: {str(e)}"
        )


@app.post("/flashcards", response_model=FlashcardsResponse)
async def generate_flashcards(request: ConceptFlashcardRequest) -> FlashcardsResponse:
    """Generate flashcards from semantic concept chunks."""
    if not request.chunks:
        raise HTTPException(status_code=400, detail="No chunks provided")

    try:
        flashcard_data = chunks_to_flashcards(request.chunks)
        return FlashcardsResponse(**flashcard_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating flashcards: {str(e)}"
        )


@app.post("/extract-and-structure")
async def extract_and_structure(request: HTMLInput):
    """
    Complete pipeline: Extract content from HTML and structure into concepts.
    
    Args:
        request: Contains raw HTML text
        
    Returns:
        JSON with both extracted content and structured concepts
    """
    if not request.html or not request.html.strip():
        raise HTTPException(status_code=400, detail="HTML content cannot be empty")
    
    try:
        # Step 1: Extract content
        content_extractor = ContentExtractor(request.html)
        extracted = content_extractor.extract()
        
        if not extracted.title and not extracted.sections:
            raise HTTPException(
                status_code=422,
                detail="No educational content found in provided HTML"
            )
        
        # Step 2: Structure concepts
        concept_extractor = ConceptExtractor("", mode=ConceptExtractionMode.HYBRID)
        sections_data = [
            {"heading": s.heading, "content": s.content}
            for s in extracted.sections
        ]
        concepts = concept_extractor.extract(sections=sections_data)
        
        return {
            "extracted_content": extracted,
            "structured_concepts": concepts
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error in extraction pipeline: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/modes")
async def available_modes():
    """Get available concept extraction modes."""
    return {
        "modes": [m.value for m in ConceptExtractionMode],
        "descriptions": {
            "heuristic": "Pattern-based extraction (fast, no external API required)",
            "llm": "AI-powered extraction (requires ANTHROPIC_API_KEY or OPENAI_API_KEY)",
            "hybrid": "Try LLM first, fall back to heuristic"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
