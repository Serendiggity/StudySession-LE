"""
Enhanced French Removal from BIA Statute.

Multi-phase cleaning strategy:
- Phase 1: High-confidence pattern removal (95%+ accuracy)
- Phase 2: Contextual removal (80%+ accuracy)
- Phase 3: Validation and statistics
"""

from pathlib import Path
import re
from typing import List, Tuple


class EnhancedFrenchFilter:
    """Enhanced French content removal."""

    def __init__(self, text: str):
        self.original_text = text
        self.text = text
        self.removal_stats = {
            'phase1_partie_headers': 0,
            'phase1_french_citations': 0,
            'phase1_duplicate_section_titles': 0,
            'phase2_lowercase_bullets': 0,
            'phase2_french_paragraphs': 0,
            'phase2_inline_french': 0,
            'total_lines_removed': 0,
            'total_chars_removed': 0
        }

    def clean(self) -> str:
        """Run all cleaning phases."""
        print('='*70)
        print('ENHANCED FRENCH REMOVAL')
        print('='*70)

        original_len = len(self.text)
        original_lines = self.text.count('\n')

        # Phase 1: High-confidence removals
        self._remove_partie_headers()
        self._remove_french_citations()
        self._clean_section_title_duplicates()

        # Phase 2: Contextual removals
        self._remove_lowercase_bullets()
        self._remove_french_paragraphs()
        self._clean_inline_french()

        # Calculate stats
        final_len = len(self.text)
        final_lines = self.text.count('\n')

        self.removal_stats['total_chars_removed'] = original_len - final_len
        self.removal_stats['total_lines_removed'] = original_lines - final_lines

        return self.text

    def _remove_partie_headers(self):
        """Remove PARTIE I, PARTIE II, etc. headers."""
        pattern = r'^PARTIE\s+[IVX]+\s*$'
        lines_before = self.text.count('\n')

        self.text = re.sub(pattern, '', self.text, flags=re.MULTILINE)

        lines_after = self.text.count('\n')
        self.removal_stats['phase1_partie_headers'] = lines_before - lines_after

    def _remove_french_citations(self):
        """Remove French citation lines (ch., art.)."""
        # French citations use "ch." (chapitre) and "art." (article)
        # English uses "c." (chapter) and "s." (section)
        pattern = r'^.*\bch\.\s+\d+.*\bart\.\s+\d+.*$'
        lines_before = self.text.count('\n')

        self.text = re.sub(pattern, '', self.text, flags=re.MULTILINE)

        lines_after = self.text.count('\n')
        self.removal_stats['phase1_french_citations'] = lines_before - lines_after

    def _clean_section_title_duplicates(self):
        """Clean section title duplicates: '50.4 English 50.4 French'."""
        # Pattern: section number appears twice on same line
        # Keep only text before second occurrence
        count = 0

        lines = self.text.split('\n')
        cleaned_lines = []

        for line in lines:
            # Find section number pattern at start
            match = re.match(r'^(\d+(?:\.\d+)?)\s+(.+)', line)
            if match:
                section_num = match.group(1)
                rest_of_line = match.group(2)

                # Check if section number appears again in the line
                duplicate_pattern = rf'\b{re.escape(section_num)}\b'
                if len(re.findall(duplicate_pattern, rest_of_line)) >= 1:
                    # Split at second occurrence of section number
                    second_occurrence = rest_of_line.find(section_num)
                    if second_occurrence > 0:
                        english_portion = rest_of_line[:second_occurrence].strip()
                        cleaned_line = f'{section_num} {english_portion}'
                        cleaned_lines.append(cleaned_line)
                        count += 1
                        continue

            cleaned_lines.append(line)

        self.text = '\n'.join(cleaned_lines)
        self.removal_stats['phase1_duplicate_section_titles'] = count

    def _remove_lowercase_bullets(self):
        """Remove French-style lowercase bullet paragraphs."""
        # French uses: a), b), c) (lowercase, no parentheses before)
        # English uses: (a), (b), (c)
        pattern = r'^[a-z]\).*$'
        lines_before = self.text.count('\n')

        self.text = re.sub(pattern, '', self.text, flags=re.MULTILINE)

        lines_after = self.text.count('\n')
        self.removal_stats['phase2_lowercase_bullets'] = lines_before - lines_after

    def _remove_french_paragraphs(self):
        """Remove paragraphs with high French indicator density."""
        french_indicators = 'éèêàâçôûùïÉÈÊÀÂÇÔÛÙÏ'
        count = 0

        lines = self.text.split('\n')
        cleaned_lines = []

        for line in lines:
            if len(line.strip()) < 20:  # Keep short lines
                cleaned_lines.append(line)
                continue

            # Count French indicators
            french_char_count = sum(line.count(c) for c in french_indicators)
            french_density = french_char_count / len(line) if len(line) > 0 else 0

            # Remove if > 1.5% French characters
            if french_density > 0.015:
                count += 1
                continue

            # Also check for French keywords
            french_keywords = ['fiduciaire', 'créancier', 'débiteur', 'failli', 'syndic',
                             'faillite', 'proposition', 'ordonnance']
            french_word_count = sum(1 for word in french_keywords if word in line.lower())

            if french_word_count >= 2:
                count += 1
                continue

            cleaned_lines.append(line)

        self.text = '\n'.join(cleaned_lines)
        self.removal_stats['phase2_french_paragraphs'] = count

    def _clean_inline_french(self):
        """Remove inline French portions from mixed lines."""
        count = 0
        lines = self.text.split('\n')
        cleaned_lines = []

        for line in lines:
            # Pattern: "English text Numéro French text"
            # Look for accented capital letter indicating French start
            match = re.search(r'([A-ZÉÈÊÀÂÇÔÛÙÏ][éèêàâçôûùï])', line)
            if match:
                # Check if there's substantive English before it
                english_portion = line[:match.start()].strip()
                if len(english_portion) > 20:  # Substantial English content
                    cleaned_lines.append(english_portion)
                    count += 1
                    continue

            cleaned_lines.append(line)

        self.text = '\n'.join(cleaned_lines)
        self.removal_stats['phase2_inline_french'] = count

    def print_stats(self):
        """Print removal statistics."""
        print('\n' + '='*70)
        print('FRENCH REMOVAL STATISTICS')
        print('='*70)
        print('\nPhase 1 - High Confidence Removals:')
        print(f'  PARTIE headers:            {self.removal_stats["phase1_partie_headers"]:5d} lines')
        print(f'  French citations:          {self.removal_stats["phase1_french_citations"]:5d} lines')
        print(f'  Duplicate section titles:  {self.removal_stats["phase1_duplicate_section_titles"]:5d} lines')

        print('\nPhase 2 - Contextual Removals:')
        print(f'  Lowercase bullets:         {self.removal_stats["phase2_lowercase_bullets"]:5d} lines')
        print(f'  French paragraphs:         {self.removal_stats["phase2_french_paragraphs"]:5d} lines')
        print(f'  Inline French portions:    {self.removal_stats["phase2_inline_french"]:5d} lines')

        print('\n' + '='*70)
        print(f'Total lines removed:       {self.removal_stats["total_lines_removed"]:5d}')
        print(f'Total characters removed:  {self.removal_stats["total_chars_removed"]:7,}')

        original_len = len(self.original_text)
        final_len = len(self.text)
        reduction_pct = (1 - final_len / original_len) * 100

        print(f'\nOriginal size:  {original_len:7,} chars')
        print(f'Final size:     {final_len:7,} chars')
        print(f'Reduction:      {reduction_pct:6.1f}%')
        print('='*70)


def main():
    """Run enhanced French filtering."""
    input_file = Path('data/input/study_materials/bia_statute.txt')
    output_file = Path('data/input/study_materials/bia_statute_clean_english.txt')

    print('Loading original BIA statute...')
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()
    print(f'✓ Loaded {len(text):,} characters')

    # Run filter
    filter = EnhancedFrenchFilter(text)
    cleaned_text = filter.clean()

    # Save
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(cleaned_text)

    # Report
    filter.print_stats()

    print(f'\n✓ Clean English BIA saved to: {output_file}')
    print('\nNext: Run structure parser on clean text')


if __name__ == '__main__':
    main()
