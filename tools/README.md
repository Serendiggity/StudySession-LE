# Knowledge Base Tools

Organized by purpose for intuitive navigation.

---

## `/query/` - Using the Knowledge Base

**Purpose:** Query and explore the knowledge base

- **`test_exam_questions.py`** - Validate database with actual exam questions
- **`cross_reference_navigator.py`** - Follow citations across sources (Study Material ↔ BIA ↔ Directives)
- **`quick_query_examples.py`** - Demonstrates optimized query patterns

**Usage:**
```bash
# Test with exam questions
python tools/query/test_exam_questions.py

# Demo cross-reference navigation
python tools/query/cross_reference_navigator.py
```

---

## `/validation/` - Quality Assurance

**Purpose:** Track accuracy and build exam intelligence

- **`quiz_validation_system.py`** - Store quizzes, validate system answers, track errors
- **`track_exam_question.py`** - Build exam pattern data from completed quizzes

**Usage:**
```bash
# Validate a quiz
python tools/validation/quiz_validation_system.py validate --dataset "Module Quiz"

# View accuracy stats
python tools/validation/quiz_validation_system.py status

# Analyze error patterns
python tools/validation/quiz_validation_system.py analyze
```

---

## `/ingestion/` - Adding New Sources

**Purpose:** Load new source materials into the knowledge base

- **`load_bia_structure.py`** - Load BIA statutory sections
- **`load_directives.py`** - Load OSB Directives
- **`migrate_to_multisource.py`** - Schema migrations

**Usage:**
```bash
# Load new OSB Directive
python tools/ingestion/load_directives.py --directive "Directive 11R2" --file sources/osb_directives/...
```

---

## `/maintenance/` - Database Optimization

**Purpose:** Keep database performant

- **`optimize_database.py`** - Create FTS5 indexes, analyze tables, create views

**Usage:**
```bash
# Optimize after adding new sources
python tools/maintenance/optimize_database.py
```

---

## Path Configuration

**All tools expect:**
- Database: `database/insolvency_knowledge.db`
- Sources: `sources/`

**If you move the database**, update the path in each script or set environment variable:
```bash
export INSOLVENCY_DB="/path/to/database/insolvency_knowledge.db"
```
