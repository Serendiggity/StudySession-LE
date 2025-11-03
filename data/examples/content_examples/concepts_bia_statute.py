"""
BIA-specific concept examples using formal statutory definition language.
Based on actual BIA statute section 2 definitions.
"""

import langextract as lx


# Example 1: Simple statutory definition
concept_bia_1 = lx.data.ExampleData(
    text="bankrupt means a person who has made an assignment or against whom a bankruptcy order has been made",
    extractions=[
        lx.data.Extraction(
            extraction_class="concept",
            extraction_text="bankrupt",
            attributes={"term": "bankrupt"}
        )
    ]
)

# Example 2: Definition with "means"
concept_bia_2 = lx.data.ExampleData(
    text="creditor means a person having a claim provable as a claim under this Act",
    extractions=[
        lx.data.Extraction(
            extraction_class="concept",
            extraction_text="creditor",
            attributes={
                "term": "creditor",
                "definition": "person having a claim provable as a claim under this Act"
            }
        )
    ]
)

# Example 3: Definition with "includes"
concept_bia_3 = lx.data.ExampleData(
    text="debtor includes an insolvent person and any person who, at the time an act of bankruptcy was committed by him, resided or carried on business in Canada",
    extractions=[
        lx.data.Extraction(
            extraction_class="concept",
            extraction_text="debtor",
            attributes={
                "term": "debtor",
                "definition": "includes an insolvent person and any person who resided or carried on business in Canada",
                "importance": "high"
            }
        )
    ]
)


concept_bia_statute_examples = [
    concept_bia_1,
    concept_bia_2,
    concept_bia_3
]
