---
description: Find what documents are required for a procedure
argument-hint: [procedure-keyword]
allowed-tools: Bash(sqlite3:*)
---

Find documents required for: **$ARGUMENTS**

**Execute:**

```sql
sqlite3 -header -column database/insolvency_knowledge.db "
SELECT
    procedure,
    document,
    CASE is_mandatory WHEN 1 THEN 'Required' ELSE 'Optional' END as requirement,
    filing_context,
    bia_section,
    source_name
FROM v_document_requirements
WHERE procedure LIKE '%$ARGUMENTS%'
   OR document LIKE '%$ARGUMENTS%'
ORDER BY is_mandatory DESC, bia_section;
"
```

**Format as table with:**
- Procedure name
- Required document (canonical name)
- Mandatory vs Optional
- When/why needed (filing_context)
- BIA section reference
- Source (BIA or Study Materials)
