#!/usr/bin/env python3
"""
Study Material Relationship Extractor

Extracts relationships from Insolvency Administration Course Material.
Uses same schema as BIA extractor but adapted for educational content structure.
"""

import google.generativeai as genai
from pathlib import Path
import sqlite3
import json
import os
from typing import Dict, List, Tuple
import time
from dotenv import load_dotenv

load_dotenv()


class StudyMaterialExtractor:
    """Extract relationships from study materials."""

    def __init__(self, db_path: Path, text_file: Path):
        """Initialize extractor."""
        self.db_path = db_path
        self.db = sqlite3.connect(db_path)
        self.db.row_factory = sqlite3.Row

        # Load study material text
        with open(text_file, 'r', encoding='utf-8') as f:
            self.study_text = f.read()

        # Configure Gemini
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

        # Stats
        self.stats = {
            'sections_processed': 0,
            'duty_relationships': 0,
            'document_requirements': 0,
            'api_calls': 0,
            'errors': 0
        }

    def get_unique_sections(self) -> List[str]:
        """Get unique section contexts from study materials."""
        cursor = self.db.execute('''
            SELECT DISTINCT section_context
            FROM actors
            WHERE source_id = 1
              AND section_context IS NOT NULL
              AND section_context != 'Unknown Section'
            ORDER BY section_context
        ''')
        return [row['section_context'] for row in cursor.fetchall()]

    def get_section_text_and_entities(self, section_context: str) -> Tuple[str, Dict]:
        """Get text snippet and entities for a section."""
        # Get char range for this section
        cursor = self.db.execute('''
            SELECT MIN(char_start) as start, MAX(char_end) as end
            FROM actors
            WHERE source_id = 1
              AND section_context = ?
        ''', (section_context,))

        result = cursor.fetchone()
        if not result or not result['start']:
            return "", {}

        char_start, char_end = result['start'], result['end']

        # Get text snippet
        text_snippet = self.study_text[char_start:char_end]

        # Get entities in this section
        entities = {}

        # Actors
        cursor = self.db.execute('''
            SELECT id, role_canonical, extraction_text
            FROM actors
            WHERE source_id = 1 AND section_context = ?
        ''', (section_context,))
        entities['actors'] = [dict(row) for row in cursor.fetchall()]

        # Procedures
        cursor = self.db.execute('''
            SELECT id, extraction_text
            FROM procedures
            WHERE source_id = 1 AND section_context = ?
        ''', (section_context,))
        entities['procedures'] = [dict(row) for row in cursor.fetchall()]

        # Deadlines
        cursor = self.db.execute('''
            SELECT id, timeframe, extraction_text
            FROM deadlines
            WHERE source_id = 1 AND section_context = ?
        ''', (section_context,))
        entities['deadlines'] = [dict(row) for row in cursor.fetchall()]

        # Documents
        cursor = self.db.execute('''
            SELECT id, document_name_canonical, extraction_text
            FROM documents
            WHERE source_id = 1 AND section_context = ?
        ''', (section_context,))
        entities['documents'] = [dict(row) for row in cursor.fetchall()]

        return text_snippet[:2000], entities  # Limit text length

    def extract_from_section(self, section_context: str) -> Dict:
        """Extract relationships from a study material section."""
        # Get text and entities
        text, entities = self.get_section_text_and_entities(section_context)

        if not text or not any(entities.values()):
            return {'duties': [], 'documents': []}

        # Build entity summary
        entity_summary = self._format_entities(entities)

        # Use FULL hierarchical context (all breadcrumbs)
        section_label = section_context  # Complete hierarchy

        # AI prompt
        prompt = f"""Analyze this study material section and extract relationships.

Section (full hierarchy): {section_label}
{text[:1500]}

Entities found:
{entity_summary}

Extract TWO types of relationships:

1. DUTY/ACTION RELATIONSHIPS
   Pattern: Who does what, when
   Include: mandatory actions, procedural steps

2. DOCUMENT REQUIREMENTS
   Pattern: Which documents are needed for which procedures

Return ONLY JSON:
{{
  "duties": [
    {{
      "actor_id": 123,
      "procedure_id": 456,
      "deadline_id": null,
      "modal_verb": "shall|must|may",
      "duty_type": "mandatory|discretionary",
      "relationship_text": "actual sentence from text"
    }}
  ],
  "document_requirements": [
    {{
      "procedure_id": 456,
      "document_id": 789,
      "is_mandatory": true,
      "filing_context": "when/why needed"
    }}
  ]
}}

Return ONLY the JSON, no other text."""

        try:
            response = self.model.generate_content(prompt)
            self.stats['api_calls'] += 1

            # Clean response
            response_text = response.text.strip()
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            result = json.loads(response_text)

            # Add metadata
            for duty in result.get('duties', []):
                duty['bia_section'] = section_label[:50]  # Use section as identifier
                duty['source_id'] = 1

            for doc_req in result.get('document_requirements', []):
                doc_req['bia_section'] = section_label[:50]
                doc_req['source_id'] = 1

            return result

        except Exception as e:
            print(f"  ❌ Error: {e}")
            self.stats['errors'] += 1
            return {'duties': [], 'documents': []}

    def _format_entities(self, entities: Dict) -> str:
        """Format entities for prompt."""
        lines = []
        if entities.get('actors'):
            lines.append("Actors:")
            for actor in entities['actors'][:10]:
                lines.append(f"  - id={actor['id']}: {actor['role_canonical']}")

        if entities.get('procedures'):
            lines.append("\nProcedures:")
            for proc in entities['procedures'][:10]:
                lines.append(f"  - id={proc['id']}: {proc['extraction_text'][:60]}")

        if entities.get('deadlines'):
            lines.append("\nDeadlines:")
            for dl in entities['deadlines']:
                lines.append(f"  - id={dl['id']}: {dl['timeframe']}")

        if entities.get('documents'):
            lines.append("\nDocuments:")
            for doc in entities['documents'][:10]:
                lines.append(f"  - id={doc['id']}: {doc['document_name_canonical']}")

        return "\n".join(lines)

    def store_relationships(self, duties: List[Dict], doc_reqs: List[Dict]):
        """Store extracted relationships."""
        # Store duties
        for duty in duties:
            if not duty.get('modal_verb'):
                continue  # Skip invalid

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
            self.stats['duty_relationships'] += 1

        # Store document requirements
        for req in doc_reqs:
            if not req.get('procedure_id') or not req.get('document_id'):
                continue  # Skip invalid

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
            self.stats['document_requirements'] += 1

        self.db.commit()

    def process_all_sections(self):
        """Process all study material sections."""
        sections = self.get_unique_sections()

        print(f"\n{'='*60}")
        print(f"Processing {len(sections)} Study Material Sections")
        print(f"{'='*60}")

        for i, section in enumerate(sections):
            print(f"\n📍 [{i+1}/{len(sections)}] {section[:80]}...")

            result = self.extract_from_section(section)

            duties = result.get('duties', [])
            docs = result.get('document_requirements', [])

            if duties:
                print(f"  ✅ {len(duties)} duties")
            if docs:
                print(f"  ✅ {len(docs)} document requirements")

            self.store_relationships(duties, docs)

            self.stats['sections_processed'] += 1

            # Rate limiting
            if i % 10 == 0:
                time.sleep(2)  # Brief pause every 10 sections
            else:
                time.sleep(0.5)

        self.print_stats()

    def print_stats(self):
        """Print statistics."""
        print(f"\n{'='*60}")
        print("Extraction Statistics")
        print(f"{'='*60}")
        print(f"Sections processed:       {self.stats['sections_processed']}")
        print(f"Duty relationships:       {self.stats['duty_relationships']}")
        print(f"Document requirements:    {self.stats['document_requirements']}")
        print(f"Total relationships:      {self.stats['duty_relationships'] + self.stats['document_requirements']}")
        print(f"API calls:                {self.stats['api_calls']}")
        print(f"Errors:                   {self.stats['errors']}")
        print(f"{'='*60}\n")

    def close(self):
        """Close database."""
        self.db.close()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Extract relationships from study materials')
    parser.add_argument('--db', default='database/insolvency_knowledge.db')
    parser.add_argument('--text', default='data/input/study_materials/insolvency_admin_extracted.txt')

    args = parser.parse_args()

    extractor = StudyMaterialExtractor(Path(args.db), Path(args.text))

    try:
        extractor.process_all_sections()
    finally:
        extractor.close()


if __name__ == '__main__':
    main()
