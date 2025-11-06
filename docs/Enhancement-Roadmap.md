# Enhancement Roadmap - Universal Knowledge Extraction & Learning Platform

**Date**: 2025-01-04
**Status**: Planning Phase
**Goal**: Transform insolvency-specific tool into universal, multi-project learning platform

---

## 🎯 **The Complete Vision**

A **Universal Knowledge Extraction & Learning Platform** that:

1. **Accepts any input** (PDF, Word, URL, image, text)
2. **AI analyzes** structure and suggests schemas
3. **User guides** by selecting examples from material
4. **Extracts knowledge** using optimal approach (research entities vs relationships)
5. **Builds knowledge graph** across multiple projects/domains
6. **Finds common ground** (Legal "procedures" ≈ Medical "treatments")
7. **Answers questions** with direct quotes (zero hallucination)
8. **Generates quizzes** adapted to user's learning patterns
9. **Continuously improves** through pattern recognition
10. **Works everywhere** via MCP server (Claude Desktop, custom apps)

---

## 📋 **Core Requirements (From User Feedback)**

### **1. Dynamic Schema Discovery**
> "How are these entities determined when we don't know what future source data would be?"

**The Problem**: Current system hardcodes entity types (actors, procedures, deadlines). Won't work for Radiology, Software Engineering, etc.

**Solution**: AI analyzes unknown material → suggests appropriate categories → user approves

**Example Flow**:
```
Upload medical textbook → AI detects: conditions, treatments,
contraindications, dosages, patient_types → User refines → Extract
```

---

### **2. Intelligent Agent-Guided Extraction**
> "The agent should understand and guide the user along the extraction step"

**Requirements**:
- Agent **samples** the document first
- Agent **reasons** about document structure
- Agent **suggests** data slices and categories
- Agent **compares** to existing knowledge base
- Agent **finds common ground** across different materials

**Example**:
```
Agent: "I've analyzed your contract law textbook. I see patterns of:
        - Parties (similar to 'actors' in your insolvency project)
        - Obligations (similar to 'procedures')
        - Remedies (similar to 'consequences')

        Should I map these to create a unified knowledge graph?"

User: Yes, map parties → actors
```

---

### **3. User-Selected Examples (Not AI-Generated)**
> "The agent should prompt the user to select examples from the material"

**Current Approach**: We write examples in Python files
**Better Approach**: User highlights text from the actual material

**Workflow**:
```
1. Agent: "I found 47 potential 'deadlines'.
           Please select 3-5 good examples by highlighting them."

2. User highlights in document:
   - "within 10 days after filing"
   - "21 months from bankruptcy date"
   - "immediately upon receipt"

3. Agent: "Got it! I'll use these patterns to find similar deadlines."

4. Extraction runs using user's examples
```

**Benefit**: More accurate, user controls quality, learns from real material

---

### **4. Multi-Modal Input**
> "Should support URLs, other text types, and even images of text"

**Requirements**:
- ✅ PDFs (current)
- ✅ Word documents (.docx)
- ✅ Plain text files
- ✅ URLs / web pages
- ✅ Images (OCR via Gemini Vision)
- ✅ Copy & paste text
- ✅ Screenshots

**AI Pre-Processing**:
> "AI should intervene somewhere to study input and suggest if data needs cleaning"

**Example**:
```
Upload scanned PDF → AI detects: "Low quality OCR,
many errors. Should I clean this first? [Y/n]"
```

---

### **5. RESEARCH NEEDED: Entities vs Relationships**
> "More research about if entity extraction and relationship extraction both are needed and what advantages they present"

**This is CRITICAL - affects entire architecture**

**Three Options to Research**:

#### **Option A: Entities Only**
```sql
-- Store atomic facts
actors: {id: 1, name: "Trustee"}
procedures: {id: 2, name: "file cash flow"}
deadlines: {id: 3, timeframe: "10 days"}

-- Problem: How do we know which connects to which?
-- No context, no direct quotes
```

**Pros**:
- Simple structure
- Fast individual entity lookup
- Easy to add new entities

**Cons**:
- No relationships = no context
- Can't preserve direct quotes
- Hard to answer "who does what when" questions

---

#### **Option B: Relationships Only (with full text)**
```sql
-- Store complete sentences only
relationships: {
  text: "Trustee shall file cash flow within 10 days",
  section: "50.4(1)"
}

-- Problem: Can't filter by actor, slow queries
-- But: Preserves context, has direct quotes
```

**Pros**:
- Always have direct quotes
- Complete context preserved
- Simple schema

**Cons**:
- Can't filter by entity type (e.g., "show all Trustee duties")
- Slower queries (full-text search only)
- Harder to find patterns

---

#### **Option C: Hybrid (Current Approach)**
```sql
-- Both entities AND relationships
entities: {actors, procedures, deadlines}
relationships: {
  actor_id: 1,
  procedure_id: 2,
  deadline_id: 3,
  relationship_text: "Trustee shall file cash flow within 10 days"
}

-- Benefit: Structured queries + source truth
-- Cost: More complex, more storage
```

**Pros**:
- Structured filtering (fast queries)
- Direct quotes preserved
- Best of both worlds

**Cons**:
- More complex extraction
- More storage required
- More code to maintain

---

**Need to Test**:
- Query performance (which is faster?)
- Storage requirements (how much bigger?)
- Accuracy (which preserves meaning better?)
- Flexibility (which adapts to new domains?)

---

### **6. Continuous Improvement & Pattern Recognition**
> "Logging + pattern recognition to understand why system sometimes fails"

**What to Log**:
```sql
CREATE TABLE system_operations (
  id INTEGER PRIMARY KEY,
  timestamp DATETIME,
  operation_type TEXT,  -- 'extraction', 'query', 'quiz_generation'
  input_data TEXT,
  output_data TEXT,
  success BOOLEAN,
  failure_reason TEXT,
  user_feedback TEXT,
  performance_metrics JSON
);
```

**Pattern Detection Examples**:
```python
# Analyze failures
if most_failures.reason == "Quote not in database":
    suggest_re_extraction(missing_sections)

if most_failures.section == "50.4":
    suggest_more_examples_for("50.4")

if user_satisfaction < 0.7:
    flag_for_review(question_id)
```

**Self-Improvement Loop**:
```
User asks question → Log query → Track if answer satisfied user
→ Detect patterns in failures → Auto-suggest improvements
→ Re-extract or add examples → Quality improves
```

---

### **7. Quiz Generation Engine**
> "Learn question structure from historical questions and generate new practice questions"

**What to Learn**:
```sql
CREATE TABLE quiz_analytics (
  id INTEGER PRIMARY KEY,
  question_structure TEXT,      -- "When must [actor] [action]?"
  correct_answer_pattern TEXT,  -- Numerical, timeframe, yes/no
  distractor_patterns JSON,     -- Wrong but plausible answers
  difficulty_level REAL,        -- Based on % correct
  topic_tags TEXT,
  frequently_confused_with TEXT -- e.g., "50.4 vs 50.5"
);
```

**Generation Algorithm**:
```python
# Learn from existing questions
patterns = analyze_historical_questions()

# Generate new question
new_question = {
  "structure": "When must {actor} {procedure}?",
  "answer": extract_from_db(actor="Trustee", procedure="file cash flow"),
  "distractors": generate_plausible_wrongs(
    common_confusion="10 days vs 21 days",
    similar_section="50.4 vs 50.5"
  )
}
```

**Adaptive Features**:
- User answers correctly → Increase difficulty
- User struggles → Provide easier questions on same topic
- Spaced repetition based on forgetting curve
- Track weak areas and focus practice there

---

### **8. Multi-Project Architecture**
> "Create different projects like Insolvency Law, Radiology, etc. and switch between them"

**Directory Structure**:
```
projects/
├── insolvency-law/
│   ├── database/knowledge.db
│   ├── sources/
│   │   ├── bia_statute/
│   │   ├── study_materials/
│   │   └── osb_directives/
│   ├── schema/entity_types.json  ← Custom per project
│   ├── data/
│   │   ├── input/
│   │   ├── output/
│   │   └── examples/
│   └── config.json
│
├── radiology/
│   ├── database/knowledge.db
│   ├── sources/
│   ├── schema/entity_types.json  ← Different schema
│   ├── data/
│   └── config.json
│
└── software-engineering/
    ├── database/knowledge.db
    ├── sources/
    ├── schema/entity_types.json
    ├── data/
    └── config.json
```

**Project Config Example**:
```json
{
  "project_name": "Radiology",
  "project_id": "radiology",
  "domain": "medicine",
  "entity_schema": {
    "categories": [
      {"name": "conditions", "attributes": ["condition_name", "presentation"]},
      {"name": "imaging_methods", "attributes": ["modality", "protocol"]},
      {"name": "findings", "attributes": ["finding_description", "significance"]},
      {"name": "diagnoses", "attributes": ["diagnosis", "confidence_level"]}
    ]
  },
  "sources": [...],
  "database_path": "database/knowledge.db"
}
```

---

## 🔬 **CRITICAL: Research Phase (Must Do First)**

Before building anything, we MUST answer these questions with data.

### **Research Question 1: Entities vs Relationships vs Hybrid**

**Hypothesis**: Hybrid approach provides best balance of speed, accuracy, and flexibility

**Test Design**:
```
1. Take same BIA content (e.g., Section 50.4)
2. Extract 3 ways:
   - Entities only (actors, procedures, deadlines as separate tables)
   - Relationships only (full sentences with minimal metadata)
   - Hybrid (current approach - both entities + relationship_text)

3. Run 10 test queries:
   - "What must Trustee do within 10 days?"
   - "All duties with deadlines"
   - "Find all 'shall' requirements"
   - etc.

4. Measure for each approach:
   - Storage size (KB)
   - Query speed (ms)
   - Answer accuracy (can we get direct quotes?)
   - Code complexity (LOC)
   - Flexibility (can we adapt schema to medical domain?)

5. Score each dimension (1-10)
6. Calculate weighted total
7. Winner: Choose optimal approach based on data
```

**Estimated Time**: 2-3 hours
**Deliverable**: Research report with recommendation

**Success Criteria**:
- Clear winner emerges (>20% better on weighted score)
- OR we identify when to use each approach (situational)

---

### **Research Question 2: AI Schema Discovery Accuracy**

**Hypothesis**: AI can reliably suggest entity categories for unknown materials with >80% accuracy

**Test Design**:
```
1. Gather 3 test materials (different domains):
   - Medical textbook chapter (radiology)
   - Software engineering documentation (API design)
   - Contract law sample (commercial agreements)

2. For each material:
   - Have AI analyze and suggest entity categories
   - Have human expert define "gold standard" schema
   - Compare AI suggestions to expert schema

3. Measure:
   - Precision: % of AI suggestions that are useful
   - Recall: % of expert categories that AI found
   - F1 Score: Harmonic mean of precision and recall
   - User effort reduction: Time saved vs manual schema design

4. Qualitative analysis:
   - What types of categories does AI miss?
   - What spurious categories does AI suggest?
   - Can errors be fixed with better prompting?
```

**Estimated Time**: 3-4 hours
**Deliverable**: Confidence score for AI schema discovery + improvement recommendations

**Success Criteria**:
- F1 Score >0.80 (80% accurate)
- User effort reduction >50%
- Errors are catchable during user review phase

---

### **Research Question 3: Optimal Extraction Granularity**

**Hypothesis**: Sentence-level extraction provides best accuracy-to-performance ratio

**Test Design**:
```
1. Extract BIA Section 50.4 at different granularities:
   - Word-level: Every significant word tagged
   - Phrase-level: Extract noun/verb phrases
   - Sentence-level: Extract complete sentences
   - Paragraph-level: Extract paragraph blocks
   - Section-level: Extract entire sections

2. For each granularity:
   - Run extraction
   - Test 10 queries
   - Measure:
     * Processing time (minutes)
     * Storage size (KB)
     * Answer completeness (do we get full context?)
     * Direct quote availability

3. Plot granularity vs performance
4. Identify sweet spot (best trade-off)
```

**Estimated Time**: 2 hours
**Deliverable**: Best practice guide for extraction granularity

**Success Criteria**:
- Clear optimal granularity identified
- <10% accuracy loss vs highest granularity
- >50% faster than highest granularity

---

## 🗺️ **Implementation Roadmap (After Research)**

### **Phase 0: Research** (1-2 days, 8-16 hours)

**Goal**: Answer critical questions before building

**Tasks**:
- [ ] Research Q1: Entities vs Relationships (2-3 hours)
- [ ] Research Q2: AI Schema Discovery (3-4 hours)
- [ ] Research Q3: Extraction Granularity (2 hours)
- [ ] Synthesize findings into design decisions (1 hour)
- [ ] Create detailed technical specs based on research (2 hours)

**Deliverables**:
- `docs/research/entities-vs-relationships.md`
- `docs/research/ai-schema-discovery.md`
- `docs/research/extraction-granularity.md`
- `docs/Technical-Specification.md`

---

### **Phase 1: Foundation** (3-5 days)

**Goal**: Multi-project infrastructure and dynamic schema system

**Tasks**:
- [ ] Create multi-project directory structure
- [ ] Implement `ProjectManager` class
- [ ] Implement dynamic schema system (JSON-based)
- [ ] Build multi-modal input handler (PDF, Word, URL, image)
- [ ] Create project manager CLI (`kb projects create/switch/list`)
- [ ] Implement project config system
- [ ] Add project switcher

**Deliverables**:
- `src/project/project_manager.py`
- `src/project/schema_manager.py`
- `src/input/multi_modal_handler.py`
- `tools/project/kb_cli.py`
- Working multi-project system (create, switch, manage)

**Test**:
```bash
kb projects create "Test Project" --domain test
kb projects switch test-project
kb projects list
```

---

### **Phase 2: Intelligence** (5-7 days)

**Goal**: AI-powered material analysis and schema suggestion

**Tasks**:
- [ ] Build AI material analyzer (samples content, detects patterns)
- [ ] Build schema suggester (proposes entity categories)
- [ ] Build example selector interface (user highlights examples)
- [ ] Build common ground finder (maps across projects)
- [ ] Create review interface for schema approval
- [ ] Implement AI pre-processing (detect quality issues)

**Deliverables**:
- `src/analysis/material_analyzer.py`
- `src/analysis/schema_suggester.py`
- `src/analysis/example_selector.py`
- `src/analysis/common_ground_finder.py`
- `tools/ingestion/add_material.py` (interactive CLI)

**Test**:
```bash
kb sources add --file unknown_material.pdf --analyze
# AI suggests schema → User reviews → Extraction runs
```

---

### **Phase 3: Extraction** (3-4 days)

**Goal**: Implement optimal extraction approach (based on research results)

**Tasks**:
- [ ] Implement chosen extraction strategy (entities/relationships/hybrid)
- [ ] Build user-guided extraction workflow
- [ ] Add progress tracking and reporting
- [ ] Implement incremental extraction (add to existing knowledge)
- [ ] Add extraction quality checks
- [ ] Create extraction retry/refinement system

**Deliverables**:
- `src/extraction/optimal_extractor.py` (based on research)
- `src/extraction/guided_workflow.py`
- `src/extraction/progress_tracker.py`
- Enhanced extraction pipeline

**Test**:
- Extract test material using new approach
- Verify quality metrics
- Compare to baseline

---

### **Phase 4: Enhancement** (4-6 days)

**Goal**: Continuous improvement and quiz generation

**Tasks**:
- [ ] Implement operation logging system
- [ ] Build pattern recognition engine
- [ ] Create quiz generation algorithm
- [ ] Implement adaptive difficulty system
- [ ] Build continuous improvement loop
- [ ] Add user feedback collection
- [ ] Create analytics dashboard

**Deliverables**:
- `src/logging/operation_logger.py`
- `src/analytics/pattern_detector.py`
- `src/quiz/question_generator.py`
- `src/quiz/adaptive_difficulty.py`
- `src/improvement/continuous_improver.py`
- `tools/analytics/dashboard.py`

**Test**:
```bash
kb quiz generate --topic "deadlines" --difficulty adaptive
kb analytics show --failures
kb improve suggest
```

---

### **Phase 5A: MCP Server** (2-3 days)

**Goal**: Build MCP server for data access layer

**Tasks**:
- [ ] Build MCP server (multi-project aware)
- [ ] Implement MCP tools:
  - [ ] `query_knowledge_base` - Query with direct quotes
  - [ ] `extract_relationships` - Extract from material
  - [ ] `switch_project` - Switch between projects
  - [ ] `add_material` - Add source to project
  - [ ] `get_statistics` - Database statistics
- [ ] Implement MCP resources:
  - [ ] `bia://section/[N]` - BIA section access
  - [ ] `project://[name]/schema` - Project schema access
  - [ ] `project://list` - List all projects
- [ ] Test MCP server with Claude Desktop

**Deliverables**:
- `insolvency_mcp/server.py`
- `insolvency_mcp/tools/` (5 core tools)
- `insolvency_mcp/resources/` (resource handlers)
- MCP configuration for Claude Desktop

**Test**:
```bash
# Install MCP server in Claude Desktop
# Query insolvency database
# Switch to radiology project
# Query radiology database
```

---

### **Phase 5B: Claude Skills** (2-3 days) ⭐ NEW

**Goal**: Create universal workflow skills (based on Claude Skills research)

**Why Skills?**:
- **Automatic invocation** (no manual delegation)
- **Universal workflows** (work across all projects)
- **Progressive disclosure** (lighter context usage)
- **Claude Desktop compatible** (not just Claude Code)
- **Reusable** across law, medicine, engineering, etc.

**Skills to Create**:

#### 1. Knowledge Extraction Skill
```yaml
---
name: knowledge-extraction
description: Extract structured knowledge from any document (legal, medical, technical). Guides user through document analysis, schema suggestion, example selection, and extraction. Use when user wants to extract knowledge from PDFs, textbooks, or technical documentation.
---
```

**Structure**:
```
.claude/skills/knowledge-extraction/
├── SKILL.md                        # Main instructions (<500 lines)
├── scripts/
│   ├── analyze_document.py         # Uses MaterialAnalyzer
│   ├── suggest_schema.py           # Uses SchemaSuggester
│   └── run_extraction.py           # Uses ExtractionRunner
└── resources/
    ├── schema_templates.json       # Pre-built templates
    └── examples.md                 # Example workflows
```

#### 2. Multi-Project Query Skill
```yaml
---
name: multi-project-query
description: Query knowledge bases across multiple projects (insolvency law, radiology, software engineering). Finds answers with direct quotes and cross-references. Use when user asks domain-specific questions requiring database lookup.
---
```

**Structure**:
```
.claude/skills/multi-project-query/
├── SKILL.md                        # Query workflow
├── scripts/
│   ├── detect_project.py           # Auto-detect which project
│   ├── format_answer.py            # Sidebar formatting
│   └── record_qa.py                # Log to CSV
└── resources/
    └── query_templates.json        # Common query patterns
```

#### 3. Exam Quiz Generator Skill
```yaml
---
name: exam-quiz-generator
description: Generate practice exam questions from knowledge base content. Learns question patterns and creates realistic practice questions with plausible distractors. Use when user wants to practice or test knowledge.
---
```

**Structure**:
```
.claude/skills/exam-quiz-generator/
├── SKILL.md                        # Quiz generation workflow
├── scripts/
│   ├── analyze_patterns.py         # Pattern learning
│   ├── generate_questions.py       # Question generation
│   └── create_distractors.py       # Wrong answer creation
└── resources/
    ├── question_patterns.json      # Learned patterns
    └── quiz_templates.json         # Question formats
```

**Tasks**:
- [ ] Create knowledge-extraction skill
- [ ] Create multi-project-query skill
- [ ] Create exam-quiz-generator skill
- [ ] Test skills in Claude Desktop
- [ ] Test skills with Haiku, Sonnet, Opus
- [ ] Validate automatic invocation
- [ ] Ensure <500 lines per SKILL.md

**Deliverables**:
- `.claude/skills/knowledge-extraction/`
- `.claude/skills/multi-project-query/`
- `.claude/skills/exam-quiz-generator/`
- `docs/Skills-Guide.md` (usage documentation)

**Test**:
```bash
# Test in Claude Desktop:
# 1. Upload document → knowledge-extraction auto-invokes
# 2. Ask domain question → multi-project-query auto-invokes
# 3. Request practice quiz → exam-quiz-generator auto-invokes
```

**Note**: Keep existing agent (`.claude/agents/insolvency-exam-assistant.md`) for specialized exam answering.

---

### **Phase 5C: Distribution** (1-2 days)

**Goal**: Package and distribute complete system

**Tasks**:
- [ ] Create project templates (law, medicine, engineering)
- [ ] Write comprehensive documentation
- [ ] Package for distribution (PyPI or GitHub)
- [ ] Create setup guide (MCP + Skills)
- [ ] Create video tutorial

**Deliverables**:
- `templates/` (pre-built project schemas)
- `README.md`, `docs/User-Guide.md`
- `docs/Skills-Guide.md`
- `docs/MCP-Setup.md`
- `pyproject.toml` (for distribution)
- Setup video/screenshots

**Test**:
```bash
# Install complete system from scratch
# Follow setup guide
# Create new project
# Extract knowledge
# Query database
# Generate quiz
```

---

## ⏱️ **Timeline Estimate**

| Phase | Duration | Calendar Time | Status |
|-------|----------|---------------|--------|
| Phase 0: Research | 8-16 hours | 1-2 days | ✅ COMPLETE |
| Phase 1: Foundation | 24-40 hours | 3-5 days | ✅ COMPLETE |
| Phase 2: Intelligence | 40-56 hours | 5-7 days | ✅ COMPLETE |
| Phase 3: Extraction | 24-32 hours | 3-4 days | ✅ COMPLETE |
| Phase 4: Enhancement | 32-48 hours | 4-6 days | ⏳ PENDING |
| Phase 5A: MCP Server | 16-24 hours | 2-3 days | ⏳ PENDING |
| Phase 5B: Claude Skills ⭐ | 16-24 hours | 2-3 days | ⏳ PENDING |
| Phase 5C: Distribution | 8-16 hours | 1-2 days | ⏳ PENDING |
| **Total** | **168-256 hours** | **21-32 days** |

**Realistic Timeline**: 4-5 weeks of focused development

**Updated Progress**: 4/8 phases complete (50%)

---

## ✅ **Success Criteria**

### **Phase 0 Success**
- ✅ Data-driven answer to entities vs relationships question
- ✅ AI schema discovery validated (>80% F1 score)
- ✅ Optimal granularity identified

### **Phase 1 Success**
- ✅ Can create new project with custom schema
- ✅ Can switch between projects
- ✅ Can upload any file type (PDF, Word, URL, image)

### **Phase 2 Success**
- ✅ AI accurately suggests schemas for unknown materials
- ✅ User can select examples by highlighting text
- ✅ System finds common ground across projects

### **Phase 3 Success**
- ✅ Extraction uses optimal approach from research
- ✅ User guides extraction with selected examples
- ✅ Quality meets baseline (25/25 exam questions)

### **Phase 4 Success**
- ✅ System logs all operations
- ✅ Pattern detection identifies improvement opportunities
- ✅ Quiz generation creates realistic practice questions
- ✅ System improves over time

### **Phase 5A Success** (MCP Server)
- ✅ MCP server installed in Claude Desktop
- ✅ Can query any project from Claude Desktop
- ✅ All 5 core tools working (query, extract, switch, add, statistics)
- ✅ Resources accessible (bia://, project://)
- ✅ Multi-project switching works

### **Phase 5B Success** (Claude Skills) ⭐
- ✅ knowledge-extraction skill auto-invokes on document upload
- ✅ multi-project-query skill auto-invokes on domain questions
- ✅ exam-quiz-generator skill auto-invokes on quiz requests
- ✅ Skills work in Claude Desktop (not just Claude Code)
- ✅ Each skill <500 lines with progressive disclosure
- ✅ Tested on Haiku, Sonnet, Opus

### **Phase 5C Success** (Distribution)
- ✅ Complete installation guide (MCP + Skills)
- ✅ Documentation complete
- ✅ Ready for distribution (PyPI or GitHub)
- ✅ Works for new users following guide

---

## 🎯 **Next Step: Begin Research Phase**

**Recommended Starting Point**: Research Question 1 (Entities vs Relationships)

**Why This First**:
- Affects entire architecture
- Informs all subsequent design decisions
- Can be tested with existing data
- Takes only 2-3 hours
- High-impact, low-effort

**Proposed Action**:
```bash
# Create research experiment
python3 research/test_extraction_approaches.py

# Run for 2 hours, get data-driven answer
# Then proceed with confidence
```

---

## 📚 **References**

- Current system architecture: `docs/architecture/01-System-Overview.md`
- Key innovation (relationship_text): `docs/architecture/05-Key-Innovation.md`
- User feedback (screenshots): Captured in this document
- Existing codebase: `/src`, `/tools`, `/data`

---

## 📝 **Notes**

- This roadmap is based on comprehensive user feedback
- Research phase is critical - do not skip
- Phases can be adjusted based on research findings
- Success criteria must be met before proceeding to next phase
- Timeline assumes focused development time

**Document Status**: Draft v1.0
**Last Updated**: 2025-01-04
**Next Review**: After Phase 0 completion
