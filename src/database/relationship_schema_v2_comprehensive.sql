-- ============================================================================
-- Comprehensive Relationship Schema v2
-- Captures ALL legal statement types in the BIA
-- ============================================================================

-- =================================================================
-- TIER 1: DEONTIC RELATIONSHIPS (Actions - 86% of statements)
-- =================================================================

-- 1.1 DUTY RELATIONSHIPS (Keep existing, add refinements)
-- Pattern: Actor SHALL/MUST/MAY Action [Deadline] [OR Consequence]
CREATE TABLE IF NOT EXISTS duty_relationships_v2 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Core entities
    actor_id INTEGER,
    procedure_id INTEGER,
    deadline_id INTEGER,
    consequence_id INTEGER,

    -- Deontic modality
    modal_verb TEXT NOT NULL,       -- shall, must, may, shall not, may not
    duty_type TEXT NOT NULL,        -- mandatory, discretionary, prohibited

    -- Context
    relationship_text TEXT NOT NULL,
    bia_section TEXT NOT NULL,

    -- Metadata
    source_id INTEGER,
    is_conditional BOOLEAN DEFAULT FALSE,
    condition_text TEXT,            -- IF condition applies

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (actor_id) REFERENCES actors(id),
    FOREIGN KEY (procedure_id) REFERENCES procedures(id),
    FOREIGN KEY (deadline_id) REFERENCES deadlines(id),
    FOREIGN KEY (consequence_id) REFERENCES consequences(id),
    FOREIGN KEY (source_id) REFERENCES source_documents(id),

    -- Validation: Must have at least actor OR procedure
    CHECK (actor_id IS NOT NULL OR procedure_id IS NOT NULL)
);

-- 1.2 DOCUMENT REQUIREMENTS (Keep existing)
CREATE TABLE IF NOT EXISTS document_requirements_v2 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    procedure_id INTEGER NOT NULL,
    document_id INTEGER NOT NULL,
    is_mandatory BOOLEAN DEFAULT TRUE,
    filing_context TEXT,
    bia_section TEXT,
    source_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (procedure_id) REFERENCES procedures(id),
    FOREIGN KEY (document_id) REFERENCES documents(id),
    FOREIGN KEY (source_id) REFERENCES source_documents(id)
);

-- =================================================================
-- TIER 2: CONTENT/STRUCTURAL RELATIONSHIPS
-- =================================================================

-- 2.1 CONTENT REQUIREMENTS (NEW - for list items in documents)
-- Pattern: Document MUST CONTAIN Item(s)
CREATE TABLE IF NOT EXISTS content_requirements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- What document/procedure requires content
    parent_document_id INTEGER,
    parent_procedure_id INTEGER,

    -- The required content
    required_content_text TEXT NOT NULL,
    item_reference TEXT,            -- "(a)", "(b)", "(1)", "paragraph 3"
    is_mandatory BOOLEAN DEFAULT TRUE,

    -- Context
    bia_section TEXT NOT NULL,
    source_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (parent_document_id) REFERENCES documents(id),
    FOREIGN KEY (parent_procedure_id) REFERENCES procedures(id),
    FOREIGN KEY (source_id) REFERENCES source_documents(id),

    -- Must have at least one parent
    CHECK (parent_document_id IS NOT NULL OR parent_procedure_id IS NOT NULL)
);

-- =================================================================
-- TIER 3: LEGAL EFFECTS & CONSEQUENCES
-- =================================================================

-- 3.1 LEGAL EFFECTS (NEW - void/valid/binding status)
-- Pattern: Action/Transfer IS VOID/VALID IF Condition
CREATE TABLE IF NOT EXISTS legal_effects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Subject of the effect (what becomes void/valid)
    subject_procedure_id INTEGER,   -- "transfer", "payment", "charge"
    subject_document_id INTEGER,    -- document that becomes void
    subject_description TEXT,       -- if not an extracted entity

    -- The legal effect
    effect_type TEXT NOT NULL,      -- 'void', 'voidable', 'valid', 'binding', 'stayed', 'unenforceable'

    -- Against/for whom
    void_against_actor_id INTEGER,  -- "void against trustee"
    benefits_actor_id INTEGER,      -- "trustee can void this"

    -- Conditions
    condition_text TEXT NOT NULL,   -- "if within 3 months of bankruptcy"
    is_rebuttable BOOLEAN DEFAULT FALSE,  -- Can be overcome with evidence?

    -- Context
    bia_section TEXT NOT NULL,
    relationship_text TEXT,
    source_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (subject_procedure_id) REFERENCES procedures(id),
    FOREIGN KEY (subject_document_id) REFERENCES documents(id),
    FOREIGN KEY (void_against_actor_id) REFERENCES actors(id),
    FOREIGN KEY (benefits_actor_id) REFERENCES actors(id),
    FOREIGN KEY (source_id) REFERENCES source_documents(id)
);

-- 3.2 PRESUMPTIONS (NEW - deemed statuses)
-- Pattern: X IS DEEMED Y IF Condition
CREATE TABLE IF NOT EXISTS presumptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- What is being deemed
    subject_text TEXT NOT NULL,
    subject_entity_id INTEGER,
    subject_entity_type TEXT,       -- 'proposal', 'person', 'assignment'

    -- What it's deemed to be
    deemed_status TEXT NOT NULL,    -- "accepted", "insolvent", "filed", "valid"

    -- Condition
    condition_text TEXT NOT NULL,
    is_rebuttable BOOLEAN DEFAULT TRUE,  -- Most presumptions are rebuttable

    -- Context
    bia_section TEXT NOT NULL,
    relationship_text TEXT,
    source_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (source_id) REFERENCES source_documents(id)
);

-- =================================================================
-- TIER 4: RIGHTS & CONSTRAINTS
-- =================================================================

-- 4.1 ENTITLEMENTS (NEW - rights to benefits)
-- Pattern: Actor IS ENTITLED TO Benefit IF Condition
CREATE TABLE IF NOT EXISTS entitlements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Who has the entitlement
    actor_id INTEGER NOT NULL,

    -- What they're entitled to
    entitled_to_text TEXT NOT NULL,
    entitled_to_entity_id INTEGER,
    entitled_to_entity_type TEXT,   -- 'surplus', 'fees', 'costs', 'security'

    -- Conditions
    condition_text TEXT,
    priority_order INTEGER,         -- Order of entitlement (1st, 2nd, etc.)
    superseded_by TEXT,             -- What takes priority over this

    -- Context
    bia_section TEXT NOT NULL,
    relationship_text TEXT,
    source_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (actor_id) REFERENCES actors(id),
    FOREIGN KEY (source_id) REFERENCES source_documents(id)
);

-- 4.2 CONSTRAINTS (NEW - limits and bounds)
-- Pattern: Subject SHALL NOT EXCEED Limit
CREATE TABLE IF NOT EXISTS constraints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- What is constrained
    subject_text TEXT NOT NULL,
    subject_entity_id INTEGER,
    subject_entity_type TEXT,       -- 'payment', 'extension', 'claim'

    -- The constraint
    constraint_type TEXT NOT NULL,  -- 'maximum', 'minimum', 'fixed', 'not_exceed'
    limit_value TEXT NOT NULL,      -- "100 cents on dollar", "5 months", "$250"
    limit_numeric REAL,             -- Parsed numeric value if applicable
    limit_unit TEXT,                -- "dollars", "months", "percent"

    -- Who it applies to
    applies_to_actor_id INTEGER,

    -- Context
    bia_section TEXT NOT NULL,
    relationship_text TEXT,
    source_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (applies_to_actor_id) REFERENCES actors(id),
    FOREIGN KEY (source_id) REFERENCES source_documents(id)
);

-- =================================================================
-- TIER 5: META-LEGAL RELATIONSHIPS
-- =================================================================

-- 5.1 APPLICABILITY RULES (NEW - when sections apply)
-- Pattern: Section APPLIES/DOES NOT APPLY IF Condition
CREATE TABLE IF NOT EXISTS applicability_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Which section's applicability is being defined
    applies_to_section TEXT NOT NULL,  -- Can be range: "Sections 95-101"

    -- Does it apply?
    applies BOOLEAN NOT NULL,

    -- Conditions
    condition_text TEXT,
    exception_text TEXT,

    -- Scope
    applies_to_actor_type TEXT,     -- "corporations", "individuals", "proposals"
    excludes_actor_type TEXT,

    -- Context
    defined_in_section TEXT NOT NULL,  -- Where this rule is stated
    relationship_text TEXT,
    source_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (source_id) REFERENCES source_documents(id)
);

-- 5.2 DEFINITIONAL RELATIONSHIPS (NEW - enhance concepts table)
-- Links concepts to the entities they define
CREATE TABLE IF NOT EXISTS concept_entity_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    concept_id INTEGER NOT NULL,    -- From concepts table

    -- What entity this concept defines/relates to
    defined_entity_id INTEGER,
    defined_entity_type TEXT,       -- 'actor', 'procedure', 'document', 'deadline'

    -- Relationship type
    relationship_type TEXT,         -- 'defines', 'includes', 'excludes', 'modifies'

    bia_section TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (concept_id) REFERENCES concepts(id),
    FOREIGN KEY (source_id) REFERENCES source_documents(id)
);

-- =================================================================
-- TIER 6: TRIGGER/CONDITIONAL RELATIONSHIPS (Redesigned)
-- =================================================================

-- 6.1 TRIGGER RELATIONSHIPS (Enhanced from v1)
-- Pattern: IF Condition THEN Consequence
CREATE TABLE IF NOT EXISTS trigger_relationships_v2 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Trigger source (what must happen/not happen)
    trigger_entity_id INTEGER,
    trigger_entity_type TEXT,       -- 'procedure', 'deadline', 'event', 'failure_to_act'
    trigger_condition TEXT NOT NULL,

    -- Result
    consequence_id INTEGER,
    consequence_text TEXT,

    -- Timing
    trigger_timing TEXT,            -- "immediately", "within 30 days", "on expiry of"

    -- Context
    bia_section TEXT NOT NULL,
    relationship_text TEXT,
    source_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (consequence_id) REFERENCES consequences(id),
    FOREIGN KEY (source_id) REFERENCES source_documents(id)
);

-- =================================================================
-- MIGRATION FROM V1 TO V2
-- =================================================================

-- Copy existing v1 data to v2 tables
INSERT INTO duty_relationships_v2
    (actor_id, procedure_id, deadline_id, consequence_id, modal_verb,
     duty_type, relationship_text, bia_section, source_id)
SELECT
    actor_id, procedure_id, deadline_id, consequence_id, modal_verb,
    duty_type, relationship_text, bia_section, source_id
FROM duty_relationships
WHERE modal_verb IS NOT NULL  -- Exclude the 87 NULL modal (list items);

INSERT INTO document_requirements_v2
SELECT * FROM document_requirements;

INSERT INTO trigger_relationships_v2
    (trigger_entity_id, trigger_entity_type, trigger_condition,
     consequence_id, bia_section, source_id)
SELECT
    trigger_entity_id, trigger_entity_type, trigger_condition,
    consequence_id, bia_section, source_id
FROM trigger_relationships;

-- =================================================================
-- INDEXES FOR PERFORMANCE
-- =================================================================

-- Duty relationships
CREATE INDEX IF NOT EXISTS idx_duty_v2_actor ON duty_relationships_v2(actor_id);
CREATE INDEX IF NOT EXISTS idx_duty_v2_procedure ON duty_relationships_v2(procedure_id);
CREATE INDEX IF NOT EXISTS idx_duty_v2_modal ON duty_relationships_v2(modal_verb);
CREATE INDEX IF NOT EXISTS idx_duty_v2_section ON duty_relationships_v2(bia_section);

-- Legal effects
CREATE INDEX IF NOT EXISTS idx_effect_type ON legal_effects(effect_type);
CREATE INDEX IF NOT EXISTS idx_effect_section ON legal_effects(bia_section);
CREATE INDEX IF NOT EXISTS idx_effect_benefits ON legal_effects(benefits_actor_id);

-- Entitlements
CREATE INDEX IF NOT EXISTS idx_entitle_actor ON entitlements(actor_id);
CREATE INDEX IF NOT EXISTS idx_entitle_section ON entitlements(bia_section);

-- Constraints
CREATE INDEX IF NOT EXISTS idx_constraint_type ON constraints(constraint_type);
CREATE INDEX IF NOT EXISTS idx_constraint_section ON constraints(bia_section);

-- Applicability
CREATE INDEX IF NOT EXISTS idx_applicability_to ON applicability_rules(applies_to_section);
CREATE INDEX IF NOT EXISTS idx_applicability_from ON applicability_rules(defined_in_section);

-- =================================================================
-- COMPREHENSIVE VIEWS
-- =================================================================

-- All actions (duties) with full context
CREATE VIEW IF NOT EXISTS v_all_duties AS
SELECT
    dr.id,
    a.role_canonical as actor,
    p.extraction_text as procedure,
    d.timeframe as deadline,
    c.outcome as consequence,
    dr.modal_verb,
    dr.duty_type,
    dr.is_conditional,
    dr.condition_text,
    dr.bia_section,
    sd.source_name
FROM duty_relationships_v2 dr
LEFT JOIN actors a ON dr.actor_id = a.id
LEFT JOIN procedures p ON dr.procedure_id = p.id
LEFT JOIN deadlines d ON dr.deadline_id = d.id
LEFT JOIN consequences c ON dr.consequence_id = c.id
LEFT JOIN source_documents sd ON dr.source_id = sd.id;

-- All legal effects (voidness, validity)
CREATE VIEW IF NOT EXISTS v_legal_effects AS
SELECT
    le.id,
    le.subject_description,
    le.effect_type,
    le.condition_text,
    a1.role_canonical as void_against,
    a2.role_canonical as benefits,
    le.is_rebuttable,
    le.bia_section
FROM legal_effects le
LEFT JOIN actors a1 ON le.void_against_actor_id = a1.id
LEFT JOIN actors a2 ON le.benefits_actor_id = a2.id;

-- All entitlements
CREATE VIEW IF NOT EXISTS v_entitlements AS
SELECT
    e.id,
    a.role_canonical as actor,
    e.entitled_to_text,
    e.condition_text,
    e.priority_order,
    e.bia_section
FROM entitlements e
JOIN actors a ON e.actor_id = a.id;

-- All constraints
CREATE VIEW IF NOT EXISTS v_constraints AS
SELECT
    c.id,
    c.subject_text,
    c.constraint_type,
    c.limit_value,
    c.limit_numeric,
    a.role_canonical as applies_to,
    c.bia_section
FROM constraints c
LEFT JOIN actors a ON c.applies_to_actor_id = a.id;

-- Comprehensive coverage statistics
CREATE VIEW IF NOT EXISTS v_relationship_coverage AS
SELECT 'Duty relationships' as type, COUNT(*) as count FROM duty_relationships_v2
UNION ALL SELECT 'Document requirements', COUNT(*) FROM document_requirements_v2
UNION ALL SELECT 'Content requirements', COUNT(*) FROM content_requirements
UNION ALL SELECT 'Legal effects', COUNT(*) FROM legal_effects
UNION ALL SELECT 'Presumptions', COUNT(*) FROM presumptions
UNION ALL SELECT 'Entitlements', COUNT(*) FROM entitlements
UNION ALL SELECT 'Constraints', COUNT(*) FROM constraints
UNION ALL SELECT 'Applicability rules', COUNT(*) FROM applicability_rules
UNION ALL SELECT 'Trigger relationships', COUNT(*) FROM trigger_relationships_v2
UNION ALL SELECT '═════════════════', NULL
UNION ALL SELECT 'TOTAL', COUNT(*) FROM (
    SELECT id FROM duty_relationships_v2
    UNION ALL SELECT id FROM document_requirements_v2
    UNION ALL SELECT id FROM content_requirements
    UNION ALL SELECT id FROM legal_effects
    UNION ALL SELECT id FROM presumptions
    UNION ALL SELECT id FROM entitlements
    UNION ALL SELECT id FROM constraints
    UNION ALL SELECT id FROM applicability_rules
    UNION ALL SELECT id FROM trigger_relationships_v2
);
