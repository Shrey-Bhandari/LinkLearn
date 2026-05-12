from typing import List, Tuple
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from .models import ConceptChunk


class EmbeddingStore:
    """In-memory FAISS-backed embedding store for semantic retrieval."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.index: faiss.IndexFlatIP | None = None
        self.chunks: List[ConceptChunk] = []
        self.embeddings: np.ndarray | None = None

    def index_chunks(self, chunks: List[ConceptChunk]) -> None:
        """Generate embeddings for chunks and build a FAISS index."""
        self.chunks = chunks
        texts = [chunk.content for chunk in chunks]
        if not texts:
            self.index = None
            self.embeddings = None
            return

        self.embeddings = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        dim = self.embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(self.embeddings)

    def search(self, query: str, k: int = 4) -> List[Tuple[ConceptChunk, float]]:
        """Search for chunks most similar to the query text."""
        if self.index is None or self.embeddings is None or not self.chunks:
            return []

        query_embedding = self.model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
        distances, indices = self.index.search(query_embedding, k)
        hits: List[Tuple[ConceptChunk, float]] = []
        for distance, index in zip(distances[0], indices[0]):
            if index < 0 or index >= len(self.chunks):
                continue
            hits.append((self.chunks[index], float(distance)))
        return hits

    def related_pairs(self, threshold: float = 0.78, top_k: int = 5) -> List[Tuple[ConceptChunk, ConceptChunk, float]]:
        """Return related chunk pairs above a similarity threshold."""
        if self.index is None or self.embeddings is None or not self.chunks:
            return []

        pairs = []
        for index, chunk in enumerate(self.chunks):
            distances, indices = self.index.search(self.embeddings[index:index + 1], top_k + 1)
            for score, other_index in zip(distances[0], indices[0]):
                if other_index == index or other_index < 0:
                    continue
                if score >= threshold:
                    pairs.append((chunk, self.chunks[other_index], float(score)))
        return pairs
