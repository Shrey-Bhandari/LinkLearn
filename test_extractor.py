"""Test suite for content extraction engine."""

import pytest
from extractor import ContentExtractor


# Sample HTML for testing
SAMPLE_EDUCATIONAL_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Introduction to Machine Learning</title>
    <script>console.log('ignored');</script>
</head>
<body>
    <nav>
        <a href="/">Home</a>
        <a href="/courses">Courses</a>
    </nav>
    
    <main>
        <h1>Introduction to Machine Learning</h1>
        <p>Machine learning is a subset of artificial intelligence that focuses on enabling 
        computers to learn from data without being explicitly programmed.</p>
        <p>It has become one of the most important technologies in the modern world.</p>
        
        <h2>Key Concepts</h2>
        <p>Machine learning can be divided into three main categories: supervised learning, 
        unsupervised learning, and reinforcement learning.</p>
        <p>Each category has its own applications and challenges.</p>
        
        <h3>Supervised Learning</h3>
        <p>Supervised learning uses labeled data to train algorithms. The algorithm learns 
        the mapping from inputs to outputs.</p>
        
        <h3>Unsupervised Learning</h3>
        <p>Unsupervised learning works with unlabeled data to discover hidden patterns and structures.</p>
        
        <h2>Applications</h2>
        <p>Machine learning is used in many real-world applications including image recognition, 
        natural language processing, and recommendation systems.</p>
        
        <div class="advertisement">
            <p>Buy our ML course for $99!</p>
        </div>
    </main>
    
    <footer>
        <p>Copyright 2024. All rights reserved.</p>
    </footer>
</body>
</html>
"""

HTML_WITH_ADS = """
<!DOCTYPE html>
<html>
<head>
    <title>Python Basics</title>
</head>
<body>
    <div id="banner-ad">
        <p>Click here for amazing deals!</p>
    </div>
    
    <h1>Python Basics</h1>
    <p>Python is a high-level programming language known for its simplicity.</p>
    
    <div class="sidebar-ad">Advertisement content</div>
    
    <h2>Variables and Data Types</h2>
    <p>Variables are containers for storing data values.</p>
    
    <div class="sponsor-widget">
        Sponsor content
    </div>
</body>
</html>
"""

MINIMAL_HTML = """
<html>
    <h1>Simple Title</h1>
    <p>Simple content paragraph.</p>
</html>
"""

EMPTY_HTML = """
<html>
    <nav>Navigation only</nav>
    <footer>Footer only</footer>
</html>
"""


class TestContentExtractor:
    """Test the content extraction functionality."""
    
    def test_extract_title(self):
        """Test that title is correctly extracted."""
        extractor = ContentExtractor(SAMPLE_EDUCATIONAL_HTML)
        result = extractor.extract()
        assert result.title == "Introduction to Machine Learning"
    
    def test_extract_sections(self):
        """Test that sections are correctly extracted."""
        extractor = ContentExtractor(SAMPLE_EDUCATIONAL_HTML)
        result = extractor.extract()
        
        assert len(result.sections) > 0
        # Check first section
        assert result.sections[0].heading == "Introduction to Machine Learning"
        assert "Machine learning" in result.sections[0].content
        
        # Check that we have multiple sections
        headings = [s.heading for s in result.sections]
        assert "Key Concepts" in headings
        assert "Applications" in headings
    
    def test_remove_navigation(self):
        """Test that navigation is removed."""
        extractor = ContentExtractor(SAMPLE_EDUCATIONAL_HTML)
        result = extractor.extract()
        
        content_text = ' '.join(s.content for s in result.sections)
        assert "Home" not in content_text
        assert "Courses" not in content_text
    
    def test_remove_footer(self):
        """Test that footer is removed."""
        extractor = ContentExtractor(SAMPLE_EDUCATIONAL_HTML)
        result = extractor.extract()
        
        content_text = ' '.join(s.content for s in result.sections)
        assert "Copyright" not in content_text
    
    def test_remove_ads(self):
        """Test that ads are removed."""
        extractor = ContentExtractor(HTML_WITH_ADS)
        result = extractor.extract()
        
        content_text = ' '.join(s.content for s in result.sections)
        assert "Buy our" not in content_text
        assert "deals" not in content_text
        assert "Sponsor" not in content_text
    
    def test_remove_ad_patterns(self):
        """Test removal of common ad pattern classes/ids."""
        extractor = ContentExtractor(HTML_WITH_ADS)
        result = extractor.extract()
        
        content_text = ' '.join(s.content for s in result.sections)
        assert "Click here" not in content_text
        assert "Advertisement content" not in content_text
    
    def test_minimal_html(self):
        """Test extraction from minimal HTML."""
        extractor = ContentExtractor(MINIMAL_HTML)
        result = extractor.extract()
        
        assert result.title == "Simple Title"
        assert len(result.sections) > 0
        assert "Simple content" in result.sections[0].content
    
    def test_empty_educational_content(self):
        """Test handling of HTML with no educational content."""
        extractor = ContentExtractor(EMPTY_HTML)
        result = extractor.extract()
        
        # Should have no sections since nav and footer are removed
        assert result.title is None
        assert len(result.sections) == 0
    
    def test_preserve_paragraph_order(self):
        """Test that paragraph order is preserved."""
        extractor = ContentExtractor(SAMPLE_EDUCATIONAL_HTML)
        result = extractor.extract()
        
        # First section should have multiple paragraphs combined
        first_section = result.sections[0]
        assert "without being explicitly programmed" in first_section.content
        assert "has become one of the most important" in first_section.content
    
    def test_clean_multiple_spaces(self):
        """Test that multiple spaces are cleaned up."""
        html = """
        <h1>Test</h1>
        <p>Multiple   spaces   between   words</p>
        """
        extractor = ContentExtractor(html)
        result = extractor.extract()
        
        assert "Multiple   spaces" not in result.sections[0].content
        assert "Multiple spaces between words" in result.sections[0].content
    
    def test_heading_hierarchy(self):
        """Test that different heading levels are handled."""
        extractor = ContentExtractor(SAMPLE_EDUCATIONAL_HTML)
        result = extractor.extract()
        
        headings = [s.heading for s in result.sections]
        # Should have h1, h2, and h3 headings
        assert "Introduction to Machine Learning" in headings  # h1
        assert "Key Concepts" in headings  # h2
        assert "Supervised Learning" in headings  # h3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
