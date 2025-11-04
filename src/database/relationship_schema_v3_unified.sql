-- ============================================================================
-- Unified Relationship Schema v3
-- Handles ALL source types: BIA Statute, Study Materials, OSB Directives
-- ============================================================================

-- =================================================================
-- LAYER 1: LEGAL/DEONTIC RELATIONSHIPS (BIA, Directives)
-- =================================================================

-- Legal duties, permissions, prohibitions
CREATE TABLE IF NOT EXISTS deontic_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    actor_id INTEGER,
    procedure_id INTEGER,
    deadline_id INTEGER,
    consequence_id INTEGER,
    modal_verb TEXT NOT NULL,           -- shall, must, may, shall not
    modality_type TEXT NOT NULL,        -- mandatory, discretionary, prohibited
    condition_text TEXT,
    relationship_text TEXT NOT NULL,
    source_section TEXT NOT NULL,       -- BIA section or directive section
    source_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (actor_id) REFERENCES actors(id),
    FOREIGN KEY (procedure_id) REFERENCES procedures(id),
    FOREIGN KEY (deadline_id) REFERENCES deadlines(id),
    FOREIGN KEY (consequence_id) REFERENCES consequences(id),
    FOREIGN KEY (source_id) REFERENCES source_documents(id)
);

-- Legal effects (void, valid, binding)
CREATE TABLE IF NOT EXISTS legal_effects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_description TEXT NOT NULL,
    effect_type TEXT NOT NULL,          -- void, voidable, valid, binding, stayed
    condition_text TEXT NOT NULL,
    void_against_actor_id INTEGER,
    benefits_actor_id INTEGER,
    is_rebuttable BOOLEAN DEFAULT FALSE,
    source_section TEXT NOT NULL,
    source_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (void_against_actor_id) REFERENCES actors(id),
    FOREIGN KEY (benefits_actor_id) REFERENCES actors(id),
    FOREIGN KEY (source_id) REFERENCES source_documents(id)
);

-- Entitlements and rights
CREATE TABLE IF NOT EXISTS entitlements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    actor_id INTEGER NOT NULL,
    entitled_to_text TEXT NOT NULL,
    condition_text TEXT,
    priority_order INTEGER,
    source_section TEXT NOT NULL,
    source_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (actor_id) REFERENCES actors(id),
    FOREIGN KEY (source_id) REFERENCES source_documents(id)
);

-- Constraints and limits
CREATE TABLE IF NOT EXISTS constraints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_text TEXT NOT NULL,
    constraint_type TEXT NOT NULL,      -- maximum, minimum, fixed, not_exceed
    limit_value TEXT NOT NULL,
    limit_numeric REAL,
    limit_unit TEXT,
    applies_to_actor_id INTEGER,
    source_section TEXT NOT NULL,
    source_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (applies_to_actor_id) REFERENCES actors(id),
    FOREIGN KEY (source_id) REFERENCES source_documents(id)
);

-- Document/content requirements
CREATE TABLE IF NOT EXISTS document_requirements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    procedure_id INTEGER NOT NULL,
    document_id INTEGER NOT NULL,
    is_mandatory BOOLEAN DEFAULT TRUE,
    filing_context TEXT,
    source_section TEXT NOT NULL,
    source_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (procedure_id) REFERENCES procedures(id),
    FOREIGN KEY (document_id) REFERENCES documents(id),
    FOREIGN KEY (source_id) REFERENCES source_documents(id)
);

-- =================================================================
-- LAYER 2: EDUCATIONAL/WORKFLOW RELATIONSHIPS (Study Materials)
-- =================================================================

-- Sequential workflow steps
CREATE TABLE IF NOT EXISTS workflow_sequences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Current step
    step_procedure_id INTEGER NOT NULL,
    step_number TEXT,                   -- "6.2", "6.3", etc.
    step_title TEXT,

    -- Next step
    next_step_procedure_id INTEGER,

    -- Sequence metadata
    sequence_order INTEGER,             -- 1, 2, 3, 4...
    chapter_context TEXT,               -- "6 PREPARE DOCUMENTS FOR OSB"
    is_mandatory_sequence BOOLEAN DEFAULT TRUE,  -- Must follow order?
    can_be_parallel BOOLEAN DEFAULT FALSE,       -- Can do simultaneously?

    -- Source
    source_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (step_procedure_id) REFERENCES procedures(id),
    FOREIGN KEY (next_step_procedure_id) REFERENCES procedures(id),
    FOREIGN KEY (source_id) REFERENCES source_documents(id)
);

-- Hierarchical structure
CREATE TABLE IF NOT EXISTS content_hierarchy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Parent-child relationship
    parent_section_number TEXT,         -- "6", "6.2"
    parent_title TEXT,
    child_procedure_id INTEGER,         -- Procedure within this section
    child_section_number TEXT,          -- "6.2.1"

    -- Position in hierarchy
    depth_level INTEGER,                -- 0=chapter, 1=section, 2=subsection
    sibling_order INTEGER,              -- Position among siblings

    -- Source
    source_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (child_procedure_id) REFERENCES procedures(id),
    FOREIGN KEY (source_id) REFERENCES source_documents(id)
);

-- Practical procedures and best practices
CREATE TABLE IF NOT EXISTS practical_guidance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    procedure_id INTEGER NOT NULL,
    guidance_text TEXT NOT NULL,
    guidance_type TEXT,                 -- 'best_practice', 'tip', 'warning', 'example'

    -- Related legal requirement (if any)
    implements_bia_section TEXT,        -- Which BIA section this helps comply with
    relates_to_duty_id INTEGER,         -- Link to deontic_relationships

    -- Source
    source_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (procedure_id) REFERENCES procedures(id),
    FOREIGN KEY (relates_to_duty_id) REFERENCES deontic_relationships(id),
    FOREIGN KEY (source_id) REFERENCES source_documents(id)
);

-- =================================================================
-- LAYER 3: CROSS-SOURCE INTEGRATION
-- =================================================================

-- Links between different sources
CREATE TABLE IF NOT EXISTS cross_source_references (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Source (e.g., study material)
    from_source_id INTEGER NOT NULL,
    from_entity_id INTEGER,
    from_entity_type TEXT,              -- 'procedure', 'concept', 'actor'
    from_section TEXT,                  -- Study material section

    -- Target (e.g., BIA)
    to_source_id INTEGER NOT NULL,
    to_bia_section TEXT,
    to_entity_id INTEGER,
    to_entity_type TEXT,

    -- Relationship nature
    reference_type TEXT NOT NULL,       -- 'implements', 'explains', 'cites', 'governed_by', 'example_of'
    reference_context TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (from_source_id) REFERENCES source_documents(id),
    FOREIGN KEY (to_source_id) REFERENCES source_documents(id)
);

-- Educational elaborations (study materials explaining BIA concepts)
CREATE TABLE IF NOT EXISTS educational_elaborations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- What's being explained
    explains_bia_section TEXT,
    explains_concept_id INTEGER,

    -- The explanation
    study_material_section TEXT,
    study_material_procedure_id INTEGER,
    elaboration_type TEXT,              -- 'example', 'clarification', 'workflow', 'case_study'
    elaboration_text TEXT,

    -- Source
    source_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (explains_concept_id) REFERENCES concepts(id),
    FOREIGN KEY (study_material_procedure_id) REFERENCES procedures(id),
    FOREIGN KEY (source_id) REFERENCES source_documents(id)
);

-- =================================================================
-- INDEXES FOR PERFORMANCE
-- =================================================================

-- Deontic relationships
CREATE INDEX IF NOT EXISTS idx_deontic_actor ON deontic_relationships(actor_id);
CREATE INDEX IF NOT EXISTS idx_deontic_section ON deontic_relationships(source_section);
CREATE INDEX IF NOT EXISTS idx_deontic_modal ON deontic_relationships(modal_verb);
CREATE INDEX IF NOT EXISTS idx_deontic_source ON deontic_relationships(source_id);

-- Workflow sequences
CREATE INDEX IF NOT EXISTS idx_workflow_step ON workflow_sequences(step_procedure_id);
CREATE INDEX IF NOT EXISTS idx_workflow_next ON workflow_sequences(next_step_procedure_id);
CREATE INDEX IF NOT EXISTS idx_workflow_chapter ON workflow_sequences(chapter_context);
CREATE INDEX IF NOT EXISTS idx_workflow_order ON workflow_sequences(sequence_order);

-- Hierarchy
CREATE INDEX IF NOT EXISTS idx_hierarchy_parent ON content_hierarchy(parent_section_number);
CREATE INDEX IF NOT EXISTS idx_hierarchy_child ON content_hierarchy(child_procedure_id);
CREATE INDEX IF NOT EXISTS idx_hierarchy_depth ON content_hierarchy(depth_level);

-- Cross-source references
CREATE INDEX IF NOT EXISTS idx_xref_from ON cross_source_references(from_source_id, from_entity_type);
CREATE INDEX IF NOT EXISTS idx_xref_to ON cross_source_references(to_source_id, to_bia_section);
CREATE INDEX IF NOT EXISTS idx_xref_type ON cross_source_references(reference_type);

-- =================================================================
-- COMPREHENSIVE VIEWS (Cross-Source Queries)
-- =================================================================

-- All deontic duties (across BIA + directives)
CREATE VIEW IF NOT EXISTS v_all_duties AS
SELECT
    dr.id,
    a.role_canonical as actor,
    p.extraction_text as procedure,
    d.timeframe as deadline,
    c.outcome as consequence,
    dr.modal_verb,
    dr.modality_type,
    dr.source_section,
    sd.source_name,
    dr.relationship_text
FROM deontic_relationships dr
LEFT JOIN actors a ON dr.actor_id = a.id
LEFT JOIN procedures p ON dr.procedure_id = p.id
LEFT JOIN deadlines d ON dr.deadline_id = d.id
LEFT JOIN consequences c ON dr.consequence_id = c.id
JOIN source_documents sd ON dr.source_id = sd.id;

-- Complete workflows with sequence
CREATE VIEW IF NOT EXISTS v_workflows AS
SELECT
    ws.chapter_context,
    ws.step_number,
    ws.step_title,
    p1.extraction_text as current_step,
    p2.extraction_text as next_step,
    ws.sequence_order,
    sd.source_name
FROM workflow_sequences ws
LEFT JOIN procedures p1 ON ws.step_procedure_id = p1.id
LEFT JOIN procedures p2 ON ws.next_step_procedure_id = p2.id
JOIN source_documents sd ON ws.source_id = sd.id
ORDER BY ws.chapter_context, ws.sequence_order;

-- BIA sections with study material explanations
CREATE VIEW IF NOT EXISTS v_bia_with_explanations AS
SELECT
    ee.explains_bia_section,
    bs.section_title as bia_title,
    ee.elaboration_type,
    ee.study_material_section,
    ee.elaboration_text,
    p.extraction_text as study_procedure
FROM educational_elaborations ee
LEFT JOIN bia_sections bs ON ee.explains_bia_section = bs.section_number
LEFT JOIN procedures p ON ee.study_material_procedure_id = p.id
ORDER BY ee.explains_bia_section;

-- Cross-source relationship map
CREATE VIEW IF NOT EXISTS v_cross_source_map AS
SELECT
    sd1.source_name as from_source,
    csr.from_section,
    csr.reference_type,
    sd2.source_name as to_source,
    csr.to_bia_section,
    csr.reference_context
FROM cross_source_references csr
JOIN source_documents sd1 ON csr.from_source_id = sd1.id
JOIN source_documents sd2 ON csr.to_source_id = sd2.id;

-- Coverage statistics
CREATE VIEW IF NOT EXISTS v_comprehensive_coverage AS
SELECT 'Deontic (BIA/Directives)' as category, COUNT(*) as count FROM deontic_relationships
UNION ALL SELECT 'Legal Effects', COUNT(*) FROM legal_effects
UNION ALL SELECT 'Entitlements', COUNT(*) FROM entitlements
UNION ALL SELECT 'Constraints', COUNT(*) FROM constraints
UNION ALL SELECT 'Document Requirements', COUNT(*) FROM document_requirements
UNION ALL SELECT '─ Legal Total ─', SUM(cnt) FROM (
    SELECT COUNT(*) as cnt FROM deontic_relationships
    UNION ALL SELECT COUNT(*) FROM legal_effects
    UNION ALL SELECT COUNT(*) FROM entitlements
    UNION ALL SELECT COUNT(*) FROM constraints
    UNION ALL SELECT COUNT(*) FROM document_requirements
)
UNION ALL SELECT 'Workflow Sequences', COUNT(*) FROM workflow_sequences
UNION ALL SELECT 'Content Hierarchy', COUNT(*) FROM content_hierarchy
UNION ALL SELECT 'Practical Guidance', COUNT(*) FROM practical_guidance
UNION ALL SELECT '─ Educational Total ─', SUM(cnt) FROM (
    SELECT COUNT(*) as cnt FROM workflow_sequences
    UNION ALL SELECT COUNT(*) FROM content_hierarchy
    UNION ALL SELECT COUNT(*) FROM practical_guidance
)
UNION ALL SELECT 'Cross-Source References', COUNT(*) FROM cross_source_references
UNION ALL SELECT 'Educational Elaborations', COUNT(*) FROM educational_elaborations
UNION ALL SELECT '═════════════════', NULL
UNION ALL SELECT 'GRAND TOTAL', SUM(cnt) FROM (
    SELECT COUNT(*) as cnt FROM deontic_relationships
    UNION ALL SELECT COUNT(*) FROM legal_effects
    UNION ALL SELECT COUNT(*) FROM entitlements
    UNION ALL SELECT COUNT(*) FROM constraints
    UNION ALL SELECT COUNT(*) FROM document_requirements
    UNION ALL SELECT COUNT(*) FROM workflow_sequences
    UNION ALL SELECT COUNT(*) FROM content_hierarchy
    UNION ALL SELECT COUNT(*) FROM practical_guidance
    UNION ALL SELECT COUNT(*) FROM cross_source_references
    UNION ALL SELECT COUNT(*) FROM educational_elaborations
);
