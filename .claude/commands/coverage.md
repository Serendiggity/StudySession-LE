---
description: Show extraction coverage statistics
allowed-tools: Bash(sqlite3:*)
---

Show knowledge base extraction coverage statistics.

**Execute:**

```sql
sqlite3 -header -column database/insolvency_knowledge.db "
-- Overall statistics
SELECT '════════ OVERALL STATISTICS ════════' as header;

SELECT
    sd.source_name,
    COUNT(DISTINCT dr.bia_section) as sections_with_relationships,
    COUNT(dr.id) as duty_relationships,
    (SELECT COUNT(*) FROM document_requirements WHERE source_id = sd.id) as document_requirements,
    COUNT(dr.id) + (SELECT COUNT(*) FROM document_requirements WHERE source_id = sd.id) as total
FROM source_documents sd
LEFT JOIN duty_relationships dr ON sd.id = dr.source_id
GROUP BY sd.source_name;

-- BIA coverage
SELECT '════════ BIA COVERAGE ════════' as header;

SELECT
    'BIA sections with relationships' as metric,
    COUNT(DISTINCT bia_section) || ' / 385 (' ||
    ROUND(COUNT(DISTINCT bia_section) * 100.0 / 385, 1) || '%)' as value
FROM duty_relationships
WHERE source_id = 2;

-- Top sections by relationship count
SELECT '════════ TOP 10 SECTIONS ════════' as header;

SELECT
    bia_section,
    COUNT(*) as relationships
FROM duty_relationships
WHERE source_id = 2
GROUP BY bia_section
ORDER BY relationships DESC
LIMIT 10;
"
```

**Format output showing:**
1. Total relationships by source
2. BIA coverage percentage
3. Top sections with most relationships
4. Extraction quality metrics
