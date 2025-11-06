"""
BIA Structure Parser - Extract Parts and Sections structurally.

Parses the BIA statute to extract:
- Parts (PART I, PART II, etc.)
- Sections (2, 43, 50.4, etc.)
- Complete section text for AI querying
"""

import re
from pathlib import Path
from typing import List, Dict
import json


class BIAStructureParser:
    """Parse BIA statute structure."""

    def __init__(self, text: str):
        """Initialize with BIA text."""
        self.text = text
        self.parts = []
        self.sections = []

    def parse(self):
        """Parse complete structure."""
        # Clear previous results (in case parse() is called multiple times)
        self.parts = []
        self.sections = []

        self._parse_parts()
        self._parse_sections()
        return {
            'parts': self.parts,
            'sections': self.sections
        }

    def _parse_parts(self):
        """Extract all PART divisions."""
        # Pattern: PART I followed by English title on next line
        # Structure: PART I\nAdministrative Officials\nPARTIE I\n...
        part_pattern = r'^PART\s+([IVX]+)\s*$'

        for match in re.finditer(part_pattern, self.text, re.MULTILINE):
            part_num_roman = match.group(1)

            # Get English title (next line after PART I)
            start_pos = match.end() + 1  # Skip newline
            # Find next newline
            end_of_title = self.text.find('\n', start_pos)
            english_title = self.text[start_pos:end_of_title].strip()

            # Remove French indicators if any slipped through
            if 'of/f_i' in english_title:
                english_title = english_title.replace('of/f_i', 'Offi')

            self.parts.append({
                'part_number': f'PART {part_num_roman}',
                'part_title': english_title,
                'char_start': match.start(),
                'char_end': match.end()
            })

    def _parse_sections(self):
        """Extract all sections with full text from actual provisions (skip TOC)."""
        # BIA structure: TOC first (~20K chars), then actual provisions
        # Skip to actual provisions (after "PART I" marker in body, not TOC)

        # Find where actual provisions start
        # Strategy: TOC doesn't have citations, but actual provisions do
        # Look for first "R.S., 1985, c. B-3" citation which marks actual statutory text

        # Find first citation (marks the end of Section 1 text)
        citation_match = re.search(r'R\.S\., 1985, c\. B-3', self.text)

        if citation_match:
            # Back up from citation to find the start of Section 1
            # Look backwards for "1 This Act" or similar pattern
            search_start = max(0, citation_match.start() - 500)
            lookback_text = self.text[search_start:citation_match.start()]

            # Find "1 " followed by capital letter (start of Section 1)
            section_1_match = re.search(r'\n1 [A-Z]', lookback_text)
            if section_1_match:
                provisions_start = search_start + section_1_match.start() + 1  # +1 to skip newline
            else:
                # Fallback: start just before citation
                provisions_start = max(0, citation_match.start() - 200)
        else:
            # Fallback: estimate based on file size (TOC is usually first ~5-10%)
            provisions_start = len(self.text) // 10

        provisions_text = self.text[provisions_start:]

        # Pattern: Section can start with either:
        # Format 1: "50.4 Title text" (section without subsections)
        # Format 2: "50.4 (1) Text..." (section starts with subsection 1)
        # We need to catch both and also grab marginal notes

        # Find all potential section starts (including subsections)
        section_pattern = r'^(\d+(?:\.\d+)?)\s+(?:\([0-9]+\)|[A-Z])'

        all_matches = list(re.finditer(section_pattern, provisions_text, re.MULTILINE))

        # CRITICAL FIX: Handle duplicates (marginal notes vs actual text)
        # Strategy: For each section number, keep the match with MORE following text
        # (actual section text is longer than marginal notes)

        from collections import defaultdict
        matches_by_section = defaultdict(list)

        # Group all matches by section number
        for match in all_matches:
            section_num = match.group(1)
            matches_by_section[section_num].append(match)

        # For each section, choose the best match
        section_matches = []
        for section_num, matches in matches_by_section.items():
            if len(matches) == 1:
                section_matches.append(matches[0])
            else:
                # Multiple matches: choose the one followed by most text before next section
                best_match = matches[0]
                best_length = 0

                for match in matches:
                    # Estimate text length: distance to next different section number
                    match_pos = match.start()
                    next_pos = len(provisions_text)  # Default: end of file

                    # Find next match with different section number
                    for other_match in all_matches:
                        if other_match.start() > match_pos:
                            other_section_num = other_match.group(1)
                            if other_section_num != section_num:
                                next_pos = other_match.start()
                                break

                    text_length = next_pos - match_pos
                    if text_length > best_length:
                        best_length = text_length
                        best_match = match

                section_matches.append(best_match)

        # Sort by position
        section_matches.sort(key=lambda m: m.start())

        print(f'DEBUG: all_matches={len(all_matches)}, unique sections={len(matches_by_section)}, section_matches={len(section_matches)}')

        for i, match in enumerate(section_matches):
            section_num = match.group(1)

            # Look for marginal note (title) on previous line
            # Marginal notes are typically short descriptive phrases before section number
            line_start = provisions_text.rfind('\n', 0, match.start())
            if line_start > 0:
                prev_line_start = provisions_text.rfind('\n', 0, line_start)
                marginal_note_line = provisions_text[prev_line_start+1:line_start].strip()

                # Extract English portion from marginal note (before French if bilingual)
                # Common pattern: "English Title French Title" or "English Titre français"
                section_title = marginal_note_line

                # Split on common bilingual indicators
                # Pattern: Look for French word starts (capital + accents or known French words)
                split_patterns = [
                    r'\s+Avis\s+d',         # "Avis d'intention"
                    r'\s+[ÉÀÇ]',            # Accented capitals
                    r'\s+[A-Z]é',           # Capital + é
                    r'\s+Définitions?\s',   # French "Définitions"
                    r'\s+Nomination\s',     # Common French title word
                ]

                for pattern in split_patterns:
                    split_match = re.search(pattern, marginal_note_line)
                    if split_match:
                        section_title = marginal_note_line[:split_match.start()].strip()
                        break

                # If no title found or very short, extract from first line of section
                if len(section_title) < 5 or section_title == marginal_note_line:
                    section_title = "Section " + section_num
            else:
                section_title = "Section " + section_num

            # Extract full text until next section
            start_pos_relative = match.start()
            start_pos_absolute = provisions_start + start_pos_relative

            # Find end: next section number at line start, EXCLUDING its marginal note
            if i + 1 < len(section_matches):
                next_section_start = section_matches[i + 1].start()

                # Look backwards from next section to find its marginal note (usually 2-3 lines before)
                # Marginal notes are separated by blank lines or "Current to..." markers
                lookback_start = max(0, next_section_start - 500)
                lookback_text = provisions_text[lookback_start:next_section_start]

                # Find the last occurrence of common separators before next section
                separators = [
                    '\n\n',  # Double newline (blank line)
                    'Current to',  # Date marker
                    'Last amended',  # Amendment marker
                ]

                last_separator_pos = lookback_start
                for sep in separators:
                    pos = lookback_text.rfind(sep)
                    if pos != -1:
                        last_separator_pos = max(last_separator_pos, lookback_start + pos + len(sep))

                # If we found a separator, use it; otherwise use 3 lines back
                if last_separator_pos > lookback_start:
                    end_pos_relative = last_separator_pos
                else:
                    # Fallback: go back 3 newlines from next section
                    temp_pos = next_section_start
                    for _ in range(3):
                        temp_pos = provisions_text.rfind('\n', 0, temp_pos)
                        if temp_pos == -1:
                            break
                    end_pos_relative = temp_pos if temp_pos != -1 else next_section_start

                # CRITICAL: Ensure end is never before start (can happen if separator found before current section)
                if end_pos_relative <= start_pos_relative:
                    # Fallback to next section start
                    end_pos_relative = next_section_start
            else:
                end_pos_relative = len(provisions_text)

            full_text = provisions_text[start_pos_relative:end_pos_relative].strip()

            # Remove remaining French fragments from full text
            full_text_english = self._clean_french_from_text(full_text)

            # Determine which Part this section belongs to
            part_number = self._get_part_for_position(start_pos_absolute)

            self.sections.append({
                'section_number': section_num,
                'section_title': section_title,
                'part_number': part_number,
                'full_text': full_text_english,
                'char_start': start_pos_absolute,
                'char_end': provisions_start + end_pos_relative,
                'subsection_number': None
            })

    def _clean_french_from_text(self, text: str) -> str:
        """Remove French fragments from section text."""
        # Remove lines that are primarily French
        lines = text.split('\n')
        cleaned_lines = []

        french_indicators = 'éèêàâçôûùïÉÈÊÀÂÇÔÛÙÏ'
        french_keywords = ['tribunal', 'demande', 'ordonnance', 'proposant',
                          'syndic', 'créancier', 'débiteur', 'failli']

        for line in lines:
            if len(line.strip()) < 15:
                cleaned_lines.append(line)
                continue

            # Count French indicators
            french_char_count = sum(line.count(c) for c in french_indicators)
            french_density = french_char_count / len(line) if len(line) > 0 else 0

            # Check for French keywords
            french_word_count = sum(1 for word in french_keywords if word in line.lower())

            # Remove if high French density OR multiple French keywords
            if french_density > 0.02 or french_word_count >= 2:
                continue

            cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def _get_part_for_position(self, pos: int) -> str:
        """Find which Part a character position belongs to."""
        for i, part in enumerate(self.parts):
            # Check if position is after this part and before next part
            if pos >= part['char_start']:
                if i + 1 < len(self.parts):
                    if pos < self.parts[i + 1]['char_start']:
                        return part['part_number']
                else:
                    # Last part
                    return part['part_number']
        return None

    def save_to_json(self, output_path: Path):
        """Save parsed structure to JSON."""
        data = self.parse()
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        return data


if __name__ == '__main__':
    # Test the parser
    bia_text_path = Path('sources/bia_statute/bia_statute_clean_english.txt')
    output_path = Path('data/output/bia_structure.json')

    print('='*70)
    print('BIA STRUCTURE PARSER - Clean English Version')
    print('='*70)

    print(f'\nLoading BIA text: {bia_text_path}')
    with open(bia_text_path, 'r') as f:
        text = f.read()
    print(f'✓ Loaded {len(text):,} characters (enhanced French-filtered)')

    print('\nParsing structure...')
    parser = BIAStructureParser(text)
    data = parser.parse()

    print(f'✓ Found {len(data["parts"])} Parts')
    print(f'✓ Found {len(data["sections"])} Sections')

    print('\n=== Sample Parts ===')
    for part in data['parts'][:5]:
        print(f'{part["part_number"]:10s}: {part["part_title"]}')

    print('\n=== Sample Sections ===')
    for section in data['sections'][:10]:
        text_preview = section['full_text'][:80].replace('\n', ' ')
        print(f'Section {section["section_number"]:6s} ({section["part_number"]}): {section["section_title"][:40]}')

    # Save
    parser.save_to_json(output_path)
    print(f'\n✓ Saved structure to: {output_path}')
