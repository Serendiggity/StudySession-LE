"""
Concept examples for Lang Extract training - V2 (Optimized for JSON parsing).

Key changes from V1:
- Shorter definitions (<100 chars)
- Fewer attributes (3-4 max)
- No embedded quotes that could break JSON
- Simpler language
"""

import langextract as lx


# Example 1: Insolvency
concept_v2_1 = lx.data.ExampleData(
    text="""
    Insolvency is the financial situation a person finds himself in when he is unable to pay his
    debts when they are due, or has ceased making payments, or his liabilities exceed the value
    of his assets.
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="concept",
            extraction_text="Insolvency",
            attributes={
                "term": "Insolvency",
                "definition": "Unable to pay debts when due or liabilities exceed assets",
                "importance": "high"
            }
        )
    ]
)

# Example 2: Trustee
concept_v2_2 = lx.data.ExampleData(
    text="""
    A Trustee is an officer of the court who owes a duty of care to all stakeholders.
    A Trustee operates in a position of trust and must maintain a high standard of ethics.
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="concept",
            extraction_text="Trustee",
            attributes={
                "term": "Trustee",
                "definition": "Officer of court administering bankruptcy estates with duty of care to all stakeholders",
                "importance": "high"
            }
        )
    ]
)

# Example 3: Bankrupt Person
concept_v2_3 = lx.data.ExampleData(
    text="""
    A bankrupt person has either filed an assignment in bankruptcy or has been petitioned into
    bankruptcy by a creditor and is now subject to the provisions of the BIA.
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="concept",
            extraction_text="bankrupt person",
            attributes={
                "term": "Bankrupt Person",
                "definition": "Person who filed assignment or was petitioned into bankruptcy",
                "source_act": "BIA",
                "importance": "high"
            }
        )
    ]
)

# Example 4: CCAA
concept_v2_4 = lx.data.ExampleData(
    text="""
    Companies' Creditors Arrangement Act (CCAA)
    Provides for the financial restructuring of a company or related group of companies
    with debts of more than $5,000,000 under court supervision.
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="concept",
            extraction_text="Companies' Creditors Arrangement Act",
            attributes={
                "term": "CCAA",
                "definition": "Restructuring for companies with debts over 5M under court supervision",
                "source_act": "CCAA",
                "importance": "high"
            }
        )
    ]
)

# Example 5: BIA
concept_v2_5 = lx.data.ExampleData(
    text="""
    The BIA is a rehabilitative act that offers an insolvent person an opportunity to be released
    from his debts. It also offers creditors an orderly wind-up and distribution of assets.
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="concept",
            extraction_text="BIA",
            attributes={
                "term": "BIA",
                "definition": "Federal act offering debt relief to insolvents and orderly distribution to creditors",
                "importance": "high"
            }
        )
    ]
)


# Export
concept_examples = [
    concept_v2_1,
    concept_v2_2,
    concept_v2_3,
    concept_v2_4,
    concept_v2_5
]
