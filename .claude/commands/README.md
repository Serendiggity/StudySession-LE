# Slash Commands - Insolvency Knowledge Base

## Available Commands (Tool Execution Only)

**Why so few?** The `.claude/CLAUDE.md` file handles all query behavior automatically. These commands are only for running tools.

### `/diagram [topic] [section-pattern] [type]`
Generate Mermaid diagram

**Example:**
```
/diagram "Division I NOI" "50.4%" flowchart
```

**Types:** flowchart, swimlane, duty-chain, timeline, erd

---

### `/coverage`
Show extraction coverage statistics

**Shows:**
- Relationships by source (BIA vs Study Materials)
- BIA section coverage percentage
- Top 10 sections by relationship count

---

### `/extract-bia`
Run BIA relationship extraction (if needed to re-extract or catch missed sections)

**Time:** ~15-30 minutes
**Cost:** ~$0.15-0.20

---

### `/extract-study`
Run study material relationship extraction

**Time:** ~20-40 minutes
**Cost:** ~$0.20-0.25

---

## For All Other Queries

**Just ask normally!**

The `.claude/CLAUDE.md` file ensures I always:
- ✅ Provide direct BIA quotes
- ✅ Cite section references
- ✅ Follow cross-references
- ✅ Show SQL queries
- ✅ Use fixed format

**No slash command needed for:**
- Exam questions (CLAUDE.md handles formatting)
- BIA section lookups (CLAUDE.md handles queries)
- Actor duty queries (CLAUDE.md handles queries)
- Document searches (CLAUDE.md handles queries)

---

## Quick Start

**Ask any exam question:**
```
When is first-time bankrupt with surplus discharged?
```

**I will automatically:**
1. Query database
2. Show direct BIA quote
3. Follow cross-references (e.g., section 68)
4. Cite sections
5. Show SQL used
6. Format consistently

**Every time. No command needed.**
