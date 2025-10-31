# Architecture Document
## Insolvency Study Assistant - Technical Design

**Version:** 1.0
**Date:** 2025-10-28
**Status:** Approved

---

## 1. System Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACE LAYER                     │
│  ┌──────────────────────┐         ┌────────────────────┐   │
│  │   CLI Interface      │         │  (Future: Web UI)  │   │
│  │  - Commands          │         │  - React Frontend  │   │
│  │  - Interactive modes │         │  - REST API        │   │
│  └──────────┬───────────┘         └─────────┬──────────┘   │
└─────────────┼─────────────────────────────────┼─────────────┘
              │                                 │
┌─────────────▼─────────────────────────────────▼─────────────┐
│                   APPLICATION LAYER                          │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │  Document   │  │  Extraction  │  │  Quiz Generator  │   │
│  │  Processor  │  │  Engine      │  │  & Style Learner │   │
│  └──────┬──────┘  └──────┬───────┘  └────────┬─────────┘   │
└─────────┼────────────────┼─────────────────────┼────────────┘
          │                │                     │
┌─────────▼────────────────▼─────────────────────▼────────────┐
│                      CORE SERVICES LAYER                     │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────────┐   │
│  │  PDF Parser  │  │  Lang       │  │  Deadline        │   │
│  │              │  │  Extract    │  │  Calculator      │   │
│  └──────────────┘  │  Wrapper    │  └──────────────────┘   │
│                    └──────┬──────┘                          │
└───────────────────────────┼─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                    DATA PERSISTENCE LAYER                    │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────────┐   │
│  │  SQLite DB   │  │  JSONL      │  │  Configuration   │   │
│  │  (Structured)│  │  Storage    │  │  (YAML/ENV)      │   │
│  └──────────────┘  └─────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                    EXTERNAL SERVICES                         │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────────┐   │
│  │  Google      │  │  (Optional)  │  │  (Optional)      │   │
│  │  Gemini API  │  │  OpenAI API  │  │  Local Models    │   │
│  └──────────────┘  └─────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Component Design

### 2.1 Document Processor Module

**Responsibility:** Extract text from various document formats

**Components:**
```
document_processor/
├── __init__.py
├── pdf_extractor.py         # PDF → text conversion
├── text_cleaner.py          # Text preprocessing
├── chunker.py               # Smart text chunking
└── validators.py            # Text quality validation
```

**Key Classes:**

```python
class PDFExtractor:
    """Extract text from PDF documents."""

    def __init__(self, prefer_library: str = "pypdf"):
        self.primary_parser = pypdf
        self.fallback_parser = pdfplumber

    def extract_text(self, pdf_path: Path) -> str:
        """Extract all text from PDF."""

    def extract_with_structure(self, pdf_path: Path) -> List[Page]:
        """Extract text maintaining page structure."""

    def validate_extraction(self, text: str) -> QualityReport:
        """Check for OCR errors, missing content."""

class TextCleaner:
    """Clean and normalize extracted text."""

    def remove_artifacts(self, text: str) -> str:
        """Remove headers, footers, page numbers."""

    def normalize_whitespace(self, text: str) -> str:
        """Standardize spacing and line breaks."""

    def fix_hyphenation(self, text: str) -> str:
        """Join hyphenated words at line breaks."""

class SmartChunker:
    """Chunk text intelligently for Lang Extract."""

    def chunk_by_context(self,
                        text: str,
                        max_tokens: int = 8000,
                        overlap: int = 500) -> List[Chunk]:
        """Create overlapping chunks respecting context boundaries."""
```

**Design Decisions:**
- Use pypdf as primary (fast, reliable)
- Fall back to pdfplumber for complex layouts
- Maintain page-level structure for source grounding
- Smart chunking respects sentence/paragraph boundaries

---

### 2.2 Extraction Engine

**Responsibility:** Orchestrate Lang Extract for knowledge extraction

**Components:**
```
extraction/
├── __init__.py
├── extractor.py             # Main extraction logic
├── schemas.py               # All 13+ extraction schemas
├── examples.py              # ExampleData management
├── prompts.py               # Prompt templates
├── multi_pass.py            # Multi-pass orchestration
└── validators.py            # Extraction quality checks
```

**Key Classes:**

```python
class ExtractionEngine:
    """Main extraction orchestrator."""

    def __init__(self,
                 model_id: str = "gemini-2.5-flash",
                 api_key: str = None):
        self.model_id = model_id
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

    def extract_category(self,
                        document: str,
                        category: ExtractionCategory,
                        passes: int = 3) -> ExtractionResult:
        """Extract single category with multiple passes."""

    def extract_all_categories(self,
                              document: str,
                              categories: List[ExtractionCategory],
                              parallel: bool = True) -> Dict[str, ExtractionResult]:
        """Extract all categories with optimization."""

class ExtractionCategory:
    """Definition of an extraction category."""

    name: str
    description: str
    attributes: List[str]
    prompt_template: str
    examples: List[ExampleData]
    priority: int  # Order of extraction

class MultiPassExtractor:
    """Handle multi-pass extraction logic."""

    def run_passes(self,
                  document: str,
                  category: ExtractionCategory,
                  num_passes: int) -> ExtractionResult:
        """
        Pass 1: Broad sweep (70-80% recall)
        Pass 2: Targeted sweep (15-20% more)
        Pass 3: Final sweep (5-10% more)
        """
```

**Design Decisions:**
- Modular schema definitions (easy to add categories)
- Multi-pass extraction for completeness
- Rate limit handling built-in
- Support for parallel processing (respecting rate limits)
- Comprehensive logging for debugging

---

### 2.3 Storage Layer

**Responsibility:** Persist extracted data for querying

**Components:**
```
storage/
├── __init__.py
├── jsonl_store.py           # JSONL file operations
├── database.py              # SQLite operations
├── models.py                # Data models (Pydantic)
├── indexing.py              # Search indexing
└── migrations/              # DB schema migrations
```

**Database Schema:**

```sql
-- Core tables
CREATE TABLE concepts (
    id INTEGER PRIMARY KEY,
    term TEXT NOT NULL,
    definition TEXT,
    source_act TEXT,
    section_reference TEXT,
    page_number INTEGER,
    char_start INTEGER,
    char_end INTEGER,
    importance_level TEXT,
    created_at TIMESTAMP
);

CREATE TABLE deadlines (
    id INTEGER PRIMARY KEY,
    deadline_type TEXT NOT NULL,
    timeframe TEXT,
    calculation_method TEXT,
    triggering_event TEXT,
    required_action TEXT,
    responsible_party TEXT,
    statutory_reference TEXT,
    consequences_if_missed TEXT,
    page_number INTEGER,
    char_start INTEGER,
    char_end INTEGER,
    created_at TIMESTAMP
);

CREATE TABLE statutory_references (
    id INTEGER PRIMARY KEY,
    act_name TEXT NOT NULL,
    section_number TEXT,
    provision_text TEXT,
    practical_effect TEXT,
    page_number INTEGER,
    char_start INTEGER,
    char_end INTEGER,
    created_at TIMESTAMP
);

-- Relationship table
CREATE TABLE relationships (
    id INTEGER PRIMARY KEY,
    relationship_type TEXT,
    element_a_type TEXT,
    element_a_id INTEGER,
    element_b_type TEXT,
    element_b_id INTEGER,
    description TEXT,
    created_at TIMESTAMP
);

-- Quiz style patterns
CREATE TABLE question_patterns (
    id INTEGER PRIMARY KEY,
    exam_board TEXT,
    question_type TEXT,
    command_verb TEXT,
    marks INTEGER,
    difficulty TEXT,
    pattern_data JSON,
    created_at TIMESTAMP
);

-- User progress tracking
CREATE TABLE quiz_attempts (
    id INTEGER PRIMARY KEY,
    quiz_id TEXT,
    score REAL,
    total_questions INTEGER,
    topics JSON,
    completed_at TIMESTAMP
);

-- Indexes for fast querying
CREATE INDEX idx_concepts_term ON concepts(term);
CREATE INDEX idx_deadlines_type ON deadlines(deadline_type);
CREATE INDEX idx_statutory_act ON statutory_references(act_name);
CREATE INDEX idx_relationships_type ON relationships(relationship_type);
```

**Key Classes:**

```python
class KnowledgeStore:
    """Unified interface for knowledge base access."""

    def __init__(self, db_path: Path):
        self.db = Database(db_path)
        self.jsonl_path = db_path.parent / "extractions.jsonl"

    def save_extraction(self, result: ExtractionResult) -> None:
        """Save to both JSONL and SQLite."""

    def query_by_topic(self, topic: str) -> List[Dict]:
        """Find all extractions related to topic."""

    def query_by_category(self, category: str) -> List[Dict]:
        """Get all extractions of specific category."""

    def get_related(self, extraction_id: int) -> List[Dict]:
        """Find related extractions via relationships."""

    def search_full_text(self, query: str) -> List[Dict]:
        """Full-text search across all extractions."""
```

**Design Decisions:**
- Dual storage: JSONL for raw data, SQLite for queries
- Source grounding in every record (page, char position)
- Flexible schema supports all 13 categories
- Relationship table links extractions
- Indexes optimize common queries

---

### 2.4 Quiz System

**Responsibility:** Learn quiz styles and generate questions

**Components:**
```
quiz/
├── __init__.py
├── style_analyzer.py        # Analyze sample quizzes
├── style_templates.py       # Style template management
├── generator.py             # Quiz generation engine
├── question_types/          # Question type implementations
│   ├── multiple_choice.py
│   ├── true_false.py
│   ├── short_answer.py
│   ├── scenario.py
│   ├── calculation.py
│   └── fill_blank.py
├── distractor_engine.py     # Generate plausible wrong answers
└── validators.py            # Quiz quality validation
```

**Key Classes:**

```python
class QuizStyleAnalyzer:
    """Learn question patterns from sample papers."""

    def analyze_samples(self,
                       quiz_files: List[Path]) -> StyleTemplate:
        """Extract patterns using Lang Extract."""

    def synthesize_template(self,
                           patterns: List[Pattern]) -> StyleTemplate:
        """Create reusable style template."""

class StyleTemplate:
    """Encapsulates learned quiz style."""

    exam_board: str
    command_verbs: Dict[str, int]  # verb -> frequency
    question_types: Dict[str, float]  # type -> percentage
    mark_allocations: List[int]
    difficulty_distribution: Dict[str, float]
    language_patterns: List[str]
    distractor_strategies: List[str]

class QuizGenerator:
    """Generate quizzes matching learned style."""

    def __init__(self,
                 knowledge_base: KnowledgeStore,
                 style_template: StyleTemplate):
        self.kb = knowledge_base
        self.style = style_template

    def generate_quiz(self,
                     topic: str,
                     num_questions: int,
                     difficulty: str = "mixed") -> Quiz:
        """Generate complete quiz with model answers."""

    def generate_question(self,
                         q_type: str,
                         knowledge: Dict,
                         style: StyleTemplate) -> Question:
        """Generate single question."""

class DistractorEngine:
    """Generate plausible wrong answers for MCQs."""

    def generate_distractors(self,
                            correct_answer: str,
                            context: Dict,
                            strategy: str) -> List[str]:
        """Create 3 plausible wrong answers."""
```

**Design Decisions:**
- Lang Extract learns patterns (not hardcoded)
- Style templates are exam-board specific
- Each question type has dedicated implementation
- Distractor engine uses learned strategies
- Validation ensures style match >90%

---

### 2.5 CLI Interface

**Responsibility:** User interaction and workflow orchestration

**Components:**
```
cli/
├── __init__.py
├── main.py                  # Entry point, command routing
├── commands/                # Individual commands
│   ├── extract.py
│   ├── learn_style.py
│   ├── generate_quiz.py
│   ├── query.py
│   ├── validate.py
│   ├── stats.py
│   └── calculate_deadline.py
├── interactive/             # Interactive modes
│   ├── study_mode.py
│   └── quiz_mode.py
├── formatters.py            # Rich output formatting
└── utils.py                 # Shared utilities
```

**CLI Design:**

```bash
# Command structure
insolvency-study <command> [options]

# Commands
extract          - Extract knowledge from documents
learn-style      - Analyze sample quizzes
generate-quiz    - Create practice quizzes
query            - Search knowledge base
validate         - Check extraction/quiz quality
stats            - View statistics
calculate        - Calculate deadlines
study            - Interactive study mode
quiz             - Interactive quiz mode

# Examples
insolvency-study extract --input materials/book.pdf --categories concepts,deadlines
insolvency-study learn-style --input samples/*.pdf --exam-board "insolvency-2020"
insolvency-study generate-quiz --topic "administrator_duties" --num 10 --difficulty mixed
insolvency-study query "What are the duties of a trustee?"
insolvency-study calculate --event "bankruptcy" --date "2024-10-15" --deadline "statement_of_affairs"
```

**Design Decisions:**
- Click framework for robust CLI
- Rich library for beautiful terminal output
- Interactive modes for study/quiz-taking
- Progress bars for long operations
- Comprehensive help text

---

### 2.6 Deadline Calculator

**Responsibility:** Calculate and validate legal deadlines

**Components:**
```
deadline_calculator/
├── __init__.py
├── calculator.py            # Core calculation logic
├── rules.py                 # Calculation rules (clear days, etc.)
├── calendars.py             # Holiday calendars
└── validators.py            # Validation logic
```

**Key Classes:**

```python
class DeadlineCalculator:
    """Calculate legal deadlines with precision."""

    def calculate(self,
                 triggering_date: date,
                 timeframe: int,
                 method: CalculationMethod,
                 exclude_weekends: bool = True,
                 exclude_holidays: bool = True) -> DeadlineResult:
        """Calculate deadline with full justification."""

    def validate_compliance(self,
                           proposed_date: date,
                           requirement: Deadline) -> ValidationResult:
        """Check if date meets requirement."""

    def explain_calculation(self,
                          calculation: DeadlineResult) -> str:
        """Human-readable explanation of calculation."""

class CalculationMethod(Enum):
    BUSINESS_DAYS = "business_days"
    CALENDAR_DAYS = "calendar_days"
    CLEAR_DAYS = "clear_days"

class HolidayCalendar:
    """Manage federal/provincial holiday calendars."""

    def is_holiday(self, date: date) -> bool:
    def get_next_business_day(self, date: date) -> date:
```

---

## 3. Data Flow

### 3.1 Extraction Flow

```
1. User: `insolvency-study extract --input book.pdf`
2. CLI: Parse arguments, validate input
3. DocumentProcessor: Extract text from PDF
4. TextCleaner: Clean and normalize text
5. SmartChunker: Create overlapping chunks
6. ExtractionEngine: For each category:
   a. Load schema definition
   b. Load examples
   c. Build prompt
   d. Call Lang Extract (with rate limiting)
   e. Run multiple passes
   f. Merge and deduplicate results
7. KnowledgeStore: Save to JSONL + SQLite
8. HTMLGenerator: Create interactive visualization
9. CLI: Display summary and stats
```

### 3.2 Quiz Generation Flow

```
1. User: `insolvency-study generate-quiz --topic X --num 10`
2. CLI: Parse arguments
3. KnowledgeStore: Query relevant extractions for topic X
4. StyleTemplate: Load learned style for exam board
5. QuizGenerator: For each question:
   a. Select knowledge item
   b. Choose question type (based on style distribution)
   c. Generate question using Lang Extract
   d. Generate distractors (for MCQs)
   e. Create model answer with source refs
   f. Assign difficulty and marks
6. QuizValidator: Check style match
7. CLI: Output quiz (JSON, Markdown, or interactive)
```

---

## 4. Technology Stack

### 4.1 Core Dependencies

```python
# requirements.txt
langextract>=0.1.0           # Extraction framework
google-generativeai>=0.3.0   # Gemini API client

# PDF processing
pypdf>=4.0.0                 # Primary PDF parser
pdfplumber>=0.11.0           # Fallback PDF parser

# Data management
pydantic>=2.0.0              # Data validation
sqlalchemy>=2.0.0            # Database ORM
python-dotenv>=1.0.0         # Environment variables

# CLI
click>=8.0.0                 # CLI framework
rich>=13.0.0                 # Terminal formatting
questionary>=2.0.0           # Interactive prompts

# Configuration
pyyaml>=6.0.0                # YAML config files

# Utilities
python-dateutil>=2.8.0       # Date calculations
holidays>=0.35               # Holiday calendars
```

### 4.2 Development Dependencies

```python
# requirements-dev.txt
pytest>=7.4.0                # Testing
pytest-cov>=4.1.0            # Coverage
pytest-mock>=3.11.0          # Mocking
black>=23.0.0                # Code formatting
ruff>=0.1.0                  # Linting
mypy>=1.5.0                  # Type checking
```

---

## 5. Configuration Management

### 5.1 Configuration Files

```yaml
# config/extraction_config.yaml
extraction:
  model_id: "gemini-2.5-flash"
  default_passes: 3
  max_workers: 10
  chunk_size: 8000
  chunk_overlap: 500

categories:
  - name: concepts
    priority: 1
    passes: 3
  - name: deadlines
    priority: 2
    passes: 3
  - name: statutory_references
    priority: 1
    passes: 2
  # ... etc

rate_limits:
  free_tier_rpm: 15
  free_tier_tpm: 1000000
  paid_tier_rpm: 1000
  paid_tier_tpm: 4000000
```

```yaml
# config/quiz_config.yaml
quiz_generation:
  default_exam_board: "insolvency-2020"
  default_num_questions: 10
  default_difficulty: "mixed"

question_types:
  - name: multiple_choice
    weight: 0.4
  - name: short_answer
    weight: 0.3
  - name: scenario
    weight: 0.2
  - name: calculation
    weight: 0.1
```

```bash
# .env
GEMINI_API_KEY=your_api_key_here
OPENAI_API_KEY=optional_openai_key
DATABASE_PATH=data/database/knowledge_base.db
LOG_LEVEL=INFO
```

---

## 6. Testing Strategy

### 6.1 Unit Tests
- Test each module in isolation
- Mock external API calls
- Test edge cases (holidays, weekends, etc.)
- Target: 80%+ coverage

### 6.2 Integration Tests
- Test full extraction workflow
- Test quiz generation end-to-end
- Test database operations
- Use sample documents

### 6.3 Validation Tests
- Test deadline calculations against known examples
- Validate extraction quality on sample text
- Compare generated quizzes to style templates
- Manual quality review

---

## 7. Deployment

### 7.1 Project Structure

```
insolvency-knowledge/
├── src/
│   ├── __init__.py
│   ├── document_processor/
│   ├── extraction/
│   ├── storage/
│   ├── quiz/
│   ├── deadline_calculator/
│   └── cli/
├── config/
│   ├── extraction_config.yaml
│   ├── quiz_config.yaml
│   └── .env.example
├── data/
│   ├── input/
│   │   ├── study_materials/
│   │   └── sample_quizzes/
│   ├── output/
│   │   ├── knowledge_base/
│   │   ├── style_patterns/
│   │   └── generated_quizzes/
│   ├── examples/
│   │   ├── content_examples/
│   │   └── quiz_examples/
│   └── database/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── docs/
│   ├── 01-PRD-Product-Requirements-Document.md
│   ├── 02-Architecture-Document.md
│   ├── 03-Implementation-Plan.md
│   ├── 04-Schema-Specification.md
│   ├── 05-Example-Creation-Guide.md
│   └── 06-API-Cost-Management-Plan.md
├── requirements.txt
├── requirements-dev.txt
├── setup.py
├── pyproject.toml
└── .gitignore
```

---

## 8. Security Considerations

- API keys stored in .env (never committed)
- Input validation on all user input
- Rate limiting respected (avoid abuse)
- No execution of arbitrary code
- PDF parsing sandboxed
- Database uses parameterized queries (SQL injection prevention)

---

## 9. Performance Optimization

- Batch API calls where possible
- Cache extraction results
- Index database for fast queries
- Parallel processing (respecting rate limits)
- Smart chunking minimizes API calls
- Reuse Lang Extract context across categories

---

## 10. Monitoring & Logging

```python
# Logging configuration
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/insolvency_study.log'),
        logging.StreamHandler()
    ]
)

# Track metrics
- API calls made
- API cost incurred
- Extraction time per category
- Quiz generation time
- Error rates
- Quality scores
```

---

## Appendix: Key Design Principles

1. **Modularity:** Each component has single responsibility
2. **Testability:** Components designed for easy testing
3. **Extensibility:** Easy to add new categories, question types
4. **Source Grounding:** Every extraction links to source
5. **Cost Efficiency:** Optimize API usage
6. **User Experience:** Clear feedback and progress indication
7. **Data Integrity:** Validate at every layer
8. **Performance:** Async/parallel where appropriate
