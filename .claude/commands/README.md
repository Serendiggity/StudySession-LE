# Custom Slash Commands - Insolvency Knowledge Base

These commands provide quick access to the knowledge base with consistent formatting.

## Available Commands

### Query Commands

**`/bia [section-number]`**
- Query specific BIA section with all relationships
- Example: `/bia 50.4`
- Shows: Section text, duties, documents, full quotes

**`/duties [actor]`**
- Find all duties for an actor
- Example: `/duties Trustee`
- Shows: What they must/may do, when, consequences, BIA quotes

**`/docs [keyword]`**
- Find required documents for procedures
- Example: `/docs proposal`
- Shows: Which docs needed, mandatory vs optional, context

**`/search [keyword]`**
- Search across all sources (BIA + Study Materials)
- Example: `/search discharge`
- Shows: Relationships, sections, entities with keyword

**`/exam [question]`**
- Answer exam question using knowledge base
- Example: `/exam When is first-time bankrupt with surplus discharged?`
- Shows: Answer + direct BIA quote + section reference

### Visualization Commands

**`/diagram [topic] [section-pattern] [type]`**
- Generate Mermaid diagram
- Example: `/diagram "Division I NOI" "50.4%" flowchart`
- Types: flowchart, swimlane, duty-chain, timeline, erd

### System Commands

**`/coverage`**
- Show extraction coverage statistics
- Shows: Relationships by source, BIA coverage %, top sections

**`/extract-bia`**
- Run BIA relationship extraction
- Processes all 385 sections (~20-30 min)

**`/extract-study`**
- Run study material relationship extraction
- Processes all study sections (~20-40 min)

**`/quick-ref`**
- Show this quick reference guide

## Output Format Standards

All commands follow consistent formatting:

**Tables:**
- Header row with column names
- Separator line
- Data rows
- Source citations

**Quotes:**
- Direct BIA text in "quotes"
- Section reference: "Section X.X"
- Source: BIA Statute / Study Materials

**Traceability:**
- Every answer includes section number
- Every quote is exact text from source
- Every relationship links to entities

## Usage Tips

**Chain commands:**
```
/bia 168.1
/duties Trustee
```

**Use for exam prep:**
```
/exam [paste question]
→ Get answer with BIA quote + section
```

**Generate study aids:**
```
/diagram "Your Topic" "50%" flowchart
→ Visual diagram in Mermaid format
```

## Files

Commands are in: `.claude/commands/`
- Edit any `.md` file to customize
- Filename = command name
- Simple Markdown format
