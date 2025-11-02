"""
Minimal procedure examples - 2-3 ATTRIBUTES.
Based on actual PDF text from Division I Proposal section.
Following the winning pattern from concepts_minimal.py
"""

import langextract as lx


# Example 1: Assessment step
procedure_minimal_1 = lx.data.ExampleData(
    text="The Trustee must make an assessment of the debtor before filing.",
    extractions=[
        lx.data.Extraction(
            extraction_class="procedure",
            extraction_text="make an assessment of the debtor",
            attributes={
                "step_name": "Assessment",
                "action": "Trustee assesses debtor"
            }
        )
    ]
)

# Example 2: Document preparation
procedure_minimal_2 = lx.data.ExampleData(
    text="Once the decision is made, the Trustee prepares documents for signature.",
    extractions=[
        lx.data.Extraction(
            extraction_class="procedure",
            extraction_text="prepares documents for signature",
            attributes={
                "step_name": "Document preparation",
                "action": "Trustee prepares documents",
                "order": 2
            }
        )
    ]
)

# Example 3: Filing step
procedure_minimal_3 = lx.data.ExampleData(
    text="The proposal is filed with the Official Receiver to become effective.",
    extractions=[
        lx.data.Extraction(
            extraction_class="procedure",
            extraction_text="filed with the Official Receiver",
            attributes={
                "step_name": "Filing",
                "action": "file with Official Receiver"
            }
        )
    ]
)


procedures_minimal_examples = [
    procedure_minimal_1,
    procedure_minimal_2,
    procedure_minimal_3
]
