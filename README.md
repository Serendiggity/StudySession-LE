# Insolvency Knowledge Base

**AI-Queryable Multi-Source Database for Exam Preparation**

A comprehensive, validated knowledge base containing insolvency course material, BIA statute, and OSB Directives - optimized for AI-assisted studying.

---

## What's Inside

**📁 `/database/`** - The Knowledge Base (Main Product)
- `insolvency_knowledge.db` - Complete multi-source database
- 13,779 entities + 385 BIA sections + 5 OSB Directives
- **Validated: 100% accuracy on 25 exam questions**

**📚 `/sources/`** - Original Source Materials
- Insolvency Administration Course Material (291 pages)
- BIA Statute - English sections (306 pages)
- OSB Directives (6R7, 16R, 17, 32R, 4R)

**🔧 `/tools/`** - Query and Validation Tools
- `/query/` - Search and navigate the knowledge base
- `/validation/` - Track quiz performance and accuracy
- `/ingestion/` - Add new source materials
- `/maintenance/` - Database optimization

**📖 `/docs/`** - Documentation
- `/guides/` - How to use the system
- `/analysis/` - Exam patterns and session summaries

---

## Quick Start

### 1. Query a BIA Section

```bash
sqlite3 database/insolvency_knowledge.db "
SELECT full_text FROM bia_sections WHERE section_number = '50.4';
"
```

### 2. Cross-Source Search

```bash
sqlite3 database/insolvency_knowledge.db "
SELECT source_name, COUNT(*) as mentions
FROM actors a
JOIN source_documents sd ON a.source_id = sd.id
WHERE role_canonical = 'Trustee'
GROUP BY source_name;
"
```

### 3. Find OSB Directive Content

```bash
sqlite3 database/insolvency_knowledge.db "
SELECT directive_name, LENGTH(full_text) as chars
FROM osb_directives
ORDER BY directive_number;
"
```

### 4. Use with AI Assistant

```bash
# Test with exam questions
python tools/query/test_exam_questions.py

# Navigate cross-references
python tools/query/cross_reference_navigator.py

# Validate quiz performance
python tools/validation/quiz_validation_system.py status
```

---

## Database Contents

### Source 1: Insolvency Administration Course Material
- **8,376 entities** across 7 categories:
  - 411 concepts
  - 228 deadlines
  - 1,374 documents
  - 2,869 actors
  - 1,788 procedures
  - 508 consequences
  - 1,198 statutory references

### Source 2: BIA Statute
- **5,403 entities** (4 categories: deadlines, documents, actors, procedures)
- **385 complete statutory sections** from 14 Parts
- Full-text search enabled (FTS5)

### Source 3: OSB Directives
- **5 complete directives** with full text:
  - Directive 6R7: Assessment of Individual Debtor
  - Directive 16R: Preparation of Statement of Affairs
  - Directive 17: Retention of Documents
  - Directive 32R: Electronic Recordkeeping
  - Directive 4R: Delegation of Tasks

---

## Validation Results

**Quiz 1:** 10/10 (100%) ✅
**Quiz 2:** 15/15 (100%) ✅
**Total:** 25/25 exam questions answered correctly

**Key Insight:** Grounded retrieval from validated sources prevents AI hallucinations (ChatGPT without database: 67% accuracy)

---

## Key Features

✅ **Multi-source integration** - Query across course material, statute, and directives
✅ **Cross-reference navigation** - Follow citations between sources automatically
✅ **Full-text search** - FTS5-optimized (<5ms queries)
✅ **Exam validation** - Track quiz performance and identify gaps
✅ **Section-level precision** - Complete statutory provisions, not fragments

---

## Technical Stack

- **Database:** SQLite with FTS5 full-text search
- **Extraction:** Lang Extract (entity extraction) + Regex (structural parsing)
- **Source Fetching:** Firecrawl MCP
- **Languages:** Python 3.11+, SQL

---

## Directory Structure

```
insolvency-knowledge/
├── database/              # Main product - the knowledge base
├── sources/               # Original PDFs and clean text
├── tools/                 # Organized by purpose (query, validation, etc.)
├── docs/                  # Documentation and analysis
├── src/                   # Core library code
├── archive/               # Old extraction attempts (reference only)
└── README.md              # This file
```

---

## Adding New Sources

See `/docs/guides/` for:
- Adding new OSB Directives
- Integrating additional statutes (CCAA, etc.)
- Expanding course material coverage

---

## Built With

- Lang Extract (Google) - Entity extraction
- Gemini 2.5 Flash - AI processing
- SQLite - Database
- Firecrawl - Web scraping
- Python - Core logic

---

## Repository

https://github.com/Serendiggity/StudySession-LE.git

---

**Status:** Production-ready, exam-validated ✅
**Last Updated:** November 2025
**Session:** 2 Complete
