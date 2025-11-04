---
description: Quick reference guide for the knowledge base system
---

# Insolvency Knowledge Base - Quick Reference

## Custom Slash Commands

```
/bia [section]          - Query BIA section with relationships
/duties [actor]         - Find duties for actor (Trustee, Creditor, etc.)
/docs [keyword]         - Find required documents
/exam [question]        - Answer exam question with BIA quotes
/diagram [topic] [sec] [type] - Generate Mermaid diagram
/coverage               - Show extraction statistics
/extract-bia            - Extract BIA relationships
/extract-study          - Extract study material relationships
/quick-ref              - This guide
```

## Common SQL Queries

**Find trustee duties:**
```sql
SELECT actor, procedure, deadline, bia_section, relationship_text
FROM v_complete_duties
WHERE actor = 'Trustee' AND procedure IS NOT NULL;
```

**Find document requirements:**
```sql
SELECT procedure, document, is_mandatory, filing_context
FROM v_document_requirements
WHERE procedure LIKE '%proposal%';
```

**Query specific section:**
```sql
SELECT * FROM v_complete_duties WHERE bia_section LIKE '50.4%';
```

## Database Location

`database/insolvency_knowledge.db`

## Key Views

- `v_complete_duties` - All duties with entity names
- `v_document_requirements` - Document requirements
- `v_relationship_stats` - Coverage statistics

## Current Coverage

- BIA: 1,047 relationships (80%)
- Study Materials: 1,123 relationships
- Total: 2,170 relationships

## Documentation

See `README_SYSTEM_GUIDE.md` for complete system documentation.
