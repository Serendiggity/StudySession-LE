"""
Simple loader: Add BIA to existing database without reinitializing schema.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import sqlite3
import json
import logging
from utils.section_mapper import SectionMapper

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

db_path = Path('data/output/insolvency_knowledge.db')
section_map_path = Path('data/output/section_map.json')
extraction_dir = Path('data/output/bia_extraction')

logger.info('='*70)
logger.info('LOADING BIA INTO EXISTING DATABASE')
logger.info('='*70)

# Connect to existing database
conn = sqlite3.connect(db_path)
logger.info(f'✓ Connected to: {db_path}')

# Load section mapper (for context enrichment)
section_mapper = SectionMapper.load_from_json(section_map_path)
logger.info(f'✓ Loaded section map: {len(section_mapper.sections)} sections')

# Register BIA source
logger.info('\nRegistering BIA statute...')
cursor = conn.execute('SELECT id FROM source_documents WHERE source_name = ?', ('BIA Statute',))
result = cursor.fetchone()

if result:
    source_id = result[0]
    logger.info(f'✓ BIA already registered with source_id={source_id}')
else:
    cursor = conn.execute('''
        INSERT INTO source_documents (source_name, file_path, pages, total_chars, notes)
        VALUES (?, ?, ?, ?, ?)
    ''', ('BIA Statute', 'Materials/Bankruptcy and Insolvency Act.pdf', 306, 784344,
          'Bankruptcy and Insolvency Act - English sections only'))
    source_id = cursor.lastrowid
    conn.commit()
    logger.info(f'✓ BIA registered with source_id={source_id}')

# Helper to add context
def enrich_with_context(extraction):
    """Add section context (minimal for BIA - just char positions)."""
    char_interval = extraction.get('char_interval') or {}
    char_start = char_interval.get('start_pos', 0) if isinstance(char_interval, dict) else 0
    char_end = char_interval.get('end_pos', 0) if isinstance(char_interval, dict) else 0

    # Try to map to study material sections (won't match, but provides structure)
    section = section_mapper.get_section_for_position(char_start)

    return {
        'char_start': char_start,
        'char_end': char_end,
        'section_number': None,  # BIA uses different numbering
        'section_title': None,
        'section_context': 'BIA Statute'  # Generic context for now
    }

# Load each category
categories = {
    'documents': 'documents',
    'actors': 'actors',
    'procedures': 'procedures',
    'deadlines': 'deadlines'
}

total_loaded = 0

for category, table_name in categories.items():
    jsonl_file = extraction_dir / category

    if not jsonl_file.exists():
        logger.warning(f'File not found: {jsonl_file}')
        continue

    logger.info(f'\nLoading {category}...')

    with open(jsonl_file, 'r') as f:
        data = json.load(f)

    rows = []
    for ext in data['extractions']:
        attrs = ext.get('attributes') or {}
        context = enrich_with_context(ext)

        if category == 'documents':
            doc_name = attrs.get('document_name', '')
            rows.append((source_id, ext['extraction_text'], doc_name, doc_name,
                        context['char_start'], context['char_end'],
                        context['section_number'], context['section_title'], context['section_context']))

        elif category == 'actors':
            role_raw = attrs.get('role', '')
            rows.append((source_id, ext['extraction_text'], role_raw, role_raw,
                        context['char_start'], context['char_end'],
                        context['section_number'], context['section_title'], context['section_context']))

        elif category == 'procedures':
            rows.append((source_id, ext['extraction_text'], attrs.get('step_name'), attrs.get('action'), attrs.get('order'),
                        context['char_start'], context['char_end'],
                        context['section_number'], context['section_title'], context['section_context']))

        elif category == 'deadlines':
            rows.append((source_id, ext['extraction_text'], attrs.get('timeframe'),
                        context['char_start'], context['char_end'],
                        context['section_number'], context['section_title'], context['section_context']))

    # Insert based on category
    if category == 'documents':
        conn.executemany('''
            INSERT INTO documents (source_id, extraction_text, document_name, document_name_canonical,
                                 char_start, char_end, section_number, section_title, section_context)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', rows)
    elif category == 'actors':
        conn.executemany('''
            INSERT INTO actors (source_id, extraction_text, role_raw, role_canonical,
                              char_start, char_end, section_number, section_title, section_context)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', rows)
    elif category == 'procedures':
        conn.executemany('''
            INSERT INTO procedures (source_id, extraction_text, step_name, action, step_order,
                                  char_start, char_end, section_number, section_title, section_context)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', rows)
    elif category == 'deadlines':
        conn.executemany('''
            INSERT INTO deadlines (source_id, extraction_text, timeframe, char_start, char_end,
                                 section_number, section_title, section_context)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', rows)

    conn.commit()
    logger.info(f'✓ Loaded {len(rows):,} {category}')
    total_loaded += len(rows)

# Update total_entities for BIA source
conn.execute('UPDATE source_documents SET total_entities = ? WHERE id = ?', (total_loaded, source_id))
conn.commit()

logger.info('\n' + '='*70)
logger.info('LOADING COMPLETE')
logger.info('='*70)
logger.info(f'Total BIA entities loaded: {total_loaded:,}')

# Show stats by source
logger.info('\n=== Per-Source Statistics ===')
cursor = conn.execute('SELECT * FROM v_extraction_stats_by_source ORDER BY source_name, category')
for row in cursor.fetchall():
    source, category, total, sections = row
    logger.info(f'{source:20s} | {category:15s}: {total:5,} entities')

conn.close()
logger.info('\n✓ Database updated successfully!')
logger.info('\nReady for cross-source queries!')

if __name__ == '__main__':
    main()
