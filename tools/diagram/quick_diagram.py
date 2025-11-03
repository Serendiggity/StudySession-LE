#!/usr/bin/env python3
"""
Quick Diagram Generator - Proof of Concept
Generate Mermaid diagrams from database queries

Usage:
    python quick_diagram.py "Division I NOI timeline"
    python quick_diagram.py "Trustee duties workflow"
    python quick_diagram.py "Stay of proceedings process"

Requirements:
    npm install -g @mermaid-js/mermaid-cli
"""

import sqlite3
import subprocess
import tempfile
import sys
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent.parent.parent / "database" / "insolvency_knowledge.db"


def generate_division_i_noi_timeline():
    """Generate Division I NOI timeline diagram"""

    conn = sqlite3.connect(DB_PATH)

    # Query entities from sections 4.3.6-4.3.11 (Division I NOI sections)
    query = """
    SELECT
        'deadline' as type,
        timeframe as label,
        section_number,
        section_context
    FROM deadlines
    WHERE section_number LIKE '4.3.%'
        AND CAST(SUBSTR(section_number, 5) AS REAL) BETWEEN 6 AND 11

    UNION ALL

    SELECT
        'document' as type,
        document_name_canonical as label,
        section_number,
        section_context
    FROM documents
    WHERE section_number LIKE '4.3.%'
        AND CAST(SUBSTR(section_number, 5) AS REAL) BETWEEN 6 AND 11

    UNION ALL

    SELECT
        'actor' as type,
        role_canonical as label,
        section_number,
        section_context
    FROM actors
    WHERE section_number LIKE '4.3.%'
        AND CAST(SUBSTR(section_number, 5) AS REAL) BETWEEN 6 AND 11
        AND role_canonical IN ('Trustee', 'Debtor', 'Creditor')

    ORDER BY section_number
    """

    results = conn.execute(query).fetchall()
    conn.close()

    # Generate Mermaid flowchart
    mermaid = "flowchart TD\n"
    mermaid += "    Start([Debtor in Financial Difficulty])\n\n"

    # Main timeline
    mermaid += "    Start --> NOI\n"
    mermaid += "    NOI[File Notice of Intention - Form 43<br/>BIA s. 50.4]\n\n"

    mermaid += "    NOI --> T1\n"
    mermaid += "    T1[10 days: File Proposal<br/>or deemed bankruptcy]\n\n"

    mermaid += "    T1 --> Meeting\n"
    mermaid += "    Meeting[First Meeting of Creditors<br/>BIA s. 51]\n\n"

    mermaid += "    Meeting --> Vote\n"
    mermaid += "    Vote{Creditors Vote<br/>2/3 approval required}\n\n"

    mermaid += "    Vote -->|Approve| Court\n"
    mermaid += "    Vote -->|Reject| Bankruptcy\n\n"

    mermaid += "    Court[Court Approval Hearing<br/>BIA s. 58]\n"
    mermaid += "    Court --> Success\n"
    mermaid += "    Success([Proposal Approved])\n\n"

    mermaid += "    Bankruptcy([Deemed Bankruptcy])\n\n"

    # Parallel stay of proceedings
    mermaid += "    NOI -.-> Stay\n"
    mermaid += "    Stay[Automatic Stay of Proceedings<br/>BIA s. 69]\n"
    mermaid += "    Stay -.-> Protected\n"
    mermaid += "    Protected[Creditors Cannot Take Action]\n\n"

    # Styling
    mermaid += "    style Start fill:#e1f5ff\n"
    mermaid += "    style Success fill:#c8e6c9\n"
    mermaid += "    style Bankruptcy fill:#ffcdd2\n"
    mermaid += "    style Stay fill:#fff9c4\n"

    return mermaid, results


def generate_trustee_duties():
    """Generate trustee duties workflow diagram"""

    mermaid = """flowchart TD
    Appointment([Trustee Appointed]) --> Duties

    Duties[Core Trustee Duties<br/>BIA s. 13-25]
    Duties --> D1
    Duties --> D2
    Duties --> D3
    Duties --> D4

    D1[Take Possession of Assets<br/>BIA s. 16]
    D2[File Statement of Affairs<br/>Within 5 days - BIA s. 49]
    D3[Call First Meeting of Creditors<br/>Within 21 days - BIA s. 102]
    D4[Distribute to Creditors<br/>BIA s. 136-147]

    D1 --> Report
    D2 --> Report
    D3 --> Report
    D4 --> Report

    Report[Report to OSB<br/>Directives 6R7, 16R]

    style Appointment fill:#e1f5ff
    style Report fill:#fff9c4
    style D1 fill:#c8e6c9
    style D2 fill:#c8e6c9
    style D3 fill:#c8e6c9
    style D4 fill:#c8e6c9
"""
    return mermaid, []


def generate_stay_of_proceedings():
    """Generate stay of proceedings diagram"""

    mermaid = """flowchart TD
    Filing([Bankruptcy/Proposal Filed]) --> Stay

    Stay[Automatic Stay Begins<br/>BIA s. 69]
    Stay --> Protected

    Protected[Creditors CANNOT:]
    Protected --> P1[Start legal proceedings]
    Protected --> P2[Continue existing proceedings]
    Protected --> P3[Seize assets]
    Protected --> P4[Continue enforcement]

    Stay --> Exceptions

    Exceptions[Exceptions:<br/>NOT stayed]
    Exceptions --> E1[Criminal proceedings]
    Exceptions --> E2[Child/spousal support]
    Exceptions --> E3[Secured creditors<br/>with court permission]

    Stay --> Lift

    Lift{Creditor applies<br/>to lift stay}
    Lift -->|Granted| CanAct[Creditor can proceed]
    Lift -->|Denied| MustWait[Must wait until discharge]

    style Filing fill:#e1f5ff
    style Stay fill:#c8e6c9
    style Protected fill:#fff9c4
    style CanAct fill:#ffcdd2
    style MustWait fill:#c8e6c9
"""
    return mermaid, []


def render_diagram(mermaid_code, output_filename="diagram.png"):
    """Render Mermaid code to PNG using mermaid-cli"""

    # Write Mermaid code to temp file
    with tempfile.NamedTemporaryFile(suffix='.mmd', mode='w', delete=False) as f:
        f.write(mermaid_code)
        temp_path = f.name

    # Generate PNG
    try:
        subprocess.run(
            ["mmdc", "-i", temp_path, "-o", output_filename, "-b", "white"],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ Diagram generated: {output_filename}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error rendering diagram:")
        print(e.stderr)
        return False
    except FileNotFoundError:
        print("❌ mermaid-cli not found!")
        print("Install with: npm install -g @mermaid-js/mermaid-cli")
        return False


def open_diagram(filename):
    """Open diagram in default viewer"""
    try:
        # macOS
        subprocess.run(["open", filename])
    except:
        try:
            # Linux
            subprocess.run(["xdg-open", filename])
        except:
            try:
                # Windows
                subprocess.run(["start", filename], shell=True)
            except:
                print(f"Please open {filename} manually")


def main():
    if len(sys.argv) < 2:
        print("Usage: python quick_diagram.py <topic>")
        print("\nAvailable topics:")
        print("  - Division I NOI timeline")
        print("  - Trustee duties")
        print("  - Stay of proceedings")
        sys.exit(1)

    topic = sys.argv[1].lower()

    # Generate appropriate diagram
    if "noi" in topic or "division i" in topic or "proposal" in topic:
        print("📊 Generating Division I NOI Timeline...")
        mermaid_code, entities = generate_division_i_noi_timeline()
        output_file = "division_i_noi_timeline.png"

    elif "trustee" in topic or "duties" in topic:
        print("📊 Generating Trustee Duties Workflow...")
        mermaid_code, entities = generate_trustee_duties()
        output_file = "trustee_duties.png"

    elif "stay" in topic or "proceedings" in topic:
        print("📊 Generating Stay of Proceedings Diagram...")
        mermaid_code, entities = generate_stay_of_proceedings()
        output_file = "stay_of_proceedings.png"

    else:
        print(f"❌ Unknown topic: {topic}")
        print("Try: 'Division I NOI timeline', 'Trustee duties', or 'Stay of proceedings'")
        sys.exit(1)

    # Save Mermaid code
    mermaid_file = output_file.replace('.png', '.mmd')
    with open(mermaid_file, 'w') as f:
        f.write(mermaid_code)
    print(f"💾 Mermaid code saved: {mermaid_file}")

    # Render diagram
    if render_diagram(mermaid_code, output_file):
        print(f"🎨 Opening diagram...")
        open_diagram(output_file)
        print("\n" + "="*60)
        print("Mermaid Code:")
        print("="*60)
        print(mermaid_code)
        print("="*60)
        print("\n✅ Done! You can also paste this code into https://mermaid.live")
    else:
        print("\n⚠️  Rendering failed, but you can still use the code manually:")
        print(f"\n1. Copy code from: {mermaid_file}")
        print("2. Paste into: https://mermaid.live")
        print("3. Export as PNG/SVG")


if __name__ == "__main__":
    main()
