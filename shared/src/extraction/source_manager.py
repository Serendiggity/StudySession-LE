"""
Source Manager - Manage source materials for projects.

Handles adding, removing, and tracking source materials for extraction.
Part of Phase 3: Extraction Pipeline implementation.
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class Source:
    """Represents a source material for extraction."""
    source_id: str
    source_name: str
    source_type: str  # "pdf", "text", "markdown", "url"
    file_path: str
    added_at: str
    file_size: int
    content_hash: str
    extracted: bool = False
    extraction_date: Optional[str] = None
    entity_count: int = 0
    relationship_count: int = 0

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)


class SourceManager:
    """
    Manage source materials for knowledge base projects.

    Handles:
    - Adding source materials (text, PDF, markdown, URLs)
    - Tracking extraction status
    - Content deduplication
    - Source metadata management
    """

    def __init__(self, project_dir: Path):
        """
        Initialize SourceManager.

        Args:
            project_dir: Project directory path
        """
        self.project_dir = Path(project_dir)
        self.sources_dir = self.project_dir / "sources"
        self.config_file = self.project_dir / "config.json"

        # Ensure directories exist
        self.sources_dir.mkdir(parents=True, exist_ok=True)

    def add_source(
        self,
        file_path: Path,
        source_name: Optional[str] = None,
        source_type: Optional[str] = None
    ) -> Source:
        """
        Add a source material to the project.

        Args:
            file_path: Path to source file
            source_name: Optional custom name (defaults to filename)
            source_type: Optional type override (auto-detected from extension)

        Returns:
            Source object

        Raises:
            ValueError: If file doesn't exist or already added
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise ValueError(f"File not found: {file_path}")

        # Auto-detect source type
        if source_type is None:
            ext = file_path.suffix.lower()
            type_map = {
                ".txt": "text",
                ".md": "markdown",
                ".pdf": "pdf",
                ".html": "html"
            }
            source_type = type_map.get(ext, "unknown")

        # Generate source ID and name
        if source_name is None:
            source_name = file_path.stem

        source_id = self._generate_source_id(source_name)

        # Check if already exists
        if self._source_exists(source_id):
            raise ValueError(f"Source already exists: {source_name}")

        # Read content and compute hash
        content = file_path.read_text()
        content_hash = self._compute_hash(content)

        # Check for duplicate content
        duplicate = self._find_duplicate_content(content_hash)
        if duplicate:
            raise ValueError(
                f"Duplicate content detected. "
                f"This material is already added as '{duplicate}'"
            )

        # Copy file to project sources directory
        dest_path = self.sources_dir / f"{source_id}{file_path.suffix}"
        dest_path.write_text(content)

        # Create source object
        source = Source(
            source_id=source_id,
            source_name=source_name,
            source_type=source_type,
            file_path=str(dest_path.relative_to(self.project_dir)),
            added_at=datetime.utcnow().isoformat() + "Z",
            file_size=len(content),
            content_hash=content_hash,
            extracted=False
        )

        # Add to project config
        self._add_to_config(source)

        print(f"✓ Added source: {source_name}")
        print(f"  Type: {source_type}")
        print(f"  Size: {len(content):,} characters")
        print(f"  ID: {source_id}")

        return source

    def list_sources(self) -> List[Source]:
        """
        List all sources in the project.

        Returns:
            List of Source objects
        """
        config = self._load_config()
        sources_data = config.get("sources", [])

        sources = []
        for data in sources_data:
            source = Source(**data)
            sources.append(source)

        return sources

    def get_source(self, source_id: str) -> Optional[Source]:
        """
        Get a specific source by ID.

        Args:
            source_id: Source identifier

        Returns:
            Source object or None if not found
        """
        sources = self.list_sources()
        for source in sources:
            if source.source_id == source_id:
                return source
        return None

    def remove_source(self, source_id: str, confirm: bool = False):
        """
        Remove a source from the project.

        Args:
            source_id: Source identifier
            confirm: Must be True to actually delete

        Raises:
            ValueError: If confirm is False or source not found
        """
        if not confirm:
            raise ValueError("Must set confirm=True to delete source")

        source = self.get_source(source_id)
        if not source:
            raise ValueError(f"Source not found: {source_id}")

        # Delete file
        file_path = self.project_dir / source.file_path
        if file_path.exists():
            file_path.unlink()

        # Remove from config
        self._remove_from_config(source_id)

        print(f"✓ Removed source: {source.source_name}")

    def mark_extracted(
        self,
        source_id: str,
        entity_count: int,
        relationship_count: int
    ):
        """
        Mark a source as extracted and update statistics.

        Args:
            source_id: Source identifier
            entity_count: Number of entities extracted
            relationship_count: Number of relationships extracted
        """
        config = self._load_config()
        sources = config.get("sources", [])

        for source in sources:
            if source["source_id"] == source_id:
                source["extracted"] = True
                source["extraction_date"] = datetime.utcnow().isoformat() + "Z"
                source["entity_count"] = entity_count
                source["relationship_count"] = relationship_count
                break

        self._save_config(config)

    def get_unextracted_sources(self) -> List[Source]:
        """
        Get all sources that haven't been extracted yet.

        Returns:
            List of unextracted Source objects
        """
        all_sources = self.list_sources()
        return [s for s in all_sources if not s.extracted]

    def read_source_content(self, source_id: str) -> str:
        """
        Read content of a source file.

        Args:
            source_id: Source identifier

        Returns:
            Source content as string

        Raises:
            ValueError: If source not found
        """
        source = self.get_source(source_id)
        if not source:
            raise ValueError(f"Source not found: {source_id}")

        file_path = self.project_dir / source.file_path
        return file_path.read_text()

    def _generate_source_id(self, source_name: str) -> str:
        """Generate unique source ID from name."""
        # Convert to lowercase, replace spaces with hyphens
        base_id = source_name.lower().replace(" ", "-")
        # Remove special characters
        base_id = "".join(c for c in base_id if c.isalnum() or c == "-")

        # Check uniqueness, add number if needed
        candidate = base_id
        counter = 1
        while self._source_exists(candidate):
            candidate = f"{base_id}-{counter}"
            counter += 1

        return candidate

    def _compute_hash(self, content: str) -> str:
        """Compute SHA-256 hash of content."""
        return hashlib.sha256(content.encode()).hexdigest()

    def _source_exists(self, source_id: str) -> bool:
        """Check if source ID already exists."""
        sources = self.list_sources()
        return any(s.source_id == source_id for s in sources)

    def _find_duplicate_content(self, content_hash: str) -> Optional[str]:
        """
        Find source with duplicate content.

        Returns:
            Source name if duplicate found, None otherwise
        """
        sources = self.list_sources()
        for source in sources:
            if source.content_hash == content_hash:
                return source.source_name
        return None

    def _add_to_config(self, source: Source):
        """Add source to project config."""
        config = self._load_config()

        if "sources" not in config:
            config["sources"] = []

        config["sources"].append(source.to_dict())
        self._save_config(config)

    def _remove_from_config(self, source_id: str):
        """Remove source from project config."""
        config = self._load_config()
        sources = config.get("sources", [])

        config["sources"] = [
            s for s in sources
            if s["source_id"] != source_id
        ]

        self._save_config(config)

    def _load_config(self) -> Dict:
        """Load project configuration."""
        if not self.config_file.exists():
            return {}

        with open(self.config_file, 'r') as f:
            return json.load(f)

    def _save_config(self, config: Dict):
        """Save project configuration."""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)


# Example usage
if __name__ == "__main__":
    from pathlib import Path

    # Example: Add source to a project
    project_dir = Path("projects/insolvency-law")
    manager = SourceManager(project_dir)

    # List existing sources
    sources = manager.list_sources()
    print(f"Existing sources: {len(sources)}")
    for source in sources:
        print(f"  - {source.source_name} ({source.source_type})")
        print(f"    Extracted: {source.extracted}")
