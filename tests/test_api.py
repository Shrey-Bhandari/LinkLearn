"""Test suite for FastAPI service."""

import pytest
from fastapi.testclient import TestClient
from src.api import app


client = TestClient(app)

VALID_HTML = """
<html>
    <head><title>Test Course</title></head>
    <body>
        <h1>Test Course</h1>
        <p>This is test content.</p>
        <h2>Section 1</h2>
        <p>More content here.</p>
    </body>
</html>
"""

HTML_WITH_NAV_AND_ADS = """
<html>
    <head><title>Learning</title></head>
    <body>
        <nav><a href="/">Home</a></nav>
        <h1>Learning</h1>
        <p>Educational content.</p>
        <div class="advertisement">Buy now!</div>
        <footer>Footer info</footer>
    </body>
</html>
"""

HTML_MACHINE_LEARNING = """
<html>
    <head><title>Machine Learning Basics</title></head>
    <body>
        <h1>Machine Learning Basics</h1>
        <p>Machine learning is a subset of artificial intelligence that enables computers to learn from data without being explicitly programmed.</p>
        <h2>Supervised Learning</h2>
        <p>Supervised learning uses labeled data. For example, predicting house prices from historical data.</p>
        <h2>Unsupervised Learning</h2>
        <p>Unsupervised learning discovers patterns in unlabeled data. K-means clustering is a common technique.</p>
    </body>
</html>
"""


class TestAPI:
    """Test the FastAPI endpoints."""
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_available_modes(self):
        """Test available modes endpoint."""
        response = client.get("/modes")
        assert response.status_code == 200
        data = response.json()
        assert "modes" in data
        assert "heuristic" in data["modes"]
    
    def test_extract_valid_html(self):
        """Test extraction of valid HTML."""
        response = client.post("/extract", json={"html": VALID_HTML})
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == "Test Course"
        assert len(data["sections"]) > 0
        assert data["sections"][0]["heading"] == "Test Course"
    
    def test_extract_removes_ads_and_nav(self):
        """Test that ads and navigation are removed."""
        response = client.post("/extract", json={"html": HTML_WITH_NAV_AND_ADS})
        assert response.status_code == 200
        
        data = response.json()
        content = ' '.join(s["content"] for s in data["sections"])
        
        assert "Home" not in content
        assert "Buy now" not in content
        assert "Footer info" not in content
        assert "Educational content" in content
    
    def test_extract_empty_html(self):
        """Test handling of empty HTML."""
        response = client.post("/extract", json={"html": ""})
        assert response.status_code == 400
        assert "cannot be empty" in response.json()["detail"]
    
    def test_extract_whitespace_only_html(self):
        """Test handling of whitespace-only HTML."""
        response = client.post("/extract", json={"html": "   \n\t  "})
        assert response.status_code == 400
    
    def test_extract_no_content_html(self):
        """Test handling of HTML with no educational content."""
        no_content_html = "<html><nav>Nav</nav><footer>Footer</footer></html>"
        response = client.post("/extract", json={"html": no_content_html})
        assert response.status_code == 422
        assert "No educational content" in response.json()["detail"]
    
    def test_extract_response_format(self):
        """Test that response format matches specification."""
        response = client.post("/extract", json={"html": VALID_HTML})
        data = response.json()
        
        # Check structure
        assert "title" in data
        assert "sections" in data
        assert isinstance(data["sections"], list)
        
        # Check section structure
        for section in data["sections"]:
            assert "heading" in section
            assert "content" in section
            assert isinstance(section["heading"], str)
            assert isinstance(section["content"], str)


class TestConceptExtractionAPI:
    """Test concept extraction endpoints."""
    
    def test_structure_concepts_valid(self):
        """Test concept structuring with valid sections."""
        sections = [
            {
                "heading": "Machine Learning",
                "content": "Machine learning is a subset of AI. For example, neural networks are used in image recognition."
            },
            {
                "heading": "Supervised Learning",
                "content": "Supervised learning uses labeled data. This is important for training models."
            }
        ]
        
        response = client.post(
            "/structure-concepts",
            json={"sections": sections, "mode": "heuristic"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "concepts" in data
        assert len(data["concepts"]) > 0

    def test_concept_graph_endpoint(self):
        """Test the concept graph endpoint."""
        sections = [
            {
                "heading": "Photosynthesis",
                "content": "Photosynthesis is a process that converts light into chemical energy. It requires light reactions."
            },
            {
                "heading": "Light reactions",
                "content": "Light reactions produce ATP and NADPH for the Calvin cycle."
            }
        ]

        response = client.post(
            "/concept-graph",
            json={"sections": sections, "mode": "heuristic"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "nodes" in data
        assert "edges" in data
        assert any(edge["type"] == "parent-child" for edge in data["edges"])
        assert any("Photosynthesis" in node for node in data["nodes"])

    def test_flashcards_endpoint(self):
        """Test the flashcards endpoint."""
        chunks = [
            {
                "concept": "Photosynthesis",
                "content": (
                    "Photosynthesis is a process used by plants to convert light into chemical energy. "
                    "Key points: It produces oxygen; It stores energy in glucose. "
                    "Example: Plants make glucose using sunlight. "
                    "Prerequisites: Light reactions"
                )
            }
        ]

        response = client.post(
            "/flashcards",
            json={"chunks": chunks}
        )

        assert response.status_code == 200
        data = response.json()
        assert "flashcards" in data
        assert len(data["flashcards"]) >= 3
        types = {card["type"] for card in data["flashcards"]}
        assert {"definition", "concept", "application"}.issubset(types)
    
    def test_structure_concepts_response_format(self):
        """Test that concept response format is correct."""
        sections = [
            {
                "heading": "Photosynthesis",
                "content": "Photosynthesis is a process where plants convert light into energy."
            }
        ]
        
        response = client.post(
            "/structure-concepts",
            json={"sections": sections, "mode": "heuristic"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check structure
        assert "concepts" in data
        assert "total_concepts" in data
        
        # Check concept format
        for concept in data["concepts"]:
            assert "name" in concept
            assert "definition" in concept
            assert "key_points" in concept
            assert "example" in concept
            assert "prerequisites" in concept
            assert "related_concepts" in concept
            
            # Check types
            assert isinstance(concept["name"], str)
            assert isinstance(concept["definition"], str)
            assert isinstance(concept["key_points"], list)
            assert concept["example"] is None or isinstance(concept["example"], str)
    
    def test_structure_concepts_empty_sections(self):
        """Test concept structuring with empty sections."""
        response = client.post(
            "/structure-concepts",
            json={"sections": [], "mode": "heuristic"}
        )
        assert response.status_code == 400
    
    def test_structure_concepts_invalid_mode(self):
        """Test concept structuring with invalid mode."""
        sections = [
            {
                "heading": "Test",
                "content": "Test content about concepts."
            }
        ]
        
        response = client.post(
            "/structure-concepts",
            json={"sections": sections, "mode": "invalid_mode"}
        )
        assert response.status_code == 400
        assert "Invalid mode" in response.json()["detail"]
    
    def test_structure_concepts_atomicity(self):
        """Test that extracted concepts are atomic."""
        sections = [
            {
                "heading": "ML Types",
                "content": "Supervised learning uses labeled data. Unsupervised learning finds patterns. Reinforcement learning uses rewards."
            }
        ]
        
        response = client.post(
            "/structure-concepts",
            json={"sections": sections, "mode": "heuristic"}
        )
        
        data = response.json()
        for concept in data["concepts"]:
            # Each concept name should be reasonably short (atomic)
            assert len(concept["name"]) < 150
    
    def test_extract_and_structure_pipeline(self):
        """Test complete extraction and structuring pipeline."""
        response = client.post(
            "/extract-and-structure",
            json={"html": HTML_MACHINE_LEARNING}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have both extracted content and concepts
        assert "extracted_content" in data
        assert "structured_concepts" in data
        
        # Check extracted content
        extracted = data["extracted_content"]
        assert extracted["title"]
        assert len(extracted["sections"]) > 0
        
        # Check structured concepts
        concepts = data["structured_concepts"]
        assert "concepts" in concepts
    
    def test_extract_and_structure_invalid_html(self):
        """Test pipeline with invalid HTML."""
        response = client.post(
            "/extract-and-structure",
            json={"html": ""}
        )
        assert response.status_code == 400
    
    def test_concept_exam_relevance(self):
        """Test that concepts extracted are exam-relevant."""
        sections = [
            {
                "heading": "Photosynthesis",
                "content": "Photosynthesis is the process by which plants convert light energy into chemical energy. It occurs in two stages: light-dependent reactions in the thylakoid and the Calvin cycle in the stroma."
            }
        ]
        
        response = client.post(
            "/structure-concepts",
            json={"sections": sections, "mode": "heuristic"}
        )
        
        data = response.json()
        
        # Should extract meaningful concepts
        for concept in data["concepts"]:
            # Should have meaningful names
            assert len(concept["name"]) > 0
            # Should avoid empty definitions
            if concept["definition"]:
                assert len(concept["definition"]) > 5


class TestConceptExtractorModes:
    """Test different concept extraction modes."""
    
    def test_heuristic_mode(self):
        """Test heuristic extraction mode."""
        sections = [
            {
                "heading": "Classification",
                "content": "Classification is a supervised learning task. It assigns data to predefined categories."
            }
        ]
        
        response = client.post(
            "/structure-concepts",
            json={"sections": sections, "mode": "heuristic"}
        )
        
        assert response.status_code == 200
        assert len(response.json()["concepts"]) >= 0
    
    def test_hybrid_mode_fallback(self):
        """Test hybrid mode (should fall back gracefully)."""
        sections = [
            {
                "heading": "Regression",
                "content": "Regression predicts continuous values. For example, predicting house prices."
            }
        ]
        
        response = client.post(
            "/structure-concepts",
            json={"sections": sections, "mode": "hybrid"}
        )
        
        # Should work even without LLM API
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
