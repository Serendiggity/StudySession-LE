"""
Extract BIA in chunks to avoid stalls on large documents.

Strategy:
1. Split 784K char document into 4 chunks of ~200K each
2. Extract 3 missing categories from each chunk
3. Combine results

Missing categories: concepts, statutory_references, consequences
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import logging
from dotenv import load_dotenv
from extraction.extractor import ExtractionEngine
import json

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Paths
INPUT_TEXT = Path('data/input/study_materials/bia_statute_english_only.txt')
OUTPUT_DIR = Path('data/output/bia_extraction')
CHUNK_SIZE = 200000  # 200K chars per chunk

# Only the 3 missing categories
CATEGORIES = ['concepts', 'statutory_references', 'consequences']


def split_text(text: str, chunk_size: int):
    """Split text into chunks."""
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i+chunk_size]
        chunks.append({
            'chunk_id': len(chunks) + 1,
            'start_pos': i,
            'end_pos': i + len(chunk),
            'text': chunk,
            'size': len(chunk)
        })
    return chunks


def main():
    """Main extraction process."""
    logger.info('='*70)
    logger.info('BIA STATUTE - CHUNKED EXTRACTION (Final 3 Categories)')
    logger.info('='*70)

    # Load text
    logger.info(f'\nLoading text from: {INPUT_TEXT}')
    with open(INPUT_TEXT, 'r', encoding='utf-8') as f:
        text = f.read()
    logger.info(f'✓ Loaded {len(text):,} characters (English-only)')

    # Split into chunks
    chunks = split_text(text, CHUNK_SIZE)
    logger.info(f'\n✓ Split into {len(chunks)} chunks:')
    for chunk in chunks:
        logger.info(f"  Chunk {chunk['chunk_id']}: {chunk['size']:7,} chars (pos {chunk['start_pos']:7,} to {chunk['end_pos']:7,})")

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Initialize extraction engine
    engine = ExtractionEngine(model_id='gemini-2.5-flash')

    # Extract from each chunk
    logger.info(f'\nExtracting {len(CATEGORIES)} categories from each chunk...\n')

    all_results = {cat: {'extractions': []} for cat in CATEGORIES}

    for chunk in chunks:
        logger.info('='*70)
        logger.info(f"CHUNK {chunk['chunk_id']}/{len(chunks)} - Processing {chunk['size']:,} chars")
        logger.info('='*70)

        chunk_results = engine.extract_all_categories(
            text=chunk['text'],
            categories=CATEGORIES,
            passes=1,
            max_workers=5,
            output_dir=None  # Don't save yet, we'll combine first
        )

        # Adjust char positions and combine
        for category, result in chunk_results.items():
            for extraction in result.extractions:
                # Adjust character positions to global positions
                if 'char_interval' in extraction:
                    extraction['char_interval']['start_pos'] += chunk['start_pos']
                    extraction['char_interval']['end_pos'] += chunk['start_pos']

            # Add to combined results
            all_results[category]['extractions'].extend(result.extractions)

        # Progress
        for category, result in chunk_results.items():
            logger.info(f"  {category:22s}: +{len(result.extractions):4,} entities")

    # Save combined results
    logger.info('\n' + '='*70)
    logger.info('COMBINING AND SAVING RESULTS')
    logger.info('='*70)

    for category, data in all_results.items():
        output_file = OUTPUT_DIR / category
        with open(output_file, 'w') as f:
            json.dump(data, f)
        logger.info(f'✓ Saved {category:22s}: {len(data["extractions"]):5,} entities')

    # Final summary
    total_new = sum(len(data['extractions']) for data in all_results.values())
    logger.info('\n' + '='*70)
    logger.info('EXTRACTION COMPLETE - ALL CHUNKS PROCESSED')
    logger.info('='*70)
    logger.info(f'Total new entities: {total_new:,}')

    logger.info('\n=== COMPLETE BIA EXTRACTION (ALL 7 CATEGORIES) ===')
    logger.info('Previously extracted:')
    logger.info('  documents          :   770 entities')
    logger.info('  actors             : 2,988 entities')
    logger.info('  procedures         : 1,318 entities')
    logger.info('  deadlines          :   327 entities')
    logger.info('\nNewly extracted (chunked):')
    for category, data in all_results.items():
        logger.info(f'  {category:22s}: {len(data["extractions"]):5,} entities')

    grand_total = 5403 + total_new
    logger.info(f'\nGRAND TOTAL: {grand_total:,} BIA entities across all 7 categories!')
    logger.info('\n✓ Ready to load into database with source_id=2')


if __name__ == '__main__':
    main()
