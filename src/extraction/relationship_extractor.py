"""
Relationship Extractor - AI-powered relationship detection from existing entities.

This module analyzes entities within BIA sections and identifies explicit relationships:
1. Duty relationships: Actor → Procedure → Deadline → Consequence
2. Document requirements: Procedure → Document
3. Trigger relationships: Condition → Consequence

Uses Gemini API to understand context and connect entities intelligently.
"""

import google.generativeai as genai
from pathlib import Path
import sqlite3
import json
import os
from typing import Dict, List, Optional, Tuple
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class RelationshipExtractor:
    """Extract relationships from existing entity data using AI."""

    def __init__(self, db_path: Path, api_key: Optional[str] = None):
        """
        Initialize the relationship extractor.

        Args:
            db_path: Path to SQLite database
            api_key: Gemini API key (or use GEMINI_API_KEY env var)
        """
        self.db_path = db_path
        self.db = sqlite3.connect(db_path)
        self.db.row_factory = sqlite3.Row  # Access columns by name

        # Configure Gemini
        api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

        # Statistics
        self.stats = {
            'sections_processed': 0,
            'duty_relationships': 0,
            'document_requirements': 0,
            'trigger_relationships': 0,
            'api_calls': 0,
            'errors': 0
        }

    def get_entities_in_section(self, section_number: str) -> Dict[str, List[Dict]]:
        """
        Get all entities that appear in a specific BIA section.

        Uses character position proximity since BIA entities don't have section_number.

        Args:
            section_number: Section number (e.g., "50.4", "50.4(1)")

        Returns:
            Dictionary with entity lists: actors, procedures, deadlines, consequences, documents
        """
        # Get section boundaries
        cursor = self.db.execute('''
            SELECT char_start, char_end
            FROM bia_sections
            WHERE section_number = ?
        ''', (section_number,))

        result = cursor.fetchone()
        if not result:
            return {}

        char_start, char_end = result['char_start'], result['char_end']

        entities = {}

        # BIA source_id = 2
        # Get entities whose char positions overlap with section boundaries

        # Get actors
        cursor = self.db.execute('''
            SELECT id, role_canonical, extraction_text
            FROM actors
            WHERE source_id = 2
              AND char_start >= ?
              AND char_end <= ?
        ''', (char_start, char_end))
        entities['actors'] = [dict(row) for row in cursor.fetchall()]

        # Get procedures
        cursor = self.db.execute('''
            SELECT id, extraction_text, step_name, action
            FROM procedures
            WHERE source_id = 2
              AND char_start >= ?
              AND char_end <= ?
        ''', (char_start, char_end))
        entities['procedures'] = [dict(row) for row in cursor.fetchall()]

        # Get deadlines
        cursor = self.db.execute('''
            SELECT id, extraction_text, timeframe
            FROM deadlines
            WHERE source_id = 2
              AND char_start >= ?
              AND char_end <= ?
        ''', (char_start, char_end))
        entities['deadlines'] = [dict(row) for row in cursor.fetchall()]

        # Get consequences
        cursor = self.db.execute('''
            SELECT id, extraction_text, outcome
            FROM consequences
            WHERE source_id = 2
              AND char_start >= ?
              AND char_end <= ?
        ''', (char_start, char_end))
        entities['consequences'] = [dict(row) for row in cursor.fetchall()]

        # Get documents
        cursor = self.db.execute('''
            SELECT id, extraction_text, document_name_canonical
            FROM documents
            WHERE source_id = 2
              AND char_start >= ?
              AND char_end <= ?
        ''', (char_start, char_end))
        entities['documents'] = [dict(row) for row in cursor.fetchall()]

        return entities

    def get_section_text(self, section_number: str) -> Tuple[str, int, str, str]:
        """
        Get the full text and metadata of a BIA section.

        Args:
            section_number: Section number

        Returns:
            Tuple of (section_text, source_id, section_title, part_number)
        """
        cursor = self.db.execute('''
            SELECT full_text, section_title, part_number
            FROM bia_sections
            WHERE section_number = ?
        ''', (section_number,))

        result = cursor.fetchone()
        if result:
            # BIA source_id is hardcoded as 2
            return (
                result['full_text'],
                2,
                result['section_title'] or "",
                result['part_number'] or ""
            )
        return "", None, "", ""

    def extract_duties_from_section(self, section_number: str) -> List[Dict]:
        """
        Extract duty relationships from a BIA section using AI.

        Args:
            section_number: Section number to process

        Returns:
            List of duty relationship dictionaries
        """
        # Get section text and metadata
        section_text, source_id, section_title, part_number = self.get_section_text(section_number)
        if not section_text:
            print(f"  ⚠️  Section {section_number} not found")
            return []

        entities = self.get_entities_in_section(section_number)

        # Skip if no entities
        if not any(entities.values()):
            print(f"  ⚠️  No entities in section {section_number}")
            return []

        # Build entity summary for prompt
        entity_summary = self._format_entities_for_prompt(entities)

        # Build section header with context
        section_header = f"Section {section_number}"
        if section_title:
            section_header += f": {section_title}"
        if part_number:
            section_header += f" ({part_number})"

        # Create AI prompt
        prompt = f"""Analyze this Bankruptcy and Insolvency Act section and identify DUTY RELATIONSHIPS.

{section_header}
{section_text[:2000]}

Entities found in this section:
{entity_summary}

Identify duty relationships with this pattern:
- WHO (actor) has the duty
- WHAT (procedure/action) they must do
- WHEN (deadline) it must be done (if specified)
- CONSEQUENCE (what happens if not done) (if specified)
- MODAL VERB (shall, may, shall not, must)

Return ONLY a JSON array of duty objects. Each duty must have:
- actor_id: from the actors list above (or null if no specific actor)
- procedure_id: from the procedures list above
- deadline_id: from the deadlines list above (or null if no deadline)
- consequence_id: from the consequences list above (or null if no consequence)
- modal_verb: one of [shall, must, may, shall not]
- duty_type: one of [mandatory, discretionary, prohibited]
- relationship_text: the actual sentence from the section

Example format:
[
  {{
    "actor_id": 123,
    "procedure_id": 456,
    "deadline_id": 789,
    "consequence_id": null,
    "modal_verb": "shall",
    "duty_type": "mandatory",
    "relationship_text": "The trustee shall file a cash flow statement within 10 days"
  }}
]

Return ONLY the JSON array, no other text."""

        try:
            response = self.model.generate_content(prompt)
            self.stats['api_calls'] += 1

            # Parse JSON response
            response_text = response.text.strip()

            # Clean up response (remove markdown code blocks if present)
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            duties = json.loads(response_text)

            # Add section and source metadata
            for duty in duties:
                duty['bia_section'] = section_number
                duty['source_id'] = source_id

            return duties

        except json.JSONDecodeError as e:
            print(f"  ❌ JSON parse error for section {section_number}: {e}")
            print(f"  Response: {response.text[:200]}")
            self.stats['errors'] += 1
            return []
        except Exception as e:
            print(f"  ❌ Error processing section {section_number}: {e}")
            self.stats['errors'] += 1
            return []

    def extract_document_requirements_from_section(self, section_number: str) -> List[Dict]:
        """
        Extract document requirements from a section.

        Args:
            section_number: Section to analyze

        Returns:
            List of document requirement dictionaries
        """
        section_text, source_id, section_title, part_number = self.get_section_text(section_number)
        if not section_text:
            return []

        entities = self.get_entities_in_section(section_number)

        # Need both procedures and documents
        if not entities['procedures'] or not entities['documents']:
            return []

        entity_summary = self._format_entities_for_prompt(entities)

        # Build section header
        section_header = f"Section {section_number}"
        if section_title:
            section_header += f": {section_title}"

        prompt = f"""Analyze this BIA section and identify DOCUMENT REQUIREMENTS.

{section_header}
{section_text[:2000]}

Entities:
{entity_summary}

Identify which documents are required for which procedures.

Return ONLY a JSON array:
[
  {{
    "procedure_id": 456,
    "document_id": 789,
    "is_mandatory": true,
    "filing_context": "brief description of when/why"
  }}
]

Return ONLY the JSON array, no other text."""

        try:
            response = self.model.generate_content(prompt)
            self.stats['api_calls'] += 1

            response_text = response.text.strip()
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            doc_reqs = json.loads(response_text)

            for req in doc_reqs:
                req['bia_section'] = section_number
                req['source_id'] = source_id

            return doc_reqs

        except Exception as e:
            print(f"  ❌ Error extracting doc requirements from {section_number}: {e}")
            self.stats['errors'] += 1
            return []

    def extract_triggers_from_section(self, section_number: str) -> List[Dict]:
        """
        Extract trigger relationships (condition → consequence).

        Args:
            section_number: Section to analyze

        Returns:
            List of trigger relationship dictionaries
        """
        section_text, source_id, section_title, part_number = self.get_section_text(section_number)
        if not section_text:
            return []

        entities = self.get_entities_in_section(section_number)

        # Need consequences
        if not entities['consequences']:
            return []

        entity_summary = self._format_entities_for_prompt(entities)

        # Build section header
        section_header = f"Section {section_number}"
        if section_title:
            section_header += f": {section_title}"

        prompt = f"""Analyze this BIA section and identify TRIGGER RELATIONSHIPS.

{section_header}
{section_text[:2000]}

Entities:
{entity_summary}

Identify what triggers consequences. Pattern: "If X happens, then Y consequence occurs"

Return ONLY a JSON array:
[
  {{
    "trigger_entity_id": 123,
    "trigger_entity_type": "procedure",
    "trigger_condition": "description of what triggers this",
    "consequence_id": 456
  }}
]

trigger_entity_type must be one of: procedure, deadline, event, condition

Return ONLY the JSON array, no other text."""

        try:
            response = self.model.generate_content(prompt)
            self.stats['api_calls'] += 1

            response_text = response.text.strip()
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            triggers = json.loads(response_text)

            for trigger in triggers:
                trigger['bia_section'] = section_number
                trigger['source_id'] = source_id

            return triggers

        except Exception as e:
            print(f"  ❌ Error extracting triggers from {section_number}: {e}")
            self.stats['errors'] += 1
            return []

    def _format_entities_for_prompt(self, entities: Dict[str, List[Dict]]) -> str:
        """Format entities for inclusion in AI prompt."""
        lines = []

        if entities['actors']:
            lines.append("Actors:")
            for actor in entities['actors']:
                lines.append(f"  - id={actor['id']}: {actor['role_canonical']} ({actor['extraction_text']})")

        if entities['procedures']:
            lines.append("\nProcedures:")
            for proc in entities['procedures'][:10]:  # Limit to avoid token overflow
                lines.append(f"  - id={proc['id']}: {proc['extraction_text'][:80]}")

        if entities['deadlines']:
            lines.append("\nDeadlines:")
            for deadline in entities['deadlines']:
                lines.append(f"  - id={deadline['id']}: {deadline['timeframe']} ({deadline['extraction_text'][:60]})")

        if entities['consequences']:
            lines.append("\nConsequences:")
            for cons in entities['consequences']:
                lines.append(f"  - id={cons['id']}: {cons['outcome']} ({cons['extraction_text'][:60]})")

        if entities['documents']:
            lines.append("\nDocuments:")
            for doc in entities['documents'][:10]:
                lines.append(f"  - id={doc['id']}: {doc['document_name_canonical']}")

        return "\n".join(lines)

    def store_duty_relationships(self, duties: List[Dict]):
        """Store duty relationships in database."""
        if not duties:
            return

        for duty in duties:
            self.db.execute('''
                INSERT INTO duty_relationships
                (actor_id, procedure_id, deadline_id, consequence_id,
                 bia_section, duty_type, modal_verb, relationship_text, source_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                duty.get('actor_id'),
                duty.get('procedure_id'),
                duty.get('deadline_id'),
                duty.get('consequence_id'),
                duty.get('bia_section'),
                duty.get('duty_type'),
                duty.get('modal_verb'),
                duty.get('relationship_text'),
                duty.get('source_id')
            ))

        self.db.commit()
        self.stats['duty_relationships'] += len(duties)

    def store_document_requirements(self, doc_reqs: List[Dict]):
        """Store document requirements in database."""
        if not doc_reqs:
            return

        stored = 0
        for req in doc_reqs:
            # Validate required fields
            if not req.get('procedure_id') or not req.get('document_id'):
                print(f"    ⚠️  Skipping invalid doc requirement (missing procedure_id or document_id)")
                continue

            self.db.execute('''
                INSERT INTO document_requirements
                (procedure_id, document_id, is_mandatory, filing_context, bia_section, source_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                req.get('procedure_id'),
                req.get('document_id'),
                req.get('is_mandatory', True),
                req.get('filing_context'),
                req.get('bia_section'),
                req.get('source_id')
            ))
            stored += 1

        self.db.commit()
        self.stats['document_requirements'] += stored

    def store_trigger_relationships(self, triggers: List[Dict]):
        """Store trigger relationships in database."""
        if not triggers:
            return

        stored = 0
        for trigger in triggers:
            # Validate required fields
            if not trigger.get('consequence_id'):
                print(f"    ⚠️  Skipping invalid trigger (missing consequence_id)")
                continue

            self.db.execute('''
                INSERT INTO trigger_relationships
                (trigger_entity_id, trigger_entity_type, trigger_condition,
                 consequence_id, bia_section, source_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                trigger.get('trigger_entity_id'),
                trigger.get('trigger_entity_type'),
                trigger.get('trigger_condition'),
                trigger.get('consequence_id'),
                trigger.get('bia_section'),
                trigger.get('source_id')
            ))
            stored += 1

        self.db.commit()
        self.stats['trigger_relationships'] += stored

    def process_section(self, section_number: str):
        """
        Process a single section - extract all relationship types.

        Args:
            section_number: Section to process
        """
        print(f"\n📍 Processing Section {section_number}")

        # Extract duty relationships
        duties = self.extract_duties_from_section(section_number)
        if duties:
            print(f"  ✅ Found {len(duties)} duty relationships")
            self.store_duty_relationships(duties)

        # Extract document requirements
        doc_reqs = self.extract_document_requirements_from_section(section_number)
        if doc_reqs:
            print(f"  ✅ Found {len(doc_reqs)} document requirements")
            self.store_document_requirements(doc_reqs)

        # Extract triggers
        triggers = self.extract_triggers_from_section(section_number)
        if triggers:
            print(f"  ✅ Found {len(triggers)} trigger relationships")
            self.store_trigger_relationships(triggers)

        self.stats['sections_processed'] += 1

        # Rate limiting
        time.sleep(1)  # 1 second between sections

    def process_priority_sections(self):
        """
        Process high-value BIA sections for exam prep.

        These sections cover the most testable material.
        """
        priority_sections = [
            # Division I - Consumer Proposals
            '50.4',   # Notice of Intention
            '50',     # Division I overview
            '66.13',  # Administrator duties
            '66.14',  # Proposal approval

            # Division II - Commercial Proposals
            '50.4',   # NOI (shared with Division I)
            '62',     # Proposal filing
            '69',     # Stay of proceedings

            # Bankruptcy
            '158',    # Bankrupt duties
            '170',    # Discharge

            # Trustee duties
            '13.3',   # Trustee licensing
            '13.4',   # Conflict of interest
            '25',     # Estate administration
            '26',     # Books and records
            '30',     # Distribution

            # Creditor rights
            '38',     # Proof of claim
            '95',     # Fraudulent preferences
            '96',     # Settlements
        ]

        print(f"\n{'='*60}")
        print(f"Processing {len(priority_sections)} Priority BIA Sections")
        print(f"{'='*60}")

        for section in priority_sections:
            self.process_section(section)

        self.print_stats()

    def process_all_sections(self):
        """Process ALL BIA sections (385 total)."""
        cursor = self.db.execute('SELECT section_number FROM bia_sections ORDER BY section_number')
        all_sections = [row[0] for row in cursor.fetchall()]

        print(f"\n{'='*60}")
        print(f"Processing ALL {len(all_sections)} BIA Sections")
        print(f"{'='*60}")

        for section in all_sections:
            self.process_section(section)

        self.print_stats()

    def print_stats(self):
        """Print extraction statistics."""
        print(f"\n{'='*60}")
        print("Extraction Statistics")
        print(f"{'='*60}")
        print(f"Sections processed:       {self.stats['sections_processed']}")
        print(f"Duty relationships:       {self.stats['duty_relationships']}")
        print(f"Document requirements:    {self.stats['document_requirements']}")
        print(f"Trigger relationships:    {self.stats['trigger_relationships']}")
        print(f"Total relationships:      {self.stats['duty_relationships'] + self.stats['document_requirements'] + self.stats['trigger_relationships']}")
        print(f"API calls made:           {self.stats['api_calls']}")
        print(f"Errors encountered:       {self.stats['errors']}")
        print(f"{'='*60}\n")

    def close(self):
        """Close database connection."""
        self.db.close()


def main():
    """Main entry point for relationship extraction."""
    import argparse

    parser = argparse.ArgumentParser(description='Extract relationships from BIA entities')
    parser.add_argument('--mode', choices=['priority', 'all'], default='priority',
                        help='Process priority sections or all sections')
    parser.add_argument('--db', default='database/insolvency_knowledge.db',
                        help='Path to database file')

    args = parser.parse_args()

    # Initialize extractor
    extractor = RelationshipExtractor(Path(args.db))

    try:
        if args.mode == 'priority':
            extractor.process_priority_sections()
        else:
            extractor.process_all_sections()
    finally:
        extractor.close()


if __name__ == '__main__':
    main()
