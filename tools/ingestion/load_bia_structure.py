"""
Load BIA structural data into database.
Loads Parts and Sections from parsed structure JSON.
"""

import sqlite3
import json
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def main():
    """Load BIA structure into database."""
    db_path = Path('data/output/insolvency_knowledge.db')
    structure_path = Path('data/output/bia_structure.json')

    logger.info('='*70)
    logger.info('LOADING BIA STRUCTURE INTO DATABASE')
    logger.info('='*70)

    # Load parsed structure
    logger.info(f'\nLoading structure: {structure_path}')
    with open(structure_path, 'r') as f:
        data = json.load(f)

    logger.info(f'✓ Loaded {len(data["parts"])} Parts')
    logger.info(f'✓ Loaded {len(data["sections"])} Sections')

    # Connect to database
    logger.info(f'\nConnecting to: {db_path}')
    conn = sqlite3.connect(db_path)
    logger.info('✓ Connected (schema already exists)')

    # Load Parts
    logger.info('\nLoading BIA Parts...')
    parts_loaded = 0
    for part in data['parts']:
        try:
            conn.execute('''
                INSERT OR REPLACE INTO bia_parts (part_number, part_title, char_start, char_end)
                VALUES (?, ?, ?, ?)
            ''', (part['part_number'], part['part_title'], part['char_start'], part['char_end']))
            parts_loaded += 1
        except Exception as e:
            logger.error(f'  Error loading {part["part_number"]}: {e}')

    conn.commit()
    logger.info(f'✓ Loaded {parts_loaded} Parts')

    # Load Sections
    logger.info('\nLoading BIA Sections...')
    sections_loaded = 0
    for section in data['sections']:
        try:
            conn.execute('''
                INSERT OR REPLACE INTO bia_sections
                (section_number, part_number, section_title, full_text, char_start, char_end)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                section['section_number'],
                section['part_number'],
                section['section_title'],
                section['full_text'],
                section['char_start'],
                section['char_end']
            ))
            sections_loaded += 1

            if sections_loaded % 100 == 0:
                logger.info(f'  Loaded {sections_loaded} sections...')

        except Exception as e:
            logger.error(f'  Error loading section {section["section_number"]}: {e}')

    conn.commit()
    logger.info(f'✓ Loaded {sections_loaded} Sections')

    # Verification
    logger.info('\n' + '='*70)
    logger.info('DATABASE VERIFICATION')
    logger.info('='*70)

    # Check Parts
    cursor = conn.execute('SELECT COUNT(*) FROM bia_parts')
    count = cursor.fetchone()[0]
    logger.info(f'BIA Parts in database: {count}')

    # Check Sections
    cursor = conn.execute('SELECT COUNT(*) FROM bia_sections')
    count = cursor.fetchone()[0]
    logger.info(f'BIA Sections in database: {count}')

    # Sample sections
    logger.info('\nSample sections:')
    cursor = conn.execute('''
        SELECT section_number, section_title, LENGTH(full_text)
        FROM bia_sections
        WHERE section_number IN ('2', '43', '50.4', '57', '69')
        ORDER BY section_number
    ''')
    for row in cursor.fetchall():
        logger.info(f'  Section {row[0]:6s}: {row[1][:40]:40s} ({row[2]:5,} chars)')

    # Test critical section 50.4
    logger.info('\n' + '='*70)
    logger.info('CRITICAL SECTION TEST: 50.4 (Extension Provisions)')
    logger.info('='*70)

    cursor = conn.execute('''
        SELECT section_title, LENGTH(full_text), full_text
        FROM bia_sections
        WHERE section_number = '50.4'
    ''')
    result = cursor.fetchone()
    if result:
        title, text_len, full_text = result
        logger.info(f'Title: {title}')
        logger.info(f'Text length: {text_len:,} chars')

        # Check for exam answer content
        has_45days = '45 days' in full_text
        has_5months = 'five months' in full_text

        logger.info(f'\nContent verification:')
        logger.info(f'  Contains "45 days": {has_45days}')
        logger.info(f'  Contains "five months": {has_5months}')

        if has_45days and has_5months:
            logger.info(f'\n✅ Section 50.4 COMPLETE - Can answer exam question!')
        else:
            logger.info(f'\n⚠ Section 50.4 incomplete')

    else:
        logger.info('⚠ Section 50.4 not found in database')

    conn.close()

    logger.info('\n✓ BIA structure loaded successfully!')
    logger.info('\nReady to test exam questions!')


if __name__ == '__main__':
    main()
