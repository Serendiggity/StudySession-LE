#!/usr/bin/env python3
"""
Most basic test - verify API and examples work.
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, str(Path(__file__).parent))

import langextract as lx

# Simplest possible example
simple_example = lx.data.ExampleData(
    text="Insolvency is when a person cannot pay debts when due.",
    extractions=[
        lx.data.Extraction(
            extraction_class="concept",
            extraction_text="Insolvency",
            attributes={"term": "Insolvency"}
        )
    ]
)

test_text = """
A Trustee is an officer of the court.
Bankruptcy is a legal process.
The BIA governs insolvency in Canada.
"""

print("Running basic extraction test...")

try:
    result = lx.extract(
        text_or_documents=test_text,
        prompt_description="Extract insolvency concepts.",
        examples=[simple_example],
        model_id="gemini-2.5-flash"
    )

    print(f"✓ SUCCESS! Extracted {len(result.extractions)} items")
    for e in result.extractions:
        print(f"  - {e.extraction_text}")
    print()
    print("Your examples work! Paid tier is active and faster.")

except Exception as e:
    print(f"❌ Failed: {e}")
