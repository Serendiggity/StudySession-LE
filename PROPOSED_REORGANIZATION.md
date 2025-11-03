# Proposed Directory Reorganization

## Current Problems
- Root directory cluttered with logs, test files, and markdown docs
- Scripts directory has 17 unorganized files
- Multiple duplicate BIA statute files (3 versions)
- No clear separation between "source materials" and "processed data"
- Hard to find the actual knowledge base (buried in data/output/)

---

## Proposed Clean Structure

```
insolvency-knowledge/
│
├── database/                          # THE KNOWLEDGE BASE (main product)
│   ├── insolvency_knowledge.db        # Main database
│   └── README.md                      # How to query the database
│
├── sources/                           # Original source materials
│   ├── study_material/
│   │   ├── InsolvencyStudyGuide.pdf
│   │   └── extracted_text.txt
│   ├── bia_statute/
│   │   ├── Bankruptcy_and_Insolvency_Act.pdf
│   │   └── bia_clean_english.txt      # Final cleaned version
│   └── osb_directives/
│       ├── Directive_6R7_Assessment.md
│       ├── Directive_16R_Statement_of_Affairs.md
│       ├── Directive_17_Document_Retention.md
│       ├── Directive_32R_Electronic_Records.md
│       └── Directive_4R_Delegation.md
│
├── tools/                             # Organized by purpose
│   ├── query/                         # Using the knowledge base
│   │   ├── test_exam_questions.py
│   │   ├── cross_reference_navigator.py
│   │   └── quick_query_examples.py
│   ├── validation/                    # Quality assurance
│   │   ├── quiz_validation_system.py
│   │   └── track_exam_question.py
│   ├── ingestion/                     # Adding new sources
│   │   ├── load_bia_structure.py
│   │   ├── load_directives.py
│   │   └── migrate_to_multisource.py
│   └── maintenance/                   # Database maintenance
│       └── optimize_database.py
│
├── docs/                              # Documentation
│   ├── guides/
│   │   ├── AI_Query_Guide.md          # How to query efficiently
│   │   ├── Adding_OSB_Directives.md
│   │   └── Cross_Reference_Guide.md
│   ├── analysis/
│   │   ├── Exam_Pattern_Analysis.md
│   │   ├── Directive_Inventory.md
│   │   └── Session_2_Summary.md
│   └── README.md                      # Main documentation entry point
│
├── archive/                           # Old attempts, logs (for reference)
│   ├── extraction_logs/
│   │   ├── bia_extraction_*.log
│   │   └── README.md                  # What these represent
│   └── deprecated_scripts/
│       ├── extract_bia_*.py           # Old extraction attempts
│       └── README.md                  # Why these exist
│
├── src/                               # Core library code (Lang Extract integration)
│   ├── extraction/                    # Entity extraction
│   ├── database/                      # Database schemas and loaders
│   └── utils/                         # Parsers and utilities
│
├── .env                               # Environment variables
├── .gitignore
├── README.md                          # Project overview
└── requirements.txt
```

---

## Key Improvements

### 1. **Clear Entry Points**
- Want the knowledge base? → `/database/insolvency_knowledge.db`
- Want to query it? → `/tools/query/`
- Want documentation? → `/docs/`

### 2. **Source Organization**
- All original PDFs in `/sources/`
- Clean text versions alongside PDFs
- One authoritative version (not 3 BIA files)

### 3. **Tool Organization by Purpose**
- **Query** - Using the system
- **Validation** - Testing accuracy
- **Ingestion** - Adding new content
- **Maintenance** - Database upkeep

### 4. **Clean Root Directory**
- No test files
- No log files
- No scattered markdown docs
- Just project essentials

### 5. **Archive Instead of Delete**
- Preserve extraction attempts for learning
- Document what didn't work
- Don't lose historical context

---

## Migration Plan

### Phase 1: Create New Structure (5 minutes)
```bash
mkdir -p database sources/{study_material,bia_statute,osb_directives}
mkdir -p tools/{query,validation,ingestion,maintenance}
mkdir -p docs/{guides,analysis}
mkdir -p archive/{extraction_logs,deprecated_scripts}
```

### Phase 2: Move Files (10 minutes)

**Database:**
```bash
mv data/output/insolvency_knowledge.db database/
```

**Sources:**
```bash
mv Materials/"Bankruptcy and Insolvency Act.pdf" sources/bia_statute/
mv data/input/study_materials/bia_statute_clean_english.txt sources/bia_statute/
mv data/input/osb_directives/* sources/osb_directives/
```

**Tools:**
```bash
mv scripts/test_exam_questions.py tools/query/
mv scripts/cross_reference_navigator.py tools/query/
mv scripts/quick_query_examples.py tools/query/
mv scripts/quiz_validation_system.py tools/validation/
mv scripts/track_exam_question.py tools/validation/
mv scripts/load_bia_structure.py tools/ingestion/
mv scripts/optimize_database.py tools/maintenance/
```

**Docs:**
```bash
mv AI_QUERY_OPTIMIZATION_GUIDE.md docs/guides/
mv docs/EXAM_PATTERN_ANALYSIS.md docs/analysis/
mv docs/SESSION_2_SUMMARY.md docs/analysis/
mv docs/DIRECTIVE_INVENTORY.md docs/analysis/
```

**Archive:**
```bash
mv bia_*.log archive/extraction_logs/
mv scripts/extract_bia_*.py archive/deprecated_scripts/
mv scripts/filter_bia_*.py archive/deprecated_scripts/
```

### Phase 3: Update Paths in Code (15 minutes)
- Update database path references in scripts
- Update import statements
- Create path config file

### Phase 4: Create README Files (10 minutes)
- database/README.md - How to use the knowledge base
- tools/README.md - What each tool does
- archive/README.md - What's archived and why

---

## Total Time: ~40 minutes

## Benefits

**User Experience:**
- ✅ Immediately obvious what the project does (knowledge base in `/database/`)
- ✅ Clear how to use it (`/tools/query/`)
- ✅ Easy to find documentation (`/docs/`)

**Maintainability:**
- ✅ Add new directives → `/sources/osb_directives/`
- ✅ New query script → `/tools/query/`
- ✅ Organized by purpose, not chronology

**Professional:**
- ✅ Clean root directory
- ✅ Intuitive navigation
- ✅ Repository looks production-ready

---

**Want me to execute this reorganization?**
