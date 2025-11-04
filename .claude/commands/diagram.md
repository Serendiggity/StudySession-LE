---
description: Generate Mermaid diagram for a BIA topic
argument-hint: [topic] [section-pattern] [diagram-type]
allowed-tools: Bash(python3:*), Bash(cd:*)
---

Generate diagram for: **$1**

**Run diagram generator:**

```bash
cd /Users/jeffr/Local\ Project\ Repo/insolvency-knowledge && \
python3 tools/diagram/generate_mermaid.py \
  --topic "$1" \
  --section "${2:-50%}" \
  --type "${3:-flowchart}"
```

**Then display the generated .md file contents.**

**Diagram types available:**
- flowchart: Process flow (default)
- swimlane: Multi-actor visualization
- duty-chain: Obligation chains
- timeline: Gantt chart
- erd: Database schema

**Example outputs:**
- Division I NOI: /diagram "Division I NOI" "50.4%" flowchart
- Trustee duties: /diagram "Trustee Duties" "13%" duty-chain
- Discharge process: /diagram "Discharge" "170%" flowchart

**Output:**
Show the Mermaid diagram code and tell user to open in VS Code with Mermaid Preview extension.
