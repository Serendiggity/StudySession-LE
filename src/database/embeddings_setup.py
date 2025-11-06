#!/usr/bin/env python3
"""
Embeddings Setup Module for Hybrid Search

Generates embeddings for structured content tables (BIA sections, study materials)
and stores them in SQLite using sqlite-vec extension for vector similarity search.

This enables hybrid search combining keyword-based FTS5 with semantic vector search.
"""

import sqlite3
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class EmbeddingsManager:
    """
    Manages embeddings generation and storage for hybrid search.

    Uses sentence-transformers for free, local embedding generation.
    Stores vectors in SQLite using sqlite-vec extension.
    """

    def __init__(self, db_path: Path, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize embeddings manager.

        Args:
            db_path: Path to SQLite database
            model_name: Sentence transformer model to use
        """
        self.db_path = db_path
        self.model_name = model_name
        self.model = None
        self.vector_dim = 384  # Dimension for all-MiniLM-L6-v2

    def _load_model(self):
        """Lazy load the sentence transformer model."""
        if self.model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading model: {self.model_name}")
                self.model = SentenceTransformer(self.model_name)
                logger.info("Model loaded successfully")
            except ImportError:
                raise ImportError(
                    "sentence-transformers not installed. "
                    "Install with: pip install sentence-transformers"
                )

    def _load_sqlite_vec(self, conn: sqlite3.Connection):
        """Load sqlite-vec extension."""
        try:
            import sqlite_vec
            conn.enable_load_extension(True)
            sqlite_vec.load(conn)
            logger.info("sqlite-vec extension loaded")
        except ImportError:
            raise ImportError(
                "sqlite-vec not installed. "
                "Install with: pip install sqlite-vec"
            )

    def create_vector_table(self, table_name: str, base_table: str):
        """
        Create virtual vector table for storing embeddings.

        Args:
            table_name: Name for the vector table (e.g., 'bia_sections_vec')
            base_table: Name of the base table to embed
        """
        conn = sqlite3.connect(self.db_path)

        try:
            self._load_sqlite_vec(conn)

            # Create virtual table using vec0
            # Format: vec0(rowid INTEGER PRIMARY KEY, embedding FLOAT[dimension])
            conn.execute(f"""
                CREATE VIRTUAL TABLE IF NOT EXISTS {table_name}
                USING vec0(
                    rowid INTEGER PRIMARY KEY,
                    embedding FLOAT[{self.vector_dim}]
                )
            """)

            conn.commit()
            logger.info(f"Created vector table: {table_name}")

        finally:
            conn.close()

    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of text strings to embed

        Returns:
            numpy array of embeddings (n_texts x vector_dim)
        """
        self._load_model()

        logger.info(f"Generating embeddings for {len(texts)} texts")
        embeddings = self.model.encode(texts, show_progress_bar=True)

        return embeddings

    def populate_vector_table(
        self,
        vector_table: str,
        base_table: str,
        text_column: str = 'full_text',
        batch_size: int = 100
    ) -> Dict[str, int]:
        """
        Generate and store embeddings for all rows in a table.

        Args:
            vector_table: Name of the vector table to populate
            base_table: Name of the base table to read from
            text_column: Column containing text to embed
            batch_size: Number of rows to process at once

        Returns:
            Statistics dictionary
        """
        conn = sqlite3.connect(self.db_path)

        try:
            self._load_sqlite_vec(conn)
            cursor = conn.cursor()

            # Get total count
            cursor.execute(f"SELECT COUNT(*) FROM {base_table}")
            total_count = cursor.fetchone()[0]

            logger.info(f"Embedding {total_count} rows from {base_table}")

            # Process in batches
            processed = 0
            offset = 0

            while offset < total_count:
                # Fetch batch
                cursor.execute(f"""
                    SELECT rowid, {text_column}
                    FROM {base_table}
                    LIMIT ? OFFSET ?
                """, (batch_size, offset))

                rows = cursor.fetchall()
                if not rows:
                    break

                # Generate embeddings
                rowids = [row[0] for row in rows]
                texts = [row[1] or '' for row in rows]
                embeddings = self.generate_embeddings(texts)

                # Insert into vector table
                for rowid, embedding in zip(rowids, embeddings):
                    # Convert to list for SQLite
                    embedding_list = embedding.tolist()

                    cursor.execute(f"""
                        INSERT OR REPLACE INTO {vector_table} (rowid, embedding)
                        VALUES (?, ?)
                    """, (rowid, str(embedding_list)))

                conn.commit()
                processed += len(rows)
                offset += batch_size

                logger.info(f"Progress: {processed}/{total_count} ({100*processed//total_count}%)")

            return {
                'total_rows': total_count,
                'embeddings_generated': processed,
                'vector_table': vector_table,
                'base_table': base_table
            }

        finally:
            conn.close()

    def setup_table_embeddings(self, base_table: str, text_column: str = 'full_text'):
        """
        One-shot setup: create vector table and generate all embeddings.

        Args:
            base_table: Name of the table to embed (e.g., 'bia_sections')
            text_column: Column containing text to embed

        Returns:
            Statistics dictionary
        """
        vector_table = f"{base_table}_vec"

        # Create vector table
        self.create_vector_table(vector_table, base_table)

        # Populate with embeddings
        stats = self.populate_vector_table(vector_table, base_table, text_column)

        return stats


def setup_bia_sections_embeddings(db_path: Path) -> Dict[str, int]:
    """
    Convenience function to set up embeddings for BIA sections.

    Args:
        db_path: Path to the knowledge database

    Returns:
        Statistics dictionary
    """
    manager = EmbeddingsManager(db_path)
    return manager.setup_table_embeddings('bia_sections', 'full_text')


def setup_all_embeddings(db_path: Path) -> Dict[str, Dict[str, int]]:
    """
    Set up embeddings for all relevant tables in the database.

    Args:
        db_path: Path to the knowledge database

    Returns:
        Dictionary mapping table names to statistics
    """
    manager = EmbeddingsManager(db_path)

    results = {}

    # Tables to embed
    tables_to_embed = [
        ('bia_sections', 'full_text'),
        ('osb_directives', 'content'),
    ]

    # Study material tables (if they exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = {row[0] for row in cursor.fetchall()}

    conn.close()

    # Add study material tables if they exist
    study_tables = [
        ('concepts', 'extraction_text'),
        ('procedures', 'extraction_text'),
        ('deadlines', 'extraction_text'),
        ('documents', 'extraction_text'),
        ('actors', 'extraction_text'),
        ('consequences', 'extraction_text'),
        ('statutory_references', 'extraction_text'),
    ]

    for table, column in study_tables:
        if table in existing_tables:
            tables_to_embed.append((table, column))

    # Generate embeddings for each table
    for table, column in tables_to_embed:
        if table in existing_tables:
            logger.info(f"\n{'='*60}")
            logger.info(f"Setting up embeddings for: {table}")
            logger.info(f"{'='*60}")

            try:
                stats = manager.setup_table_embeddings(table, column)
                results[table] = stats
                logger.info(f"✅ Completed {table}: {stats['embeddings_generated']} embeddings")
            except Exception as e:
                logger.error(f"❌ Failed to embed {table}: {e}")
                results[table] = {'error': str(e)}

    return results


if __name__ == '__main__':
    import sys

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    if len(sys.argv) < 2:
        print("Usage: python embeddings_setup.py <database_path>")
        print("\nExample:")
        print("  python embeddings_setup.py projects/insolvency-law/database/knowledge.db")
        sys.exit(1)

    db_path = Path(sys.argv[1])

    if not db_path.exists():
        print(f"Error: Database not found: {db_path}")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"Embedding Setup for Knowledge Base")
    print(f"{'='*60}")
    print(f"Database: {db_path}")
    print(f"Model: all-MiniLM-L6-v2 (384 dimensions)")
    print(f"\nThis will:")
    print("  1. Create vector tables for all content tables")
    print("  2. Generate embeddings using sentence-transformers")
    print("  3. Store vectors in SQLite using sqlite-vec")
    print(f"\n{'='*60}\n")

    # Run setup
    results = setup_all_embeddings(db_path)

    # Print summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")

    for table, stats in results.items():
        if 'error' in stats:
            print(f"❌ {table}: {stats['error']}")
        else:
            print(f"✅ {table}: {stats['embeddings_generated']} embeddings")

    print(f"\n{'='*60}")
    print("Embeddings setup complete!")
    print(f"{'='*60}\n")
