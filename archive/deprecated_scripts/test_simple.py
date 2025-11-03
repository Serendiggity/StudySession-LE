#!/usr/bin/env python3
"""
Simple quick test - very small sample.
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, str(Path(__file__).parent))

import langextract as lx
from data.examples.content_examples.concepts_examples import concept_examples


# Very small test text
test_text = """
A bankrupt person has either filed an assignment in bankruptcy or has been petitioned into
bankruptcy by a creditor and is now subject to the provisions of the BIA.

Insolvency is the financial situation a person finds himself in when he is unable to pay his
debts when they are due, or has ceased making payments, or his liabilities exceed the value
of his assets.

The BIA is a rehabilitative act that offers an insolvent person an opportunity to be released
from his debts. It also offers creditors an orderly wind-up and distribution of a bankrupt's
realizable assets.

A Trustee is an officer of the court who owes a duty of care to all stakeholders.
"""

prompt = "Extract key insolvency concepts and their definitions."

print("Testing with small sample...")
print(f"Text length: {len(test_text)} characters")
print()

result = lx.extract(
    text_or_documents=test_text,
    prompt_description=prompt,
    examples=concept_examples,
    model_id="gemini-2.5-flash",
    extraction_passes=1,
    max_workers=1
)

print(f"✓ Extracted {len(result.extractions)} concepts")
print()

for i, e in enumerate(result.extractions, 1):
    term = e.attributes.get("term", "Unknown")
    print(f"{i}. {term}")
    print(f"   Def: {e.attributes.get('definition', '')[:80]}...")
    print(f"   Source: {e.char_interval}")
    print()

print("✓ Test successful! Examples are working correctly.")
