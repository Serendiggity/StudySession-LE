"""
PDF text extraction module.
Supports extracting text from PDF files using pypdf (primary) and pdfplumber (fallback).
"""

import logging
from pathlib import Path
from typing import List, Optional, Dict
from dataclasses import dataclass
import pypdf
import pdfplumber


@dataclass
class Page:
    """Represents a single page from a PDF document."""
    number: int
    text: str
    char_count: int


@dataclass
class QualityReport:
    """Quality assessment of PDF text extraction."""
    total_pages: int
    total_chars: int
    avg_chars_per_page: float
    pages_with_low_content: List[int]  # Pages with <50 chars
    pages_with_errors: List[int]
    extraction_method: str
    warnings: List[str]


class PDFExtractor:
    """
    Extract text from PDF documents.

    Uses pypdf as primary extraction method with pdfplumber as fallback
    for complex layouts or when pypdf fails.
    """

    def __init__(self):
        """Initialize PDF extractor with logging."""
        self.logger = logging.getLogger(__name__)

    def extract_text(self, pdf_path: Path) -> str:
        """
        Extract all text from PDF as a single string.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Extracted text as a single string

        Raises:
            FileNotFoundError: If PDF file doesn't exist
            Exception: If both extraction methods fail
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        self.logger.info(f"Extracting text from: {pdf_path.name}")

        try:
            text = self._extract_with_pypdf(pdf_path)
            self.logger.info(f"Successfully extracted {len(text):,} characters using pypdf")
            return text
        except Exception as e:
            self.logger.warning(f"pypdf extraction failed: {e}")
            self.logger.info("Falling back to pdfplumber...")
            try:
                text = self._extract_with_pdfplumber(pdf_path)
                self.logger.info(f"Successfully extracted {len(text):,} characters using pdfplumber")
                return text
            except Exception as e2:
                self.logger.error(f"pdfplumber extraction also failed: {e2}")
                raise Exception(f"Both extraction methods failed. pypdf: {e}, pdfplumber: {e2}")

    def extract_with_structure(self, pdf_path: Path) -> List[Page]:
        """
        Extract text maintaining page structure.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            List of Page objects, one per PDF page
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        self.logger.info(f"Extracting structured text from: {pdf_path.name}")

        try:
            pages = self._extract_pages_with_pypdf(pdf_path)
            self.logger.info(f"Extracted {len(pages)} pages using pypdf")
            return pages
        except Exception as e:
            self.logger.warning(f"pypdf extraction failed: {e}")
            self.logger.info("Falling back to pdfplumber...")
            pages = self._extract_pages_with_pdfplumber(pdf_path)
            self.logger.info(f"Extracted {len(pages)} pages using pdfplumber")
            return pages

    def validate_extraction(self, pdf_path: Path, text: Optional[str] = None) -> QualityReport:
        """
        Validate quality of extracted text.

        Args:
            pdf_path: Path to the PDF file
            text: Extracted text to validate (if None, will extract)

        Returns:
            QualityReport with quality metrics and warnings
        """
        if text is None:
            text = self.extract_text(pdf_path)

        pages = self.extract_with_structure(pdf_path)

        total_chars = sum(p.char_count for p in pages)
        avg_chars = total_chars / len(pages) if pages else 0

        # Check for pages with low content
        low_content_pages = [p.number for p in pages if p.char_count < 50]

        # Check for potential errors (empty pages, unusual patterns)
        error_pages = [p.number for p in pages if p.char_count == 0]

        warnings = []

        if len(low_content_pages) > len(pages) * 0.1:  # More than 10% low content
            warnings.append(f"{len(low_content_pages)} pages have very low content (<50 chars)")

        if error_pages:
            warnings.append(f"{len(error_pages)} pages are completely empty")

        if avg_chars < 500:
            warnings.append(f"Average chars/page ({avg_chars:.0f}) is quite low - may indicate OCR issues")

        method = "pypdf"  # Could track which method was used

        report = QualityReport(
            total_pages=len(pages),
            total_chars=total_chars,
            avg_chars_per_page=avg_chars,
            pages_with_low_content=low_content_pages,
            pages_with_errors=error_pages,
            extraction_method=method,
            warnings=warnings
        )

        return report

    def _extract_with_pypdf(self, pdf_path: Path) -> str:
        """Extract text using pypdf library."""
        text_parts = []

        with open(pdf_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            total_pages = len(pdf_reader.pages)

            self.logger.info(f"Processing {total_pages} pages with pypdf...")

            for page_num, page in enumerate(pdf_reader.pages, 1):
                page_text = page.extract_text()
                text_parts.append(page_text)

                if page_num % 50 == 0:  # Log progress every 50 pages
                    self.logger.info(f"Processed {page_num}/{total_pages} pages...")

        return "\n\n".join(text_parts)

    def _extract_with_pdfplumber(self, pdf_path: Path) -> str:
        """Extract text using pdfplumber library (fallback)."""
        text_parts = []

        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)

            self.logger.info(f"Processing {total_pages} pages with pdfplumber...")

            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)

                if page_num % 50 == 0:
                    self.logger.info(f"Processed {page_num}/{total_pages} pages...")

        return "\n\n".join(text_parts)

    def _extract_pages_with_pypdf(self, pdf_path: Path) -> List[Page]:
        """Extract pages with structure using pypdf."""
        pages = []

        with open(pdf_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)

            for page_num, page in enumerate(pdf_reader.pages, 1):
                text = page.extract_text()
                pages.append(Page(
                    number=page_num,
                    text=text,
                    char_count=len(text)
                ))

        return pages

    def _extract_pages_with_pdfplumber(self, pdf_path: Path) -> List[Page]:
        """Extract pages with structure using pdfplumber."""
        pages = []

        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text() or ""
                pages.append(Page(
                    number=page_num,
                    text=text,
                    char_count=len(text)
                ))

        return pages
