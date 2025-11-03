# OSB Directives - Download and Integration Guide

## Critical Gap Identified

**Quiz 2 Error Analysis:** 5/15 wrong (33% error rate)
- 4 errors due to missing OSB Directive content
- System has references to Directives but not full text
- **Adding Directives expected to increase accuracy: 67% → 93%**

---

## Directives to Download (Priority Order)

### **Priority 1: Resolve Quiz Errors**

**Directive 6R5/6R7 - Assessment of Individual Debtor**
- **Link:** https://ised-isde.canada.ca/site/office-superintendent-bankruptcy/en/licensed-insolvency-trustees/directives-and-circulars/directive-no-6r5-assessment-individual-debtor
- **Resolves:** Q2 (Assessment acknowledgement), Q8 (who conducts assessment)
- **Quiz impact:** 2 questions

**Directive 16R - Statement of Affairs Preparation (Pre-1992)**
- **Link:** https://ised-isde.canada.ca/site/office-superintendent-bankruptcy/en/directive-no-16r-pre-1992
- **Resolves:** Q9 (jointly owned assets), Q13 (under-secured liabilities)
- **Quiz impact:** 2 questions

### **Priority 2: Commonly Referenced**

**Directive 17R**
- **Link:** https://ised-isde.canada.ca/site/office-superintendent-bankruptcy/en/directive-no-17-coming-force-september-18-2009
- **Referenced in:** Study Material

**Directive 32R - Electronic Recordkeeping**
- **Link:** https://ised-isde.canada.ca/site/office-superintendent-bankruptcy/en/directive-no-32r-trustee-electronic-recordkeeping
- **Referenced in:** Study Material

**Directive 4 - Delegation of Tasks**
- **Link:** TBD (search on OSB directives page)
- **Resolves:** Q11 context (delegation qualifications)

**Directive 5 - Estate Funds and Banking**
- **Link:** TBD (search on OSB directives page)
- **Referenced in:** Study Material

**Surplus Income Directive**
- **Link:** TBD (search on OSB directives page)
- **Resolves:** Q6 context (surplus income calculations)

---

## Manual Download Process

### Step 1: Download Each Directive

**For each link above:**

1. Open in browser
2. **Save complete page:**
   - **Option A (Best):** File → Save Page As → "Complete Page" or "Web Page, Complete"
   - **Option B:** Print → Save as PDF
   - **Option C:** Select all text → Copy → Paste into .txt file

3. **Save to:** `data/input/osb_directives/`
4. **Naming convention:** `directive_6r_assessment.txt` or `.html` or `.pdf`

### Step 2: Place Files

```
data/input/osb_directives/
├── directive_6r_assessment.txt (or .pdf or .html)
├── directive_16r_statement_of_affairs.txt
├── directive_17r.txt
├── directive_32r_recordkeeping.txt
├── directive_4_delegation.txt
├── directive_5_estate_funds.txt
└── directive_surplus_income.txt
```

---

## Automated Integration (After Download)

Once you have the files, run:

```bash
# Process all directives
python3 scripts/process_osb_directives.py \
  --input-dir data/input/osb_directives \
  --output-dir data/output/osb_directives

# Load into database as source #3
python3 scripts/load_directives.py \
  --source-name "OSB Directives" \
  --directive-dir data/output/osb_directives

# Re-test Quiz 2
python3 scripts/test_exam_questions.py --quiz "Quiz 2"

# Expected result: 14/15 or 15/15 correct
```

---

## What the Scripts Will Do

**1. Directive Parser** (Like BIA parser)
- Extract sections/paragraphs
- Preserve complete provision text
- Create structured JSON

**2. Database Loader**
- Add `osb_directives` table
- Add `directive_sections` table
- Link to source_documents (source_id = 3)

**3. FTS5 Indexing**
- Enable fast text search on directives
- Same query optimization as BIA

---

## Expected Results After Integration

### Database Growth
- **Current:** 2 sources, 13,779 entities, 385 BIA sections
- **After:** 3 sources, ~15,000-16,000 entities, 385 BIA + ~50 Directive sections

### Quiz Accuracy
- **Quiz 1:** 100% (no change - didn't need Directives)
- **Quiz 2:** 67% → **~93%** (4 Directive errors resolved)
- **Future quizzes:** Expected 90%+ on Directive-heavy questions

### Coverage
- ✅ BIA statutory provisions
- ✅ Study Material educational context
- ✅ OSB Directive procedural details
- = **Comprehensive exam coverage**

---

## Why Automated Download Failed

**canada.ca site issues:**
- Connection timeouts
- Possible rate limiting
- Slow server response

**Manual download is reliable and quick** - 10-15 minutes for all directives

---

## Next Steps

**After you download the directives:**

1. Let me know and I'll create:
   - `directive_structure_parser.py`
   - `load_directives.py`
   - Schema additions for directive tables

2. Integration time: ~1 hour
3. Re-test Quiz 2: Expected 93%+ accuracy
4. System complete with 3 authoritative sources

**The validation system worked exactly as intended - found the gaps!** 🎯
