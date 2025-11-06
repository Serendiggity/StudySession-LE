# Phase 0 Research Prompt - Knowledge Extraction Architecture

**Purpose**: Conduct data-driven research to determine optimal architecture for universal knowledge extraction system

**Context**: We have a working insolvency knowledge base that uses a hybrid approach (entities + relationships). Before expanding to a universal multi-domain platform, we need to validate architectural decisions with empirical data.

**Your Mission**: Execute the three research questions below, collect data, analyze results, and provide clear recommendations.

---

## 🔬 Research Question 1: Entities vs Relationships vs Hybrid

### Background

**Current System**: Uses hybrid approach
- Stores entities separately (actors, procedures, deadlines)
- Links them via relationships table
- Preserves original text in `relationship_text` field

**Database Location**: `database/insolvency_knowledge.db`

**Question**: Is the hybrid approach optimal, or would entities-only or relationships-only be better?

---

### Research Methodology

#### Step 1: Understand Current Data Structure

```bash
# Connect to existing database
sqlite3 database/insolvency_knowledge.db

# Examine current schema
.schema duty_relationships
.schema actors
.schema procedures
.schema deadlines
.schema v_complete_duties

# Get statistics
SELECT COUNT(*) FROM duty_relationships;
SELECT COUNT(*) FROM actors;
SELECT COUNT(*) FROM procedures;
SELECT COUNT(*) FROM deadlines;
```

**Deliverable**: Summary of current data structure (tables, row counts, relationships)

---

#### Step 2: Extract Sample Data Using Three Approaches

**Test Subject**: BIA Section 50.4 (Notice of Intention - Division I Proposals)

**Why This Section?**
- Well-documented (10+ relationships)
- Mix of actors, procedures, deadlines, consequences
- Representative of system's capabilities

**Extract Data**:
```sql
-- Get all relationships for Section 50.4
SELECT
    relationship_text,
    bia_section,
    actor_id,
    procedure_id,
    deadline_id,
    consequence_id
FROM duty_relationships
WHERE bia_section LIKE '50.4%'
ORDER BY bia_section;

-- Get entities involved
SELECT DISTINCT a.role_canonical as actor, p.extraction_text as procedure
FROM duty_relationships dr
LEFT JOIN actors a ON dr.actor_id = a.id
LEFT JOIN procedures p ON dr.procedure_id = p.id
WHERE dr.bia_section LIKE '50.4%';
```

**Deliverable**: Dataset with 10+ relationships from Section 50.4

---

#### Step 3: Model Three Approaches

##### **Approach A: Entities Only**

Create a model where we store only atomic entities, no explicit relationships.

**Schema**:
```sql
CREATE TABLE entities_only_actors (
    id INTEGER PRIMARY KEY,
    role_canonical TEXT,
    extraction_text TEXT,
    bia_section TEXT
);

CREATE TABLE entities_only_procedures (
    id INTEGER PRIMARY KEY,
    step_name TEXT,
    action TEXT,
    extraction_text TEXT,
    bia_section TEXT
);

CREATE TABLE entities_only_deadlines (
    id INTEGER PRIMARY KEY,
    timeframe TEXT,
    trigger_event TEXT,
    bia_section TEXT
);
```

**Query Method**: Full-text search across all tables, user must infer connections

---

##### **Approach B: Relationships Only**

Create a model where we store only complete sentences with minimal metadata.

**Schema**:
```sql
CREATE TABLE relationships_only (
    id INTEGER PRIMARY KEY,
    relationship_text TEXT,  -- Full sentence
    bia_section TEXT,
    duty_type TEXT,
    modal_verb TEXT
);

-- FTS5 for full-text search
CREATE VIRTUAL TABLE relationships_fts USING fts5(
    relationship_text,
    bia_section,
    content=relationships_only
);
```

**Query Method**: Full-text search on relationship_text

---

##### **Approach C: Hybrid (Current)**

Current system with both entities and relationships.

**Schema**: Already exists in database

**Query Method**: JOIN entities via relationships, filter by entity properties

---

#### Step 4: Define Test Queries

Create 10 representative queries that users would ask:

```
Q1: "What must the insolvent person do within 10 days of filing NOI?"
Q2: "All duties in Section 50.4"
Q3: "What are the trustee's duties for NOI?"
Q4: "Find all mandatory duties (shall/must)"
Q5: "What happens if cash flow statement not filed?"
Q6: "All procedures with deadlines"
Q7: "What documents must be filed for NOI?"
Q8: "When must creditors be notified?"
Q9: "What are consequences of non-compliance in Section 50.4?"
Q10: "Compare deadlines in 50.4(1) vs 50.4(2)"
```

---

#### Step 5: Execute Queries Against Each Approach

For each test query (Q1-Q10), execute against all three approaches:

**Approach A (Entities Only)**:
```sql
-- Example for Q1
SELECT a.role_canonical, p.extraction_text, d.timeframe
FROM entities_only_actors a, entities_only_procedures p, entities_only_deadlines d
WHERE a.bia_section LIKE '50.4%'
  AND p.bia_section LIKE '50.4%'
  AND d.bia_section LIKE '50.4%'
  AND d.timeframe LIKE '%10 days%'
  AND a.role_canonical LIKE '%insolvent person%';
```

**Approach B (Relationships Only)**:
```sql
-- Example for Q1
SELECT relationship_text, bia_section
FROM relationships_only
WHERE relationship_text LIKE '%insolvent person%'
  AND relationship_text LIKE '%10 days%'
  AND bia_section LIKE '50.4%';
```

**Approach C (Hybrid)**:
```sql
-- Example for Q1
SELECT relationship_text, bia_section, actor, procedure, deadline
FROM v_complete_duties
WHERE actor LIKE '%insolvent person%'
  AND deadline LIKE '%10 days%'
  AND bia_section LIKE '50.4%';
```

---

#### Step 6: Measure Performance Metrics

For each query on each approach, measure:

##### **1. Query Speed**
```sql
-- Use EXPLAIN QUERY PLAN
EXPLAIN QUERY PLAN
SELECT ... (your query here);

-- Time the query
.timer on
SELECT ... (your query here);
```

**Record**: Execution time in milliseconds

---

##### **2. Result Accuracy**

Compare results to ground truth (manually verified correct answer).

**Scoring**:
- **Precision**: % of returned results that are correct
- **Recall**: % of correct results that were returned
- **F1 Score**: Harmonic mean of precision and recall

**Formula**:
```
Precision = True Positives / (True Positives + False Positives)
Recall = True Positives / (True Positives + False Negatives)
F1 = 2 * (Precision * Recall) / (Precision + Recall)
```

---

##### **3. Quote Preservation**

Can the approach return the original BIA text as a direct quote?

**Scoring**:
- **Yes** (1.0): Complete original sentence returned
- **Partial** (0.5): Parts of original sentence, but incomplete
- **No** (0.0): Cannot return direct quote

---

##### **4. Code Complexity**

Measure difficulty of writing queries.

**Metrics**:
- Lines of SQL required
- Number of JOINs
- Cognitive load (subjective: easy/medium/hard)

**Scoring**:
- Simple query (1-3 lines, no JOINs): 10
- Medium query (4-6 lines, 1-2 JOINs): 5
- Complex query (7+ lines, 3+ JOINs): 1

---

##### **5. Storage Requirements**

Measure database size for Section 50.4 data.

```sql
-- Check page count
SELECT page_count * page_size as size_bytes
FROM pragma_page_count(), pragma_page_size();

-- Or use system tools
du -h database/*.db
```

**Record**: Storage in KB for equivalent data

---

##### **6. Flexibility Score**

Can this approach adapt to a different domain (e.g., medical)?

**Subjective Assessment** (1-10):
- 10: Trivial to adapt (just change table/column names)
- 5: Moderate effort (restructure some queries)
- 1: Major rewrite required (fundamental assumptions broken)

---

#### Step 7: Create Results Matrix

Build a comparison table:

| Metric | Weight | Entities Only | Relationships Only | Hybrid | Winner |
|--------|--------|---------------|--------------------|---------| -------|
| **Avg Query Speed (ms)** | 20% | | | | |
| **Avg F1 Score** | 30% | | | | |
| **Quote Preservation** | 25% | | | | |
| **Code Simplicity** | 10% | | | | |
| **Storage Efficiency** | 5% | | | | |
| **Flexibility** | 10% | | | | |
| **WEIGHTED TOTAL** | 100% | | | | |

**Scoring Formula**:
```
Weighted Score = Σ(Metric Score × Weight)
```

Normalize all metrics to 0-10 scale before weighting.

---

#### Step 8: Analyze Results

**Questions to Answer**:
1. Which approach has highest weighted score?
2. Is the winner >20% better than alternatives? (Clear winner)
3. Are there scenarios where different approaches excel?
4. What are the trade-offs of each approach?

**Deliverable**:
- Completed results matrix
- Statistical analysis
- Qualitative observations

---

#### Step 9: Provide Recommendation

Based on data, recommend:

**Format**:
```markdown
## Recommendation: [Approach Name]

### Decision Rationale
- [Why this approach scored highest]
- [Key strengths]
- [Acceptable trade-offs]

### When to Use This Approach
- [Scenario 1]
- [Scenario 2]

### When to Use Alternatives
- [If X is priority, consider Y approach]

### Implementation Notes
- [Key considerations for building this]
- [Potential pitfalls to avoid]
```

---

## 🔬 Research Question 2: AI Schema Discovery Accuracy

### Background

**Goal**: Determine if AI can reliably suggest entity categories for unknown materials

**Success Threshold**: F1 Score >0.80 (80% accuracy)

---

### Research Methodology

#### Step 1: Gather Test Materials

Collect 3 diverse documents from different domains:

**Material 1: Medical (Radiology)**
- Document: Radiology textbook chapter or ACR guidelines
- Expert schema (ground truth):
  - conditions
  - imaging_methods
  - findings
  - diagnoses
  - contraindications

**Material 2: Technical (Software Engineering)**
- Document: API documentation or software architecture guide
- Expert schema (ground truth):
  - components
  - interfaces
  - operations
  - data_models
  - requirements

**Material 3: Legal (Contract Law)**
- Document: Contract law study guide
- Expert schema (ground truth):
  - parties
  - obligations
  - conditions
  - remedies
  - jurisdictions

**Deliverable**: 3 documents (5-10 pages each) + expert-defined schemas

---

#### Step 2: Design AI Analysis Prompt

Create a standardized prompt for AI to analyze materials:

```
You are a knowledge extraction expert. Your task is to analyze a document
and suggest entity categories that should be extracted.

DOCUMENT:
[Insert document text here - first 2000 words]

INSTRUCTIONS:
1. Read the document carefully
2. Identify recurring patterns and structures
3. Suggest 4-7 entity categories that capture the key information
4. For each category, provide:
   - Name (singular, lowercase, e.g., "condition")
   - 2-3 key attributes to extract
   - Brief description
   - 3 example instances from the document

OUTPUT FORMAT:
{
  "categories": [
    {
      "name": "category_name",
      "attributes": ["attr1", "attr2"],
      "description": "What this category represents",
      "examples": ["example 1", "example 2", "example 3"]
    }
  ]
}
```

---

#### Step 3: Execute AI Analysis

For each test material:
1. Run the AI analysis prompt
2. Record AI-suggested schema
3. Compare to expert schema

**Deliverable**: 3 AI-suggested schemas (JSON format)

---

#### Step 4: Calculate Accuracy Metrics

Compare AI suggestions to expert ground truth:

##### **Category-Level Metrics**

```python
# Precision: % of AI categories that are useful
precision = correct_ai_categories / total_ai_categories

# Recall: % of expert categories that AI found
recall = correct_ai_categories / total_expert_categories

# F1 Score
f1 = 2 * (precision * recall) / (precision + recall)
```

**Matching Rules**:
- Exact match: Same name (e.g., "condition" = "condition")
- Semantic match: Different name, same concept (e.g., "imaging_method" = "diagnostic_technique")
- Near miss: Overlapping but not equivalent (e.g., "treatment" ≠ "medication" but related)

---

##### **Attribute-Level Metrics**

For categories that matched, compare attributes:

```python
# Attribute accuracy
attr_precision = correct_attributes / total_ai_attributes
attr_recall = correct_attributes / total_expert_attributes
```

---

##### **Example Quality**

Human evaluation of AI-provided examples:

**Scoring**:
- Good example (clear, representative): 1.0
- Acceptable example (usable but not ideal): 0.5
- Poor example (not representative): 0.0

Average across all examples.

---

#### Step 5: Measure User Effort Reduction

**Baseline**: Time for human to define schema manually
- Estimated: 30-60 minutes per document

**With AI**: Time to review and refine AI suggestions
- Measured: Actual time to review + adjust

**Calculate**:
```
Effort Reduction = (Baseline Time - AI Time) / Baseline Time × 100%
```

**Target**: >50% reduction

---

#### Step 6: Qualitative Analysis

**Questions**:
1. What types of categories does AI consistently miss?
2. What spurious categories does AI frequently suggest?
3. Are AI's attribute suggestions useful?
4. Are AI's examples high quality?
5. Can errors be fixed with better prompting?

**Deliverable**: Written analysis with specific examples

---

#### Step 7: Results Summary

**Format**:
```markdown
## AI Schema Discovery Results

### Overall Accuracy
- Average F1 Score: X.XX (across 3 materials)
- Category Precision: X.XX
- Category Recall: X.XX
- Attribute Accuracy: X.XX
- Example Quality: X.XX/10

### User Effort Reduction
- Baseline time: XX minutes
- AI-assisted time: XX minutes
- Reduction: XX%

### Qualitative Findings
- Strengths: [What AI does well]
- Weaknesses: [What AI struggles with]
- Improvement Opportunities: [How to make AI better]

### Recommendation
[Should we use AI for schema discovery? Under what conditions?]
```

---

## 🔬 Research Question 3: Optimal Extraction Granularity

### Background

**Question**: At what level should we extract knowledge?
- Word-level (every significant word)
- Phrase-level (noun/verb phrases)
- Sentence-level (complete sentences)
- Paragraph-level (paragraph blocks)
- Section-level (entire sections)

**Hypothesis**: Sentence-level provides best accuracy-to-performance ratio

---

### Research Methodology

#### Step 1: Define Test Data

**Subject**: BIA Section 50.4(1) - Cash Flow Statement Requirement

**Full Text**:
```
The insolvent person shall, within 10 days after filing a notice of
intention, file with the official receiver a cash-flow statement in
the prescribed form indicating the insolvent person's projected cash
flow by week during the expected duration of the proposal.
```

---

#### Step 2: Extract at Different Granularities

##### **Granularity 1: Word-Level**

Tag every significant word:
```json
[
  {"word": "insolvent person", "type": "actor"},
  {"word": "shall", "type": "modal_verb"},
  {"word": "10 days", "type": "deadline_value"},
  {"word": "after filing", "type": "deadline_trigger"},
  {"word": "file", "type": "action"},
  {"word": "cash-flow statement", "type": "document"},
  {"word": "official receiver", "type": "recipient"}
]
```

---

##### **Granularity 2: Phrase-Level**

Extract noun and verb phrases:
```json
[
  {"phrase": "The insolvent person", "type": "actor"},
  {"phrase": "within 10 days after filing a notice", "type": "deadline"},
  {"phrase": "file with the official receiver", "type": "procedure"},
  {"phrase": "a cash-flow statement in prescribed form", "type": "document"}
]
```

---

##### **Granularity 3: Sentence-Level**

Extract complete sentences:
```json
{
  "sentence": "The insolvent person shall, within 10 days after filing a notice of intention, file with the official receiver a cash-flow statement in the prescribed form...",
  "entities": {
    "actor": "insolvent person",
    "procedure": "file cash-flow statement",
    "deadline": "10 days after filing notice",
    "document": "cash-flow statement"
  }
}
```

---

##### **Granularity 4: Paragraph-Level**

Extract paragraph as unit:
```json
{
  "paragraph": "[Full paragraph text containing multiple sentences]",
  "topics": ["cash flow requirements", "NOI filing", "timelines"]
}
```

---

##### **Granularity 5: Section-Level**

Extract entire section:
```json
{
  "section": "50.4(1)",
  "full_text": "[Complete section text]",
  "summary": "Cash flow filing requirements"
}
```

---

#### Step 3: Test Query Performance

**Test Query**: "What must the insolvent person file within 10 days?"

For each granularity, construct appropriate query and measure:

##### **Metrics**:
1. **Processing Time**: Time to extract at this granularity (seconds)
2. **Storage Size**: Size of extracted data (KB)
3. **Query Speed**: Time to retrieve answer (ms)
4. **Answer Completeness**: Does result have full context? (0-10)
5. **Direct Quote Available**: Can we return exact BIA text? (yes/no)

---

#### Step 4: Create Performance Matrix

| Granularity | Processing Time | Storage | Query Speed | Completeness | Quote Available | Total Score |
|-------------|----------------|---------|-------------|--------------|-----------------|-------------|
| Word-level | | | | | | |
| Phrase-level | | | | | | |
| Sentence-level | | | | | | |
| Paragraph-level | | | | | | |
| Section-level | | | | | | |

**Scoring**:
- Normalize all metrics to 0-10
- Lower is better for time/storage (invert scale)
- Higher is better for completeness
- Equal weights (20% each)

---

#### Step 5: Identify Sweet Spot

Plot granularity vs performance:

```
Performance Score
    ^
 10 |     *
    |    /|\
    |   / | \
    |  /  |  \
    | /   |   \
  0 +-----|-----|-----|-----|---->
      W   P   S   Par  Sec

Legend: W=Word, P=Phrase, S=Sentence, Par=Paragraph, Sec=Section
```

**Sweet Spot**: Granularity with highest total score

---

#### Step 6: Provide Recommendation

**Format**:
```markdown
## Optimal Granularity: [Level Name]

### Performance Summary
- Processing Time: X seconds (vs baseline)
- Storage Size: X KB (vs baseline)
- Query Speed: X ms
- Completeness Score: X/10
- Quote Preservation: Yes/No

### Trade-offs
- Wins: [What this level does best]
- Loses: [What this level sacrifices]

### When to Use Different Granularities
- Use [word-level] when: [scenario]
- Use [sentence-level] when: [scenario]
- Use [section-level] when: [scenario]

### Implementation Guidance
- [How to implement this granularity]
- [Tools/libraries to use]
- [Pitfalls to avoid]
```

---

## 📊 Final Deliverables

### Research Report Structure

Create comprehensive report: `docs/research/Phase0-Research-Report.md`

```markdown
# Phase 0 Research Report - Knowledge Extraction Architecture

## Executive Summary
- [2-3 paragraph overview of findings]
- [Key recommendations]

## Research Question 1: Entities vs Relationships
- [Full methodology and results]
- [Data tables and analysis]
- [Recommendation]

## Research Question 2: AI Schema Discovery
- [Full methodology and results]
- [Accuracy metrics]
- [Recommendation]

## Research Question 3: Optimal Granularity
- [Full methodology and results]
- [Performance analysis]
- [Recommendation]

## Impact on Architecture
- [How findings affect system design]
- [Changes to roadmap]
- [Technical specifications update]

## Appendices
- Appendix A: Raw data
- Appendix B: SQL queries used
- Appendix C: Test materials
```

---

## ⏱️ Time Estimates

- Research Q1: 2-3 hours
- Research Q2: 3-4 hours
- Research Q3: 2 hours
- Report writing: 1-2 hours
- **Total: 8-11 hours**

---

## ✅ Success Criteria

**Research Q1**:
- ✅ All 3 approaches tested with same data
- ✅ 10 queries executed on each
- ✅ Performance matrix complete
- ✅ Clear winner identified OR situational guidelines provided

**Research Q2**:
- ✅ 3 diverse materials tested
- ✅ F1 Score calculated
- ✅ User effort reduction measured
- ✅ Qualitative analysis complete

**Research Q3**:
- ✅ 5 granularities tested
- ✅ Performance matrix complete
- ✅ Sweet spot identified
- ✅ Usage guidelines provided

**Overall**:
- ✅ Report is data-driven (not opinion)
- ✅ Recommendations are specific and actionable
- ✅ Trade-offs are clearly explained
- ✅ Next steps are obvious

---

## 🚀 How to Execute This Research

### Option 1: Manual Execution
Follow each step sequentially, collecting data in spreadsheets, writing SQL queries manually.

### Option 2: Automated Script
Create Python script that automates data collection and analysis.

### Option 3: AI Agent Execution
Use this prompt with an AI agent (Claude, GPT-4, etc.) to autonomously conduct research and generate report.

**Recommended**: Option 3 with human validation of findings

---

## 📝 Notes

- All database queries assume SQLite
- Timing measurements should use consistent hardware
- AI schema discovery may require multiple prompt iterations
- Human judgment required for qualitative assessments
- Results should be reproducible (document all parameters)

---

**Document Status**: Research Protocol v1.0
**Created**: 2025-01-04
**Ready for Execution**: Yes
