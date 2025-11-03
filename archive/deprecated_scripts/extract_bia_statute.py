"""
Extract entities from BIA Statute using proven ultra-minimal approach.

Categories:
- Concepts (statutory definitions)
- Procedures (requirements/obligations)
- Consequences (deemed events/outcomes)
- Statutory References (section citations)
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import logging
from dotenv import load_dotenv
from extraction.extractor import ExtractionEngine

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Paths
INPUT_TEXT = Path('data/input/study_materials/bia_statute_english_only.txt')  # English-filtered version
OUTPUT_DIR = Path('data/output/bia_extraction')

# Categories to extract (all 7 categories for comprehensive extraction)
CATEGORIES = [
    'concepts',            # Statutory definitions
    'deadlines',           # Time requirements (within X days)
    'documents',           # Forms, certificates, statements
    'actors',              # Roles (trustee, creditor, superintendent)
    'statutory_references',# Section citations (BIA s. X)
    'procedures',          # Requirements and obligations
    'consequences'         # Deemed events and outcomes
]


def main():
    """Main extraction process."""
    logger.info('='*70)
    logger.info('BIA STATUTE EXTRACTION - Ultra-Minimal Approach')
    logger.info('='*70)

    # Load text
    logger.info(f'\nLoading text from: {INPUT_TEXT}')
    with open(INPUT_TEXT, 'r', encoding='utf-8') as f:
        text = f.read()
    logger.info(f'✓ Loaded {len(text):,} characters')

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Initialize extraction engine
    engine = ExtractionEngine(model_id='gemini-2.5-flash')

    # Extract all categories
    logger.info(f'\nStarting extraction for {len(CATEGORIES)} categories:')
    for i, cat in enumerate(CATEGORIES, 1):
        logger.info(f'  {i}. {cat}')
    logger.info(f'\nUsing 1 pass (ultra-minimal = reliable on first pass)\n')

    results = engine.extract_all_categories(
        text=text,
        categories=CATEGORIES,
        passes=1,  # Ultra-minimal works reliably in single pass
        max_workers=5,  # Conservative to avoid rate limits
        output_dir=OUTPUT_DIR
    )

    # Summary
    total_extracted = sum(len(r.extractions) for r in results.values())
    logger.info('\n' + '='*70)
    logger.info('EXTRACTION COMPLETE')
    logger.info('='*70)
    logger.info(f'Total entities extracted: {total_extracted:,}')
    logger.info(f'Output directory: {OUTPUT_DIR}')

    for category, result in results.items():
        logger.info(f'  {category:22s}: {len(result.extractions):5,} entities')

    logger.info('\nNext step: Load into database with source_id=2')


if __name__ == '__main__':
    main()
