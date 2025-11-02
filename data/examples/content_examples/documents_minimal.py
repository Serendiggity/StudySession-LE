"""
ULTRA-minimal document examples - 1 ATTRIBUTE ONLY.
Just extract document names. Lang Extract will capture full context automatically.
Based on actual PDF text patterns.
"""

import langextract as lx


# Example 1: BIA Form with rule reference
document_ultra_1 = lx.data.ExampleData(
    text="BIA Rule 129, Form 14 must be completed for the final statement.",
    extractions=[
        lx.data.Extraction(
            extraction_class="document",
            extraction_text="Form 14",
            attributes={
                "document_name": "Form 14"
            }
        )
    ]
)

# Example 2: Certificate
document_ultra_2 = lx.data.ExampleData(
    text="The Official Receiver will issue a Certificate of Assignment.",
    extractions=[
        lx.data.Extraction(
            extraction_class="document",
            extraction_text="Certificate of Assignment",
            attributes={
                "document_name": "Certificate of Assignment"
            }
        )
    ]
)

# Example 3: Statement
document_ultra_3 = lx.data.ExampleData(
    text="The Administrator will prepare the Statement of Receipts and Disbursements.",
    extractions=[
        lx.data.Extraction(
            extraction_class="document",
            extraction_text="Statement of Receipts and Disbursements",
            attributes={
                "document_name": "Statement of Receipts and Disbursements"
            }
        )
    ]
)


documents_minimal_examples = [
    document_ultra_1,
    document_ultra_2,
    document_ultra_3
]
