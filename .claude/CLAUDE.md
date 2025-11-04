# Insolvency Knowledge Base - Claude Behavior Rules

## Project Context

This is an AI-powered knowledge extraction system for Canadian insolvency law (BIA) and study materials. Built for exam preparation with emphasis on traceability and accuracy.

## DELEGATION RULE (Primary)

**For ANY insolvency, BIA, bankruptcy, proposal, or exam question:**

✅ **DELEGATE to the `insolvency-exam-assistant` subagent**

**Do NOT answer directly** - use the Task tool to invoke the specialized agent:

```
User asks insolvency question
→ I detect it's about BIA/insolvency/exam
→ I use Task tool with subagent_type: "insolvency-exam-assistant"
→ Agent searches database + directives + study materials
→ Agent formats answer with quotes + cross-refs
→ Agent records to CSV
→ Agent returns formatted answer
→ I show result to user
```

**Why delegate:**
- Agent has specialized search strategy (database → files → web)
- Agent enforces mandatory format automatically
- Agent records every Q&A for tracking
- Keeps main conversation context clean
- Agent can do exhaustive searches without cluttering our chat

**Only answer directly if:**
- Question is about the SYSTEM itself (not exam content)
- User explicitly asks me not to delegate

---

## Core Principles (ALWAYS FOLLOW)

### 1. Traceability is Mandatory

**Every answer MUST include:**
- ✅ Direct quote from source (`relationship_text` or `bia_sections.full_text`)
- ✅ Section reference (e.g., "Section 168.1(1)(a)(ii)")
- ✅ Source identification (BIA Statute / Study Materials)
- ✅ SQL query shown (for reproducibility)

**NEVER:**
- ❌ Paraphrase BIA text
- ❌ Give answers without section citations
- ❌ Skip showing the query used

### 2. Cross-Reference Following is Automatic

**If any quote mentions another section:**
- "under section 68" → MUST query Section 68
- "referred to in paragraph (1)" → MUST query that paragraph
- "as defined in section X" → MUST query Section X definition

**Then include referenced content in answer.**

### 3. Fixed Output Formats

**For exam questions, ALWAYS use this structure:**

```markdown
## Question
[Restate question]

## Answer
✅ [Correct answer choice]

## Direct Quote (Primary Source)
"[Exact text from database - NO paraphrasing]"

**Section Reference:** Section X.X(subsection)
**Source:** BIA Statute / Insolvency Administration Course Material

## Cross-References (if any)
**Referenced Section Y.Y:**
"[Direct quote from referenced section]"
**Context:** [Brief explanation of why this reference matters]

## Explanation
[Connect quote to answer - be concise]

## Traceability
- Primary section: Section X.X
- Cross-references: Section Y.Y, Section Z.Z
- Database query:
```sql
[Show exact SQL used]
```

**This format is NON-NEGOTIABLE for all exam-related questions.**

---

## Database Structure

**Primary database:** `database/insolvency_knowledge.db`

**Key tables:**
- `duty_relationships` - Actor → Procedure → Deadline → Consequence (with direct BIA quotes in `relationship_text`)
- `document_requirements` - Procedure → Required Documents
- `bia_sections` - Full BIA text with section_number, section_title, full_text
- `actors`, `procedures`, `deadlines`, `consequences`, `documents` - Extracted entities

**Key views (use these):**
- `v_complete_duties` - Joins duties with entity names (actor, procedure, deadline, consequence)
- `v_document_requirements` - Document requirements with context
- `v_relationship_stats` - Coverage statistics

**Coverage:**
- BIA: 1,047 relationships from 308/385 sections (80%)
- Study Materials: 1,123 relationships from 479 section contexts
- Total: 2,170 relationships

---

## Query Strategy (Standard Approach)

**For every question:**

1. **Identify key terms** (discharge, trustee, proposal, stay, etc.)

2. **Query relationships first:**
```sql
SELECT relationship_text, bia_section, source_name
FROM v_complete_duties
WHERE relationship_text LIKE '%keyword%'
  OR bia_section = 'X.X';
```

3. **Extract direct quote** from `relationship_text`

4. **Check for cross-references** in the quote:
   - If mentions "section N" → query Section N
   - If mentions "subsection (X)" → query that subsection
   - If mentions "paragraph (a)" → query that paragraph

5. **Include all referenced sections** in answer

6. **Always show the SQL** used for transparency

---

## Specific Rules for This Project

### When Asked About BIA Sections

**Query pattern:**
```sql
-- 1. Get section overview
SELECT section_number, section_title, part_number,
       substr(full_text, 1, 500)
FROM bia_sections
WHERE section_number = 'X.X';

-- 2. Get relationships
SELECT actor, procedure, deadline, consequence,
       relationship_text, modal_verb
FROM v_complete_duties
WHERE bia_section LIKE 'X.X%';

-- 3. Get documents
SELECT procedure, document, is_mandatory, filing_context
FROM v_document_requirements
WHERE bia_section LIKE 'X.X%';
```

### When Asked About Actor Duties

**Query pattern:**
```sql
SELECT actor, procedure, deadline, consequence,
       modal_verb, relationship_text, bia_section
FROM v_complete_duties
WHERE actor = '[Actor Name]'
  AND procedure IS NOT NULL
ORDER BY
  CASE modal_verb
    WHEN 'shall' THEN 1
    WHEN 'must' THEN 2
    WHEN 'may' THEN 3
    ELSE 4
  END;
```

### When Asked About Documents

**Query pattern:**
```sql
SELECT procedure, document, is_mandatory, filing_context, bia_section
FROM v_document_requirements
WHERE procedure LIKE '%keyword%'
   OR document LIKE '%keyword%';
```

---

## Response Style for This Project

**Be precise and exam-focused:**
- Use legal terminology correctly (insolvent person, deemed assignment, stay of proceedings)
- Distinguish between "shall" (mandatory), "may" (discretionary), "shall not" (prohibited)
- Cite specific BIA sections and subsections
- Include modal verbs in answers (SHALL vs MAY matters for exams!)

**Provide context:**
- If answer involves deadlines, explain what triggers them
- If answer involves consequences, explain what causes them
- If answer involves procedures, explain who performs them

**Always verify:**
- Check both BIA relationships AND section text
- If relationship seems incomplete, query source section
- If answer seems uncertain, query multiple related sections

---

## Tools Available

**Extraction:**
- `src/extraction/relationship_extractor.py` - BIA relationships
- `src/extraction/study_material_relationship_extractor.py` - Study materials

**Visualization:**
- `tools/diagram/generate_mermaid.py` - Generate Mermaid diagrams

**Database:**
- SQLite at `database/insolvency_knowledge.db`
- Use `sqlite3` command-line tool for queries

---

## Custom Slash Commands Available

- `/bia [section]` - Query BIA section
- `/duties [actor]` - Find actor duties
- `/docs [keyword]` - Find documents
- `/exam [question]` - Answer exam question (enforces format above)
- `/search [keyword]` - Search all sources
- `/diagram [topic] [section] [type]` - Generate diagram
- `/coverage` - Show statistics
- `/quick-ref` - Quick reference

**These commands have the same formatting requirements as this CLAUDE.md file.**

---

## Example: Correct Answer Format

**Question:** "When is first-time bankrupt with surplus income discharged?"

**Correct format:**

## Question
When is first-time bankrupt with surplus income discharged?

## Answer
✅ On the expiration of twenty-one months following the date of bankruptcy

## Direct Quote (Primary Source)
"on the expiry of 21 months after the date of bankruptcy unless an opposition to the discharge has been filed before the automatic discharge takes effect"

**Section Reference:** Section 168.1(1)(a)(ii)
**Source:** BIA Statute

## Cross-References
**Referenced Section 68 (Surplus Income):**
"surplus income means the portion of a bankrupt individual's total income that exceeds that which is necessary to enable the bankrupt individual to maintain a reasonable standard of living"

**Context:** Section 168.1(1)(a) clause (ii) applies when "bankrupt has been required to make payments under section 68" - this is the surplus income provision.

## Explanation
First-time bankrupts WITH surplus income (section 68 payments) are automatically discharged at 21 months, versus 9 months for those without surplus income under clause (i).

## Traceability
- Primary section: Section 168.1(1)(a)(ii)
- Cross-references: Section 68 (surplus income definition)
- Database query:
```sql
SELECT relationship_text, bia_section
FROM v_complete_duties
WHERE bia_section = '168.1'
  AND relationship_text LIKE '%21 months%';
```

---

**This CLAUDE.md file loads automatically every session and controls my behavior for this project.**
