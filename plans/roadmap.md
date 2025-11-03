# Product Roadmap - Insolvency Study Assistant

**Vision:** Integrated AI-powered study assistant with dynamic visualization capabilities for comprehensive insolvency exam preparation.

---

## ✅ Phase 1: Foundation (Sessions 1-2) - COMPLETE

**Goal:** Build validated multi-source knowledge base

**Completed:**
- Multi-source database (Course Material + BIA + OSB Directives)
- 13,779 entities + 385 BIA sections + 5 Directives
- Cross-reference navigation
- Full-text search (FTS5)
- Quiz validation system
- 100% exam accuracy (25/25 questions)

**Status:** ✅ Production-ready knowledge base

---

## 🔜 Phase 2: Relationships + Web UI (Session 3)

**Goal:** Enable complex queries and dynamic visualization in integrated web interface

### Part A: Relationship Extraction (3-4 hours)
**Deliverable:** Enhanced database with explicit relationships

- Extract relationships from existing entities (NO re-extraction)
- 3 relationship types: duties, document requirements, triggers
- Cover ALL BIA sections (not just Division I)
- 100+ relationships extracted

**Query Enhancement:**
```sql
-- Before: "Show deadlines"
SELECT timeframe FROM deadlines;

-- After: "Show complete duty chains"
SELECT actor, procedure, deadline, consequence
FROM v_complete_duties
WHERE actor = 'Trustee';
```

### Part B: Streamlit Web UI (6-8 hours)
**Deliverable:** Working web application with live diagram rendering

**UI Components:**
1. **Prompt Input Box**
   - User types: "Show me the discharge process"
   - Submit button

2. **AI Response Area**
   - Claude/Gemini processes query
   - Queries database for relevant sections/relationships
   - Generates diagram code

3. **Live Diagram Display**
   - Renders Mermaid diagrams in-browser
   - Multiple diagram types available
   - Supports: flowchart, mindmap, sequence, class, ER, Gantt, state

4. **Diagram Type Selector**
   - User chooses visualization type
   - AI regenerates in selected format
   - Side-by-side comparison option

**Tech Stack:**
- Streamlit (Python web framework)
- streamlit-mermaid (in-app diagram rendering)
- Claude/Gemini API (AI processing)
- SQLite (database queries)

**Example User Flow:**
```
1. User types: "Explain Division I NOI process"
2. AI queries: bia_sections for s. 50-66 + relationships
3. AI generates: Mermaid flowchart code
4. UI renders: Visual flowchart in browser
5. User clicks: "Show as mindmap instead"
6. AI regenerates: Mermaid mindmap code
7. UI renders: Visual mindmap
```

---

## 🔮 Phase 3: Advanced UI Features (Session 4+)

**Goal:** Enhanced study tools and production-ready deployment

### Features to Add:

**Study Tools:**
- Interactive quiz mode (questions pulled from validation database)
- Progress tracking (topics covered, accuracy stats)
- Spaced repetition system (flashcards from concepts)
- Search across all sources with highlighting

**Visualization Enhancements:**
- Export diagrams (PNG, SVG, PDF)
- Diagram editing (customize generated diagrams)
- Multiple diagrams side-by-side
- Zoom, pan, interactive elements
- Additional libraries: D3.js for Venn diagrams, complex visualizations

**Advanced Queries:**
- Natural language: "What are trustee duties in bankruptcy?"
- Follow-up questions: "What happens if they miss the deadline?"
- Citation tracking: "Show me where this is in the BIA"
- Cross-reference traversal UI

---

## 🚀 Phase 4: Production Deployment (Post-Exam)

**Goal:** Shareable, hosted application

**Deployment Options:**
- Streamlit Cloud (free tier available)
- Heroku/Railway (simple deployment)
- Self-hosted (local network)

**Enhancements:**
- Multi-user support
- Saved study sessions
- Collaborative features (share diagrams)
- Mobile-responsive design

---

## Feature Prioritization by Exam Timeline

**1 Month to Exam:**

### Week 1 (Session 3)
- ✅ Relationship extraction (all sections)
- ✅ Streamlit UI with live Mermaid rendering
- ✅ Basic diagram types (flowchart, mindmap)
- ✅ Query interface

### Week 2
- ⭐ More diagram types (sequence, class, state)
- ⭐ Quiz mode integration
- ⭐ Polish UI/UX

### Week 3
- 📚 **STUDY USING THE TOOL**
- 🐛 Fix any bugs discovered
- 🎯 Refine based on actual usage

### Week 4 (Exam Week)
- 🎓 **EXAM**
- System is frozen (no changes during exam prep)

### Post-Exam
- 🚀 Production features (deployment, advanced viz, etc.)

---

## Technical Milestones

### Milestone 1: Queryable Knowledge Base ✅
- **Completed:** Session 2
- **Validated:** 100% exam accuracy

### Milestone 2: Relationship-Enhanced Database
- **Target:** Session 3A
- **Validation:** Complex multi-entity queries work

### Milestone 3: Integrated Web UI
- **Target:** Session 3B
- **Validation:** Prompt → Diagram renders in-app

### Milestone 4: Production-Ready
- **Target:** Post-exam
- **Validation:** Deployable, shareable, polished

---

## Success Metrics

**By End of Session 3:**
- ✅ Can ask AI any insolvency question via web interface
- ✅ Diagrams generate dynamically for any process
- ✅ Multiple visualization types supported
- ✅ All in one integrated application

**By Exam:**
- ✅ Well-practiced with the tool
- ✅ All major processes visualized
- ✅ Confident in exam readiness

**Post-Exam:**
- ✅ Shareable application
- ✅ Advanced features
- ✅ Production deployment

---

## Current Status

**Completed:**
- ✅ Multi-source knowledge base
- ✅ Exam validation (100% accuracy)
- ✅ Tech stack research (Streamlit selected)

**Next:**
- 🔜 Session 3: Build integrated UI with relationships + diagrams

**Vision:**
- 🔮 Complete AI study assistant with dynamic visualizations
- 🔮 Integrated web application (no external tools)
- 🔮 Production-ready deployment

---

**Path is clear: Foundation built → Now building the integrated experience → Then production polish**
