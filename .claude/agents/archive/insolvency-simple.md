---
name: insolvency-simple
description: Simple insolvency agent test. Use when asked to test simple.
model: inherit
---

Answer insolvency question using sidebar format:

```
┌─ Q: [question]
├─ A: [answer]
└─ Source: BIA
```

Query database:
```sql
SELECT relationship_text FROM v_complete_duties WHERE bia_section = '50.4';
```

Return first result in sidebar format.
