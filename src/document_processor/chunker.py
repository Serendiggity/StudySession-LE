"""
Smart text chunking module for Lang Extract.
Creates overlapping chunks that respect context boundaries.
"""

import logging
from typing import List
from dataclasses import dataclass


@dataclass
class Chunk:
    """Represents a chunk of text with metadata."""
    text: str
    start_char: int
    end_char: int
    token_count: int
    chunk_index: int


class SmartChunker:
    """
    Create smart, context-aware chunks for Lang Extract processing.

    Chunks text while:
    - Respecting natural boundaries (paragraphs, sentences)
    - Maintaining overlap to avoid missing context
    - Staying within token limits
    - Preserving character positions for source grounding
    """

    def __init__(self, max_tokens: int = 8000, overlap: int = 500):
        """
        Initialize chunker.

        Args:
            max_tokens: Maximum tokens per chunk (default: 8000)
                       Gemini supports up to 128K, but smaller chunks work better
            overlap: Number of tokens to overlap between chunks (default: 500)
                    Ensures context isn't lost at boundaries
        """
        self.max_tokens = max_tokens
        self.overlap = overlap
        self.logger = logging.getLogger(__name__)

        # Rough estimation: 1 token ≈ 4 characters for English text
        self.chars_per_token = 4
        self.max_chars = max_tokens * self.chars_per_token
        self.overlap_chars = overlap * self.chars_per_token

    def chunk_text(self, text: str) -> List[Chunk]:
        """
        Create overlapping chunks from text.

        Args:
            text: Full text to chunk

        Returns:
            List of Chunk objects
        """
        self.logger.info(f"Chunking text ({len(text):,} chars, max_chunk={self.max_chars:,})...")

        chunks = []
        start = 0
        chunk_index = 0

        while start < len(text):
            # Calculate end position
            end = min(start + self.max_chars, len(text))

            # Find good break point if not at end of text
            if end < len(text):
                end = self._find_break_point(text, start, end)

            # Extract chunk text
            chunk_text = text[start:end]

            # Estimate tokens
            token_count = len(chunk_text) // self.chars_per_token

            # Create chunk
            chunk = Chunk(
                text=chunk_text,
                start_char=start,
                end_char=end,
                token_count=token_count,
                chunk_index=chunk_index
            )

            chunks.append(chunk)
            chunk_index += 1

            # Move start position for next chunk (with overlap)
            if end < len(text):
                start = end - self.overlap_chars
                # Ensure we don't go backwards
                start = max(start, 0)
            else:
                break

        self.logger.info(f"Created {len(chunks)} chunks (avg {len(text)//len(chunks):,} chars/chunk)")

        return chunks

    def _find_break_point(self, text: str, start: int, end: int) -> int:
        """
        Find a good break point for chunking.

        Preference order:
        1. Double newline (paragraph break) - best
        2. Single newline + capital letter (new sentence)
        3. Period + space (sentence end)
        4. Any whitespace
        5. Original position (if no good break found)

        Args:
            text: Full text
            start: Start position of chunk
            end: Desired end position

        Returns:
            Actual end position (at good break point)
        """
        # Don't look too far back from desired end
        search_start = max(start, end - (self.max_chars // 4))

        # Look for paragraph break (double newline)
        para_break = text.rfind('\n\n', search_start, end)
        if para_break > search_start:
            self.logger.debug(f"Found paragraph break at {para_break}")
            return para_break + 2  # Include the double newline

        # Look for single newline followed by capital letter (likely new sentence/section)
        for i in range(end - 1, search_start, -1):
            if text[i] == '\n' and i + 1 < len(text) and text[i + 1].isupper():
                self.logger.debug(f"Found sentence break at {i}")
                return i + 1

        # Look for sentence ending (period + space)
        sent_break = text.rfind('. ', search_start, end)
        if sent_break > search_start:
            self.logger.debug(f"Found sentence end at {sent_break}")
            return sent_break + 2  # After the period and space

        # Look for any whitespace
        space_break = text.rfind(' ', search_start, end)
        if space_break > search_start:
            self.logger.debug(f"Found space break at {space_break}")
            return space_break + 1

        # No good break point found - use original end
        self.logger.warning(f"No good break point found, using position {end}")
        return end

    def chunk_by_pages(self, pages: List[str], pages_per_chunk: int = 10) -> List[Chunk]:
        """
        Chunk text by PDF pages (alternative to token-based chunking).

        Args:
            pages: List of page texts
            pages_per_chunk: Number of pages per chunk

        Returns:
            List of Chunk objects
        """
        self.logger.info(f"Chunking {len(pages)} pages into groups of {pages_per_chunk}...")

        chunks = []
        chunk_index = 0
        start_char = 0

        for i in range(0, len(pages), pages_per_chunk):
            page_group = pages[i:i + pages_per_chunk]
            chunk_text = '\n\n'.join(page_group)

            chunk = Chunk(
                text=chunk_text,
                start_char=start_char,
                end_char=start_char + len(chunk_text),
                token_count=len(chunk_text) // self.chars_per_token,
                chunk_index=chunk_index
            )

            chunks.append(chunk)
            chunk_index += 1
            start_char += len(chunk_text)

        self.logger.info(f"Created {len(chunks)} page-based chunks")

        return chunks
