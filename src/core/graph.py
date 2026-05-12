from collections import OrderedDict
from typing import List
import networkx as nx
from .models import ConceptChunk, GraphEdge, KnowledgeGraph
from .semantic import EmbeddingStore


class KnowledgeGraphBuilder:
    """Build a hierarchical and similarity-based knowledge graph."""

    def __init__(self, embedding_store: EmbeddingStore, similarity_threshold: float = 0.78):
        self.embedding_store = embedding_store
        self.similarity_threshold = similarity_threshold

    def build(self, chunks: List[ConceptChunk]) -> KnowledgeGraph:
        graph = nx.DiGraph()

        for chunk in chunks:
            label = self._normalize_label(chunk.concept)
            graph.add_node(label)

        self._add_hierarchy_edges(graph, chunks)
        self._add_similarity_edges(graph)

        nodes = list(graph.nodes)
        edges: List[GraphEdge] = []
        for source, target, data in graph.edges(data=True):
            edges.append(GraphEdge(from_=source, to=target, type=data.get("type", "related-to")))

        return KnowledgeGraph(nodes=nodes, edges=edges)

    def _add_hierarchy_edges(self, graph: nx.DiGraph, chunks: List[ConceptChunk]) -> None:
        for chunk in chunks:
            target = self._normalize_label(chunk.concept)
            for parent in chunk.topic_hierarchy:
                source = self._normalize_label(parent)
                if source and source != target:
                    graph.add_edge(source, target, type="parent-child")

    def _add_similarity_edges(self, graph: nx.DiGraph) -> None:
        if self.embedding_store is None or self.embedding_store.index is None:
            return

        for source_chunk, target_chunk, score in self.embedding_store.related_pairs(self.similarity_threshold, top_k=5):
            source = self._normalize_label(source_chunk.concept)
            target = self._normalize_label(target_chunk.concept)
            if source and target and source != target:
                if not graph.has_edge(source, target):
                    graph.add_edge(source, target, type="related-to")

    def _normalize_label(self, text: str) -> str:
        if not text:
            return ""
        return " ".join(text.strip().split())
