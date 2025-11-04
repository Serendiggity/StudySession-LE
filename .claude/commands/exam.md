---
description: Answer exam question with direct BIA quotes and cross-reference following
argument-hint: [your exam question]
allowed-tools: Bash(sqlite3:*)
---

Answer this exam question: **$ARGUMENTS**

**MANDATORY OUTPUT FORMAT (always follow this):**

```markdown
## Question
[Restate the exam question]

## Answer
✅ [Correct answer choice]

## Direct Quote (Primary Source)
"[Exact text from relationship_text or bia_sections.full_text]"

**Section Reference:** Section X.X
**Source:** BIA Statute / Study Materials

## Cross-References (if any references found)
[If the quote mentions "section 68" or other sections, FOLLOW THEM:]

**Referenced Section X.X:**
"[Direct quote from referenced section]"
**Context:** [Why this reference matters]

## Explanation
[Brief explanation connecting quote to answer]

## Traceability
- Primary section: Section X.X
- Cross-references: Section Y.Y, Section Z.Z (if applicable)
- Database query used: [show SQL]
```

**Search strategy:**

1. Query `v_complete_duties` for relationships
2. Extract `relationship_text` for direct quote
3. If quote contains "section X", "subsection Y", or "paragraph Z":
   - Query that referenced section
   - Include its text in cross-references
4. Always show the SQL query used for traceability
5. Always include direct quotes (never paraphrase)

**Example cross-reference following:**
```
If quote says: "required to make payments under section 68"
→ Query section 68
→ Show: Section 68 defines "surplus income"
→ Include that context in answer
```

**Required elements (never omit):**
- ✅ Direct quote from source
- ✅ Section number
- ✅ Source (BIA/Study Materials)
- ✅ Cross-references followed
- ✅ SQL query shown

