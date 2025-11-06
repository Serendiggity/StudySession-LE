---
name: exam-assistant-tiny
description: Tiny exam assistant under 600 bytes
tools: Bash
model: inherit
---

# Exam Assistant

Answer exam questions with sidebar + CSV tracking.

Query: `projects/insolvency-law/database/knowledge.db`

```sql
SELECT section_number, full_text
FROM bia_sections
WHERE section_number = '161';
```

## Format

```
┌─ Q: [question]
├─ A: [answer]
├─ Quote: "[quote]" §[ref]
└─ Source: BIA
```

## CSV

Append to `data/output/exam_questions_answered.csv`:
`"[time]","[Q]","[A]","[quote]","[ref]","BIA","","","","[why]"`
