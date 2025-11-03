"""
Database loader with context enrichment.

Loads Lang Extract JSONL files into SQLite with:
- Section context from section_mapper
- Actor/document normalization
- Efficient bulk inserts
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import Dict, List
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.section_mapper import SectionMapper

logger = logging.getLogger(__name__)


class KnowledgeBaseLoader:
    """Loads extractions into SQLite with context enrichment."""

    def __init__(self, db_path: Path, section_map_path: Path):
        """
        Initialize loader.

        Args:
            db_path: Path to SQLite database
            section_map_path: Path to section map JSON
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.section_mapper = SectionMapper.load_from_json(section_map_path)

        # Initialize schema
        self._init_schema()

    def _init_schema(self):
        """Initialize database schema."""
        schema_path = Path(__file__).parent / 'schema.sql'
        with open(schema_path, 'r') as f:
            self.conn.executescript(f.read())
        self.conn.commit()
        logger.info('Database schema initialized')

    def register_source(self, source_name: str, file_path: str,
                       pages: int = None, total_chars: int = None, notes: str = None) -> int:
        """
        Register a source document or get existing source ID.

        Args:
            source_name: Name of the source (e.g., "Study Material", "BIA Statute")
            file_path: Path to the original PDF
            pages: Number of pages in the document
            total_chars: Total character count
            notes: Optional notes about the source

        Returns:
            source_id: The ID of the registered source
        """
        # Check if source already exists
        cursor = self.conn.execute(
            'SELECT id FROM source_documents WHERE source_name = ?',
            (source_name,)
        )
        result = cursor.fetchone()

        if result:
            logger.info(f'Source "{source_name}" already registered with ID {result[0]}')
            return result[0]

        # Insert new source
        cursor = self.conn.execute('''
            INSERT INTO source_documents (source_name, file_path, pages, total_chars, notes)
            VALUES (?, ?, ?, ?, ?)
        ''', (source_name, file_path, pages, total_chars, notes))

        source_id = cursor.lastrowid
        self.conn.commit()
        logger.info(f'Registered new source "{source_name}" with ID {source_id}')
        return source_id

    def load_all_categories(self, extraction_dir: Path, source_id: int):
        """
        Load all extraction categories with source tracking.

        Args:
            extraction_dir: Directory containing JSONL files
            source_id: ID of the source document (from register_source)
        """
        categories = {
            'concepts': self._load_concepts,
            'deadlines': self._load_deadlines,
            'documents': self._load_documents,
            'actors': self._load_actors,
            'statutory_references': self._load_statutory_refs,
            'procedures': self._load_procedures,
            'consequences': self._load_consequences
        }

        total_loaded = 0
        for category, loader_func in categories.items():
            jsonl_file = extraction_dir / category
            if not jsonl_file.exists():
                jsonl_file = extraction_dir / f'{category}.jsonl'

            if jsonl_file.exists():
                logger.info(f'Loading {category}...')
                count = loader_func(jsonl_file, source_id)
                logger.info(f'✓ Loaded {count} {category}')
                total_loaded += count
            else:
                logger.warning(f'File not found: {jsonl_file}')

        # Update total_entities in source_documents
        self.conn.execute('''
            UPDATE source_documents
            SET total_entities = ?
            WHERE id = ?
        ''', (total_loaded, source_id))

        self.conn.commit()
        logger.info(f'Total entities loaded for source {source_id}: {total_loaded}')

    def _enrich_with_context(self, extraction: Dict) -> Dict:
        """Add section context to extraction."""
        char_interval = extraction.get('char_interval')
        if not char_interval:
            return {
                'char_start': 0,
                'char_end': 0,
                'section_number': None,
                'section_title': None,
                'section_context': 'Unknown'
            }

        char_start = char_interval['start_pos']
        char_end = char_interval['end_pos']
        section = self.section_mapper.get_section_for_position(char_start)

        return {
            'char_start': char_start,
            'char_end': char_end,
            'section_number': section['section_number'] if section else None,
            'section_title': section['title'] if section else None,
            'section_context': self.section_mapper.get_hierarchical_context(char_start)
        }

    def _normalize_actor(self, role: str) -> str:
        """Normalize actor name to canonical form."""
        # Simple normalization - title case, singular
        normalized = role.strip()

        # Canonical mappings
        mappings = {
            'trustee': 'Trustee',
            'trustees': 'Trustee',
            'creditor': 'Creditor',
            'creditors': 'Creditor',
            'debtor': 'Debtor',
            'debtors': 'Debtor',
            'bankrupt': 'Bankrupt',
            'bankrupts': 'Bankrupt',
            'inspector': 'Inspector',
            'inspectors': 'Inspector',
            'receiver': 'Receiver',
            'receivers': 'Receiver',
            'official receiver': 'Official Receiver',
            'o.r.': 'Official Receiver',
            'o. r.': 'Official Receiver',
        }

        # Check exact lowercase match first
        lower = normalized.lower()
        if lower in mappings:
            return mappings[lower]

        # Remove trailing 's' for plurals
        if lower.endswith('s') and lower[:-1] in mappings:
            return mappings[lower[:-1]]

        # Default: title case
        return normalized.title() if normalized.islower() or normalized.isupper() else normalized

    def _load_concepts(self, jsonl_file: Path, source_id: int) -> int:
        """Load concepts into database."""
        with open(jsonl_file, 'r') as f:
            data = json.load(f)

        rows = []
        for ext in data['extractions']:
            attrs = ext.get('attributes') or {}  # Handle None
            context = self._enrich_with_context(ext)

            rows.append((
                source_id,
                ext['extraction_text'],
                attrs.get('term'),
                attrs.get('definition'),
                attrs.get('importance'),
                context['char_start'],
                context['char_end'],
                context['section_number'],
                context['section_title'],
                context['section_context']
            ))

        self.conn.executemany('''
            INSERT INTO concepts (source_id, extraction_text, term, definition, importance,
                                char_start, char_end, section_number, section_title, section_context)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', rows)

        return len(rows)

    def _load_deadlines(self, jsonl_file: Path, source_id: int) -> int:
        """Load deadlines into database."""
        with open(jsonl_file, 'r') as f:
            data = json.load(f)

        rows = []
        for ext in data['extractions']:
            attrs = ext.get('attributes') or {}  # Handle None
            context = self._enrich_with_context(ext)

            rows.append((
                source_id,
                ext['extraction_text'],
                attrs.get('timeframe'),
                context['char_start'],
                context['char_end'],
                context['section_number'],
                context['section_title'],
                context['section_context']
            ))

        self.conn.executemany('''
            INSERT INTO deadlines (source_id, extraction_text, timeframe, char_start, char_end,
                                 section_number, section_title, section_context)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', rows)

        return len(rows)

    def _load_documents(self, jsonl_file: Path, source_id: int) -> int:
        """Load documents with normalization."""
        with open(jsonl_file, 'r') as f:
            data = json.load(f)

        rows = []
        for ext in data['extractions']:
            attrs = ext.get('attributes') or {}  # Handle None
            context = self._enrich_with_context(ext)
            doc_name = attrs.get('document_name', '')

            rows.append((
                source_id,
                ext['extraction_text'],
                doc_name,
                doc_name,  # Canonical - same for now, can enhance later
                context['char_start'],
                context['char_end'],
                context['section_number'],
                context['section_title'],
                context['section_context']
            ))

        self.conn.executemany('''
            INSERT INTO documents (source_id, extraction_text, document_name, document_name_canonical,
                                 char_start, char_end, section_number, section_title, section_context)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', rows)

        return len(rows)

    def _load_actors(self, jsonl_file: Path, source_id: int) -> int:
        """Load actors with normalization."""
        with open(jsonl_file, 'r') as f:
            data = json.load(f)

        rows = []
        for ext in data['extractions']:
            attrs = ext.get('attributes') or {}  # Handle None
            context = self._enrich_with_context(ext)
            role_raw = attrs.get('role', '')
            role_canonical = self._normalize_actor(role_raw)

            rows.append((
                source_id,
                ext['extraction_text'],
                role_raw,
                role_canonical,
                context['char_start'],
                context['char_end'],
                context['section_number'],
                context['section_title'],
                context['section_context']
            ))

        self.conn.executemany('''
            INSERT INTO actors (source_id, extraction_text, role_raw, role_canonical,
                              char_start, char_end, section_number, section_title, section_context)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', rows)

        return len(rows)

    def _load_statutory_refs(self, jsonl_file: Path, source_id: int) -> int:
        """Load statutory references."""
        with open(jsonl_file, 'r') as f:
            data = json.load(f)

        rows = []
        for ext in data['extractions']:
            attrs = ext.get('attributes') or {}  # Handle None
            context = self._enrich_with_context(ext)
            ref = attrs.get('reference', '')

            # Parse act and section from reference
            act, section = self._parse_reference(ref)

            rows.append((
                source_id,
                ext['extraction_text'],
                ref,
                act,
                section,
                context['char_start'],
                context['char_end'],
                context['section_number'],
                context['section_title'],
                context['section_context']
            ))

        self.conn.executemany('''
            INSERT INTO statutory_references (source_id, extraction_text, reference, act, section,
                                            char_start, char_end, section_number, section_title, section_context)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', rows)

        return len(rows)

    def _parse_reference(self, ref: str) -> tuple:
        """Parse reference into act and section."""
        # Simple parser for "BIA s. 50.4", "Form 33", "CCAA s. 11"
        if ' s. ' in ref or ' s ' in ref:
            parts = ref.split(' s')
            return (parts[0].strip(), 's' + parts[1].strip())
        elif 'Form ' in ref:
            return ('BIA', ref)
        elif ref.startswith('BIA') or ref.startswith('CCAA'):
            parts = ref.split(' ', 1)
            return (parts[0], parts[1] if len(parts) > 1 else '')
        return (None, ref)

    def _load_procedures(self, jsonl_file: Path, source_id: int) -> int:
        """Load procedures."""
        with open(jsonl_file, 'r') as f:
            data = json.load(f)

        rows = []
        for ext in data['extractions']:
            attrs = ext.get('attributes') or {}  # Handle None
            context = self._enrich_with_context(ext)

            rows.append((
                source_id,
                ext['extraction_text'],
                attrs.get('step_name'),
                attrs.get('action'),
                attrs.get('order'),
                context['char_start'],
                context['char_end'],
                context['section_number'],
                context['section_title'],
                context['section_context']
            ))

        self.conn.executemany('''
            INSERT INTO procedures (source_id, extraction_text, step_name, action, step_order,
                                  char_start, char_end, section_number, section_title, section_context)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', rows)

        return len(rows)

    def _load_consequences(self, jsonl_file: Path, source_id: int) -> int:
        """Load consequences."""
        with open(jsonl_file, 'r') as f:
            data = json.load(f)

        rows = []
        for ext in data['extractions']:
            attrs = ext.get('attributes') or {}  # Handle None
            context = self._enrich_with_context(ext)

            rows.append((
                source_id,
                ext['extraction_text'],
                attrs.get('outcome'),
                context['char_start'],
                context['char_end'],
                context['section_number'],
                context['section_title'],
                context['section_context']
            ))

        self.conn.executemany('''
            INSERT INTO consequences (source_id, extraction_text, outcome, char_start, char_end,
                                    section_number, section_title, section_context)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', rows)

        return len(rows)

    def get_stats(self) -> Dict:
        """Get database statistics."""
        cursor = self.conn.execute('SELECT * FROM v_extraction_stats')
        return {row[0]: {'total': row[1], 'sections': row[2]} for row in cursor.fetchall()}

    def close(self):
        """Close database connection."""
        self.conn.close()


if __name__ == '__main__':
    # Test loading with source tracking
    db_path = Path('data/output/insolvency_knowledge.db')
    section_map = Path('data/output/section_map.json')
    extraction_dir = Path('data/output/knowledge_base')

    print('Loading knowledge base into SQLite with source tracking...')

    loader = KnowledgeBaseLoader(db_path, section_map)

    # Register the source document
    source_id = loader.register_source(
        source_name='Study Material',
        file_path='data/input/study_materials/InsolvencyStudyGuide.pdf',
        pages=291,
        notes='Complete insolvency study guide with 18 chapters'
    )

    # Load all categories with source tracking
    loader.load_all_categories(extraction_dir, source_id)

    stats = loader.get_stats()
    print('\nDatabase loaded successfully!')
    print('='*60)
    for category, data in stats.items():
        print(f'{category:20s}: {data["total"]:5d} items across {data["sections"]:4d} sections')

    loader.close()
    print(f'\nDatabase saved to: {db_path}')
