# Unified Relationship Architecture - Cross-Source Design

## Answer: Is the Same Structure Compatible with All Input Materials?

**Short Answer:** NO - but a unified design can handle all types.

---

## Source Material Analysis

### Source 1: BIA Statute
**Content Type:** Primary legislation
**Statement Types:**
- Deontic (shall/must/may): 95% of statements
- Legal effects (void/valid): ~50-100 statements
- Entitlements (entitled to): ~20-40 statements
- Constraints (not exceed): ~30-50 statements

**Linguistic Pattern:** Modal verbs + legal entities
**Example:** "Trustee SHALL file cash flow within 10 days OR deemed assignment"

**Relationship Nature:**
- Actor ↔ Duty ↔ Deadline ↔ Consequence
- Transaction ↔ Legal Effect ↔ Condition
- Actor ↔ Entitlement ↔ Benefit

---

### Source 2: Study Materials (Insolvency Administration Course)
**Content Type:** Educational synthesis
**Statement Types:**
- Sequential workflows: ~80% of statements
- BIA explanations: ~10%
- Practical guidance: ~5%
- Cross-references: ~5%

**Linguistic Pattern:** Imperative commands + workflow steps
**Example:** "6.2 Document Preparation → 6.3 Obtain assessment → 6.4 Prepare documents → 6.7 Submit to OSB"

**Relationship Nature:**
- Step A → PRECEDES → Step B
- Chapter → CONTAINS → Sections
- Study Step → IMPLEMENTS → BIA Section
- Study Content → EXPLAINS → BIA Concept

---

### Source 3: OSB Directives (Not yet processed)
**Content Type:** Regulatory guidance
**Probable Statement Types:**
- Procedural requirements (SHALL file Form X)
- Technical specifications (document must include Y)
- Best practices (recommended approach)

**Would Likely Match:** BIA pattern (deontic) + Study material pattern (workflows)

---

## Comparative Analysis

| Relationship Type | BIA | Study Materials | OSB Directives | Unified Schema Needed? |
|-------------------|-----|-----------------|----------------|------------------------|
| **Deontic (shall/must)** | ✅ 95% | ⚠️ 3% | ✅ Likely 70% | YES - `deontic_relationships` |
| **Legal Effects (void)** | ✅ Yes | ❌ No | ❌ No | YES - `legal_effects` |
| **Sequential Workflows** | ❌ No | ✅ 80% | ⚠️ Maybe | YES - `workflow_sequences` |
| **Hierarchical Structure** | ❌ No | ✅ Yes | ✅ Likely | YES - `content_hierarchy` |
| **Cross-References** | ⚠️ Rare | ✅ Common | ✅ Common | YES - `cross_source_references` |
| **Entitlements** | ✅ Yes | ❌ No | ❌ No | YES - `entitlements` |
| **Constraints** | ✅ Yes | ❌ No | ⚠️ Maybe | YES - `constraints` |

**Conclusion:** Each source type needs **different relationship tables**, but they can coexist in ONE unified schema.

---

## Three-Layer Architecture (v3 Unified)

### Layer 1: Legal/Deontic (BIA + Directives)
```
Tables:
- deontic_relationships  (shall/must/may actions)
- legal_effects          (void/valid status)
- entitlements           (rights to benefits)
- constraints            (limits/bounds)
- document_requirements  (required documents)

Primary Sources: BIA, OSB Directives
Query: "What must trustee do?"
```

### Layer 2: Educational/Workflow (Study Materials)
```
Tables:
- workflow_sequences     (step A → step B)
- content_hierarchy      (chapter → section → subsection)
- practical_guidance     (best practices, tips)

Primary Sources: Study Materials
Query: "What are the steps to file NOI?"
```

### Layer 3: Integration (Cross-Source Links)
```
Tables:
- cross_source_references    (study material → BIA section)
- educational_elaborations   (study material explains BIA concept)

Links: Study Materials ↔ BIA ↔ Directives
Query: "Show me study material workflow for BIA s. 50.4"
```

---

## Key Design Decisions

### Decision 1: Source-Specific Tables vs Universal Table

**❌ Rejected: Single universal "relationships" table**
```sql
-- Too generic
CREATE TABLE relationships (
    subject_id, predicate, object_id, metadata JSON
);
```
**Problem:** Loses semantic meaning, complex queries

**✅ Chosen: Typed tables per relationship category**
```sql
-- Clear semantics
deontic_relationships: actor → duty → deadline
workflow_sequences: step1 → precedes → step2
```
**Benefit:** Self-documenting, type-safe, intuitive queries

---

### Decision 2: How to Handle Source Differences

**❌ Rejected: Separate schemas per source**
```
bia_schema.sql (9 tables)
study_schema.sql (5 tables)
osb_schema.sql (7 tables)
```
**Problem:** Can't query across sources

**✅ Chosen: Unified schema with source_id discrimination**
```sql
-- All tables have source_id
deontic_relationships WHERE source_id = 1  -- Study materials
deontic_relationships WHERE source_id = 2  -- BIA
workflow_sequences WHERE source_id = 1     -- Study materials only
```
**Benefit:** Single database, can join across sources

---

### Decision 3: Relationship Granularity

**Wrong Granularity Examples (from v1):**
- List items (a), (b), (c) as separate duty relationships ❌
- Subordinate clauses as relationships ❌
- Definitions as duties ❌

**Correct Granularity:**
- One relationship = one semantic statement
- List items → `content_requirements` table (children of parent relationship)
- Sequential steps → `workflow_sequences` with explicit order

---

## Extraction Strategy Per Source

### BIA Extraction
```python
prompt = """Extract from BIA section:
1. Deontic relationships (shall/must/may)
2. Legal effects (void/valid)
3. Entitlements
4. Constraints
5. Document requirements

Return: {duties: [...], effects: [...], ...}
"""
```

### Study Material Extraction
```python
prompt = """Extract from study material chapter:
1. Workflow sequences (step order)
2. BIA cross-references (implements which section?)
3. Practical guidance (tips/warnings)
4. Content hierarchy (section structure)

Return: {workflows: [...], cross_refs: [...], ...}
"""
```

### OSB Directive Extraction
```python
prompt = """Extract from OSB directive:
1. Deontic relationships (SHALL/SHOULD requirements)
2. Document requirements (forms, formats)
3. BIA cross-references (implements BIA s. X)

Return: {duties: [...], docs: [...], ...}
"""
```

**Each source type gets an optimized extraction prompt!**

---

## Answer to Your Question

**"Is that same structure compatible with every input material?"**

### Direct Answer

**NO** - the v2 schema I designed is BIA-specific (deontic focus).

**BUT** - the v3 unified schema (just created) IS compatible with all sources:

| Source | Compatible Tables | Incompatible with v2 |
|--------|-------------------|----------------------|
| **BIA** | deontic_relationships, legal_effects, entitlements, constraints | ✅ v2 works |
| **Study Materials** | workflow_sequences, content_hierarchy, practical_guidance, cross_source_references | ❌ v2 missing these |
| **OSB Directives** | deontic_relationships, document_requirements, cross_source_references | ⚠️ Partial |

**Solution:** v3 unified schema has **10 relationship tables** (vs v2's 9):
- 5 for legal content (BIA/directives)
- 3 for educational content (study materials)
- 2 for cross-source integration

---

## Implementation Path

### Path A: Implement v3 Comprehensive (~6 hours)
1. Apply v3 unified schema
2. Refactor extractor for efficiency (single API call)
3. Add source-specific extraction logic
4. Extract BIA (385 sections)
5. Extract Study Materials (479 sections)
6. Extract cross-references

**Result:**
- ~1,500-2,000 total relationships
- All relationship types
- All sources integrated

---

### Path B: Incremental (Recommended)
1. **Now:** Commit current v1 state (847 BIA relationships)
2. **Post-exam:** Implement v3 unified schema
3. **Post-exam:** Re-extract all sources comprehensively

**Benefit:** No exam delay, but properly designed for future

---

## The System Design Answer

**Your schema must be source-aware:**

```python
class UnifiedRelationshipExtractor:
    def extract(self, section, source_id):
        source_type = self.get_source_type(source_id)

        if source_type == 'statute':  # BIA
            return self.extract_legal_relationships(section)
        elif source_type == 'educational':  # Study materials
            return self.extract_workflow_relationships(section)
        elif source_type == 'directive':  # OSB directives
            return self.extract_regulatory_relationships(section)
```

**Each source type needs its own extraction logic + relationship tables.**

**Want me to implement v3 unified now, or save the design for post-exam?**
