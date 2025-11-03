"""
Load BIA extraction results into database as source_id=2.

Note: BIA has simpler section structure (just section numbers, not hierarchical)
so we'll create a minimal section map.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import logging
from database.loader import KnowledgeBaseLoader

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def main():
    """Load BIA into database."""
    logger.info('='*70)
    logger.info('LOADING BIA STATUTE INTO DATABASE')
    logger.info('='*70)

    # Paths
    db_path = Path('data/output/insolvency_knowledge.db')
    section_map = Path('data/output/section_map.json')  # Using study material map for now
    extraction_dir = Path('data/output/bia_extraction')

    logger.info(f'\nDatabase: {db_path}')
    logger.info(f'Extractions: {extraction_dir}')

    # Initialize loader
    loader = KnowledgeBaseLoader(db_path, section_map)

    # Register BIA as source
    logger.info('\nRegistering BIA statute as source...')
    source_id = loader.register_source(
        source_name='BIA Statute',
        file_path='Materials/Bankruptcy and Insolvency Act.pdf',
        pages=306,
        total_chars=784344,  # English-only version
        notes='Bankruptcy and Insolvency Act (R.S.C., 1985, c. B-3) - English sections only'
    )
    logger.info(f'✓ BIA registered with source_id={source_id}')

    # Load categories
    logger.info('\nLoading BIA categories...')
    logger.info('Note: Using study material section map (BIA sections will be mapped as available)')

    # Only load categories that exist
    categories_to_load = {
        'documents': 770,
        'actors': 2988,
        'procedures': 1318,
        'deadlines': 327
    }

    logger.info(f'\nCategories to load:')
    for cat, count in categories_to_load.items():
        logger.info(f'  {cat:20s}: {count:5,} entities')

    # Load all categories
    loader.load_all_categories(extraction_dir, source_id)

    # Verify
    stats = loader.get_stats()
    logger.info('\n' + '='*70)
    logger.info('DATABASE STATISTICS (ALL SOURCES)')
    logger.info('='*70)
    for category, data in stats.items():
        logger.info(f'{category:20s}: {data["total"]:5d} items across {data["sections"]:4d} sections')

    # Check source-specific stats
    logger.info('\n' + '='*70)
    logger.info('PER-SOURCE STATISTICS')
    logger.info('='*70)
    cursor = loader.conn.execute('SELECT * FROM v_extraction_stats_by_source ORDER BY source_name, category')
    for row in cursor.fetchall():
        source, category, total, sections = row
        logger.info(f'{source:20s} | {category:15s}: {total:5,} entities')

    loader.close()

    logger.info('\n✓ BIA loaded successfully!')
    logger.info('\nNext: Test cross-source queries!')


if __name__ == '__main__':
    main()
