"""
Deadline examples for Lang Extract training.
CRITICAL CATEGORY - Deadlines with calculation methods.

Following Lang Extract best practices:
- Use EXACT text from source
- MUST capture calculation method (business days vs calendar days)
- Include triggering event and responsible party
"""

import langextract as lx


# Example 1: 10 days to file cash flow - Division I NOI
deadlines_example_1 = lx.data.ExampleData(
    text="""
    4.3.8. Other documents to be filed
    BIA s. 50.4
    BIA Forms 29 and 30
    Within ten days of filing the Notice of Intention the insolvent person must file the following
    with the Official Receiver:
    the Cash Flow Statement (containing a list of the significant assumptions on which it is
    premised), signed by the Trustee and the insolvent person;
    a report by the insolvent person regarding the preparation of the cash flow, prepared and
    signed by the insolvent person; and
    a report on the reasonableness of the Cash Flow, signed by the Trustee.
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="deadline",
            extraction_text="Within ten days of filing the Notice of Intention",
            attributes={
                "deadline_type": "Filing",
                "timeframe": "10 days",
                "calculation_method": "calendar_days",
                "triggering_event": "Filing of Notice of Intention with Official Receiver",
                "required_action": "File cash flow statement and related reports with Official Receiver",
                "required_documents": "Cash Flow Statement (Form 29), Report on cash flow preparation, Trustee's report on reasonableness (Form 30)",
                "responsible_party": "Insolvent person (with Trustee assistance)",
                "recipient": "Official Receiver",
                "communication_method": "E-filing with OSB",
                "statutory_reference": "BIA s. 50.4"
            }
        )
    ]
)

# Example 2: 30 days to file proposal
deadlines_example_2 = lx.data.ExampleData(
    text="""
    Within 30 days of filing the Notice of Intention the insolvent person must either file the
    proposal, or ask for an extension of the delay to file a proposal. In both cases, it will be
    necessary to file a revised Cash Flow Statement with the Official Receiver and, in the case of
    an extension of the delay, with the court.
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="deadline",
            extraction_text="Within 30 days of filing the Notice of Intention",
            attributes={
                "deadline_type": "Filing",
                "timeframe": "30 days",
                "calculation_method": "calendar_days",
                "triggering_event": "Filing of Notice of Intention",
                "required_action": "File the proposal OR request extension",
                "required_documents": "Proposal document, Revised Cash Flow Statement",
                "responsible_party": "Insolvent person",
                "recipient": "Official Receiver and Court (if extension)",
                "communication_method": "E-filing with OSB",
                "statutory_reference": "BIA s. 50.4",
                "extension_available": "Yes - up to 45 days per extension, maximum 6 months total"
            }
        )
    ]
)

# Example 3: 5 days to notify creditors
deadlines_example_3 = lx.data.ExampleData(
    text="""
    4.3.9. Notification to Creditors
    Within five days of filing the Notice of Intention, the Trustee sends a copy of the Notice of
    Intention to every known creditor.
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="deadline",
            extraction_text="Within five days of filing the Notice of Intention",
            attributes={
                "deadline_type": "Notice",
                "timeframe": "5 days",
                "calculation_method": "calendar_days",
                "triggering_event": "Filing of Notice of Intention",
                "required_action": "Send copy of Notice of Intention to every known creditor",
                "required_documents": "Copy of Notice of Intention (Form 33)",
                "responsible_party": "Trustee",
                "recipient": "All known creditors",
                "communication_method": "Mail to last known address",
                "statutory_reference": "BIA s. 50.4"
            }
        )
    ]
)

# Example 4: 15 days deemed acceptance
deadlines_example_4 = lx.data.ExampleData(
    text="""
    The proposal is deemed accepted
    by the court 15 days after creditor
    approval, unless a creditor, the
    Official Receiver or the
    Administrator requests a review
    by the court.
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="deadline",
            extraction_text="15 days after creditor approval",
            attributes={
                "deadline_type": "Deemed acceptance",
                "timeframe": "15 days",
                "calculation_method": "calendar_days",
                "triggering_event": "Creditor approval of proposal",
                "required_action": "Proposal deemed accepted by court (automatic)",
                "responsible_party": "Court (automatic process)",
                "recipient": "Debtor and creditors",
                "consequences_if_missed": "If review requested within 15 days, court hearing required"
            }
        )
    ]
)

# Example 5: Discharge timing - 9 months
deadlines_example_5 = lx.data.ExampleData(
    text="""
    •First-time Bankrupt

    Auto discharge at 9 months if no
    surplus income or at 21 months if
    surplus income

    •Second-time Bankrupt

    Auto discharge at 24 months if no
    surplus income or at 36 months if
    surplus income
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="deadline",
            extraction_text="Auto discharge at 9 months if no surplus income",
            attributes={
                "deadline_type": "Discharge",
                "timeframe": "9 months",
                "calculation_method": "calendar_days",
                "triggering_event": "Date of bankruptcy filing (first-time bankrupt)",
                "required_action": "Automatic discharge granted",
                "responsible_party": "Court (automatic)",
                "recipient": "Bankrupt person",
                "statutory_reference": "BIA",
                "common_pitfalls": "Extended to 21 months if surplus income exists"
            }
        )
    ]
)


# List of all deadline examples
deadlines_examples = [
    deadlines_example_1,
    deadlines_example_2,
    deadlines_example_3,
    deadlines_example_4,
    deadlines_example_5
]
