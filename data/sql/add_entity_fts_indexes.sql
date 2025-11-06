-- Add FTS5 indexes to atomic entity tables for full-text search
-- This enables searching study material entities (8,376 entities)

-- 1. Concepts FTS
CREATE VIRTUAL TABLE IF NOT EXISTS concepts_fts USING fts5(
    term,
    definition,
    extraction_text,
    section_context,
    content=concepts,
    content_rowid=id
);

-- Populate concepts FTS
INSERT INTO concepts_fts(rowid, term, definition, extraction_text, section_context)
SELECT id, term, definition, extraction_text, section_context FROM concepts;

-- 2. Actors FTS
CREATE VIRTUAL TABLE IF NOT EXISTS actors_fts USING fts5(
    role_raw,
    role_canonical,
    extraction_text,
    section_context,
    content=actors,
    content_rowid=id
);

-- Populate actors FTS
INSERT INTO actors_fts(rowid, role_raw, role_canonical, extraction_text, section_context)
SELECT id, role_raw, role_canonical, extraction_text, section_context FROM actors;

-- 3. Deadlines FTS
CREATE VIRTUAL TABLE IF NOT EXISTS deadlines_fts USING fts5(
    extraction_text,
    section_context,
    content=deadlines,
    content_rowid=id
);

-- Populate deadlines FTS
INSERT INTO deadlines_fts(rowid, extraction_text, section_context)
SELECT id, extraction_text, section_context FROM deadlines;

-- 4. Documents FTS
CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
    extraction_text,
    section_context,
    content=documents,
    content_rowid=id
);

-- Populate documents FTS
INSERT INTO documents_fts(rowid, extraction_text, section_context)
SELECT id, extraction_text, section_context FROM documents;

-- 5. Procedures FTS
CREATE VIRTUAL TABLE IF NOT EXISTS procedures_fts USING fts5(
    extraction_text,
    section_context,
    content=procedures,
    content_rowid=id
);

-- Populate procedures FTS
INSERT INTO procedures_fts(rowid, extraction_text, section_context)
SELECT id, extraction_text, section_context FROM procedures;

-- 6. Statutory References FTS
CREATE VIRTUAL TABLE IF NOT EXISTS statutory_references_fts USING fts5(
    extraction_text,
    section_context,
    content=statutory_references,
    content_rowid=id
);

-- Populate statutory_references FTS
INSERT INTO statutory_references_fts(rowid, extraction_text, section_context)
SELECT id, extraction_text, section_context FROM statutory_references;

-- 7. Consequences FTS
CREATE VIRTUAL TABLE IF NOT EXISTS consequences_fts USING fts5(
    extraction_text,
    section_context,
    content=consequences,
    content_rowid=id
);

-- Populate consequences FTS
INSERT INTO consequences_fts(rowid, extraction_text, section_context)
SELECT id, extraction_text, section_context FROM consequences;

-- Create triggers to keep FTS indexes in sync

-- Concepts triggers
CREATE TRIGGER IF NOT EXISTS concepts_ai AFTER INSERT ON concepts BEGIN
  INSERT INTO concepts_fts(rowid, term, definition, extraction_text, section_context)
  VALUES (new.id, new.term, new.definition, new.extraction_text, new.section_context);
END;

CREATE TRIGGER IF NOT EXISTS concepts_ad AFTER DELETE ON concepts BEGIN
  DELETE FROM concepts_fts WHERE rowid = old.id;
END;

CREATE TRIGGER IF NOT EXISTS concepts_au AFTER UPDATE ON concepts BEGIN
  DELETE FROM concepts_fts WHERE rowid = old.id;
  INSERT INTO concepts_fts(rowid, term, definition, extraction_text, section_context)
  VALUES (new.id, new.term, new.definition, new.extraction_text, new.section_context);
END;

-- Actors triggers
CREATE TRIGGER IF NOT EXISTS actors_ai AFTER INSERT ON actors BEGIN
  INSERT INTO actors_fts(rowid, role_raw, role_canonical, extraction_text, section_context)
  VALUES (new.id, new.role_raw, new.role_canonical, new.extraction_text, new.section_context);
END;

CREATE TRIGGER IF NOT EXISTS actors_ad AFTER DELETE ON actors BEGIN
  DELETE FROM actors_fts WHERE rowid = old.id;
END;

CREATE TRIGGER IF NOT EXISTS actors_au AFTER UPDATE ON actors BEGIN
  DELETE FROM actors_fts WHERE rowid = old.id;
  INSERT INTO actors_fts(rowid, role_raw, role_canonical, extraction_text, section_context)
  VALUES (new.id, new.role_raw, new.role_canonical, new.extraction_text, new.section_context);
END;

-- (Similar triggers for other tables can be added as needed)
