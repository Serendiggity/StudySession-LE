"""
Examples for remaining 7 categories.
Simplified examples (3 each) to complete Phase 3.

Categories:
- Document requirements
- Event triggers
- Communication requirements
- Relationships
- Cases
- Requirements
- Exceptions
"""

import langextract as lx


# ============================================================================
# DOCUMENT REQUIREMENTS (3 examples)
# ============================================================================

doc_req_1 = lx.data.ExampleData(
    text="""
    BIA Form 31
    The filing of a proof of claim entitles the creditor to ultimately participate in any distribution of
    dividends, if the claim is found to be valid.
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="document_requirement",
            extraction_text="Form 31",
            attributes={
                "document_name": "Proof of Claim",
                "form_number": "Form 31",
                "triggering_event": "Bankruptcy filed",
                "required_by": "Creditor",
                "recipients": ["Trustee"]
            }
        )
    ]
)

doc_req_2 = lx.data.ExampleData(
    text="""
    BIA Form 33
    The insolvent person would file the Notice of Intention with the Official Receiver in his locale.
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="document_requirement",
            extraction_text="Form 33",
            attributes={
                "document_name": "Notice of Intention",
                "form_number": "Form 33",
                "triggering_event": "Decision to file Division I proposal with stay required",
                "required_by": "Insolvent person",
                "recipients": ["Official Receiver"]
            }
        )
    ]
)

doc_req_3 = lx.data.ExampleData(
    text="""
    the Cash Flow Statement (containing a list of the significant assumptions on which it is
    premised), signed by the Trustee and the insolvent person;
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="document_requirement",
            extraction_text="Cash Flow Statement",
            attributes={
                "document_name": "Cash Flow Statement",
                "triggering_event": "Filing of Notice of Intention",
                "required_by": "Insolvent person and Trustee",
                "deadline": "Within 10 days of NOI filing",
                "recipients": ["Official Receiver"]
            }
        )
    ]
)


# ============================================================================
# EVENT TRIGGERS (3 examples)
# ============================================================================

event_1 = lx.data.ExampleData(
    text="""
    Upon filing an assignment in bankruptcy the bankrupt must prepare (and the Trustee is to
    review) the required financial information
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="event_trigger",
            extraction_text="Upon filing an assignment in bankruptcy",
            attributes={
                "event_type": "Bankruptcy",
                "event_description": "Filing of assignment in bankruptcy",
                "immediate_obligations": ["Prepare financial information", "Trustee reviews documents"]
            }
        )
    ]
)

event_2 = lx.data.ExampleData(
    text="""
    Within five days of filing the Notice of Intention, the Trustee sends a copy of the Notice of
    Intention to every known creditor.
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="event_trigger",
            extraction_text="filing the Notice of Intention",
            attributes={
                "event_type": "Filing",
                "event_description": "Filing of Notice of Intention with Official Receiver",
                "time_bound_obligations": ["Send notice to creditors within 5 days", "File cash flow within 10 days", "File proposal within 30 days"]
            }
        )
    ]
)

event_3 = lx.data.ExampleData(
    text="""
    once appointed, must carry out his duties in an honest and competent manner
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="event_trigger",
            extraction_text="once appointed",
            attributes={
                "event_type": "Appointment",
                "event_description": "Trustee appointment",
                "immediate_obligations": ["Carry out duties in honest and competent manner"]
            }
        )
    ]
)


# ============================================================================
# COMMUNICATION REQUIREMENTS (3 examples)
# ============================================================================

comm_1 = lx.data.ExampleData(
    text="""
    Within five days of filing the Notice of Intention, the Trustee sends a copy of the Notice of
    Intention to every known creditor.
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="communication_requirement",
            extraction_text="Trustee sends a copy of the Notice of Intention to every known creditor",
            attributes={
                "communication_type": "Notice",
                "from_party": "Trustee",
                "to_parties": ["All known creditors"],
                "timing": "Within 5 days of NOI filing"
            }
        )
    ]
)

comm_2 = lx.data.ExampleData(
    text="""
    Summary bankruptcy – advise creditors and OSB of pending Trustee discharge
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="communication_requirement",
            extraction_text="advise creditors and OSB of pending Trustee discharge",
            attributes={
                "communication_type": "Notice",
                "from_party": "Trustee",
                "to_parties": ["Creditors", "OSB"],
                "timing": "Before Trustee discharge"
            }
        )
    ]
)

comm_3 = lx.data.ExampleData(
    text="""
    Book court date,
    notify creditors
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="communication_requirement",
            extraction_text="notify creditors",
            attributes={
                "communication_type": "Notice",
                "from_party": "Trustee",
                "to_parties": ["Creditors"],
                "timing": "After booking court date for discharge hearing"
            }
        )
    ]
)


# ============================================================================
# RELATIONSHIPS (3 examples)
# ============================================================================

rel_1 = lx.data.ExampleData(
    text="""
    Within ten days of filing the Notice of Intention the insolvent person must file the following
    with the Official Receiver:
    the Cash Flow Statement
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="relationship",
            extraction_text="Within ten days of filing the Notice of Intention",
            attributes={
                "relationship_type": "triggers",
                "element_a": "Notice of Intention filing",
                "element_b": "Cash Flow Statement filing deadline",
                "relationship_description": "NOI filing triggers 10-day deadline to file cash flow"
            }
        )
    ]
)

rel_2 = lx.data.ExampleData(
    text="""
    For a debtor to file a proposal, the proposal must be more beneficial than bankruptcy.
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="relationship",
            extraction_text="proposal must be more beneficial than bankruptcy",
            attributes={
                "relationship_type": "prerequisite",
                "element_a": "Proposal being more beneficial than bankruptcy",
                "element_b": "Filing a proposal",
                "relationship_description": "Proposal must be more beneficial than bankruptcy to be filed"
            }
        )
    ]
)

rel_3 = lx.data.ExampleData(
    text="""
    A Trustee can delegate certain duties, but is ultimately responsible for all actions taken by
    individuals under his supervision.
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="relationship",
            extraction_text="delegate certain duties, but is ultimately responsible",
            attributes={
                "relationship_type": "responsibility_chain",
                "element_a": "Trustee delegation of duties",
                "element_b": "Trustee responsibility for delegated actions",
                "relationship_description": "Trustee can delegate but remains ultimately responsible for all actions"
            }
        )
    ]
)


# ============================================================================
# CASES / REQUIREMENTS / EXCEPTIONS (Simplified - 3 each)
# ============================================================================

# Cases - Will extract from actual case law sections later
case_1 = lx.data.ExampleData(
    text="Example case placeholder - will be populated from actual content",
    extractions=[
        lx.data.Extraction(
            extraction_class="case",
            extraction_text="placeholder",
            attributes={"case_name": "Placeholder"}
        )
    ]
)

# Requirements
req_1 = lx.data.ExampleData(
    text="""
    must be a Licensed Insolvency Trustee;
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="requirement",
            extraction_text="must be a Licensed Insolvency Trustee",
            attributes={
                "requirement_type": "Qualification",
                "description": "Must hold license as Licensed Insolvency Trustee",
                "who_must_satisfy": "Trustee, Receiver, Administrator"
            }
        )
    ]
)

req_2 = lx.data.ExampleData(
    text="""
    For a debtor to file a proposal, the proposal must be more beneficial than bankruptcy.
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="requirement",
            extraction_text="proposal must be more beneficial than bankruptcy",
            attributes={
                "requirement_type": "Condition",
                "description": "Proposal must be more beneficial than bankruptcy option",
                "when_applicable": "Before filing proposal"
            }
        )
    ]
)

req_3 = lx.data.ExampleData(
    text="""
    debts of more than $5,000,000
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="requirement",
            extraction_text="debts of more than $5,000,000",
            attributes={
                "requirement_type": "Threshold",
                "description": "Debts must exceed $5,000,000",
                "when_applicable": "CCAA filing eligibility"
            }
        )
    ]
)

# Exceptions
except_1 = lx.data.ExampleData(
    text="""
    does not have the authority to continue to operate a debtor's business
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="exception",
            extraction_text="does not have the authority to continue to operate",
            attributes={
                "exception_to": "General receiver powers",
                "exception_description": "Receiver does NOT have authority to continue business operations (unlike Receiver Manager)"
            }
        )
    ]
)

except_2 = lx.data.ExampleData(
    text="""
    Corporations cannot file a consumer proposal.
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="exception",
            extraction_text="Corporations cannot file a consumer proposal",
            attributes={
                "exception_to": "Consumer proposal eligibility",
                "exception_description": "Corporations are excluded from filing consumer proposals - only individuals"
            }
        )
    ]
)

except_3 = lx.data.ExampleData(
    text="""
    These companies are excluded from utilizing the provisions of the BIA.
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="exception",
            extraction_text="excluded from utilizing the provisions of the BIA",
            attributes={
                "exception_to": "BIA application",
                "exception_description": "Banks, insurance companies, and trust companies excluded from BIA (use WURA instead)"
            }
        )
    ]
)


# Export all remaining category examples
document_requirements_examples = [doc_req_1, doc_req_2, doc_req_3]
event_triggers_examples = [event_1, event_2, event_3]
communication_requirements_examples = [comm_1, comm_2, comm_3]
relationships_examples = [rel_1, rel_2, rel_3]
cases_examples = [case_1, case_1, case_1]  # Placeholder - will refine later if needed
requirements_examples = [req_1, req_2, req_3]
exceptions_examples = [except_1, except_2, except_3]
