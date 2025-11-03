# Adding OSB Directives to Knowledge Base

## Priority Directives (From Quiz Error Analysis)

Based on quiz validation, these directives are critical for exam accuracy:

### High Priority (Resolve Current Errors)

**1. Directive 6R7 - Assessment of Individual Debtor**
- **Link:** https://ised-isde.canada.ca/site/office-superintendent-bankruptcy/en/licensed-insolvency-trustees/directives-and-circulars/directive-no-6r7assessment-individual-debtor
- **Why:** Answers Q2 (Assessment Certificate acknowledgement), Q8 (who discusses rights)
- **Quiz errors:** 2 questions failed

**2. Directive 16R - Statement of Affairs Preparation**
- **Link:** https://ised-isde.canada.ca/site/office-superintendent-bankruptcy/en/directive-no-16r-pre-1992
- **Why:** Answers Q9 (jointly owned assets), Q13 (under-secured liabilities)
- **Quiz errors:** 2 questions failed

### Important (Referenced in Study Material)

**3. Directive 4 - Delegation of Tasks**
- **Why:** Q11 (who can be delegated assessment tasks)
- **Referenced in:** Study Material sections

**4. Directive 5 - Estate Funds and Banking**
- **Why:** Estate administration questions
- **Referenced in:** Study Material

**5. Surplus Income Directive**
- **Why:** Q6 (surplus income calculations)
- **Referenced in:** Study Material

**6. Directive 17R**
- **Link:** https://ised-isde.canada.ca/site/office-superintendent-bankruptcy/en/directive-no-17-coming-force-september-18-2009
- **Referenced in:** Study Material

**7. Directive 32R - Electronic Recordkeeping**
- **Link:** https://ised-isde.canada.ca/site/office-superintendent-bankruptcy/en/directive-no-32r-trustee-electronic-recordkeeping
- **Referenced in:** Study Material

---

## How to Add Directives to Your System

### Step 1: Download Directives

**Option A: Manual Download (Recommended)**
1. Visit each link above
2. Save as PDF or copy text to .txt file
3. Place in: `data/input/osb_directives/`
4. Name format: `directive_6r7_assessment.pdf` or `.txt`

**Option B: Browser Extension**
If canada.ca site has rate limiting:
- Use browser to download
- Right-click → "Save as PDF" or copy text

### Step 2: Extract Text (If PDF)

```bash
# If you have PDFs
cd data/input/osb_directives
python3 -c "
import pypdf
from pathlib import Path

for pdf in Path('.').glob('*.pdf'):
    reader = pypdf.PdfReader(str(pdf))
    text = ''
    for page in reader.pages:
        text += page.extract_text() + '\n'

    output = pdf.with_suffix('.txt')
    with open(output, 'w') as f:
        f.write(text)

    print(f'✓ Extracted {pdf.name} → {output.name}')
"
```

### Step 3: Run Structural Extraction

**Directives are structured documents like statutes. Use structural approach:**

```bash
# Parse directive structure
python3 src/utils/directive_structure_parser.py \
  --input data/input/osb_directives/directive_6r7_assessment.txt \
  --output data/output/directive_6r7_structure.json

# Load into database
python3 scripts/load_directive.py \
  --directive "Directive 6R7" \
  --structure data/output/directive_6r7_structure.json \
  --source-id 3
```

### Step 4: Verify Against Quiz Errors

```bash
# Test Q2: Assessment acknowledgement
sqlite3 data/output/insolvency_knowledge.db "
SELECT section_number, full_text
FROM directive_sections
WHERE directive_name = 'Directive 6R7'
  AND full_text LIKE '%acknowledgement%'
LIMIT 5;
"

# Test Q9: Jointly owned assets
sqlite3 data/output/insolvency_knowledge.db "
SELECT section_number, full_text
FROM directive_sections
WHERE directive_name = 'Directive 16R'
  AND full_text LIKE '%jointly owned%'
LIMIT 5;
"
```

### Step 5: Re-Test Quiz 2

After adding directives, re-run quiz questions and validate:
- Should resolve Q2, Q8 (Directive 6R)
- Should resolve Q9, Q13 (Directive 16R)
- Expected accuracy improvement: 67% → 93% (14/15)

---

## Database Schema for Directives

**Similar to BIA structural approach:**

```sql
CREATE TABLE osb_directives (
    directive_id INTEGER PRIMARY KEY,
    directive_number TEXT UNIQUE,  -- "6R7", "16R", etc.
    directive_name TEXT,
    effective_date DATE,
    full_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE directive_sections (
    section_id INTEGER PRIMARY KEY,
    directive_id INTEGER,
    section_number TEXT,
    section_title TEXT,
    full_text TEXT NOT NULL,
    FOREIGN KEY (directive_id) REFERENCES osb_directives(directive_id)
);

CREATE VIRTUAL TABLE directive_sections_fts USING fts5(
    section_number,
    section_title,
    full_text,
    content='directive_sections'
);
```

---

## Expected Quiz Accuracy After Adding Directives

| Quiz | Current Accuracy | After Directives | Notes |
|------|------------------|------------------|-------|
| Quiz 1 | 100% (10/10) | 100% | No directive questions |
| Quiz 2 | 67% (10/15) | ~93% (14/15) | 4 directive errors resolved |

**Remaining gap:** BIA s. 68, 173 (need better section coverage)

---

## Next Session Plan

**Session 3: Add OSB Directives**
1. Download Directives 6R7, 16R, 4, 5, Surplus Income
2. Create directive_structure_parser.py (similar to bia_structure_parser.py)
3. Load into database as structured documents
4. Re-test Quiz 2
5. Validate 93%+ accuracy

**Total time estimate:** 2-3 hours

---

## Manual Download Checklist

- [ ] Directive 6R7 (Assessment)
- [ ] Directive 16R (Statement of Affairs)
- [ ] Directive 4 (Delegation)
- [ ] Directive 5 (Estate Funds)
- [ ] Directive 17R
- [ ] Directive 32R (Electronic Recordkeeping)
- [ ] Surplus Income Directive

**Place all in:** `data/input/osb_directives/`
**Format:** PDF or TXT

Once you have them downloaded, the extraction and loading process is straightforward (same approach as BIA).
