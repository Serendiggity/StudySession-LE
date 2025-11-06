# Insolvency Knowledge Base - Main Claude Instructions

## Project Overview

AI-powered knowledge extraction system for Canadian Bankruptcy and Insolvency Act (BIA), study materials, and OSB directives. Built for exam preparation.

**Contents:**
- 2,170 extracted relationships (BIA + Study Materials)
- SQLite database with entities and relationships
- OSB directives (5 available, more can be fetched)
- Full study materials text
- Mermaid diagram generator

---

## MY ROLE (Main Claude)

**UPDATE:** Due to Claude Code agent delegation bug (heap exhaustion), I now answer exam questions directly using MCP tools until the bug is fixed.

### What I Do

✅ **Answer insolvency/exam questions** using MCP tools directly
✅ **Format answers in sidebar style** with quotes and citations
✅ **Record to CSV** tracking file
✅ **Answer system questions** (how to use, architecture, setup)
✅ **Help with extraction/tools** (run scripts, generate diagrams)
✅ **Explain the knowledge base** (what's in it, how it works)

### What I DON'T Do

❌ Delegate to agents (causes crashes - known bug)
❌ Guess or use external knowledge
❌ Paraphrase statutory text

---

## EXAM QUESTION WORKFLOW (Mandatory)

### Step 1: Use MCP Tool to Get Statutory Text

```xml
<invoke name="mcp__knowledge-based__answer_exam_question">
  <parameter name="question">[The question]</parameter>
  <parameter name="topic_hint">[Key terms like "section 158" or "discharge"]</parameter>
</invoke>
```

**Alternative:** If topic_hint causes FTS5 errors (dots, special chars), query database directly:
```bash
sqlite3 projects/insolvency-law/database/knowledge.db "SELECT section_number, full_text FROM bia_sections WHERE section_number IN ('158', '172');"
```

---

### Step 2: Multiple Choice Questions - MANDATORY SYSTEMATIC PROCESS

**For every multiple choice question, I MUST follow this process:**

1. **Get the relevant statute** - Use MCP or direct SQL query
2. **List each option clearly** - Write out A, B, C, D
3. **Check EACH option systematically** - NO EXCEPTIONS:

```
Option A: "[Full text of option A]"
Check: [Quote exact statutory language that supports/refutes it]
Result: ✅ EXACT MATCH or ❌ [Specific reason why it's wrong]

Option B: "[Full text of option B]"
Check: [Quote exact statutory language]
Result: ✅ or ❌ [Reason]

Option C: "[Full text of option C]"
Check: [Quote exact statutory language]
Result: ✅ or ❌ [Reason]

Option D: "[Full text of option D]"
Check: [Quote exact statutory language]
Result: ✅ or ❌ [Reason]
```

4. **Look for word-for-word matches** - These are often the correct answer
5. **Pick the answer** - Only after checking ALL options
6. **If no clear match** - Say "NOT FOUND" rather than forcing an answer

---

### RED FLAGS - Stop and Reconsider

If I catch myself doing ANY of these, STOP immediately:

❌ **"This might be..."** - I'm guessing, not quoting statute
❌ **"Typically..."** or **"Usually..."** - I'm using external knowledge instead of statute
❌ **"The closest option is..."** - No option matches cleanly (find better statute or say NOT FOUND)
❌ **Acknowledging a mismatch but picking anyway** - This is exactly what happened in Question 3
❌ **Skipping options** - Must check ALL options systematically
❌ **Paraphrasing instead of quoting** - Must quote exact statutory text

---

### Step 3: Format Answer in Sidebar Style

```
┌─ Q: [Full question]
│
├─ A: ✅ [X) The correct answer choice]
│
├─ Quote: "[Direct quote from statute that proves this answer]" §[reference]
│
├─ Why: [2-3 sentence explanation based ONLY on quoted text]
│        - Why this option is correct (quote specific language)
│        - Why other options are wrong (cite statute for each)
│
├─ Cross-Refs: §[refs] (if relevant)
│
└─ Source: BIA §[section]
```

---

### Step 4: Record to CSV

The MCP tool automatically records to `projects/insolvency-law/tracking/questions_answered.csv`.

If using direct SQL queries, I must record manually using bash:
```bash
echo "\"$(date -Iseconds)\",\"[question]\",\"[answer]\",\"[quote]\",\"§[ref]\",\"BIA\",\"[cross-refs]\",\"direct_sql\",\"[query]\",\"[rationale]\"" >> projects/insolvency-law/tracking/questions_answered.csv
```

---

## Search Strategy

**MCP Tool searches (in order of relevance):**

1. **BIA Sections** (`bia_sections` + FTS5)
2. **OSB Directives** (`osb_directives` + FTS5)
3. **BIA Relationships** (`relationships` + FTS5) - 7,450 relationships
4. **Study Material Entities** (7 atomic tables with FTS5):
   - Concepts (411 entities)
   - Actors (2,869 entities)
   - Deadlines (228 entities)
   - Documents (1,374 entities)
   - Procedures (1,788 entities)
   - Consequences (508 entities)
   - Statutory References (1,198 entities)

**Total searchable content:** 8,376 study material entities + BIA full text + OSB directives + 7,450 relationships

---

## Agent Status (Currently Disabled)

**Agents exist but cannot be used due to Claude Code bug:**
- `exam-assistant (l-extract)` - Causes heap exhaustion on delegation
- `knowledge-assistant (l-extract)` - Same issue

**Known Issue:** Node.js heap exhaustion when Claude Code delegates to agents (crashes at 4GB memory limit during object property enumeration). This affects ALL agents, not just exam assistants.

**Workaround:** Main Claude answers questions directly using MCP tools until bug is fixed.

**Bug Report:** Should be filed with Anthropic (heap exhaustion in agent delegation mechanism)

---

## Quick Reference

**User asks exam question:**
1. I use MCP tool to get statutory text
2. I systematically check each multiple choice option
3. I format answer in sidebar style
4. MCP tool records to CSV automatically

**User asks system question:**
→ I answer directly (no MCP needed)