---
description: Find all duties for a specific actor (Trustee, Creditor, Bankrupt, etc.)
argument-hint: [actor-name]
allowed-tools: Bash(sqlite3:*)
---

Find all duties for: **$1**

**Execute query and format results in a table:**

```sql
sqlite3 -header -column database/insolvency_knowledge.db "
SELECT
    actor,
    substr(procedure, 1, 50) as what_they_must_do,
    deadline as when,
    consequence as or_else,
    modal_verb,
    bia_section,
    source_name
FROM v_complete_duties
WHERE actor LIKE '%$1%'
  AND procedure IS NOT NULL
ORDER BY
    CASE modal_verb
        WHEN 'shall' THEN 1
        WHEN 'must' THEN 2
        WHEN 'may' THEN 3
        ELSE 4
    END,
    bia_section
LIMIT 30;
"
```

**Present results as:**
1. Table with: Actor | What | When | Or Else | Modal | Section
2. Group by mandatory (shall/must) vs discretionary (may)
3. Include direct BIA quotes in relationship_text column
4. Cite specific sections for traceability
