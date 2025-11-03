# Session 3: Complete Relationships + Simple Mermaid Generator

**Scope:** Focused on exam prep - build data foundation + simple diagram generation
**Time:** 5-6 hours
**Workflow:** Generate .md files → Open in VS Code → Mermaid preview renders

---

## Part 1: Complete Relationship Extraction (3-4 hours)

### Database Schema
Add 3 relationship tables:
```sql
- duty_relationships (actor → procedure → deadline → consequence)
- document_requirements (procedure → document)
- trigger_relationships (condition → consequence)
```

### Comprehensive Extraction
**Process ALL insolvency content:**
- 385 BIA sections
- 18 study material chapters
- 5 OSB directives

**AI-powered from existing entities:**
- NOT re-extraction from text
- Analyze existing actors/procedures/deadlines/consequences
- Connect them into relationships
- Cost: ~$3-5, Time: ~30 minutes API processing

**Expected:** 350-450 relationships total

---

## Part 2: Simple Mermaid File Generator (2-3 hours)

### Tool: `tools/diagram/generate_mermaid.py`

**Usage:**
```bash
python tools/diagram/generate_mermaid.py \
  --topic "Division I NOI" \
  --type flowchart \
  --output data/output/diagrams/division_i_noi.md
```

**Outputs:** .md file with Mermaid code

**Your Workflow:**
1. Run script → generates .md file
2. Open in VS Code → Mermaid preview shows diagram
3. Study the visualization

**Diagram Types Supported:**
- Process flowchart (step-by-step)
- Actor swimlane (who does what)
- Duty chain (obligations with consequences)
- Entity relationship (schema view)
- Timeline Gantt (already have this)

---

## Deliverables

### Enhanced Database
- ✅ Relationship tables with 350-450 relationships
- ✅ Enhanced query capabilities
- ✅ Covers entire insolvency domain

### Diagram Generator
- ✅ Simple Python script
- ✅ Generates Mermaid .md files
- ✅ Works for any topic
- ✅ 5 diagram templates

### NO UI Development
- No Streamlit
- No web application
- No complex infrastructure
- Pure focus on data + simple tool

---

## Success Criteria

**Relationship Extraction:**
- ✅ Can query: "What are trustee duties with deadlines?"
- ✅ Can query: "What triggers deemed assignment?"
- ✅ Can query: "What documents required for proposals?"

**Diagram Generation:**
- ✅ Generate diagram for Division I NOI
- ✅ Generate diagram for discharge process
- ✅ Generate diagram for trustee duties
- ✅ Open in VS Code, preview renders correctly

**Time Investment:**
- ✅ Completed in 5-6 hours
- ✅ Doesn't interfere with exam studying

---

## Future State (Post-Exam)

**The relationships built in Session 3 will power:**
- Interactive Streamlit UI
- Dynamic diagram generation
- In-browser rendering
- Advanced study tools

**But for now:** Keep it simple, stay focused on exam.

---

**Session 3: Build the foundation (relationships) + simple tool (Mermaid files for VS Code preview)**

Ready to execute when you start Session 3!
