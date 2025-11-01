"""
Concept examples for Lang Extract training.
Based on actual content from Insolvency Administration study guide.

Following Lang Extract best practices:
- Use EXACT text from source (no paraphrasing!)
- No overlapping text spans
- Extract in order of appearance
- 3-5 high-quality examples per category
"""

import langextract as lx


# Example 1: Insolvency definition
concept_example_1 = lx.data.ExampleData(
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
                "definition": "The financial situation a person finds himself in when he is unable to pay his debts when they are due, or has ceased making payments, or his liabilities exceed the value of his assets",
                "context": "Financial condition triggering bankruptcy/proposal options",
                "importance_level": "high"
            }
        )
    ]
)

# Example 2: Trustee definition
concept_example_2 = lx.data.ExampleData(
    text="""
    A Trustee is an officer of the court who owes a duty of care to all stakeholders.
    A Trustee operates in a position of trust and must maintain a high standard of ethics in the
    administration of his duties.
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="concept",
            extraction_text="Trustee",
            attributes={
                "term": "Trustee",
                "definition": "An officer of the court who owes a duty of care to all stakeholders and operates in a position of trust maintaining high ethical standards",
                "context": "Licensed insolvency practitioner administering bankruptcy/proposal estates",
                "importance_level": "high",
                "related_terms": ["Licensed Insolvency Trustee", "LIT", "Officer of the court"]
            }
        )
    ]
)

# Example 3: Bankrupt person definition
concept_example_3 = lx.data.ExampleData(
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
                "definition": "A person who has either filed an assignment in bankruptcy or has been petitioned into bankruptcy by a creditor and is now subject to the provisions of the BIA",
                "source_act": "Bankruptcy and Insolvency Act",
                "context": "Legal status after bankruptcy proceeding initiated",
                "importance_level": "high",
                "related_terms": ["Assignment in bankruptcy", "Petition", "Debtor"]
            }
        )
    ]
)

# Example 4: CCAA definition
concept_example_4 = lx.data.ExampleData(
    text="""
    Companies' Creditors Arrangement Act (CCAA)
    Enacted in 1933.
    Provides for the financial restructuring of a company or related group of companies
    with debts of more than $5,000,000 under court supervision.
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="concept",
            extraction_text="Companies' Creditors Arrangement Act",
            attributes={
                "term": "Companies' Creditors Arrangement Act",
                "definition": "Provides for the financial restructuring of a company or related group of companies with debts of more than $5,000,000 under court supervision",
                "source_act": "Companies' Creditors Arrangement Act",
                "context": "Large corporate restructuring (>$5M debt)",
                "importance_level": "high",
                "related_terms": ["CCAA", "restructuring", "court supervision"]
            }
        )
    ]
)

# Example 5: BIA rehabilitative purpose
concept_example_5 = lx.data.ExampleData(
    text="""
    The BIA is a rehabilitative act that offers an insolvent person an opportunity to be released
    from his debts. It also offers creditors an orderly wind-up and distribution of a bankrupt's
    realizable assets.
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="concept",
            extraction_text="BIA",
            attributes={
                "term": "Bankruptcy and Insolvency Act (BIA)",
                "definition": "A rehabilitative act that offers an insolvent person an opportunity to be released from debts and offers creditors an orderly wind-up and distribution of a bankrupt's realizable assets",
                "source_act": "Bankruptcy and Insolvency Act",
                "context": "Primary federal legislation governing insolvency in Canada",
                "importance_level": "high",
                "related_terms": ["Bankruptcy", "Insolvency", "Federal legislation"]
            }
        )
    ]
)


# List of all concept examples
concept_examples = [
    concept_example_1,
    concept_example_2,
    concept_example_3,
    concept_example_4,
    concept_example_5
]
