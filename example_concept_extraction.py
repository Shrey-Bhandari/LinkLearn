"""Example usage of the complete extraction and structuring pipeline."""

from extractor import ContentExtractor
from concept_extractor import ConceptExtractor, ConceptExtractionMode
import json


# Sample educational content
SAMPLE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Introduction to Photosynthesis</title>
    <script>analytics();</script>
</head>
<body>
    <nav><a href="/">Home</a></nav>
    
    <article>
        <h1>Introduction to Photosynthesis</h1>
        <p>Photosynthesis is a process used by plants and other organisms to convert light energy 
        into chemical energy stored in glucose. This process occurs primarily in the leaves of plants 
        and is essential for life on Earth.</p>
        
        <h2>Light-Dependent Reactions</h2>
        <p>The light-dependent reactions occur in the thylakoid membranes of chloroplasts. These reactions 
        require light energy and produce ATP and NADPH. For example, in photosystem II, light excites 
        electrons that move through the electron transport chain, ultimately driving the synthesis of ATP.</p>
        
        <h3>Photosystem II</h3>
        <p>Photosystem II is the first light-dependent reaction complex. It captures photons and 
        uses their energy to split water molecules, releasing oxygen as a byproduct.</p>
        
        <h3>Photosystem I</h3>
        <p>Photosystem I is the second complex in the light reactions. It regenerates NADPH 
        and completes the electron transport chain.</p>
        
        <h2>Light-Independent Reactions (Calvin Cycle)</h2>
        <p>The Calvin cycle is the light-independent reaction that occurs in the stroma. It requires 
        ATP and NADPH from the light reactions to fix carbon dioxide into glucose.</p>
        
        <h3>Carbon Fixation</h3>
        <p>Carbon fixation is the first step of the Calvin cycle. The enzyme RuBisCO catalyzes the 
        reaction between RuBP and CO2, creating an unstable six-carbon compound that splits into 
        two 3-phosphoglycerate molecules.</p>
        
        <h3>Reduction Phase</h3>
        <p>In the reduction phase, 3-phosphoglycerate is reduced to glyceraldehyde-3-phosphate (G3P) 
        using ATP and NADPH. Some G3P molecules leave the cycle to form glucose.</p>
        
        <h3>Regeneration of RuBP</h3>
        <p>The remaining G3P molecules are rearranged to regenerate RuBP, allowing the cycle to continue. 
        This step consumes additional ATP.</p>
        
        <h2>Factors Affecting Photosynthesis</h2>
        <p>Several factors affect the rate of photosynthesis: 1) Light intensity - higher intensity 
        increases the rate up to a saturation point, 2) Temperature - affects enzyme activity with 
        an optimal range around 25-35°C, 3) CO2 concentration - limits the rate when other conditions 
        are optimal, 4) Water availability - essential as both a substrate and solvent.</p>
        
        <div class="advertisement">
            <h3>Learn More About Photosynthesis</h3>
            <p>Take our online course for just $29.99!</p>
        </div>
    </article>
    
    <footer>
        <p>Copyright 2024. All rights reserved.</p>
    </footer>
</body>
</html>
"""


def print_section_divider(title: str, char: str = "="):
    """Print a section divider."""
    print(f"\n{char * 60}")
    print(f"{title.center(60)}")
    print(f"{char * 60}\n")


def demo_content_extraction():
    """Demonstrate content extraction."""
    print_section_divider("STEP 1: Content Extraction")
    
    print("Extracting educational content from HTML...")
    extractor = ContentExtractor(SAMPLE_HTML)
    extracted = extractor.extract()
    
    print(f"\nTitle: {extracted.title}")
    print(f"Number of sections: {len(extracted.sections)}")
    
    for i, section in enumerate(extracted.sections[:3], 1):
        print(f"\n  [{i}] {section.heading}")
        preview = section.content[:100] + "..." if len(section.content) > 100 else section.content
        print(f"      {preview}")
    
    return extracted


def demo_concept_structuring(extracted):
    """Demonstrate concept structuring."""
    print_section_divider("STEP 2: Concept Structuring", "=")
    
    print("Structuring extracted content into academic concepts...")
    print("(Using heuristic mode - no LLM API required)\n")
    
    # Convert extracted sections to format needed by concept extractor
    sections_data = [
        {"heading": s.heading, "content": s.content}
        for s in extracted.sections
    ]
    
    # Extract concepts
    concept_extractor = ConceptExtractor("", mode=ConceptExtractionMode.HEURISTIC)
    concepts = concept_extractor.extract(sections=sections_data)
    
    print(f"Total concepts identified: {concepts.total_concepts}\n")
    
    # Display each concept
    for i, concept in enumerate(concepts.concepts[:5], 1):
        print(f"Concept {i}: {concept.name}")
        print(f"  Definition: {concept.definition}")
        
        if concept.key_points:
            print(f"  Key Points:")
            for point in concept.key_points[:3]:
                print(f"    - {point}")
        
        if concept.example:
            print(f"  Example: {concept.example}")
        
        if concept.prerequisites:
            print(f"  Prerequisites: {', '.join(concept.prerequisites)}")
        
        print()
    
    return concepts


def demo_json_output(concepts):
    """Demonstrate JSON output format."""
    print_section_divider("STEP 3: JSON Output")
    
    print("Structured concepts in JSON format:\n")
    
    # Create output in specified format
    output = {
        "concepts": [
            {
                "name": c.name,
                "definition": c.definition,
                "key_points": c.key_points,
                "example": c.example
            }
            for c in concepts.concepts[:3]  # Show first 3 concepts
        ]
    }
    
    print(json.dumps(output, indent=2))
    
    print(f"\n... and {max(0, len(concepts.concepts) - 3)} more concepts")


def demo_complete_pipeline():
    """Run complete extraction and structuring pipeline."""
    print("\n" + "="*60)
    print("LinkLearn: Content Extraction & Academic Structuring".center(60))
    print("="*60)
    
    # Step 1: Extract content
    extracted = demo_content_extraction()
    
    # Step 2: Structure concepts
    concepts = demo_concept_structuring(extracted)
    
    # Step 3: Show JSON output
    demo_json_output(concepts)
    
    # Summary
    print_section_divider("SUMMARY", "-")
    print(f"[OK] Content extracted: {len(extracted.sections)} sections")
    print(f"[OK] Concepts structured: {len(concepts.concepts)} concepts")
    print(f"[OK] Non-educational content removed (nav, ads, footer)")
    print(f"[OK] Output in structured JSON format")
    print(f"[OK] Concepts are atomic (one idea each)")
    print(f"[OK] Exam-relevant content preserved")


def demo_api_integration():
    """Show how to use with the API."""
    print_section_divider("API USAGE EXAMPLE")
    
    print("Using with the FastAPI service:\n")
    print("1. Start the server:")
    print("   $ python main.py\n")
    
    print("2. Extract and structure in one call:")
    print("   $ curl -X POST http://localhost:8000/extract-and-structure \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"html\": \"<html>...</html>\"}'\n")
    
    print("3. Or extract concepts from pre-extracted content:")
    print("   $ curl -X POST http://localhost:8000/structure-concepts \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{'")
    print("       \"sections\": [")
    print("         {\"heading\": \"...\", \"content\": \"...\"},")
    print("       ],")
    print("       \"mode\": \"heuristic\"")
    print("     }'")


if __name__ == "__main__":
    # Run complete pipeline demo
    demo_complete_pipeline()
    
    # Show API usage
    print()
    demo_api_integration()
    
    print("\n" + "="*60)
    print("For more information, see README.md and QUICKSTART.md".center(60))
    print("="*60 + "\n")
