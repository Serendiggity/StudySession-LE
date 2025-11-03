"""
Extraction engine for processing documents with Lang Extract.
Orchestrates multi-pass extraction across all categories.

Version: 2.0 - Atomic extraction approach
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional
import langextract as lx
from .schemas_v2_atomic import ExtractionCategory, ALL_CATEGORIES, get_category


class ExtractionEngine:
    """
    Main extraction orchestrator.

    Handles:
    - Loading examples for each category
    - Multi-pass extraction
    - Progress tracking
    - Result aggregation
    - HTML visualization generation
    """

    def __init__(self, model_id: str = "gemini-2.5-flash", api_key: Optional[str] = None):
        """
        Initialize extraction engine.

        Args:
            model_id: Gemini model to use (default: gemini-2.5-flash)
            api_key: API key (reads from environment if not provided)
        """
        import os
        self.model_id = model_id
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.logger = logging.getLogger(__name__)

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")

        self.logger.info(f"Initialized ExtractionEngine with model: {model_id}")

    def extract_category(self,
                        text: str,
                        category: ExtractionCategory,
                        passes: int = 3,
                        max_workers: int = 10) -> lx.data.AnnotatedDocument:
        """
        Extract single category with multiple passes.

        Args:
            text: Text to extract from
            category: Category definition with examples
            passes: Number of extraction passes (default: 3 for thoroughness)
            max_workers: Parallel workers (default: 10, adjust based on rate limits)

        Returns:
            AnnotatedDocument with extractions
        """
        self.logger.info(f"=" * 70)
        self.logger.info(f"Extracting category: {category.name}")
        self.logger.info(f"Examples: {len(category.examples)}")
        self.logger.info(f"Passes: {passes}")
        self.logger.info(f"=" * 70)

        try:
            result = lx.extract(
                text_or_documents=text,
                prompt_description=category.prompt_template,
                examples=category.examples,
                model_id=self.model_id,
                extraction_passes=passes,
                max_workers=max_workers
                # fence_output=True - Not needed in 1.0.9+ (PR #239 fixed parsing issues)
            )

            self.logger.info(f"✓ Extracted {len(result.extractions)} items for category: {category.name}")
            return result

        except Exception as e:
            self.logger.error(f"✗ Extraction failed for {category.name}: {e}")
            raise

    def extract_all_categories(self,
                              text: str,
                              categories: List[str] = None,
                              passes: int = 3,
                              max_workers: int = 10,
                              output_dir: Path = None) -> Dict[str, lx.data.AnnotatedDocument]:
        """
        Extract all categories sequentially.

        Args:
            text: Text to extract from
            categories: List of category names (default: ALL_CATEGORIES)
            passes: Number of passes per category
            max_workers: Parallel workers
            output_dir: Where to save results (default: data/output/knowledge_base)

        Returns:
            Dictionary mapping category names to AnnotatedDocuments
        """
        if categories is None:
            categories = ALL_CATEGORIES

        if output_dir is None:
            output_dir = Path("data/output/knowledge_base")

        output_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info(f"\n{'='*70}")
        self.logger.info(f"FULL EXTRACTION - {len(categories)} categories")
        self.logger.info(f"Text length: {len(text):,} characters")
        self.logger.info(f"Passes per category: {passes}")
        self.logger.info(f"Output directory: {output_dir}")
        self.logger.info(f"{'='*70}\n")

        results = {}

        # Load examples
        import sys
        # Add data directory to path (Path already imported at module level)
        data_dir = Path(__file__).parent.parent.parent / "data" / "examples"
        sys.path.insert(0, str(data_dir))
        from content_examples import ALL_EXAMPLES

        for i, category_name in enumerate(categories, 1):
            self.logger.info(f"\n[{i}/{len(categories)}] Processing: {category_name}")

            # Get examples for this category
            examples = ALL_EXAMPLES.get(category_name, [])

            if not examples:
                self.logger.warning(f"No examples found for {category_name}, skipping...")
                continue

            # Create category definition
            category = self._create_category_def(category_name, examples)

            # Extract
            try:
                result = self.extract_category(
                    text=text,
                    category=category,
                    passes=passes,
                    max_workers=max_workers
                )

                results[category_name] = result

                # Save immediately
                self._save_result(result, category_name, output_dir)

                self.logger.info(f"✓ {category_name}: {len(result.extractions)} items extracted and saved")

            except Exception as e:
                self.logger.error(f"✗ Failed to extract {category_name}: {e}")
                # Continue with other categories
                continue

        # Generate summary
        total_extractions = sum(len(r.extractions) for r in results.values())
        self.logger.info(f"\n{'='*70}")
        self.logger.info(f"EXTRACTION COMPLETE")
        self.logger.info(f"Categories processed: {len(results)}/{len(categories)}")
        self.logger.info(f"Total extractions: {total_extractions}")
        self.logger.info(f"Results saved to: {output_dir}")
        self.logger.info(f"{'='*70}\n")

        return results

    def _create_category_def(self, category_name: str, examples: List) -> ExtractionCategory:
        """
        Create category definition with examples.

        Uses atomic schemas_v2 with get_category() function.
        All categories are now registered in CATEGORY_CREATORS.
        """
        try:
            return get_category(category_name, examples)
        except ValueError as e:
            self.logger.error(f"Unknown category: {category_name}")
            raise

    def _save_result(self, result: lx.data.AnnotatedDocument, category_name: str, output_dir: Path):
        """Save extraction result to JSONL."""
        try:
            lx.io.save_annotated_documents(
                [result],
                output_name=category_name,
                output_dir=str(output_dir)
            )
            self.logger.info(f"Saved {category_name}.jsonl")
        except Exception as e:
            self.logger.error(f"Failed to save {category_name}: {e}")

    def generate_html_visualizations(self, output_dir: Path = None):
        """
        Generate HTML visualizations for all extracted categories.

        Args:
            output_dir: Directory containing .jsonl files
        """
        if output_dir is None:
            output_dir = Path("data/output/knowledge_base")

        self.logger.info(f"\nGenerating HTML visualizations from {output_dir}")

        jsonl_files = list(output_dir.glob("*.jsonl"))

        for jsonl_file in jsonl_files:
            try:
                html_content = lx.visualize(str(jsonl_file))
                html_file = jsonl_file.with_suffix('.html')
                html_file.write_text(html_content)
                self.logger.info(f"✓ Generated: {html_file.name}")
            except Exception as e:
                self.logger.warning(f"✗ Failed to generate HTML for {jsonl_file.name}: {e}")

        self.logger.info(f"\n✓ HTML visualizations complete: {len(jsonl_files)} files")
