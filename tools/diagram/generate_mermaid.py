#!/usr/bin/env python3
"""
Mermaid Diagram Generator

Generates Mermaid diagrams from the knowledge base for visualization in VS Code.

Usage:
    python tools/diagram/generate_mermaid.py --topic "Division I NOI" --type flowchart
    python tools/diagram/generate_mermaid.py --topic "Trustee Duties" --type swimlane
    python tools/diagram/generate_mermaid.py --section 50.4 --type duty-chain
"""

import argparse
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class MermaidGenerator:
    """Generate Mermaid diagrams from knowledge base."""

    def __init__(self, db_path: Path):
        """Initialize generator with database connection."""
        self.db = sqlite3.connect(db_path)
        self.db.row_factory = sqlite3.Row

    def generate_flowchart(self, section_pattern: str, title: str) -> str:
        """
        Generate process flowchart diagram.

        Shows step-by-step process flow with actors, procedures, and decisions.
        """
        # Get duties for this section
        cursor = self.db.execute('''
            SELECT actor, procedure, deadline, consequence, modal_verb, bia_section
            FROM v_complete_duties
            WHERE bia_section LIKE ?
              AND procedure IS NOT NULL
            ORDER BY bia_section
        ''', (section_pattern,))

        duties = cursor.fetchall()

        # Build Mermaid flowchart
        mermaid = f"# {title}\n\n"
        mermaid += "```mermaid\n"
        mermaid += "flowchart TD\n"
        mermaid += f"    START([{title}])\n\n"

        node_id = 1
        for duty in duties:
            actor = duty['actor'] or "Party"
            procedure = (duty['procedure'] or "")[:50]  # Truncate long text
            deadline = duty['deadline']
            consequence = duty['consequence']
            modal = duty['modal_verb'] or ""

            # Create procedure node
            proc_id = f"P{node_id}"
            mermaid += f"    {proc_id}[\"{actor}: {procedure}\"]\n"

            # Add deadline if exists
            if deadline:
                deadline_id = f"D{node_id}"
                mermaid += f"    {deadline_id}{{\"{deadline}\"}}\n"
                mermaid += f"    {proc_id} --> {deadline_id}\n"

            # Add consequence if exists
            if consequence:
                cons_id = f"C{node_id}"
                mermaid += f"    {cons_id}[(\"{consequence}\")]\n"
                if deadline:
                    mermaid += f"    {deadline_id} -.\"if not met\".-> {cons_id}\n"
                else:
                    mermaid += f"    {proc_id} -.-> {cons_id}\n"

            mermaid += "\n"
            node_id += 1

        mermaid += "```\n"
        return mermaid

    def generate_swimlane(self, section_pattern: str, title: str) -> str:
        """
        Generate actor swimlane diagram.

        Shows who does what in parallel lanes.
        """
        # Get duties grouped by actor
        cursor = self.db.execute('''
            SELECT actor, procedure, deadline, bia_section
            FROM v_complete_duties
            WHERE bia_section LIKE ?
              AND actor IS NOT NULL
              AND procedure IS NOT NULL
            ORDER BY actor, bia_section
        ''', (section_pattern,))

        duties = cursor.fetchall()

        # Group by actor
        actors = {}
        for duty in duties:
            actor = duty['actor']
            if actor not in actors:
                actors[actor] = []
            actors[actor].append(duty)

        # Build Mermaid swimlane (using graph with subgraphs)
        mermaid = f"# {title} - Swimlane Diagram\n\n"
        mermaid += "```mermaid\n"
        mermaid += "graph TD\n\n"

        for actor, actor_duties in actors.items():
            # Create subgraph for each actor
            actor_id = actor.replace(' ', '_').replace('-', '_')[:20]
            mermaid += f"    subgraph {actor_id}[\"{actor}\"]\n"

            for i, duty in enumerate(actor_duties):
                proc = (duty['procedure'] or "")[:40]
                deadline = duty['deadline'] or ""
                node_id = f"{actor_id}_{i}"

                if deadline:
                    mermaid += f"        {node_id}[\"{proc}<br/>{deadline}\"]\n"
                else:
                    mermaid += f"        {node_id}[\"{proc}\"]\n"

            mermaid += "    end\n\n"

        mermaid += "```\n"
        return mermaid

    def generate_duty_chain(self, section_pattern: str, title: str) -> str:
        """
        Generate duty chain diagram.

        Shows: Actor → Duty → Deadline → Consequence relationships.
        """
        cursor = self.db.execute('''
            SELECT actor, procedure, deadline, consequence, modal_verb, bia_section
            FROM v_complete_duties
            WHERE bia_section LIKE ?
            ORDER BY actor, bia_section
        ''', (section_pattern,))

        duties = cursor.fetchall()

        mermaid = f"# {title} - Duty Chain\n\n"
        mermaid += "```mermaid\n"
        mermaid += "graph LR\n\n"

        node_id = 1
        prev_actor = None

        for duty in duties:
            actor = duty['actor']
            procedure = duty['procedure']
            deadline = duty['deadline']
            consequence = duty['consequence']
            modal = duty['modal_verb'] or ""

            # Actor node (reuse if same actor)
            if actor and actor != prev_actor:
                actor_id = f"A{node_id}"
                mermaid += f"    {actor_id}[{actor}]\n"
                prev_actor = actor
                node_id += 1
            else:
                actor_id = f"A{node_id - 1}" if prev_actor else f"A{node_id}"

            # Procedure node
            if procedure:
                proc_id = f"P{node_id}"
                proc_text = procedure[:30]
                mermaid += f"    {proc_id}[{proc_text}]\n"
                mermaid += f"    {actor_id} --\"{modal}\"--> {proc_id}\n"
                node_id += 1

                # Deadline node
                if deadline:
                    dead_id = f"D{node_id}"
                    mermaid += f"    {dead_id}{{{deadline}}}\n"
                    mermaid += f"    {proc_id} --> {dead_id}\n"
                    node_id += 1

                    # Consequence node
                    if consequence:
                        cons_id = f"C{node_id}"
                        mermaid += f"    {cons_id}[({consequence})]\n"
                        mermaid += f"    {dead_id} -.\"if missed\".-> {cons_id}\n"
                        node_id += 1

            mermaid += "\n"

        mermaid += "```\n"
        return mermaid

    def generate_erd(self, title: str = "Knowledge Base Schema") -> str:
        """
        Generate entity relationship diagram showing database schema.
        """
        mermaid = f"# {title}\n\n"
        mermaid += "```mermaid\n"
        mermaid += "erDiagram\n\n"

        # Define entities and relationships
        mermaid += "    ACTORS ||--o{ DUTY_RELATIONSHIPS : involved_in\n"
        mermaid += "    PROCEDURES ||--o{ DUTY_RELATIONSHIPS : has\n"
        mermaid += "    DEADLINES ||--o{ DUTY_RELATIONSHIPS : constrained_by\n"
        mermaid += "    CONSEQUENCES ||--o{ DUTY_RELATIONSHIPS : leads_to\n"
        mermaid += "    PROCEDURES ||--o{ DOCUMENT_REQUIREMENTS : requires\n"
        mermaid += "    DOCUMENTS ||--o{ DOCUMENT_REQUIREMENTS : needed_for\n"
        mermaid += "    CONSEQUENCES ||--o{ TRIGGER_RELATIONSHIPS : triggered_by\n\n"

        # Entity definitions
        mermaid += "    ACTORS {\n"
        mermaid += "        int id\n"
        mermaid += "        string role_canonical\n"
        mermaid += "        string extraction_text\n"
        mermaid += "    }\n\n"

        mermaid += "    PROCEDURES {\n"
        mermaid += "        int id\n"
        mermaid += "        string extraction_text\n"
        mermaid += "        string step_name\n"
        mermaid += "    }\n\n"

        mermaid += "    DUTY_RELATIONSHIPS {\n"
        mermaid += "        int id\n"
        mermaid += "        int actor_id\n"
        mermaid += "        int procedure_id\n"
        mermaid += "        int deadline_id\n"
        mermaid += "        int consequence_id\n"
        mermaid += "        string duty_type\n"
        mermaid += "        string modal_verb\n"
        mermaid += "    }\n\n"

        mermaid += "```\n"
        return mermaid

    def generate_timeline(self, section_pattern: str, title: str) -> str:
        """
        Generate Gantt timeline showing deadlines and milestones.
        """
        cursor = self.db.execute('''
            SELECT procedure, deadline, bia_section
            FROM v_complete_duties
            WHERE bia_section LIKE ?
              AND deadline IS NOT NULL
            ORDER BY bia_section
        ''', (section_pattern,))

        duties = cursor.fetchall()

        mermaid = f"# {title} - Timeline\n\n"
        mermaid += "```mermaid\n"
        mermaid += "gantt\n"
        mermaid += f"    title {title}\n"
        mermaid += "    dateFormat  YYYY-MM-DD\n"
        mermaid += "    section Process\n\n"

        # For Gantt charts, we need to map deadlines to actual dates
        # Since we don't have real dates, we'll use relative positioning
        base_date = datetime.now()

        for i, duty in enumerate(duties):
            proc = (duty['procedure'] or "Step")[:30]
            deadline_text = duty['deadline'] or ""

            # Simple mapping: extract days if mentioned
            days = 0
            if 'day' in deadline_text.lower():
                try:
                    # Extract number from deadline text
                    import re
                    match = re.search(r'(\d+)\s*day', deadline_text, re.IGNORECASE)
                    if match:
                        days = int(match.group(1))
                except:
                    days = (i + 1) * 5  # Default spacing

            if days == 0:
                days = (i + 1) * 5

            start_day = i * 5
            end_day = start_day + days

            mermaid += f"    {proc} :task{i}, {base_date.strftime('%Y-%m-%d')}, {days}d\n"

        mermaid += "```\n"
        return mermaid

    def save_diagram(self, mermaid_code: str, output_path: Path):
        """Save Mermaid diagram to markdown file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            f.write(mermaid_code)

        print(f"✅ Diagram saved to: {output_path}")

    def close(self):
        """Close database connection."""
        self.db.close()


def main():
    """Main entry point for diagram generation."""
    parser = argparse.ArgumentParser(description='Generate Mermaid diagrams from knowledge base')

    parser.add_argument('--db', default='projects/insolvency-law/database/knowledge.db',
                        help='Path to database file')
    parser.add_argument('--topic', help='Topic/title for diagram')
    parser.add_argument('--section', help='BIA section pattern (e.g., "50.4" or "50%%")')
    parser.add_argument('--type', required=True,
                        choices=['flowchart', 'swimlane', 'duty-chain', 'erd', 'timeline'],
                        help='Diagram type to generate')
    parser.add_argument('--output', help='Output file path (default: data/output/diagrams/{topic}.md)')

    args = parser.parse_args()

    # Default section pattern
    section_pattern = args.section or '50.4%'  # Default to Section 50.4

    # Default topic
    topic = args.topic or f"BIA Section {section_pattern.rstrip('%')}"

    # Initialize generator
    generator = MermaidGenerator(Path(args.db))

    try:
        # Generate diagram based on type
        if args.type == 'flowchart':
            mermaid = generator.generate_flowchart(section_pattern, topic)
        elif args.type == 'swimlane':
            mermaid = generator.generate_swimlane(section_pattern, topic)
        elif args.type == 'duty-chain':
            mermaid = generator.generate_duty_chain(section_pattern, topic)
        elif args.type == 'erd':
            mermaid = generator.generate_erd(topic)
        elif args.type == 'timeline':
            mermaid = generator.generate_timeline(section_pattern, topic)

        # Determine output path
        if args.output:
            output_path = Path(args.output)
        else:
            filename = topic.lower().replace(' ', '_').replace('/', '_')
            output_path = Path(f'data/output/diagrams/{filename}_{args.type}.md')

        # Save diagram
        generator.save_diagram(mermaid, output_path)

        print(f"\n📊 Generated {args.type} diagram for: {topic}")
        print(f"📍 Open in VS Code and use Mermaid preview extension to view")

    finally:
        generator.close()


if __name__ == '__main__':
    main()
