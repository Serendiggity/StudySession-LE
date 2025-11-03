"""
Extract missing BIA categories only.
Categories: concepts, deadlines, statutory_references, consequences
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

# Only missing categories
CATEGORIES = [
    'concepts',            # Statutory definitions - MISSING
    'deadlines',           # Time requirements - MISSING
    'statutory_references',# Section citations - MISSING
    'consequences'         # Deemed events - MISSING
]


def main():
    """Main extraction process."""
    logger.info('='*70)
    logger.info('BIA STATUTE - MISSING CATEGORIES EXTRACTION')
    logger.info('='*70)

    # Load text
    logger.info(f'\nLoading text from: {INPUT_TEXT}')
    with open(INPUT_TEXT, 'r', encoding='utf-8') as f:
        text = f.read()
    logger.info(f'✓ Loaded {len(text):,} characters (English-only)')

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Initialize extraction engine
    engine = ExtractionEngine(model_id='gemini-2.5-flash')

    # Extract missing categories
    logger.info(f'\nExtracting {len(CATEGORIES)} missing categories:')
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
    logger.info('EXTRACTION COMPLETE - MISSING CATEGORIES')
    logger.info('='*70)
    logger.info(f'Total entities extracted: {total_extracted:,}')
    logger.info(f'Output directory: {OUTPUT_DIR}')

    for category, result in results.items():
        logger.info(f'  {category:22s}: {len(result.extractions):5,} entities')

    logger.info('\n=== All BIA Categories Status ===')
    logger.info('Previously extracted:')
    logger.info('  documents          :   770 entities')
    logger.info('  actors             : 2,988 entities')
    logger.info('  procedures         : 1,318 entities')
    logger.info('\nNewly extracted:')
    for category, result in results.items():
        logger.info(f'  {category:19s}: {len(result.extractions):5,} entities')

    logger.info('\nNext step: Load all 7 categories into database with source_id=2')


if __name__ == '__main__':
    main()
