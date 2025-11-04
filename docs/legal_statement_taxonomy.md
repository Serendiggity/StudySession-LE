# Comprehensive Legal Statement Taxonomy - BIA

## Analysis of 847 Extracted Relationships + Missing Patterns

Based on empirical analysis of the Bankruptcy and Insolvency Act.

---

## 1. DEONTIC STATEMENTS (What parties MUST/MAY/MAY NOT do)

### 1.1 Obligations (362 occurrences)
**Pattern:** `Actor SHALL/MUST Action [Deadline] [OR Consequence]`

**Examples:**
- "Trustee shall file cash flow within 10 days"
- "Bankrupt must attend examination"

**Current Model:** ✅ `duty_relationships` with `duty_type='mandatory'`

---

### 1.2 Permissions (285 occurrences)
**Pattern:** `Actor MAY Action [Condition]`

**Examples:**
- "Creditor may obtain cash flow statement"
- "Court may extend deadline"

**Current Model:** ✅ `duty_relationships` with `duty_type='discretionary'`

---

### 1.3 Prohibitions (80 occurrences)
**Pattern:** `Actor SHALL NOT / MAY NOT Action`

**Examples:**
- "Creditor shall not commence proceedings during stay"
- "Trustee may not delegate certain duties"

**Current Model:** ✅ `duty_relationships` with `duty_type='prohibited'`

**Coverage: 727 / 847 = 86% ✅**

---

## 2. CONTENT/REQUIREMENT STATEMENTS (Currently Miscategorized)

### 2.1 Required Content (87 occurrences - NULL modal)
**Pattern:** `Document MUST CONTAIN Item(s)`

**Examples:**
- "Notice of Intention stating: (a) intention, (b) trustee name, (c) creditor list"
- "Proposal must contain: (a) payment terms, (b) cash flow"

**Current Model:** ❌ Extracted as separate duty_relationships with NULL modal
**Should Be:** New table or sub-structure

```sql
-- Proposed model
CREATE TABLE content_requirements (
    document_id INTEGER,
    required_item TEXT,
    item_reference TEXT,  -- "(a)", "(b)", etc.
    is_mandatory BOOLEAN,
    parent_procedure_id INTEGER  -- Filing proposal, filing NOI, etc.
);
```

---

## 3. LEGAL EFFECTS & PRESUMPTIONS (Not captured)

### 3.1 Void/Invalid Transactions
**Pattern:** `Action/Transfer IS VOID IF Condition`

**Examples:**
- "Transfer is void if within 3 months and gives preference" (S. 95)
- "Transaction void against trustee if fraudulent"

**Current Model:** ❌ Not captured
**Should Be:**

```sql
CREATE TABLE legal_effects (
    subject_type TEXT,      -- 'transfer', 'payment', 'transaction'
    effect TEXT,            -- 'void', 'valid', 'voidable', 'stayed'
    condition TEXT,         -- When effect applies
    beneficiary_actor_id INTEGER,  -- Who benefits from void (trustee)
    against_actor_id INTEGER,      -- Against whom (creditor)
    bia_section TEXT
);
```

**Estimated missing:** 50-100 statements (Sections 95, 96, 97, 101, etc.)

---

### 3.2 Legal Presumptions
**Pattern:** `X IS DEEMED Y IF Condition`

**Examples:**
- "Proposal deemed accepted if majority votes yes"
- "Person deemed insolvent if liabilities > $1000"
- "Assignment deemed filed on date received"

**Current Model:** ❌ Only 1 captured (are deemed)
**Should Be:**

```sql
CREATE TABLE presumptions (
    subject_text TEXT,
    deemed_status TEXT,
    condition TEXT,
    rebuttable BOOLEAN,     -- Can be rebutted with evidence?
    bia_section TEXT
);
```

**Estimated missing:** 30-50 statements

---

## 4. ENTITLEMENTS & RIGHTS (Not captured)

### 4.1 Rights/Entitlements
**Pattern:** `Actor IS ENTITLED TO Benefit IF Condition`

**Examples:**
- "Bankrupt entitled to surplus after creditors paid" (S. 144)
- "Secured creditor entitled to realize security"
- "Inspector entitled to access books"

**Current Model:** ❌ Only 1 captured
**Should Be:**

```sql
CREATE TABLE entitlements (
    actor_id INTEGER,
    entitled_to TEXT,
    condition TEXT,
    priority INTEGER,       -- Order of entitlement
    superseded_by TEXT,     -- What takes priority
    bia_section TEXT
);
```

**Estimated missing:** 20-40 statements

---

## 5. CONSTRAINTS & LIMITS (Not captured)

### 5.1 Maximum/Minimum Limits
**Pattern:** `Subject SHALL NOT EXCEED Limit` or `Subject >= Minimum`

**Examples:**
- "Creditor shall not receive > 100 cents on dollar" (S. 134)
- "Aggregate extensions shall not exceed 5 months"
- "Claim must be >= $250 to vote"

**Current Model:** ❌ Not captured
**Should Be:**

```sql
CREATE TABLE constraints (
    subject TEXT,
    constraint_type TEXT,   -- 'maximum', 'minimum', 'fixed'
    limit_value TEXT,
    applies_to_actor_id INTEGER,
    bia_section TEXT
);
```

**Estimated missing:** 30-50 statements

---

## 6. DEFINITIONS & SCOPE (Partially captured)

### 6.1 Term Definitions
**Pattern:** `Term MEANS Definition`

**Examples:**
- "Surplus income means portion exceeding reasonable standard"
- "Insolvent person means person who is not bankrupt..."

**Current Model:** ✅ `concepts` table, BUT not linked to other entities
**Should Be:** Enhanced with relationships

```sql
-- Add to concepts table
ALTER TABLE concepts ADD COLUMN defines_entity_type TEXT;
ALTER TABLE concepts ADD COLUMN referenced_by_sections TEXT;
```

### 6.2 Applicability Rules
**Pattern:** `Section APPLIES/DOES NOT APPLY IF Condition`

**Examples:**
- "Sections 95-101 do not apply to Division I proposals"
- "This Part applies to corporations"

**Current Model:** ❌ Not captured
**Should Be:**

```sql
CREATE TABLE applicability_rules (
    applies_to_section TEXT,
    applies BOOLEAN,
    condition TEXT,
    exception TEXT,
    bia_section TEXT
);
```

---

## 7. CALCULATION FORMULAS (Not captured)

**Pattern:** `Value = Formula`

**Examples:**
- "Surplus income = total income - necessary living expenses"
- "Dividend = (estate value - costs) / creditor claims"

**Current Model:** ❌ Not captured
**Should Be:**

```sql
CREATE TABLE calculations (
    result_concept_id INTEGER,
    formula TEXT,
    component_1 TEXT,
    operator TEXT,
    component_2 TEXT,
    bia_section TEXT
);
```

---

## Comprehensive Relationship Model Design

### Option A: Typed Tables (Recommended)

**Pros:**
- Clear semantics
- Type-safe queries
- Easy to understand

**Cons:**
- 8-10 tables
- More complex schema

**Tables:**
1. ✅ `duty_relationships` (actions: shall/may/must)
2. ✅ `document_requirements` (procedure → document)
3. `content_requirements` (document → required items)
4. `legal_effects` (void/valid transactions)
5. `presumptions` (deemed statuses)
6. `entitlements` (rights to benefits)
7. `constraints` (limits/bounds)
8. `applicability_rules` (when sections apply)
9. `calculations` (formulas)

---

### Option B: Generic Triple Store

```sql
CREATE TABLE relationships (
    id INTEGER PRIMARY KEY,
    subject_id INTEGER,
    subject_type TEXT,      -- actor, procedure, document, section, concept
    predicate TEXT,         -- 'shall_perform', 'is_void_if', 'is_entitled_to', etc.
    object_id INTEGER,
    object_type TEXT,
    condition TEXT,
    metadata JSON,          -- flexible additional data
    bia_section TEXT
);
```

**Pros:**
- One table handles everything
- Infinitely flexible
- Easy to add new relationship types

**Cons:**
- Generic queries complex
- Less semantic meaning
- Harder to validate

---

### Option C: Hybrid (Recommended for You)

**Core typed tables for common patterns:**
- `duty_relationships` (actions - 86% of statements)
- `document_requirements` (already working)

**Generic table for rare patterns:**
```sql
CREATE TABLE legal_statements (
    id INTEGER PRIMARY KEY,
    statement_type TEXT,    -- 'legal_effect', 'presumption', 'entitlement', 'constraint', 'definition'
    subject TEXT,
    predicate TEXT,
    object TEXT,
    condition TEXT,
    entities JSON,          -- {actor_ids: [...], procedure_ids: [...]}
    bia_section TEXT
);
```

**Benefit:**
- 86% in clean typed tables
- 14% in flexible generic table
- Easy to query common cases
- Can handle edge cases

---

## Key Design Principles

1. **Relationship = Semantic Connection Between 2+ Concepts**
   - NOT just sentence fragments
   - NOT list items (those are attributes)
   - NOT subordinate clauses

2. **Relationships Must Be Query-able**
   - "Show me all void transactions" → legal_effects table
   - "What is trustee entitled to?" → entitlements table
   - "What are the limits?" → constraints table

3. **Extraction Should Be Atomic**
   - One relationship = one database row
   - List items should be: one parent relationship + child items

---

## Recommendation

**Hybrid approach with 5 tables:**
1. ✅ `duty_relationships` - keep as-is (86% coverage)
2. ✅ `document_requirements` - keep as-is
3. ⭐ `legal_effects` - add for Section 95-type
4. ⭐ `entitlements` - add for Section 144-type
5. ⭐ `legal_statements` - generic catch-all for rare patterns

**This covers 95%+ of BIA with clear semantics.**

Sound good?
