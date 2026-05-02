"""FastAPI web service for content extraction."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from extractor import ContentExtractor, ExtractedContent
from concept_extractor import ConceptExtractor, StructuredConcepts, ConceptExtractionMode


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
