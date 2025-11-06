# Insolvency Knowledge Base - Complete System Guide

## What Is This System?

An AI-powered knowledge extraction and relationship mapping system for the Canadian Bankruptcy and Insolvency Act (BIA) and related materials.

**Built over 3 sessions:**
- **Session 1:** PDF extraction + section mapping
- **Session 2:** Entity extraction (actors, procedures, deadlines, documents, etc.)
- **Session 3:** Relationship extraction + diagram generation

---

## Quick Start - Using the Knowledge Base

### Query BIA Relationships

```bash
# Open SQLite database
sqlite3 projects/insolvency-law/database/knowledge.db

# What must trustee do?
SELECT actor, procedure, deadline, bia_section
FROM v_complete_duties
WHERE actor = 'Trustee' AND procedure IS NOT NULL;

# What documents required for proposals?
SELECT procedure, document, is_mandatory
FROM v_document_requirements
WHERE procedure LIKE '%proposal%';

# All duties in Section 50.4 (NOI)
SELECT * FROM v_complete_duties WHERE bia_section LIKE '50.4%';
```

### Generate Diagrams

```bash
# Division I NOI flowchart
python tools/diagram/generate_mermaid.py \
  --topic "Division I NOI" \
  --section "50.4%" \
  --type flowchart

# Open the .md file in VS Code, use Mermaid preview extension
```

---

## System Architecture

### Database (`projects/insolvency-law/database/knowledge.db`)

**Source Documents (3):**
- Insolvency Administration Course Material (291 pages)
- BIA Statute (385 sections)
- OSB Directives (5 directives)

**Entities Extracted:**
```
Actors: 5,857        (trustees, creditors, bankrupts, etc.)
Procedures: 3,106    (file proposal, attend meeting, etc.)
Deadlines: 555       (within 10 days, 30 days, etc.)
Consequences: 508    (deemed assignment, discharge refused, etc.)
Documents: 2,144     (Form 31, cash flow statement, etc.)
Concepts: 411        (insolvency, proposal, stay, etc.)
Statutory Refs: 1,198 (BIA s. 50.4, CCAA, ITA references)
```

**Relationships Extracted (Session 3):**
```
BIA:
- 847 duty relationships (actor → procedure → deadline → consequence)
- 200 document requirements (procedure → document)
- 308 sections covered (80% of BIA)

Study Materials:
- [Will be extracted - see commands below]
```

---

## File Structure

```
insolvency-knowledge/
├── database/
│   └── insolvency_knowledge.db        # Main SQLite database
│
├── data/
│   ├── input/
│   │   └── study_materials/
│   │       ├── InsolvencyStudyGuide.pdf
│   │       ├── insolvency_admin_extracted.txt   # Extracted text
│   │       ├── bia_statute.txt
│   │       └── bia_statute_english_only.txt
│   │
│   └── output/
│       ├── diagrams/                  # Mermaid diagram .md files
│       │   ├── division_i_noi_process_flowchart.md
│       │   ├── consumer_proposals_swimlane.md
│       │   └── ...
│       └── timelines/
│           └── division_i_noi.md      # Timeline diagrams
│
├── src/
│   ├── database/
│   │   ├── relationship_schema.sql              # Current schema (v1)
│   │   ├── relationship_schema_v2_comprehensive.sql  # Future design
│   │   └── relationship_schema_v3_unified.sql        # Future design
│   │
│   ├── extraction/
│   │   ├── relationship_extractor.py           # BIA relationship extraction
│   │   └── study_material_relationship_extractor.py  # Study material extraction
│   │
│   ├── normalization/
│   │   └── canonical_actor_mapper.py    # AI-powered actor name normalization
│   │
│   └── visualization/
│       └── timeline_generator.py        # Generate timeline diagrams
│
├── tools/
│   └── diagram/
│       └── generate_mermaid.py          # Generate Mermaid diagrams
│
└── docs/
    ├── legal_statement_taxonomy.md      # Design: BIA relationship types
    ├── study_material_relationship_types.md  # Design: Study material types
    ├── unified_relationship_architecture.md  # Design: v3 unified
    └── single_unified_schema_design.md       # Design: v4 graph model
```

---

## Commands Reference

### 1. Extract Relationships

**BIA Sections:**
```bash
# Extract from all BIA sections
python src/extraction/relationship_extractor.py --mode all

# Extract from priority sections only
python src/extraction/relationship_extractor.py --mode priority

# Specify database
python src/extraction/relationship_extractor.py --mode all --db projects/insolvency-law/database/knowledge.db
```

**Study Materials:**
```bash
# Extract from study materials
python src/extraction/study_material_relationship_extractor.py

# Specify files
python src/extraction/study_material_relationship_extractor.py \
  --db projects/insolvency-law/database/knowledge.db \
  --text data/input/study_materials/insolvency_admin_extracted.txt
```

---

### 2. Query the Database

**Open database:**
```bash
sqlite3 projects/insolvency-law/database/knowledge.db
```

**Useful queries:**

```sql
-- Coverage statistics
SELECT * FROM v_relationship_stats;

-- Find all trustee duties with deadlines
SELECT actor, procedure, deadline, consequence, bia_section
FROM v_complete_duties
WHERE actor = 'Trustee' AND deadline IS NOT NULL
ORDER BY bia_section;

-- What triggers deemed assignment?
SELECT trigger_condition, consequence, bia_section
FROM v_trigger_consequences
WHERE consequence LIKE '%deemed assignment%';

-- Documents required for specific procedure
SELECT procedure, document, is_mandatory, filing_context
FROM v_document_requirements
WHERE procedure LIKE '%filing%proposal%';

-- Count duties by actor
SELECT actor, COUNT(*) as duty_count
FROM v_complete_duties
WHERE actor IS NOT NULL
GROUP BY actor
ORDER BY duty_count DESC;

-- Section 50.4 complete analysis
SELECT actor, procedure, deadline, consequence, modal_verb
FROM v_complete_duties
WHERE bia_section LIKE '50.4%';
```

---

### 3. Generate Diagrams

**Flowchart (process flow):**
```bash
python tools/diagram/generate_mermaid.py \
  --topic "Division I NOI Process" \
  --section "50.4%" \
  --type flowchart
```

**Swimlane (multi-actor processes):**
```bash
python tools/diagram/generate_mermaid.py \
  --topic "Consumer Proposals" \
  --section "66%" \
  --type swimlane
```

**Duty Chain (obligations with consequences):**
```bash
python tools/diagram/generate_mermaid.py \
  --topic "Trustee Duties" \
  --section "13%" \
  --type duty-chain
```

**ERD (database schema):**
```bash
python tools/diagram/generate_mermaid.py \
  --type erd
```

**Timeline (Gantt chart):**
```bash
python tools/diagram/generate_mermaid.py \
  --topic "Division I Timeline" \
  --section "50%" \
  --type timeline
```

**View diagrams:** Open the generated `.md` files in VS Code with Mermaid Preview extension

---

## Database Schema (Current - v1)

### Entity Tables
- `actors` - Legal roles (trustees, creditors, bankrupts)
- `procedures` - Actions and processes
- `deadlines` - Time constraints
- `consequences` - Outcomes if conditions not met
- `documents` - Forms and filings
- `concepts` - Key terminology
- `statutory_references` - BIA/CCAA/ITA section references

### Relationship Tables
- `duty_relationships` - Actor → Procedure → Deadline → Consequence
- `document_requirements` - Procedure → Required Documents
- `trigger_relationships` - Condition → Consequence

### Useful Views
- `v_complete_duties` - Full duty chains with all entity names
- `v_document_requirements` - Document requirements with context
- `v_trigger_consequences` - Trigger conditions and results
- `v_relationship_stats` - Coverage statistics

---

## How the System Works

### Step 1: PDF → Text Extraction
- PDFs converted to text with position tracking
- Section headers identified and mapped
- Result: Full text with char_start/char_end positions

### Step 2: Entity Extraction (Lang Extract + AI)
- AI reads text and identifies entities (actors, procedures, deadlines, etc.)
- Entities stored with char positions for proximity matching
- Actor/document names normalized (e.g., "trustee" = "Trustee" = "licensed trustee")

### Step 3: Relationship Extraction (AI)
- For each section:
  1. Get section text
  2. Get all entities in that section (by char position proximity)
  3. AI identifies how entities connect into relationships
  4. Store as structured data with foreign keys

### Step 4: Query & Visualize
- Fast SQL queries on indexed relationships
- Generate Mermaid diagrams for visualization
- 50-100x faster than text search

---

## Current Capabilities

### What You Can Ask

✅ "What are trustee duties with deadlines?"
✅ "What documents required for filing proposal?"
✅ "What happens if bankrupt doesn't attend examination?"
✅ "Show me all Section 50.4 requirements"
✅ "When is first-time bankrupt with surplus income discharged?"
✅ "What are creditor rights during stay of proceedings?"

### What You Can Generate

✅ Process flowcharts for any BIA section
✅ Actor swimlane diagrams
✅ Duty chain visualizations
✅ Timeline Gantt charts
✅ Entity-relationship diagrams

---

## Performance

**Query Speed:**
- Text search: ~500-1000ms (full scan)
- Relationship query: ~5-20ms (indexed lookup)
- **50-100x faster**

**Extraction Costs:**
- BIA (385 sections): ~$0.15-0.20 (Gemini 2.0 Flash)
- Study Materials (479 sections): ~$0.20-0.25 estimated
- One-time cost, infinite queries afterward

---

## Future Extensions (Post-Exam)

### Planned Enhancements (Design Complete)
- v2 Comprehensive schema (9 relationship types)
- v3 Unified multi-source schema (BIA + Study + Directives)
- v4 Graph database model (universal predicates)

### Potential Features
- Streamlit web interface
- Interactive diagram generation
- Practice exam generator
- AI-powered Q&A interface
- Cross-reference navigator

---

## Troubleshooting

**If extraction fails:**
- Check GEMINI_API_KEY in .env file
- Check rate limits (10 RPM on experimental models)
- Use stable model: `gemini-2.0-flash` not `gemini-2.0-flash-exp`

**If queries are slow:**
- Ensure indexes exist (run relationship_schema.sql)
- Use views (v_complete_duties) instead of manual joins
- Check with: `EXPLAIN QUERY PLAN SELECT ...`

**If diagrams don't render:**
- Install Mermaid Preview extension in VS Code
- Check .md file syntax with online Mermaid editor
- Ensure section pattern matches data (use wildcard: "50%")

---

## Quick Reference Card

**Most Common Commands:**

```bash
# 1. Extract BIA relationships
python src/extraction/relationship_extractor.py --mode all

# 2. Extract study material relationships
python src/extraction/study_material_relationship_extractor.py

# 3. Query database
sqlite3 projects/insolvency-law/database/knowledge.db
> SELECT * FROM v_complete_duties WHERE actor = 'Trustee';

# 4. Generate diagram
python tools/diagram/generate_mermaid.py \
  --topic "Your Topic" --section "50%" --type flowchart

# 5. Check coverage
sqlite3 projects/insolvency-law/database/knowledge.db \
  "SELECT * FROM v_relationship_stats;"
```

---

## Support

**Documentation:**
- This file (system overview)
- `data/output/diagrams/README.md` (diagram usage)
- Design docs in `docs/` (for understanding architecture)

**Key Files to Remember:**
- Database: `projects/insolvency-law/database/knowledge.db`
- BIA extractor: `src/extraction/relationship_extractor.py`
- Study extractor: `src/extraction/study_material_relationship_extractor.py`
- Diagram tool: `tools/diagram/generate_mermaid.py`

**For exam prep, you mainly need:**
1. SQL queries to `projects/insolvency-law/database/knowledge.db`
2. Diagram generation for visualization
3. That's it!

---

**Last Updated:** Session 3 (Nov 3, 2025)
**Status:** BIA extraction complete (847 relationships), Study materials pending
