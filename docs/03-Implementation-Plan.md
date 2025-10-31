# Implementation Plan
## Insolvency Study Assistant - Phase-by-Phase Guide

**Version:** 1.0
**Date:** 2025-10-28
**Status:** Approved

---

## Overview

This document provides a detailed, actionable implementation plan for building the Insolvency Study Assistant system. The plan is divided into 12 phases over 8-12 weeks.

### Quick Reference

| Phase | Focus | Duration | Cost |
|-------|-------|----------|------|
| 1 | Project Setup | 3 days | $0 |
| 2 | PDF Processing | 2 days | $0 |
| 3 | Schema & Examples | 3-4 days | $0.10-0.30 |
| 4 | Core Extraction | 7 days | $0.10-0.50 |
| 5 | Storage Layer | 4 days | $0 |
| 6 | Full Extraction | 7 days | $0-2 |
| 7 | Quiz Style Learning | 5 days | $0.10-0.20 |
| 8 | Quiz Generation | 9 days | $0.50-1 |
| 9 | Deadline Calculator | 3 days | $0 |
| 10 | CLI Commands | 7 days | $0 |
| 11 | Testing & QA | 4 days | $0.20-0.50 |
| 12 | Documentation | 4 days | $0 |
| **Total** | **MVP Complete** | **57-58 days** | **$1-5** |

---

## Phase 1: Project Setup (Week 1, Days 1-3)

### Objectives
- Set up development environment
- Verify API access
- Create basic project structure

### Tasks

#### Day 1: Environment Setup
1. **Create project directory structure**
   ```bash
   mkdir -p insolvency-knowledge/{src,tests,docs,config,data/{input,output,examples,database}}
   cd insolvency-knowledge
   ```

2. **Initialize git repository**
   ```bash
   git init
   git add .
   git commit -m "Initial project structure"
   ```

3. **Create Python virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```

4. **Create requirements.txt**
   ```
   langextract>=0.1.0
   google-generativeai>=0.3.0
   pypdf>=4.0.0
   pdfplumber>=0.11.0
   pydantic>=2.0.0
   python-dotenv>=1.0.0
   click>=8.0.0
   rich>=13.0.0
   pyyaml>=6.0.0
   python-dateutil>=2.8.0
   ```

5. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

#### Day 2: API Setup
1. **Create Google AI Studio account**
   - Go to https://aistudio.google.com
   - Sign in with Google account
   - Navigate to API keys section

2. **Generate Gemini API key**
   - Click "Create API key"
   - Copy key (keep secure!)

3. **Configure environment**
   ```bash
   # Create .env file
   echo "GEMINI_API_KEY=your_key_here" > .env
   echo "DATABASE_PATH=data/database/knowledge_base.db" >> .env
   echo "LOG_LEVEL=INFO" >> .env
   ```

4. **Test API connection**
   ```python
   # test_api.py
   import os
   from dotenv import load_dotenv
   import langextract as lx

   load_dotenv()

   # Simple test
   result = lx.extract(
       text_or_documents="The Bankruptcy and Insolvency Act (BIA) governs bankruptcy proceedings in Canada.",
       prompt_description="Extract the name of the Act mentioned.",
       examples=[],
       model_id="gemini-2.5-flash"
   )
   print("API test successful!")
   print(result)
   ```

#### Day 3: Basic CLI Setup
1. **Create CLI entry point**
   ```python
   # src/cli/main.py
   import click

   @click.group()
   @click.version_option(version="0.1.0")
   def cli():
       """Insolvency Study Assistant - Extract knowledge and generate quizzes."""
       pass

   @cli.command()
   def test():
       """Test that CLI is working."""
       click.echo("CLI is working! ✓")

   if __name__ == "__main__":
       cli()
   ```

2. **Set up logging**
   ```python
   # src/utils/logging_config.py
   import logging
   from pathlib import Path

   def setup_logging(log_level: str = "INFO"):
       log_dir = Path("logs")
       log_dir.mkdir(exist_ok=True)

       logging.basicConfig(
           level=getattr(logging, log_level),
           format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
           handlers=[
               logging.FileHandler('logs/insolvency_study.log'),
               logging.StreamHandler()
           ]
       )
   ```

3. **Test CLI**
   ```bash
   python src/cli/main.py test
   # Should output: CLI is working! ✓
   ```

### Deliverables
- ✅ Complete project structure
- ✅ Working virtual environment
- ✅ API connection verified
- ✅ Basic CLI scaffolding
- ✅ Logging configured

### Success Criteria
- Can run `python src/cli/main.py test` successfully
- API test connects to Gemini
- No errors in setup

### Time: 3 days
### Cost: $0

---

## Phase 2: PDF Processing (Week 1, Days 4-5)

### Objectives
- Extract text from 291-page insolvency PDF
- Validate extraction quality
- Prepare text for Lang Extract processing

### Tasks

#### Day 4: PDF Extraction
1. **Implement PDFExtractor class**
   ```python
   # src/document_processor/pdf_extractor.py
   from pathlib import Path
   from typing import List, Dict
   import pypdf
   import pdfplumber
   from dataclasses import dataclass

   @dataclass
   class Page:
       number: int
       text: str
       char_count: int

   class PDFExtractor:
       def __init__(self):
           self.logger = logging.getLogger(__name__)

       def extract_text(self, pdf_path: Path) -> str:
           """Extract all text from PDF using pypdf."""
           try:
               with open(pdf_path, 'rb') as file:
                   pdf = pypdf.PdfReader(file)
                   text = []
                   for page_num, page in enumerate(pdf.pages, 1):
                       page_text = page.extract_text()
                       text.append(page_text)
                       self.logger.info(f"Extracted page {page_num}/{len(pdf.pages)}")
                   return "\n\n".join(text)
           except Exception as e:
               self.logger.error(f"pypdf failed: {e}, trying pdfplumber...")
               return self._extract_with_pdfplumber(pdf_path)

       def _extract_with_pdfplumber(self, pdf_path: Path) -> str:
           """Fallback extraction using pdfplumber."""
           with pdfplumber.open(pdf_path) as pdf:
               text = [page.extract_text() for page in pdf.pages]
               return "\n\n".join(text)

       def extract_with_structure(self, pdf_path: Path) -> List[Page]:
           """Extract maintaining page structure."""
           pages = []
           with open(pdf_path, 'rb') as file:
               pdf = pypdf.PdfReader(file)
               for page_num, page in enumerate(pdf.pages, 1):
                   text = page.extract_text()
                   pages.append(Page(
                       number=page_num,
                       text=text,
                       char_count=len(text)
                   ))
           return pages
   ```

2. **Extract your PDF**
   ```python
   extractor = PDFExtractor()
   text = extractor.extract_text("Materials/Insolvency Administration - July 2020.pdf")

   # Save for reuse
   with open("data/input/study_materials/insolvency_admin_text.txt", "w") as f:
       f.write(text)
   ```

3. **Validate extraction**
   - Check total character count (~1.2M characters for 291 pages)
   - Manually review first 10 pages for quality
   - Check for OCR errors or garbled text
   - Verify page breaks are preserved

#### Day 5: Text Cleaning & Chunking
1. **Implement TextCleaner**
   ```python
   # src/document_processor/text_cleaner.py
   import re

   class TextCleaner:
       def clean(self, text: str) -> str:
           """Full cleaning pipeline."""
           text = self.remove_artifacts(text)
           text = self.normalize_whitespace(text)
           text = self.fix_hyphenation(text)
           return text

       def remove_artifacts(self, text: str) -> str:
           """Remove headers, footers, page numbers."""
           # Remove page numbers (common patterns)
           text = re.sub(r'\n\d+\s*\n', '\n', text)
           # Remove multiple dashes (section breaks)
           text = re.sub(r'-{3,}', '', text)
           return text

       def normalize_whitespace(self, text: str) -> str:
           """Standardize spacing."""
           # Replace multiple spaces with single
           text = re.sub(r' +', ' ', text)
           # Standardize line breaks (max 2 consecutive)
           text = re.sub(r'\n{3,}', '\n\n', text)
           return text

       def fix_hyphenation(self, text: str) -> str:
           """Join hyphenated words at line breaks."""
           # Match word-\nword pattern
           text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
           return text
   ```

2. **Implement SmartChunker**
   ```python
   # src/document_processor/chunker.py
   from typing import List
   from dataclasses import dataclass

   @dataclass
   class Chunk:
       text: str
       start_char: int
       end_char: int
       token_count: int

   class SmartChunker:
       def __init__(self, max_tokens: int = 8000, overlap: int = 500):
           self.max_tokens = max_tokens
           self.overlap = overlap

       def chunk_text(self, text: str) -> List[Chunk]:
           """Create overlapping chunks respecting boundaries."""
           # Simple token estimation: ~4 chars per token
           max_chars = self.max_tokens * 4
           overlap_chars = self.overlap * 4

           chunks = []
           start = 0

           while start < len(text):
               end = start + max_chars

               # Find good break point (paragraph, sentence)
               if end < len(text):
                   # Look for paragraph break
                   para_break = text.rfind('\n\n', start, end)
                   if para_break > start + max_chars // 2:
                       end = para_break
                   else:
                       # Look for sentence break
                       sent_break = text.rfind('. ', start, end)
                       if sent_break > start + max_chars // 2:
                           end = sent_break + 1

               chunk_text = text[start:end]
               chunks.append(Chunk(
                   text=chunk_text,
                   start_char=start,
                   end_char=end,
                   token_count=len(chunk_text) // 4
               ))

               start = end - overlap_chars

           return chunks
   ```

3. **Add CLI command**
   ```python
   @cli.command()
   @click.option('--input', type=click.Path(exists=True), required=True)
   @click.option('--output', type=click.Path(), default="data/input/study_materials/extracted_text.txt")
   def extract_text(input, output):
       """Extract text from PDF."""
       from document_processor.pdf_extractor import PDFExtractor
       from document_processor.text_cleaner import TextCleaner

       extractor = PDFExtractor()
       cleaner = TextCleaner()

       click.echo(f"Extracting text from {input}...")
       text = extractor.extract_text(Path(input))

       click.echo("Cleaning text...")
       text = cleaner.clean(text)

       Path(output).write_text(text)
       click.echo(f"✓ Extracted {len(text):,} characters to {output}")
   ```

### Deliverables
- ✅ Working PDF extraction module
- ✅ Clean text extracted from 291-page PDF
- ✅ Chunking logic tested
- ✅ CLI command: `extract-text`

### Success Criteria
- Text extraction completes without errors
- Character count is reasonable (~1.2M chars)
- Manual review shows good quality
- No major OCR issues

### Time: 2 days
### Cost: $0

---

## Phase 3: Schema Design & Examples (Week 1-2, Days 6-9) - UPDATED!

### Objectives
- Define all 13 extraction schemas
- Create 40-65 high-quality examples (3-5 per category)
- Write extraction prompts
- **Test iteratively** after each category

### This is THE MOST IMPORTANT phase - quality here determines overall success

**UPDATED BASED ON LANG EXTRACT DOCS:**
> "Zero examples work; 3-5 high-quality ones usually lift accuracy and consistency."

**New Strategy:** Quality over quantity! 3-5 excellent examples per category, test immediately, iterate based on results.

### Tasks

#### Day 6: Schema Definition
1. **Create schema definitions** (see Schema Specification doc for details)
2. **Implement ExtractionCategory dataclass**
   ```python
   # src/extraction/schemas.py
   from dataclasses import dataclass
   from typing import List
   import langextract as lx

   @dataclass
   class ExtractionCategory:
       name: str
       description: str
       attributes: List[str]
       prompt_template: str
       examples: List[lx.data.ExampleData]
       priority: int
       passes: int = 3
   ```

#### Days 7-9: Example Creation (REVISED - Much Faster!)

**Critical Rules to Follow:**
- ✅ Use EXACT text from source (no paraphrasing!)
- ✅ No overlapping text spans
- ✅ Extract in order of appearance
- ✅ Use attributes for grouping related items

**Day 7: Critical Foundation (Test After Each Category!)**

1. **Concepts** (3-5 examples) → **Test immediately!**
   - Find clear definitions in your PDF
   - Include term, definition, source act, section reference
   - Examples: "Administration", "Proposal", "Secured Creditor"
   - **Test on 10-20 pages before proceeding**

2. **Statutory References** (3-5 examples) → **Test immediately!**
   - BIA sections with full citations
   - Include practical effect
   - Examples: BIA s. 43(1), BIA s. 65.13
   - **Test on sample text**

3. **Deadlines** (3-5 examples) → **Test immediately!**
   - MUST include calculation method
   - Business days vs. calendar days examples
   - Include triggering event
   - Examples: "10 days notice before meeting", "30 days for Statement of Affairs"
   - **Critical: Test deadline extraction accuracy**

**Day 8: Core Knowledge (Test After Each!)**

4. **Role Obligations** (4 examples) → **Test!**
   - Duties by role (Trustee, Receiver, etc.)
   - Include when obligation arises
   - Examples: Trustee's duty to notify OSB

5. **Principles** (4 examples) → **Test!**
   - Legal principles and rules
   - Include statutory basis
   - Examples: Fiduciary duty principles

6. **Procedures** (4 examples) → **Test!**
   - Step-by-step processes
   - Include prerequisites
   - Examples: Filing for bankruptcy procedure

**Day 9: Supporting & Contextual Categories (Batch Test)**

7-13. **Remaining 7 categories** (3 examples each):
   - Document requirements (3)
   - Event triggers (3)
   - Communication requirements (3)
   - Relationships (3)
   - Cases (3)
   - Requirements (3)
   - Exceptions (3)
   - **Test all 7 categories together at end of day**

**Example format:**
```python
concept_example_1 = lx.data.ExampleData(
    text="""
    Administration is a procedure under the Insolvency Act 1986 whereby
    a licensed insolvency practitioner (administrator) is appointed to
    manage the affairs, business, and property of a company. The primary
    purpose is to rescue the company as a going concern.
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="concept",
            extraction_text="Administration",
            attributes={
                "term": "Administration",
                "definition": "A procedure whereby a licensed insolvency practitioner is appointed to manage the affairs of a company",
                "source_act": "Insolvency Act 1986",
                "context": "rescue procedure",
                "importance_level": "high"
            }
        )
    ]
)
```

**Save examples:**
```python
# data/examples/content_examples/concepts_examples.py
# data/examples/content_examples/deadlines_examples.py
# etc.
```

### Deliverables
- ✅ Complete schemas.py with all 13 categories
- ✅ 40-65 high-quality examples (3-5 per category) - **REVISED!**
- ✅ Extraction prompts documented
- ✅ examples/ directory populated
- ✅ Test results from each category showing 80%+ accuracy

### Success Criteria
- Each category has 3-5 representative examples (**Updated - quality over quantity!**)
- Examples follow Lang Extract rules (exact text, no overlap, order matters)
- Deadline examples include calculation methods
- All examples formatted correctly for Lang Extract
- Tested after each category with 80%+ initial accuracy

### Time: 3-4 days (MUCH faster than original 5-10 day estimate!)
### Cost: ~$0.10-0.30 (testing with small samples)

---

## Phase 4: Core Extraction Engine (Week 2-3, Days 11-17)

### Objectives
- Build extraction engine
- Run first successful extraction
- Validate approach

### Tasks

#### Days 11-12: Engine Implementation
1. **Implement ExtractionEngine**
   ```python
   # src/extraction/extractor.py
   import langextract as lx
   from typing import List, Dict
   import logging

   class ExtractionEngine:
       def __init__(self, model_id: str = "gemini-2.5-flash", api_key: str = None):
           self.model_id = model_id
           self.api_key = api_key or os.getenv("GEMINI_API_KEY")
           self.logger = logging.getLogger(__name__)

       def extract_category(self,
                           text: str,
                           category: ExtractionCategory,
                           passes: int = 3) -> lx.data.AnnotatedDocument:
           """Extract single category with multiple passes."""
           self.logger.info(f"Extracting category: {category.name} with {passes} passes")

           result = lx.extract(
               text_or_documents=text,
               prompt_description=category.prompt_template,
               examples=category.examples,
               model_id=self.model_id,
               extraction_passes=passes,
               max_workers=10  # Respects rate limits
           )

           self.logger.info(f"Extracted {len(result.extractions)} items")
           return result
   ```

2. **Implement rate limit handling**
   - Lang Extract handles this automatically!
   - Just set max_workers appropriately

#### Days 13-15: First Extraction Test
1. **Test with concepts category**
   ```python
   # Load your cleaned text
   text = Path("data/input/study_materials/extracted_text.txt").read_text()

   # Load examples
   from examples.content_examples.concepts_examples import concept_examples

   # Create category
   concepts_category = ExtractionCategory(
       name="concepts",
       description="Key terms and definitions",
       attributes=["term", "definition", "source_act", "importance_level"],
       prompt_template="Extract key concepts and their definitions...",
       examples=concept_examples,
       priority=1,
       passes=3
   )

   # Extract!
   engine = ExtractionEngine()
   result = engine.extract_category(text, concepts_category)

   # Save result
   lx.io.save_annotated_documents([result], output_name="concepts", output_dir="data/output/knowledge_base")
   ```

2. **Review results**
   - Check extraction count (expect 100-200 concepts from 291 pages)
   - Verify source grounding (page numbers present)
   - Look for quality issues

3. **Generate HTML visualization**
   ```python
   html = lx.visualize("data/output/knowledge_base/concepts.jsonl")
   Path("data/output/knowledge_base/concepts.html").write_text(html)
   # Open in browser to review
   ```

#### Days 16-17: Refinement
1. **Identify gaps**
   - What concepts were missed?
   - Any false positives?

2. **Refine examples/prompts**
   - Add examples for missed patterns
   - Clarify prompt if needed

3. **Re-run extraction**
   - Should see improvement in recall

### Deliverables
- ✅ Working ExtractionEngine
- ✅ Successful extraction of concepts category
- ✅ Progress tracking and logging
- ✅ CLI command: `extract --category concepts`
- ✅ HTML visualization

### Success Criteria
- Extract 80-100+ concepts from PDF
- All extractions have source grounding
- HTML visualization works smoothly
- <5% obvious errors on manual review

### Time: 7 days
### Cost: ~$0.10-0.50 (testing with one category)

---

## Phase 5: Storage Layer (Week 3, Days 18-21)

### Objectives
- Build database to store extractions
- Enable querying by multiple dimensions

### Tasks

#### Days 18-19: Database Schema
1. **Create SQLite schema** (see Architecture doc for full schema)
2. **Implement migrations**
   ```python
   # src/storage/migrations/001_initial_schema.sql
   CREATE TABLE concepts (...);
   CREATE TABLE deadlines (...);
   -- etc
   ```

3. **Create Database class**
   ```python
   # src/storage/database.py
   from sqlalchemy import create_engine, MetaData
   from sqlalchemy.orm import sessionmaker

   class Database:
       def __init__(self, db_path: Path):
           self.engine = create_engine(f'sqlite:///{db_path}')
           self.SessionLocal = sessionmaker(bind=self.engine)
           self.metadata = MetaData()

       def create_tables(self):
           """Run migrations."""
           with open('src/storage/migrations/001_initial_schema.sql') as f:
               self.engine.execute(f.read())
   ```

#### Days 20-21: KnowledgeStore Implementation
1. **Implement unified storage interface**
   ```python
   # src/storage/knowledge_store.py
   class KnowledgeStore:
       def __init__(self, db_path: Path):
           self.db = Database(db_path)
           self.jsonl_dir = db_path.parent / "jsonl"

       def save_extraction(self, result: lx.data.AnnotatedDocument, category: str):
           """Save to both JSONL and SQLite."""
           # Save JSONL
           lx.io.save_annotated_documents([result],
                                         output_name=category,
                                         output_dir=str(self.jsonl_dir))

           # Save to SQLite
           with self.db.SessionLocal() as session:
               for extraction in result.extractions:
                   if category == "concepts":
                       record = Concept(
                           term=extraction.attributes["term"],
                           definition=extraction.attributes["definition"],
                           # ... etc
                       )
                       session.add(record)
               session.commit()

       def query_by_topic(self, topic: str) -> List[Dict]:
           """Find extractions related to topic."""
           pass

       def query_by_category(self, category: str) -> List[Dict]:
           """Get all extractions of category."""
           pass
   ```

2. **Test storage**
   - Save concepts from Phase 4
   - Query back
   - Verify data integrity

### Deliverables
- ✅ Working SQLite database
- ✅ KnowledgeStore interface
- ✅ Query functionality
- ✅ Data persisted from Phase 4

### Success Criteria
- Can save and retrieve extractions
- Queries return correct results
- No data loss
- Indexes improve query speed

### Time: 4 days
### Cost: $0

---

## Phase 6: Comprehensive Extraction (Week 3-4, Days 22-28)

### Objectives
- Extract all 13 categories from your PDF
- Build complete knowledge base

### Tasks

#### Days 22-24: Foundational Categories
1. **Extract: concepts, statutory_references, principles**
   ```bash
   insolvency-study extract --input materials/book.pdf --categories concepts,statutory_references,principles --passes 3
   ```

2. **Review results**
   - Use HTML visualization
   - Check quality metrics
   - Validate source grounding

#### Days 25-26: Deadline & Procedure Categories
1. **Extract: deadlines, procedures, role_obligations**
2. **Special attention to deadlines**
   - Verify calculation methods captured
   - Check business vs. calendar days distinction

#### Day 27: Relationship Categories
1. **Extract: document_requirements, event_triggers, communication_requirements, relationships**
2. **Build dependency graphs**

#### Day 28: Supporting Categories
1. **Extract: cases, requirements, exceptions, pitfalls**
2. **Final quality review**
   - Random sample of 50 extractions
   - Verify source grounding
   - Check for obvious errors
   - Measure recall (aim for 90%+)

### Deliverables
- ✅ Complete knowledge base (all 13 categories)
- ✅ 800-1200 structured extractions
- ✅ Interactive HTML visualizations
- ✅ Quality review documentation
- ✅ knowledge_base.db populated

### Success Criteria
- 90%+ recall on manual validation sample
- All extractions have source grounding
- Database queries work efficiently
- HTML visualizations render correctly

### Time: 7 days
### Cost: $0-2 (using free tier strategically)

---

## Phase 7: Quiz Style Learning (Week 4-5, Days 29-33)

### Objectives
- Learn question patterns from sample exam papers
- Create style templates

### Tasks

#### Day 29: Sample Paper Collection
1. **Gather 3-5 sample exam papers**
2. **Convert to text if needed**
3. **Organize in data/input/sample_quizzes/**

#### Days 30-32: Style Analysis
1. **Define quiz style schema** (see Schema Specification doc)
2. **Create quiz examples**
   - 5-10 examples showing question patterns
   - Include MCQ, essay, short answer examples
   - Show distractor patterns

3. **Run style analysis**
   ```python
   analyzer = QuizStyleAnalyzer()
   style = analyzer.analyze_samples([
       "data/input/sample_quizzes/exam_2019.pdf",
       "data/input/sample_quizzes/exam_2020.pdf",
       "data/input/sample_quizzes/exam_2021.pdf"
   ])
   ```

#### Day 33: Template Generation
1. **Synthesize patterns**
   - Command verb frequencies
   - Question type distribution
   - Mark allocation patterns
   - Distractor strategies

2. **Save style template**
   ```python
   style.save("data/output/style_patterns/insolvency-2020.json")
   ```

### Deliverables
- ✅ QuizStyleAnalyzer module
- ✅ Style template for insolvency exam board
- ✅ Command verb frequency analysis
- ✅ Distractor strategy documentation
- ✅ CLI command: `learn-style`

### Success Criteria
- Successfully extract patterns from 3+ papers
- Style template captures key patterns
- Command verbs identified
- Question type distribution calculated

### Time: 5 days
### Cost: ~$0.10-0.20

---

## Phase 8: Quiz Generation Engine (Week 5-6, Days 34-42)

### Objectives
- Build quiz generator
- Implement all question types
- Generate sample quizzes

### Tasks

#### Days 34-36: Generator Core
1. **Implement QuizGenerator class**
2. **Implement question type selection logic**
3. **Integrate knowledge base and style template**

#### Days 37-40: Question Type Implementations
1. **Day 37: Multiple Choice Generator**
   - Generate questions
   - Implement DistractorEngine
   - Test with various topics

2. **Day 38: True/False & Short Answer**
   - Implement generators
   - Add explanation generation

3. **Day 39: Scenario & Calculation**
   - Scenario-based questions
   - Deadline calculation questions

4. **Day 40: Fill-in-Blank & Polish**
   - Final question type
   - Polish all generators

#### Days 41-42: Testing & Validation
1. **Generate sample quizzes**
   ```bash
   insolvency-study generate-quiz --topic "administrator_duties" --num 10 --difficulty mixed
   ```

2. **Validate style match**
   - Compare to sample papers
   - Aim for >90% style similarity

3. **Manual quality review**
   - Are questions realistic?
   - Are distractors plausible?
   - Are model answers correct?

### Deliverables
- ✅ Working QuizGenerator
- ✅ All 6 question types implemented
- ✅ Distractor generation working
- ✅ 5-10 sample quizzes generated
- ✅ CLI command: `generate-quiz`

### Success Criteria
- Generate quizzes on any topic
- Questions match exam style (>90%)
- Distractors are plausible
- Model answers have source references
- Difficulty calibration works

### Time: 9 days
### Cost: ~$0.50-1.00

---

## Phase 9: Deadline Calculator (Week 6, Days 43-45)

### Objectives
- Build deadline calculator
- Handle all calculation methods
- Validate against known examples

### Tasks

#### Day 43: Core Calculator
1. **Implement DeadlineCalculator class**
2. **Implement CalculationMethod enum**
3. **Handle business days, calendar days, clear days**

#### Day 44: Holiday Calendar
1. **Implement HolidayCalendar**
2. **Add Canadian federal holidays**
3. **Handle weekend extensions**

#### Day 45: Testing & CLI
1. **Create 20+ test cases**
   - Known deadline calculations
   - Edge cases (holidays, weekends)
   - Validate 100% accuracy

2. **Add CLI command**
   ```bash
   insolvency-study calculate --event "bankruptcy" --date "2024-10-15" --deadline "30 days"
   ```

### Deliverables
- ✅ Working DeadlineCalculator
- ✅ All calculation methods implemented
- ✅ Test suite (20+ cases)
- ✅ CLI command: `calculate`

### Success Criteria
- All test cases pass
- Handles edge cases correctly
- Explanations are clear

### Time: 3 days
### Cost: $0

---

## Phase 10: CLI Commands (Week 6-7, Days 46-52)

### Objectives
- Polish all CLI commands
- Add interactive modes
- Implement export functionality

### Tasks

#### Days 46-48: Command Implementation
1. **Implement `query` command**
   - Search knowledge base
   - Filter by category, topic
   - Display results

2. **Implement `validate` command**
   - Check extraction quality
   - Validate quiz style match
   - Generate reports

3. **Implement `stats` command**
   - Show extraction counts
   - Display coverage metrics
   - API usage stats

#### Days 49-50: Interactive Modes
1. **Interactive study mode**
   - Browse concepts
   - View source references
   - Navigate by topic

2. **Interactive quiz mode**
   - Take quizzes in terminal
   - Immediate feedback
   - Score tracking

#### Days 51-52: Export & Polish
1. **Export functionality**
   - JSON export
   - Markdown export
   - CSV export for flashcards

2. **Polish all commands**
   - Rich formatting
   - Progress bars
   - Better error messages
   - Comprehensive help text

### Deliverables
- ✅ Complete CLI (8+ commands)
- ✅ Interactive modes
- ✅ Export functionality
- ✅ Beautiful terminal output

### Success Criteria
- All commands work smoothly
- User experience is intuitive
- Help text is comprehensive
- Export formats are correct

### Time: 7 days
### Cost: $0

---

## Phase 11: Testing & QA (Week 7-8, Days 53-56)

### Objectives
- Comprehensive testing
- Quality assurance
- Performance optimization

### Tasks

#### Day 53: Unit Tests
1. **Write unit tests**
   - Test each module
   - Mock API calls
   - Edge cases

2. **Run tests**
   ```bash
   pytest tests/unit/ --cov=src --cov-report=html
   ```

#### Day 54: Integration Tests
1. **End-to-end workflows**
   - Extraction pipeline
   - Quiz generation
   - All CLI commands

#### Day 55: Manual QA
1. **Quality validation**
   - Random sample of 100 extractions
   - Verify source grounding
   - Check for errors

2. **Quiz quality check**
   - Generate 10 quizzes
   - Manual review
   - Style match validation

#### Day 56: Performance
1. **Profile code**
2. **Optimize bottlenecks**
3. **Fix bugs found during testing**

### Deliverables
- ✅ Test suite (80%+ coverage)
- ✅ All tests passing
- ✅ Quality metrics documented
- ✅ Bug fixes
- ✅ Performance optimizations

### Success Criteria
- Tests pass
- 90%+ accuracy on validation
- No critical bugs
- Performance acceptable

### Time: 4 days
### Cost: ~$0.20-0.50

---

## Phase 12: Documentation (Week 8, Days 57-60)

### Objectives
- Complete documentation
- User guides
- Developer guides

### Tasks

#### Day 57: User Documentation
1. **Write README.md**
   - Project overview
   - Quick installation
   - Basic usage

2. **Write QUICKSTART.md**
   - 5-minute getting started
   - First extraction
   - First quiz

#### Day 58: Complete User Guide
1. **Write USER_GUIDE.md**
   - All commands documented
   - Example workflows
   - Troubleshooting

#### Day 59: Developer Documentation
1. **Write DEVELOPER_GUIDE.md**
   - Architecture overview
   - Adding new categories
   - Adding question types
   - API reference

#### Day 60: Final Polish
1. **FAQ**
2. **Troubleshooting guide**
3. **Final review of all docs**

### Deliverables
- ✅ Complete documentation package
- ✅ README
- ✅ User guide
- ✅ Developer guide
- ✅ FAQ

### Success Criteria
- Documentation is comprehensive
- Examples are clear
- New users can get started easily

### Time: 4 days
### Cost: $0

---

## MVP Launch (End of Week 8)

### Final Checklist

- ✅ Knowledge base extracted from 291-page PDF
- ✅ 90%+ recall on core categories
- ✅ All extractions source-grounded
- ✅ Style templates from sample papers
- ✅ Quiz generation works (6 types)
- ✅ All CLI commands functional
- ✅ Deadline calculator accurate
- ✅ Documentation complete
- ✅ Total cost <$5
- ✅ Ready for exam preparation!

### Success Metrics

- Can study from knowledge base
- Can generate realistic quizzes
- Can calculate deadlines correctly
- System is reliable and usable
- **Ultimate goal: Pass the exam!**

---

## Total Project Summary

### Timeline
- **Phases 1-12:** 60 days (8 weeks)
- **Compressed schedule:** 42 days (6 weeks) if full-time
- **Extended schedule:** 84 days (12 weeks) if part-time

### Cost Breakdown
- **Phase 1-3:** $0 (setup and design)
- **Phase 4:** ~$0.50 (initial extraction testing)
- **Phase 6:** ~$1.50 (comprehensive extraction)
- **Phase 7:** ~$0.20 (style learning)
- **Phase 8:** ~$1.00 (quiz generation)
- **Phase 11:** ~$0.50 (testing)
- **Total:** **$3.70** (using free tier strategically)

### What You Get
- Complete knowledge base
- Quiz generation system
- Interactive study tools
- Deadline calculator
- CLI interface
- Full documentation
- **A powerful exam prep system!**

---

## Next Steps

1. ✅ **Review all planning documents**
2. **Get API key from Google AI Studio**
3. **Start Phase 1: Project Setup**
4. **Extract your PDF (Phase 2)**
5. **Begin creating examples (Phase 3)**

**Ready to build this system? Let's get started with Phase 1!**
