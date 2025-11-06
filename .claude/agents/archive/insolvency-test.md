---
name: insolvency-test
description: Test with hardcoded examination query
model: inherit
---

Answer using sidebar format:

```
┌─ Q: [question]
├─ A: [answer]
└─ Source: BIA §161
```

Query database to get Section 161:

```sql
SELECT section_number, full_text FROM bia_sections WHERE section_number = '161';
```

Return result about examination in sidebar format.
