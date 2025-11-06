"""
Progress Tracker - Track extraction progress in real-time.

Monitors extraction progress and provides status updates.
Part of Phase 3: Extraction Pipeline implementation.
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class CategoryProgress:
    """Progress for a single category."""
    category_name: str
    total_items: int = 0
    completed_items: int = 0
    status: str = "pending"  # pending, in_progress, completed, failed
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    error_message: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)

    @property
    def progress_percent(self) -> float:
        """Calculate progress percentage."""
        if self.total_items == 0:
            return 0.0
        return (self.completed_items / self.total_items) * 100


@dataclass
class ExtractionProgress:
    """Overall extraction progress."""
    source_id: str
    source_name: str
    total_categories: int
    completed_categories: int
    total_entities: int = 0
    total_relationships: int = 0
    status: str = "pending"  # pending, in_progress, completed, failed
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    categories: Dict[str, CategoryProgress] = None

    def __post_init__(self):
        if self.categories is None:
            self.categories = {}

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        data = asdict(self)
        # Convert CategoryProgress objects to dicts
        data["categories"] = {
            name: cat.to_dict()
            for name, cat in self.categories.items()
        }
        return data

    @property
    def progress_percent(self) -> float:
        """Calculate overall progress percentage."""
        if self.total_categories == 0:
            return 0.0
        return (self.completed_categories / self.total_categories) * 100

    @property
    def elapsed_time(self) -> Optional[float]:
        """Calculate elapsed time in seconds."""
        if not self.start_time:
            return None

        start = datetime.fromisoformat(self.start_time.replace('Z', '+00:00'))

        if self.end_time:
            end = datetime.fromisoformat(self.end_time.replace('Z', '+00:00'))
        else:
            end = datetime.utcnow()

        return (end - start).total_seconds()


class ProgressTracker:
    """
    Track extraction progress in real-time.

    Saves progress to JSON file for persistence and monitoring.
    """

    def __init__(self, project_dir: Path):
        """
        Initialize ProgressTracker.

        Args:
            project_dir: Project directory path
        """
        self.project_dir = Path(project_dir)
        self.progress_dir = self.project_dir / "data" / "progress"
        self.progress_dir.mkdir(parents=True, exist_ok=True)

    def start_extraction(
        self,
        source_id: str,
        source_name: str,
        categories: List[str]
    ) -> ExtractionProgress:
        """
        Start tracking extraction for a source.

        Args:
            source_id: Source identifier
            source_name: Source name
            categories: List of category names to extract

        Returns:
            ExtractionProgress object
        """
        progress = ExtractionProgress(
            source_id=source_id,
            source_name=source_name,
            total_categories=len(categories),
            completed_categories=0,
            status="in_progress",
            start_time=datetime.utcnow().isoformat() + "Z"
        )

        # Initialize category progress
        for cat_name in categories:
            progress.categories[cat_name] = CategoryProgress(
                category_name=cat_name,
                status="pending"
            )

        self._save_progress(progress)

        print(f"✓ Started extraction tracking for: {source_name}")
        print(f"  Categories: {len(categories)}")

        return progress

    def start_category(
        self,
        source_id: str,
        category_name: str,
        total_items: int = 0
    ):
        """
        Mark category extraction as started.

        Args:
            source_id: Source identifier
            category_name: Category name
            total_items: Expected number of items (optional)
        """
        progress = self._load_progress(source_id)
        if not progress:
            return

        if category_name in progress.categories:
            cat_progress = progress.categories[category_name]
            cat_progress.status = "in_progress"
            cat_progress.start_time = datetime.utcnow().isoformat() + "Z"
            cat_progress.total_items = total_items
            cat_progress.completed_items = 0

            self._save_progress(progress)

    def update_category(
        self,
        source_id: str,
        category_name: str,
        completed_items: int
    ):
        """
        Update category progress.

        Args:
            source_id: Source identifier
            category_name: Category name
            completed_items: Number of items completed
        """
        progress = self._load_progress(source_id)
        if not progress:
            return

        if category_name in progress.categories:
            cat_progress = progress.categories[category_name]
            cat_progress.completed_items = completed_items

            self._save_progress(progress)

    def complete_category(
        self,
        source_id: str,
        category_name: str,
        items_extracted: int
    ):
        """
        Mark category as completed.

        Args:
            source_id: Source identifier
            category_name: Category name
            items_extracted: Number of items extracted
        """
        progress = self._load_progress(source_id)
        if not progress:
            return

        if category_name in progress.categories:
            cat_progress = progress.categories[category_name]
            cat_progress.status = "completed"
            cat_progress.end_time = datetime.utcnow().isoformat() + "Z"
            cat_progress.completed_items = items_extracted
            cat_progress.total_items = items_extracted

            progress.completed_categories += 1
            progress.total_entities += items_extracted

            self._save_progress(progress)

            print(f"  ✓ {category_name}: {items_extracted} entities extracted")

    def fail_category(
        self,
        source_id: str,
        category_name: str,
        error_message: str
    ):
        """
        Mark category as failed.

        Args:
            source_id: Source identifier
            category_name: Category name
            error_message: Error description
        """
        progress = self._load_progress(source_id)
        if not progress:
            return

        if category_name in progress.categories:
            cat_progress = progress.categories[category_name]
            cat_progress.status = "failed"
            cat_progress.end_time = datetime.utcnow().isoformat() + "Z"
            cat_progress.error_message = error_message

            self._save_progress(progress)

            print(f"  ✗ {category_name}: Failed - {error_message}")

    def complete_extraction(
        self,
        source_id: str,
        total_relationships: int = 0
    ):
        """
        Mark extraction as completed.

        Args:
            source_id: Source identifier
            total_relationships: Number of relationships extracted
        """
        progress = self._load_progress(source_id)
        if not progress:
            return

        progress.status = "completed"
        progress.end_time = datetime.utcnow().isoformat() + "Z"
        progress.total_relationships = total_relationships

        self._save_progress(progress)

        elapsed = progress.elapsed_time
        print(f"\n✓ Extraction completed!")
        print(f"  Entities: {progress.total_entities:,}")
        print(f"  Relationships: {progress.total_relationships:,}")
        print(f"  Time: {elapsed:.1f}s")

    def fail_extraction(self, source_id: str, error_message: str):
        """
        Mark extraction as failed.

        Args:
            source_id: Source identifier
            error_message: Error description
        """
        progress = self._load_progress(source_id)
        if not progress:
            return

        progress.status = "failed"
        progress.end_time = datetime.utcnow().isoformat() + "Z"

        self._save_progress(progress)

        print(f"\n✗ Extraction failed: {error_message}")

    def get_progress(self, source_id: str) -> Optional[ExtractionProgress]:
        """
        Get current progress for a source.

        Args:
            source_id: Source identifier

        Returns:
            ExtractionProgress object or None if not found
        """
        return self._load_progress(source_id)

    def display_progress(self, source_id: str):
        """
        Display current progress in terminal.

        Args:
            source_id: Source identifier
        """
        progress = self._load_progress(source_id)
        if not progress:
            print(f"No progress found for: {source_id}")
            return

        print(f"\n{'='*70}")
        print(f"EXTRACTION PROGRESS: {progress.source_name}")
        print(f"{'='*70}")

        print(f"\nOverall: {progress.progress_percent:.1f}% "
              f"({progress.completed_categories}/{progress.total_categories} categories)")
        print(f"Status: {progress.status}")

        if progress.elapsed_time:
            print(f"Elapsed: {progress.elapsed_time:.1f}s")

        print(f"\nCategories:")
        for cat_name, cat_progress in progress.categories.items():
            status_icon = {
                "pending": "⏳",
                "in_progress": "🔄",
                "completed": "✓",
                "failed": "✗"
            }.get(cat_progress.status, "?")

            print(f"  {status_icon} {cat_name}: {cat_progress.status}")
            if cat_progress.status in ["in_progress", "completed"]:
                print(f"      {cat_progress.completed_items} items")

        print(f"\nTotals:")
        print(f"  Entities: {progress.total_entities:,}")
        print(f"  Relationships: {progress.total_relationships:,}")

        print(f"\n{'='*70}\n")

    def _save_progress(self, progress: ExtractionProgress):
        """Save progress to JSON file."""
        progress_file = self.progress_dir / f"{progress.source_id}.json"

        with open(progress_file, 'w') as f:
            json.dump(progress.to_dict(), f, indent=2)

    def _load_progress(self, source_id: str) -> Optional[ExtractionProgress]:
        """Load progress from JSON file."""
        progress_file = self.progress_dir / f"{source_id}.json"

        if not progress_file.exists():
            return None

        with open(progress_file, 'r') as f:
            data = json.load(f)

        # Reconstruct CategoryProgress objects
        categories = {}
        for cat_name, cat_data in data.get("categories", {}).items():
            categories[cat_name] = CategoryProgress(**cat_data)

        data["categories"] = categories

        return ExtractionProgress(**data)


# Example usage
if __name__ == "__main__":
    from pathlib import Path
    import time

    # Test progress tracking
    project_dir = Path("projects/test-project")
    tracker = ProgressTracker(project_dir)

    # Start extraction
    progress = tracker.start_extraction(
        "test-source",
        "Test Material",
        ["actors", "procedures", "deadlines"]
    )

    # Simulate extraction
    for category in ["actors", "procedures", "deadlines"]:
        tracker.start_category("test-source", category)
        time.sleep(0.5)
        tracker.complete_category("test-source", category, items_extracted=10)

    tracker.complete_extraction("test-source", total_relationships=5)

    # Display final progress
    tracker.display_progress("test-source")
