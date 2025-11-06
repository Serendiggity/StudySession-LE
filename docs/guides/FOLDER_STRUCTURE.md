# Universal Knowledge Platform - Folder Structure

## Root Level

```
insolvency-knowledge/
├── .claude/              # Claude Code configuration
├── .mcp.json            # MCP server configuration for Claude Code
├── .env                 # API keys (gitignored)
├── README.md            # Main system overview
├── projects/            # Multi-domain knowledge bases
├── mcp_server/          # MCP server for Claude integration
├── shared/              # Reusable code across domains
├── src/                 # Core extraction engine
├── scripts/             # Utility scripts
├── docs/                # Documentation
├── archive/             # Deprecated code and investigations
├── tests/               # Test suite
└── [Legacy folders]     # To be migrated/removed
```

---

## Project Structure (Multi-Domain)

Each knowledge domain gets its own isolated project:

```
projects/
└── {domain-name}/           # e.g., insolvency-law, radiology, civil-engineering
    ├── config.json          # Domain configuration (terminology, schema)
    ├── database/
    │   └── knowledge.db     # SQLite database with FTS5 indexes
    ├── sources/             # Original source materials
    │   ├── {source-type}/   # e.g., bia_statute, study_materials, osb_directives
    │   └── ...
    └── tracking/            # Q&A audit trail (exam prep)
        └── questions_answered.csv
```

### Domain Configuration (`config.json`)

```json
{
  "project_id": "insolvency-law",
  "project_name": "Canadian Insolvency Law",
  "domain": "insolvency",
  "database_path": "projects/insolvency-law/database/knowledge.db",
  "domain_terminology": {
    "reference_format": "§{section_number}",
    "reference_prefix": "BIA",
    "source_type": "BIA Statute",
    "primary_content_table": "bia_sections"
  }
}
```

---

## Claude Code Configuration

```
.claude/
├── CLAUDE.md              # Main instructions for Claude Code
├── settings.local.json    # Project-specific settings
├── agents/                # Specialized agents (currently disabled)
│   ├── exam-assistant.md
│   ├── knowledge-assistant.md
│   └── archive/           # Test/debug agents
└── commands/              # Custom slash commands
    ├── extract-bia.md
    ├── coverage.md
    └── diagram.md
```

---

## MCP Server

```
mcp_server/
├── server.py              # Main MCP server implementation
├── README.md              # Setup instructions
├── pyproject.toml         # Python package config
├── config_examples/       # Example configurations
├── resources/             # MCP resource definitions
└── tools/                 # MCP tool implementations
```

**Key MCP Tools:**
- `answer_exam_question` - Primary question answering with sidebar format
- `query_knowledge_base` - Low-level database search
- `switch_project` - Change active knowledge domain
- `get_statistics` - View database stats

---

## Core Extraction Engine

```
src/
├── extraction/           # Lang Extract integration
│   ├── schemas_v2_atomic.py    # Entity definitions
│   ├── extract.py              # Main extraction runner
│   └── section_mapper.py       # Document structure mapping
├── database/             # Database management
│   ├── schema.py               # SQLite schema definitions
│   ├── loader.py               # Data loading utilities
│   └── fts_setup.py            # Full-text search configuration
├── normalization/        # Data cleaning
│   ├── canonical_mapper.py     # AI-powered entity deduplication
│   └── proximity_linker.py     # Entity relationship detection
├── visualization/        # Output generation
│   ├── timeline_generator.py   # Swimlane diagrams
│   └── diagram_utils.py        # Mermaid helpers
└── cli/                  # Command-line interface
    └── main.py
```

---

## Shared Libraries (Universal Code)

```
shared/
├── src/
│   ├── project.py        # ProjectManager class (multi-domain support)
│   ├── extraction.py     # SourceManager, ExtractionRunner
│   └── storage.py        # DatabaseLoader
└── tools/                # Reusable utilities
    ├── pdf_processor.py
    └── text_cleaner.py
```

**Usage:** Import from `shared.src` in any domain-specific code.

---

## Scripts

```
scripts/
├── migration/            # Database migration scripts
│   ├── migrate_to_new_db.py
│   ├── load_bia_to_new_db.py
│   └── migrate_old_data.py
└── maintenance/          # Utility scripts
    ├── backup_database.sh
    └── verify_extraction.py
```

---

## Documentation

```
docs/
├── guides/               # User-facing documentation
│   ├── SYSTEM_GUIDE.md         # Complete system guide
│   ├── FOLDER_STRUCTURE.md     # This file
│   └── EXAM_PREP_GUIDE.md      # How to use for exam prep
├── architecture/         # Technical design
│   ├── DATABASE_SCHEMA.md
│   ├── EXTRACTION_PIPELINE.md
│   └── MCP_INTEGRATION.md
├── analysis/             # Extraction reports
│   ├── 09-Extraction-Success-Summary.md
│   └── coverage_reports/
└── research/             # Planning and investigation
    └── original_planning.md
```

---

## Archive

```
archive/
├── crash_investigation/  # Agent delegation bug investigation
│   ├── CRASH-ROOT-CAUSE-REVISED.md
│   ├── PATTERN_ANALYSIS.md
│   └── TEST-RESULTS.md
├── deprecated_scripts/   # Old code
└── extraction_logs/      # Historical extraction runs
```

---

## Data Organization

```
data/
├── input/                # Source materials (staging)
│   └── study_materials/
│       └── InsolvencyStudyGuide.pdf
├── output/               # Generated files
│   ├── timelines/              # Visual diagrams
│   ├── gemini_canonical_mappings.json
│   └── section_map.json
├── sql/                  # SQL scripts
│   └── add_entity_fts_indexes.sql
├── examples/             # Lang Extract examples
│   └── content_examples/
│       ├── actors_minimal.py
│       ├── deadlines_minimal.py
│       └── ...
└── test_materials/       # Test data for validation
```

---

## Legacy Folders (To Be Migrated or Removed)

The following folders exist from earlier iterations and may need cleanup:

```
database/              # OLD - Use projects/{domain}/database/ instead
sources/               # OLD - Use projects/{domain}/sources/ instead
tools/                 # Partially migrated to src/ and scripts/
logs/                  # Can be removed (logs gitignored)
```

**Migration Plan:**
- Move active code to appropriate locations
- Archive historical content
- Update references in documentation

---

## Adding a New Domain

1. Create project folder:
   ```bash
   mkdir -p projects/radiology/{database,sources,tracking}
   ```

2. Create config.json:
   ```json
   {
     "project_id": "radiology",
     "project_name": "Radiology Clinical Guidelines",
     "domain": "medical",
     "database_path": "projects/radiology/database/knowledge.db",
     "domain_terminology": {
       "reference_format": "ACR {section_number}",
       "reference_prefix": "ACR",
       "source_type": "Clinical Guideline",
       "primary_content_table": "clinical_guidelines"
     }
   }
   ```

3. Add source materials to `projects/radiology/sources/`

4. Run extraction:
   ```bash
   python src/cli/main.py extract --project radiology
   ```

5. Query via MCP:
   ```
   User: "Switch to radiology project"
   User: "What are contraindications for contrast agents?"
   ```

---

## Best Practices

### For Users
- **Keep projects isolated** - Each domain in its own folder
- **Use tracking/** - All Q&A automatically recorded for review
- **Back up databases** - Before major changes

### For Developers
- **Use shared/** - For code reusable across domains
- **Use src/** - For domain-agnostic extraction logic
- **Document in docs/** - Architecture decisions and design
- **Archive old code** - Don't delete, move to archive/ with notes

### For Claude Code
- **Check .claude/CLAUDE.md** - System behavior defined there
- **Use MCP tools** - Don't query database directly
- **Follow systematic workflow** - Especially for multiple choice questions

---

## Version Control

**Committed:**
- All code (src/, shared/, scripts/, mcp_server/)
- Configuration (.claude/, .mcp.json)
- Documentation (docs/, README.md)
- Project configs (projects/*/config.json)
- Tracking files (projects/*/tracking/*.csv)

**Gitignored:**
- API keys (.env)
- Large databases (*.db)
- Generated outputs (data/output/)
- IDE files (.vscode/, .idea/)
- System files (.DS_Store)
- Logs (*.log)

---

**Last Updated:** 2025-11-05
**System Version:** Universal Knowledge Platform v2.0
