"""
Role obligations examples for Lang Extract training.
Captures duties, powers, and prohibitions for each role in insolvency.

Critical for swimlane diagrams - shows WHO does WHAT.
"""

import langextract as lx


# Example 1: Trustee - Duty of care
role_example_1 = lx.data.ExampleData(
    text="""
    A Trustee is an officer of the court who owes a duty of care to all stakeholders.
    A Trustee operates in a position of trust and must maintain a high standard of ethics in the
    administration of his duties.
    A Trustee can delegate certain duties, but is ultimately responsible for all actions taken by
    individuals under his supervision.
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="role_obligation",
            extraction_text="owes a duty of care to all stakeholders",
            attributes={
                "role_type": "Trustee",
                "obligation_type": "Duty",
                "description": "Owes duty of care to all stakeholders and must maintain high standard of ethics",
                "to_whom_owed": "All stakeholders (creditors, debtor, court, OSB)",
                "statutory_basis": "BIA"
            }
        )
    ]
)

# Example 2: Trustee - Financial assessment requirement
role_example_2 = lx.data.ExampleData(
    text="""
    1.5.1. Licensed Insolvency Trustee:
    must complete a financial assessment of the debtor's circumstances and provide him with
    the various options available;
    has a duty of care to both the debtor and the creditors and must remain impartial while
    completing the administration of the estate;
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="role_obligation",
            extraction_text="must complete a financial assessment of the debtor's circumstances",
            attributes={
                "role_type": "Trustee",
                "obligation_type": "Duty",
                "description": "Must complete financial assessment of debtor and provide available options",
                "triggering_event": "Initial consultation with debtor",
                "to_whom_owed": "Debtor and creditors",
                "statutory_basis": "BIA"
            }
        )
    ]
)

# Example 3: Receiver - Take possession and sell assets
role_example_3 = lx.data.ExampleData(
    text="""
    1.5.4. Receiver:
    BIA s. 243-252
    must be a Licensed Insolvency Trustee;
    can be appointed privately by a secured creditor, pursuant to a security instrument, or
    can be court-appointed;
    will take possession and sell the assets pledged as security for the benefit of the secured
    creditor after the debtor has defaulted under the terms of the agreement;
    does not have the authority to continue to operate a debtor's business; and
    must comply with BIA sections 243-252.
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="role_obligation",
            extraction_text="will take possession and sell the assets pledged as security",
            attributes={
                "role_type": "Receiver",
                "obligation_type": "Duty",
                "description": "Take possession and sell assets pledged as security for benefit of secured creditor",
                "triggering_event": "Debtor default under security agreement",
                "to_whom_owed": "Secured creditor",
                "statutory_basis": "BIA s. 243-252"
            }
        )
    ]
)

# Example 4: Administrator - Monitor proposal payments
role_example_4 = lx.data.ExampleData(
    text="""
    1.5.2. Administrator of a Consumer Proposal:
    must be either a Licensed Insolvency Trustee or an individual appointed by the
    Superintendent of Bankruptcy to administer a consumer proposal;
    must assess the debtor's financial situation and assist in the preparation and filing of the
    proposal and other statutory documents as required under the BIA; and
    is responsible for monitoring the payments made under the proposal and ensuring that
    the dividends are issued to the creditors according to the provisions of the BIA.
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="role_obligation",
            extraction_text="is responsible for monitoring the payments made under the proposal",
            attributes={
                "role_type": "Administrator",
                "obligation_type": "Duty",
                "description": "Monitor payments under proposal and ensure dividends issued to creditors according to BIA",
                "to_whom_owed": "Creditors",
                "statutory_basis": "BIA"
            }
        )
    ]
)


# List of role obligation examples
role_obligations_examples = [
    role_example_1,
    role_example_2,
    role_example_3,
    role_example_4
]
