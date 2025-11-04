---
description: Search knowledge base for keyword across all sources
argument-hint: [keyword]
allowed-tools: Bash(sqlite3:*)
---

Search for: **$ARGUMENTS**

**Execute comprehensive search:**

```sql
sqlite3 -header -column database/insolvency_knowledge.db "
-- Search in relationships
SELECT '════════ RELATIONSHIPS ════════' as header;

SELECT
    substr(relationship_text, 1, 100) as quote,
    bia_section,
    source_name
FROM v_complete_duties
WHERE relationship_text LIKE '%$ARGUMENTS%'
LIMIT 10;

-- Search in BIA sections
SELECT '════════ BIA SECTIONS ════════' as header;

SELECT
    section_number,
    section_title,
    substr(full_text, INSTR(LOWER(full_text), LOWER('$ARGUMENTS')) - 50, 150) as context
FROM bia_sections
WHERE full_text LIKE '%$ARGUMENTS%'
LIMIT 10;

-- Search in entities
SELECT '════════ ENTITIES ════════' as header;

SELECT
    'Actor' as type,
    role_canonical as name,
    extraction_text as context
FROM actors
WHERE extraction_text LIKE '%$ARGUMENTS%'
LIMIT 5
UNION ALL
SELECT
    'Procedure',
    extraction_text,
    section_context
FROM procedures
WHERE extraction_text LIKE '%$ARGUMENTS%'
LIMIT 5;
"
```

**Present results showing:**
1. Extracted relationships with keyword
2. BIA sections containing keyword
3. Entities mentioning keyword
4. All with section references for traceability
