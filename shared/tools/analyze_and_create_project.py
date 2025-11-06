#!/usr/bin/env python3
"""
Analyze Material and Create Project - Phase 2 Integration Workflow

This script demonstrates the complete AI-assisted project creation workflow:
1. MaterialAnalyzer: Analyze document structure
2. SchemaSuggester: Suggest extraction schema
3. ExampleSelector: User refines examples
4. CommonGroundFinder: Map to existing projects
5. ProjectManager: Create new project with schema

Usage:
    python3 analyze_and_create_project.py --file <path> --name "Project Name" --domain <domain>
"""

import sys
import json
import argparse
from pathlib import Path

# Add shared/src to Python path
shared_dir = Path(__file__).parent.parent
sys.path.insert(0, str(shared_dir / "src"))

from analysis import MaterialAnalyzer, SchemaSuggester, ExampleSelector, CommonGroundFinder
from project import ProjectManager


def read_file(file_path: Path) -> str:
    """Read content from file."""
    with open(file_path, 'r') as f:
        return f.read()


def analyze_and_create_project(
    file_path: Path,
    project_name: str,
    domain: str,
    description: str = "",
    interactive: bool = True
):
    """
    Complete workflow: analyze material and create project.

    Args:
        file_path: Path to material file
        project_name: Name for new project
        domain: Domain/subject area
        description: Project description
        interactive: If True, prompt user for example selection
    """
    print("\n" + "="*70)
    print("AI-ASSISTED PROJECT CREATION WORKFLOW")
    print("="*70)
    print(f"\nProject: {project_name}")
    print(f"Domain: {domain}")
    print(f"Material: {file_path}")
    print()

    # -------------------------------------------------------------------------
    # Step 1: Read material
    # -------------------------------------------------------------------------
    print("[1/6] Reading material...")
    content = read_file(file_path)
    print(f"✓ Loaded {len(content)} characters ({len(content.split())} words)")

    # -------------------------------------------------------------------------
    # Step 2: Analyze material
    # -------------------------------------------------------------------------
    print("\n[2/6] Analyzing material structure with AI...")
    analyzer = MaterialAnalyzer()
    analysis = analyzer.analyze(content, content_type="text")

    print(f"✓ Analysis complete")
    print(f"  - Document Structure: {analysis['document_structure']['section_pattern']}")
    print(f"  - Detected Patterns: {len(analysis['detected_patterns'])} patterns")
    print(f"  - Recommended Categories: {len(analysis['recommended_categories'])} categories")
    print(f"  - Primary Domain: {analysis['domain_indicators']['primary_domain']} "
          f"(confidence: {analysis['domain_indicators']['confidence']:.2f})")

    # Show recommended categories
    print(f"\n  Suggested Categories:")
    for cat in analysis['recommended_categories']:
        print(f"    • {cat['name']}: {cat['description']} "
              f"(confidence: {cat['confidence']:.2f})")

    # -------------------------------------------------------------------------
    # Step 3: Suggest schema
    # -------------------------------------------------------------------------
    print("\n[3/6] Generating extraction schema with AI...")
    suggester = SchemaSuggester()
    schema = suggester.suggest_schema(analysis, domain, project_name)

    categories = schema['entity_schema']['categories']
    relationships = schema['entity_schema']['relationship_types']

    print(f"✓ Schema generated")
    print(f"  - Entity Categories: {len(categories)}")
    print(f"  - Relationship Types: {len(relationships)}")
    print(f"  - Extraction Granularity: {schema['extraction_recommendations']['granularity']}")

    # -------------------------------------------------------------------------
    # Step 4: Refine examples (interactive)
    # -------------------------------------------------------------------------
    if interactive:
        print("\n[4/6] Example selection (interactive)...")
        selector = ExampleSelector()
        user_examples = selector.review_and_refine(
            categories,
            content,
            interactive=True
        )

        # Apply user examples to schema
        schema = suggester.refine_with_user_examples(schema, user_examples)
        print(f"✓ Examples refined by user")
    else:
        print("\n[4/6] Skipping example selection (non-interactive mode)")

    # -------------------------------------------------------------------------
    # Step 5: Find common ground with existing projects
    # -------------------------------------------------------------------------
    print("\n[5/6] Finding common ground with existing projects...")
    pm = ProjectManager()
    existing_projects = pm.list_projects()

    if existing_projects:
        # Load existing project schemas
        existing_schemas = []
        for project in existing_projects:
            config = pm.get_project_config(project.project_id)
            if config:
                existing_schemas.append(config)

        # Find mappings
        finder = CommonGroundFinder()
        mappings = finder.find_mappings(
            schema,
            existing_schemas,
            project_name,
            domain
        )

        print(f"✓ Found mappings")
        print(f"  - Category Mappings: {len(mappings['mappings'])}")
        print(f"  - Unified Categories: {len(mappings['unified_categories'])}")
        print(f"  - Recommendations: {len(mappings['recommendations'])}")

        # Show visualization
        print("\n" + finder.visualize_mappings(mappings))

        # Save mappings
        mappings_path = Path(f"data/output/mappings/{project_name.lower().replace(' ', '-')}-mappings.json")
        finder.save_mappings(mappings, mappings_path)

    else:
        print(f"✓ No existing projects to map to")

    # -------------------------------------------------------------------------
    # Step 6: Create project
    # -------------------------------------------------------------------------
    print("\n[6/6] Creating project...")

    # Generate full config
    config = suggester.generate_project_config(
        schema,
        project_name,
        domain,
        description
    )

    # Create project
    project = pm.create_project(
        name=project_name,
        domain=domain,
        description=description
    )

    # Update config with schema
    pm.update_project_config(
        project.project_id,
        {
            "entity_schema": config["entity_schema"],
            "extraction_config": config["extraction_config"]
        }
    )

    print(f"✓ Project created successfully!")
    print(f"\n{'='*70}")
    print("PROJECT CREATION COMPLETE")
    print(f"{'='*70}")
    print(f"\nProject ID: {project.project_id}")
    print(f"Database: {project.database_path}")
    print(f"Entity Categories: {len(categories)}")
    print(f"Relationship Types: {len(relationships)}")

    print(f"\nNext steps:")
    print(f"  1. Switch to project: python3 shared/tools/kb_cli.py projects switch {project.project_id}")
    print(f"  2. Add source material for extraction")
    print(f"  3. Run extraction with Lang Extract API")

    # Save analysis and schema for reference
    output_dir = Path(f"projects/{project.project_id}/data/input")
    output_dir.mkdir(parents=True, exist_ok=True)

    analyzer.save_analysis(analysis, output_dir / "material_analysis.json")
    suggester.save_schema(schema, output_dir / "suggested_schema.json")

    print(f"\n✓ Analysis and schema saved to: {output_dir}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze material and create project with AI assistance"
    )

    parser.add_argument(
        "--file",
        required=True,
        help="Path to material file (text, markdown, etc.)"
    )

    parser.add_argument(
        "--name",
        required=True,
        help="Project name"
    )

    parser.add_argument(
        "--domain",
        required=True,
        help="Domain/subject area (e.g., law, medicine, engineering)"
    )

    parser.add_argument(
        "--description",
        default="",
        help="Project description"
    )

    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Skip interactive example selection"
    )

    args = parser.parse_args()

    # Validate file exists
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        return 1

    try:
        analyze_and_create_project(
            file_path,
            args.name,
            args.domain,
            args.description,
            interactive=not args.non_interactive
        )

        return 0

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
