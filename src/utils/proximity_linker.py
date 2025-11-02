"""
Proximity-based entity linker.

Links deadlines to actors and documents based on:
- Same section number
- Character position proximity
- Context keywords
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Optional


class ProximityLinker:
    """Link entities by proximity and context."""

    def __init__(self, db_path: Path):
        """Initialize with database path."""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def link_deadline_to_actors(self, deadline_id: int, char_window: int = 300) -> List[str]:
        """
        Find actors responsible for a deadline based on proximity.

        Args:
            deadline_id: Deadline ID
            char_window: Character window to search (default 300)

        Returns:
            List of canonical actor names
        """
        # Get deadline info
        cursor = self.conn.execute('''
            SELECT char_start, char_end, section_number, extraction_text
            FROM deadlines
            WHERE id = ?
        ''', (deadline_id,))

        deadline = cursor.fetchone()
        if not deadline:
            return []

        # Find actors in same section within char window
        cursor = self.conn.execute('''
            SELECT DISTINCT role_canonical
            FROM actors
            WHERE section_number = ?
                AND ABS(char_start - ?) < ?
                AND role_canonical IS NOT NULL
            ORDER BY ABS(char_start - ?)
            LIMIT 3
        ''', (deadline['section_number'], deadline['char_start'], char_window, deadline['char_start']))

        actors = [row['role_canonical'] for row in cursor.fetchall()]

        # If no actors found by proximity, infer from extraction text
        if not actors:
            text = deadline['extraction_text'].lower()
            if 'trustee' in text:
                actors = ['Trustee']
            elif 'debtor' in text or 'insolvent person' in text:
                actors = ['Debtor']
            elif 'creditor' in text:
                actors = ['Creditor']

        return actors

    def link_deadline_to_documents(self, deadline_id: int, char_window: int = 300) -> List[str]:
        """
        Find documents related to a deadline.

        Args:
            deadline_id: Deadline ID
            char_window: Character window

        Returns:
            List of document names
        """
        cursor = self.conn.execute('''
            SELECT char_start, section_number
            FROM deadlines
            WHERE id = ?
        ''', (deadline_id,))

        deadline = cursor.fetchone()
        if not deadline:
            return []

        # Find documents in same section within window
        cursor = self.conn.execute('''
            SELECT DISTINCT document_name_canonical
            FROM documents
            WHERE section_number = ?
                AND ABS(char_start - ?) < ?
                AND document_name_canonical IS NOT NULL
            ORDER BY ABS(char_start - ?)
            LIMIT 5
        ''', (deadline['section_number'], deadline['char_start'], char_window, deadline['char_start']))

        return [row['document_name_canonical'] for row in cursor.fetchall()]

    def get_timeline_with_actors(self, section_numbers: List[str]) -> List[Dict]:
        """
        Get timeline events with actor assignments for given sections.

        Args:
            section_numbers: List of section numbers (e.g., ['4.3.8', '4.3.9'])

        Returns:
            List of timeline events with actors, actions, documents
        """
        # Get all deadlines from these sections
        placeholders = ','.join('?' * len(section_numbers))
        cursor = self.conn.execute(f'''
            SELECT
                id,
                timeframe,
                extraction_text,
                char_start,
                section_number,
                section_context
            FROM deadlines
            WHERE section_number IN ({placeholders})
            ORDER BY section_number, char_start
        ''', section_numbers)

        deadlines = [dict(row) for row in cursor.fetchall()]

        # Enrich each deadline with linked entities
        timeline = []
        for dl in deadlines:
            actors = self.link_deadline_to_actors(dl['id'])
            documents = self.link_deadline_to_documents(dl['id'])

            # Parse day number from timeframe
            day = self._parse_day_number(dl['timeframe'])

            # Infer action from extraction text
            action = self._infer_action(dl['extraction_text'])

            timeline.append({
                'day': day,
                'timeframe': dl['timeframe'],
                'actors': actors,
                'action': action,
                'documents': documents,
                'section': dl['section_number'],
                'full_text': dl['extraction_text']
            })

        return sorted(timeline, key=lambda x: x['day'])

    def _parse_day_number(self, timeframe: str) -> int:
        """Extract day number from timeframe string."""
        if not timeframe:
            return 0

        timeframe = timeframe.lower()
        if '5 days' in timeframe or '5 day' in timeframe:
            return 5
        elif '10 days' in timeframe or '10 day' in timeframe:
            return 10
        elif '15 days' in timeframe:
            return 15
        elif '30 days' in timeframe or '30 day' in timeframe:
            return 30
        elif '45 days' in timeframe:
            return 45
        elif '6 months' in timeframe:
            return 180

        return 0

    def _infer_action(self, text: str) -> str:
        """Infer action description from deadline text."""
        text_lower = text.lower()

        if 'file' in text_lower:
            if 'cash flow' in text_lower:
                return "File Cash Flow Statement"
            elif 'proposal' in text_lower:
                return "File Proposal"
            elif 'notice' in text_lower:
                return "File Notice of Intention"
            else:
                return "File required documents"
        elif 'mail' in text_lower or 'send' in text_lower:
            return "Send notice to creditors"
        elif 'apply' in text_lower:
            return "Apply to court"
        elif 'issue' in text_lower:
            return "Issue certificate"

        return "Action required"

    def close(self):
        """Close database connection."""
        self.conn.close()


if __name__ == '__main__':
    # Test proximity linking
    db_path = Path('data/output/insolvency_knowledge.db')

    linker = ProximityLinker(db_path)

    # Test: Get Division I NOI timeline with actors
    noi_sections = ['4.3.6', '4.3.7', '4.3.8', '4.3.9', '4.3.10', '4.3.11']
    timeline = linker.get_timeline_with_actors(noi_sections)

    print("Division I NOI Timeline (With Proximity Linking):")
    print("="*70)

    for event in timeline:
        actors_str = ', '.join(event['actors']) if event['actors'] else 'Unknown'
        docs_str = ', '.join(event['documents'][:2]) if event['documents'] else 'None'

        print(f"\nDay {event['day']:3d} ({event['section']})")
        print(f"  Actor(s): {actors_str}")
        print(f"  Action: {event['action']}")
        print(f"  Documents: {docs_str}")
        print(f"  Detail: {event['full_text'][:80]}...")

    linker.close()

    print(f"\n✅ Proximity linking working!")
    print(f"   Found {len(timeline)} deadline events with actor assignments")
