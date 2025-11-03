"""
Conservative BIA extraction: Small chunks, one category at a time.
NOW USING BIA-SPECIFIC EXAMPLES (formal statutory language patterns)

Strategy:
1. Split into 100K char chunks (smaller = more reliable)
2. Extract ONE category at a time across all chunks
3. Use BIA-specific examples (not study material examples)
4. Save after each category completes
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import logging
from dotenv import load_dotenv
import langextract as lx
import json

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Paths
INPUT_TEXT = Path('data/input/study_materials/bia_statute_english_only.txt')
OUTPUT_DIR = Path('data/output/bia_extraction')
CHUNK_SIZE = 100000  # 100K chars per chunk (conservative)

# Missing categories with their example definitions
CATEGORIES = {
    'concepts': 'content_examples.concepts_minimal',
    'statutory_references': 'content_examples.statutory_references_minimal',
    'consequences': 'content_examples.consequences_minimal'
}


def load_category_examples(category_name: str):
    """Load BIA-specific examples for a category."""
    import sys
    examples_dir = Path(__file__).parent.parent / 'data/examples'
    sys.path.insert(0, str(examples_dir))

    if category_name == 'concepts':
        from content_examples.concepts_bia_statute import concept_bia_statute_examples
        return concept_bia_statute_examples
    elif category_name == 'statutory_references':
        from content_examples.statutory_references_bia import statutory_references_bia_statute_examples
        return statutory_references_bia_statute_examples
    elif category_name == 'consequences':
        from content_examples.consequences_bia import consequences_bia_statute_examples
        return consequences_bia_statute_examples


def split_text(text: str, chunk_size: int):
    """Split text into chunks."""
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunk_text = text[i:i+chunk_size]
        chunks.append({
            'id': len(chunks) + 1,
            'start_pos': i,
            'text': chunk_text,
            'size': len(chunk_text)
        })
    return chunks


def extract_category_from_chunk(chunk, category_name: str, examples):
    """Extract single category from single chunk."""
    result = lx.extract(
        text_or_documents=chunk['text'],
        examples=examples,
        model_id='gemini-2.5-flash',
        extraction_passes=1,
        max_workers=5
    )
    return result


def main():
    """Main extraction process."""
    logger.info('='*70)
    logger.info('BIA STATUTE - CONSERVATIVE CHUNKED EXTRACTION')
    logger.info('='*70)

    # Load text
    logger.info(f'\nLoading: {INPUT_TEXT}')
    with open(INPUT_TEXT, 'r') as f:
        text = f.read()
    logger.info(f'✓ Loaded {len(text):,} characters')

    # Split into chunks
    chunks = split_text(text, CHUNK_SIZE)
    logger.info(f'\n✓ Split into {len(chunks)} chunks of ~{CHUNK_SIZE:,} chars each')

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Extract each category separately
    for category_idx, category_name in enumerate(CATEGORIES.keys(), 1):
        logger.info('\n' + '='*70)
        logger.info(f'CATEGORY {category_idx}/3: {category_name.upper()}')
        logger.info('='*70)

        # Load examples
        examples = load_category_examples(category_name)
        logger.info(f'Loaded {len(examples)} examples')

        # Extract from each chunk and combine
        combined_result = None

        for chunk in chunks:
            logger.info(f"\nChunk {chunk['id']}/{len(chunks)}: Extracting from {chunk['size']:,} chars...")

            try:
                result = extract_category_from_chunk(chunk, category_name, examples)
                logger.info(f"  ✓ Extracted {len(result.extractions):4,} entities")

                # Adjust char positions for this chunk
                for extraction in result.extractions:
                    if hasattr(extraction, 'char_interval') and extraction.char_interval:
                        extraction.char_interval.start_pos += chunk['start_pos']
                        extraction.char_interval.end_pos += chunk['start_pos']

                # Combine with previous results
                if combined_result is None:
                    combined_result = result
                else:
                    combined_result.extractions.extend(result.extractions)

            except Exception as e:
                logger.error(f"  ✗ Error on chunk {chunk['id']}: {e}")
                import traceback
                traceback.print_exc()
                continue

        # Save combined results using Lang Extract's built-in method
        logger.info(f'\n✓ All chunks processed for {category_name}')
        logger.info(f'✓ Total entities: {len(combined_result.extractions):,}')
        logger.info(f'✓ Saving to {OUTPUT_DIR}/{category_name}...')

        lx.io.save_annotated_documents(
            [combined_result],
            output_name=category_name,
            output_dir=str(OUTPUT_DIR)
        )

        logger.info(f'✓ Saved {category_name}: {len(combined_result.extractions):,} total entities')

    # Final summary
    logger.info('\n' + '='*70)
    logger.info('EXTRACTION COMPLETE - ALL 3 CATEGORIES')
    logger.info('='*70)

    total_new = 0
    for category_name in CATEGORIES.keys():
        output_file = OUTPUT_DIR / category_name
        with open(output_file, 'r') as f:
            data = json.load(f)
        count = len(data['extractions'])
        total_new += count
        logger.info(f'  {category_name:22s}: {count:5,} entities')

    logger.info(f'\nTotal new entities: {total_new:,}')
    logger.info(f'Combined with existing: {5403 + total_new:,} BIA entities')
    logger.info('\n✓ ALL 7 BIA CATEGORIES COMPLETE!')


if __name__ == '__main__':
    main()
