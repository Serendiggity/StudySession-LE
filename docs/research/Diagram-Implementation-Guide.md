# Quick Implementation Guide: Diagram Generation

**Target System:** Insolvency Knowledge Base (SQLite + MCP)
**Based on:** Diagram-Generation-Research-2025.md
**Last Updated:** January 6, 2025

---

## Quick Start (5 Minutes)

### Installation

```bash
# Core dependencies
pip install mermaid-py plotly pandas

# Optional (for advanced features)
pip install eralchemy pm4py networkx
```

---

## Use Case Implementations

### 1. Consumer Proposal Process Flow (Mermaid)

**File:** `src/diagram_generators/process_flow.py`

```python
#!/usr/bin/env python3
"""Generate process flow diagrams from procedures table"""

import sqlite3
from pathlib import Path

def generate_mermaid_flowchart(topic: str, db_path: str = "database/insolvency.db"):
    """Generate Mermaid flowchart from database procedures"""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query procedures
    cursor.execute("""
        SELECT step_number, action, actor, decision_point
        FROM procedures
        WHERE topic = ?
        ORDER BY step_number
    """, (topic,))

    rows = cursor.fetchall()
    conn.close()

    # Build Mermaid syntax
    mermaid_lines = ["flowchart TD"]

    for i, (step_num, action, actor, is_decision) in enumerate(rows):
        node_id = f"S{step_num}"

        # Format node
        if is_decision:
            # Diamond for decisions
            mermaid_lines.append(f'    {node_id}{{{action}}}')
        else:
            # Rectangle with actor
            label = f"{actor}: {action}" if actor else action
            mermaid_lines.append(f'    {node_id}["{label}"]')

        # Connect to previous step
        if i > 0:
            prev_id = f"S{rows[i-1][0]}"
            mermaid_lines.append(f"    {prev_id} --> {node_id}")

    return "\n".join(mermaid_lines)

# Usage
if __name__ == "__main__":
    mermaid_code = generate_mermaid_flowchart("consumer proposal")

    # Save to markdown file
    output = Path("docs/diagrams/consumer_proposal_flow.md")
    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w") as f:
        f.write(f"# Consumer Proposal Process Flow\n\n")
        f.write("```mermaid\n")
        f.write(mermaid_code)
        f.write("\n```\n")

    print(f"✓ Flowchart saved to {output}")
    print(f"\nPreview on GitHub or use Mermaid Live Editor:")
    print("https://mermaid.live")
```

**Run:**
```bash
python src/diagram_generators/process_flow.py
```

---

### 2. Timeline Generation (Plotly)

**File:** `src/diagram_generators/timeline.py`

```python
#!/usr/bin/env python3
"""Generate interactive timeline from deadlines table"""

import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from pathlib import Path

def generate_timeline(division: str = "I", db_path: str = "database/insolvency.db"):
    """Generate Plotly timeline for division deadlines"""

    conn = sqlite3.connect(db_path)

    # Query deadlines
    query = """
        SELECT
            deadline_name as Task,
            trigger_event as Description,
            timeframe_days as Days,
            reference_section as Section
        FROM deadlines
        WHERE division = ?
        ORDER BY timeframe_days
    """

    df = pd.read_sql(query, conn, params=(division,))
    conn.close()

    if df.empty:
        print(f"No deadlines found for Division {division}")
        return None

    # Calculate dates (Day 0 = today)
    base_date = datetime.now()
    df['Start'] = base_date
    df['Finish'] = df.apply(
        lambda row: base_date + timedelta(days=row['Days']),
        axis=1
    )

    # Create Gantt chart
    fig = px.timeline(
        df,
        x_start="Start",
        x_end="Finish",
        y="Task",
        color="Section",
        hover_data=["Description", "Days"],
        title=f"Division {division} Deadlines Timeline"
    )

    # Customize
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(
        xaxis_title="Timeline",
        yaxis_title="Deadline",
        height=max(400, len(df) * 40),
        hovermode='closest',
        showlegend=True
    )

    return fig

# Usage
if __name__ == "__main__":
    for division in ["I", "II"]:
        fig = generate_timeline(division)

        if fig:
            output = Path(f"docs/diagrams/timeline_division_{division}.html")
            output.parent.mkdir(parents=True, exist_ok=True)

            fig.write_html(str(output))
            print(f"✓ Timeline saved to {output}")

    print("\nOpen HTML files in browser to view interactive timelines")
```

**Run:**
```bash
python src/diagram_generators/timeline.py
```

---

### 3. Database Schema Diagram (ERAlchemy)

**File:** `src/diagram_generators/schema.py`

```python
#!/usr/bin/env python3
"""Generate ER diagram of database schema"""

from eralchemy import render_er
from pathlib import Path
import subprocess

def generate_schema_diagram(db_path: str = "database/insolvency.db",
                           output_format: str = "png"):
    """Generate ER diagram using ERAlchemy"""

    output = Path(f"docs/diagrams/schema.{output_format}")
    output.parent.mkdir(parents=True, exist_ok=True)

    # Generate diagram
    try:
        render_er(
            f"sqlite:///{db_path}",
            str(output)
        )
        print(f"✓ Schema diagram saved to {output}")

        # Also generate with customization
        render_er(
            f"sqlite:///{db_path}",
            str(output.with_stem("schema_detailed")),
            exclude_tables=['sqlite_sequence'],
            include_columns=True
        )
        print(f"✓ Detailed schema saved to {output.with_stem('schema_detailed')}")

        return output

    except Exception as e:
        print(f"Error generating schema: {e}")
        print("\nMake sure Graphviz is installed:")
        print("  macOS: brew install graphviz")
        print("  Ubuntu: sudo apt-get install graphviz")
        return None

# Usage
if __name__ == "__main__":
    generate_schema_diagram(output_format="png")
    generate_schema_diagram(output_format="pdf")
```

**Run:**
```bash
# Install Graphviz first (one-time)
brew install graphviz  # macOS
# or: sudo apt-get install graphviz  # Linux

python src/diagram_generators/schema.py
```

---

### 4. Section Relationship Network (NetworkX + Plotly)

**File:** `src/diagram_generators/section_network.py`

```python
#!/usr/bin/env python3
"""Generate interactive network of BIA section relationships"""

import sqlite3
import networkx as nx
import plotly.graph_objects as go
from pathlib import Path

def generate_section_network(limit: int = 100, db_path: str = "database/insolvency.db"):
    """Generate interactive network graph of section relationships"""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query section references
    cursor.execute("""
        SELECT citing_section, cited_section, relationship_type
        FROM statutory_references
        LIMIT ?
    """, (limit,))

    # Build directed graph
    G = nx.DiGraph()

    for citing, cited, rel_type in cursor.fetchall():
        if citing and cited:  # Skip null values
            G.add_edge(citing, cited, relationship=rel_type)

    conn.close()

    if len(G.nodes()) == 0:
        print("No relationships found in database")
        return None

    # Layout using spring algorithm
    pos = nx.spring_layout(G, k=0.5, iterations=50, seed=42)

    # Extract coordinates for Plotly
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    node_x = [pos[node][0] for node in G.nodes()]
    node_y = [pos[node][1] for node in G.nodes()]
    node_text = [f"Section {node}" for node in G.nodes()]

    # Calculate node sizes based on degree
    node_degrees = [G.degree(node) for node in G.nodes()]
    node_sizes = [10 + degree * 2 for degree in node_degrees]

    # Create Plotly figure
    fig = go.Figure()

    # Add edges
    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines',
        name='References'
    ))

    # Add nodes
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=[str(node) for node in G.nodes()],
        textposition="top center",
        marker=dict(
            size=node_sizes,
            color='lightblue',
            line=dict(width=2, color='darkblue')
        ),
        hovertext=node_text,
        hoverinfo='text',
        name='Sections'
    ))

    # Layout
    fig.update_layout(
        title=f"BIA Section Relationship Network ({len(G.nodes())} sections)",
        showlegend=False,
        hovermode='closest',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=700,
        plot_bgcolor='white'
    )

    return fig

# Usage
if __name__ == "__main__":
    fig = generate_section_network(limit=100)

    if fig:
        output = Path("docs/diagrams/section_network.html")
        output.parent.mkdir(parents=True, exist_ok=True)

        fig.write_html(str(output))
        print(f"✓ Network diagram saved to {output}")
        print("\nOpen in browser to explore interactively")
```

**Run:**
```bash
pip install networkx  # one-time
python src/diagram_generators/section_network.py
```

---

### 5. Priority Payment Waterfall (Mermaid)

**File:** `src/diagram_generators/priority_waterfall.py`

```python
#!/usr/bin/env python3
"""Generate BIA §136 priority payment waterfall"""

import sqlite3
from pathlib import Path

def generate_priority_waterfall(db_path: str = "database/insolvency.db"):
    """Generate hierarchical payment priority diagram"""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query priority levels
    cursor.execute("""
        SELECT priority_level, claim_type, amount_limit, bia_section
        FROM priority_claims
        ORDER BY priority_level
    """)

    rows = cursor.fetchall()
    conn.close()

    # Build Mermaid flowchart
    mermaid_lines = [
        "flowchart TD",
        '    START["💰 Estate Funds Available"]',
        ""
    ]

    previous_node = "START"

    for level, claim_type, limit, section in rows:
        node_id = f"P{level}"

        # Format amount limit
        if limit:
            limit_text = f"Max: ${limit:,}"
        else:
            limit_text = "No limit"

        # Create node with multi-line label
        label = f"{level}. {claim_type}<br/>{limit_text}<br/>BIA §{section}"
        mermaid_lines.append(f'    {node_id}["{label}"]')

        # Connect from previous
        mermaid_lines.append(f"    {previous_node} -->|Pay| {node_id}")
        previous_node = node_id

    # Add final distribution
    mermaid_lines.extend([
        "",
        '    UNSECURED["Unsecured Creditors<br/>(Pro Rata)"]',
        f"    {previous_node} -->|Remaining| UNSECURED",
        '    END["Distribution Complete"]',
        "    UNSECURED --> END",
        "",
        "    %% Styling",
        "    classDef secured fill:#d4edda,stroke:#28a745,stroke-width:2px",
        "    classDef preferred fill:#fff3cd,stroke:#ffc107,stroke-width:2px",
        "    classDef unsecured fill:#f8d7da,stroke:#dc3545,stroke-width:2px",
        "",
        "    class P1,P2 secured",
        "    class P3,P4,P5 preferred",
        "    class UNSECURED unsecured"
    ])

    return "\n".join(mermaid_lines)

# Usage
if __name__ == "__main__":
    mermaid_code = generate_priority_waterfall()

    output = Path("docs/diagrams/priority_waterfall.md")
    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w") as f:
        f.write("# BIA §136 Priority Payment Waterfall\n\n")
        f.write("```mermaid\n")
        f.write(mermaid_code)
        f.write("\n```\n")

    print(f"✓ Priority waterfall saved to {output}")
    print("\nView on GitHub or use Mermaid Live Editor")
```

**Run:**
```bash
python src/diagram_generators/priority_waterfall.py
```

---

## MCP Integration

### Add to MCP Server

**File:** `mcp_server/tools/diagrams.py`

```python
"""MCP tools for diagram generation"""

import json
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from diagram_generators.process_flow import generate_mermaid_flowchart
from diagram_generators.timeline import generate_timeline
from diagram_generators.section_network import generate_section_network
from diagram_generators.schema import generate_schema_diagram
from diagram_generators.priority_waterfall import generate_priority_waterfall

def register_diagram_tools(server, db_path: str):
    """Register diagram generation tools with MCP server"""

    @server.tool()
    async def generate_diagram(
        diagram_type: str,
        topic: str = None,
        division: str = None,
        limit: int = 100
    ) -> str:
        """
        Generate diagrams from database data

        Args:
            diagram_type: One of ['flowchart', 'timeline', 'network', 'schema', 'waterfall']
            topic: Topic for flowchart (e.g., 'consumer proposal')
            division: Division for timeline ('I' or 'II')
            limit: Max items for network diagram

        Returns:
            JSON with diagram format and content
        """

        try:
            if diagram_type == 'flowchart':
                if not topic:
                    return json.dumps({"error": "topic required for flowchart"})

                mermaid_code = generate_mermaid_flowchart(topic, db_path)
                return json.dumps({
                    "format": "mermaid",
                    "content": mermaid_code,
                    "metadata": {"type": "flowchart", "topic": topic}
                })

            elif diagram_type == 'timeline':
                division = division or "I"
                fig = generate_timeline(division, db_path)

                if fig is None:
                    return json.dumps({"error": f"No deadlines for Division {division}"})

                html = fig.to_html(include_plotlyjs='cdn')
                return json.dumps({
                    "format": "html",
                    "content": html,
                    "metadata": {"type": "timeline", "division": division}
                })

            elif diagram_type == 'network':
                fig = generate_section_network(limit, db_path)

                if fig is None:
                    return json.dumps({"error": "No relationships found"})

                html = fig.to_html(include_plotlyjs='cdn')
                return json.dumps({
                    "format": "html",
                    "content": html,
                    "metadata": {"type": "network", "node_count": limit}
                })

            elif diagram_type == 'waterfall':
                mermaid_code = generate_priority_waterfall(db_path)
                return json.dumps({
                    "format": "mermaid",
                    "content": mermaid_code,
                    "metadata": {"type": "waterfall"}
                })

            elif diagram_type == 'schema':
                output_path = generate_schema_diagram(db_path, "png")

                if output_path is None:
                    return json.dumps({"error": "Schema generation failed"})

                return json.dumps({
                    "format": "file_path",
                    "content": str(output_path),
                    "metadata": {"type": "schema"}
                })

            else:
                return json.dumps({
                    "error": f"Unknown diagram type: {diagram_type}",
                    "supported": ['flowchart', 'timeline', 'network', 'schema', 'waterfall']
                })

        except Exception as e:
            return json.dumps({"error": str(e)})

    return True
```

**Register in server.py:**

```python
from tools.diagrams import register_diagram_tools

# After server initialization
register_diagram_tools(mcp_server, db_path="database/insolvency.db")
```

**Usage from Claude:**

```
Generate a flowchart for the consumer proposal process
→ @generate_diagram(diagram_type="flowchart", topic="consumer proposal")

Show me the timeline for Division I deadlines
→ @generate_diagram(diagram_type="timeline", division="I")

Create a network diagram of section relationships
→ @generate_diagram(diagram_type="network", limit=50)
```

---

## Testing

**File:** `tests/test_diagram_generators.py`

```python
"""Tests for diagram generators"""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from diagram_generators.process_flow import generate_mermaid_flowchart
from diagram_generators.timeline import generate_timeline
from diagram_generators.section_network import generate_section_network

# Assume test database exists
TEST_DB = "database/test_insolvency.db"

def test_flowchart_generation():
    """Test Mermaid flowchart generation"""
    mermaid = generate_mermaid_flowchart("test_topic", TEST_DB)

    assert "flowchart TD" in mermaid
    assert len(mermaid) > 0

def test_timeline_generation():
    """Test Plotly timeline generation"""
    fig = generate_timeline("I", TEST_DB)

    assert fig is not None
    assert len(fig.data) > 0

def test_network_generation():
    """Test NetworkX network generation"""
    fig = generate_section_network(limit=10, db_path=TEST_DB)

    if fig:  # May be None if no data
        assert len(fig.data) > 0

def test_mermaid_syntax_valid():
    """Ensure Mermaid syntax is valid"""
    mermaid = generate_mermaid_flowchart("test", TEST_DB)

    # Basic syntax checks
    assert "flowchart" in mermaid
    assert "-->" in mermaid or "---" in mermaid
    assert "[" in mermaid or "{" in mermaid
```

**Run tests:**
```bash
pytest tests/test_diagram_generators.py -v
```

---

## Performance Optimization

### Caching Layer

**File:** `src/diagram_generators/cache.py`

```python
"""Simple caching for diagram generation"""

import hashlib
import json
from pathlib import Path
from datetime import datetime, timedelta
from functools import wraps

CACHE_DIR = Path("cache/diagrams")
CACHE_TTL = timedelta(hours=24)

def cached_diagram(func):
    """Decorator to cache diagram results"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Generate cache key
        key_data = json.dumps({
            "func": func.__name__,
            "args": args,
            "kwargs": kwargs
        }, sort_keys=True)
        cache_key = hashlib.md5(key_data.encode()).hexdigest()

        cache_file = CACHE_DIR / f"{cache_key}.json"

        # Check cache
        if cache_file.exists():
            age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)

            if age < CACHE_TTL:
                with open(cache_file) as f:
                    return json.load(f)["result"]

        # Generate fresh result
        result = func(*args, **kwargs)

        # Cache result
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with open(cache_file, "w") as f:
            json.dump({"result": result, "timestamp": datetime.now().isoformat()}, f)

        return result

    return wrapper

# Usage
@cached_diagram
def generate_expensive_diagram():
    # ... expensive operation
    pass
```

---

## Troubleshooting

### Common Issues

**1. Graphviz not found**
```bash
# macOS
brew install graphviz

# Ubuntu/Debian
sudo apt-get install graphviz

# Windows
# Download from: https://graphviz.org/download/
```

**2. Mermaid syntax errors**
- Use Mermaid Live Editor to validate: https://mermaid.live
- Check for special characters in labels (escape or quote)
- Ensure node IDs are alphanumeric

**3. Plotly figures not showing**
- Include CDN: `fig.write_html("file.html", include_plotlyjs='cdn')`
- Check DataFrame column names match x_start/x_end parameters
- Ensure dates are datetime objects, not strings

**4. NetworkX layout issues**
- Increase iterations: `nx.spring_layout(G, iterations=100)`
- Try different algorithms: `nx.circular_layout`, `nx.kamada_kawai_layout`
- Filter to smaller subgraphs for clarity

---

## Next Steps

1. **Create diagram output directory:**
   ```bash
   mkdir -p docs/diagrams
   ```

2. **Run all generators:**
   ```bash
   python src/diagram_generators/process_flow.py
   python src/diagram_generators/timeline.py
   python src/diagram_generators/schema.py
   python src/diagram_generators/section_network.py
   python src/diagram_generators/priority_waterfall.py
   ```

3. **View outputs:**
   - Markdown files (*.md): Open on GitHub or Mermaid Live
   - HTML files (*.html): Open in browser
   - Image files (*.png): Standard image viewer

4. **Integrate with MCP:**
   - Add tools/diagrams.py to MCP server
   - Test with Claude
   - Add to documentation

5. **Automate:**
   - Add to CI/CD pipeline
   - Schedule regeneration on database updates
   - Generate on demand via MCP

---

## Resources

**Mermaid:**
- Live Editor: https://mermaid.live
- Documentation: https://mermaid.js.org
- Syntax: https://mermaid.js.org/intro/syntax-reference.html

**Plotly:**
- Gallery: https://plotly.com/python/
- Timeline docs: https://plotly.com/python/gantt/
- Customization: https://plotly.com/python/figure-structure/

**ERAlchemy:**
- Docs: https://github.com/eralchemy/eralchemy
- Examples: https://pypi.org/project/eralchemy/

**NetworkX:**
- Tutorial: https://networkx.org/documentation/stable/tutorial.html
- Layouts: https://networkx.org/documentation/stable/reference/drawing.html

---

**Quick Reference Complete**

For comprehensive research and additional tools, see: `Diagram-Generation-Research-2025.md`
