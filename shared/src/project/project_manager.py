"""
Project Manager - Multi-project workspace management.

Handles creation, switching, and management of multiple knowledge base projects.
"""

import json
import os
import shutil
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class Project:
    """Represents a knowledge base project."""
    project_id: str
    project_name: str
    domain: str
    description: str
    database_path: str
    sources_count: int
    total_entities: int
    total_relationships: int
    created_at: str
    domain_terminology: Dict

    @classmethod
    def from_config(cls, config: Dict, project_dir: Path):
        """Create Project from config dictionary."""
        stats = config.get('statistics', {})

        # Load domain terminology with defaults
        domain_terminology = config.get('domain_terminology', {})
        if not domain_terminology:
            # Fallback defaults for projects without domain config
            domain_terminology = {
                'primary_content_table': 'hierarchical_content',
                'reference_format': '{id}',
                'source_type': 'document',
                'answer_format': 'generic'
            }

        return cls(
            project_id=config['project_id'],
            project_name=config['project_name'],
            domain=config.get('domain', 'unknown'),
            description=config.get('description', ''),
            database_path=str(project_dir / config['database_path']),
            sources_count=len(config.get('sources', [])),
            total_entities=stats.get('total_entities', 0),
            total_relationships=stats.get('total_relationships', 0),
            created_at=config.get('created_at', ''),
            domain_terminology=domain_terminology
        )

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)

    def get_tracking_file(self, filename: str) -> Path:
        """Get path to tracking file (CSV, logs, etc.) for this project."""
        project_dir = Path(self.database_path).parent.parent  # database/knowledge.db -> project root
        tracking_dir = project_dir / "tracking"
        tracking_dir.mkdir(exist_ok=True)
        return tracking_dir / filename


class ProjectManager:
    """Manage multiple knowledge base projects."""

    def __init__(self, workspace_root: Optional[Path] = None):
        """
        Initialize ProjectManager.

        Args:
            workspace_root: Root directory of workspace (defaults to current dir)
        """
        if workspace_root is None:
            workspace_root = Path.cwd()

        self.workspace_root = Path(workspace_root)
        self.projects_dir = self.workspace_root / "projects"
        self.shared_dir = self.workspace_root / "shared"
        self.current_project_file = self.workspace_root / ".current_project"
        self.workspace_config_file = self.workspace_root / "workspace_config.json"

        # Ensure directories exist
        self.projects_dir.mkdir(exist_ok=True)
        self.shared_dir.mkdir(exist_ok=True)

    def load_workspace_config(self) -> Dict:
        """Load workspace configuration."""
        if not self.workspace_config_file.exists():
            return {}

        with open(self.workspace_config_file, 'r') as f:
            return json.load(f)

    def save_workspace_config(self, config: Dict):
        """Save workspace configuration."""
        with open(self.workspace_config_file, 'w') as f:
            json.dump(config, f, indent=2)

    def list_projects(self) -> List[Project]:
        """
        List all projects in workspace.

        Returns:
            List of Project objects
        """
        projects = []

        if not self.projects_dir.exists():
            return projects

        for project_dir in self.projects_dir.iterdir():
            if not project_dir.is_dir():
                continue

            config_file = project_dir / "config.json"
            if not config_file.exists():
                continue

            try:
                config = self._load_config(config_file)
                project = Project.from_config(config, project_dir)
                projects.append(project)
            except Exception as e:
                print(f"Warning: Could not load project {project_dir.name}: {e}")
                continue

        return sorted(projects, key=lambda p: p.project_name)

    def get_current_project(self) -> Optional[Project]:
        """
        Get currently active project.

        Returns:
            Project object or None if no project is active
        """
        if not self.current_project_file.exists():
            return None

        project_id = self.current_project_file.read_text().strip()
        if not project_id:
            return None

        return self.load_project(project_id)

    def load_project(self, project_id: str) -> Optional[Project]:
        """
        Load a specific project by ID.

        Args:
            project_id: Project identifier

        Returns:
            Project object or None if not found
        """
        project_dir = self.projects_dir / project_id
        if not project_dir.exists():
            return None

        config_file = project_dir / "config.json"
        if not config_file.exists():
            return None

        try:
            config = self._load_config(config_file)
            return Project.from_config(config, project_dir)
        except Exception as e:
            print(f"Error loading project {project_id}: {e}")
            return None

    def switch_to(self, project_id: str) -> Project:
        """
        Switch to a different project.

        Args:
            project_id: Project identifier to switch to

        Returns:
            Project object

        Raises:
            ValueError: If project not found
        """
        project = self.load_project(project_id)
        if not project:
            raise ValueError(f"Project not found: {project_id}")

        # Update current project marker
        self.current_project_file.write_text(project_id)

        # Update environment variables
        os.environ["KB_ACTIVE_PROJECT"] = project_id
        os.environ["KB_DATABASE_PATH"] = project.database_path

        print(f"✓ Switched to project: {project.project_name}")
        print(f"Database: {project.database_path}")
        print(f"Sources: {project.sources_count} configured")

        return project

    def create_project(
        self,
        name: str,
        domain: str,
        description: str = "",
        template: Optional[str] = None
    ) -> Project:
        """
        Create a new project.

        Args:
            name: Human-readable project name
            domain: Domain/subject area (e.g., "law", "medicine")
            description: Optional description
            template: Optional template name for schema

        Returns:
            Created Project object

        Raises:
            ValueError: If project already exists
        """
        project_id = name.lower().replace(" ", "-")
        project_dir = self.projects_dir / project_id

        if project_dir.exists():
            raise ValueError(f"Project already exists: {project_id}")

        # Create directory structure
        project_dir.mkdir(parents=True)
        (project_dir / "database").mkdir()
        (project_dir / "sources").mkdir()
        (project_dir / "data" / "input").mkdir(parents=True)
        (project_dir / "data" / "output").mkdir(parents=True)
        (project_dir / "data" / "examples").mkdir(parents=True)
        (project_dir / "schema").mkdir()

        # Create config
        config = {
            "project_name": name,
            "project_id": project_id,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "description": description,
            "domain": domain,
            "entity_schema": {},
            "sources": [],
            "database_path": "database/knowledge.db",
            "agent_config": {
                "search_phases": ["database", "full_text"],
                "auto_follow_references": True,
                "logging_enabled": True
            },
            "statistics": {
                "total_entities": 0,
                "total_relationships": 0,
                "total_questions_answered": 0,
                "average_query_time_ms": 0
            }
        }

        # Apply template if provided
        if template:
            template_schema = self._load_template(template)
            if template_schema:
                config["entity_schema"] = template_schema

        # Save config
        config_path = project_dir / "config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        print(f"✓ Created project: {project_id}")
        print(f"Directory: {project_dir}")

        project = Project.from_config(config, project_dir)

        # Set as current project if it's the first one
        if not self.current_project_file.exists():
            self.switch_to(project_id)

        return project

    def delete_project(self, project_id: str, confirm: bool = False):
        """
        Delete a project (requires confirmation).

        Args:
            project_id: Project identifier to delete
            confirm: Must be True to actually delete

        Raises:
            ValueError: If confirm is False or project not found
        """
        if not confirm:
            raise ValueError("Must set confirm=True to delete project")

        project_dir = self.projects_dir / project_id
        if not project_dir.exists():
            raise ValueError(f"Project not found: {project_id}")

        # Remove directory
        shutil.rmtree(project_dir)

        # Clear current project if it was the deleted one
        if self.current_project_file.exists():
            current_id = self.current_project_file.read_text().strip()
            if current_id == project_id:
                self.current_project_file.unlink()

        print(f"✓ Deleted project: {project_id}")

    def get_project_config(self, project_id: str) -> Optional[Dict]:
        """
        Get project configuration.

        Args:
            project_id: Project identifier

        Returns:
            Configuration dictionary or None if not found
        """
        config_file = self.projects_dir / project_id / "config.json"
        if not config_file.exists():
            return None

        return self._load_config(config_file)

    def update_project_config(self, project_id: str, updates: Dict):
        """
        Update project configuration.

        Args:
            project_id: Project identifier
            updates: Dictionary of updates to apply
        """
        config_file = self.projects_dir / project_id / "config.json"
        if not config_file.exists():
            raise ValueError(f"Project not found: {project_id}")

        config = self._load_config(config_file)
        config.update(updates)

        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)

    def _load_config(self, config_path: Path) -> Dict:
        """Load configuration from JSON file."""
        with open(config_path, 'r') as f:
            return json.load(f)

    def _load_template(self, template_name: str) -> Optional[Dict]:
        """
        Load project template schema.

        Args:
            template_name: Name of template (e.g., "law", "medicine")

        Returns:
            Schema dictionary or None if template not found
        """
        # Templates would be stored in shared/templates/
        template_file = self.shared_dir / "templates" / f"{template_name}.json"
        if not template_file.exists():
            return None

        return self._load_config(template_file)


# Example usage
if __name__ == "__main__":
    pm = ProjectManager()

    # List projects
    projects = pm.list_projects()
    print(f"Found {len(projects)} projects:")
    for p in projects:
        print(f"  - {p.project_name} ({p.project_id})")

    # Get current project
    current = pm.get_current_project()
    if current:
        print(f"\nCurrent project: {current.project_name}")
        print(f"  Domain: {current.domain}")
        print(f"  Entities: {current.total_entities:,}")
        print(f"  Relationships: {current.total_relationships:,}")
