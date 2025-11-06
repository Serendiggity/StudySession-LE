# Database Directory

**Current Architecture:** Multi-project structure (as of January 2025)

## Active Database

**Location:** `../projects/insolvency-law/database/knowledge.db`

The active database has been moved to the project-specific location to support multi-domain architecture.

**Contents:**
- 16,531 rows across 22 tables
- 385 complete BIA sections (full text, no truncation)
- 2,088 duty_relationships (legal rules with context)
- 5,857 actors, 3,106 procedures, 2,144 documents
- 17 views including v_complete_duties (enriched relationships)
- 5 OSB Directives with FTS5 search

## Archived Database (LAST STABLE VERSION)

**Location:** `backups/insolvency_knowledge_STABLE_pre_migration_20251105.db`

**Purpose:** Rollback point if issues arise with current database

This is the last stable version before migration to the new project structure. It contains:
- 13,779 entities from 3 sources
- 385 complete BIA statutory provisions
- 5 OSB Directives with full text
- All atomic entities and relationships

**When to use:** Only if the current database has critical issues. To restore:
```bash
cp backups/insolvency_knowledge_STABLE_pre_migration_20251105.db ../projects/insolvency-law/database/knowledge.db
```

## Quick Start

### Query the Active Database

```bash
# Simple query
sqlite3 ../projects/insolvency-law/database/knowledge.db "SELECT full_text FROM bia_sections WHERE section_number = '50.4';"

# Search with FTS5 ranking
sqlite3 ../projects/insolvency-law/database/knowledge.db "
SELECT section_number, section_title, rank
FROM bia_sections
JOIN bia_sections_fts ON bia_sections.rowid = bia_sections_fts.rowid
WHERE bia_sections_fts MATCH 'extension proposal'
ORDER BY rank
LIMIT 5;
"

# Query duty relationships (legal rules)
sqlite3 ../projects/insolvency-law/database/knowledge.db "
SELECT actor, modal_verb, substr(relationship_text, 1, 100)
FROM v_complete_duties
WHERE bia_section = '172'
LIMIT 5;
"
```

### Using with AI

The database is optimized for AI assistants like Claude. Use tools in `/tools/query/` for advanced queries.

## Contents

### Sources (3)

1. **Insolvency Administration Course Material** - 8,376 entities
   - Concepts, deadlines, documents, actors, procedures, consequences, statutory references

2. **BIA Statute** - 5,403 entities + 385 complete sections
   - Key entity types + full statutory provision text

3. **OSB Directives** - 5 directives
   - Directive 6R7 (Assessment)
   - Directive 16R (Statement of Affairs)
   - Directive 17 (Document Retention)
   - Directive 32R (Electronic Recordkeeping)
   - Directive 4R (Delegation)

### Performance

- Query speed: <5ms average
- Section lookup: <1ms (indexed)
- Full-text search: 1-4ms (FTS5 optimized)

### Validation

- Quiz 1: 100% accuracy (10/10 questions)
- Quiz 2: 100% accuracy (15/15 questions with Directives)

## Backups

Located in `backups/` subdirectory with timestamps.
