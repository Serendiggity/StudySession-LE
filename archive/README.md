# Archive - Historical Reference

This directory contains deprecated scripts and logs from the development process. **Kept for learning and reference, not for active use.**

---

## `/extraction_logs/` - Lang Extract Attempts

**What happened:** Multiple attempts to extract BIA statute entities using Lang Extract
- Various chunking strategies (200K, 100K)
- Different example sets (study material vs BIA-specific)
- Bilingual vs English-only filtering

**Outcome:** Entity extraction from large legal statutes proved unreliable (stalled repeatedly)

**Lesson learned:** Use structural extraction (regex parsing) for legal statutes, not semantic entity extraction

**Files:**
- `bia_extraction_english_only.log` - First major attempt
- `bia_conservative_*.log` - Chunked extraction attempts
- `bia_final3_extraction.log` - Final entity extraction attempt

---

## `/deprecated_scripts/` - Obsolete Extraction Scripts

**What's here:** Scripts that attempted various BIA extraction strategies

**Why deprecated:**
- `extract_bia_statute.py` - Full-document extraction (stalled)
- `extract_bia_chunked.py` - Chunked extraction (had bugs)
- `extract_bia_conservative.py` - Small chunks (too slow)
- `filter_bia_english_only.py` - Superseded by enhanced filter
- `monitor_extraction.py` - Progress monitor (no longer needed)

**Current approach:** Structural extraction via `src/utils/bia_structure_parser.py` (fast, reliable)

---

## Why Keep This?

**Learning:**
- Documents what didn't work
- Shows evolution of approach
- Educational value for understanding tool limitations

**Reference:**
- May contain useful code patterns
- Can be adapted for future sources
- Preserves institutional knowledge

**Don't use these scripts** - refer to `/tools/` for current, working tools.
