"""
BIA-specific consequence examples using formal statutory language.
"""

import langextract as lx


# Example 1: Deemed outcome
consequence_bia_1 = lx.data.ExampleData(
    text="the proceedings shall be continued as if the debtor were alive",
    extractions=[
        lx.data.Extraction(
            extraction_class="consequence",
            extraction_text="proceedings shall be continued as if the debtor were alive",
            attributes={"outcome": "proceedings continued as if debtor alive"}
        )
    ]
)

# Example 2: Deemed event
consequence_bia_2 = lx.data.ExampleData(
    text="the proposal is deemed to be refused by the creditors",
    extractions=[
        lx.data.Extraction(
            extraction_class="consequence",
            extraction_text="proposal is deemed to be refused",
            attributes={"outcome": "proposal deemed refused by creditors"}
        )
    ]
)

# Example 3: Automatic outcome
consequence_bia_3 = lx.data.ExampleData(
    text="the bankrupt shall be deemed to be automatically discharged from bankruptcy",
    extractions=[
        lx.data.Extraction(
            extraction_class="consequence",
            extraction_text="bankrupt shall be deemed to be automatically discharged",
            attributes={"outcome": "automatic discharge from bankruptcy"}
        )
    ]
)


consequences_bia_statute_examples = [
    consequence_bia_1,
    consequence_bia_2,
    consequence_bia_3
]
