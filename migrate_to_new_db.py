#!/usr/bin/env python3
"""
Migrate all atomic entities and relationships from old database to new project database.
"""

import sqlite3
from pathlib import Path

# Database paths
OLD_DB = Path("database/insolvency_knowledge.db")
NEW_DB = Path("projects/insolvency-law/database/knowledge.db")

# Tables to migrate (in dependency order)
TABLES_TO_MIGRATE = [
    # Source metadata
    "source_documents",

    # Atomic entities
    "concepts",
    "deadlines",
    "documents",
    "actors",
    "statutory_references",
    "procedures",
    "consequences",

    # Canonical mappings
    "actor_canonical_map",
    "document_canonical_map",

    # OSB directives
    "osb_directives",

    # Exam/quiz data
    "exam_datasets",
    "exam_questions",
    "quiz_datasets",
    "quiz_questions",

    # System
    "system_errors",

    # Relationships (after entities)
    "duty_relationships",
    "document_requirements",
    "trigger_relationships",
]

def table_exists(cursor, table_name):
    """Check if table exists."""
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name=?
    """, (table_name,))
    return cursor.fetchone() is not None

def copy_table(old_conn, new_conn, table_name):
    """Copy entire table from old to new database."""
    old_cursor = old_conn.cursor()
    new_cursor = new_conn.cursor()

    # Check if table exists in old database
    if not table_exists(old_cursor, table_name):
        print(f"⚠️  {table_name}: Not in old database, skipping")
        return 0

    # Get table schema
    old_cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    schema_row = old_cursor.fetchone()
    if not schema_row:
        print(f"⚠️  {table_name}: No schema found, skipping")
        return 0

    schema = schema_row[0]

    # Drop table if exists in new database (fresh start)
    new_cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

    # Create table in new database
    new_cursor.execute(schema)

    # Copy data
    old_cursor.execute(f"SELECT * FROM {table_name}")
    rows = old_cursor.fetchall()

    if not rows:
        print(f"✓ {table_name}: Table created, 0 rows")
        return 0

    # Get column count
    old_cursor.execute(f"PRAGMA table_info({table_name})")
    col_count = len(old_cursor.fetchall())

    # Insert data
    placeholders = ",".join(["?"] * col_count)
    new_cursor.executemany(f"INSERT INTO {table_name} VALUES ({placeholders})", rows)

    print(f"✓ {table_name}: {len(rows)} rows migrated")
    return len(rows)

def copy_fts_tables(old_conn, new_conn):
    """Copy FTS tables and their data."""
    old_cursor = old_conn.cursor()
    new_cursor = new_conn.cursor()

    # Get all FTS tables from old database
    old_cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name LIKE '%_fts'
        AND name NOT LIKE 'bia_%_fts'
    """)

    fts_tables = [row[0] for row in old_cursor.fetchall()]
    total_copied = 0

    for fts_table in fts_tables:
        # Get the FTS creation statement
        old_cursor.execute(f"SELECT sql FROM sqlite_master WHERE name=?", (fts_table,))
        schema_row = old_cursor.fetchone()
        if not schema_row:
            continue

        schema = schema_row[0]

        # Drop and recreate
        new_cursor.execute(f"DROP TABLE IF EXISTS {fts_table}")
        new_cursor.execute(schema)

        # Copy data (FTS tables need special handling)
        try:
            old_cursor.execute(f"SELECT * FROM {fts_table}")
            rows = old_cursor.fetchall()

            if rows:
                col_count = len(rows[0])
                placeholders = ",".join(["?"] * col_count)
                new_cursor.executemany(f"INSERT INTO {fts_table} VALUES ({placeholders})", rows)
                print(f"✓ {fts_table}: {len(rows)} rows")
                total_copied += len(rows)
        except sqlite3.Error as e:
            print(f"⚠️  {fts_table}: Skipping (error: {e})")

    return total_copied

def copy_views(old_conn, new_conn):
    """Copy all views from old to new database."""
    old_cursor = old_conn.cursor()
    new_cursor = new_conn.cursor()

    # Get all views
    old_cursor.execute("""
        SELECT name, sql FROM sqlite_master
        WHERE type='view'
        ORDER BY name
    """)

    views = old_cursor.fetchall()

    for view_name, view_sql in views:
        # Drop if exists
        new_cursor.execute(f"DROP VIEW IF EXISTS {view_name}")

        # Create view
        try:
            new_cursor.execute(view_sql)
            print(f"✓ View: {view_name}")
        except sqlite3.Error as e:
            print(f"⚠️  View {view_name}: {e}")

    return len(views)

def main():
    """Run migration."""
    print("=" * 60)
    print("MIGRATING OLD DATABASE TO NEW PROJECT DATABASE")
    print("=" * 60)
    print(f"Source: {OLD_DB}")
    print(f"Target: {NEW_DB}")
    print()

    # Verify databases exist
    if not OLD_DB.exists():
        print(f"❌ Old database not found: {OLD_DB}")
        return

    if not NEW_DB.exists():
        print(f"❌ New database not found: {NEW_DB}")
        return

    # Connect to databases
    old_conn = sqlite3.connect(OLD_DB)
    new_conn = sqlite3.connect(NEW_DB)

    try:
        total_rows = 0

        # Migrate tables
        print("\n📦 Migrating Tables:")
        print("-" * 60)
        for table in TABLES_TO_MIGRATE:
            rows = copy_table(old_conn, new_conn, table)
            total_rows += rows

        # Commit after tables
        new_conn.commit()

        # Migrate FTS tables
        print("\n🔍 Migrating FTS Tables:")
        print("-" * 60)
        fts_rows = copy_fts_tables(old_conn, new_conn)
        new_conn.commit()

        # Migrate views
        print("\n👁️  Migrating Views:")
        print("-" * 60)
        view_count = copy_views(old_conn, new_conn)
        new_conn.commit()

        # Summary
        print("\n" + "=" * 60)
        print("✅ MIGRATION COMPLETE")
        print("=" * 60)
        print(f"Tables migrated: {len(TABLES_TO_MIGRATE)}")
        print(f"Total rows: {total_rows:,}")
        print(f"FTS rows: {fts_rows:,}")
        print(f"Views created: {view_count}")
        print()

        # Verify key table
        new_cursor = new_conn.cursor()
        new_cursor.execute("SELECT COUNT(*) FROM duty_relationships")
        duty_count = new_cursor.fetchone()[0]
        print(f"✓ duty_relationships: {duty_count:,} rows")

        new_cursor.execute("SELECT COUNT(*) FROM actors")
        actor_count = new_cursor.fetchone()[0]
        print(f"✓ actors: {actor_count:,} rows")

        new_cursor.execute("SELECT COUNT(*) FROM v_complete_duties")
        view_count = new_cursor.fetchone()[0]
        print(f"✓ v_complete_duties view: {view_count:,} rows")

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        new_conn.rollback()
        raise

    finally:
        old_conn.close()
        new_conn.close()

if __name__ == "__main__":
    main()
