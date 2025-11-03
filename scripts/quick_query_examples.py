"""
Quick query examples using optimized database.
Demonstrates fastest ways to find answers.
"""

import sqlite3
from pathlib import Path
import time

db_path = Path('data/output/insolvency_knowledge.db')
conn = sqlite3.connect(db_path)

print('='*70)
print('OPTIMIZED QUERY EXAMPLES - Fast Answer Retrieval')
print('='*70)

# Example 1: Find BIA section by topic (FAST - uses FTS)
print('\n1. Find sections about "extensions" (Full-Text Search)')
start = time.time()
cursor = conn.execute('''
    SELECT s.section_number, s.section_title, p.part_title
    FROM bia_sections_fts fts
    JOIN bia_sections s ON fts.rowid = s.rowid
    LEFT JOIN bia_parts p ON s.part_number = p.part_number
    WHERE fts.full_text MATCH 'extension'
    LIMIT 5
''')
results = cursor.fetchall()
elapsed = time.time() - start

print(f'   Found {len(results)} sections in {elapsed*1000:.1f}ms:')
for row in results:
    print(f'   - Section {row[0]}: {row[1]} ({row[2]})')

# Example 2: Get specific section instantly (INSTANT - primary key lookup)
print('\n2. Get complete section 50.4 (Direct lookup)')
start = time.time()
cursor = conn.execute('''
    SELECT section_title, full_text
    FROM bia_sections
    WHERE section_number = '50.4'
''')
result = cursor.fetchone()
elapsed = time.time() - start

if result:
    print(f'   Retrieved {len(result[1]):,} chars in {elapsed*1000:.2f}ms')
    print(f'   Title: {result[0]}')

# Example 3: Compare entities across sources (FAST - pre-aggregated view)
print('\n3. Compare "Trustee" mentions across sources (Pre-aggregated)')
start = time.time()
cursor = conn.execute('''
    SELECT source_name, mention_count, section_count
    FROM v_actors_cross_source
    WHERE role_canonical = 'Trustee'
''')
results = cursor.fetchall()
elapsed = time.time() - start

print(f'   Found in {elapsed*1000:.1f}ms:')
for row in results:
    print(f'   - {row[0]:20s}: {row[1]:4d} mentions in {row[2]:3d} sections')

# Example 4: Search multiple keywords (FAST - FTS with boolean)
print('\n4. Find sections with "proposal" AND "refusal" (FTS Boolean)')
start = time.time()
cursor = conn.execute('''
    SELECT s.section_number, s.section_title
    FROM bia_sections_fts fts
    JOIN bia_sections s ON fts.rowid = s.rowid
    WHERE fts.full_text MATCH 'proposal AND refusal'
    LIMIT 5
''')
results = cursor.fetchall()
elapsed = time.time() - start

print(f'   Found {len(results)} sections in {elapsed*1000:.1f}ms:')
for row in results:
    print(f'   - Section {row[0]}: {row[1]}')

# Example 5: Get all sections in a Part (FAST - indexed)
print('\n5. Get all Division I Proposal sections (Indexed lookup)')
start = time.time()
cursor = conn.execute('''
    SELECT section_number, section_title
    FROM v_bia_quick_lookup
    WHERE part_number = 'PART III'
      AND full_text LIKE '%Division I%'
    LIMIT 10
''')
results = cursor.fetchall()
elapsed = time.time() - start

print(f'   Found {len(results)} sections in {elapsed*1000:.1f}ms')

print('\n' + '='*70)
print('SPEED OPTIMIZATION SUMMARY')
print('='*70)
print('''
Best Practices for Fast Queries:

1. Section lookup by number:
   SELECT * FROM bia_sections WHERE section_number = 'X'
   → Instant (primary key)

2. Text search in BIA:
   SELECT * FROM bia_sections_fts WHERE full_text MATCH 'keyword'
   → 10-100x faster than LIKE

3. Cross-source comparison:
   SELECT * FROM v_actors_cross_source WHERE role_canonical = 'X'
   → Pre-aggregated, instant

4. Boolean search:
   WHERE full_text MATCH 'keyword1 AND keyword2'
   WHERE full_text MATCH 'keyword1 OR keyword2'
   WHERE full_text MATCH 'keyword1 NOT keyword2'
   → Powerful and fast

5. Phrase search:
   WHERE full_text MATCH '"exact phrase"'
   → Finds exact matches only
''')

conn.close()
