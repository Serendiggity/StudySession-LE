"""
Extraction Runner - Orchestrate the extraction pipeline.

Main component that coordinates all extraction steps.
Part of Phase 3: Extraction Pipeline implementation.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

from .source_manager import SourceManager, Source
from .lang_extract_client import LangExtractClient, MockLangExtractClient
from .progress_tracker import ProgressTracker
from .database_loader import DatabaseLoader


class ExtractionRunner:
    """
    Orchestrate the complete extraction pipeline.

    Steps:
    1. Load source material
    2. Get schema and examples
    3. Extract entities (category by category)
    4. Extract relationships
    5. Load into database
    6. Track progress
    7. Validate quality
    """

    def __init__(
        self,
        project_dir: Path,
        use_mock: bool = False,
        api_key: Optional[str] = None
    ):
        """
        Initialize ExtractionRunner.

        Args:
            project_dir: Project directory path
            use_mock: Use mock client for testing (no API calls)
            api_key: Lang Extract API key (optional)
        """
        self.project_dir = Path(project_dir)
        self.config_file = self.project_dir / "config.json"

        # Initialize components
        self.source_manager = SourceManager(project_dir)
        self.progress_tracker = ProgressTracker(project_dir)
        self.database_loader = DatabaseLoader(project_dir)

        # Initialize Lang Extract client
        if use_mock:
            self.client = MockLangExtractClient()
            print("Using MOCK Lang Extract client (no API calls)")
        else:
            self.client = LangExtractClient(api_key)

        # Load project config
        self.config = self._load_config()

    def extract_source(
        self,
        source_id: str,
        examples: Optional[Dict[str, List[Dict]]] = None
    ) -> Dict:
        """
        Extract knowledge from a source.

        Args:
            source_id: Source identifier
            examples: Optional user-provided examples per category

        Returns:
            Extraction results summary
        """
        print(f"\n{'='*70}")
        print(f"STARTING EXTRACTION")
        print(f"{'='*70}\n")

        # Get source
        source = self.source_manager.get_source(source_id)
        if not source:
            raise ValueError(f"Source not found: {source_id}")

        print(f"Source: {source.source_name}")
        print(f"Type: {source.source_type}")
        print(f"Size: {source.file_size:,} characters")

        # Get schema
        schema = self.config.get("entity_schema", {})
        categories = schema.get("categories", [])
        relationship_types = schema.get("relationship_types", [])

        print(f"\nSchema:")
        print(f"  Categories: {len(categories)}")
        print(f"  Relationship types: {len(relationship_types)}")

        # Initialize database if not exists
        if not self.database_loader.database_path.exists():
            print(f"\nInitializing database...")
            self.database_loader.initialize_database({"entity_schema": schema})

        # Read source content
        content = self.source_manager.read_source_content(source_id)

        # Start progress tracking
        category_names = [cat["name"] for cat in categories]
        progress = self.progress_tracker.start_extraction(
            source_id,
            source.source_name,
            category_names
        )

        print(f"\nExtracting {len(categories)} categories...")

        # Extract entities category by category
        total_entities = 0

        for cat in categories:
            cat_name = cat["name"]
            attributes = cat["attributes"]
            cat_examples = examples.get(cat_name, []) if examples else cat.get("examples", [])

            print(f"\n[{cat_name}]")
            self.progress_tracker.start_category(source_id, cat_name)

            try:
                # Convert examples to attribute dictionaries if needed
                if cat_examples and isinstance(cat_examples[0], str):
                    # Examples are strings, convert to dicts
                    cat_examples = [
                        {attributes[0]: ex} for ex in cat_examples
                    ]

                # Extract entities
                entities = self.client.extract_entities(
                    text=content,
                    category=cat_name,
                    attributes=attributes,
                    examples=cat_examples[:5],  # Use first 5 examples
                    granularity="sentence"
                )

                # Load into database
                loaded_count = self.database_loader.load_entities(
                    cat_name,
                    entities,
                    source_id
                )

                self.progress_tracker.complete_category(
                    source_id,
                    cat_name,
                    loaded_count
                )

                total_entities += loaded_count

            except Exception as e:
                self.progress_tracker.fail_category(
                    source_id,
                    cat_name,
                    str(e)
                )
                print(f"  Error: {e}")

        # Extract relationships
        print(f"\nExtracting relationships...")
        total_relationships = 0

        for rel in relationship_types:
            rel_name = rel["name"]
            structure = rel.get("structure", "")
            examples = rel.get("examples", [])

            print(f"\n[{rel_name}]")

            try:
                relationships = self.client.extract_relationships(
                    text=content,
                    relationship_type=rel_name,
                    structure=structure,
                    examples=examples,
                    entity_categories=category_names
                )

                # Load into database
                loaded_count = self.database_loader.load_relationships(
                    rel_name,
                    relationships,
                    source_id
                )

                print(f"  ✓ {rel_name}: {loaded_count} relationships extracted")
                total_relationships += loaded_count

            except Exception as e:
                print(f"  Error: {e}")

        # Complete extraction
        self.progress_tracker.complete_extraction(
            source_id,
            total_relationships
        )

        # Mark source as extracted
        self.source_manager.mark_extracted(
            source_id,
            total_entities,
            total_relationships
        )

        # Update project statistics
        self._update_statistics()

        # Get final statistics
        stats = self.database_loader.get_statistics()

        print(f"\n{'='*70}")
        print(f"EXTRACTION COMPLETE")
        print(f"{'='*70}")
        print(f"\nExtracted from this source:")
        print(f"  Entities: {total_entities:,}")
        print(f"  Relationships: {total_relationships:,}")
        print(f"\nTotal in database:")
        print(f"  Entities: {stats['total_entities']:,}")
        print(f"  Relationships: {stats['total_relationships']:,}")

        return {
            "source_id": source_id,
            "source_name": source.source_name,
            "entities_extracted": total_entities,
            "relationships_extracted": total_relationships,
            "total_entities": stats["total_entities"],
            "total_relationships": stats["total_relationships"],
            "status": "completed"
        }

    def extract_all_sources(self) -> Dict:
        """
        Extract all unextracted sources.

        Returns:
            Summary of extraction results
        """
        unextracted = self.source_manager.get_unextracted_sources()

        if not unextracted:
            print("No unextracted sources found.")
            return {
                "sources_processed": 0,
                "total_entities": 0,
                "total_relationships": 0
            }

        print(f"Found {len(unextracted)} unextracted sources\n")

        total_entities = 0
        total_relationships = 0

        for source in unextracted:
            try:
                result = self.extract_source(source.source_id)
                total_entities += result["entities_extracted"]
                total_relationships += result["relationships_extracted"]

            except Exception as e:
                print(f"\nError extracting {source.source_name}: {e}")

        return {
            "sources_processed": len(unextracted),
            "total_entities": total_entities,
            "total_relationships": total_relationships
        }

    def validate_extraction(self, source_id: str) -> Dict:
        """
        Validate extraction quality for a source.

        Args:
            source_id: Source identifier

        Returns:
            Validation results
        """
        source = self.source_manager.get_source(source_id)
        if not source:
            raise ValueError(f"Source not found: {source_id}")

        # Get database statistics
        stats = self.database_loader.get_statistics()

        # Validate
        issues = []

        # Check if entities were extracted
        if source.entity_count == 0:
            issues.append("No entities extracted")

        # Check if relationships were extracted
        if source.relationship_count == 0:
            issues.append("No relationships extracted")

        # Check entity coverage
        schema = self.config.get("entity_schema", {})
        categories = schema.get("categories", [])

        for cat in categories:
            cat_name = cat["name"]
            count = stats["entities_by_category"].get(cat_name, 0)
            if count == 0:
                issues.append(f"No {cat_name} entities found")

        return {
            "source_id": source_id,
            "valid": len(issues) == 0,
            "issues": issues,
            "entity_count": source.entity_count,
            "relationship_count": source.relationship_count
        }

    def _load_config(self) -> Dict:
        """Load project configuration."""
        if not self.config_file.exists():
            raise ValueError(f"Config not found: {self.config_file}")

        with open(self.config_file, 'r') as f:
            return json.load(f)

    def _update_statistics(self):
        """Update project statistics in config."""
        stats = self.database_loader.get_statistics()

        self.config["statistics"] = {
            "total_entities": stats["total_entities"],
            "total_relationships": stats["total_relationships"],
            "entities_by_category": stats["entities_by_category"],
            "relationships_by_type": stats["relationships_by_type"]
        }

        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)


# Example usage
if __name__ == "__main__":
    from pathlib import Path

    # Test extraction with mock client
    project_dir = Path("projects/test-project")
    runner = ExtractionRunner(project_dir, use_mock=True)

    # Add test source
    test_file = Path("data/test_materials/radiology_sample.txt")
    if test_file.exists():
        source = runner.source_manager.add_source(
            test_file,
            "Test Material"
        )

        # Extract
        result = runner.extract_source(source.source_id)

        print(f"\nExtraction result:")
        print(json.dumps(result, indent=2))
    else:
        print(f"Test file not found: {test_file}")
