"""
Section mapping utility for adding context to extractions.

Parses PDF text to find section headings and maps character positions
to section titles for context enrichment.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class SectionMapper:
    """
    Maps character positions in text to section titles.

    Parses section headings like:
    - "4.3.18. Notice to Creditors"
    - "5.3.22. Trustee discharge"
    - "1. INTRODUCTION TO INSOLVENCY"
    """

    def __init__(self, text: str):
        """
        Initialize with source text.

        Args:
            text: The full extracted PDF text
        """
        self.text = text
        self.sections: List[Dict] = []
        self._parse_sections()

    def _parse_sections(self):
        """
        Parse all section headings from text.

        Patterns to match:
        - "1. CHAPTER TITLE"
        - "1.1. Section Title"
        - "1.1.1. Subsection Title"
        """
        # Pattern: number.number.number. Title
        # Handles: 1., 1.1., 1.1.1., etc.
        pattern = r'^(\d+(?:\.\d+)*)\.\s+(.+)$'

        lines = self.text.split('\n')

        for i, line in enumerate(lines):
            line = line.strip()
            match = re.match(pattern, line)

            if match:
                section_num = match.group(1)
                title = match.group(2).strip()

                # Find character position of this line in full text
                # Approximate by counting characters up to this line
                char_pos = sum(len(l) + 1 for l in lines[:i])

                self.sections.append({
                    'section_number': section_num,
                    'title': title,
                    'full_title': f'{section_num} {title}',
                    'char_start': char_pos,
                    'char_end': None,  # Will be set to next section's start
                    'depth': section_num.count('.') + 1,
                    'parent': self._get_parent_section(section_num)
                })

        # Set char_end for each section (next section's start)
        for i in range(len(self.sections) - 1):
            self.sections[i]['char_end'] = self.sections[i + 1]['char_start']

        # Last section extends to end of document
        if self.sections:
            self.sections[-1]['char_end'] = len(self.text)

        logger.info(f'Parsed {len(self.sections)} sections from text')

    def _get_parent_section(self, section_num: str) -> Optional[str]:
        """
        Get parent section number.

        Examples:
        - 4.3.18 → parent is 4.3
        - 4.3 → parent is 4
        - 4 → parent is None
        """
        parts = section_num.split('.')
        if len(parts) <= 1:
            return None
        return '.'.join(parts[:-1])

    def get_section_for_position(self, char_pos: int) -> Optional[Dict]:
        """
        Find section containing given character position.

        Args:
            char_pos: Character position in text

        Returns:
            Section dict or None if not found
        """
        for section in self.sections:
            if section['char_start'] <= char_pos < section['char_end']:
                return section
        return None

    def get_hierarchical_context(self, char_pos: int) -> str:
        """
        Get full hierarchical context for a position.

        Example: "4 Division I Proposal > 4.3 Division I proposals > 4.3.18 Notice to Creditors"

        Args:
            char_pos: Character position

        Returns:
            Hierarchical breadcrumb string
        """
        section = self.get_section_for_position(char_pos)
        if not section:
            return "Unknown Section"

        # Build hierarchy
        breadcrumbs = [section['full_title']]
        current_num = section['parent']

        while current_num:
            # Find parent section
            parent = next((s for s in self.sections if s['section_number'] == current_num), None)
            if parent:
                breadcrumbs.insert(0, parent['full_title'])
                current_num = parent['parent']
            else:
                break

        return ' > '.join(breadcrumbs)

    def save_to_json(self, output_path: Path):
        """
        Save section map to JSON for reuse.

        Args:
            output_path: Where to save the section map JSON
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump({
                'total_sections': len(self.sections),
                'text_length': len(self.text),
                'sections': self.sections
            }, f, indent=2)

        logger.info(f'Saved section map to {output_path}')

    @classmethod
    def load_from_json(cls, json_path: Path) -> 'SectionMapper':
        """
        Load section map from JSON.

        Args:
            json_path: Path to section map JSON

        Returns:
            SectionMapper instance
        """
        with open(json_path, 'r') as f:
            data = json.load(f)

        mapper = cls.__new__(cls)
        mapper.text = ""  # Don't need full text for lookups
        mapper.sections = data['sections']

        logger.info(f'Loaded {len(mapper.sections)} sections from {json_path}')
        return mapper

    def get_stats(self) -> Dict:
        """Get statistics about sections."""
        depth_counts = {}
        for section in self.sections:
            depth = section['depth']
            depth_counts[depth] = depth_counts.get(depth, 0) + 1

        return {
            'total_sections': len(self.sections),
            'by_depth': depth_counts,
            'max_depth': max(s['depth'] for s in self.sections) if self.sections else 0
        }


def create_section_map(text_file: Path, output_file: Path = None) -> SectionMapper:
    """
    Create section map from text file.

    Args:
        text_file: Path to extracted PDF text
        output_file: Where to save section map (optional)

    Returns:
        SectionMapper instance
    """
    logger.info(f'Creating section map from {text_file}')

    with open(text_file, 'r', encoding='utf-8') as f:
        text = f.read()

    mapper = SectionMapper(text)

    if output_file:
        mapper.save_to_json(output_file)

    stats = mapper.get_stats()
    logger.info(f'Section map created: {stats}')

    return mapper


if __name__ == '__main__':
    # Test with our extracted text
    text_file = Path('data/input/study_materials/insolvency_admin_extracted.txt')
    output_file = Path('data/output/section_map.json')

    mapper = create_section_map(text_file, output_file)

    # Print stats
    print(f"\nSection Map Created:")
    print(f"Total sections: {len(mapper.sections)}")
    print(f"\nSample sections:")
    for section in mapper.sections[:10]:
        print(f"  {section['section_number']:8s} {section['title']}")

    # Test lookup
    print(f"\nTest lookups:")
    test_positions = [50000, 150000, 300000]
    for pos in test_positions:
        context = mapper.get_hierarchical_context(pos)
        print(f"  Char {pos:6d}: {context}")
