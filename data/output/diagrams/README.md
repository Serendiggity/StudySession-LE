# Mermaid Diagrams - Insolvency Knowledge Base

## Viewing Diagrams

These `.md` files contain Mermaid diagrams that visualize BIA processes and relationships.

**To view in VS Code:**
1. Install the [Mermaid Preview extension](https://marketplace.visualstudio.com/items?itemName=bierner.markdown-mermaid)
2. Open any `.md` file in this directory
3. Use the preview pane (Cmd+K V) or right-click → "Open Preview"

## Generated Diagrams

### Process Diagrams
- `division_i_noi_process_flowchart.md` - Division I Notice of Intention process flow
- `division_i_noi_process_duty-chain.md` - Division I duties with actors and deadlines
- `stay_of_proceedings_flowchart.md` - Stay of proceedings process
- `consumer_proposals_swimlane.md` - Consumer proposal swimlane showing actors

### Schema Diagram
- `knowledge_base_schema_erd.md` - Entity-Relationship Diagram of the database

## Generating More Diagrams

Use the `generate_mermaid.py` tool to create diagrams for any BIA section:

```bash
# Flowchart for a section
python tools/diagram/generate_mermaid.py \
  --topic "Division I NOI" \
  --section "50.4%" \
  --type flowchart

# Duty chain
python tools/diagram/generate_mermaid.py \
  --topic "Trustee Duties" \
  --section "13%" \
  --type duty-chain

# Swimlane diagram
python tools/diagram/generate_mermaid.py \
  --topic "Bankruptcy Process" \
  --section "158%" \
  --type swimlane

# Timeline (Gantt chart)
python tools/diagram/generate_mermaid.py \
  --topic "Discharge Timeline" \
  --section "170%" \
  --type timeline

# Entity-Relationship Diagram (schema)
python tools/diagram/generate_mermaid.py \
  --type erd
```

## Diagram Types

1. **Flowchart** (`--type flowchart`)
   - Step-by-step process flow
   - Shows actors, procedures, deadlines, consequences
   - Best for: Understanding sequential processes

2. **Swimlane** (`--type swimlane`)
   - Parallel lanes for different actors
   - Shows who does what
   - Best for: Multi-party processes

3. **Duty Chain** (`--type duty-chain`)
   - Actor → Duty → Deadline → Consequence
   - Shows obligations with modal verbs (shall, may)
   - Best for: Understanding mandatory vs discretionary actions

4. **Timeline** (`--type timeline`)
   - Gantt chart showing deadlines
   - Shows temporal relationships
   - Best for: Understanding time-sensitive processes

5. **ERD** (`--type erd`)
   - Entity-Relationship Diagram
   - Shows database schema
   - Best for: Understanding data structure

## Data Source

Diagrams are generated from the `insolvency_knowledge.db` database, using:
- **54 relationship records** extracted from BIA sections
- Relationship types: duty_relationships, document_requirements, trigger_relationships
- Sections covered: 50, 50.4, 62, 66.13, 66.14, 69 (from initial extraction)

## Notes

- Diagrams reflect relationships extracted during Session 3
- More comprehensive diagrams will be available after extracting relationships from all 385 BIA sections
- Current diagrams focus on Division I proposals and consumer insolvency processes
