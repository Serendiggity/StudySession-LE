"""
Timeline generator - creates Mermaid swimlane diagrams from database queries.

Generates visual timelines for insolvency processes like Division I NOI.
Uses proximity linking to connect deadlines with actors and documents.
"""

import sqlite3
from pathlib import Path
from typing import List, Dict
import re
import sys

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.proximity_linker import ProximityLinker


class TimelineGenerator:
    """Generate Mermaid timeline diagrams from database."""

    def __init__(self, db_path: Path):
        """Initialize with database path."""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # Access by column name
        self.linker = ProximityLinker(db_path)

    def generate_division_i_noi_timeline(self) -> str:
        """
        Generate Division I Notice of Intention timeline (sections 4.3.6-4.3.11).

        Uses proximity linking to assign actors to deadlines.

        Returns:
            Mermaid gantt chart code
        """
        # Get timeline with proximity-linked actors
        noi_sections = ['4.3.6', '4.3.7', '4.3.8', '4.3.9', '4.3.10', '4.3.11']
        timeline_events = self.linker.get_timeline_with_actors(noi_sections)

        # Generate Mermaid
        return self._generate_mermaid_from_timeline(
            timeline_events,
            title="Division I Proposal - Notice of Intention Process"
        )

    def _generate_mermaid_gantt(self, entities: List[Dict], title: str) -> str:
        """
        Generate Mermaid gantt chart from entities (DATA-DRIVEN).

        Args:
            entities: List of entity dicts with type, detail, extraction_text, section_number

        Returns:
            Mermaid gantt chart markdown
        """
        # Group entities
        deadlines = [e for e in entities if e['type'] == 'deadline' and e['detail']]
        documents = [e for e in entities if e['type'] == 'document' and e['detail']]
        actors_found = set(e['detail'] for e in entities if e['type'] == 'actor' and e['detail'])

        # Parse deadlines to extract timeline
        timeline_events = []
        for dl in deadlines:
            text = dl['extraction_text'].lower()
            timeframe = dl['detail'].lower()
            section = dl['section_number']

            # Determine actor from context
            actor = 'Unknown'
            if 'trustee' in text and 'insolvent person' not in text:
                actor = 'Trustee'
            elif 'insolvent person' in text or 'debtor' in text:
                actor = 'Debtor'
            elif 'landlord' in text:
                actor = 'Landlord'
            elif 'creditor' in text:
                actor = 'Creditor'

            # Determine action from text
            action = "Action required"
            if 'file' in text:
                if 'cash flow' in text:
                    action = "File Cash Flow Statement"
                elif 'proposal' in text:
                    action = "File Proposal or Request Extension"
                elif 'notice' in text:
                    action = "File Notice of Intention"
            elif 'mail' in text or 'send' in text:
                action = "Send notice to creditors"
            elif 'apply' in text:
                action = "Apply for extension"

            # Parse relative day
            day = 0
            if '5 days' in timeframe or '5 day' in timeframe:
                day = 5
            elif '10 days' in timeframe or '10 day' in timeframe:
                day = 10
            elif '30 days' in timeframe or '30 day' in timeframe:
                day = 30
            elif '15 days' in timeframe:
                day = 15
            elif '45 days' in timeframe:
                day = 45

            timeline_events.append({
                'actor': actor,
                'action': action,
                'day': day,
                'section': section,
                'detail': dl['detail'],
                'text': dl['extraction_text'][:100]
            })

        # Sort by day
        timeline_events.sort(key=lambda x: x['day'])

        # Build Mermaid
        mermaid = [
            "```mermaid",
            "gantt",
            f"    title {title}",
            "    dateFormat YYYY-MM-DD",
            "    axisFormat Day %d",
            ""
        ]

        # Group by actor
        actors_in_timeline = sorted(set(e['actor'] for e in timeline_events))

        for actor in actors_in_timeline:
            mermaid.append(f"    section {actor}")
            actor_events = [e for e in timeline_events if e['actor'] == actor]

            for event in actor_events:
                date = f"2024-01-{event['day']+1:02d}" if event['day'] < 30 else "2024-02-01"
                task = f"{event['action']} (Day {event['day']})"
                mermaid.append(f"    {task} :{date}, 1d")

        mermaid.append("```")
        mermaid.append("")

        # Add extracted deadlines list
        mermaid.append("**Deadlines Extracted from PDF:**")
        for event in timeline_events:
            mermaid.append(f"- **Day {event['day']}** ({event['section']}): {event['detail']} - {event['text']}")

        mermaid.append("")
        mermaid.append("**Required Documents:**")
        unique_docs = sorted(set(d['detail'] for d in documents if d['detail']))
        for doc in unique_docs:
            mermaid.append(f"- {doc}")

        return "\n".join(mermaid)

    def _generate_mermaid_from_timeline(self, timeline_events: List[Dict], title: str) -> str:
        """
        Generate Mermaid gantt from proximity-linked timeline events.

        Args:
            timeline_events: List from proximity linker with actors, actions, documents

        Returns:
            Mermaid markdown
        """
        mermaid = [
            "```mermaid",
            "gantt",
            f"    title {title}",
            "    dateFormat YYYY-MM-DD",
            "    axisFormat Day %d",
            ""
        ]

        # Get all unique actors
        all_actors = set()
        for event in timeline_events:
            all_actors.update(event.get('actors', []))

        # Main actors in preferred order
        priority_actors = ['Debtor', 'Insolvent Person', 'Trustee', 'Official Receiver', 'Creditor', 'Court']
        ordered_actors = [a for a in priority_actors if a in all_actors]
        ordered_actors += sorted([a for a in all_actors if a not in ordered_actors])

        # Build swimlane for each actor
        for actor in ordered_actors:
            mermaid.append(f"    section {actor}")

            actor_events = [e for e in timeline_events if actor in e.get('actors', [])]

            for event in actor_events:
                day = event['day']
                date = f"2024-01-{day+1:02d}" if day <= 30 else f"2024-02-{day-30:02d}"
                task_name = f"{event['action']} (Day {day})"

                mermaid.append(f"    {task_name} :{date}, 1d")

        mermaid.append("```")
        mermaid.append("")

        # Add detailed breakdown
        mermaid.append("## Timeline Details")
        mermaid.append("")

        for event in timeline_events:
            actors_str = ', '.join(event['actors']) if event['actors'] else 'Unknown'
            docs_str = ', '.join(event['documents'][:3]) if event['documents'] else 'None'

            mermaid.append(f"### Day {event['day']} - {event['action']}")
            mermaid.append(f"- **Section:** {event['section']}")
            mermaid.append(f"- **Actor(s):** {actors_str}")
            mermaid.append(f"- **Documents:** {docs_str}")
            mermaid.append(f"- **Deadline:** {event['timeframe']}")
            mermaid.append(f"- **Context:** _{event['full_text']}_")
            mermaid.append("")

        return "\n".join(mermaid)

    def close(self):
        """Close database connection."""
        self.conn.close()
        self.linker.close()


if __name__ == '__main__':
    # Generate Division I NOI timeline
    db_path = Path('data/output/insolvency_knowledge.db')
    output_path = Path('data/output/timelines/division_i_noi.md')

    generator = TimelineGenerator(db_path)
    timeline = generator.generate_division_i_noi_timeline()
    generator.close()

    # Save to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(f"# Division I Notice of Intention Timeline\n\n")
        f.write(timeline)

    print("✅ Division I NOI Timeline Generated!")
    print("="*70)
    print(timeline)
    print()
    print(f"Saved to: {output_path}")
    print("\nOpen this file in any Mermaid viewer or paste into GitHub markdown!")
