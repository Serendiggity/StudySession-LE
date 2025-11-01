"""
Timeline sequence examples for Lang Extract training.
NEW CATEGORY for visualization support (swimlane diagrams).

These capture complete event sequences with:
- Timing of each step
- Responsible actor
- Required documents
- Dependencies
"""

import langextract as lx


# Example 1: Division I NOI Timeline - Your exact use case!
timeline_example_1 = lx.data.ExampleData(
    text="""
    4.3.7. Filing the Notice of Intention
    BIA s. 50.4(1)
    The insolvent person would file the Notice of Intention with the Official Receiver in his locale.

    4.3.8. Other documents to be filed
    Within ten days of filing the Notice of Intention the insolvent person must file the following
    with the Official Receiver: the Cash Flow Statement, signed by the Trustee and the insolvent person.

    4.3.9. Notification to Creditors
    Within five days of filing the Notice of Intention, the Trustee sends a copy of the Notice of
    Intention to every known creditor.

    Within 30 days of filing the Notice of Intention the insolvent person must either file the
    proposal, or ask for an extension of the delay to file a proposal.
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="timeline_sequence",
            extraction_text="Filing the Notice of Intention",
            attributes={
                "scenario_name": "Division I Proposal - Notice of Intention",
                "scenario_type": "Proposal",
                "total_duration": "30 days from NOI to proposal filing (extendable to 6 months)",
                "statutory_basis": "BIA s. 50.4"
            }
        )
    ]
)

# Example 2: Bankruptcy discharge timeline
timeline_example_2 = lx.data.ExampleData(
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
            extraction_class="timeline_sequence",
            extraction_text="Auto discharge at 9 months",
            attributes={
                "scenario_name": "Bankruptcy Discharge - First-time Bankrupt",
                "scenario_type": "Bankruptcy",
                "total_duration": "9 months (no surplus income) or 21 months (with surplus income)",
                "statutory_basis": "BIA"
            }
        )
    ]
)

# Example 3: Extension process
timeline_example_3 = lx.data.ExampleData(
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
            extraction_class="timeline_sequence",
            extraction_text="extension of the delay to file the proposal",
            attributes={
                "scenario_name": "Division I Proposal Extension Request",
                "scenario_type": "Proposal",
                "total_duration": "Maximum 6 months total including original 30 days",
                "statutory_basis": "BIA s. 50.4(9)"
            }
        )
    ]
)


# List of timeline sequence examples
timeline_examples = [
    timeline_example_1,
    timeline_example_2,
    timeline_example_3
]
