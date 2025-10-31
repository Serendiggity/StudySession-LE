# Schema Specification Document
## Extraction Categories for Insolvency Study Assistant

**Version:** 1.0
**Date:** 2025-10-28
**Status:** Approved

---

## Table of Contents

1. [Overview](#overview)
2. [Schema Definitions](#schema-definitions)
   - [1. Concepts](#1-concepts)
   - [2. Principles](#2-principles)
   - [3. Statutory References](#3-statutory-references)
   - [4. Role Obligations](#4-role-obligations)
   - [5. Deadlines](#5-deadlines)
   - [6. Procedures](#6-procedures)
   - [7. Document Requirements](#7-document-requirements)
   - [8. Event Triggers](#8-event-triggers)
   - [9. Communication Requirements](#9-communication-requirements)
   - [10. Relationships](#10-relationships)
   - [11. Cases](#11-cases)
   - [12. Requirements](#12-requirements)
   - [13. Exceptions](#13-exceptions)
   - [14. Pitfalls](#14-pitfalls)
3. [Validation Rules](#validation-rules)
4. [Quality Criteria](#quality-criteria)

---

## Overview

This document defines the 13 extraction categories used to structure knowledge from insolvency study materials. Each category has:
- **Name:** Category identifier
- **Description:** What this category captures
- **Attributes:** Data fields to extract
- **Data Types:** Expected format for each attribute
- **Extraction Guidance:** What to look for and how to extract it
- **Example Snippet:** Sample extraction from source material
- **Common Pitfalls:** What to avoid

**Priority for exam preparation:**
1. **Critical (extract first):** Concepts, Statutory References, Deadlines, Role Obligations
2. **Important (extract second):** Principles, Procedures, Document Requirements
3. **Supporting (extract third):** Event Triggers, Communication Requirements, Relationships
4. **Contextual (extract last):** Cases, Requirements, Exceptions, Pitfalls

---

## Schema Definitions

### 1. Concepts

**Description:** Key terms and their definitions that form the foundation of insolvency law.

**Priority:** 🔴 Critical

**Attributes:**

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `term` | string | ✅ | The concept or term being defined |
| `definition` | string | ✅ | Clear, concise definition |
| `source_act` | string | Optional | Which Act defines this (BIA, CCAA, etc.) |
| `section_reference` | string | Optional | Specific section where defined (e.g., "s. 2(1)") |
| `context` | string | Optional | When/where this concept applies |
| `importance_level` | enum | Optional | "high", "medium", "low" |
| `related_terms` | list[string] | Optional | Other concepts that relate to this |

**What to Extract:**
- Explicit definitions (e.g., "X is defined as...")
- Key terminology with explanations
- Concepts central to exam topics
- Technical terms specific to insolvency

**What NOT to Extract:**
- Common words with dictionary definitions
- Passing mentions without explanation
- Overly vague or general statements

**Extraction Guidance:**
```
Look for patterns:
- "X is...", "X means...", "X refers to..."
- Bold or italicized terms followed by explanation
- Numbered definitions in statute sections
- Terms in glossaries or definition sections
```

**Example Extraction:**
```json
{
  "term": "Administration",
  "definition": "A procedure under the Insolvency Act 1986 whereby a licensed insolvency practitioner (administrator) is appointed to manage the affairs, business, and property of a company",
  "source_act": "Insolvency Act 1986",
  "section_reference": "Schedule B1",
  "context": "Corporate insolvency rescue procedure",
  "importance_level": "high",
  "related_terms": ["Administrator", "Moratorium", "Rescue"]
}
```

**Validation Rules:**
- `term` must be non-empty
- `definition` must be at least 10 characters
- `importance_level` if present must be one of: "high", "medium", "low"
- `section_reference` should match pattern: "s. X" or "section X"

**Example Count:** 3-5 examples (per Lang Extract best practices)
**Target Extraction Count:** 150-250 concepts from 291-page PDF

---

### 2. Principles

**Description:** Legal principles, rules, and standards that govern insolvency practice.

**Priority:** 🟡 Important

**Attributes:**

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `principle_name` | string | ✅ | Name of the principle or rule |
| `description` | string | ✅ | What the principle states |
| `statutory_basis` | string | Optional | Which Act(s) establish this |
| `section_references` | list[string] | Optional | Relevant sections |
| `application_context` | string | Optional | When this principle applies |
| `exceptions` | string | Optional | When principle doesn't apply |
| `case_law_support` | list[string] | Optional | Key cases establishing principle |
| `priority_level` | enum | Optional | "critical", "important", "helpful" |

**What to Extract:**
- Fiduciary duties
- Priority rules (secured vs. unsecured creditors)
- Principles of fairness and equity
- Professional standards for IPs
- Statutory interpretation principles

**What NOT to Extract:**
- Vague general statements
- Personal opinions or recommendations
- Historical background without current application

**Example Extraction:**
```json
{
  "principle_name": "Duty to act in creditors' interests",
  "description": "The administrator must perform their functions with the objective of achieving the best result for creditors as a whole",
  "statutory_basis": "Insolvency Act 1986",
  "section_references": ["Schedule B1, para 3(1)(a)"],
  "application_context": "Throughout the administration period",
  "exceptions": "Subject to duty to company and shareholders in certain circumstances",
  "priority_level": "critical"
}
```

**Target Count:** 80-120 principles

---

### 3. Statutory References

**Description:** Specific citations to legislation (BIA, CCAA, Farm Debt Act, etc.) with their practical effect.

**Priority:** 🔴 Critical

**Attributes:**

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `act_name` | string | ✅ | Name of the Act (BIA, CCAA, etc.) |
| `section_number` | string | ✅ | Section number (e.g., "43", "65.13") |
| `subsection` | string | Optional | Subsection if applicable |
| `provision_text` | string | Optional | Actual text of provision (if brief) |
| `practical_effect` | string | ✅ | What this section means in practice |
| `related_sections` | list[string] | Optional | Cross-referenced sections |
| `amendments` | string | Optional | Recent changes |
| `frequency_of_reference` | enum | Optional | "very_common", "common", "occasional", "rare" |

**What to Extract:**
- Every BIA section mentioned (priority!)
- CCAA sections
- Farm Debt Act sections
- Other relevant legislation
- Both the citation and practical explanation

**Example Extraction:**
```json
{
  "act_name": "Bankruptcy and Insolvency Act",
  "section_number": "43",
  "subsection": "(1)",
  "provision_text": "The property of a bankrupt divisible among their creditors shall not comprise...",
  "practical_effect": "Defines exempt property that cannot be seized by the trustee, including necessary household items, tools of trade up to prescribed value, and certain pension rights",
  "related_sections": ["s. 67", "s. 68"],
  "frequency_of_reference": "very_common"
}
```

**Validation Rules:**
- `act_name` must be valid Act name
- `section_number` must be numeric or contain decimal (e.g., "65.13")
- `practical_effect` must be non-empty

**Target Count:** 200-300 statutory references (BIA is heavily cited)

---

### 4. Role Obligations

**Description:** Duties, powers, and prohibitions specific to each role in insolvency proceedings.

**Priority:** 🔴 Critical

**Attributes:**

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `role_type` | enum | ✅ | "Trustee", "Receiver", "Administrator", "Proposal Trustee", "Monitor", "Debtor", etc. |
| `obligation_type` | enum | ✅ | "Duty", "Power", "Prohibition", "Discretion" |
| `description` | string | ✅ | What the obligation entails |
| `triggering_event` | string | Optional | What activates this obligation |
| `timing_requirement` | string | Optional | When must it be done |
| `statutory_basis` | string | Optional | Which section creates obligation |
| `consequences_if_failed` | string | Optional | Penalties, liability |
| `to_whom_owed` | string | Optional | Creditors, Court, OSB, etc. |
| `exceptions` | string | Optional | When obligation doesn't apply |

**What to Extract:**
- Trustee duties (most important!)
- Receiver duties and powers
- Administrator roles (if UK content)
- Proposal Trustee obligations
- Monitor duties (CCAA)
- Debtor obligations

**Example Extraction:**
```json
{
  "role_type": "Trustee",
  "obligation_type": "Duty",
  "description": "Notify the Office of the Superintendent of Bankruptcy immediately upon appointment",
  "triggering_event": "Appointment as trustee in bankruptcy",
  "timing_requirement": "Immediately (same day)",
  "statutory_basis": "BIA s. 13",
  "consequences_if_failed": "Administrative penalty; potential removal as trustee",
  "to_whom_owed": "Office of the Superintendent of Bankruptcy",
  "exceptions": "None"
}
```

**Target Count:** 100-150 role obligations

---

### 5. Deadlines

**Description:** Time-sensitive requirements with calculation methods - ONE OF THE MOST IMPORTANT CATEGORIES!

**Priority:** 🔴 Critical

**Attributes:**

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `deadline_type` | enum | ✅ | "Filing", "Notice", "Meeting", "Payment", "Report" |
| `timeframe` | string | ✅ | "10 days", "30 days", "immediately", etc. |
| `calculation_method` | enum | ✅ | "business_days", "calendar_days", "clear_days" |
| `day_type_specified` | string | Optional | What statute actually says |
| `exclude_holidays` | boolean | Optional | Are holidays excluded? |
| `exclude_weekends` | boolean | Optional | Are weekends excluded? |
| `same_day_counts` | boolean | Optional | Does triggering day count as Day 0 or 1? |
| `end_of_day_rule` | string | Optional | 5pm? Midnight? End of business? |
| `triggering_event` | string | ✅ | What starts the clock |
| `required_action` | string | ✅ | What must be done |
| `responsible_party` | string | ✅ | Who must act |
| `recipient` | string | Optional | Who receives/benefits |
| `statutory_reference` | string | ✅ | BIA s. X |
| `consequences_if_missed` | string | Optional | Penalties, invalidity |
| `extension_available` | string | Optional | Can it be extended? How? |
| `common_pitfalls` | string | Optional | Common mistakes |
| `calculation_examples` | string | Optional | Worked example |

**What to Extract:**
- EVERY deadline mentioned!
- Pay special attention to calculation method
- Note whether business days or calendar days
- Capture triggering events precisely
- Document what happens if missed

**Example Extraction:**
```json
{
  "deadline_type": "Notice",
  "timeframe": "10 days",
  "calculation_method": "clear_days",
  "day_type_specified": "Statute says 'at least 10 days' - Interpretation Act applies",
  "exclude_holidays": true,
  "exclude_weekends": false,
  "same_day_counts": false,
  "end_of_day_rule": "Must be mailed by end of business day",
  "triggering_event": "Date of intended first meeting of creditors",
  "required_action": "Send notice to all known creditors",
  "responsible_party": "Trustee",
  "recipient": "All known creditors",
  "statutory_reference": "BIA s. 102(1)",
  "consequences_if_missed": "Meeting may be invalid; must be rescheduled",
  "extension_available": "Can reschedule meeting if insufficient notice",
  "common_pitfalls": "Counting calendar days instead of clear days; not accounting for weekends",
  "calculation_examples": "Meeting on Friday Aug 15 → Notice by Monday Aug 4 (excludes Aug 4 and Aug 15, counts 10 clear days)"
}
```

**Validation Rules:**
- `timeframe` must contain a number
- `calculation_method` must be one of the enum values
- `statutory_reference` must be present
- If `calculation_method` is "business_days", `exclude_weekends` should be true

**Target Count:** 60-100 deadlines (critical for exam!)

---

### 6. Procedures

**Description:** Step-by-step processes for various insolvency actions.

**Priority:** 🟡 Important

**Attributes:**

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `procedure_name` | string | ✅ | Name of the procedure |
| `purpose` | string | ✅ | What this procedure accomplishes |
| `initiating_event` | string | Optional | What triggers this procedure |
| `steps` | list[object] | ✅ | Ordered list of steps |
| `steps[].step_number` | int | ✅ | Order (1, 2, 3...) |
| `steps[].description` | string | ✅ | What to do |
| `steps[].responsible_party` | string | Optional | Who does this step |
| `steps[].deadline` | string | Optional | Time requirement |
| `required_documents` | list[string] | Optional | What docs are needed |
| `statutory_basis` | string | Optional | BIA section |
| `prerequisites` | list[string] | Optional | Must be done first |
| `outcomes` | list[string] | Optional | Possible results |
| `decision_points` | list[string] | Optional | Where choices are made |
| `common_errors` | list[string] | Optional | Mistakes to avoid |

**What to Extract:**
- Filing for bankruptcy procedure
- Proposal filing procedure
- Receivership appointment process
- Administration procedures
- Creditor meeting procedures

**Example Extraction:**
```json
{
  "procedure_name": "Filing for Personal Bankruptcy",
  "purpose": "Initiate bankruptcy proceedings for an individual debtor",
  "initiating_event": "Debtor decides to file or creditor petitions",
  "steps": [
    {
      "step_number": 1,
      "description": "Debtor meets with licensed insolvency trustee for initial consultation",
      "responsible_party": "Debtor and Trustee"
    },
    {
      "step_number": 2,
      "description": "Complete and sign bankruptcy forms (including Statement of Affairs)",
      "responsible_party": "Debtor with Trustee assistance",
      "required_documents": ["Statement of Affairs", "Assignment in Bankruptcy"]
    },
    {
      "step_number": 3,
      "description": "Trustee files assignment with Office of Superintendent of Bankruptcy",
      "responsible_party": "Trustee",
      "deadline": "Immediately after signing"
    }
  ],
  "statutory_basis": "BIA Part III",
  "outcomes": ["Bankruptcy order made", "Stay of proceedings takes effect", "Trustee assumes control of assets"]
}
```

**Target Count:** 40-60 procedures

---

### 7. Document Requirements

**Description:** Required documents and forms for various insolvency events.

**Priority:** 🟡 Important

**Attributes:**

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `document_name` | string | ✅ | Official name of document |
| `form_number` | string | Optional | Form number if applicable (e.g., "Form 79") |
| `triggering_event` | string | ✅ | What makes it required |
| `required_by` | string | ✅ | Who must produce it |
| `deadline` | string | Optional | When due |
| `recipients` | list[string] | ✅ | Who receives it |
| `content_requirements` | list[string] | Optional | What must be included |
| `format_requirements` | string | Optional | Sworn affidavit? Prescribed form? |
| `statutory_basis` | string | Optional | BIA section |
| `consequences_if_missing` | string | Optional | Penalties |
| `dependencies` | string | Optional | "Requires X document first" |

**What to Extract:**
- Statement of Affairs
- Assignment in Bankruptcy
- Notice to Creditors
- Proof of Claim
- Trustee reports
- Court filings

**Example Extraction:**
```json
{
  "document_name": "Statement of Affairs",
  "form_number": "Form 79",
  "triggering_event": "Bankruptcy or proposal filing",
  "required_by": "Debtor (with Trustee assistance)",
  "deadline": "At time of filing bankruptcy; within 30 days for proposal",
  "recipients": ["Trustee", "Office of Superintendent of Bankruptcy", "Creditors (on request)"],
  "content_requirements": [
    "List of all assets with values",
    "List of all liabilities with amounts",
    "Income and expense statement",
    "List of creditors with addresses"
  ],
  "format_requirements": "Prescribed Form 79; must be sworn before authorized person",
  "statutory_basis": "BIA s. 158",
  "consequences_if_missing": "Bankruptcy proceedings may be suspended",
  "dependencies": "Required before first meeting of creditors can be held"
}
```

**Target Count:** 30-50 document requirements

---

### 8. Event Triggers

**Description:** Events that trigger obligations, deadlines, or procedures.

**Priority:** 🟢 Supporting

**Attributes:**

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `event_type` | enum | ✅ | "Bankruptcy", "Proposal", "Receivership", "Meeting", "Filing", etc. |
| `event_description` | string | ✅ | What happened |
| `immediate_obligations` | list[string] | Optional | Must do right away |
| `time_bound_obligations` | list[object] | Optional | Must do within X days |
| `responsible_parties` | list[string] | Optional | Who must act |
| `notification_requirements` | list[string] | Optional | Who must be notified |
| `required_documents` | list[string] | Optional | What docs must be filed |
| `statutory_basis` | string | Optional | BIA section |
| `sequence` | int | Optional | Order of operations |
| `dependencies` | list[string] | Optional | "Can't do Y until X is done" |

**Example Extraction:**
```json
{
  "event_type": "Bankruptcy",
  "event_description": "Individual files assignment in bankruptcy",
  "immediate_obligations": [
    "Trustee must notify OSB",
    "Stay of proceedings takes effect",
    "Debtor must surrender assets"
  ],
  "time_bound_obligations": [
    {"action": "Send notice to creditors", "deadline": "5 days", "reference": "BIA s. 102"},
    {"action": "File Statement of Affairs", "deadline": "30 days", "reference": "BIA s. 158"},
    {"action": "Hold first meeting of creditors", "deadline": "Within 45 days", "reference": "BIA s. 102"}
  ],
  "responsible_parties": ["Trustee", "Debtor"],
  "notification_requirements": ["All known creditors", "OSB", "Secured creditors"],
  "statutory_basis": "BIA Part III",
  "sequence": 0,
  "dependencies": ["First meeting cannot be held until Statement of Affairs filed"]
}
```

**Target Count:** 25-40 event triggers

---

### 9. Communication Requirements

**Description:** Required notices and communications in insolvency proceedings.

**Priority:** 🟢 Supporting

**Attributes:**

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `communication_type` | enum | ✅ | "Notice", "Report", "Meeting Notice", "Disclosure" |
| `from_party` | string | ✅ | Who sends |
| `to_parties` | list[string] | ✅ | Who receives |
| `timing` | string | ✅ | When/how soon |
| `method` | list[string] | Optional | Mail, email, publication, personal service |
| `content_requirements` | list[string] | Optional | What must be included |
| `proof_required` | string | Optional | Affidavit of service? |
| `statutory_basis` | string | Optional | BIA section |
| `consequences_if_improper` | string | Optional | What happens if done wrong |

**Example Extraction:**
```json
{
  "communication_type": "Notice",
  "from_party": "Trustee",
  "to_parties": ["All known creditors", "Bankrupt"],
  "timing": "At least 10 clear days before meeting",
  "method": ["Ordinary mail to last known address", "Publication in newspaper (if required)"],
  "content_requirements": [
    "Date, time, place of meeting",
    "Purpose of meeting",
    "Copy of Statement of Affairs",
    "Proof of claim form"
  ],
  "proof_required": "Affidavit of service may be required",
  "statutory_basis": "BIA s. 102",
  "consequences_if_improper": "Meeting may be adjourned or declared invalid"
}
```

**Target Count:** 20-35 communication requirements

---

### 10. Relationships

**Description:** How concepts, deadlines, procedures, and other elements relate to and depend on each other.

**Priority:** 🟢 Supporting

**Attributes:**

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `relationship_type` | enum | ✅ | "prerequisite", "triggers", "prohibits", "modifies", "cross_reference" |
| `element_a` | string | ✅ | First element (concept, procedure, document) |
| `element_b` | string | ✅ | Second element |
| `relationship_description` | string | ✅ | How they relate |
| `conditional_factors` | string | Optional | "Only if X condition" |
| `timing_implications` | string | Optional | Sequential? Parallel? |
| `practical_example` | string | Optional | Real-world illustration |

**Example Extraction:**
```json
{
  "relationship_type": "prerequisite",
  "element_a": "Statement of Affairs (Form 79)",
  "element_b": "First meeting of creditors",
  "relationship_description": "Statement of Affairs must be filed before first meeting of creditors can be held",
  "conditional_factors": "None - absolute requirement",
  "timing_implications": "Sequential - meeting cannot proceed without Statement",
  "practical_example": "If Statement is not ready by day 10, trustee must delay sending 10-day notice until Statement is available"
}
```

**Target Count:** 40-60 relationships

---

### 11. Cases

**Description:** Case law and judicial decisions that interpret insolvency law.

**Priority:** 🟢 Supporting

**Attributes:**

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `case_name` | string | ✅ | Full case name |
| `citation` | string | Optional | Legal citation |
| `court_level` | string | Optional | Supreme Court, Court of Appeal, etc. |
| `year` | int | Optional | Year decided |
| `key_facts` | string | Optional | Relevant facts |
| `legal_issue` | string | ✅ | What question was decided |
| `holding` | string | ✅ | Court's decision |
| `principle_established` | string | ✅ | What principle this case stands for |
| `relevance_to_practice` | string | Optional | Practical application |
| `related_sections` | list[string] | Optional | BIA sections involved |
| `related_concepts` | list[string] | Optional | Key concepts |

**Example Extraction:**
```json
{
  "case_name": "Hypothetical Case v. Another Party",
  "citation": "[2020] SCC 42",
  "court_level": "Supreme Court of Canada",
  "year": 2020,
  "legal_issue": "Whether administrator's duty to creditors overrides duty to company shareholders",
  "holding": "Administrator's primary duty is to creditors as a whole; shareholder interests are secondary",
  "principle_established": "Creditor primacy in insolvency proceedings",
  "relevance_to_practice": "Administrators must prioritize creditor interests when making decisions about company's future",
  "related_sections": ["BIA s. 13.4", "Schedule B1"],
  "related_concepts": ["Fiduciary duty", "Creditor interests", "Administrator duties"]
}
```

**Target Count:** 20-40 cases

---

### 12. Requirements

**Description:** Prerequisites and conditions that must be met for various actions.

**Priority:** 🟢 Supporting

**Attributes:**

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `requirement_type` | enum | ✅ | "Qualification", "Condition", "Threshold", "Authorization" |
| `description` | string | ✅ | What the requirement is |
| `when_applicable` | string | ✅ | When this requirement applies |
| `who_must_satisfy` | string | ✅ | Who must meet requirement |
| `verification_method` | string | Optional | How to prove compliance |
| `statutory_basis` | string | Optional | BIA section |
| `exceptions` | string | Optional | When not required |
| `consequences_if_not_met` | string | Optional | What happens if failed |

**Example Extraction:**
```json
{
  "requirement_type": "Qualification",
  "description": "Must be licensed as an insolvency practitioner by a recognized professional body",
  "when_applicable": "Before acting as trustee in bankruptcy",
  "who_must_satisfy": "Trustee in bankruptcy",
  "verification_method": "License issued by regulatory body; registration with OSB",
  "statutory_basis": "BIA s. 13.3",
  "exceptions": "None",
  "consequences_if_not_met": "Acts as trustee are invalid; professional sanctions; potential criminal liability"
}
```

**Target Count:** 20-35 requirements

---

### 13. Exceptions

**Description:** Special cases, exclusions, and situations where general rules don't apply.

**Priority:** 🟢 Supporting

**Attributes:**

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `exception_to` | string | ✅ | What rule does this modify |
| `exception_description` | string | ✅ | What the exception is |
| `conditions` | list[string] | Optional | When does exception apply |
| `statutory_basis` | string | Optional | BIA section |
| `case_law_examples` | list[string] | Optional | Cases illustrating exception |
| `practical_implications` | string | Optional | What this means in practice |

**Example Extraction:**
```json
{
  "exception_to": "General rule that all debtor assets vest in trustee upon bankruptcy",
  "exception_description": "Certain property is exempt and cannot be seized by trustee",
  "conditions": [
    "Property is necessary household furniture and furnishings",
    "Tools of trade up to prescribed value",
    "Registered pension plans (with some limits)",
    "Property held in trust for others"
  ],
  "statutory_basis": "BIA s. 67(1)(b)",
  "practical_implications": "Debtor retains basic necessities and ability to earn living post-bankruptcy"
}
```

**Target Count:** 20-30 exceptions

---

### 14. Pitfalls

**Description:** Common mistakes, traps for the unwary, and frequently misunderstood points.

**Priority:** 🟢 Supporting (but very useful for exam prep!)

**Attributes:**

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `pitfall_description` | string | ✅ | What the mistake is |
| `why_problematic` | string | ✅ | Why this is a problem |
| `consequences` | string | ✅ | What happens if mistake made |
| `how_to_avoid` | string | ✅ | How to avoid the mistake |
| `related_deadline` | string | Optional | If deadline-related |
| `related_document` | string | Optional | If document-related |
| `real_world_example` | string | Optional | Actual example |

**Example Extraction:**
```json
{
  "pitfall_description": "Counting calendar days instead of clear days for meeting notice",
  "why_problematic": "Results in insufficient notice period; meeting may be invalid",
  "consequences": "Meeting must be adjourned and re-noticed; wastes time and money; may delay distribution to creditors",
  "how_to_avoid": "Always check whether statute specifies calculation method; when in doubt, apply Interpretation Act rules (clear days); use deadline calculator",
  "related_deadline": "10 days notice for first meeting of creditors (BIA s. 102)",
  "real_world_example": "Trustee scheduled meeting for Friday and sent notice the previous Monday, thinking that was 10 days. Actually only 7 clear days. Meeting had to be rescheduled."
}
```

**Target Count:** 15-25 pitfalls

---

## Validation Rules

### General Rules (All Categories)

1. **Source Grounding Required:**
   - Every extraction MUST be traceable to source
   - Include page number if available
   - Character position for precise location

2. **Text Length:**
   - Required string fields: minimum 5 characters
   - Descriptions: minimum 20 characters
   - Definitions: minimum 10 characters

3. **Enum Values:**
   - Must use exact values specified in schema
   - Case-sensitive
   - No custom values unless specified as "other"

4. **Statutory References:**
   - Format: "BIA s. X" or "CCAA s. X"
   - Must be actual section numbers
   - Include subsection if applicable: "s. 43(1)"

### Category-Specific Rules

**Deadlines:**
- `timeframe` must contain a number
- `calculation_method` must be one of: business_days, calendar_days, clear_days
- `statutory_reference` is mandatory
- `triggering_event` must be specific, not vague

**Statutory References:**
- `section_number` must be numeric or contain valid format (e.g., "65.13")
- `practical_effect` mandatory (explanation required)
- Cross-references must use valid format

**Role Obligations:**
- `role_type` must be from approved list
- `obligation_type` must be one of: Duty, Power, Prohibition, Discretion
- Must specify who obligation is owed to

---

## Quality Criteria

### Extraction Quality Checklist

**For each example, verify:**

✅ **Accuracy**
- [ ] Information is factually correct
- [ ] Quotes are exact (if quoting)
- [ ] No hallucinated details

✅ **Completeness**
- [ ] All required attributes present
- [ ] No critical information missing
- [ ] Related concepts noted

✅ **Clarity**
- [ ] Definitions are clear and concise
- [ ] No jargon without explanation
- [ ] Examples aid understanding

✅ **Relevance**
- [ ] Information is exam-relevant
- [ ] Not overly obscure or tangential
- [ ] Appropriate importance level

✅ **Consistency**
- [ ] Terminology consistent across extractions
- [ ] Format matches schema
- [ ] Enum values used correctly

✅ **Source Grounding**
- [ ] Can locate in source document
- [ ] Page number noted
- [ ] Context preserved

### Quality Levels

**Excellent (90-100%):**
- All required fields present and accurate
- Rich detail and context
- Perfect source grounding
- Clear and exam-relevant

**Good (75-89%):**
- Required fields present
- Minor gaps in optional fields
- Source grounding present
- Generally clear and relevant

**Acceptable (60-74%):**
- Core information present
- Some missing optional fields
- Source grounding may be approximate
- Useful but could be better

**Poor (<60%):**
- Missing required fields
- Factual errors
- No source grounding
- Not useful for exam prep

**Target:** 90%+ of extractions should be "Excellent" or "Good"

---

## Priority Extraction Order

**UPDATED GUIDANCE:** Based on Lang Extract documentation, 3-5 high-quality examples per category is optimal!

### Day 1: Critical Foundation (Test After Each!)
1. **Concepts** (3-5 examples) → Test immediately!
2. **Statutory References - BIA** (3-5 examples) → Test!
3. **Deadlines** (3-5 examples - include calculation methods!) → Test!

### Day 2: Core Knowledge (Test After Each!)
4. **Role Obligations** (4 examples) → Test!
5. **Principles** (4 examples) → Test!
6. **Procedures** (4 examples) → Test!

### Day 3: Supporting Information (Batch Test)
7. **Document Requirements** (3 examples)
8. **Event Triggers** (3 examples)
9. **Communication Requirements** (3 examples)
10. **Relationships** (3 examples)
→ Test all 4 categories together

### Day 4: Contextual (Batch Test)
11. **Cases** (3 examples)
12. **Requirements** (3 examples)
13. **Exceptions** (3 examples)
14. **Pitfalls** (3 examples)
→ Test all 4 categories together + final refinement

**Total:** 40-65 examples over 4 days (much more efficient!)

---

## Notes for Example Creation

### Best Practices

1. **Start Simple**
   - Begin with obvious, clear-cut examples
   - Add complexity gradually
   - Test extraction early

2. **Diversity Matters**
   - Include various types within each category
   - Mix simple and complex examples
   - Cover different topics

3. **Source Quality**
   - Use actual text from your PDF
   - Verify accuracy
   - Note page numbers

4. **Test Early, Test Often**
   - Don't wait until all examples done
   - Test with 3-5 examples first
   - Refine based on results

5. **Document Decisions**
   - Note why you included/excluded something
   - Track edge cases
   - Keep a log of questions

### Common Questions

**Q: How long should a definition be?**
A: 1-3 sentences. Long enough to be clear, short enough to be concise.

**Q: Should I extract historical information?**
A: Only if exam-relevant. Focus on current law and practice.

**Q: What if I'm not sure about calculation method?**
A: Note uncertainty in `day_type_specified` field. Can refine later.

**Q: How do I handle conflicting information?**
A: Note both versions and the source of conflict. Flag for review.

**Q: Should I paraphrase or quote?**
A: For statutory text, quote exactly. For explanations, paraphrase is fine.

---

## Appendix: Example Template

```python
import langextract as lx

# Template for creating examples
example_name = lx.data.ExampleData(
    text="""
    [Paste relevant text from source here.
    Include enough context for the extraction to make sense.
    Usually 2-5 sentences.]
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="[category_name]",
            extraction_text="[The specific text being extracted]",
            attributes={
                "required_field_1": "value",
                "required_field_2": "value",
                "optional_field": "value",
                # ... all relevant attributes
            }
        )
    ]
)
```

---

This specification is your guide for Phase 3 (Schema Design & Examples). Follow it carefully when creating examples, and you'll build a high-quality knowledge base!
