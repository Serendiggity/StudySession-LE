#!/usr/bin/env python3
"""
Migrate old JSONL extraction data to new SQLite database format.

Usage:
    python3 migrate_old_data.py
"""

import json
import sqlite3
import sys
from pathlib import Path

# Add shared/src to path
repo_root = Path(__file__).parent
sys.path.insert(0, str(repo_root / "shared" / "src"))

from project import ProjectManager


def load_json_file(file_path: Path):
    """Load JSON file and return list of extractions."""
    if not file_path.exists():
        print(f"  ⚠️  File not found: {file_path}")
        return []

    try:
        with open(file_path, 'r') as f:
            data = json.load(f)

        if 'extractions' in data:
            return data['extractions']
        return []
    except json.JSONDecodeError as e:
        print(f"  ⚠️  JSON decode error: {e}")
        return []


def create_tables(conn: sqlite3.Connection):
    """Create necessary tables in the database."""
    cursor = conn.cursor()

    # Create relationships table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS relationships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            relationship_type TEXT NOT NULL,
            relationship_text TEXT NOT NULL,
            source_id TEXT,
            char_start INTEGER,
            char_end INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create FTS5 virtual table for full-text search
    cursor.execute('''
        CREATE VIRTUAL TABLE IF NOT EXISTS relationships_fts
        USING fts5(
            relationship_text,
            content='relationships',
            content_rowid='id'
        )
    ''')

    # Create trigger to keep FTS index updated
    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS relationships_fts_insert
        AFTER INSERT ON relationships
        BEGIN
            INSERT INTO relationships_fts(rowid, relationship_text)
            VALUES (new.id, new.relationship_text);
        END
    ''')

    conn.commit()
    print("✓ Tables created")


def migrate_json_file(conn: sqlite3.Connection, json_path: Path, relationship_type: str):
    """Migrate a single JSON file to the database."""
    extractions = load_json_file(json_path)

    if not extractions:
        return 0

    cursor = conn.cursor()
    count = 0

    for extraction in extractions:
        # Get the extraction text
        text = extraction.get('extraction_text', '')
        if not text:
            continue

        # Get character positions
        char_interval = extraction.get('char_interval', {}) or {}
        char_start = char_interval.get('start_pos')
        char_end = char_interval.get('end_pos')

        # Insert into relationships table
        cursor.execute('''
            INSERT INTO relationships (relationship_type, relationship_text, source_id, char_start, char_end)
            VALUES (?, ?, ?, ?, ?)
        ''', (relationship_type, text, 'bia-statute', char_start, char_end))

        count += 1

    conn.commit()
    return count


def main():
    print("=" * 60)
    print("Migrating Old JSONL Data to New SQLite Database")
    print("=" * 60)
    print()

    # Initialize ProjectManager
    pm = ProjectManager(repo_root)

    # Get insolvency-law project
    project = pm.load_project("insolvency-law")
    if not project:
        print("❌ insolvency-law project not found")
        return 1

    print(f"✓ Found project: {project.project_name}")
    print(f"  Database: {project.database_path}")
    print()

    # Connect to database
    db_path = Path(project.database_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)

    # Create tables
    print("Creating tables...")
    create_tables(conn)
    print()

    # Migrate JSON files
    print("Migrating JSON files...")

    data_dir = repo_root / "data" / "output" / "knowledge_base"

    migrations = [
        ("deadlines.jsonl", "deadline"),
        ("concepts.jsonl", "concept"),
        ("actors", "actor"),
        ("procedures", "procedure"),
        ("consequences", "consequence"),
        ("documents", "document"),
        ("statutory_references", "statutory_reference"),
    ]

    total_count = 0

    for filename, rel_type in migrations:
        file_path = data_dir / filename
        print(f"  {filename}...", end=" ")
        count = migrate_json_file(conn, file_path, rel_type)
        print(f"✓ {count} records")
        total_count += count

    conn.close()

    print()
    print("=" * 60)
    print(f"✓ Migration Complete")
    print(f"  Total records: {total_count:,}")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Restart Claude Desktop")
    print("2. Try querying: 'Query my knowledge base about trustee duties'")

    return 0


if __name__ == "__main__":
    sys.exit(main())
