# Relationship Extraction System - Design v2 (Comprehensive)

## Design Principles

1. **Completeness:** Capture all types of legal relationships, not just duties
2. **Efficiency:** Minimize API calls through batching and pre-validation
3. **Resilience:** Handle failures gracefully with retry and checkpointing
4. **Accuracy:** Extract semantic relationships, not sentence fragments

---

## Part 1: Relationship Type Taxonomy

### Empirical Analysis (from 847 extracted relationships)

| Category | Count | % | Captured? |
|----------|-------|---|-----------|
| **Obligations** (shall/must) | 362 | 43% | ✅ duty_relationships |
| **Permissions** (may) | 285 | 34% | ✅ duty_relationships |
| **Prohibitions** (shall not) | 80 | 9% | ✅ duty_relationships |
| **Content Items** (NULL modal) | 87 | 10% | ❌ Miscategorized as duties |
| **Other Patterns** | 33 | 4% | ⚠️ Mixed |

**Coverage:** 727/847 = 86% properly categorized

### Additional Patterns Found (Not Yet Extracted)

Based on systematic BIA review:
- **Legal Effects** (void/valid): Est. 50-100 statements (Sections 95-101)
- **Presumptions** (deemed): Est. 30-50 statements
- **Entitlements** (entitled to): Est. 20-40 statements
- **Constraints** (limits): Est. 30-50 statements
- **Applicability Rules**: Est. 10-20 statements

**Total estimated relationships in BIA: ~1,200-1,500**

---

## Part 2: Comprehensive Schema Design

### Relationship Tables (9 types)

**Tier 1: Actions (86% of content)**
1. `duty_relationships_v2` - SHALL/MAY/MUST actions
2. `document_requirements_v2` - Required documents

**Tier 2: Content**
3. `content_requirements` - List items in documents/procedures

**Tier 3: Legal Effects**
4. `legal_effects` - Void/valid/binding statuses
5. `presumptions` - Deemed statuses

**Tier 4: Rights & Limits**
6. `entitlements` - Rights to benefits
7. `constraints` - Maximum/minimum limits

**Tier 5: Meta-Legal**
8. `applicability_rules` - When sections apply
9. `trigger_relationships_v2` - Conditional consequences

### Key Design Decisions

**Decision 1: Typed Tables vs Triple Store**
✅ **Choice:** Typed tables (hybrid approach)

**Rationale:**
- 86% of content fits cleanly into duty/document patterns
- Clear semantics enable intuitive queries
- Can add generic fallback table later if needed

**Decision 2: How to Handle List Items**
❌ **Current:** Extract each (a), (b), (c) as separate relationship
✅ **Corrected:** One parent relationship + `content_requirements` table for items

**Example:**
```sql
-- Wrong (current):
duty_relationships: {modal: NULL, text: "(a) intention to make proposal"}
duty_relationships: {modal: NULL, text: "(b) trustee name"}

-- Right (v2):
duty_relationships: {actor: "insolvent person", procedure: "file NOI", modal: "may"}
content_requirements: {parent_procedure: "file NOI", content: "(a) intention", item_ref: "(a)"}
content_requirements: {parent_procedure: "file NOI", content: "(b) trustee name", item_ref: "(b)"}
```

**Decision 3: Section Validation Before Extraction**
✅ **Add pre-flight check:**

```python
def is_section_extractable(section_number):
    entities = get_entities_in_section(section_number)

    # Count entity types present
    types = sum([
        len(entities['actors']) > 0,
        len(entities['procedures']) > 0,
        len(entities['deadlines']) > 0,
        len(entities['consequences']) > 0,
        len(entities['documents']) > 0
    ])

    # Need at least 2 entity types for meaningful relationships
    if types < 2:
        return False

    # Check section length (too short = definitions/admin)
    if len(section_text) < 100:
        return False

    return True
```

**Benefit:** Skip ~100-150 sections → save 300-450 API calls

---

## Part 3: Extraction Process Redesign

### Current Architecture (Inefficient)

```python
for section in all_sections:
    # 3 separate API calls per section
    duties = extract_duties(section)          # Call 1
    docs = extract_documents(section)         # Call 2
    triggers = extract_triggers(section)      # Call 3
```

**Problems:**
- 385 sections × 3 calls = 1,155 API calls
- Same section text sent 3 times
- Same entities fetched 3 times
- 3x rate limit exposure

### Redesigned Architecture (Efficient)

```python
class ComprehensiveRelationshipExtractor:
    """Extract ALL relationship types in a single pass."""

    def extract_all_from_section(self, section_number):
        """Single API call extracts all relationship types."""

        # Pre-flight validation
        if not self.is_section_extractable(section_number):
            return None  # Skip

        # Check if already processed
        if self.has_relationships(section_number):
            return None  # Skip (idempotent)

        # Get section data ONCE
        section_text, metadata = self.get_section_with_metadata(section_number)
        entities = self.get_entities_in_section(section_number)

        # Single comprehensive prompt
        prompt = self.build_comprehensive_prompt(
            section_text, metadata, entities
        )

        # One API call returns ALL types
        with retry_logic(max_attempts=3):
            result = self.model.generate_content(prompt)

        # Parse and store all types
        return {
            'duties': result['duties'],
            'documents': result['document_requirements'],
            'content': result['content_requirements'],
            'effects': result['legal_effects'],
            'presumptions': result['presumptions'],
            'entitlements': result['entitlements'],
            'constraints': result['constraints'],
            'applicability': result['applicability_rules']
        }
```

**Benefits:**
- 385 API calls (not 1,155) = **67% reduction**
- All relationship types captured together
- Better context for AI (sees all patterns at once)

---

## Part 4: Resilience Improvements

### 4.1 Retry with Exponential Backoff

```python
def extract_with_retry(section, max_retries=3):
    for attempt in range(max_retries):
        try:
            return extract_relationships(section)
        except RateLimitError as e:
            wait = min(2 ** attempt * 30, 300)  # Max 5 min
            print(f"Rate limited, retry in {wait}s...")
            time.sleep(wait)
        except APIError as e:
            if "quota" in str(e).lower():
                # Permanent quota exceeded
                raise
            # Transient error - retry
            time.sleep(30)

    # All retries failed - save for later
    self.save_failed_section(section)
    return None
```

### 4.2 Stateful Checkpointing

```python
class StatefulExtractor:
    def __init__(self):
        self.state = self.load_checkpoint()

    def process_all_sections(self):
        for section in all_sections:
            if section in self.state['completed']:
                continue  # Already done

            result = self.extract(section)

            # Checkpoint after each section
            self.state['completed'].add(section)
            self.save_checkpoint()

    def save_checkpoint(self):
        with open('.extraction_state.json', 'w') as f:
            json.dump({
                'completed_sections': list(self.state['completed']),
                'failed_sections': list(self.state['failed']),
                'timestamp': datetime.now().isoformat()
            }, f)
```

**Benefits:**
- Can stop/resume anytime
- Never lose progress
- Track failures separately

### 4.3 Priority-Based Processing

```python
# Process in order of exam importance
priority_tiers = [
    # Tier 1: Exam-critical (proposals, discharge, bankruptcy)
    (1, ['50.4', '69', '168.1', '170', '172', '49', '158']),

    # Tier 2: High-importance (meetings, claims, duties)
    (2, ['102', '136', '38', '95', '96', '25', '26']),

    # Tier 3: All other sections with 2+ entity types
    (3, [...]),

    # Skip: sections with <2 entity types
]
```

**Benefits:**
- Get exam value immediately
- Can stop early if time/quota limited
- Always process most important first

---

## Part 5: Extraction Prompt Redesign

### Current Prompt Issues

1. **Too narrow:** Only asks for one relationship type at a time
2. **No guidance on exclusions:** AI extracts list items as relationships
3. **No structure validation:** Accepts NULL modal verbs

### Redesigned Comprehensive Prompt

```python
prompt = f"""Analyze this BIA section and extract ALL legal relationships.

{section_header}: {section_title}
{section_text[:2500]}

Entities found in this section:
{entity_summary}

Extract the following relationship types:

1. DUTY RELATIONSHIPS - Actions parties must/may/shall (not) perform
   Pattern: Actor + Modal Verb + Action + [Deadline] + [Consequence]
   DO NOT extract list items like "(a)", "(b)" as separate duties

2. DOCUMENT REQUIREMENTS - Documents required for procedures
   Pattern: Procedure requires Document

3. CONTENT REQUIREMENTS - Items that must be IN documents
   Pattern: Document must contain Item(s)
   Extract list items HERE, not as duties

4. LEGAL EFFECTS - Void/valid statuses
   Pattern: Transaction is VOID/VALID if Condition

5. ENTITLEMENTS - Rights to benefits
   Pattern: Actor is ENTITLED TO Benefit if Condition

6. CONSTRAINTS - Limits and bounds
   Pattern: Subject shall NOT EXCEED Limit

Return JSON with 6 arrays:
{{
  "duties": [...],
  "document_requirements": [...],
  "content_requirements": [...],
  "legal_effects": [...],
  "entitlements": [...],
  "constraints": [...]
}}

IMPORTANT:
- Only extract complete statements, not subordinate clauses
- Each relationship must have a clear subject-predicate-object structure
- List items (a), (b), (c) go in content_requirements, NOT duties
"""
```

---

## Part 6: Implementation Plan

### Phase 1: Schema Migration (30 min)
1. Apply `relationship_schema_v2_comprehensive.sql`
2. Migrate existing v1 data to v2 tables
3. Validate migration (760 duties → 760 duties_v2)

### Phase 2: Extractor Refactoring (2 hours)
1. Create `ComprehensiveRelationshipExtractor` class
2. Single `extract_all_from_section()` method
3. Add pre-validation logic
4. Add retry/checkpoint logic
5. Comprehensive prompt design

### Phase 3: Re-extraction (1 hour with proper design)
1. Process priority sections first
2. Skip already-completed sections
3. Handle all 385 sections
4. Expected: ~1,200-1,500 total relationships

### Phase 4: Validation (30 min)
1. Verify no list items in duty_relationships
2. Verify Section 95 (legal effects) captured
3. Verify Section 144 (entitlements) captured
4. Run coverage analysis

---

## Expected Outcomes

**Current State (v1):**
- 847 relationships (86% duties, 14% misc)
- 3 relationship types
- 1,155 API calls made
- 80 sections missing

**After v2 Implementation:**
- ~1,200-1,500 relationships (comprehensive)
- 9 relationship types
- ~350-400 API calls (67% reduction)
- <10 sections missing (only pure admin/transitional)

**Query Capability Improvement:**
- v1: "What must trustee do?" ✅
- v2: "What transactions are void?" ✅
- v2: "What are payment limits?" ✅
- v2: "Who is entitled to surplus?" ✅

---

## Cost-Benefit Analysis

**Investment:**
- Schema design: 30 min ✅ (done)
- Refactoring: 2-3 hours
- Re-extraction: 1 hour
- **Total: ~4 hours**

**Benefit:**
- 95%+ BIA coverage (vs 80%)
- All legal statement types (vs 3 types)
- Proper semantic structure (vs miscategorized list items)
- Resilient extraction (vs fragile one-shot)
- **Long-term value:** Properly designed foundation

**For Exam:**
- Can defer implementation
- Current 80% covers exam-critical sections
- Text search still works for gaps

**Post-Exam:**
- Comprehensive system enables advanced features
- Foundation for AI query interface
- Basis for practice exam generator

---

## Recommendation

**Two paths:**

**Path A: Exam-Focused (use current state)**
- 847 relationships cover 80% of sections
- All exam-critical sections included
- Fill gaps with text search
- Time investment: 0 hours

**Path B: Properly Designed System (implement v2)**
- Comprehensive coverage
- All relationship types
- Resilient architecture
- Time investment: 4 hours

**My assessment:**
Given your exam timing, **Path A** makes sense NOW, implement **Path B** post-exam for long-term value.

But you wanted it designed properly - so I've created the complete v2 design. Your call on timing!
