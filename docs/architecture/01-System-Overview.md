# System Overview - High-Level Architecture

This diagram shows the complete end-to-end flow of the Insolvency Knowledge Base system.

## Architecture Flow

```mermaid
// [MermaidChart: 7662fd92-b21e-4242-a631-9942eb6d04b9]
graph LR
    INPUT[📥 Input Sources<br/>BIA PDF, Study Materials,<br/>OSB Directives, Forms]

    EXTRACT[⚙️ Extraction Pipeline<br/>5 phases:<br/>Text → Structure → Entities<br/>→ Enrichment → Relationships]

    DB[(💾 SQLite Database<br/>13,779 entities<br/>2,170 relationships<br/>385 BIA sections)]

    QUERY[🔍 Query System<br/>Exam Assistant Agent<br/>Diagram Generator]

    OUTPUT[📤 Outputs<br/>Formatted Answers + Quotes<br/>CSV Logs<br/>Mermaid Diagrams]

    INPUT --> EXTRACT --> DB --> QUERY --> OUTPUT

    classDef blue fill:#e1f5ff,stroke:#0078d4,stroke-width:2px
    classDef yellow fill:#fff4ce,stroke:#f59e0b,stroke-width:2px
    classDef green fill:#d1fae5,stroke:#059669,stroke-width:2px
    classDef pink fill:#fce7f3,stroke:#db2777,stroke-width:2px
    classDef purple fill:#f3e8ff,stroke:#9333ea,stroke-width:2px

    class INPUT blue
    class EXTRACT yellow
    class DB green
    class QUERY pink
    class OUTPUT purple
```

## Key Components

### 📥 Input Sources
- **BIA Statute PDF**: 385 sections, 492K characters
- **Study Materials PDF**: 291 pages (Insolvency Administration course)
- **OSB Directives**: 6 local files + web fetch capability
- **Forms & Rules**: BIA forms and general rules

### ⚙️ Extraction Pipeline
5-phase process that transforms raw PDFs into structured knowledge:
1. Text extraction and cleaning
2. Structure mapping (sections, hierarchy)
3. Entity extraction (Lang Extract with 7 categories)
4. Enrichment and normalization
5. Relationship extraction (AI-powered)

### 💾 SQLite Database
Central storage with:
- **13,779 entities** across 7 categories
- **2,170 relationships** with direct BIA quotes
- **385 BIA sections** with full-text search (FTS5)
- **3 primary views** for efficient querying

### 🔍 Query System
- **Exam Assistant Agent**: 5-phase intelligent search with cross-reference following
- **Diagram Generator**: Creates Mermaid visualizations (5 types)

### 📤 Outputs
- **Formatted Answers**: Sidebar format with direct quotes and section references
- **CSV Logs**: Complete Q&A tracking for study review
- **Mermaid Diagrams**: Process flows, timelines, duty chains

## Performance Metrics

- **Query Speed**: 5-20ms (50-100x faster than text search)
- **Extraction Cost**: $0.15-0.25 per source (Gemini Flash)
- **Processing Time**: 15-30 minutes per source
- **Validation**: 25/25 exam questions answered correctly (100%)
- **Accuracy**: Zero hallucinations (all answers source-grounded)
