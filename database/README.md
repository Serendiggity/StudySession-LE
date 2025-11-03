# Insolvency Knowledge Base

**This is the main product** - a multi-source, AI-queryable database for insolvency exam preparation.

## Database File

**`insolvency_knowledge.db`** - SQLite database containing:
- 13,779 entities from 3 sources
- 385 complete BIA statutory provisions
- 5 OSB Directives with full text
- Cross-reference links between sources

## Quick Start

### Query the Database

```bash
# Simple query
sqlite3 insolvency_knowledge.db "SELECT full_text FROM bia_sections WHERE section_number = '50.4';"

# Cross-source comparison
sqlite3 insolvency_knowledge.db "
SELECT source_name, COUNT(*)
FROM actors a
JOIN source_documents sd ON a.source_id = sd.id
WHERE role_canonical = 'Trustee'
GROUP BY source_name;
"

# Full-text search
sqlite3 insolvency_knowledge.db "
SELECT section_number, section_title
FROM bia_sections_fts
WHERE full_text MATCH 'extension AND proposal';
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
