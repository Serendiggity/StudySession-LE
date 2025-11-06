"""
Database Loader - Load extraction results into SQLite.

Handles loading entities and relationships into the project database.
Implements the hybrid architecture with relationship_text preservation.
Part of Phase 3: Extraction Pipeline implementation.
"""

import sqlite3
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class DatabaseLoader:
    """
    Load extraction results into SQLite database.

    Implements hybrid architecture:
    - Entity tables for structured data
    - Relationship tables with relationship_text field
    - Full-text search indexes
    """

    def __init__(self, project_dir: Path):
        """
        Initialize DatabaseLoader.

        Args:
            project_dir: Project directory path
        """
        self.project_dir = Path(project_dir)
        self.database_path = self.project_dir / "database" / "knowledge.db"
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

    def initialize_database(self, schema: Dict):
        """
        Initialize database with schema.

        Creates tables for all entity categories and relationships.

        Args:
            schema: Entity schema from project config
        """
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        try:
            # Create entity tables
            categories = schema.get("entity_schema", {}).get("categories", [])

            for cat in categories:
                cat_name = cat["name"]
                attributes = cat["attributes"]

                self._create_entity_table(cursor, cat_name, attributes)

            # Create relationship tables
            rel_types = schema.get("entity_schema", {}).get("relationship_types", [])

            for rel in rel_types:
                rel_name = rel["name"]
                self._create_relationship_table(cursor, rel_name)

            # Create metadata table
            self._create_metadata_table(cursor)

            conn.commit()
            print(f"✓ Database initialized: {self.database_path}")
            print(f"  Entity tables: {len(categories)}")
            print(f"  Relationship tables: {len(rel_types)}")

        finally:
            conn.close()

    def load_entities(
        self,
        category: str,
        entities: List[Dict],
        source_id: str
    ) -> int:
        """
        Load entities into database.

        Args:
            category: Entity category name
            entities: List of entity dictionaries
            source_id: Source identifier

        Returns:
            Number of entities loaded
        """
        if not entities:
            return 0

        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        loaded_count = 0

        try:
            for entity in entities:
                # Generate entity ID
                entity_id = self._generate_entity_id(category, entity)

                # Check if already exists
                if self._entity_exists(cursor, category, entity_id):
                    continue

                # Insert entity
                self._insert_entity(cursor, category, entity_id, entity, source_id)
                loaded_count += 1

            conn.commit()

        finally:
            conn.close()

        return loaded_count

    def load_relationships(
        self,
        relationship_type: str,
        relationships: List[Dict],
        source_id: str
    ) -> int:
        """
        Load relationships into database.

        CRITICAL: Preserves relationship_text field for zero-hallucination answers.

        Args:
            relationship_type: Relationship type name
            relationships: List of relationship dictionaries
            source_id: Source identifier

        Returns:
            Number of relationships loaded
        """
        if not relationships:
            return 0

        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        loaded_count = 0

        try:
            for rel in relationships:
                # Generate relationship ID
                rel_id = self._generate_relationship_id(rel)

                # Check if already exists
                if self._relationship_exists(cursor, relationship_type, rel_id):
                    continue

                # Insert relationship
                self._insert_relationship(
                    cursor,
                    relationship_type,
                    rel_id,
                    rel,
                    source_id
                )
                loaded_count += 1

            conn.commit()

        finally:
            conn.close()

        return loaded_count

    def get_statistics(self) -> Dict:
        """
        Get database statistics.

        Returns:
            {
                "total_entities": 1000,
                "total_relationships": 200,
                "entities_by_category": {...},
                "relationships_by_type": {...}
            }
        """
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        stats = {
            "total_entities": 0,
            "total_relationships": 0,
            "entities_by_category": {},
            "relationships_by_type": {}
        }

        try:
            # Get list of tables
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                AND name NOT LIKE '%_fts'
            """)

            tables = [row[0] for row in cursor.fetchall()]

            for table in tables:
                if table == "metadata":
                    continue

                # Count rows
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]

                # Determine if entity or relationship table
                if table.endswith("_relationships") or "relationship" in table:
                    stats["relationships_by_type"][table] = count
                    stats["total_relationships"] += count
                else:
                    stats["entities_by_category"][table] = count
                    stats["total_entities"] += count

        finally:
            conn.close()

        return stats

    def _create_entity_table(
        self,
        cursor: sqlite3.Cursor,
        category_name: str,
        attributes: List[str]
    ):
        """Create entity table with FTS index."""

        # Build column definitions
        columns = [
            f"{category_name}_id TEXT PRIMARY KEY",
            "source_id TEXT NOT NULL",
            "extraction_text TEXT",
            "created_at TEXT NOT NULL"
        ]

        # Add attribute columns
        for attr in attributes:
            columns.append(f"{attr} TEXT")

        create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {category_name} (
                {', '.join(columns)}
            )
        """

        cursor.execute(create_table_sql)

        # Create FTS virtual table for full-text search
        fts_columns = ["extraction_text"] + attributes

        create_fts_sql = f"""
            CREATE VIRTUAL TABLE IF NOT EXISTS {category_name}_fts
            USING fts5({', '.join(fts_columns)}, content={category_name})
        """

        cursor.execute(create_fts_sql)

    def _create_relationship_table(
        self,
        cursor: sqlite3.Cursor,
        relationship_name: str
    ):
        """Create relationship table with relationship_text field."""

        create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {relationship_name} (
                relationship_id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                relationship_text TEXT NOT NULL,
                entities_json TEXT,
                structure TEXT,
                confidence REAL,
                created_at TEXT NOT NULL
            )
        """

        cursor.execute(create_table_sql)

        # Create FTS for relationship_text (critical for search)
        create_fts_sql = f"""
            CREATE VIRTUAL TABLE IF NOT EXISTS {relationship_name}_fts
            USING fts5(relationship_text, content={relationship_name})
        """

        cursor.execute(create_fts_sql)

    def _create_metadata_table(self, cursor: sqlite3.Cursor):
        """Create metadata tracking table."""

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TEXT
            )
        """)

    def _generate_entity_id(self, category: str, entity: Dict) -> str:
        """Generate unique entity ID from content."""
        # Use extraction text or first attribute
        content = entity.get("extraction_text", "")
        if not content:
            # Use first available attribute
            for key, value in entity.items():
                if key not in ["confidence", "source_id"]:
                    content = str(value)
                    break

        # Hash to create ID
        hash_value = hashlib.md5(content.encode()).hexdigest()[:16]
        return f"{category}_{hash_value}"

    def _generate_relationship_id(self, relationship: Dict) -> str:
        """Generate unique relationship ID from relationship_text."""
        text = relationship.get("relationship_text", "")
        hash_value = hashlib.md5(text.encode()).hexdigest()[:16]
        return f"rel_{hash_value}"

    def _entity_exists(
        self,
        cursor: sqlite3.Cursor,
        category: str,
        entity_id: str
    ) -> bool:
        """Check if entity already exists."""
        cursor.execute(
            f"SELECT 1 FROM {category} WHERE {category}_id = ?",
            (entity_id,)
        )
        return cursor.fetchone() is not None

    def _relationship_exists(
        self,
        cursor: sqlite3.Cursor,
        relationship_type: str,
        relationship_id: str
    ) -> bool:
        """Check if relationship already exists."""
        cursor.execute(
            f"SELECT 1 FROM {relationship_type} WHERE relationship_id = ?",
            (relationship_id,)
        )
        return cursor.fetchone() is not None

    def _insert_entity(
        self,
        cursor: sqlite3.Cursor,
        category: str,
        entity_id: str,
        entity: Dict,
        source_id: str
    ):
        """Insert entity into table."""
        # Build column and value lists
        columns = [f"{category}_id", "source_id", "created_at"]
        values = [
            entity_id,
            source_id,
            datetime.utcnow().isoformat() + "Z"
        ]

        # Add entity attributes
        for key, value in entity.items():
            if key not in ["confidence", "source_id"]:
                columns.append(key)
                values.append(str(value) if value is not None else None)

        placeholders = ", ".join(["?"] * len(values))

        insert_sql = f"""
            INSERT INTO {category} ({', '.join(columns)})
            VALUES ({placeholders})
        """

        cursor.execute(insert_sql, values)

    def _insert_relationship(
        self,
        cursor: sqlite3.Cursor,
        relationship_type: str,
        relationship_id: str,
        relationship: Dict,
        source_id: str
    ):
        """Insert relationship into table."""
        import json

        # Extract fields
        relationship_text = relationship.get("relationship_text", "")
        entities = relationship.get("entities", {})
        structure = relationship.get("structure", "")
        confidence = relationship.get("confidence", 0.0)

        insert_sql = f"""
            INSERT INTO {relationship_type}
            (relationship_id, source_id, relationship_text, entities_json,
             structure, confidence, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        cursor.execute(
            insert_sql,
            (
                relationship_id,
                source_id,
                relationship_text,
                json.dumps(entities),
                structure,
                confidence,
                datetime.utcnow().isoformat() + "Z"
            )
        )


# Example usage
if __name__ == "__main__":
    from pathlib import Path

    # Test database operations
    project_dir = Path("projects/test-project")
    loader = DatabaseLoader(project_dir)

    # Example schema
    schema = {
        "entity_schema": {
            "categories": [
                {
                    "name": "actors",
                    "attributes": ["role_canonical", "extraction_text"]
                }
            ],
            "relationship_types": [
                {
                    "name": "duty_relationships"
                }
            ]
        }
    }

    # Initialize database
    loader.initialize_database(schema)

    # Load test entities
    entities = [
        {
            "role_canonical": "trustee",
            "extraction_text": "The trustee shall file..."
        }
    ]

    count = loader.load_entities("actors", entities, "test-source")
    print(f"Loaded {count} entities")

    # Get statistics
    stats = loader.get_statistics()
    print(f"Statistics: {stats}")
