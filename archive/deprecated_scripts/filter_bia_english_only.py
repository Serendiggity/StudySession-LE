"""
Filter BIA statute to English-only text.
Removes French sections to reduce file size and improve extraction speed.
"""

from pathlib import Path
import re

def is_likely_french(text: str) -> bool:
    """Detect if text is likely French."""
    if len(text.strip()) < 20:
        return False

    # French-specific characters (higher density = French)
    french_chars = 'éèêàâçôûùïÉÈÊÀÂÇÔÛÙÏ'
    french_char_count = sum(text.count(c) for c in french_chars)
    french_density = french_char_count / len(text) if len(text) > 0 else 0

    # French keywords
    french_keywords = [
        'faillite', 'syndic', 'créancier', 'débiteur',
        'loi sur', 'article', 'alinéa', 'paragraphe',
        'Faillite', 'Syndic', 'Créancier', 'Débiteur',
        'proposant', 'ordonnance', 'tribunal'
    ]
    french_word_count = sum(text.lower().count(word) for word in french_keywords)

    # Thresholds
    if french_density > 0.015:  # > 1.5% French chars
        return True
    if french_word_count >= 3:  # 3+ French keywords
        return True

    return False


def filter_english_only(input_file: Path, output_file: Path):
    """Filter BIA text to English-only."""

    print(f'Reading: {input_file}')
    with open(input_file, 'r', encoding='utf-8') as f:
        full_text = f.read()

    print(f'Original size: {len(full_text):,} characters')

    # Split into paragraphs
    paragraphs = full_text.split('\n')

    # Filter out French paragraphs
    english_paragraphs = []
    french_removed = 0

    for para in paragraphs:
        if is_likely_french(para):
            french_removed += 1
        else:
            english_paragraphs.append(para)

    # Rejoin
    english_text = '\n'.join(english_paragraphs)

    # Save
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(english_text)

    print(f'✓ Filtered size: {len(english_text):,} characters')
    print(f'✓ Reduction: {len(full_text) - len(english_text):,} characters ({(1 - len(english_text)/len(full_text))*100:.1f}%)')
    print(f'✓ French paragraphs removed: {french_removed:,}')
    print(f'✓ Saved to: {output_file}')


if __name__ == '__main__':
    input_file = Path('data/input/study_materials/bia_statute.txt')
    output_file = Path('data/input/study_materials/bia_statute_english_only.txt')

    filter_english_only(input_file, output_file)
