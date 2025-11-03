"""
Cross-Reference Navigator - Follow citations across sources.

Enables automatic traversal of statutory references:
- Study Material → BIA sections
- BIA sections → other BIA sections
- OSB Directives → BIA sections
- Bi-directional navigation
"""

import sqlite3
from pathlib import Path
import re
from typing import List, Dict


class CrossReferenceNavigator:
    """Navigate cross-references between sources."""

    def __init__(self, db_path: Path):
        self.conn = sqlite3.connect(db_path)

    def close(self):
        """Close connection."""
        self.conn.close()

    def find_bia_section_references(self, text: str) -> List[str]:
        """Extract BIA section references from any text."""
        # Patterns: "BIA s. 50.4", "section 158", "s. 67(1)"
        patterns = [
            r'BIA\s+s\.\s*(\d+(?:\.\d+)?(?:\(\d+\))?)',
            r'section\s+(\d+(?:\.\d+)?(?:\(\d+\))?)',
            r's\.\s*(\d+(?:\.\d+)?(?:\(\d+\))?)',
        ]

        found_sections = set()
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Clean: "50.4(1)" → "50.4" (we store main sections)
                clean = re.sub(r'\([0-9]+\)', '', match)
                found_sections.add(clean)

        return sorted(found_sections)

    def get_bia_section(self, section_number: str) -> Dict:
        """Retrieve BIA section by number."""
        cursor = self.conn.execute('''
            SELECT section_number, section_title, part_number, full_text
            FROM bia_sections
            WHERE section_number = ?
        ''', (section_number,))

        result = cursor.fetchone()
        if result:
            return {
                'section_number': result[0],
                'section_title': result[1],
                'part_number': result[2],
                'full_text': result[3]
            }
        return None

    def get_outbound_references(self, source_type: str, source_id: str) -> List[Dict]:
        """
        Get all BIA sections referenced by a source.

        Args:
            source_type: 'study_material', 'bia_section', 'osb_directive'
            source_id: Section number, chapter, or directive number
        """
        references = []

        if source_type == 'study_material':
            # Get statutory references from study material section
            cursor = self.conn.execute('''
                SELECT DISTINCT reference, act, section
                FROM statutory_references
                WHERE source_id = 1
                  AND section_context LIKE ?
                  AND act = 'BIA'
            ''', (f'%{source_id}%',))

            for row in cursor.fetchall():
                ref, act, section = row
                clean_section = re.sub(r's\.\s*', '', section).strip()
                bia_section = self.get_bia_section(clean_section)
                if bia_section:
                    references.append({
                        'reference_text': ref,
                        'target': bia_section
                    })

        elif source_type == 'bia_section':
            # Find references within a BIA section to other BIA sections
            section = self.get_bia_section(source_id)
            if section:
                referenced_sections = self.find_bia_section_references(section['full_text'])
                for ref_num in referenced_sections:
                    if ref_num != source_id:  # Don't self-reference
                        target = self.get_bia_section(ref_num)
                        if target:
                            references.append({
                                'reference_text': f's. {ref_num}',
                                'target': target
                            })

        elif source_type == 'osb_directive':
            # Find BIA sections referenced in directive
            cursor = self.conn.execute('''
                SELECT full_text FROM osb_directives WHERE directive_number = ?
            ''', (source_id,))
            result = cursor.fetchone()
            if result:
                referenced_sections = self.find_bia_section_references(result[0])
                for ref_num in referenced_sections:
                    target = self.get_bia_section(ref_num)
                    if target:
                        references.append({
                            'reference_text': f's. {ref_num}',
                            'target': target
                        })

        return references

    def navigate_from_concept(self, concept_text: str) -> Dict:
        """
        Smart navigation: Start from a concept, follow all references.

        Example: "Division I NOI" → find mentions → follow to BIA ss. 50-66
        """
        result = {
            'concept': concept_text,
            'mentions': [],
            'referenced_sections': []
        }

        # Find where concept appears
        cursor = self.conn.execute('''
            SELECT extraction_text, section_context, char_start
            FROM concepts
            WHERE source_id = 1
              AND (term LIKE ? OR extraction_text LIKE ?)
            LIMIT 5
        ''', (f'%{concept_text}%', f'%{concept_text}%'))

        for row in cursor.fetchall():
            result['mentions'].append({
                'text': row[0],
                'context': row[1]
            })

        # Find statutory references near these mentions
        cursor = self.conn.execute('''
            SELECT DISTINCT sr.reference, sr.section
            FROM statutory_references sr
            WHERE sr.source_id = 1
              AND sr.act = 'BIA'
              AND sr.section_context LIKE ?
        ''', (f'%{concept_text}%',))

        for row in cursor.fetchall():
            ref, section = row
            clean_section = re.sub(r's\.\s*', '', section).strip()
            bia_section = self.get_bia_section(clean_section)
            if bia_section:
                result['referenced_sections'].append(bia_section)

        return result

    def find_related_content(self, bia_section_number: str) -> Dict:
        """
        Find all content related to a BIA section across all sources.

        Returns:
        - Study material mentions
        - OSB Directive references
        - Related BIA sections
        """
        related = {
            'bia_section': self.get_bia_section(bia_section_number),
            'study_material_references': [],
            'directive_references': [],
            'related_bia_sections': []
        }

        # Find study material references to this section
        cursor = self.conn.execute('''
            SELECT reference, section_context
            FROM statutory_references
            WHERE source_id = 1
              AND section LIKE ?
        ''', (f'%{bia_section_number}%',))

        for row in cursor.fetchall():
            related['study_material_references'].append({
                'reference': row[0],
                'context': row[1]
            })

        # Find OSB Directive references
        cursor = self.conn.execute('''
            SELECT directive_number, directive_name, full_text
            FROM osb_directives
        ''')

        for row in cursor.fetchall():
            number, name, text = row
            if f's. {bia_section_number}' in text or f'section {bia_section_number}' in text:
                related['directive_references'].append({
                    'directive': f'{number}: {name}',
                    'text': text[:200] + '...'
                })

        # Find related BIA sections (referenced within this section)
        if related['bia_section']:
            refs = self.find_bia_section_references(related['bia_section']['full_text'])
            for ref in refs:
                if ref != bia_section_number:
                    section = self.get_bia_section(ref)
                    if section:
                        related['related_bia_sections'].append(section)

        return related


def demo():
    """Demonstrate cross-reference navigation."""
    db_path = Path('data/output/insolvency_knowledge.db')
    nav = CrossReferenceNavigator(db_path)

    print('='*70)
    print('CROSS-REFERENCE NAVIGATION DEMO')
    print('='*70)

    # Example 1: Follow references FROM study material
    print('\n1. Study Material → BIA Sections (Outbound References)')
    print('-'*70)
    refs = nav.get_outbound_references('study_material', 'Division I')
    print(f'   Found {len(refs)} BIA sections referenced in Division I content:')
    for ref in refs[:5]:
        print(f'   - {ref["reference_text"]:15s} → BIA s. {ref["target"]["section_number"]:6s}: {ref["target"]["section_title"][:40]}')

    # Example 2: Find what references a BIA section
    print('\n2. What References BIA s. 50.4? (Inbound References)')
    print('-'*70)
    related = nav.find_related_content('50.4')
    print(f'   Study Material mentions: {len(related["study_material_references"])}')
    for ref in related['study_material_references'][:3]:
        print(f'   - "{ref["reference"]}" in {ref["context"][:50]}...')

    print(f'\n   OSB Directive mentions: {len(related["directive_references"])}')
    for ref in related['directive_references']:
        print(f'   - {ref["directive"]}')

    # Example 3: Navigate from concept
    print('\n3. Navigate from Concept: "Notice of Intention"')
    print('-'*70)
    nav_result = nav.navigate_from_concept('Notice of Intention')
    print(f'   Appears in study material: {len(nav_result["mentions"])} times')
    print(f'   References these BIA sections: {len(nav_result["referenced_sections"])}')
    for section in nav_result['referenced_sections'][:3]:
        print(f'   - BIA s. {section["section_number"]}: {section["section_title"]}')

    # Example 4: Follow references WITHIN BIA
    print('\n4. BIA s. 50.4 References These Other Sections:')
    print('-'*70)
    refs = nav.get_outbound_references('bia_section', '50.4')
    print(f'   Found {len(refs)} cross-references within BIA:')
    for ref in refs[:5]:
        print(f'   - s. {ref["target"]["section_number"]:6s}: {ref["target"]["section_title"][:40]}')

    nav.close()

    print('\n' + '='*70)
    print('✓ Cross-reference navigation is WORKING!')
    print('='*70)


if __name__ == '__main__':
    demo()
