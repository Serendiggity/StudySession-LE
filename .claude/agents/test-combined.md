---
name: test-combined
description: Combined format test - sidebar plus special chars plus code
tools: Bash
model: inherit
---

Return sidebar with all elements:

```
┌─ Q: What type of discharge when no §173 facts proven?
│
├─ A: ✅ A. Absolute discharge
│
├─ Quote: "the court may (a) grant or refuse"  §172(1)(a)
│
└─ Source: BIA Statute
```

Code example:
```sql
SELECT section_number FROM bia_sections WHERE section_number = '172';
```
