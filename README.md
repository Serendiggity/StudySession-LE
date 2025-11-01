# Insolvency Study Assistant

AI-powered knowledge extraction and quiz generation system for insolvency exam preparation.

**Version:** 0.1.0
**Status:** Phase 1 - Setup Complete ✅
**Next:** Phase 2 - PDF Processing

---

## Quick Start (Phase 1 Setup)

### Prerequisites

- Python 3.10 or higher
- Git (for version control)
- Internet connection (for API calls)
- Your insolvency study PDF (291 pages)

### 1. Clone or Navigate to Project

```bash
cd /Users/jeffr/Local\ Project\ Repo/insolvency-knowledge
```

### 2. Run Setup Script

```bash
./setup.sh
```

This will:
- Create virtual environment
- Install all dependencies
- Create .env file from template
- Test CLI

### 3. Get Your Gemini API Key

1. Go to https://aistudio.google.com/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key

### 4. Configure Environment

Edit `.env` file and add your API key:

```bash
GEMINI_API_KEY=your_actual_api_key_here
```

### 5. Test API Connection

```bash
python3 test_api.py
```

If successful, you'll see:
```
✓ All tests passed! API is working correctly.
You're ready to proceed with Phase 2: PDF Processing!
```

---

## Manual Setup (if setup.sh doesn't work)

### Step 1: Create Virtual Environment

```bash
python3 -m venv venv
```

### Step 2: Activate Virtual Environment

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Environment

```bash
cp .env.example .env
# Edit .env and add your Gemini API key
```

### Step 5: Test

```bash
python3 src/cli/main.py test
python3 test_api.py
```

---

## Available Commands (Phase 1)

```bash
# Test CLI is working
python3 src/cli/main.py test

# Show system information
python3 src/cli/main.py info

# Show help
python3 src/cli/main.py --help

# Test API connection
python3 test_api.py
```

---

## Project Structure

```
insolvency-knowledge/
├── README.md                    # This file
├── setup.sh                     # Automated setup script
├── test_api.py                  # API connection test
├── requirements.txt             # Python dependencies
├── requirements-dev.txt         # Development dependencies
├── .env.example                 # Environment template
├── .env                         # Your environment (DO NOT COMMIT!)
├── .gitignore                   # Git ignore rules
│
├── docs/                        # Planning documents ✅
│   ├── README.md                # Document overview
│   ├── 01-PRD-Product-Requirements-Document.md
│   ├── 02-Architecture-Document.md
│   ├── 03-Implementation-Plan.md
│   ├── 04-Schema-Specification.md
│   ├── 05-Example-Creation-Guide.md
│   └── 06-API-Cost-Management-Plan.md
│
├── src/                         # Source code
│   ├── __init__.py
│   ├── cli/                     # CLI interface ✅
│   │   ├── __init__.py
│   │   └── main.py
│   ├── utils/                   # Utilities ✅
│   │   ├── __init__.py
│   │   └── logging_config.py
│   ├── document_processor/      # Phase 2
│   ├── extraction/              # Phase 3-4
│   ├── storage/                 # Phase 5
│   ├── quiz/                    # Phase 7-8
│   └── deadline_calculator/     # Phase 9
│
├── data/                        # Data directories
│   ├── input/
│   │   ├── study_materials/     # Put your PDF here
│   │   └── sample_quizzes/      # Put sample exams here
│   ├── output/
│   │   ├── knowledge_base/      # Extracted data
│   │   ├── style_patterns/      # Quiz styles
│   │   └── generated_quizzes/   # Generated quizzes
│   ├── examples/
│   │   ├── content_examples/    # Training examples (Phase 3)
│   │   └── quiz_examples/
│   └── database/                # SQLite database
│
├── tests/                       # Unit tests (Phase 11)
├── logs/                        # Application logs
├── config/                      # Configuration files
└── Materials/                   # Your existing study materials ✅
    └── Insolvency Administration - July 2020.pdf
```

---

## Phase Progress

| Phase | Status | Description |
|-------|--------|-------------|
| **Phase 1** | ✅ **Complete** | Project setup, environment, API connection |
| Phase 2 | ⏳ Next | PDF text extraction |
| Phase 3 | 📋 Planned | Create 80-100 training examples |
| Phase 4 | 📋 Planned | Build extraction engine |
| Phase 5 | 📋 Planned | Set up database |
| Phase 6 | 📋 Planned | Extract all 13 categories |
| Phase 7 | 📋 Planned | Learn quiz style from samples |
| Phase 8 | 📋 Planned | Build quiz generator |
| Phase 9 | 📋 Planned | Deadline calculator |
| Phase 10 | 📋 Planned | Complete CLI |
| Phase 11 | 📋 Planned | Testing & QA |
| Phase 12 | 📋 Planned | Documentation |

---

## Cost Tracking

| Item | Estimated | Actual |
|------|-----------|--------|
| Phase 1 | $0 | $0 |
| Total Project Budget | <$5 | TBD |

**Note:** You can complete this entire project for FREE using Gemini's free tier!

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'X'"

**Solution:** Make sure virtual environment is activated and dependencies are installed:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### "GEMINI_API_KEY not set"

**Solution:** Edit `.env` file and add your actual API key from https://aistudio.google.com/apikey

### "Permission denied: ./setup.sh"

**Solution:** Make script executable:
```bash
chmod +x setup.sh
```

### "API call failed"

**Possible causes:**
- Invalid API key - check `.env` file
- Rate limiting - wait 60 seconds and try again
- Network issues - check internet connection
- First run is slow - wait 10-20 seconds

---

## Next Steps (Phase 2)

Once Phase 1 is complete (API test passes), proceed to Phase 2:

1. **Read:** `docs/03-Implementation-Plan.md` - Phase 2 section
2. **Implement:** PDF text extraction module
3. **Extract:** Text from your 291-page PDF
4. **Validate:** Extraction quality

**Estimated time:** 2 days
**Estimated cost:** $0

---

## Documentation

All planning documents are in `docs/` directory:

- **Start here:** `docs/README.md` - Document overview
- **Phase guidance:** `docs/03-Implementation-Plan.md` - Detailed phase-by-phase plan
- **Technical specs:** `docs/02-Architecture-Document.md` - System architecture
- **Requirements:** `docs/01-PRD-Product-Requirements-Document.md` - Product requirements

---

## Support & Resources

### Official Documentation
- **Lang Extract:** https://github.com/google/langextract
- **Google Gemini:** https://ai.google.dev/
- **Click CLI:** https://click.palletsprojects.com/
- **Rich Terminal:** https://rich.readthedocs.io/

### Project Documentation
- All planning docs in `docs/` folder
- Implementation guidance in `docs/03-Implementation-Plan.md`
- Troubleshooting in each phase section

---

## License

Personal use for exam preparation.

---

## Author

Jeff R. - 2024

---

**Status Update:** Phase 4 Complete! ✅ FIRST SUCCESSFUL EXTRACTION!
**Achievement:** 411 concepts extracted from full 291-page PDF with source grounding
**Next:** Extract remaining categories (deadlines, statutory refs, etc.)
**Timeline:** Ahead of schedule - 3.5 phases in 1 day!

---

## 🎉 BREAKTHROUGH: First Successful Extraction (Nov 1, 2025)

**Extracted from full PDF:**
- ✅ 411 concepts
- ✅ 275 with definitions (67%)
- ✅ 100% source grounding
- ✅ Interactive HTML visualization generated

**View results:**
- JSONL: `data/output/knowledge_base/concepts.jsonl`
- HTML: `data/output/knowledge_base/concepts.html` ← Open in browser!

**Winning configuration:**
- Model: gemini-2.5-flash
- Examples: Minimal (1-3 attributes max)
- Single pass extraction
- Works on unlimited text size!
