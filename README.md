# Universal Knowledge Extraction Platform

**AI-Powered Multi-Domain Knowledge Base System**

Extract, structure, and query knowledge from any domain: law, medicine, engineering, and more.

**Current Implementation:** Canadian Insolvency Law (BIA + Study Materials + OSB Directives)

---

## Quick Start

### For Exam Prep (Insolvency Law)

Ask Claude Code questions directly:
```
"What are the trustee's duties under section 158?"
"What type of discharge when no §173 facts are proven?"
```

Claude will:
- Search database (BIA + study materials + OSB directives)
- Return direct quotes with section references
- Record answers to CSV for review

### For Adding New Domains

1. Create new project: `projects/{domain-name}/`
2. Add source materials to `projects/{domain-name}/sources/`
3. Configure domain terminology in `projects/{domain-name}/config.json`
4. Run extraction
5. Query via MCP tools

---

## What's Inside

### Current Project: Insolvency Law

**Database:** `projects/insolvency-law/database/knowledge.db`
- 8,376 study material entities (atomic extraction)
- 7,450 BIA relationships
- 249 BIA sections (full text with FTS5 search)
- 5 OSB directives (full text with FTS5 search)
- **All content searchable via full-text search**

**Source Materials:**
- Insolvency Administration Course Material (291 pages, 8,376 entities extracted)
- BIA Statute - English sections (306 pages, full text)
- OSB Directives (6R7, 16R, 17, 32R, 4R)

**Tracking:**
- `projects/insolvency-law/tracking/questions_answered.csv` - All exam Q&A with rationale
- Automatic CSV recording for audit trail

---

## System Architecture

```
Universal Knowledge Platform
├── projects/              # Multi-domain support
│   └── insolvency-law/   # First implementation
│       ├── database/     # SQLite with FTS5
│       ├── sources/      # Original PDFs/documents
│       ├── tracking/     # Q&A audit trail
│       └── config.json   # Domain configuration
├── mcp_server/           # MCP server for Claude integration
├── shared/src/           # Reusable extraction/query code
├── src/                  # Core extraction engine
│   ├── extraction/       # Lang Extract integration
│   ├── database/         # Schema + loaders
│   ├── normalization/    # AI-powered canonical mapping
│   └── visualization/    # Timeline/diagram generators
└── .claude/              # Claude Code configuration
    ├── CLAUDE.md         # Main instructions
    └── agents/           # Specialized agents (disabled due to bug)
```

---

## Features

### Extraction (Universal)
- **Atomic entity extraction** (7 categories: concepts, actors, deadlines, documents, procedures, consequences, statutory references)
- **Relationship extraction** (duties, triggers, consequences)
- **Section mapping** (hierarchical document structure)
- **AI-powered normalization** (canonical actor mapping)

### Search (FTS5 Full-Text)
- BIA sections (exact text + cross-references)
- OSB directives (policy guidance)
- Relationships (7,450 extracted)
- Study material entities (8,376 across 7 categories)
- Progressive search strategies (phrases → key terms → OR fallback)

### Query Interface
- **MCP tools** for Claude Code/Desktop
- **Direct SQL** for advanced queries
- **Slash commands** for common operations

### Exam Preparation
- Sidebar-formatted answers with direct quotes
- Automatic CSV tracking with timestamps
- Cross-reference following
- Source citation (statute/directive/study materials)

---

## Documentation

### For Users
- **This file** - System overview
- `.claude/CLAUDE.md` - How Claude Code uses this system
- `docs/guides/` - Detailed usage guides

### For Developers
- `docs/architecture/` - System design documents
- `docs/analysis/` - Extraction success reports
- `mcp_server/README.md` - MCP server setup

### Project History
- `docs/research/` - Original research and planning
- `archive/` - Deprecated scripts and investigations

---

## Key Innovations

1. **Atomic Extraction Approach**
   - 1-2 attributes per category = 95%+ reliability
   - Minimal examples, Lang Extract expands automatically
   - 8,376 entities extracted from 291-page PDF

2. **Multi-Domain Architecture**
   - Same extraction engine works for law, medicine, engineering
   - Domain-specific terminology in config
   - Automatic adaptation to document structure

3. **FTS5 Search with BM25 Ranking**
   - All content fully indexed
   - Progressive search strategies (exact → fuzzy → OR)
   - Sub-second query responses

4. **Systematic Quality Control**
   - Mandatory workflow for multiple choice questions
   - Check ALL options against source text
   - Look for exact word-for-word matches
   - No guessing or external knowledge

---

## Known Issues

### Agent Delegation Bug (Claude Code)
- **Issue:** Heap exhaustion when delegating to agents
- **Workaround:** Main Claude answers directly using MCP tools
- **Status:** Works perfectly, agents disabled until Claude Code bug is fixed

---

## Getting Started

### Prerequisites
- Python 3.10+
- Claude Code or Claude Desktop
- SQLite3

### Setup
1. Install MCP SDK: `pip install mcp`
2. Configure Claude Code: Copy `.mcp.json.example` to `.mcp.json`
3. Enable project MCPs in `.claude/settings.local.json`
4. Restart Claude Code

### Usage
Ask Claude Code questions about insolvency law - it will search the database and return answers with direct quotes and citations.

---

## Future Domains

The system is designed to support any knowledge domain:
- **Medical:** Clinical guidelines, drug databases, diagnostic criteria
- **Engineering:** Building codes, material specifications, design standards
- **Legal:** Other areas of law beyond insolvency

Each domain gets its own project folder with isolated database and configuration.

---

## License

MIT

---

**Built with Claude Code** 🤖
