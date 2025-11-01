"""
Statutory reference examples for Lang Extract training.
Based on BIA and CCAA references from Insolvency Administration study guide.

Following Lang Extract best practices:
- Use EXACT text from source
- No overlapping text spans
- 3-5 examples per category
"""

import langextract as lx


# Example 1: BIA s. 50.4(1) - NOI filing
statutory_example_1 = lx.data.ExampleData(
    text="""
    4.3.7. Filing the Notice of Intention
    BIA s. 50.4(1)
    BIA Form 33
    The insolvent person would file the Notice of Intention with the Official Receiver in his locale.
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="statutory_reference",
            extraction_text="BIA s. 50.4(1)",
            attributes={
                "act_name": "Bankruptcy and Insolvency Act",
                "section_number": "50.4",
                "subsection": "(1)",
                "practical_effect": "Governs filing of Notice of Intention with the Official Receiver",
                "frequency_of_reference": "very_common"
            }
        )
    ]
)

# Example 2: BIA s. 50.4(9) - Extension of time
statutory_example_2 = lx.data.ExampleData(
    text="""
    4.3.10. Extension of delay to file a proposal
    BIA s. 50.4(9)
    An insolvent person may apply for an extension of the delay to file the proposal before the
    expiration of the 30 days. The court may grant an extension for a period not exceeding 45
    days and may grant subsequent extensions of the delay, provided that the entire period,
    including the original 30 days, does not exceed 6 months.
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="statutory_reference",
            extraction_text="BIA s. 50.4(9)",
            attributes={
                "act_name": "Bankruptcy and Insolvency Act",
                "section_number": "50.4",
                "subsection": "(9)",
                "practical_effect": "Allows court to grant extensions for filing proposal - maximum 45 days per extension, 6 months total including original 30 days",
                "frequency_of_reference": "common"
            }
        )
    ]
)

# Example 3: BIA s. 50(1) - Who can file proposal
statutory_example_3 = lx.data.ExampleData(
    text="""
    4.3.2. Who can file a proposal?
    BIA s. 50(1)
    A Division I proposal can be made by:
    an insolvent person;
    a receiver, within the meaning of, but only in relation to, an insolvent person;
    a liquidator of an insolvent person's property;
    a bankrupt; or
    the Trustee of the estate of a bankrupt.
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="statutory_reference",
            extraction_text="BIA s. 50(1)",
            attributes={
                "act_name": "Bankruptcy and Insolvency Act",
                "section_number": "50",
                "subsection": "(1)",
                "practical_effect": "Defines who can file a Division I proposal: insolvent person, receiver, liquidator, bankrupt, or Trustee of bankrupt estate",
                "frequency_of_reference": "very_common"
            }
        )
    ]
)

# Example 4: BIA s. 2, 13.3-13.5 - Assigned reading reference
statutory_example_4 = lx.data.ExampleData(
    text="""
    Assigned reading
    BIA s. 2, 13.3-13.5, 16-38, 161 and 178
    BIA Rules 34-53
    Directive 5 - Estate Funds and Banking
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="statutory_reference",
            extraction_text="BIA s. 2",
            attributes={
                "act_name": "Bankruptcy and Insolvency Act",
                "section_number": "2",
                "practical_effect": "Contains definitions used throughout the BIA",
                "frequency_of_reference": "very_common"
            }
        )
    ]
)

# Example 5: BIA s. 50.4 - Filing requirements
statutory_example_5 = lx.data.ExampleData(
    text="""
    4.3.8. Other documents to be filed
    BIA s. 50.4
    BIA Forms 29 and 30
    Within ten days of filing the Notice of Intention the insolvent person must file the following
    with the Official Receiver:
    the Cash Flow Statement (containing a list of the significant assumptions on which it is
    premised), signed by the Trustee and the insolvent person
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="statutory_reference",
            extraction_text="BIA s. 50.4",
            attributes={
                "act_name": "Bankruptcy and Insolvency Act",
                "section_number": "50.4",
                "practical_effect": "Requires filing of cash flow statement and related reports within ten days of filing Notice of Intention",
                "frequency_of_reference": "very_common",
                "related_sections": ["s. 50.4(1)", "s. 50.4(9)"]
            }
        )
    ]
)


# List of all statutory reference examples
statutory_examples = [
    statutory_example_1,
    statutory_example_2,
    statutory_example_3,
    statutory_example_4,
    statutory_example_5
]
