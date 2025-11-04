# Study Material Relationship Types (Distinct from BIA)

## Key Insight: Different Content Type = Different Relationships

**BIA:** Primary law (deontic statements - shall/may/must)
**Study Materials:** Educational synthesis (workflows + explanations + cross-references)

---

## Study Material Relationship Types

### 1. SEQUENTIAL WORKFLOW RELATIONSHIPS
**Pattern:** Step A → THEN → Step B

**Examples from Chapter 6 (Prepare Documents):**
```
6.2 Document Preparation
  ↓ THEN
6.3 Obtain Trustee's assessment
  ↓ THEN
6.4 Prepare documents required
  ↓ THEN
6.5 Review and share with Trustee
  ↓ THEN
6.6 Obtain debtor's and Trustee's signature
  ↓ THEN
6.7 Submit to OSB
```

**Schema:**
```sql
CREATE TABLE workflow_sequences (
    id INTEGER PRIMARY KEY,
    step_procedure_id INTEGER,      -- Current step
    next_step_procedure_id INTEGER, -- Next step
    sequence_order INTEGER,         -- 1, 2, 3, 4...
    is_mandatory_sequence BOOLEAN,  -- Must do in order?
    chapter_context TEXT,           -- "6 PREPARE DOCUMENTS FOR OSB"
    source_id INTEGER
);
```

---

### 2. HIERARCHICAL RELATIONSHIPS
**Pattern:** Chapter CONTAINS Sections CONTAINS Subsections

**Example:**
```
6 PREPARE DOCUMENTS FOR OSB
  ├─ 6.1 Introduction
  ├─ 6.2 Document Preparation
  │   ├─ 6.2.1 Review information
  │   └─ 6.2.2 Verify data
  ├─ 6.3 Obtain assessment
  └─ 6.7 Submit to OSB
```

**Schema:**
```sql
CREATE TABLE workflow_hierarchy (
    id INTEGER PRIMARY KEY,
    parent_section TEXT,        -- "6 PREPARE DOCUMENTS"
    child_procedure_id INTEGER, -- Procedure in that section
    depth_level INTEGER,        -- 0=chapter, 1=section, 2=subsection
    sibling_order INTEGER,      -- Position among siblings
    source_id INTEGER
);
```

---

### 3. CROSS-REFERENCE RELATIONSHIPS
**Pattern:** Study Material Step REFERENCES BIA Section

**Examples:**
- "6.4 Prepare documents required" → cites BIA s. 49(2), BIGR Form 79
- "Assessment interview" → references BIA s. 157, Directive 6R7
- "First meeting" → governed by BIA s. 102

**Schema:**
```sql
CREATE TABLE educational_cross_references (
    id INTEGER PRIMARY KEY,
    study_material_procedure_id INTEGER,    -- Study material step
    references_bia_section TEXT,            -- BIA section cited
    references_statutory_ref_id INTEGER,    -- Link to statutory_references
    reference_context TEXT,                 -- Why it's referenced
    reference_type TEXT,                    -- 'required_by', 'governed_by', 'see_also'
    source_id INTEGER
);
```

---

### 4. EXPLANATION RELATIONSHIPS
**Pattern:** Study Material EXPLAINS BIA Concept

**Examples:**
- Study material explains "deemed assignment" concept from BIA s. 50.4
- Study material elaborates on "surplus income" from BIA s. 68
- Study material provides examples of "fraudulent preferences" from BIA s. 95

**Schema:**
```sql
CREATE TABLE educational_elaborations (
    id INTEGER PRIMARY KEY,
    study_material_concept_id INTEGER,  -- Concept in study materials
    explains_bia_section TEXT,          -- BIA section being explained
    explains_concept_id INTEGER,        -- Concept from concepts table
    elaboration_type TEXT,              -- 'example', 'clarification', 'procedure'
    source_id INTEGER
);
```

---

### 5. PRACTICAL GUIDANCE (Study-specific)
**Pattern:** Step REQUIRES Practical Action

**Examples:**
- "Contact OSB directly to request payment" (not in BIA)
- "Count petty cash and deposit into estate bank account" (practical step)
- "Retain copies of all documents" (best practice)

**Schema:**
```sql
CREATE TABLE practical_procedures (
    id INTEGER PRIMARY KEY,
    procedure_id INTEGER,
    is_best_practice BOOLEAN,       -- Best practice vs required
    practical_context TEXT,
    relates_to_bia_section TEXT,    -- Which BIA requirement this supports
    source_id INTEGER
);
```

---

## Compatibility Analysis

### Can v2 Schema Handle Study Materials?

**Partially:**

| Study Material Type | v2 Table | Compatibility |
|---------------------|----------|---------------|
| Workflow sequences | ❌ None | Need new table |
| Hierarchical structure | ❌ None | Need new table |
| Cross-references | ✅ Can use `applicability_rules` | ⚠️ Awkward fit |
| Explanations | ❌ None | Need new table |
| Practical guidance | ✅ Can use `duty_relationships` | ⚠️ Wrong semantics |

**Answer: NO - v2 schema is BIA-specific**

---

## Unified Relationship Model (Cross-Source Compatible)

### Option 1: Source-Specific Schemas

**BIA Schema:** 9 relationship types (deontic focus)
- duty_relationships, legal_effects, entitlements, etc.

**Study Material Schema:** 5 relationship types (workflow focus)
- workflow_sequences, hierarchy, cross_references, elaborations, practical_procedures

**Pros:** Each optimized for content type
**Cons:** Two separate systems, harder to query across sources

---

### Option 2: Unified Semantic Model

**Common abstraction layer:**

```sql
-- Universal relationship table
CREATE TABLE relationships_universal (
    id INTEGER PRIMARY KEY,

    -- Source identification
    source_id INTEGER NOT NULL,
    source_type TEXT NOT NULL,      -- 'statute', 'educational', 'directive'

    -- Relationship classification
    relationship_category TEXT,     -- 'deontic', 'workflow', 'reference', 'effect'
    relationship_type TEXT,         -- 'duty', 'sequence', 'cross_ref', 'void', etc.

    -- Entities involved
    subject_entity_id INTEGER,
    subject_entity_type TEXT,
    predicate TEXT,                 -- 'shall_perform', 'precedes', 'references', 'is_void'
    object_entity_id INTEGER,
    object_entity_type TEXT,

    -- Context
    condition TEXT,
    metadata JSON,                  -- Flexible for type-specific data

    section_reference TEXT,         -- BIA section or study material section
    created_at TIMESTAMP
);
```

**Pros:**
- One model handles all sources
- Can query across BIA + Study Materials
- Flexible for future sources (OSB directives, case law)

**Cons:**
- Generic = less clear semantics
- More complex queries
- Type-specific validation harder

---

### Option 3: Hybrid (Recommended)

**Core domain model (typed tables):**
- Keep v2's 9 BIA tables for statute content
- Add 5 study material tables for educational content

**Cross-cutting concerns (shared tables):**
```sql
-- Links between sources
CREATE TABLE cross_source_references (
    from_source_id INTEGER,
    from_entity_id INTEGER,
    from_entity_type TEXT,
    to_source_id INTEGER,
    to_bia_section TEXT,
    reference_type TEXT         -- 'implements', 'explains', 'cites', 'governed_by'
);
```

**Benefit:**
- Each source type has optimal schema
- Can still link across sources
- Clear semantics per domain

---

## Answer to Your Question

**Is v2 schema compatible with study materials?**

**NO** - they need different relationship types:

| Content Type | Primary Relationships | Schema Needed |
|--------------|----------------------|---------------|
| **BIA** | Deontic (shall/may/must) | v2: 9 typed tables ✅ |
| **Study Materials** | Workflows (step sequences) | NEW: 5 workflow tables ❌ |
| **Cross-Source** | References (cites/explains) | NEW: cross_source_references ❌ |

**Recommendation:**

Design a **three-layer architecture:**

1. **BIA Layer:** v2 schema (9 deontic relationship tables)
2. **Educational Layer:** 5 workflow relationship tables
3. **Integration Layer:** cross-source reference table

This properly handles ALL material types while maintaining semantic clarity.

**Want me to design the complete unified model?**
