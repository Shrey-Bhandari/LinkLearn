from src.core.pipeline import Link2LearnPipeline


SAMPLE_EDUCATIONAL_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Unordered Map in C++</title>
</head>
<body>
    <nav><a href="/">Home</a></nav>
    <h1>Unordered Map in C++ STL</h1>
    <p>unordered_map stores key-value pairs using hashing and does not maintain sorted order.</p>
    <h2>Insertion</h2>
    <p>You can insert items with operator[] or insert(). operator[] will create default values for missing keys.</p>
    <h2>Access</h2>
    <p>Use at() to retrieve values safely because operator[] can insert a default entry when the key is missing.</p>
    <footer>Copyright 2026</footer>
</body>
</html>
"""


def test_link2learn_process_html():
    pipeline = Link2LearnPipeline(use_groq=False)
    result = pipeline.process_html(SAMPLE_EDUCATIONAL_HTML, source_url="https://example.com/unordered_map")

    assert result.notes, "Expected at least one note"
    assert result.graph.nodes, "Graph should contain nodes"
    assert isinstance(result.flashcards, list)
    assert isinstance(result.mcqs, list)
    assert all(hasattr(card, "question") for card in result.flashcards)
    assert all(hasattr(item, "options") for item in result.mcqs)
    assert result.graph.edges, "Graph should contain at least one edge"

    # Ensure the note includes exam-oriented definition text
    definitions = [note.definition for note in result.notes]
    assert any("hashing" in definition.lower() or "sorted order" in definition.lower() for definition in definitions)
