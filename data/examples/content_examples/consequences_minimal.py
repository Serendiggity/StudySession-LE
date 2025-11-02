"""
ULTRA-minimal consequence examples - 1 ATTRIBUTE ONLY.
Just extract outcomes. Lang Extract will capture full context automatically.
"""

import langextract as lx


# Example 1: Deemed assignment
consequence_ultra_1 = lx.data.ExampleData(
    text="The person is deemed to have made an assignment in bankruptcy.",
    extractions=[
        lx.data.Extraction(
            extraction_class="consequence",
            extraction_text="deemed to have made an assignment in bankruptcy",
            attributes={
                "outcome": "deemed assignment in bankruptcy"
            }
        )
    ]
)

# Example 2: Stay of proceedings
consequence_ultra_2 = lx.data.ExampleData(
    text="The Stay of Proceedings takes effect immediately.",
    extractions=[
        lx.data.Extraction(
            extraction_class="consequence",
            extraction_text="Stay of Proceedings takes effect",
            attributes={
                "outcome": "Stay of Proceedings active"
            }
        )
    ]
)

# Example 3: Deemed accepted
consequence_ultra_3 = lx.data.ExampleData(
    text="The proposal is deemed accepted.",
    extractions=[
        lx.data.Extraction(
            extraction_class="consequence",
            extraction_text="deemed accepted",
            attributes={
                "outcome": "proposal deemed accepted"
            }
        )
    ]
)


consequences_minimal_examples = [
    consequence_ultra_1,
    consequence_ultra_2,
    consequence_ultra_3
]
