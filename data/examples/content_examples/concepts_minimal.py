"""
MINIMAL concept examples to debug JSON parsing.
Ultra-simple attributes to verify extraction works.
"""

import langextract as lx


# Example 1: Minimal - just term
concept_minimal_1 = lx.data.ExampleData(
    text="Insolvency is when debts exceed assets.",
    extractions=[
        lx.data.Extraction(
            extraction_class="concept",
            extraction_text="Insolvency",
            attributes={"term": "Insolvency"}
        )
    ]
)

# Example 2: Minimal - term + short definition
concept_minimal_2 = lx.data.ExampleData(
    text="A Trustee administers bankruptcy estates.",
    extractions=[
        lx.data.Extraction(
            extraction_class="concept",
            extraction_text="Trustee",
            attributes={
                "term": "Trustee",
                "definition": "Administers bankruptcy estates"
            }
        )
    ]
)

# Example 3: Minimal - three attributes max
concept_minimal_3 = lx.data.ExampleData(
    text="The BIA governs bankruptcy in Canada.",
    extractions=[
        lx.data.Extraction(
            extraction_class="concept",
            extraction_text="BIA",
            attributes={
                "term": "BIA",
                "definition": "Governs bankruptcy in Canada",
                "importance": "high"
            }
        )
    ]
)


concept_minimal_examples = [
    concept_minimal_1,
    concept_minimal_2,
    concept_minimal_3
]
