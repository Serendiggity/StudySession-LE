"""
Text cleaning and normalization module.
Removes artifacts, normalizes whitespace, and prepares text for Lang Extract.
"""

import re
import logging
from typing import Optional


class TextCleaner:
    """
    Clean and normalize extracted PDF text.

    Handles common PDF extraction artifacts like:
    - Headers and footers
    - Page numbers
    - Excessive whitespace
    - Hyphenated words at line breaks
    - Section breaks and formatting marks
    """

    def __init__(self):
        """Initialize text cleaner with logging."""
        self.logger = logging.getLogger(__name__)

    def clean(self, text: str, aggressive: bool = False) -> str:
        """
        Full cleaning pipeline.

        Args:
            text: Raw text to clean
            aggressive: If True, apply more aggressive cleaning (may remove more content)

        Returns:
            Cleaned text
        """
        self.logger.info(f"Cleaning text ({len(text):,} chars)...")

        original_length = len(text)

        # Apply cleaning steps in order
        text = self.remove_artifacts(text)
        text = self.fix_hyphenation(text)
        text = self.normalize_whitespace(text)

        if aggressive:
            text = self.remove_headers_footers(text)

        final_length = len(text)
        removed = original_length - final_length
        percent_removed = (removed / original_length * 100) if original_length > 0 else 0

        self.logger.info(f"Cleaning complete: {final_length:,} chars ({percent_removed:.1f}% removed)")

        return text

    def remove_artifacts(self, text: str) -> str:
        """
        Remove common PDF artifacts.

        - Page numbers (standalone numbers on lines)
        - Multiple dashes/underscores (section breaks)
        - Form feed characters
        - Excessive punctuation
        """
        # Remove form feed characters
        text = text.replace('\f', '\n')

        # Remove standalone page numbers (number alone on a line)
        text = re.sub(r'\n\s*\d+\s*\n', '\n', text)

        # Remove multiple dashes or underscores (decorative breaks)
        text = re.sub(r'-{3,}', '', text)
        text = re.sub(r'_{3,}', '', text)
        text = re.sub(r'={3,}', '', text)

        # Remove multiple dots (except ellipsis)
        text = re.sub(r'\.{4,}', '...', text)

        return text

    def remove_headers_footers(self, text: str) -> str:
        """
        Attempt to remove headers and footers.

        This is challenging and may remove some valid content.
        Only use if extraction quality is poor.
        """
        lines = text.split('\n')
        cleaned_lines = []

        # Very basic heuristic: skip very short lines at regular intervals
        # This is a rough approach and should be refined based on actual PDF structure
        for i, line in enumerate(lines):
            # Skip extremely short lines (likely page numbers or headers)
            if len(line.strip()) < 5 and i > 0 and i < len(lines) - 1:
                continue
            cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def normalize_whitespace(self, text: str) -> str:
        """
        Standardize whitespace.

        - Replace multiple spaces with single space
        - Standardize line breaks (max 2 consecutive)
        - Remove trailing whitespace
        """
        # Replace multiple spaces with single space (but preserve intentional indentation)
        text = re.sub(r'  +', ' ', text)  # 2+ spaces become 1

        # Remove trailing whitespace from each line
        lines = [line.rstrip() for line in text.split('\n')]
        text = '\n'.join(lines)

        # Replace 3+ consecutive newlines with 2 (paragraph break)
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Remove leading/trailing whitespace from entire text
        text = text.strip()

        return text

    def fix_hyphenation(self, text: str) -> str:
        """
        Join hyphenated words at line breaks.

        PDF text often has words broken across lines:
        'insol-
        vency' should become 'insolvency'

        This is a heuristic and may occasionally join words incorrectly.
        """
        # Match: word ending with hyphen, newline, word continuing
        # (\w+)-\s*\n\s*(\w+) captures hyphenated word across line break
        text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)

        return text

    def remove_excessive_newlines_in_sentences(self, text: str) -> str:
        """
        Remove newlines that break sentences unnecessarily.

        Some PDFs have line breaks mid-sentence. This attempts to rejoin them.
        Use cautiously as it may affect formatting.
        """
        # If a line doesn't end with sentence-ending punctuation,
        # and next line doesn't start with capital/number,
        # join them with a space
        lines = text.split('\n')
        result = []

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            if i < len(lines) - 1:
                next_line = lines[i + 1].strip()

                # Check if current line ends with punctuation
                ends_with_punct = line and line[-1] in '.!?:;'

                # Check if next line starts with capital or number
                starts_with_cap = next_line and (next_line[0].isupper() or next_line[0].isdigit())

                # If line doesn't end with punct AND next doesn't start with cap,
                # likely the same sentence - join them
                if line and next_line and not ends_with_punct and not starts_with_cap:
                    result.append(line + ' ' + next_line)
                    i += 2  # Skip next line since we joined it
                    continue

            result.append(line)
            i += 1

        return '\n'.join(result)

    def preserve_legal_citations(self, text: str) -> str:
        """
        Ensure legal citations aren't broken by cleaning.

        Legal text has specific patterns like:
        - BIA s. 43(1)
        - Schedule B1, para 26
        - [2020] SCC 42

        This method protects these patterns from aggressive cleaning.
        Currently a placeholder for future enhancement.
        """
        # For now, just return text
        # Could add specific protections for legal citation patterns
        return text
