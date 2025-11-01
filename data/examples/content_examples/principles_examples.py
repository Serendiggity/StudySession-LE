"""
Principles examples for Lang Extract training.
Legal principles, rules, and standards governing insolvency practice.
"""

import langextract as lx


# Example 1: Financial rehabilitation principle
principles_example_1 = lx.data.ExampleData(
    text="""
    1.1.1. Philosophy
    Bankruptcy and insolvency legislation has the following primary goals:
    Financial rehabilitation: to allow an honest but unfortunate debtor the ability to obtain a
    fresh start unfettered by an insurmountable debt load; to obtain a discharge from his
    debts on reasonable conditions;
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="principle",
            extraction_text="Financial rehabilitation",
            attributes={
                "principle_name": "Financial Rehabilitation",
                "description": "Allow honest but unfortunate debtor to obtain fresh start unfettered by insurmountable debt load and discharge from debts on reasonable conditions",
                "statutory_basis": "Bankruptcy and Insolvency Act",
                "application_context": "Primary goal of bankruptcy legislation",
                "priority_level": "critical"
            }
        )
    ]
)

# Example 2: Collective process principle
principles_example_2 = lx.data.ExampleData(
    text="""
    Collective process: to provide for an orderly and fair distribution of available proceeds to
    the creditors in an equitable manner;
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="principle",
            extraction_text="Collective process",
            attributes={
                "principle_name": "Collective Process",
                "description": "Provide for orderly and fair distribution of available proceeds to creditors in equitable manner",
                "statutory_basis": "Bankruptcy and Insolvency Act",
                "application_context": "Distribution of bankruptcy estate proceeds",
                "priority_level": "critical"
            }
        )
    ]
)

# Example 3: Impartiality principle
principles_example_3 = lx.data.ExampleData(
    text="""
    has a duty of care to both the debtor and the creditors and must remain impartial while
    completing the administration of the estate;
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="principle",
            extraction_text="must remain impartial",
            attributes={
                "principle_name": "Trustee Impartiality",
                "description": "Trustee must remain impartial while completing estate administration despite duty of care to both debtor and creditors",
                "requirements": "Trustee must have duty of care to both parties and must maintain impartiality",
                "application_context": "Trustee administration of estates",
                "priority_level": "critical"
            }
        )
    ]
)

# Example 4: Transparency principle
principles_example_4 = lx.data.ExampleData(
    text="""
    There is an inherent conflict of interest in the role of the Trustee as the Trustee has
    obligations to both the creditors and the debtor. Both the Office of the Superintendent of
    Bankruptcy and CAIRP have established codes of conduct to address these conflicts and
    ensure that the insolvency process remains transparent.
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="principle",
            extraction_text="ensure that the insolvency process remains transparent",
            attributes={
                "principle_name": "Process Transparency",
                "description": "Codes of conduct established to address conflicts of interest and ensure insolvency process remains transparent",
                "requirements": "Must follow OSB codes of conduct and CAIRP professional standards",
                "exceptions": "Confidentiality requirements may limit some disclosures",
                "statutory_basis": "BIA Rules 34-53, CAIRP Rules of Professional Conduct",
                "application_context": "Addressing inherent conflicts of interest in Trustee role",
                "priority_level": "important"
            }
        )
    ]
)


# List of principles examples
principles_examples = [
    principles_example_1,
    principles_example_2,
    principles_example_3,
    principles_example_4
]
