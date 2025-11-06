#!/usr/bin/env python3
"""
Mermaid Diagram Generator

Automatically generates Mermaid diagrams from database content:
- Timeline diagrams (Gantt charts) from deadlines
- Process flowcharts from procedures
- Entity relationship diagrams
- Comparison tables
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
import re
import logging

logger = logging.getLogger(__name__)


@dataclass
class DiagramConfig:
    """Configuration for diagram generation."""
    title: str
    diagram_type: str  # 'gantt', 'flowchart', 'erDiagram', 'classDiagram'
    orientation: str = 'TD'  # Top-Down, Left-Right, etc.
    theme: str = 'default'


class MermaidDiagramGenerator:
    """
    Generates Mermaid diagrams from database content.

    Mermaid syntax reference:
    - Flowchart: flowchart TD
    - Gantt: gantt
    - ER Diagram: erDiagram
    - Class Diagram: classDiagram
    """

    def __init__(self, db_path: Path):
        """
        Initialize diagram generator.

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path

    def _sanitize_text(self, text: str, max_length: int = 60) -> str:
        """
        Sanitize text for Mermaid diagram labels.

        Args:
            text: Text to sanitize
            max_length: Maximum label length

        Returns:
            Sanitized text
        """
        # Remove special characters that break Mermaid
        text = re.sub(r'["\[\]{}|\\]', '', text)

        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length-3] + '...'

        return text.strip()

    def _get_deadlines(self, topic: str) -> List[Dict]:
        """Get deadlines for topic from database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Check if deadlines table exists
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='deadlines'
            """)

            if not cursor.fetchone():
                return []

            # Search for relevant deadlines
            cursor.execute("""
                SELECT
                    timeframe,
                    extraction_text,
                    section_number,
                    section_title
                FROM deadlines
                WHERE extraction_text LIKE ?
                ORDER BY id
            """, (f'%{topic}%',))

            rows = cursor.fetchall()

            deadlines = []
            for row in rows:
                deadlines.append({
                    'timeframe': row[0] or '',
                    'text': row[1] or '',
                    'section': row[2] or '',
                    'title': row[3] or ''
                })

            return deadlines

        finally:
            conn.close()

    def _get_procedures(self, topic: str) -> List[Dict]:
        """Get procedures for topic from database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='procedures'
            """)

            if not cursor.fetchone():
                return []

            cursor.execute("""
                SELECT
                    step_name,
                    step_order,
                    action,
                    extraction_text,
                    section_number
                FROM procedures
                WHERE extraction_text LIKE ?
                ORDER BY step_order, id
            """, (f'%{topic}%',))

            rows = cursor.fetchall()

            procedures = []
            for row in rows:
                procedures.append({
                    'name': row[0] or '',
                    'order': row[1] or 0,
                    'action': row[2] or '',
                    'text': row[3] or '',
                    'section': row[4] or ''
                })

            return procedures

        finally:
            conn.close()

    def _get_actors(self, topic: str) -> List[Dict]:
        """Get actors for topic from database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='actors'
            """)

            if not cursor.fetchone():
                return []

            cursor.execute("""
                SELECT DISTINCT
                    role_canonical,
                    extraction_text
                FROM actors
                WHERE extraction_text LIKE ?
                LIMIT 10
            """, (f'%{topic}%',))

            rows = cursor.fetchall()

            actors = []
            for row in rows:
                actors.append({
                    'role': row[0] or '',
                    'text': row[1] or ''
                })

            return actors

        finally:
            conn.close()

    def _parse_timeframe(self, timeframe: str) -> tuple[Optional[str], Optional[int]]:
        """
        Parse timeframe into unit and duration.

        Args:
            timeframe: Timeframe string (e.g., '10 days', 'within 30 days')

        Returns:
            (unit, duration) tuple
        """
        # Extract numbers
        numbers = re.findall(r'\d+', timeframe)
        if not numbers:
            return (None, None)

        duration = int(numbers[0])

        # Detect unit
        timeframe_lower = timeframe.lower()
        if 'day' in timeframe_lower:
            unit = 'd'
        elif 'week' in timeframe_lower:
            unit = 'w'
        elif 'month' in timeframe_lower:
            unit = 'm'
        elif 'year' in timeframe_lower:
            unit = 'y'
        elif 'hour' in timeframe_lower:
            unit = 'h'
        else:
            unit = 'd'  # Default to days

        return (unit, duration)

    def generate_timeline_diagram(self, topic: str, config: Optional[DiagramConfig] = None) -> str:
        """
        Generate Gantt chart timeline from deadlines.

        Args:
            topic: Topic to generate timeline for
            config: Optional diagram configuration

        Returns:
            Mermaid diagram string
        """
        if config is None:
            config = DiagramConfig(
                title=f"{topic} Timeline",
                diagram_type='gantt'
            )

        deadlines = self._get_deadlines(topic)

        if not deadlines:
            return f"gantt\n    title {config.title}\n    section Notice\n    No deadlines found for this topic : 0, 1d"

        # Build Gantt chart
        mermaid = f"gantt\n"
        mermaid += f"    title {config.title}\n"
        mermaid += f"    dateFormat YYYY-MM-DD\n"

        # Group by section/phase
        # For simplicity, use one section
        mermaid += f"    section {topic}\n"

        # Add tasks
        start_date = "2024-01-01"  # Relative timeline
        current_offset = 0

        for deadline in deadlines[:15]:  # Limit to 15 for readability
            task_name = self._sanitize_text(deadline['text'], max_length=40)
            timeframe = deadline['timeframe']

            # Parse duration
            unit, duration = self._parse_timeframe(timeframe)

            if duration:
                # Calculate dates
                task_line = f"    {task_name} : {duration}{unit or 'd'}\n"
                mermaid += task_line
            else:
                # Default 1 day task
                mermaid += f"    {task_name} : 1d\n"

        return mermaid

    def generate_process_flowchart(self, topic: str, config: Optional[DiagramConfig] = None) -> str:
        """
        Generate flowchart from procedures.

        Args:
            topic: Topic to generate flowchart for
            config: Optional diagram configuration

        Returns:
            Mermaid diagram string
        """
        if config is None:
            config = DiagramConfig(
                title=f"{topic} Process",
                diagram_type='flowchart',
                orientation='TD'
            )

        procedures = self._get_procedures(topic)
        actors = self._get_actors(topic)

        if not procedures:
            return f"flowchart {config.orientation}\n    A[No procedures found for: {topic}]"

        # Build flowchart
        mermaid = f"flowchart {config.orientation}\n"

        # Add start node
        mermaid += f"    Start([Start: {self._sanitize_text(topic, 30)}])\n"

        prev_node = "Start"

        # Add procedure nodes
        for i, proc in enumerate(procedures[:20], 1):  # Limit to 20 steps
            node_id = f"P{i}"
            label = self._sanitize_text(proc['name'], max_length=50)
            action = self._sanitize_text(proc['action'], max_length=40)

            # Determine node shape based on action type
            if 'file' in action.lower() or 'submit' in action.lower():
                # Rectangle for actions
                node_def = f"{node_id}[{label}]"
            elif 'decide' in action.lower() or 'determine' in action.lower():
                # Diamond for decisions
                node_def = f"{node_id}{{{label}}}"
            else:
                # Rounded rectangle for general steps
                node_def = f"{node_id}({label})"

            mermaid += f"    {node_def}\n"

            # Add edge from previous node
            edge_label = self._sanitize_text(action, max_length=30) if action else ""
            if edge_label:
                mermaid += f"    {prev_node} -->|{edge_label}| {node_id}\n"
            else:
                mermaid += f"    {prev_node} --> {node_id}\n"

            prev_node = node_id

        # Add end node
        mermaid += f"    End([End])\n"
        mermaid += f"    {prev_node} --> End\n"

        return mermaid

    def generate_comparison_table(self, topic1: str, topic2: str) -> str:
        """
        Generate comparison table between two topics.

        Args:
            topic1: First topic
            topic2: Second topic

        Returns:
            Markdown table string (not Mermaid, as Mermaid doesn't support tables well)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Get key features for each topic from concepts table
            features = {}

            for topic in [topic1, topic2]:
                cursor.execute("""
                    SELECT term, definition
                    FROM concepts
                    WHERE extraction_text LIKE ?
                    LIMIT 5
                """, (f'%{topic}%',))

                rows = cursor.fetchall()
                features[topic] = [{'term': r[0], 'definition': r[1]} for r in rows]

            # Build markdown table
            table = f"# Comparison: {topic1} vs {topic2}\n\n"
            table += f"| Feature | {topic1} | {topic2} |\n"
            table += f"|---------|{'-'*len(topic1)}|{'-'*len(topic2)}|\n"

            # Add feature rows
            max_features = max(len(features[topic1]), len(features[topic2]))

            for i in range(max_features):
                feat1 = features[topic1][i] if i < len(features[topic1]) else {'term': '-', 'definition': '-'}
                feat2 = features[topic2][i] if i < len(features[topic2]) else {'term': '-', 'definition': '-'}

                row = f"| {feat1['term'][:30]} | {feat1['definition'][:50]} | {feat2['definition'][:50]} |\n"
                table += row

            return table

        finally:
            conn.close()

    def generate_entity_relationship_diagram(self, topic: str) -> str:
        """
        Generate entity-relationship diagram showing actors and documents.

        Args:
            topic: Topic to generate ER diagram for

        Returns:
            Mermaid ER diagram string
        """
        actors = self._get_actors(topic)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Get documents
            cursor.execute("""
                SELECT DISTINCT extraction_text
                FROM documents
                WHERE extraction_text LIKE ?
                LIMIT 5
            """, (f'%{topic}%',))

            docs = [row[0] for row in cursor.fetchall()]

        finally:
            conn.close()

        # Build ER diagram
        mermaid = "erDiagram\n"

        # Add entities
        if actors:
            mermaid += "    ACTOR {\n"
            for i, actor in enumerate(actors[:5], 1):
                role = self._sanitize_text(actor['role'], 30)
                mermaid += f"        string role_{i} \"{role}\"\n"
            mermaid += "    }\n"

        if docs:
            mermaid += "    DOCUMENT {\n"
            for i, doc in enumerate(docs[:5], 1):
                doc_name = self._sanitize_text(doc, 30)
                mermaid += f"        string doc_{i} \"{doc_name}\"\n"
            mermaid += "    }\n"

        # Add relationships
        if actors and docs:
            mermaid += "    ACTOR ||--o{ DOCUMENT : files\n"

        return mermaid

    def save_diagram(self, mermaid_code: str, output_path: Path):
        """
        Save Mermaid diagram to file.

        Args:
            mermaid_code: Mermaid diagram string
            output_path: Path to save file
        """
        # Wrap in markdown code fence
        content = f"```mermaid\n{mermaid_code}\n```\n"

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding='utf-8')

        logger.info(f"Diagram saved to: {output_path}")


def generate_timeline_diagram(db_path: Path, topic: str) -> str:
    """
    Convenience function to generate timeline diagram.

    Args:
        db_path: Path to database
        topic: Topic to generate for

    Returns:
        Mermaid diagram string
    """
    generator = MermaidDiagramGenerator(db_path)
    return generator.generate_timeline_diagram(topic)


def generate_process_diagram(db_path: Path, topic: str) -> str:
    """
    Convenience function to generate process flowchart.

    Args:
        db_path: Path to database
        topic: Topic to generate for

    Returns:
        Mermaid diagram string
    """
    generator = MermaidDiagramGenerator(db_path)
    return generator.generate_process_flowchart(topic)


def generate_comparison_diagram(db_path: Path, topic1: str, topic2: str) -> str:
    """
    Convenience function to generate comparison table.

    Args:
        db_path: Path to database
        topic1: First topic
        topic2: Second topic

    Returns:
        Markdown comparison table
    """
    generator = MermaidDiagramGenerator(db_path)
    return generator.generate_comparison_table(topic1, topic2)


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 3:
        print("Usage: python diagram_generator.py <database_path> <topic> [diagram_type] [output_file]")
        print("\nDiagram types: timeline, process, er")
        print("\nExample:")
        print("  python diagram_generator.py projects/insolvency-law/database/knowledge.db 'consumer proposals' timeline")
        sys.exit(1)

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    db_path = Path(sys.argv[1])
    topic = sys.argv[2]
    diagram_type = sys.argv[3] if len(sys.argv) > 3 else 'timeline'
    output_file = Path(sys.argv[4]) if len(sys.argv) > 4 else None

    generator = MermaidDiagramGenerator(db_path)

    print(f"\n{'='*60}")
    print(f"Generating {diagram_type} diagram for: {topic}")
    print(f"{'='*60}\n")

    # Generate diagram
    if diagram_type == 'timeline':
        diagram = generator.generate_timeline_diagram(topic)
    elif diagram_type == 'process':
        diagram = generator.generate_process_flowchart(topic)
    elif diagram_type == 'er':
        diagram = generator.generate_entity_relationship_diagram(topic)
    else:
        print(f"Unknown diagram type: {diagram_type}")
        sys.exit(1)

    # Print diagram
    print(diagram)
    print(f"\n{'='*60}\n")

    # Save if output file specified
    if output_file:
        generator.save_diagram(diagram, output_file)
        print(f"Saved to: {output_file}")
