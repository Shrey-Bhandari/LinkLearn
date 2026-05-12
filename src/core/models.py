from typing import List, Optional
from pydantic import BaseModel, Field


class Note(BaseModel):
    heading: str
    definition: str
    key_points: List[str] = []
    example: Optional[str] = None
    source_url: str
    topic_hierarchy: List[str] = []


class ConceptChunk(BaseModel):
    id: str
    heading: str
    concept: str
    content: str
    source_url: str
    topic_hierarchy: List[str] = []


class Flashcard(BaseModel):
    question: str
    answer: str
    type: str


class MCQ(BaseModel):
    question: str
    options: List[str]
    correct: str
    difficulty: str


class GraphEdge(BaseModel):
    from_: str = Field(..., alias="from")
    to: str
    type: str

    model_config = {
        "populate_by_name": True
    }


class KnowledgeGraph(BaseModel):
    nodes: List[str] = []
    edges: List[GraphEdge] = []


class PipelineResult(BaseModel):
    notes: List[Note] = []
    graph: KnowledgeGraph
    flashcards: List[Flashcard] = []
    mcqs: List[MCQ] = []
