-- ============================================================================
-- Relationship Schema for Insolvency Knowledge Base
-- Session 3: Connecting entities into meaningful relationships
-- ============================================================================

-- 1. DUTY RELATIONSHIPS
-- Links: Actor → Procedure → Deadline → Consequence
-- Captures: "Trustee shall file cash flow within 10 days or deemed assignment"
CREATE TABLE IF NOT EXISTS duty_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Entity foreign keys (all nullable - not all duties have all components)
    actor_id INTEGER,
    procedure_id INTEGER,
    deadline_id INTEGER,
    consequence_id INTEGER,

    -- Context and metadata
    bia_section TEXT,               -- Section where duty is defined (e.g., "50.4(1)")
    duty_type TEXT,                 -- 'mandatory', 'discretionary', 'prohibited'
    modal_verb TEXT,                -- 'shall', 'may', 'shall not', 'must'
    relationship_text TEXT,         -- Full sentence showing relationship

    -- Source tracking
    source_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Foreign key constraints
    FOREIGN KEY (actor_id) REFERENCES actors(id),
    FOREIGN KEY (procedure_id) REFERENCES procedures(id),
    FOREIGN KEY (deadline_id) REFERENCES deadlines(id),
    FOREIGN KEY (consequence_id) REFERENCES consequences(id),
    FOREIGN KEY (source_id) REFERENCES source_documents(id)
);

-- 2. DOCUMENT REQUIREMENTS
-- Links: Procedure → Document
-- Captures: "Filing proposal requires Form 31 and cash flow statement"
CREATE TABLE IF NOT EXISTS document_requirements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Core relationship
    procedure_id INTEGER NOT NULL,
    document_id INTEGER NOT NULL,

    -- Metadata
    is_mandatory BOOLEAN DEFAULT TRUE,  -- Required vs optional
    filing_context TEXT,                -- When/why document is needed
    bia_section TEXT,                   -- Governing section

    -- Source tracking
    source_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Foreign key constraints
    FOREIGN KEY (procedure_id) REFERENCES procedures(id),
    FOREIGN KEY (document_id) REFERENCES documents(id),
    FOREIGN KEY (source_id) REFERENCES source_documents(id)
);

-- 3. TRIGGER RELATIONSHIPS
-- Links: Condition/Event → Consequence
-- Captures: "Failure to file proposal triggers deemed assignment"
CREATE TABLE IF NOT EXISTS trigger_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Trigger source (what causes the consequence)
    trigger_entity_id INTEGER,
    trigger_entity_type TEXT,           -- 'procedure', 'deadline', 'event', 'condition'
    trigger_condition TEXT,             -- Description of triggering condition

    -- Result
    consequence_id INTEGER NOT NULL,

    -- Context
    bia_section TEXT,

    -- Source tracking
    source_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Foreign key constraints
    FOREIGN KEY (consequence_id) REFERENCES consequences(id),
    FOREIGN KEY (source_id) REFERENCES source_documents(id)
);

-- ============================================================================
-- INDEXES for Query Performance
-- ============================================================================

-- Duty relationships indexes
CREATE INDEX IF NOT EXISTS idx_duty_actor ON duty_relationships(actor_id);
CREATE INDEX IF NOT EXISTS idx_duty_procedure ON duty_relationships(procedure_id);
CREATE INDEX IF NOT EXISTS idx_duty_deadline ON duty_relationships(deadline_id);
CREATE INDEX IF NOT EXISTS idx_duty_consequence ON duty_relationships(consequence_id);
CREATE INDEX IF NOT EXISTS idx_duty_section ON duty_relationships(bia_section);
CREATE INDEX IF NOT EXISTS idx_duty_type ON duty_relationships(duty_type);

-- Document requirements indexes
CREATE INDEX IF NOT EXISTS idx_doc_req_procedure ON document_requirements(procedure_id);
CREATE INDEX IF NOT EXISTS idx_doc_req_document ON document_requirements(document_id);
CREATE INDEX IF NOT EXISTS idx_doc_req_mandatory ON document_requirements(is_mandatory);
CREATE INDEX IF NOT EXISTS idx_doc_req_section ON document_requirements(bia_section);

-- Trigger relationships indexes
CREATE INDEX IF NOT EXISTS idx_trigger_entity ON trigger_relationships(trigger_entity_id, trigger_entity_type);
CREATE INDEX IF NOT EXISTS idx_trigger_consequence ON trigger_relationships(consequence_id);
CREATE INDEX IF NOT EXISTS idx_trigger_section ON trigger_relationships(bia_section);

-- ============================================================================
-- VIEWS for Easy Querying
-- ============================================================================

-- Complete duty view - joins all entities
CREATE VIEW IF NOT EXISTS v_complete_duties AS
SELECT
    dr.id as duty_id,
    a.role_canonical as actor,
    p.extraction_text as procedure,
    d.timeframe as deadline,
    c.outcome as consequence,
    dr.duty_type,
    dr.modal_verb,
    dr.bia_section,
    dr.relationship_text,
    sd.source_name,
    dr.created_at
FROM duty_relationships dr
LEFT JOIN actors a ON dr.actor_id = a.id
LEFT JOIN procedures p ON dr.procedure_id = p.id
LEFT JOIN deadlines d ON dr.deadline_id = d.id
LEFT JOIN consequences c ON dr.consequence_id = c.id
LEFT JOIN source_documents sd ON dr.source_id = sd.id;

-- Document requirements view
CREATE VIEW IF NOT EXISTS v_document_requirements AS
SELECT
    dr.id as req_id,
    p.extraction_text as procedure,
    d.document_name_canonical as document,
    dr.is_mandatory,
    dr.filing_context,
    dr.bia_section,
    sd.source_name
FROM document_requirements dr
JOIN procedures p ON dr.procedure_id = p.id
JOIN documents d ON dr.document_id = d.id
LEFT JOIN source_documents sd ON dr.source_id = sd.id;

-- Trigger relationships view
CREATE VIEW IF NOT EXISTS v_trigger_consequences AS
SELECT
    tr.id as trigger_id,
    tr.trigger_entity_type,
    tr.trigger_condition,
    c.outcome as consequence,
    tr.bia_section,
    sd.source_name
FROM trigger_relationships tr
JOIN consequences c ON tr.consequence_id = c.id
LEFT JOIN source_documents sd ON tr.source_id = sd.id;

-- ============================================================================
-- RELATIONSHIP STATISTICS VIEW
-- ============================================================================

CREATE VIEW IF NOT EXISTS v_relationship_stats AS
SELECT
    'duty_relationships' as table_name,
    COUNT(*) as total_count,
    COUNT(actor_id) as with_actor,
    COUNT(procedure_id) as with_procedure,
    COUNT(deadline_id) as with_deadline,
    COUNT(consequence_id) as with_consequence
FROM duty_relationships
UNION ALL
SELECT
    'document_requirements' as table_name,
    COUNT(*) as total_count,
    COUNT(procedure_id) as with_procedure,
    COUNT(document_id) as with_document,
    SUM(CASE WHEN is_mandatory THEN 1 ELSE 0 END) as mandatory,
    NULL as with_consequence
FROM document_requirements
UNION ALL
SELECT
    'trigger_relationships' as table_name,
    COUNT(*) as total_count,
    COUNT(trigger_entity_id) as with_trigger,
    COUNT(consequence_id) as with_consequence,
    NULL as mandatory,
    NULL as with_consequence_2
FROM trigger_relationships;

-- ============================================================================
-- RELATIONSHIP VALIDATION QUERIES
-- ============================================================================

-- Check for orphaned relationships (referencing non-existent entities)
-- These queries should return 0 rows for a healthy database

CREATE VIEW IF NOT EXISTS v_orphaned_duty_relationships AS
SELECT id, 'actor' as missing_entity, actor_id as entity_id
FROM duty_relationships
WHERE actor_id IS NOT NULL AND actor_id NOT IN (SELECT id FROM actors)
UNION ALL
SELECT id, 'procedure', procedure_id
FROM duty_relationships
WHERE procedure_id IS NOT NULL AND procedure_id NOT IN (SELECT id FROM procedures)
UNION ALL
SELECT id, 'deadline', deadline_id
FROM duty_relationships
WHERE deadline_id IS NOT NULL AND deadline_id NOT IN (SELECT id FROM deadlines)
UNION ALL
SELECT id, 'consequence', consequence_id
FROM duty_relationships
WHERE consequence_id IS NOT NULL AND consequence_id NOT IN (SELECT id FROM consequences);

-- ============================================================================
-- USEFUL QUERY EXAMPLES (as comments for reference)
-- ============================================================================

/*
-- Q1: What are all trustee duties with deadlines?
SELECT actor, procedure, deadline, consequence, bia_section
FROM v_complete_duties
WHERE actor = 'Trustee'
  AND deadline IS NOT NULL
ORDER BY bia_section;

-- Q2: What triggers deemed assignment?
SELECT trigger_condition, consequence, bia_section
FROM v_trigger_consequences
WHERE consequence LIKE '%deemed assignment%';

-- Q3: What documents are required for proposals?
SELECT procedure, document, is_mandatory, filing_context
FROM v_document_requirements
WHERE procedure LIKE '%proposal%'
  AND is_mandatory = TRUE;

-- Q4: All duties in Section 50.4 (NOI)
SELECT actor, procedure, deadline, consequence, modal_verb
FROM v_complete_duties
WHERE bia_section LIKE '50.4%'
ORDER BY deadline;

-- Q5: Count duties by actor
SELECT actor, COUNT(*) as duty_count
FROM v_complete_duties
WHERE actor IS NOT NULL
GROUP BY actor
ORDER BY duty_count DESC;

-- Q6: Find all mandatory actions (shall/must)
SELECT actor, procedure, deadline, bia_section
FROM v_complete_duties
WHERE modal_verb IN ('shall', 'must')
  AND actor IS NOT NULL;
*/
