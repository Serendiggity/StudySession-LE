---
description: Query BIA section with relationships and full text
argument-hint: [section-number]
allowed-tools: Bash(sqlite3:*)
---

Query BIA Section $1 from the knowledge base.

**Execute this SQL query:**

```sql
sqlite3 -header -column database/insolvency_knowledge.db "
-- Section text
SELECT
    section_number,
    section_title,
    part_number,
    substr(full_text, 1, 500) as text_preview
FROM bia_sections
WHERE section_number = '$1';

-- Extracted relationships
SELECT
    '════════ RELATIONSHIPS ════════' as separator;

SELECT
    actor,
    procedure,
    deadline,
    consequence,
    modal_verb,
    relationship_text
FROM v_complete_duties
WHERE bia_section LIKE '$1%'
ORDER BY modal_verb;

-- Required documents
SELECT
    '════════ DOCUMENTS ════════' as separator;

SELECT
    procedure,
    document,
    is_mandatory,
    filing_context
FROM v_document_requirements
WHERE bia_section LIKE '$1%';
"
```

**Format output as:**
1. Section title and preview
2. All relationships (duties)
3. Required documents
4. Direct BIA quotes with section references
