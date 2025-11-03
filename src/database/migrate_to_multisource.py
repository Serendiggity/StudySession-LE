"""
Migration script: Add multi-source support to existing database.

This script:
1. Backs up the existing database
2. Creates a new database with multi-source schema
3. Registers existing study material as source_id=1
4. Re-loads all existing extractions with source tracking
"""

import shutil
import logging
from pathlib import Path
from datetime import datetime
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from database.loader import KnowledgeBaseLoader

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def migrate_to_multisource():
    """Migrate existing database to multi-source schema."""

    # Paths
    project_root = Path(__file__).parent.parent.parent
    db_path = project_root / 'data/output/insolvency_knowledge.db'
    backup_dir = project_root / 'data/output/backups'
    section_map = project_root / 'data/output/section_map.json'
    extraction_dir = project_root / 'data/output/knowledge_base'

    # Create backup directory
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Backup existing database
    if db_path.exists():
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = backup_dir / f'insolvency_knowledge_backup_{timestamp}.db'
        logger.info(f'Creating backup: {backup_path}')
        shutil.copy2(db_path, backup_path)
        logger.info('✓ Backup created')

        # Delete old database
        logger.info('Removing old database...')
        db_path.unlink()
        logger.info('✓ Old database removed')
    else:
        logger.warning('No existing database found - creating new one')

    # Step 2: Create new database with multi-source schema
    logger.info('Creating new database with multi-source schema...')
    loader = KnowledgeBaseLoader(db_path, section_map)
    logger.info('✓ New schema initialized')

    # Step 3: Register study material as source_id=1
    logger.info('Registering study material as source...')
    source_id = loader.register_source(
        source_name='Study Material',
        file_path='data/input/study_materials/InsolvencyStudyGuide.pdf',
        pages=291,
        total_chars=492000,  # Approximate
        notes='Complete insolvency study guide - 18 chapters covering BIA procedures'
    )
    logger.info(f'✓ Study material registered with source_id={source_id}')

    # Step 4: Re-load all existing extractions with source tracking
    logger.info('Loading all categories with source tracking...')
    loader.load_all_categories(extraction_dir, source_id)

    # Step 5: Verify migration
    stats = loader.get_stats()
    logger.info('\n' + '='*70)
    logger.info('MIGRATION COMPLETE - Database Statistics:')
    logger.info('='*70)
    for category, data in stats.items():
        logger.info(f'{category:20s}: {data["total"]:5d} items across {data["sections"]:4d} sections')

    # Test source tracking
    cursor = loader.conn.execute('SELECT * FROM source_documents')
    sources = cursor.fetchall()
    logger.info('\n' + '='*70)
    logger.info('Registered Sources:')
    logger.info('='*70)
    for source in sources:
        logger.info(f'ID: {source[0]} | Name: {source[1]} | Entities: {source[6]}')

    loader.close()

    logger.info('\n✓ Migration successful!')
    logger.info(f'New database: {db_path}')
    logger.info(f'Backup saved: {backup_path if db_path.exists() else "N/A"}')

    # Next steps
    logger.info('\n' + '='*70)
    logger.info('NEXT STEPS:')
    logger.info('='*70)
    logger.info('1. Verify data with: sqlite3 data/output/insolvency_knowledge.db "SELECT * FROM v_extraction_stats_by_source;"')
    logger.info('2. Add BIA statute as second source')
    logger.info('3. Run cross-source queries to test multi-source support')


if __name__ == '__main__':
    print('\n' + '='*70)
    print('MULTI-SOURCE MIGRATION')
    print('='*70)
    print('This will:')
    print('- Backup existing database')
    print('- Create new schema with source tracking')
    print('- Re-load all data with source_id=1 (Study Material)')
    print('='*70)

    response = input('\nProceed with migration? [y/N]: ')

    if response.lower() in ['y', 'yes']:
        migrate_to_multisource()
    else:
        print('Migration cancelled.')
