"""
Decision points examples for Lang Extract training.
NEW CATEGORY for flowchart generation.

Captures decision trees, options, and conditional branches.
"""

import langextract as lx


# Example 1: Division I vs Consumer Proposal decision
decision_example_1 = lx.data.ExampleData(
    text="""
    An individual may choose between filing a Division I and a consumer proposal (provided, of
    course, that he meets the criterion for a consumer proposal).
    During your interview, you may discuss the differences between the two types of proposals
    and the risks and benefits of each type.
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="decision_point",
            extraction_text="choose between filing a Division I and a consumer proposal",
            attributes={
                "decision_name": "Proposal Type Selection",
                "question": "Should debtor file Division I or Consumer Proposal?",
                "context": "Individual debtor choosing proposal type"
            }
        )
    ]
)

# Example 2: Proposal rejected - what happens?
decision_example_2 = lx.data.ExampleData(
    text="""
    What happens if
    creditors reject the
    proposal?

    There is an automatic
    bankruptcy. The Trustee will
    then realize upon all nonexempt assets owned by you
    for distribution to your
    creditors.

    There is no automatic bankruptcy
    but the rights of the creditors
    revive and they will seek full
    payment. You can make another
    consumer proposal (but there
    may not be a stay of proceedings)
    or you can decide to make an
    assignment in bankruptcy.
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="decision_point",
            extraction_text="What happens if creditors reject the proposal?",
            attributes={
                "decision_name": "Proposal Rejection Outcome",
                "question": "What happens if creditors reject the proposal?",
                "context": "After creditor vote on proposal"
            }
        )
    ]
)

# Example 3: Discharge timing decision
decision_example_3 = lx.data.ExampleData(
    text="""
    1st or 2nd
    time?
    Opposed?
    NO
    YES
    YES
    Book court date,
    notify creditors NO
    For personal bankruptcy

    Auto discharge at 9 months if no
    surplus income or at 21 months if
    surplus income

    Auto discharge at 24 months if no
    surplus income or at 36 months if
    surplus income

    3rd time or more
    Automatic discharge
    granted Court hearing
    •First-time Bankrupt
    •Second-time Bankrupt
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="decision_point",
            extraction_text="1st or 2nd time?",
            attributes={
                "decision_name": "Discharge Timing Decision",
                "question": "Is this first-time, second-time, or third+ time bankruptcy?",
                "context": "Determining automatic discharge eligibility and timing"
            }
        )
    ]
)


# List of decision point examples
decision_points_examples = [
    decision_example_1,
    decision_example_2,
    decision_example_3
]
