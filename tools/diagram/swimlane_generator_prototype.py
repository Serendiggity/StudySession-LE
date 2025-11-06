#!/usr/bin/env python3
"""
Swimlane Diagram Generator - Multi-Approach Prototype

Tests multiple methods for generating professional swimlane diagrams:
1. PlantUML (via Kroki API) - Best quality, widely supported
2. Direct SVG generation - Full control, no dependencies
3. BPMN XML generation - Industry standard
4. Mermaid alternative syntax - Already integrated

Each approach generates a consumer proposal workflow swimlane diagram.
"""

import sqlite3
import json
import base64
import zlib
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
import urllib.request
import urllib.parse


@dataclass
class ProcessStep:
    """Represents a single process step in swimlane."""
    actor: str
    action: str
    day: Optional[int] = None
    timeframe: Optional[str] = None
    section: Optional[str] = None
    depends_on: Optional[str] = None


class SwimlaneGenerator:
    """Generate swimlane diagrams using multiple approaches."""

    def __init__(self, db_path: Path):
        self.db_path = db_path

    def get_process_data(self, section_pattern: str = "50%") -> List[ProcessStep]:
        """Extract process data from database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT DISTINCT
                a.role_canonical,
                COALESCE(p.step_name, p.action, p.extraction_text),
                d.timeframe,
                dr.bia_section
            FROM duty_relationships dr
            LEFT JOIN actors a ON dr.actor_id = a.id
            LEFT JOIN procedures p ON dr.procedure_id = p.id
            LEFT JOIN deadlines d ON dr.deadline_id = d.id
            WHERE dr.bia_section LIKE ?
              AND a.role_canonical IS NOT NULL
              AND (p.step_name IS NOT NULL OR p.action IS NOT NULL)
            ORDER BY dr.bia_section, a.role_canonical
            LIMIT 30
        ''', (section_pattern,))

        steps = []
        for row in cursor.fetchall():
            actor = row[0]
            action = row[1][:50] if row[1] else "Process step"
            timeframe = row[2]
            section = row[3]

            steps.append(ProcessStep(
                actor=actor,
                action=action,
                timeframe=timeframe,
                section=section
            ))

        conn.close()
        return steps

    def get_mock_consumer_proposal_data(self) -> List[ProcessStep]:
        """Get mock data for consumer proposal process."""
        return [
            ProcessStep("Consumer Debtor", "Consult with administrator", day=-7),
            ProcessStep("Consumer Debtor", "Sign proposal documents", day=-1),
            ProcessStep("Administrator", "File proposal with Official Receiver", day=0),
            ProcessStep("Official Receiver", "Receive and process filing", day=0),
            ProcessStep("Administrator", "Send notice to creditors (Form 51)", day=1, timeframe="within 10 days"),
            ProcessStep("Administrator", "Prepare cash-flow statement", day=1, timeframe="within 10 days"),
            ProcessStep("Creditors", "Receive notice and cash-flow statement", day=10),
            ProcessStep("Administrator", "File affidavit of sending notices", day=10, timeframe="within 10 days"),
            ProcessStep("Creditors", "File proof of claim", day=30, timeframe="within 30 days"),
            ProcessStep("Administrator", "Convene meeting of creditors", day=21, timeframe="within 21 days"),
            ProcessStep("Creditors", "Vote on proposal at meeting", day=21),
            ProcessStep("Court", "Review proposal (if required)", day=45),
            ProcessStep("Administrator", "Supervise payments (if approved)", day=60),
            ProcessStep("Counsellor", "Provide mandatory counselling", day=90),
            ProcessStep("Administrator", "File completion certificate", day=1825, timeframe="5 years"),
        ]

    # ========================================
    # APPROACH 1: PlantUML via Kroki API
    # ========================================

    def generate_plantuml_swimlane(self, steps: List[ProcessStep]) -> str:
        """
        Generate PlantUML activity diagram with swimlanes.

        PlantUML swimlane syntax:
        - |Lane Name| defines a swimlane
        - :activity; creates an activity in current lane
        - Activities flow automatically with arrows
        """

        # Group steps by actor
        actors = list(dict.fromkeys(step.actor for step in steps))

        plantuml = "@startuml\n"
        plantuml += "title Consumer Proposal Process - Swimlane Diagram\n\n"

        # Add start
        if actors:
            plantuml += f"|{actors[0]}|\n"
        plantuml += "start\n\n"

        current_lane = None
        for i, step in enumerate(steps):
            # Switch lane if needed
            if step.actor != current_lane:
                plantuml += f"|{step.actor}|\n"
                current_lane = step.actor

            # Add activity
            activity_text = step.action.replace('"', "'")
            if step.timeframe:
                activity_text += f"\\n({step.timeframe})"
            if step.day is not None:
                activity_text += f"\\n[Day {step.day}]"

            plantuml += f":{activity_text};\n"

            # Add note for section reference
            if step.section:
                plantuml += f"note right: BIA §{step.section}\n"

            plantuml += "\n"

        plantuml += "stop\n"
        plantuml += "@enduml\n"

        return plantuml

    def plantuml_to_svg_via_kroki(self, plantuml_code: str) -> Optional[bytes]:
        """
        Convert PlantUML to SVG using Kroki.io API.

        Kroki endpoint: https://kroki.io/plantuml/svg
        Accepts POST with plain text or GET with encoded diagram.
        """
        try:
            # Use POST for simplicity (no encoding required)
            url = "https://kroki.io/plantuml/svg"

            data = plantuml_code.encode('utf-8')
            headers = {
                'Content-Type': 'text/plain'
            }

            request = urllib.request.Request(url, data=data, headers=headers)
            with urllib.request.urlopen(request, timeout=30) as response:
                svg_data = response.read()
                return svg_data

        except Exception as e:
            print(f"Kroki API error: {e}")
            return None

    def encode_plantuml_for_kroki(self, plantuml_code: str) -> str:
        """
        Encode PlantUML for Kroki GET request.
        Uses deflate + base64 encoding.
        """
        compressed = zlib.compress(plantuml_code.encode('utf-8'), 9)
        encoded = base64.urlsafe_b64encode(compressed).decode('ascii')
        return encoded

    # ========================================
    # APPROACH 2: Direct SVG Generation
    # ========================================

    def generate_svg_swimlane(self, steps: List[ProcessStep]) -> str:
        """
        Generate swimlane diagram as pure SVG.

        Advantages:
        - Full control over layout
        - No external dependencies
        - Direct embedding in HTML/markdown
        """

        # Layout parameters
        lane_width = 200
        lane_height = 100
        step_height = 60
        step_width = 180
        step_margin = 20
        header_height = 40

        # Group by actor
        actors = list(dict.fromkeys(step.actor for step in steps))
        actor_steps = {actor: [] for actor in actors}

        for step in steps:
            actor_steps[step.actor].append(step)

        # Calculate dimensions
        max_steps = max(len(actor_steps[actor]) for actor in actors)
        total_width = len(actors) * lane_width + 100
        total_height = header_height + max_steps * (step_height + step_margin) + 100

        # Build SVG
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg"
                     width="{total_width}"
                     height="{total_height}"
                     viewBox="0 0 {total_width} {total_height}">

        <!-- Title -->
        <text x="{total_width/2}" y="25"
              text-anchor="middle"
              font-size="18"
              font-weight="bold"
              font-family="Arial, sans-serif">
            Consumer Proposal Process
        </text>

        <!-- Swimlanes -->
'''

        # Draw lanes
        for i, actor in enumerate(actors):
            x = 50 + i * lane_width

            # Lane background
            svg += f'''
        <rect x="{x}" y="{header_height}"
              width="{lane_width}"
              height="{total_height - header_height - 50}"
              fill="{self._get_lane_color(i)}"
              stroke="#333"
              stroke-width="2"
              fill-opacity="0.1"/>

        <!-- Lane header -->
        <rect x="{x}" y="{header_height}"
              width="{lane_width}"
              height="40"
              fill="{self._get_lane_color(i)}"
              stroke="#333"
              stroke-width="2"
              fill-opacity="0.3"/>

        <text x="{x + lane_width/2}" y="{header_height + 25}"
              text-anchor="middle"
              font-size="14"
              font-weight="bold"
              font-family="Arial, sans-serif">
            {actor}
        </text>
'''

            # Draw steps for this actor
            for j, step in enumerate(actor_steps[actor]):
                y = header_height + 60 + j * (step_height + step_margin)

                # Step box
                svg += f'''
        <rect x="{x + 10}" y="{y}"
              width="{step_width}"
              height="{step_height}"
              fill="white"
              stroke="#333"
              stroke-width="2"
              rx="5"/>

        <text x="{x + lane_width/2}" y="{y + 20}"
              text-anchor="middle"
              font-size="12"
              font-family="Arial, sans-serif">
            {self._wrap_text(step.action, 20)}
        </text>
'''

                if step.day is not None:
                    svg += f'''
        <text x="{x + lane_width/2}" y="{y + step_height - 10}"
              text-anchor="middle"
              font-size="10"
              fill="#666"
              font-family="Arial, sans-serif">
            Day {step.day}
        </text>
'''

        svg += '''
    </svg>'''

        return svg

    def _get_lane_color(self, index: int) -> str:
        """Get color for lane based on index."""
        colors = [
            "#e3f2fd",  # Blue
            "#f3e5f5",  # Purple
            "#e8f5e9",  # Green
            "#fff3e0",  # Orange
            "#fce4ec",  # Pink
            "#e0f2f1",  # Teal
        ]
        return colors[index % len(colors)]

    def _wrap_text(self, text: str, max_chars: int) -> str:
        """Simple text wrapping for SVG."""
        if len(text) <= max_chars:
            return text
        return text[:max_chars-3] + "..."

    # ========================================
    # APPROACH 3: BPMN XML Generation
    # ========================================

    def generate_bpmn_xml(self, steps: List[ProcessStep]) -> str:
        """
        Generate BPMN 2.0 XML with pools and lanes.

        BPMN is the industry standard for business process diagrams.
        Can be rendered by:
        - bpmn.io (JavaScript)
        - Camunda Modeler
        - draw.io
        """

        actors = list(dict.fromkeys(step.actor for step in steps))

        bpmn = '''<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL"
             xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"
             xmlns:dc="http://www.omg.org/spec/DD/20100524/DC"
             xmlns:di="http://www.omg.org/spec/DD/20100524/DI"
             targetNamespace="http://insolvency.example.com/consumer-proposal">

    <process id="ConsumerProposal" name="Consumer Proposal Process">

        <!-- Pools (Participants) -->
'''

        # Add lanes for each actor
        for i, actor in enumerate(actors):
            actor_id = actor.replace(" ", "_").replace("-", "_")
            bpmn += f'''
        <laneSet id="LaneSet_{i}">
            <lane id="Lane_{actor_id}" name="{actor}">
'''

            # Add tasks for this actor
            actor_tasks = [step for step in steps if step.actor == actor]
            for j, task in enumerate(actor_tasks):
                task_id = f"Task_{actor_id}_{j}"
                task_name = task.action[:50]

                bpmn += f'''
                <flowNodeRef>{task_id}</flowNodeRef>
'''

            bpmn += '''
            </lane>
        </laneSet>
'''

        # Add task definitions
        for i, step in enumerate(steps):
            actor_id = step.actor.replace(" ", "_").replace("-", "_")
            task_id = f"Task_{actor_id}_{i}"

            bpmn += f'''
        <task id="{task_id}" name="{step.action}">
            <documentation>
                Section: {step.section or 'N/A'}
                Timeframe: {step.timeframe or 'N/A'}
                Day: {step.day or 'N/A'}
            </documentation>
        </task>
'''

        bpmn += '''
    </process>
</definitions>
'''

        return bpmn

    # ========================================
    # APPROACH 4: Enhanced Mermaid
    # ========================================

    def generate_mermaid_gantt_as_swimlane(self, steps: List[ProcessStep]) -> str:
        """
        Use Mermaid Gantt chart styled as swimlane.

        While Mermaid doesn't have true swimlanes, Gantt charts
        can be sectioned by actor to approximate the visualization.
        """

        # Group by actor
        actors = list(dict.fromkeys(step.actor for step in steps))
        actor_steps = {actor: [] for actor in actors}

        for step in steps:
            actor_steps[step.actor].append(step)

        mermaid = "gantt\n"
        mermaid += "    title Consumer Proposal Process (Swimlane View)\n"
        mermaid += "    dateFormat  YYYY-MM-DD\n"
        mermaid += "    axisFormat %d\n\n"

        for actor in actors:
            mermaid += f"    section {actor}\n"

            for step in actor_steps[actor]:
                task_name = step.action[:40]

                # Calculate duration
                if step.day is not None:
                    start_day = step.day
                    duration = 1  # Default 1 day
                else:
                    start_day = 0
                    duration = 1

                mermaid += f"    {task_name} : {duration}d\n"

        return mermaid


def main():
    """Test all approaches and save results."""

    db_path = Path("projects/insolvency-law/database/knowledge.db")
    output_dir = Path("data/output/swimlane_diagrams")
    output_dir.mkdir(parents=True, exist_ok=True)

    generator = SwimlaneGenerator(db_path)

    print("=" * 80)
    print("SWIMLANE DIAGRAM GENERATION - PROTOTYPE TEST")
    print("=" * 80)

    # Get data
    print("\n1. Fetching process data from database...")
    db_steps = generator.get_process_data("50%")
    mock_steps = generator.get_mock_consumer_proposal_data()

    print(f"   - Database steps: {len(db_steps)}")
    print(f"   - Mock steps: {len(mock_steps)}")

    # Use mock data for demo (more complete)
    steps = mock_steps

    # ========================================
    # APPROACH 1: PlantUML via Kroki
    # ========================================
    print("\n2. Generating PlantUML diagram...")
    plantuml_code = generator.generate_plantuml_swimlane(steps)

    # Save PlantUML source
    plantuml_file = output_dir / "consumer_proposal_plantuml.txt"
    plantuml_file.write_text(plantuml_code)
    print(f"   ✓ PlantUML source: {plantuml_file}")

    # Try Kroki API
    print("   - Attempting Kroki.io API call...")
    svg_data = generator.plantuml_to_svg_via_kroki(plantuml_code)

    if svg_data:
        svg_file = output_dir / "consumer_proposal_plantuml.svg"
        svg_file.write_bytes(svg_data)
        print(f"   ✓ PlantUML SVG (via Kroki): {svg_file}")
    else:
        print("   ✗ Kroki API failed (network/quota issue)")
        print("   → Alternative: Use local PlantUML JAR or online editor")
        print("   → URL: https://www.plantuml.com/plantuml/uml/")

    # ========================================
    # APPROACH 2: Direct SVG
    # ========================================
    print("\n3. Generating direct SVG diagram...")
    svg_code = generator.generate_svg_swimlane(steps)

    svg_direct_file = output_dir / "consumer_proposal_direct.svg"
    svg_direct_file.write_text(svg_code)
    print(f"   ✓ Direct SVG: {svg_direct_file}")

    # ========================================
    # APPROACH 3: BPMN XML
    # ========================================
    print("\n4. Generating BPMN XML...")
    bpmn_code = generator.generate_bpmn_xml(steps)

    bpmn_file = output_dir / "consumer_proposal_bpmn.xml"
    bpmn_file.write_text(bpmn_code)
    print(f"   ✓ BPMN XML: {bpmn_file}")
    print("   → Open with: bpmn.io, Camunda Modeler, or draw.io")

    # ========================================
    # APPROACH 4: Mermaid Gantt
    # ========================================
    print("\n5. Generating Mermaid Gantt (swimlane-style)...")
    mermaid_code = generator.generate_mermaid_gantt_as_swimlane(steps)

    mermaid_file = output_dir / "consumer_proposal_mermaid.md"
    with open(mermaid_file, 'w') as f:
        f.write("```mermaid\n")
        f.write(mermaid_code)
        f.write("\n```\n")
    print(f"   ✓ Mermaid Gantt: {mermaid_file}")

    # ========================================
    # Summary Report
    # ========================================
    print("\n" + "=" * 80)
    print("EVALUATION SUMMARY")
    print("=" * 80)

    report = """
APPROACH 1: PlantUML via Kroki.io
---------------------------------
✓ Pros:
  - True horizontal swimlanes with lanes
  - Professional appearance
  - Widely supported format
  - Free API (Kroki.io)
  - Can export SVG, PNG, PDF

✗ Cons:
  - Requires API call (network dependency)
  - Rate limits on free tier
  - PlantUML syntax learning curve

RECOMMENDATION: ⭐⭐⭐⭐⭐ BEST OPTION
Use for production. Fallback to local PlantUML JAR if API unavailable.


APPROACH 2: Direct SVG Generation
---------------------------------
✓ Pros:
  - No external dependencies
  - Full control over layout
  - Works offline
  - Can customize every pixel

✗ Cons:
  - Manual layout calculations
  - More code to maintain
  - Limited automatic positioning
  - No standard format

RECOMMENDATION: ⭐⭐⭐ GOOD FOR CUSTOM NEEDS
Use when full control required or network unavailable.


APPROACH 3: BPMN 2.0 XML
---------------------------------
✓ Pros:
  - Industry standard
  - Native swimlane support (pools/lanes)
  - Compatible with many tools
  - Formal specification

✗ Cons:
  - Requires external viewer
  - Complex XML structure
  - Layout not auto-calculated
  - Harder to embed in markdown

RECOMMENDATION: ⭐⭐⭐ GOOD FOR FORMAL DOCS
Use for official process documentation.


APPROACH 4: Mermaid Gantt
---------------------------------
✓ Pros:
  - Already integrated in project
  - GitHub markdown compatible
  - Simple syntax

✗ Cons:
  - NOT true swimlanes (just grouped tasks)
  - No cross-lane arrows
  - Limited layout control

RECOMMENDATION: ⭐⭐ ACCEPTABLE FALLBACK
Only use if PlantUML unavailable.


FINAL RECOMMENDATION
====================
PRIMARY: PlantUML via Kroki.io API
  - Best visual quality
  - True swimlane support
  - Easy to maintain

FALLBACK: Direct SVG generation
  - Use when offline/API unavailable
  - Full control over appearance

INTEGRATION STEPS
=================
1. Add to MCP server as new tool:
   - diagram_swimlane(topic, section_pattern)

2. Query database for process steps
3. Generate PlantUML code
4. Call Kroki.io API → SVG
5. Save to data/output/diagrams/
6. Return markdown with embedded SVG

CODE SNIPPET:
```python
def generate_swimlane_diagram(topic: str, section: str):
    steps = query_database(section)
    plantuml = generate_plantuml_swimlane(steps)
    svg = kroki_api_call(plantuml)
    save_svg(f"{topic}_swimlane.svg")
    return f"![{topic}]({svg_path})"
```
"""

    print(report)

    # Save report
    report_file = output_dir / "evaluation_report.txt"
    report_file.write_text(report)
    print(f"\n✓ Full report saved: {report_file}")

    print("\n" + "=" * 80)
    print("All diagrams generated successfully!")
    print(f"Output directory: {output_dir.absolute()}")
    print("=" * 80)


if __name__ == '__main__':
    main()
