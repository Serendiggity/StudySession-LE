-- Insolvency Knowledge Base Schema
-- Version 2.1 - Multi-source support with atomic entities
-- Created: 2025-11-01
-- Updated: 2025-11-02 - Added source tracking

-- ============================================================================
-- SOURCE TRACKING
-- ============================================================================

-- Source documents: Track which PDF each extraction came from
CREATE TABLE IF NOT EXISTS source_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_name TEXT NOT NULL UNIQUE,  -- "Study Material", "BIA Statute", etc.
    file_path TEXT NOT NULL,
    pages INTEGER,
    total_chars INTEGER,
    total_entities INTEGER,  -- Will be updated after loading
    extraction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT  -- Optional metadata
);

CREATE INDEX idx_source_name ON source_documents(source_name);

-- ============================================================================
-- CORE EXTRACTION TABLES
-- ============================================================================

-- Concepts: Terms and definitions
CREATE TABLE IF NOT EXISTS concepts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    extraction_text TEXT NOT NULL,
    term TEXT,
    definition TEXT,
    importance TEXT,  -- high, medium, low
    char_start INTEGER NOT NULL,
    char_end INTEGER NOT NULL,
    section_number TEXT,
    section_title TEXT,
    section_context TEXT,  -- Full hierarchical breadcrumb
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES source_documents(id)
);

CREATE INDEX idx_concepts_term ON concepts(term);
CREATE INDEX idx_concepts_section ON concepts(section_number);
CREATE INDEX idx_concepts_source ON concepts(source_id);

-- Deadlines: Temporal expressions
CREATE TABLE IF NOT EXISTS deadlines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    extraction_text TEXT NOT NULL,
    timeframe TEXT,  -- Nullable (some extractions may not have attributes)
    char_start INTEGER NOT NULL,
    char_end INTEGER NOT NULL,
    section_number TEXT,
    section_title TEXT,
    section_context TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES source_documents(id)
);

CREATE INDEX idx_deadlines_timeframe ON deadlines(timeframe);
CREATE INDEX idx_deadlines_section ON deadlines(section_number);
CREATE INDEX idx_deadlines_source ON deadlines(source_id);

-- Documents: Forms, statements, reports
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    extraction_text TEXT NOT NULL,
    document_name TEXT,  -- Nullable
    document_name_canonical TEXT,  -- Normalized name
    char_start INTEGER NOT NULL,
    char_end INTEGER NOT NULL,
    section_number TEXT,
    section_title TEXT,
    section_context TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES source_documents(id)
);

CREATE INDEX idx_documents_name ON documents(document_name);
CREATE INDEX idx_documents_canonical ON documents(document_name_canonical);
CREATE INDEX idx_documents_section ON documents(section_number);
CREATE INDEX idx_documents_source ON documents(source_id);

-- Actors: Roles and parties
CREATE TABLE IF NOT EXISTS actors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    extraction_text TEXT NOT NULL,
    role_raw TEXT,                  -- As extracted from PDF (nullable)
    role_canonical TEXT,            -- Normalized (Trustee, Creditor, etc.)
    char_start INTEGER NOT NULL,
    char_end INTEGER NOT NULL,
    section_number TEXT,
    section_title TEXT,
    section_context TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES source_documents(id)
);

CREATE INDEX idx_actors_raw ON actors(role_raw);
CREATE INDEX idx_actors_canonical ON actors(role_canonical);
CREATE INDEX idx_actors_section ON actors(section_number);
CREATE INDEX idx_actors_source ON actors(source_id);

-- Statutory References: Citations
CREATE TABLE IF NOT EXISTS statutory_references (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    extraction_text TEXT NOT NULL,
    reference TEXT,  -- Nullable
    act TEXT,                       -- Parsed: BIA, CCAA, etc.
    section TEXT,                   -- Parsed: s. 50.4, Form 33, etc.
    char_start INTEGER NOT NULL,
    char_end INTEGER NOT NULL,
    section_number TEXT,
    section_title TEXT,
    section_context TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES source_documents(id)
);

CREATE INDEX idx_statutory_ref ON statutory_references(reference);
CREATE INDEX idx_statutory_act ON statutory_references(act);
CREATE INDEX idx_statutory_section_pdf ON statutory_references(section_number);
CREATE INDEX idx_statutory_source ON statutory_references(source_id);

-- Procedures: Process steps
CREATE TABLE IF NOT EXISTS procedures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    extraction_text TEXT NOT NULL,
    step_name TEXT,
    action TEXT,
    step_order INTEGER,
    char_start INTEGER NOT NULL,
    char_end INTEGER NOT NULL,
    section_number TEXT,
    section_title TEXT,
    section_context TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES source_documents(id)
);

CREATE INDEX idx_procedures_step ON procedures(step_name);
CREATE INDEX idx_procedures_section ON procedures(section_number);
CREATE INDEX idx_procedures_source ON procedures(source_id);

-- Consequences: Outcomes and deemed events
CREATE TABLE IF NOT EXISTS consequences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    extraction_text TEXT NOT NULL,
    outcome TEXT,  -- Nullable
    char_start INTEGER NOT NULL,
    char_end INTEGER NOT NULL,
    section_number TEXT,
    section_title TEXT,
    section_context TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES source_documents(id)
);

CREATE INDEX idx_consequences_outcome ON consequences(outcome);
CREATE INDEX idx_consequences_section ON consequences(section_number);
CREATE INDEX idx_consequences_source ON consequences(source_id);

-- ============================================================================
-- SECTION METADATA TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS sections (
    section_number TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    full_title TEXT NOT NULL,
    char_start INTEGER NOT NULL,
    char_end INTEGER NOT NULL,
    depth INTEGER NOT NULL,
    parent_section TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sections_parent ON sections(parent_section);
CREATE INDEX idx_sections_depth ON sections(depth);

-- ============================================================================
-- NORMALIZATION TABLES
-- ============================================================================

-- Canonical actor mapping
CREATE TABLE IF NOT EXISTS actor_canonical_map (
    role_raw TEXT PRIMARY KEY,
    role_canonical TEXT NOT NULL,
    category TEXT  -- professional, participant, government, etc.
);

-- Canonical document mapping
CREATE TABLE IF NOT EXISTS document_canonical_map (
    document_raw TEXT PRIMARY KEY,
    document_canonical TEXT NOT NULL,
    document_type TEXT  -- form, statement, certificate, report
);

-- ============================================================================
-- SUMMARY VIEWS
-- ============================================================================

-- View: Unique canonical actors with total mentions (across all sources)
CREATE VIEW IF NOT EXISTS v_actors_summary AS
SELECT
    a.role_canonical,
    COUNT(*) as total_mentions,
    COUNT(DISTINCT a.section_number) as sections_mentioned,
    GROUP_CONCAT(DISTINCT a.role_raw) as raw_variations,
    GROUP_CONCAT(DISTINCT sd.source_name) as sources
FROM actors a
LEFT JOIN source_documents sd ON a.source_id = sd.id
GROUP BY a.role_canonical
ORDER BY total_mentions DESC;

-- View: Documents by type (across all sources)
CREATE VIEW IF NOT EXISTS v_documents_summary AS
SELECT
    d.document_name_canonical,
    COUNT(*) as total_mentions,
    COUNT(DISTINCT d.section_number) as sections_mentioned,
    GROUP_CONCAT(DISTINCT sd.source_name) as sources
FROM documents d
LEFT JOIN source_documents sd ON d.source_id = sd.id
GROUP BY d.document_name_canonical
ORDER BY total_mentions DESC;

-- View: Deadlines with full context
CREATE VIEW IF NOT EXISTS v_deadlines_enriched AS
SELECT
    d.id,
    d.extraction_text,
    d.timeframe,
    d.section_context,
    d.section_number,
    sd.source_name
FROM deadlines d
LEFT JOIN source_documents sd ON d.source_id = sd.id
ORDER BY sd.source_name, d.section_number;

-- ============================================================================
-- TIMELINE RECONSTRUCTION VIEWS
-- ============================================================================

-- View: Division I NOI Timeline (sections 4.3.6-4.3.11)
CREATE VIEW IF NOT EXISTS v_division_i_noi_timeline AS
SELECT
    'deadline' as entity_type,
    d.extraction_text,
    d.timeframe as detail,
    d.section_context
FROM deadlines d
WHERE d.section_number LIKE '4.3.%'
    AND CAST(SUBSTR(d.section_number, 5) AS INTEGER) BETWEEN 6 AND 11

UNION ALL

SELECT
    'document' as entity_type,
    doc.extraction_text,
    doc.document_name_canonical as detail,
    doc.section_context
FROM documents doc
WHERE doc.section_number LIKE '4.3.%'
    AND CAST(SUBSTR(doc.section_number, 5) AS INTEGER) BETWEEN 6 AND 11

UNION ALL

SELECT
    'actor' as entity_type,
    a.extraction_text,
    a.role_canonical as detail,
    a.section_context
FROM actors a
WHERE a.section_number LIKE '4.3.%'
    AND CAST(SUBSTR(a.section_number, 5) AS INTEGER) BETWEEN 6 AND 11;

-- ============================================================================
-- STATISTICS
-- ============================================================================

-- Overall extraction stats (all sources combined)
CREATE VIEW IF NOT EXISTS v_extraction_stats AS
SELECT
    'Concepts' as category,
    COUNT(*) as total,
    COUNT(DISTINCT section_number) as sections_covered
FROM concepts

UNION ALL

SELECT 'Deadlines', COUNT(*), COUNT(DISTINCT section_number) FROM deadlines
UNION ALL
SELECT 'Documents', COUNT(*), COUNT(DISTINCT section_number) FROM documents
UNION ALL
SELECT 'Actors', COUNT(*), COUNT(DISTINCT section_number) FROM actors
UNION ALL
SELECT 'Statutory Refs', COUNT(*), COUNT(DISTINCT section_number) FROM statutory_references
UNION ALL
SELECT 'Procedures', COUNT(*), COUNT(DISTINCT section_number) FROM procedures
UNION ALL
SELECT 'Consequences', COUNT(*), COUNT(DISTINCT section_number) FROM consequences;

-- Per-source extraction stats
CREATE VIEW IF NOT EXISTS v_extraction_stats_by_source AS
SELECT
    sd.source_name,
    'Concepts' as category,
    COUNT(*) as total,
    COUNT(DISTINCT c.section_number) as sections_covered
FROM concepts c
LEFT JOIN source_documents sd ON c.source_id = sd.id
GROUP BY sd.source_name

UNION ALL

SELECT sd.source_name, 'Deadlines', COUNT(*), COUNT(DISTINCT d.section_number)
FROM deadlines d
LEFT JOIN source_documents sd ON d.source_id = sd.id
GROUP BY sd.source_name

UNION ALL

SELECT sd.source_name, 'Documents', COUNT(*), COUNT(DISTINCT doc.section_number)
FROM documents doc
LEFT JOIN source_documents sd ON doc.source_id = sd.id
GROUP BY sd.source_name

UNION ALL

SELECT sd.source_name, 'Actors', COUNT(*), COUNT(DISTINCT a.section_number)
FROM actors a
LEFT JOIN source_documents sd ON a.source_id = sd.id
GROUP BY sd.source_name

UNION ALL

SELECT sd.source_name, 'Statutory Refs', COUNT(*), COUNT(DISTINCT sr.section_number)
FROM statutory_references sr
LEFT JOIN source_documents sd ON sr.source_id = sd.id
GROUP BY sd.source_name

UNION ALL

SELECT sd.source_name, 'Procedures', COUNT(*), COUNT(DISTINCT p.section_number)
FROM procedures p
LEFT JOIN source_documents sd ON p.source_id = sd.id
GROUP BY sd.source_name

UNION ALL

SELECT sd.source_name, 'Consequences', COUNT(*), COUNT(DISTINCT con.section_number)
FROM consequences con
LEFT JOIN source_documents sd ON con.source_id = sd.id
GROUP BY sd.source_name

ORDER BY source_name, category;

-- ============================================================================
-- BIA STATUTE STRUCTURAL TABLES
-- ============================================================================
-- Statute-specific structural extraction for complete provision text

-- BIA Parts (high-level organization)
CREATE TABLE IF NOT EXISTS bia_parts (
    part_number TEXT PRIMARY KEY,    -- "PART I", "PART II", etc.
    part_title TEXT NOT NULL,        -- "Administrative Officials", "Proposals"
    description TEXT,                -- Optional summary
    char_start INTEGER,
    char_end INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- BIA Sections (complete provisions with full text)
CREATE TABLE IF NOT EXISTS bia_sections (
    section_number TEXT PRIMARY KEY,  -- "2", "43", "50.4", "50.4(1)"
    part_number TEXT,                 -- PART I, PART II, etc.
    section_title TEXT,               -- "Definitions", "Application for bankruptcy order"
    full_text TEXT NOT NULL,          -- Complete section text (for AI querying)
    subsection_number TEXT,           -- "(1)", "(2)", etc. (if applicable)
    char_start INTEGER NOT NULL,
    char_end INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (part_number) REFERENCES bia_parts(part_number)
);

CREATE INDEX idx_bia_sections_part ON bia_sections(part_number);
CREATE INDEX idx_bia_sections_title ON bia_sections(section_title);

-- View: BIA sections with part context
CREATE VIEW IF NOT EXISTS v_bia_sections_enriched AS
SELECT
    s.section_number,
    s.section_title,
    s.full_text,
    p.part_number,
    p.part_title,
    s.subsection_number
FROM bia_sections s
LEFT JOIN bia_parts p ON s.part_number = p.part_number
ORDER BY s.section_number;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
