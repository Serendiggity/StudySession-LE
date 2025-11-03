"""
BIA-specific statutory reference examples using formal citation patterns.
"""

import langextract as lx


# Example 1: Simple R.S.C. citation
statutory_ref_bia_1 = lx.data.ExampleData(
    text="R.S., 1985, c. B-3, s. 43; 1992, c. 27, s. 15",
    extractions=[
        lx.data.Extraction(
            extraction_class="statutory_reference",
            extraction_text="R.S., 1985, c. B-3, s. 43",
            attributes={"reference": "R.S., 1985, c. B-3, s. 43"}
        )
    ]
)

# Example 2: Section reference
statutory_ref_bia_2 = lx.data.ExampleData(
    text="pursuant to section 50.4 of this Act",
    extractions=[
        lx.data.Extraction(
            extraction_class="statutory_reference",
            extraction_text="section 50.4",
            attributes={"reference": "section 50.4"}
        )
    ]
)

# Example 3: Subsection reference
statutory_ref_bia_3 = lx.data.ExampleData(
    text="as defined in subsection 2(1) of the Bank Act",
    extractions=[
        lx.data.Extraction(
            extraction_class="statutory_reference",
            extraction_text="subsection 2(1)",
            attributes={"reference": "subsection 2(1)"}
        )
    ]
)


statutory_references_bia_statute_examples = [
    statutory_ref_bia_1,
    statutory_ref_bia_2,
    statutory_ref_bia_3
]
