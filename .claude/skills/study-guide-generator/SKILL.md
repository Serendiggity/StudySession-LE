---
name: study-guide-generator
description: Generate comprehensive visual study guides with professional swimlane diagrams for knowledge base topics. Use when user says "help me visualize [topic]" or "create visual study guide for [topic]". Creates swimlanes showing all actors, timelines, flowcharts, and comprehensive explanations.
---

# Study Guide Generator (Universal)

Generate comprehensive, visually-rich study guides for ANY topic in the knowledge base using hybrid search, coverage analysis, and professional PlantUML swimlanes.

**Works for:** Insolvency law, medical guidelines, engineering standards, or any domain with structured knowledge.

## When to Use This Skill

**Primary trigger:** "Help me visualize [topic]"

**Other triggers:**
- "Create visual study guide for [topic]"
- "Visualize [topic] with swimlane"
- "Show me [topic] with diagrams"
- "I need visuals for [topic]"

**Topics can be:**
- BIA chapters (e.g., "Division I proposals", "Consumer proposals")
- Specific sections (e.g., "Section 50.4 NOI process")
- Concepts (e.g., "Discharge requirements", "Trustee duties")
- Processes (e.g., "Meeting of creditors", "Certificate of full performance")

## Workflow

### Step 1: Use Hybrid Search (30% Better Retrieval)

Query the database using hybrid search (FTS5 + vector embeddings):

```python
python3 << 'SCRIPT'
import sqlite3, json, numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
conn = sqlite3.connect('projects/insolvency-law/database/knowledge.db')

# Your search implementation here
# Returns: BIA sections + entities ranked by RRF
SCRIPT
```

**Searches:**
- BIA sections (FTS5 + vector)
- All 7 entity tables (concepts, procedures, deadlines, documents, actors, consequences, statutory_references)
- OSB directives
- Relationships

### Step 2: Analyze Coverage

Use the coverage analyzer to ensure completeness:

```bash
python3 src/analysis/coverage_analyzer.py \
  --topic "consumer proposals" \
  --content "[your generated guide content]" \
  --output coverage_report.json
```

**Checks:**
- All entity types covered?
- All cross-references found?
- All deadlines included?
- Gaps identified?

If coverage < 80%, query for missing entities and regenerate.

### Step 3: Generate Visual Diagrams

**Timeline (Gantt chart):**
```bash
python3 src/visualization/diagram_generator.py \
  projects/insolvency-law/database/knowledge.db \
  "consumer proposal" timeline
```

**Process flowchart:**
```bash
python3 src/visualization/diagram_generator.py \
  projects/insolvency-law/database/knowledge.db \
  "consumer proposal" process
```

**Comprehensive swimlane (MANUAL CREATION - Best Quality):**

**DO NOT use the auto-generator** - it produces poor results. Instead:

1. **Query database for comprehensive data:**
```python
# Get all actors
SELECT DISTINCT role_canonical FROM actors
WHERE extraction_text LIKE '%[topic]%'

# Get all procedures with timing
SELECT p.extraction_text, p.section_number, d.timeframe, a.role_canonical
FROM procedures p
LEFT JOIN deadlines d ON d.section_number = p.section_number
LEFT JOIN actors a ON a.extraction_text LIKE '%' || p.extraction_text || '%'
WHERE p.extraction_text LIKE '%[topic]%'
ORDER BY p.section_number

# Get all forms/documents
SELECT extraction_text, section_number FROM documents
WHERE extraction_text LIKE '%[topic]%'

# Get all directives
SELECT directive_number, directive_name FROM osb_directives
WHERE full_text LIKE '%[topic]%'
```

2. **Manually create PlantUML swimlane with rich annotations:**

**CRITICAL: Include helpful context for learning:**
- ✅ Full form names (not just "Form 47" - say "Form 47: Consumer Proposal")
- ✅ Directive names (not just "Dir 6R7" - say "Directive 6R7: Assessment of Individual Debtor")
- ✅ Section purposes (not just "§66.15" - add "Call meeting if ≥25%")
- ✅ Timing context (not just "Day 45" - say "Day 45 (from filing)")
- ✅ Notes explaining WHY (e.g., "Stay protects debtor from lawsuits")
- ✅ Key thresholds (e.g., "≥25% of proven claims")
- ✅ Consequences (e.g., "No certificate if counselling skipped")

**Example PlantUML template:**
```plantuml
@startuml
title [Topic] Process - Complete Swimlane

skinparam backgroundColor white
skinparam swimlaneWidth 200

|👤 [Actor 1 Name]|
start
:[Action 1]
[Timing];
note right: [BIA Section]\n[Form Name: Full Description]\n[Why this matters]

:[Action 2];
note right: [Directive Name: Purpose]\n[Threshold: X%]\n[Consequence if missed]

|💼 [Actor 2 Name]|
:[Their action];
note right: [Full context]

if ([Decision point?]) then (yes)
  :[Action if yes];
  note right: [Section]\n[Helpful explanation]
else (no)
  :[Action if no];
  note right: [What this means]
endif

stop
@enduml
```

**Rich annotation example:**
```plantuml
|💼 Administrator|
:Send notice package
**Within 10 days**;
note right: BIA §66.14(b)\n**Forms included:**\n- Form 31: Proof of Claim\n- Form 37.1: Voting Letter\n- Form 49: Explanatory Notice\n**Purpose:** Inform all creditors\n**Consequence:** Proposal may fail
```

3. **Convert to SVG via Kroki:**
```python
import requests

with open('swimlane.plantuml', 'r') as f:
    plantuml_code = f.read()

response = requests.post(
    'https://kroki.io/plantuml/svg',
    data=plantuml_code.encode('utf-8'),
    headers={'Content-Type': 'text/plain'},
    verify=False,  # macOS SSL workaround
    timeout=60
)

with open('swimlane.svg', 'wb') as f:
    f.write(response.content)
```

4. **Embed in study guide:**
```markdown
### Complete Swimlane Diagram

![Topic Swimlane](../../path/to/swimlane.svg)

**Diagram shows:**
- All [N] actors involved
- Chronological flow with all decision points
- Cross-lane interactions
- All forms with full names
- All directives with purposes
- Timing annotations throughout
```

### Step 4: Structure with JSON Schema

Ensure completeness by following this structure:

```json
{
  "topic": "string",
  "overview": {
    "definition": "string",
    "purpose": "string",
    "key_features": ["array"]
  },
  "eligibility": {
    "requirements": ["array"],
    "exclusions": ["array"],
    "bia_sections": ["array"]
  },
  "process": [
    {
      "stage_name": "string",
      "actor": "string",
      "actions": ["array"],
      "deadlines": ["array"],
      "forms": ["array"],
      "bia_sections": ["array"]
    }
  ],
  "timelines": {
    "gantt_chart": "mermaid_code",
    "swimlane": "plantuml_code",
    "key_milestones": ["array"]
  },
  "references": {
    "bia_sections": ["array"],
    "directives": ["array"],
    "forms": ["array"]
  },
  "practice_questions": [
    {
      "question": "string",
      "options": ["A", "B", "C", "D"],
      "correct": "string",
      "explanation": "string",
      "bia_reference": "string"
    }
  ]
}
```

Reference schema: `mcp_server/schemas/study_guide_schema.json`

### Step 5: Fetch Missing Directives

If directives are referenced but not in database, fetch them:

```bash
# Check which directives are in DB
sqlite3 projects/insolvency-law/database/knowledge.db \
  "SELECT directive_number FROM osb_directives"

# Fetch missing ones
# Use WebFetch (not FireCrawl - out of credits)
```

Common directives:
- Directive 1R8: Counselling
- Directive 2R: Joint Filing
- Directive 6R7: Assessment
- Directive 22R4: Voting/Quorum

### Step 6: Create Final Study Guide

**Required sections:**
1. **Overview** - What is it, why it matters
2. **Eligibility** - Who can use it, requirements
3. **Complete Process Timeline** - Gantt chart showing all stages
4. **Swimlane Diagram** - All actors and their responsibilities
5. **Key Deadlines** - Table + timeline
6. **Step-by-Step Process** - Detailed walkthrough
7. **Decision Points** - Flowchart showing branches
8. **Forms & Directives** - What each one is for
9. **Division Comparison** (if applicable) - Division I vs II
10. **Common Exam Traps** - Mistakes to avoid
11. **Practice Questions** - At least 5 questions with explanations
12. **Quick Reference** - Tables, cheat sheets

**Format:**
- Markdown with Mermaid diagrams
- Embedded SVG swimlanes
- Tables for comparisons
- Layman explanations for each concept
- BIA section citations throughout

**Save to:** `docs/guides/[TOPIC]_STUDY_GUIDE.md`

## Quality Checks

Before delivering, verify:

✅ All BIA sections mentioned in study materials are covered
✅ All deadlines from database are in timeline
✅ All forms are identified and explained
✅ All directives are fetched and summarized
✅ Coverage score ≥ 80% (use coverage analyzer)
✅ At least 3 visual diagrams included
✅ Practice questions test different concepts
✅ No hallucinations (all info from database/BIA)

## Tools Available

**Database queries:**
- Hybrid search (best results)
- Pure FTS5 (fast)
- Direct SQL (specific queries)

**Analysis:**
- `src/analysis/coverage_analyzer.py` - Gap detection
- Coverage thresholds, missing entity identification

**Visualization:**
- `src/visualization/diagram_generator.py` - Auto-generate Mermaid
- `tools/diagram/swimlane_generator.py` - PlantUML swimlanes via Kroki
- Manual Mermaid creation for custom needs

**MCP Tools (if available):**
- `mcp__knowledge-based__answer_exam_question` - Query with quotes
- `analyze_study_guide_coverage` - Validate completeness
- `generate_timeline_diagram` - Auto timelines
- `generate_process_diagram` - Auto flowcharts

## Example: Generate Consumer Proposal Study Guide

```bash
# 1. Hybrid search for all content
python3 << 'SCRIPT'
# Search all tables for "consumer proposal"
# Get BIA sections 66.11-66.4
# Get all entities (concepts, procedures, deadlines, etc.)
SCRIPT

# 2. Fetch directives
# WebFetch for Directive 1R8, 2R, 6R7, 22R4

# 3. Generate diagrams
python3 src/visualization/diagram_generator.py \
  projects/insolvency-law/database/knowledge.db \
  "consumer proposal" timeline

python3 tools/diagram/swimlane_generator.py \
  --topic "Consumer Proposal" --section "66%"

# 4. Analyze coverage
python3 src/analysis/coverage_analyzer.py \
  --topic "consumer proposals" \
  --content "$(cat draft_guide.md)"

# 5. Compile into markdown
# Include all diagrams
# Add practice questions
# Format with tables and examples

# 6. Save
# docs/guides/CONSUMER_PROPOSAL_STUDY_GUIDE.md
```

## Common Patterns

**For visual learners:**
- Lead with diagrams (swimlane, timeline)
- Use tables for comparisons
- Color-code decision points
- Include real-world examples

**For exam prep:**
- Add "Common Exam Traps" section
- Generate 10+ practice questions
- Highlight word-for-word statutory matches
- Include quick reference tables

**For comprehensive coverage:**
- Use hybrid search (not just FTS5)
- Check all 7 entity tables
- Run coverage analyzer
- Fill identified gaps

## Troubleshooting

**Low coverage score (<80%):**
- Check which entity types are missing
- Query those tables specifically
- Verify all cross-references retrieved

**Diagrams not generating:**
- Check database path is correct
- Verify sqlite-vec installed
- Check Kroki.io API accessibility (or use fallback)

**Missing directives:**
- Check `osb_directives` table first
- Use WebFetch if not in database
- Save to database for future use

## Success Criteria

A complete study guide has:
- ✅ 3+ visual diagrams (timeline, process, swimlane)
- ✅ All referenced BIA sections explained
- ✅ All deadlines in timeline
- ✅ All forms identified
- ✅ Layman's explanations
- ✅ Coverage score ≥ 80%
- ✅ 5+ practice questions
- ✅ Exam traps section
- ✅ Quick reference tables

**Goal:** User can master the topic from this one guide alone.
