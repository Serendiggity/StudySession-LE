---
name: test-ultra-minimal
description: Ultra minimal - exactly like insolvency-simple
tools: Bash
model: inherit
---

Answer in sidebar format:

```
┌─ Q: [question]
├─ A: [answer]
└─ Source: BIA
```

Query: `SELECT section_number, full_text FROM bia_sections WHERE section_number = '172' LIMIT 1`

Return first result in sidebar.
