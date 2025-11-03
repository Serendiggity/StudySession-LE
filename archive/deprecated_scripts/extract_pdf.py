#!/usr/bin/env python3
"""
Extract text from the insolvency PDF.
Phase 2: PDF Processing
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from document_processor.pdf_extractor import PDFExtractor
from document_processor.text_cleaner import TextCleaner
from utils.logging_config import setup_logging


def main():
    """Extract and clean text from insolvency PDF."""

    # Set up logging
    setup_logging()

    # Paths
    pdf_path = Path("Materials/Insolvency Administration - July 2020.pdf")
    output_path = Path("data/input/study_materials/insolvency_admin_extracted.txt")

    # Create output directory
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("PDF Text Extraction - Phase 2")
    print("=" * 60)
    print()

    # Check PDF exists
    if not pdf_path.exists():
        print(f"❌ PDF not found: {pdf_path}")
        print("Please ensure the PDF is in the Materials/ directory")
        return 1

    print(f"Input: {pdf_path.name}")
    print(f"Output: {output_path}")
    print()

    # Initialize extractor
    extractor = PDFExtractor()
    cleaner = TextCleaner()

    # Extract text
    print("Step 1: Extracting text from PDF...")
    print("(This may take 30-60 seconds for 291 pages)")
    print()

    try:
        raw_text = extractor.extract_text(pdf_path)
        print(f"✓ Extracted {len(raw_text):,} characters")
        print()

        # Get quality report
        print("Step 2: Validating extraction quality...")
        report = extractor.validate_extraction(pdf_path, raw_text)

        print(f"✓ Quality Report:")
        print(f"  • Total pages: {report.total_pages}")
        print(f"  • Total characters: {report.total_chars:,}")
        print(f"  • Avg chars/page: {report.avg_chars_per_page:.0f}")
        print(f"  • Method: {report.extraction_method}")

        if report.warnings:
            print(f"\n  Warnings:")
            for warning in report.warnings:
                print(f"    ⚠ {warning}")
        else:
            print(f"  • No quality issues detected ✓")

        print()

        # Clean text
        print("Step 3: Cleaning text...")
        cleaned_text = cleaner.clean(raw_text)
        print(f"✓ Cleaned text: {len(cleaned_text):,} characters")
        print(f"  • Removed: {len(raw_text) - len(cleaned_text):,} characters ({(len(raw_text) - len(cleaned_text))/len(raw_text)*100:.1f}%)")
        print()

        # Save to file
        print("Step 4: Saving to file...")
        output_path.write_text(cleaned_text, encoding='utf-8')
        print(f"✓ Saved to: {output_path}")
        print()

        # Show sample
        print("=" * 60)
        print("Sample (first 500 characters):")
        print("=" * 60)
        print(cleaned_text[:500])
        print("...")
        print()

        print("=" * 60)
        print("✓ Extraction Complete!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("  1. Review the extracted text quality")
        print("  2. Proceed to Phase 3: Create training examples")
        print()

        return 0

    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
