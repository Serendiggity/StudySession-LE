#!/usr/bin/env python3
"""
Load BIA statute sections into new multi-project database.
"""

import sqlite3
import json
from pathlib import Path

def main():
    # Paths
    db_path = Path('projects/insolvency-law/database/knowledge.db')
    structure_path = Path('data/output/bia_structure.json')

    print('='*70)
    print('LOADING BIA SECTIONS INTO DATABASE')
    print('='*70)

    # Load structure
    print(f'\nLoading: {structure_path}')
    with open(structure_path, 'r') as f:
        data = json.load(f)

    print(f'✓ Found {len(data["parts"])} Parts')
    print(f'✓ Found {len(data["sections"])} Sections')

    # Connect to database
    print(f'\nConnecting to: {db_path}')
    conn = sqlite3.connect(db_path)

    # Create tables
    print('\nCreating tables...')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS bia_parts (
            part_number TEXT PRIMARY KEY,
            part_title TEXT,
            char_start INTEGER,
            char_end INTEGER
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS bia_sections (
            section_number TEXT PRIMARY KEY,
            part_number TEXT,
            section_title TEXT,
            full_text TEXT,
            char_start INTEGER,
            char_end INTEGER,
            FOREIGN KEY (part_number) REFERENCES bia_parts(part_number)
        )
    ''')

    # Create FTS5 index for section full text
    conn.execute('''
        CREATE VIRTUAL TABLE IF NOT EXISTS bia_sections_fts
        USING fts5(
            section_number,
            section_title,
            full_text,
            content='bia_sections',
            content_rowid='rowid'
        )
    ''')

    # Create trigger to keep FTS updated
    conn.execute('''
        CREATE TRIGGER IF NOT EXISTS bia_sections_fts_insert
        AFTER INSERT ON bia_sections
        BEGIN
            INSERT INTO bia_sections_fts(rowid, section_number, section_title, full_text)
            VALUES (new.rowid, new.section_number, new.section_title, new.full_text);
        END
    ''')

    conn.commit()
    print('✓ Tables created')

    # Load Parts
    print('\nLoading Parts...')
    parts_loaded = 0
    for part in data['parts']:
        conn.execute('''
            INSERT OR REPLACE INTO bia_parts (part_number, part_title, char_start, char_end)
            VALUES (?, ?, ?, ?)
        ''', (part['part_number'], part['part_title'], part['char_start'], part['char_end']))
        parts_loaded += 1

    conn.commit()
    print(f'✓ Loaded {parts_loaded} Parts')

    # Load Sections (with progress)
    print('\nLoading Sections...')
    sections_loaded = 0
    for section in data['sections']:
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

        if sections_loaded % 50 == 0:
            print(f'  {sections_loaded} sections...')

    conn.commit()
    print(f'✓ Loaded {sections_loaded} Sections')

    # Rebuild FTS index
    print('\nRebuilding FTS index...')
    conn.execute("INSERT INTO bia_sections_fts(bia_sections_fts) VALUES('rebuild')")
    conn.commit()
    print('✓ FTS index rebuilt')

    # Verification
    print('\n' + '='*70)
    print('VERIFICATION')
    print('='*70)

    cursor = conn.execute('SELECT COUNT(*) FROM bia_parts')
    print(f'Parts: {cursor.fetchone()[0]}')

    cursor = conn.execute('SELECT COUNT(*) FROM bia_sections')
    print(f'Sections: {cursor.fetchone()[0]}')

    cursor = conn.execute('SELECT COUNT(*) FROM bia_sections_fts')
    print(f'FTS index: {cursor.fetchone()[0]}')

    # Test search for discharge
    print('\nTest search for "discharge":')
    cursor = conn.execute('''
        SELECT section_number, section_title
        FROM bia_sections
        WHERE section_number IN (
            SELECT section_number FROM bia_sections_fts
            WHERE full_text MATCH 'discharge'
        )
        LIMIT 5
    ''')
    for row in cursor.fetchall():
        print(f'  §{row[0]}: {row[1]}')

    conn.close()

    print('\n' + '='*70)
    print('✓ BIA SECTIONS LOADED SUCCESSFULLY')
    print('='*70)

if __name__ == '__main__':
    main()
