"""
ULTRA-minimal actor examples - 1 ATTRIBUTE ONLY.
Just extract role names. Lang Extract will capture full context automatically.
"""

import langextract as lx


# Example 1: Trustee
actor_ultra_1 = lx.data.ExampleData(
    text="The Trustee administers the estate.",
    extractions=[
        lx.data.Extraction(
            extraction_class="actor",
            extraction_text="Trustee",
            attributes={
                "role": "Trustee"
            }
        )
    ]
)

# Example 2: Official Receiver
actor_ultra_2 = lx.data.ExampleData(
    text="The Official Receiver processes filings.",
    extractions=[
        lx.data.Extraction(
            extraction_class="actor",
            extraction_text="Official Receiver",
            attributes={
                "role": "Official Receiver"
            }
        )
    ]
)

# Example 3: Creditors
actor_ultra_3 = lx.data.ExampleData(
    text="Creditors vote on the proposal.",
    extractions=[
        lx.data.Extraction(
            extraction_class="actor",
            extraction_text="Creditors",
            attributes={
                "role": "Creditors"
            }
        )
    ]
)


actors_minimal_examples = [
    actor_ultra_1,
    actor_ultra_2,
    actor_ultra_3
]
