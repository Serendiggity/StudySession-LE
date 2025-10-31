# Product Requirements Document (PRD)
## Insolvency Study Assistant with Lang Extract

**Version:** 1.0
**Date:** 2025-10-28
**Status:** Draft for Review
**Owner:** Jeff R.

---

## 1. Executive Summary

### 1.1 Purpose
Build an AI-powered learning tool that extracts structured knowledge from legal study materials (PDFs, documents) and generates exam-style quizzes based on learned question patterns from sample exam papers.

### 1.2 Problem Statement
Studying for insolvency administration exams requires:
- Processing hundreds of pages of dense legal material
- Understanding complex relationships between concepts, statutes, deadlines, and procedures
- Practicing with exam-realistic questions
- Verifying understanding against source material

Current solutions are inadequate:
- Manual note-taking is time-consuming and error-prone
- Generic AI tools hallucinate and lack source grounding
- Quiz generators don't match actual exam style
- No systematic way to capture statutory dependencies and deadline calculations

### 1.3 Solution Overview
A specialized extraction and quiz generation system powered by Google's Lang Extract framework that:
1. Extracts structured knowledge with source grounding (no hallucinations)
2. Learns question style from sample exam papers
3. Generates exam-realistic quizzes tailored to specific exam boards
4. Maintains verifiable references to source material
5. Handles documents of any length through intelligent chunking

### 1.4 Success Metrics
- **Extraction Quality:** 90-95% recall on defined categories
- **Quiz Style Match:** >90% similarity to sample exam papers
- **Source Grounding:** 100% of extractions linked to source
- **Cost Efficiency:** <$5 total for full knowledge base extraction
- **Time Savings:** 200+ hours vs. manual note-taking
- **User Satisfaction:** System enables effective exam preparation

---

## 2. Target Users

### 2.1 Primary User
**Insolvency administration student (you)**
- Preparing for professional insolvency exams
- Studying from 291-page textbook
- Needs to understand complex legal frameworks (BIA, CCAA, etc.)
- Wants exam-realistic practice questions
- Values accuracy and source verification

### 2.2 Future Users (Post-MVP)
- Other insolvency students
- Professional development candidates
- Legal education providers
- Study groups and tutors

---

## 3. Core Requirements

### 3.1 Functional Requirements

#### FR1: Document Processing
- **FR1.1:** Support PDF input (primary format)
- **FR1.2:** Extract text with high fidelity (handle legal formatting)
- **FR1.3:** Process documents up to 1000 pages
- **FR1.4:** Handle multiple documents (batch processing)
- **FR1.5:** Validate text extraction quality

#### FR2: Knowledge Extraction
- **FR2.1:** Extract 13 categories of information:
  - Concepts and definitions
  - Legal principles and rules
  - Statutory references (BIA, CCAA, Farm Debt Act, etc.)
  - Role-based obligations (Trustee, Receiver, etc.)
  - Deadlines and timeframes (with calculation methods)
  - Procedures and workflows
  - Document requirements
  - Event triggers and dependencies
  - Communication requirements
  - Relationships and dependencies
  - Case law and examples
  - Requirements and prerequisites
  - Exceptions and special cases
  - Common pitfalls
- **FR2.2:** Maintain source grounding (page, section, character position)
- **FR2.3:** Support multi-pass extraction (2-5 passes)
- **FR2.4:** Handle parallel processing for speed
- **FR2.5:** Store structured data in queryable format (JSONL + SQLite)
- **FR2.6:** Generate interactive HTML visualization

#### FR3: Deadline Calculation Intelligence
- **FR3.1:** Distinguish business days vs. calendar days vs. clear days
- **FR3.2:** Handle weekend and holiday exclusions
- **FR3.3:** Apply first-day/last-day rules correctly
- **FR3.4:** Link deadlines to triggering events
- **FR3.5:** Calculate deadline dates given triggering event
- **FR3.6:** Validate deadline compliance
- **FR3.7:** Identify common calculation pitfalls

#### FR4: Quiz Style Learning
- **FR4.1:** Accept sample quiz inputs (PDF, JSON, Markdown)
- **FR4.2:** Extract question patterns and structures
- **FR4.3:** Identify command verbs and usage frequency
- **FR4.4:** Learn answer format expectations
- **FR4.5:** Capture distractor strategies (for MCQs)
- **FR4.6:** Analyze mark allocation patterns
- **FR4.7:** Generate reusable style templates by exam board

#### FR5: Quiz Generation
- **FR5.1:** Generate 6 question types:
  - Multiple choice (4 options)
  - True/False with explanation
  - Short answer
  - Scenario-based
  - Calculation (deadline-focused)
  - Fill-in-the-blank
- **FR5.2:** Apply learned style templates
- **FR5.3:** Create plausible distractors for MCQs
- **FR5.4:** Generate model answers with source references
- **FR5.5:** Include marking criteria guidance
- **FR5.6:** Calibrate difficulty (basic, intermediate, advanced)
- **FR5.7:** Allow topic-specific quiz generation
- **FR5.8:** Support mixed difficulty quizzes
- **FR5.9:** Validate generated quizzes against style templates

#### FR6: CLI Interface
- **FR6.1:** Command: `extract` - Process study materials
- **FR6.2:** Command: `learn-style` - Analyze sample quizzes
- **FR6.3:** Command: `generate-quiz` - Create practice quizzes
- **FR6.4:** Command: `query` - Search knowledge base
- **FR6.5:** Command: `validate` - Check quiz quality
- **FR6.6:** Command: `stats` - View extraction statistics
- **FR6.7:** Command: `calculate-deadline` - Deadline calculator
- **FR6.8:** Interactive study mode (browse concepts)
- **FR6.9:** Interactive quiz-taking mode
- **FR6.10:** Progress tracking and persistence
- **FR6.11:** Export functionality (JSON, Markdown, CSV)
- **FR6.12:** Batch processing support

#### FR7: Quality Assurance
- **FR7.1:** Validate extraction completeness
- **FR7.2:** Check source grounding accuracy
- **FR7.3:** Score quiz style match (0-100)
- **FR7.4:** Test deadline calculations against known examples
- **FR7.5:** Verify statutory reference accuracy
- **FR7.6:** Detect circular dependencies
- **FR7.7:** Generate quality reports

### 3.2 Non-Functional Requirements

#### NFR1: Performance
- **NFR1.1:** Process 291-page document in <30 minutes (free tier)
- **NFR1.2:** Generate quiz in <10 seconds
- **NFR1.3:** Query knowledge base in <2 seconds
- **NFR1.4:** Support concurrent extractions (if paid tier)

#### NFR2: Cost Efficiency
- **NFR2.1:** Stay within free tier limits if possible
- **NFR2.2:** Total extraction cost <$5 (paid tier)
- **NFR2.3:** Per-quiz generation cost <$0.01
- **NFR2.4:** Implement API usage tracking and alerts

#### NFR3: Reliability
- **NFR3.1:** Handle rate limiting gracefully (auto-retry)
- **NFR3.2:** Recover from API failures
- **NFR3.3:** Validate data integrity
- **NFR3.4:** Log errors comprehensively
- **NFR3.5:** 100% source grounding (no hallucinations)

#### NFR4: Usability
- **NFR4.1:** Clear command-line interface with help text
- **NFR4.2:** Informative error messages
- **NFR4.3:** Progress indicators for long operations
- **NFR4.4:** Comprehensive documentation
- **NFR4.5:** Example workflows included

#### NFR5: Maintainability
- **NFR5.1:** Modular architecture (separate concerns)
- **NFR5.2:** Well-documented code
- **NFR5.3:** Unit test coverage >80%
- **NFR5.4:** Easy to add new extraction categories
- **NFR5.5:** Easy to add new question types

#### NFR6: Extensibility
- **NFR6.1:** Support multiple LLM providers (Gemini, OpenAI, local)
- **NFR6.2:** Pluggable extraction schemas
- **NFR6.3:** Custom quiz templates
- **NFR6.4:** API for programmatic access

---

## 4. User Stories

### 4.1 Extraction User Stories

**US1:** As a student, I want to upload my 291-page insolvency textbook so that I can extract all key concepts automatically.

**US2:** As a student, I want the system to extract deadlines with their calculation methods so that I understand when obligations arise.

**US3:** As a student, I want every extraction linked to its source page so that I can verify accuracy.

**US4:** As a student, I want to see relationships between concepts (e.g., which deadlines depend on which events) so that I understand dependencies.

**US5:** As a student, I want an interactive HTML view of extracted content so that I can navigate and review easily.

### 4.2 Quiz Generation User Stories

**US6:** As a student, I want to upload sample exam papers so that the system learns my exam board's question style.

**US7:** As a student, I want to generate quizzes on specific topics (e.g., "administrator duties") so that I can practice targeted areas.

**US8:** As a student, I want generated questions to match real exam style so that I'm properly prepared.

**US9:** As a student, I want model answers with source references so that I can verify correctness.

**US10:** As a student, I want quizzes with mixed difficulty so that I'm challenged appropriately.

### 4.3 Study & Practice User Stories

**US11:** As a student, I want to search the knowledge base by topic so that I can quickly find relevant information.

**US12:** As a student, I want to take quizzes interactively in the terminal so that I can practice without leaving my development environment.

**US13:** As a student, I want to calculate deadlines given a triggering event so that I can verify my understanding.

**US14:** As a student, I want to track my quiz scores over time so that I can measure progress.

**US15:** As a student, I want to export knowledge to flashcards so that I can use other study tools.

---

## 5. Out of Scope (for MVP)

### 5.1 Deferred Features
- **Web UI:** Phase 10 (optional), CLI is sufficient for MVP
- **Multi-user support:** Single-user tool initially
- **Real-time collaboration:** Not needed for individual study
- **Mobile app:** Desktop/terminal focus
- **Spaced repetition algorithm:** Can be added later
- **Integration with Anki/Quizlet:** Export only for now
- **Voice input:** Text-only for MVP
- **Image/diagram extraction:** Text-focused initially
- **Automatic updates to statutory references:** Manual refresh

### 5.2 Explicitly Excluded
- **Legal advice:** Tool is for study only, not practice
- **Real-time statutory tracking:** Snapshot in time
- **Commercial licensing:** Personal use only initially
- **Guaranteed exam pass:** Study aid, not certification

---

## 6. Assumptions & Constraints

### 6.1 Assumptions
- User has basic command-line familiarity
- User has Python 3.10+ installed
- User can obtain API keys (Google AI Studio)
- Source PDF is text-based (not scanned images requiring OCR)
- User has 3-5 sample exam papers available
- User is willing to create 50-100 extraction examples manually

### 6.2 Constraints
- Free tier rate limits: 15 RPM, 1M TPM
- Budget: Minimize API costs (<$10 preferred)
- Development time: 8-12 weeks
- Single developer (you + AI assistant)
- No existing codebase to integrate with

---

## 7. Dependencies & Risks

### 7.1 Dependencies
- **Critical:** Google Gemini API availability and pricing
- **Critical:** Lang Extract framework stability
- **Important:** PDF text extraction quality
- **Important:** Sample exam paper availability

### 7.2 Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Extraction quality insufficient | Medium | High | Multi-pass extraction, iterative refinement, manual validation |
| API costs exceed budget | Low | Medium | Use free tier, optimize chunking, set budget alerts |
| Rate limiting disrupts workflow | Medium | Low | Implement auto-retry, use paid tier if needed |
| Quiz style match is poor | Medium | High | Collect more sample papers, refine style templates |
| PDF text extraction fails | Low | High | Test early, use multiple PDF libraries (pypdf + pdfplumber) |
| Deadline calculations are complex | High | Medium | Extensive testing, validation against known examples |
| Project takes longer than expected | Medium | Low | Phase approach allows early value delivery |

---

## 8. Success Criteria

### 8.1 Launch Criteria (MVP)
- ✅ Successfully extract knowledge from 291-page PDF
- ✅ 90%+ recall on at least 5 core categories
- ✅ All extractions have source grounding
- ✅ Style templates created from 3+ sample papers
- ✅ Generate quizzes in 5+ question types
- ✅ CLI interface with 6+ commands works
- ✅ Deadline calculator validates correctly
- ✅ Total cost <$10
- ✅ Documentation complete
- ✅ User can complete full workflow end-to-end

### 8.2 Post-Launch Success Metrics
- User studies from knowledge base regularly (3+ times/week)
- User generates and completes 20+ practice quizzes
- User reports confidence improvement
- User passes insolvency exam (ultimate success!)

---

## 9. Timeline & Milestones

| Phase | Duration | Key Deliverable | Success Gate |
|-------|----------|----------------|--------------|
| Phase 1 | Week 1 | Project setup, PDF extraction | Clean text extracted |
| Phase 2 | Week 1-2 | Schema design, examples | 50+ examples created |
| Phase 3 | Week 2-3 | Core extraction engine | First extraction successful |
| Phase 4 | Week 3-4 | Comprehensive extraction | All categories extracted |
| Phase 5 | Week 4-5 | Quiz style learning | Style templates created |
| Phase 6 | Week 5-6 | Quiz generation | First quiz generated |
| Phase 7 | Week 6-7 | CLI interface | All commands work |
| Phase 8 | Week 7-8 | Validation & QA | Quality metrics met |
| Phase 9 | Week 8 | Documentation | Docs complete |
| **MVP Launch** | **Week 8** | **Full system operational** | **Can study & practice** |

---

## 10. Future Enhancements (Post-MVP)

### 10.1 Phase 10: Web UI (Optional)
- Document upload interface
- Interactive knowledge browser
- Quiz creation wizard
- Progress dashboard
- Timeline: Weeks 9-12
- Cost: $50-100/month hosting

### 10.2 Other Future Features
- Spaced repetition integration
- Collaborative study features
- Support for additional exam boards
- Automatic statutory update tracking
- Mobile-responsive interface
- API for third-party integrations
- Marketplace for shared study materials

---

## Appendix A: Document References

- **Architecture Document:** See `02-Architecture-Document.md`
- **Implementation Plan:** See `03-Implementation-Plan.md`
- **Schema Specification:** See `04-Schema-Specification.md`
- **Example Creation Guide:** See `05-Example-Creation-Guide.md`
- **API Cost Management:** See `06-API-Cost-Management-Plan.md`

---

## Appendix B: Glossary

- **BIA:** Bankruptcy and Insolvency Act
- **CCAA:** Companies' Creditors Arrangement Act
- **OSB:** Office of the Superintendent of Bankruptcy
- **IP:** Insolvency Practitioner
- **Lang Extract:** Google's extraction framework for structured data from unstructured text
- **Source Grounding:** Linking extracted data to exact location in source document
- **Clear Days:** Calculation method excluding both first and last day
- **Business Days:** Monday-Friday, excluding statutory holidays
- **RPM:** Requests Per Minute (API rate limit)
- **TPM:** Tokens Per Minute (API rate limit)
