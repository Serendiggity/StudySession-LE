"""
Pitfalls examples for Lang Extract training.
Common mistakes and traps for the unwary.

Very useful for exam prep!
"""

import langextract as lx


# Example 1: Proposal must be more beneficial than bankruptcy
pitfalls_example_1 = lx.data.ExampleData(
    text="""
    For a debtor to file a proposal, the proposal must be more beneficial than bankruptcy. The
    Trustee will review the options available with the debtor during the assessment and the
    debtor will choose his best option. It is important to note that the final decision has to be the
    debtor's, as he is the party affected by this decision.
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="pitfall",
            extraction_text="the final decision has to be the debtor's",
            attributes={
                "pitfall_description": "Trustee making decision for debtor instead of letting debtor choose",
                "why_problematic": "Debtor is the party affected and must make the final decision; Trustee role is advisory only",
                "consequences": "Proposal may be challenged; Trustee liability; Professional misconduct",
                "how_to_avoid": "Ensure debtor makes informed decision after reviewing all options; document that decision was debtor's choice",
                "related_procedure": "Debtor assessment"
            }
        )
    ]
)

# Example 2: No backtracking from Division I proposal
pitfalls_example_2 = lx.data.ExampleData(
    text="""
    Can I change my
    mind after filing a
    proposal and
    request that it be
    withdrawn?

    No – there is no possibility of
    backtracking without special
    permission from the court. If
    the proposal is not filed or not
    accepted, a bankruptcy
    occurs.
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="pitfall",
            extraction_text="no possibility of backtracking without special permission from the court",
            attributes={
                "pitfall_description": "Assuming Division I proposal can be withdrawn like consumer proposal",
                "why_problematic": "Division I proposal cannot be withdrawn without court permission; leads to automatic bankruptcy if rejected",
                "consequences": "Automatic bankruptcy if proposal not accepted; cannot simply withdraw",
                "how_to_avoid": "Ensure debtor understands irrevocable nature of Division I proposal before filing; consider consumer proposal if flexibility needed",
                "related_deadline": "Proposal filing decision"
            }
        )
    ]
)

# Example 3: Corporations cannot file consumer proposal
pitfalls_example_3 = lx.data.ExampleData(
    text="""
    A consumer (Division II) proposal is available only to a natural person whose aggregate
    debts, excluding any debts secured by the person's principal residence, do not exceed
    $250,000 or such other maximum as is prescribed. Corporations cannot file a consumer
    proposal.
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="pitfall",
            extraction_text="Corporations cannot file a consumer proposal",
            attributes={
                "pitfall_description": "Attempting to file consumer proposal for a corporation",
                "why_problematic": "Consumer proposals are only available to natural persons (individuals), not corporations",
                "consequences": "Proposal will be rejected; must file Division I proposal instead",
                "how_to_avoid": "Verify debtor is individual before advising on consumer proposal; corporations must use Division I",
                "related_requirement": "Consumer proposal eligibility"
            }
        )
    ]
)


# List of pitfall examples
pitfalls_examples = [
    pitfalls_example_1,
    pitfalls_example_2,
    pitfalls_example_3
]
