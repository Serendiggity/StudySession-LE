"""
ULTRA-minimal statutory reference examples - 1 ATTRIBUTE ONLY.
Just extract the reference. Lang Extract will capture full context automatically.
"""

import langextract as lx


# Example 1: BIA section
statutory_ultra_1 = lx.data.ExampleData(
    text="BIA s. 50.4 governs filing requirements.",
    extractions=[
        lx.data.Extraction(
            extraction_class="statutory_reference",
            extraction_text="BIA s. 50.4",
            attributes={
                "reference": "BIA s. 50.4"
            }
        )
    ]
)

# Example 2: Form reference
statutory_ultra_2 = lx.data.ExampleData(
    text="File Form 33 with the Official Receiver.",
    extractions=[
        lx.data.Extraction(
            extraction_class="statutory_reference",
            extraction_text="Form 33",
            attributes={
                "reference": "Form 33"
            }
        )
    ]
)

# Example 3: CCAA reference
statutory_ultra_3 = lx.data.ExampleData(
    text="CCAA s. 11 allows for court-supervised reorganization.",
    extractions=[
        lx.data.Extraction(
            extraction_class="statutory_reference",
            extraction_text="CCAA s. 11",
            attributes={
                "reference": "CCAA s. 11"
            }
        )
    ]
)


statutory_references_minimal_examples = [
    statutory_ultra_1,
    statutory_ultra_2,
    statutory_ultra_3
]
