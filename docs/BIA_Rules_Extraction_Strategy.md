# BIA Rules Extraction Strategy - Document Pattern Analysis

**Source:** BIA General Rules (C.R.C., c. 368) - 59 pages, 138 sections
**Date:** 2025-11-04
**Purpose:** Align extraction categories with document patterns and existing database schema

---

## PART 1: DOCUMENT PATTERNS IN BIA RULES

### Pattern 1: Definitions (Section 1)
**Text structure:** "X means Y" or "X, in relation to Z, means Y"

**Examples:**
- "business hours means the hours during which the Division Office is open..."
- "judge means a judge of a court having jurisdiction in bankruptcy..."
- "directive means a directive issued by the Superintendent..."

**Quantity:** ~10 definitions in Section 1

**Database fit:** ✅ PERFECT → `concepts` table
- term = X
- definition = Y
- importance = "medium" (regulatory definitions)

---

### Pattern 2: Actor Duties & Responsibilities (Throughout)
**Text structure:** "[ACTOR] shall [ACTION]" or "[ACTOR] must [ACTION]"

**Examples:**
- "Trustees shall perform their duties in a timely manner..." (§36)
- "The trustee shall, within 30 days..." (§60)
- "The official receiver may request instructions..." (§33)
- "The registrar shall transmit..." (§32)

**Quantity:** ~100+ duty statements

**Actors identified:**
- Primary: trustee, official receiver, registrar, administrator, interim receiver
- Secondary: bankrupt, creditor, court, Superintendent, mediator, contributory
- Special: partnership, corporation, consumer debtor

**Database fit:** ✅ GOOD → `actors`, `duty_relationships` tables
- role_canonical = trustee, official receiver, etc.
- relationship_text = full sentence
- modal_verb = shall, must, may

---

### Pattern 3: Time Requirements (Throughout)
**Text structure:** "within X days" or "at least X days before" or "not later than X days"

**Examples:**
- "within 30 days after receiving the letter" (§60)
- "at least 10 days before the day of the meeting" (§108)
- "not later than five days before the first meeting" (§102)
- "within three months after" (§65)

**Quantity:** ~50+ deadline references

**Types of deadlines:**
- After event: "within X days after [event]"
- Before event: "at least X days before [event]"
- Absolute: "not later than [date/time]"
- Conditional: "unless the court orders otherwise"

**Database fit:** ✅ PERFECT → `deadlines` table
- timeframe = "within 30 days", "at least 10 days before"
- context captured in `procedures` linkage

---

### Pattern 4: Document Requirements (Throughout)
**Text structure:** "shall send/file [DOCUMENT] in prescribed form"

**Examples:**
- "send...a notice in prescribed form" (§117)
- "file with the official receiver a copy of the consumer proposal" (§66.13)
- "certificate of compliance and deemed discharge, in prescribed form" (§65)
- "notice of taxation...in prescribed form" (§64)

**Quantity:** ~40+ document references

**Document types:**
- Notices (bankruptcy, meeting, taxation, discharge)
- Statements (receipts & disbursements, affairs, income & expense)
- Certificates (appointment, compliance, discharge)
- Reports (mediator, trustee, administrator)

**Database fit:** ✅ GOOD → `documents`, `document_requirements` tables
- document_name = extracted
- document_name_canonical = normalized
- is_mandatory = TRUE (when "must/shall")
- filing_context = from surrounding text

---

### Pattern 5: Fee Structures (Sections 128-136, Schedule)
**Text structure:** "$X for [SERVICE]" or "X% on [AMOUNT]"

**Examples:**
- "$75 for an estate under summary administration" (§132)
- "100 per cent on the first $975 or less of receipts" (§128)
- "five per cent, if the amount of payments is $1,000,000 or less" (§123)
- "$85 per session if counselling is provided" (§131)

**Quantity:** ~30+ fee specifications

**Fee types:**
- Filing fees (flat amounts)
- Trustee remuneration (percentage-based)
- Court officer fees (per service)
- Levy rates (tiered percentages)

**Database fit:** ❌ NO TABLE
- **Recommendation:** Create new `fees` table
- Attributes: fee_amount, fee_type, service_description, applies_to, section_reference

---

### Pattern 6: Procedural Steps (Multi-step processes)
**Text structure:** Sequential instructions with (a), (b), (c) subsections

**Examples:**
**§66 - Taxation and discharge process:**
1. "shall...send to each creditor" (a) notice, (b) statement, (c) dividend sheet
2. "within two months after...shall" (a) send dividend, (b) close account, (c) remit funds, (d) send certificate

**Quantity:** ~20 multi-step procedures

**Database fit:** ⚠️ PARTIAL → `procedures` table has `step_order`
- Can capture sequential steps
- Need to parse subsection structure

---

### Pattern 7: Exceptions & Conditions (Throughout)
**Text structure:** "unless...", "subject to...", "except when..."

**Examples:**
- "unless the court orders otherwise" (§60)
- "Subject to subsection (2)" (§5)
- "Except when it would constitute a second adjournment" (§105)

**Quantity:** ~40+ conditional clauses

**Database fit:** ⚠️ PARTIAL → could map to `consequences`
- But consequences table focuses on outcomes, not conditions
- **Gap:** No "conditions" or "exceptions" field in current schema

---

### Pattern 8: Cross-References (Throughout)
**Text structure:** "pursuant to section X", "referred to in subsection Y(Z)"

**Examples:**
- "pursuant to subsection 152(4) of the Act" (§60)
- "referred to in subsection 161(1)" (§57)
- "under section 68 of the Act" (§105)

**Quantity:** ~200+ cross-references

**Database fit:** ✅ EXCELLENT → `statutory_references` table
- reference = full citation
- act = "BIA" (or parse to "Act")
- section = parsed section number

---

## PART 2: ALIGNMENT WITH EXISTING SCHEMA

### ✅ WELL-ALIGNED CATEGORIES (Extract these first)

| BIA Rules Pattern | DB Table | Fields | Priority |
|-------------------|----------|--------|----------|
| Definitions (§1) | `concepts` | term, definition, importance | HIGH |
| Actor duties | `actors` + `duty_relationships` | role_canonical, relationship_text | HIGH |
| Time requirements | `deadlines` | timeframe | HIGH |
| Document requirements | `documents` + `document_requirements` | document_name_canonical, is_mandatory | HIGH |
| Cross-references | `statutory_references` | reference, act, section | MEDIUM |
| Procedural steps | `procedures` | step_name, action, step_order | MEDIUM |

### ❌ GAPS IN SCHEMA (Need new tables or fields)

| BIA Rules Pattern | Missing From Schema | Recommendation |
|-------------------|---------------------|----------------|
| Fee structures | No `fees` table | **CREATE** new table |
| Format specifications | No format fields in `documents` | **ADD** column: format_specs TEXT |
| Conditions/exceptions | No conditions capture | **ADD** column to relevant tables: conditions TEXT |
| Purposes/rationales | No purpose field | **ADD** to procedures: purpose TEXT |

---

## PART 3: SPECIFIC TO EXAM QUESTIONS

### Q11: Partnership Assignment Execution
**Relevant section:** §114 (Bankrupt Partnerships)
**Pattern found:** "each bankrupt partner shall submit"
**What's extractable:** Actor duties (plural requirement)
**What's missing:** WHO SIGNS the actual assignment document
**Conclusion:** §114 addresses STATEMENTS, not ASSIGNMENT execution
**Answer source:** Likely in **BIA §49 interpretation** or **case law**, NOT in Rules

---

### Q15: Purpose of Newspaper Publication
**Relevant section:** BIA §102(4) + Study Materials
**Pattern found:** PURPOSE statement in study materials
**What's extractable:** "explains bankrupt's legal status to anyone who may do business"
**Database category:** Could be `consequences` (effect of publication)
**Conclusion:** ✅ FOUND in study materials (already extracted)

---

### Q16/Q19: Publication Standards
**Relevant section:** §102(4) references "prescribed form"
**Pattern found:** Indirect reference to Form specification
**What's extractable:** "prescribed form" link
**What's missing:** The FORM itself (Form 79) with actual standards
**Conclusion:** Standards are in **BIA Forms** (separate document set), not in Rules text

---

### Q17: Definition of "Newspaper"
**Relevant section:** §1 (Definitions)
**Pattern found:** Section 1 lists definitions, "newspaper" absent
**What's extractable:** Negative finding (not defined here)
**What's missing:** External definition (Interpretation Act?)
**Conclusion:** Definition is in **Interpretation Act** or **common law**, not in BIA Rules

---

## PART 4: EXTRACTION RECOMMENDATION

### Phase 1: Extract What Aligns (Use existing schema)

**Categories to extract from BIA Rules:**
1. **Concepts** (§1 definitions) → `concepts` table
2. **Actor duties** (all "shall/must" statements) → `actors`, `duty_relationships`
3. **Deadlines** (all timeframes) → `deadlines`
4. **Documents** (all "prescribed form" references) → `documents`
5. **Statutory references** (all cross-refs) → `statutory_references`
6. **Procedures** (sequential steps in subsections) → `procedures`

**Estimated entities:** ~300-400 total

---

### Phase 2: Identify Gaps (For schema enhancement)

**What BIA Rules contains that we CAN'T capture:**
- Fee amounts and structures (no table)
- Format specifications (no field)
- Conditional clauses (no field)
- Purpose statements (no field)

**Recommendation:**
1. Extract what fits existing schema NOW
2. Log gaps for future schema v3 design
3. For missing exam answers, acknowledge they're in external sources (Forms, Interpretation Act)

---

## PART 5: ANSWER TO EXAM QUESTION GAPS

### Q11 - Not in BIA Rules
**Why:** Rules address statements of affairs, not assignment execution signatures
**Real source:** Partnership law principles or BIA §49 interpretation
**Extract value:** Low (won't help answer Q11)

### Q16/19 - Not in BIA Rules text
**Why:** "prescribed form" points to external BIA Forms document
**Real source:** BIA Form 79 (Notice of Bankruptcy specimen)
**Extract value:** Medium (can capture the reference, not the content)

### Q17 - Not in BIA Rules
**Why:** Not a bankruptcy-specific term, uses general legal definition
**Real source:** Canada Interpretation Act or common law
**Extract value:** None (definition is external)

---

## CONCLUSION

**Should we extract BIA Rules?**

**YES** - for general knowledge base completeness:
- Adds ~300-400 entities (duties, deadlines, documents, refs)
- Enriches understanding of procedural requirements
- Aligns well with existing schema

**NO** - for answering these specific exam questions:
- Q11: Not in Rules (partnership signature law)
- Q16/19: Not in Rules (need Form 79)
- Q17: Not in Rules (need Interpretation Act)

**Better approach for exam questions:**
1. **Q11:** Search for partnership bankruptcy case law or textbook
2. **Q16/19:** Fetch BIA Form 79 from OSB forms library
3. **Q17:** Check Canada Interpretation Act definitions

---

**Recommended next steps:**
1. Skip BIA Rules extraction for now (won't help exam)
2. Fetch missing sources that WILL help (Forms, Interpretation Act)
3. Return to BIA Rules extraction later for general knowledge base enhancement
