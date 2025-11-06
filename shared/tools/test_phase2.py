#!/usr/bin/env python3
"""
Test Phase 2 Components

Quick test of MaterialAnalyzer and SchemaSuggester on sample material.
"""

import sys
import json
from pathlib import Path

# Add shared/src to Python path
shared_dir = Path(__file__).parent.parent
sys.path.insert(0, str(shared_dir / "src"))

from analysis import MaterialAnalyzer, SchemaSuggester


def test_phase2():
    """Test Phase 2 components on radiology sample."""

    print("\n" + "="*70)
    print("PHASE 2 TEST - AI Material Analysis")
    print("="*70)

    # Read test material
    test_file = Path("data/test_materials/radiology_sample.txt")
    print(f"\nReading test material: {test_file}")

    with open(test_file, 'r') as f:
        content = f.read()

    print(f"✓ Loaded {len(content)} characters ({len(content.split())} words)")

    # Step 1: Analyze material
    print("\n[Step 1] Analyzing material with AI...")
    print("(This may take 10-20 seconds...)")

    analyzer = MaterialAnalyzer()
    analysis = analyzer.analyze(content, content_type="text")

    print(f"✓ Analysis complete\n")

    # Show results
    print("─"*70)
    print("DOCUMENT STRUCTURE")
    print("─"*70)
    structure = analysis['document_structure']
    print(f"Has sections: {structure['has_sections']}")
    print(f"Has numbered items: {structure['has_numbered_items']}")
    print(f"Has definitions: {structure['has_definitions']}")
    print(f"Hierarchical: {structure['hierarchical']}")
    print(f"Section pattern: {structure['section_pattern']}")

    print("\n" + "─"*70)
    print("DETECTED PATTERNS")
    print("─"*70)
    for pattern in analysis['detected_patterns']:
        print(f"  • {pattern}")

    print("\n" + "─"*70)
    print("RECOMMENDED CATEGORIES")
    print("─"*70)
    for cat in analysis['recommended_categories']:
        print(f"\n{cat['name']}")
        print(f"  Description: {cat['description']}")
        print(f"  Confidence: {cat['confidence']:.2f}")
        print(f"  Examples: {', '.join(cat['examples'][:5])}")
        if 'rationale' in cat:
            print(f"  Rationale: {cat['rationale']}")

    print("\n" + "─"*70)
    print("DOMAIN INDICATORS")
    print("─"*70)
    domain = analysis['domain_indicators']
    print(f"Primary domain: {domain['primary_domain']}")
    print(f"Confidence: {domain['confidence']:.2f}")
    if domain.get('secondary_domains'):
        print(f"Secondary domains: {', '.join(domain['secondary_domains'])}")

    print("\n" + "─"*70)
    print("SAMPLE ENTITIES")
    print("─"*70)
    for cat_name, examples in analysis['sample_entities'].items():
        print(f"{cat_name}: {', '.join(examples[:5])}")

    # Step 2: Suggest schema
    print("\n\n[Step 2] Generating extraction schema with AI...")
    print("(This may take 10-20 seconds...)")

    suggester = SchemaSuggester()
    schema = suggester.suggest_schema(
        analysis,
        domain="medicine",
        project_name="Radiology Knowledge Base"
    )

    print(f"✓ Schema generated\n")

    # Show schema
    print("="*70)
    print("GENERATED SCHEMA")
    print("="*70)

    categories = schema['entity_schema']['categories']
    relationships = schema['entity_schema']['relationship_types']
    recommendations = schema['extraction_recommendations']

    print(f"\nEntity Categories ({len(categories)}):")
    for cat in categories:
        print(f"\n  {cat['name']}")
        print(f"    Description: {cat['description']}")
        print(f"    Attributes: {', '.join(cat['attributes'])}")
        print(f"    Confidence: {cat['confidence']:.2f}")
        print(f"    Examples: {', '.join(cat['examples'][:3])}")

    print(f"\n\nRelationship Types ({len(relationships)}):")
    for rel in relationships:
        print(f"\n  {rel['name']}")
        print(f"    Description: {rel['description']}")
        print(f"    Structure: {rel['structure']}")
        print(f"    Critical field: {rel['critical_field']}")

    print(f"\n\nExtraction Recommendations:")
    print(f"  Granularity: {recommendations['granularity']}")
    print(f"  Min examples per category: {recommendations['min_examples_per_category']}")
    print(f"  Use relationship_text: {recommendations['use_relationship_text']}")

    # Save results
    output_dir = Path("data/output/phase2_test")
    output_dir.mkdir(parents=True, exist_ok=True)

    analyzer.save_analysis(analysis, output_dir / "analysis.json")
    suggester.save_schema(schema, output_dir / "schema.json")

    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)
    print(f"\nResults saved to: {output_dir}")
    print(f"  - analysis.json: Full material analysis")
    print(f"  - schema.json: Suggested extraction schema")

    print(f"\n✓ Phase 2 components working correctly!")
    print(f"\nNext steps:")
    print(f"  1. Review suggested schema in {output_dir}/schema.json")
    print(f"  2. Use analyze_and_create_project.py to create full project")
    print(f"  3. Run extraction with Lang Extract API")


if __name__ == "__main__":
    try:
        test_phase2()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
