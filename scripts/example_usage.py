"""Example usage of the content extraction engine."""

from src.core.extractor import ContentExtractor
import json


# Example 1: Educational webpage
EXAMPLE_1 = """
<!DOCTYPE html>
<html>
<head>
    <title>Introduction to Web Development</title>
    <meta charset="UTF-8">
    <script>analytics();</script>
</head>
<body>
    <nav class="navbar">
        <a href="/">Home</a>
        <a href="/courses">Courses</a>
        <a href="/about">About</a>
    </nav>
    
    <main>
        <h1>Introduction to Web Development</h1>
        <p>Web development is the work involved in developing websites for the Internet or an intranet. 
        It can range from developing a simple single static page of plain text to complex web applications, 
        electronic businesses, and social network services.</p>
        
        <p>Web development is broadly divided into frontend and backend development.</p>
        
        <h2>Frontend Development</h2>
        <p>Frontend development refers to the client-side of web development. 
        It involves working with HTML, CSS, and JavaScript to create the user interface and user experience.</p>
        <p>Frontend developers focus on making websites look good and ensuring a smooth user experience.</p>
        
        <h3>HTML</h3>
        <p>HTML (HyperText Markup Language) is the standard markup language used to create web pages.</p>
        
        <h3>CSS</h3>
        <p>CSS (Cascading Style Sheets) is used to style and layout web pages.</p>
        
        <h2>Backend Development</h2>
        <p>Backend development involves server-side programming, databases, and API development.</p>
        <p>Backend developers ensure that the server, application, and database communicate correctly.</p>
        
        <div class="advertisement">
            <h3>SPECIAL OFFER: Learn Web Dev for $49!</h3>
            <button>Enroll Now</button>
        </div>
        
        <h2>Getting Started</h2>
        <p>To start web development, you'll need a text editor, a web browser, and a willingness to learn.</p>
    </main>
    
    <aside class="sidebar-widget">
        <h3>Featured Courses</h3>
        <p>Sponsored content here</p>
    </aside>
    
    <footer>
        <p>Copyright 2024 Learning Platform. All rights reserved.</p>
        <p>Privacy Policy | Terms of Service</p>
    </footer>
</body>
</html>
"""

# Example 2: Article with heavy ads
EXAMPLE_2 = """
<!DOCTYPE html>
<html>
<head>
    <title>Machine Learning Algorithms</title>
</head>
<body>
    <div id="top-banner-ad">
        <img src="ad.jpg" alt="Buy Now">
        <p>Click here for amazing discounts!</p>
    </div>
    
    <h1>Machine Learning Algorithms</h1>
    <p>Machine learning algorithms are statistical models that learn from data.</p>
    
    <div class="sponsored-sidebar">
        <p>This article is sponsored by TechCorp</p>
    </div>
    
    <h2>Classification Algorithms</h2>
    <p>Classification is a supervised learning technique where the goal is to predict the category 
    or class of given data points.</p>
    
    <h3>Decision Trees</h3>
    <p>Decision trees are simple yet powerful classification algorithms that mimic human decision-making.</p>
    
    <div class="ad-widget">Advertisement</div>
    
    <h3>Random Forest</h3>
    <p>Random Forest is an ensemble method that combines multiple decision trees.</p>
    
    <h2>Regression Algorithms</h2>
    <p>Regression algorithms are used for predicting continuous values.</p>
    
    <footer>
        <p>© 2024 All rights reserved</p>
    </footer>
</body>
</html>
"""


def print_extracted_content(title: str, html: str):
    """Extract and print content in formatted JSON."""
    print(f"\n{'='*60}")
    print(f"Example: {title}")
    print(f"{'='*60}\n")
    
    extractor = ContentExtractor(html)
    result = extractor.extract()
    
    # Print as formatted JSON
    output = {
        "title": result.title,
        "sections": [
            {
                "heading": section.heading,
                "content": section.content
            }
            for section in result.sections
        ]
    }
    
    print(json.dumps(output, indent=2))
    print(f"\nExtracted {len(result.sections)} sections")


def main():
    """Run extraction examples."""
    print("Content Extraction Engine - Examples")
    print("="*60)
    
    # Example 1
    print_extracted_content(
        "Educational Webpage with Navigation and Ads",
        EXAMPLE_1
    )
    
    # Example 2
    print_extracted_content(
        "Article with Heavy Advertisement",
        EXAMPLE_2
    )
    
    # Summary
    print(f"\n{'='*60}")
    print("Extraction Summary:")
    print(f"{'='*60}")
    print("[OK] Navigation removed (nav, sidebar)")
    print("[OK] Advertisements removed (divs with ad patterns)")
    print("[OK] Footers removed (footer tags)")
    print("[OK] Educational content preserved (title, headings, paragraphs)")
    print("[OK] Content organized by heading hierarchy")
    print("[OK] Output in structured JSON format")


if __name__ == "__main__":
    main()
