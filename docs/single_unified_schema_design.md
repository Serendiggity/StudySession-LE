# Single Unified Relationship Schema - Graph Database Approach

## Can ONE Schema Handle Both BIA and Study Materials?

**Answer: YES - using a semantic graph model (RDF/triple-store inspired)**

---

## The Universal Pattern: Subject-Predicate-Object

**Every relationship can be expressed as:**
```
Subject → Predicate → Object [+ Context]
```

**Examples:**

### BIA Statements
```
Trustee → shall_perform → file_cash_flow [within 10 days]
Transfer → is_void_against → Trustee [if within 3 months]
Bankrupt → is_entitled_to → surplus [after creditors paid]
Creditor → may_not_exceed → 100_cents_on_dollar [payment limit]
```

### Study Material Statements
```
Step_6.2 → precedes → Step_6.3 [in Chapter 6 workflow]
Chapter_6 → contains → Step_6.2 [hierarchical]
Step_6.4 → implements → BIA_s_49 [cross-reference]
Study_Concept → explains → BIA_deemed_assignment [elaboration]
```

**All fit the same pattern with different predicates!**

---

## Single Universal Schema Design

```sql
-- ============================================================================
-- Universal Relationship Table (Graph Database Style)
-- ============================================================================

CREATE TABLE relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- ================================================================
    -- SUBJECT (what/who the relationship is about)
    -- ================================================================
    subject_entity_id INTEGER,
    subject_entity_type TEXT NOT NULL,  -- 'actor', 'procedure', 'document', 'section', 'concept'
    subject_text TEXT,                  -- If not a linked entity

    -- ================================================================
    -- PREDICATE (the type of relationship)
    -- ================================================================
    predicate TEXT NOT NULL,

    -- ================================================================
    -- OBJECT (what the subject relates to)
    -- ================================================================
    object_entity_id INTEGER,
    object_entity_type TEXT,
    object_text TEXT,

    -- ================================================================
    -- CONTEXT & METADATA
    -- ================================================================
    context JSON,                       -- Flexible structured data:
                                        -- {
                                        --   "timing": "within 10 days",
                                        --   "condition": "if opposition filed",
                                        --   "sequence_order": 3,
                                        --   "modality": "mandatory",
                                        --   "chapter": "6 PREPARE DOCUMENTS"
                                        -- }

    -- ================================================================
    -- SOURCE TRACKING
    -- ================================================================
    source_id INTEGER NOT NULL,
    source_section TEXT NOT NULL,       -- BIA section or study material section
    source_text TEXT,                   -- Original sentence

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (source_id) REFERENCES source_documents(id)
);

-- ================================================================
-- PREDICATE VOCABULARY (Controlled Terminology)
-- ================================================================

CREATE TABLE relationship_predicates (
    predicate TEXT PRIMARY KEY,
    category TEXT NOT NULL,             -- 'deontic', 'workflow', 'legal_effect', 'structural'
    description TEXT,
    applies_to_sources TEXT,            -- 'BIA', 'study_materials', 'all'
    example TEXT
);

-- Populate predicate vocabulary
INSERT INTO relationship_predicates VALUES
    -- Deontic predicates (BIA, directives)
    ('shall_perform', 'deontic', 'Mandatory obligation', 'BIA,directives', 'Trustee shall_perform file_proposal'),
    ('must_perform', 'deontic', 'Mandatory obligation', 'BIA,directives', 'Bankrupt must_perform attend_examination'),
    ('may_perform', 'deontic', 'Discretionary permission', 'BIA,directives', 'Creditor may_perform file_claim'),
    ('shall_not_perform', 'deontic', 'Prohibition', 'BIA,directives', 'Trustee shall_not_perform delegate_duty_X'),
    ('may_not_perform', 'deontic', 'Prohibition', 'BIA,directives', 'Creditor may_not_perform commence_action'),

    -- Legal effect predicates (BIA)
    ('is_void_against', 'legal_effect', 'Transaction void status', 'BIA', 'Transfer is_void_against Trustee'),
    ('is_valid_if', 'legal_effect', 'Valid transaction condition', 'BIA', 'Payment is_valid_if arm_length'),
    ('is_deemed', 'legal_effect', 'Legal presumption', 'BIA', 'Proposal is_deemed accepted'),
    ('is_entitled_to', 'legal_effect', 'Entitlement/right', 'BIA', 'Bankrupt is_entitled_to surplus'),

    -- Workflow predicates (study materials)
    ('precedes', 'workflow', 'Sequential order', 'study_materials', 'Step_6.2 precedes Step_6.3'),
    ('follows', 'workflow', 'Sequential order (reverse)', 'study_materials', 'Step_6.3 follows Step_6.2'),
    ('is_parallel_to', 'workflow', 'Can do simultaneously', 'study_materials', 'Step_A is_parallel_to Step_B'),

    -- Structural predicates (all sources)
    ('contains', 'structural', 'Hierarchical containment', 'all', 'Chapter_6 contains Section_6.2'),
    ('is_part_of', 'structural', 'Membership', 'all', 'Section_6.2 is_part_of Chapter_6'),
    ('requires', 'structural', 'Dependency', 'all', 'Procedure requires Document'),

    -- Cross-source predicates (integration)
    ('implements', 'cross_source', 'Operationalizes legal requirement', 'study_materials', 'Study_step implements BIA_s_49'),
    ('explains', 'cross_source', 'Educational elaboration', 'study_materials', 'Study_concept explains BIA_concept'),
    ('cites', 'cross_source', 'Reference to authority', 'all', 'Study_section cites BIA_s_50'),
    ('governed_by', 'cross_source', 'Legal authority', 'study_materials', 'Procedure governed_by BIA_s_102');
```

---

## How This Works

### Example 1: BIA Duty
```sql
INSERT INTO relationships (
    subject_entity_id, subject_entity_type,
    predicate,
    object_entity_id, object_entity_type,
    context,
    source_section
) VALUES (
    123, 'actor',              -- Trustee
    'shall_perform',           -- Predicate
    456, 'procedure',          -- file_cash_flow
    '{"timing": "within 10 days", "modality": "mandatory"}',
    '50.4'
);
```

**Query:**
```sql
-- What must trustee do?
SELECT object_text as action, context->>'timing' as deadline
FROM relationships r
JOIN actors a ON r.subject_entity_id = a.id
WHERE a.role_canonical = 'Trustee'
  AND predicate IN ('shall_perform', 'must_perform');
```

---

### Example 2: Study Material Workflow
```sql
INSERT INTO relationships (
    subject_entity_id, subject_entity_type,
    predicate,
    object_entity_id, object_entity_type,
    context,
    source_section
) VALUES (
    789, 'procedure',          -- Step 6.2
    'precedes',                -- Predicate
    790, 'procedure',          -- Step 6.3
    '{"sequence_order": 2, "chapter": "6 PREPARE DOCUMENTS"}',
    '6.2'
);
```

**Query:**
```sql
-- What's the workflow sequence?
SELECT
    p1.extraction_text as current_step,
    p2.extraction_text as next_step,
    context->>'sequence_order' as order
FROM relationships r
JOIN procedures p1 ON r.subject_entity_id = p1.id
JOIN procedures p2 ON r.object_entity_id = p2.id
WHERE predicate = 'precedes'
  AND context->>'chapter' = '6 PREPARE DOCUMENTS'
ORDER BY context->>'sequence_order';
```

---

### Example 3: Cross-Source Reference
```sql
INSERT INTO relationships (
    subject_entity_id, subject_entity_type,
    predicate,
    object_text,
    context,
    source_section
) VALUES (
    789, 'procedure',          -- Study Step 6.4
    'implements',              -- Predicate
    'BIA s. 49(2)',           -- Object (not entity, just text)
    '{"reference_type": "required_by"}',
    '6.4'
);
```

---

## Advantages of Single Universal Model

**✅ Pros:**
1. **One query language** - Same SELECT patterns for all sources
2. **Flexible** - Can add new predicates without schema changes
3. **Graph-friendly** - Can use graph traversal algorithms
4. **Cross-source joins** - Natural to link BIA ↔ Study materials
5. **Semantic clarity** - Predicate vocabulary is explicit and documented

**❌ Cons:**
1. **JSON queries** - `context->>'timing'` less clean than dedicated column
2. **Type safety** - Need application-layer validation
3. **Complex aggregations** - Counting by type requires JSON parsing
4. **Index complexity** - JSON fields harder to index

---

## Direct Answer: YES, It's Possible!

**Single table design:**

```sql
CREATE TABLE relationships (
    id INTEGER PRIMARY KEY,
    subject_entity_id INTEGER,
    subject_entity_type TEXT NOT NULL,
    subject_text TEXT,

    predicate TEXT NOT NULL,           -- Controlled vocabulary

    object_entity_id INTEGER,
    object_entity_type TEXT,
    object_text TEXT,

    context JSON,                      -- All type-specific data

    source_id INTEGER NOT NULL,
    source_section TEXT NOT NULL,
    source_text TEXT,

    FOREIGN KEY (source_id) REFERENCES source_documents(id),
    CHECK (subject_entity_id IS NOT NULL OR subject_text IS NOT NULL),
    CHECK (object_entity_id IS NOT NULL OR object_text IS NOT NULL)
);

CREATE INDEX idx_rel_predicate ON relationships(predicate);
CREATE INDEX idx_rel_subject ON relationships(subject_entity_id, subject_entity_type);
CREATE INDEX idx_rel_object ON relationships(object_entity_id, object_entity_type);
CREATE INDEX idx_rel_source ON relationships(source_id);
```

**With predicate vocabulary table to maintain semantic clarity.**

---

## Comparison: Typed Tables vs Universal Table

| Aspect | 10 Typed Tables | 1 Universal Table |
|--------|-----------------|-------------------|
| **Query Complexity** | Simple: `SELECT * FROM deontic_relationships` | Medium: `SELECT * FROM relationships WHERE predicate='shall_perform'` |
| **Semantic Clarity** | High: Table name = meaning | High: Predicate vocab = meaning |
| **Flexibility** | Low: New type = new table | High: New type = new predicate |
| **Type Safety** | High: Column types enforced | Medium: JSON + app validation |
| **Schema Complexity** | High: 10+ tables | Low: 1 table + vocab |
| **Performance** | Fast: Dedicated indexes | Fast: Predicate indexes |
| **Understandability** | High: Self-documenting | Medium: Need vocab reference |

---

## My Recommendation: Hybrid of Both Approaches

**Why not use BOTH?**

```sql
-- Core universal table for storage
CREATE TABLE relationships (...);  -- As designed above

-- Typed VIEWS for easy querying
CREATE VIEW deontic_duties AS
SELECT * FROM relationships
WHERE predicate IN ('shall_perform', 'must_perform', 'may_perform');

CREATE VIEW workflow_steps AS
SELECT * FROM relationships
WHERE predicate IN ('precedes', 'follows', 'is_parallel_to');

CREATE VIEW legal_voidness AS
SELECT * FROM relationships
WHERE predicate IN ('is_void_against', 'is_voidable');
```

**Benefits:**
✅ Storage: One flexible table
✅ Queries: Clean typed views
✅ Both semantic clarity AND flexibility

**This gives you the best of both worlds!**

Want me to implement this single universal model?