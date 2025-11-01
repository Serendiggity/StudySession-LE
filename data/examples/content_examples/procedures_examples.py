"""
Procedures examples for Lang Extract training.
Step-by-step processes in insolvency administration.
"""

import langextract as lx


# Example 1: Mediation procedure
procedures_example_1 = lx.data.ExampleData(
    text="""
    2.5.4. Mediation
    BIA s. 68
    Bankrupts have a right to disagree with certain decisions made by a Trustee and they can
    request that a third party review the situation. This process is called mediation. A bankrupt
    can request mediation if he does not agree with the amount of the monthly surplus income
    payments established by the Trustee.
    Usually, the mediation hearing will resolve the issue and the parties will agree on a
    settlement. However, if no agreement is made, the matter is then brought before the court
    and the court's decision is final.
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="procedure",
            extraction_text="mediation",
            attributes={
                "procedure_name": "Mediation Process",
                "purpose": "Resolve disagreements between bankrupt and Trustee through third-party review",
                "statutory_basis": "BIA s. 68"
            }
        )
    ]
)

# Example 2: Filing NOI procedure (from earlier)
procedures_example_2 = lx.data.ExampleData(
    text="""
    4.3.7. Filing the Notice of Intention
    BIA s. 50.4(1)
    BIA Form 33
    The insolvent person would file the Notice of Intention with the Official Receiver in his locale.
    The Notice of Intention states the following:
    the insolvent person's intention to make a proposal;
    the name and address of the Licensed Insolvency Trustee who has consented, in writing,
    to act as the Trustee in the proposal; and
    the names of creditors with claims amounting to $250 or more and the amounts of the
    claims, as known.
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="procedure",
            extraction_text="Filing the Notice of Intention",
            attributes={
                "procedure_name": "Filing Notice of Intention",
                "purpose": "Initiate Division I proposal process and obtain stay of proceedings",
                "statutory_basis": "BIA s. 50.4(1)"
            }
        )
    ]
)

# Example 3: Bankruptcy administration overview
procedures_example_3 = lx.data.ExampleData(
    text="""
    3.2. The bankruptcy administration process
    The next three pages illustrate the bankruptcy administration process. The key elements of
    each task are described in the pages following the process charts.
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="procedure",
            extraction_text="bankruptcy administration process",
            attributes={
                "procedure_name": "Bankruptcy Administration Process",
                "purpose": "Complete administration of bankruptcy estate from filing to discharge"
            }
        )
    ]
)

# Example 4: Assessment procedure
procedures_example_4 = lx.data.ExampleData(
    text="""
    Before filing a proposal, the Trustee must make an assessment of the debtor. The
    assessment process is discussed in detail in Module 2.
    For a debtor to file a proposal, the proposal must be more beneficial than bankruptcy. The
    Trustee will review the options available with the debtor during the assessment and the
    debtor will choose his best option.
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="procedure",
            extraction_text="Trustee must make an assessment of the debtor",
            attributes={
                "procedure_name": "Debtor Assessment",
                "purpose": "Review debtor's financial situation and determine available options",
                "prerequisites": ["Before filing proposal or bankruptcy"]
            }
        )
    ]
)


# List of procedure examples
procedures_examples = [
    procedures_example_1,
    procedures_example_2,
    procedures_example_3,
    procedures_example_4
]
