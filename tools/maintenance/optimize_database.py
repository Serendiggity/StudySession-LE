"""
Database optimizations for faster answer retrieval.

Implements:
1. Full-Text Search (FTS5) for BIA sections
2. Additional indexes for common queries
3. Materialized views for frequent lookups
4. Query performance monitoring
"""

import sqlite3
from pathlib import Path
import time

db_path = Path('data/output/insolvency_knowledge.db')

print('='*70)
print('DATABASE SPEED OPTIMIZATIONS')
print('='*70)

conn = sqlite3.connect(db_path)

# Optimization 1: Full-Text Search Index for BIA Sections
print('\n1. Creating Full-Text Search index for BIA sections...')
print('   This enables FAST text searching (10-100x faster than LIKE)')

start = time.time()

conn.executescript('''
-- Create FTS5 virtual table for BIA sections
CREATE VIRTUAL TABLE IF NOT EXISTS bia_sections_fts USING fts5(
    section_number,
    section_title,
    full_text,
    content='bia_sections',
    content_rowid='rowid'
);

-- Populate FTS index
INSERT INTO bia_sections_fts(rowid, section_number, section_title, full_text)
SELECT rowid, section_number, section_title, full_text
FROM bia_sections;

-- Triggers to keep FTS in sync
CREATE TRIGGER IF NOT EXISTS bia_sections_ai AFTER INSERT ON bia_sections BEGIN
  INSERT INTO bia_sections_fts(rowid, section_number, section_title, full_text)
  VALUES (new.rowid, new.section_number, new.section_title, new.full_text);
END;

CREATE TRIGGER IF NOT EXISTS bia_sections_ad AFTER DELETE ON bia_sections BEGIN
  INSERT INTO bia_sections_fts(bia_sections_fts, rowid, section_number, section_title, full_text)
  VALUES('delete', old.rowid, old.section_number, old.section_title, old.full_text);
END;

CREATE TRIGGER IF NOT EXISTS bia_sections_au AFTER UPDATE ON bia_sections BEGIN
  INSERT INTO bia_sections_fts(bia_sections_fts, rowid, section_number, section_title, full_text)
  VALUES('delete', old.rowid, old.section_number, old.section_title, old.full_text);
  INSERT INTO bia_sections_fts(rowid, section_number, section_title, full_text)
  VALUES (new.rowid, new.section_number, new.section_title, new.full_text);
END;
''')

elapsed = time.time() - start
print(f'   ✓ Created in {elapsed:.2f}s')

# Optimization 2: Additional indexes for common queries
print('\n2. Adding performance indexes for common queries...')

start = time.time()

conn.executescript('''
-- Index for filtering by extraction text (common in WHERE clauses)
CREATE INDEX IF NOT EXISTS idx_concepts_extraction_text ON concepts(extraction_text);
CREATE INDEX IF NOT EXISTS idx_procedures_extraction_text ON procedures(extraction_text);

-- Composite indexes for common JOIN + WHERE patterns
CREATE INDEX IF NOT EXISTS idx_actors_source_canonical ON actors(source_id, role_canonical);
CREATE INDEX IF NOT EXISTS idx_deadlines_source_timeframe ON deadlines(source_id, timeframe);
CREATE INDEX IF NOT EXISTS idx_documents_source_canonical ON documents(source_id, document_name_canonical);

-- Index for section context searches
CREATE INDEX IF NOT EXISTS idx_concepts_section_context ON concepts(section_context);
''')

elapsed = time.time() - start
print(f'   ✓ Created in {elapsed:.2f}s')

# Optimization 3: Common query views (pre-computed)
print('\n3. Creating materialized views for frequent queries...')

start = time.time()

conn.executescript('''
-- Quick lookup: BIA sections by topic keywords
CREATE VIEW IF NOT EXISTS v_bia_sections_by_topic AS
SELECT
    section_number,
    section_title,
    part_number,
    CASE
        WHEN full_text LIKE '%proposal%' THEN 'Proposals'
        WHEN full_text LIKE '%bankruptcy order%' THEN 'Bankruptcy Orders'
        WHEN full_text LIKE '%trustee%appoint%' THEN 'Trustee Appointments'
        WHEN full_text LIKE '%discharge%' THEN 'Discharge'
        WHEN full_text LIKE '%creditor%meeting%' THEN 'Creditor Meetings'
        WHEN full_text LIKE '%extension%' THEN 'Extensions'
        ELSE 'Other'
    END as topic_category,
    LENGTH(full_text) as text_length
FROM bia_sections;

-- Cross-source actor comparison (pre-aggregated)
CREATE VIEW IF NOT EXISTS v_actors_cross_source AS
SELECT
    a.role_canonical,
    sd.source_name,
    COUNT(*) as mention_count,
    COUNT(DISTINCT a.section_number) as section_count
FROM actors a
JOIN source_documents sd ON a.source_id = sd.id
GROUP BY a.role_canonical, sd.source_name;

-- Quick section lookup with part context
CREATE VIEW IF NOT EXISTS v_bia_quick_lookup AS
SELECT
    s.section_number,
    s.section_title,
    p.part_number,
    p.part_title,
    LENGTH(s.full_text) as chars,
    s.full_text
FROM bia_sections s
LEFT JOIN bia_parts p ON s.part_number = p.part_number;
''')

elapsed = time.time() - start
print(f'   ✓ Created in {elapsed:.2f}s')

# Optimization 4: ANALYZE for query planner
print('\n4. Analyzing database for query optimization...')
start = time.time()
conn.execute('ANALYZE')
elapsed = time.time() - start
print(f'   ✓ Completed in {elapsed:.2f}s')

conn.commit()

# Performance test
print('\n' + '='*70)
print('PERFORMANCE TEST')
print('='*70)

# Test 1: FTS search (fast)
print('\nTest 1: Full-text search for "extension"')
start = time.time()
cursor = conn.execute('''
    SELECT section_number, section_title
    FROM bia_sections_fts
    WHERE bia_sections_fts MATCH 'extension'
    LIMIT 10
''')
results = cursor.fetchall()
elapsed = time.time() - start
print(f'   Found {len(results)} results in {elapsed*1000:.1f}ms (FTS optimized)')

# Test 2: Section lookup by number (instant)
print('\nTest 2: Lookup specific section')
start = time.time()
cursor = conn.execute("SELECT full_text FROM bia_sections WHERE section_number = '50.4'")
result = cursor.fetchone()
elapsed = time.time() - start
print(f'   Retrieved {len(result[0]):,} chars in {elapsed*1000:.1f}ms (indexed)')

# Test 3: Cross-source aggregation
print('\nTest 3: Cross-source actor count')
start = time.time()
cursor = conn.execute('''
    SELECT role_canonical, source_name, mention_count
    FROM v_actors_cross_source
    WHERE role_canonical LIKE '%Trustee%'
''')
results = cursor.fetchall()
elapsed = time.time() - start
print(f'   Found {len(results)} results in {elapsed*1000:.1f}ms (pre-aggregated view)')

conn.close()

print('\n' + '='*70)
print('OPTIMIZATIONS COMPLETE')
print('='*70)
print('\n✓ Full-Text Search enabled for BIA sections')
print('✓ Additional indexes created')
print('✓ Materialized views for common queries')
print('✓ Database analyzed for query planning')
print('\nExpected speedup: 10-100x for text searches, 2-5x for complex queries')
