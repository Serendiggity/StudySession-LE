#!/usr/bin/env python3
"""
Test extraction with examples.
Phase 3: Testing concept examples
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

import langextract as lx
from data.examples.content_examples.concepts_examples import concept_examples


def test_concept_extraction():
    """Test concept extraction with our 5 examples."""

    print("=" * 70)
    print("Testing Concept Extraction - Phase 3")
    print("=" * 70)
    print()

    # Load sample text from extracted PDF
    text_file = Path("data/input/study_materials/insolvency_admin_extracted.txt")
    full_text = text_file.read_text()

    # Use first 50,000 characters for testing (about 20-25 pages)
    test_text = full_text[:50000]

    print(f"Test data: {len(test_text):,} characters (~20 pages)")
    print(f"Examples: {len(concept_examples)} concept examples")
    print()

    # Create prompt
    prompt = """
    Extract key insolvency concepts and their definitions from the text.
    Focus on terms central to insolvency law and practice.
    Include the act and section where defined if mentioned.
    Mark importance as high, medium, or low based on exam relevance.
    """

    print("Running extraction...")
    print("(This may take 30-60 seconds)")
    print()

    try:
        result = lx.extract(
            text_or_documents=test_text,
            prompt_description=prompt,
            examples=concept_examples,
            model_id="gemini-2.5-flash",
            extraction_passes=2,  # 2 passes for testing
            max_workers=5  # Reduced to stay within rate limits
        )

        print("=" * 70)
        print("✓ Extraction Successful!")
        print("=" * 70)
        print()

        print(f"Total extractions: {len(result.extractions)}")
        print()

        # Show first 10 results
        print("First 10 extracted concepts:")
        print("-" * 70)

        for i, extraction in enumerate(result.extractions[:10], 1):
            term = extraction.attributes.get("term", "N/A")
            definition = extraction.attributes.get("definition", "N/A")
            importance = extraction.attributes.get("importance_level", "N/A")

            print(f"\n{i}. {term} ({importance})")
            print(f"   Definition: {definition[:100]}...")
            print(f"   Source: Characters {extraction.char_interval.start_pos}-{extraction.char_interval.end_pos}")

        print()
        print("=" * 70)
        print("Quality Assessment:")
        print("=" * 70)

        # Basic quality metrics
        with_definitions = sum(1 for e in result.extractions if e.attributes.get("definition"))
        with_importance = sum(1 for e in result.extractions if e.attributes.get("importance_level"))
        with_source_act = sum(1 for e in result.extractions if e.attributes.get("source_act"))

        total = len(result.extractions)
        print(f"• Extractions with definitions: {with_definitions}/{total} ({with_definitions/total*100:.0f}%)")
        print(f"• Extractions with importance level: {with_importance}/{total} ({with_importance/total*100:.0f}%)")
        print(f"• Extractions with source act: {with_source_act}/{total} ({with_source_act/total*100:.0f}%)")
        print()

        # Save results
        output_dir = Path("data/output/knowledge_base")
        output_dir.mkdir(parents=True, exist_ok=True)

        lx.io.save_annotated_documents(
            [result],
            output_name="test_concepts",
            output_dir=str(output_dir)
        )

        print(f"✓ Results saved to: {output_dir}/test_concepts.jsonl")
        print()

        # Generate HTML visualization
        try:
            html = lx.visualize(str(output_dir / "test_concepts.jsonl"))
            html_file = output_dir / "test_concepts.html"
            html_file.write_text(html)
            print(f"✓ HTML visualization: {html_file}")
            print(f"  Open in browser to review extractions interactively")
        except Exception as e:
            print(f"⚠ HTML generation skipped: {e}")

        print()
        print("=" * 70)
        print("Next Steps:")
        print("=" * 70)
        print("1. Review the HTML file in your browser")
        print("2. Check if concepts were extracted correctly")
        print("3. If quality is good (80%+): proceed to statutory references")
        print("4. If quality is low (<80%): refine examples and re-test")
        print()

        return True

    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_concept_extraction()
    sys.exit(0 if success else 1)
