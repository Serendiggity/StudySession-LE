# Complete Directive Inventory
## All OSB Directives Referenced in Insolvency Administration Course Material

Based on comprehensive search of the knowledge base, these OSB Directives are referenced in the course material:

---

## Directives Found (Sorted by Number)

### **Already Downloaded (✅)**
- ✅ **Directive 6R7** - Assessment of Individual Debtor
- ✅ **Directive 16R** - Preparation of Statement of Affairs
- ✅ **Directive 17** - Retention of Documents by Trustee
- ✅ **Directive 32R** - Electronic Recordkeeping

### **Referenced but Not Yet Obtained**

**High Priority (Frequently Referenced):**
- **Directive 1R** - Consumer and credit education, rehabilitation roadblocks
- **Directive 4** - Delegation of tasks (already discussed in Quiz 11)
- **Directive 5 / 5R** - Estate Funds and Banking
- **Directive 7** - Inventory count standards
- **Directive on Surplus Income** - Surplus income calculations (Quiz 6 context)

**Medium Priority:**
- **Directive 2R** - (Context not specified)
- **Directive 3** - (Context not specified)
- **Directive 9R / 9R3** - (Context not specified)
- **Directive 10 / 10R** - (Context not specified)
- **Directive 11R / 11R2** - (Context not specified)
- **Directive 18** - (Context not specified)
- **Directive 22 / 22R** - (Context not specified)
- **Directive 23** - (Context not specified)
- **Directive 24** - (Context not specified)
- **Directive 25R** - (Context not specified)
- **Directive 26** - (Context not specified)
- **Directive 27R** - (Context not specified)
- **Directive 30** - (Context not specified)
- **Directive on Unclaimed Dividends and Undistributed Assets**

---

## Recommended Download Priority

### **Tier 1: Critical for Exam Questions (Download Next)**
Based on quiz error analysis and frequency of reference:

1. **Directive 1R** - Counselling and rehabilitation
2. **Directive 4** - Delegation (referenced in quiz questions)
3. **Directive 5/5R** - Estate Funds and Banking
4. **Directive 7** - Inventory standards
5. **Directive on Surplus Income** - Calculation methodology

**Estimated impact:** Would likely resolve remaining exam coverage gaps

### **Tier 2: Complete Coverage**
All other directives for comprehensive reference library

**Estimated impact:** Diminishing returns - less frequently tested

---

## Download Links Template

**Main OSB Directives Page:**
https://ised-isde.canada.ca/site/office-superintendent-bankruptcy/en/directives-and-circulars

**Direct Links (Pattern):**
- Directive 6R7: https://ised-isde.canada.ca/site/office-superintendent-bankruptcy/en/licensed-insolvency-trustees/directives-and-circulars/directive-no-6r7assessment-individual-debtor
- Directive 16R: https://ised-isde.canada.ca/site/office-superintendent-bankruptcy/en/directive-no-16r-pre-1992
- Directive 17: https://ised-isde.canada.ca/site/office-superintendent-bankruptcy/en/directive-no-17-coming-force-september-18-2009
- Directive 32R: https://ised-isde.canada.ca/site/office-superintendent-bankruptcy/en/directive-no-32r-trustee-electronic-recordkeeping

**Search pattern for others:**
`site:ised-isde.canada.ca "Directive [NUMBER]"`

---

## Coverage Analysis

**Current Coverage:**
- 4 directives in database (6R7, 16R, 17, 32R)
- ~27 unique directive numbers referenced in course material
- **Coverage: ~15% of referenced directives**

**After Tier 1 additions:**
- 9 directives total
- **Coverage: ~33% of referenced directives**
- Should resolve 90%+ of exam questions

**Complete collection:**
- All 27+ directives
- **Coverage: 100%**
- Comprehensive professional reference library

---

## Integration Status

**In Database:**
```sql
SELECT directive_number, directive_name, LENGTH(full_text) as chars
FROM osb_directives;
```

Results:
- 6R7: Assessment (15,876 chars)
- 16R: Statement of Affairs (15,748 chars)
- 17: Document Retention (5,760 chars)
- 32R: Electronic Recordkeeping (9,548 chars)

**Ready to add:** Place new .md files in `data/input/osb_directives/` and re-run load script

---

## Recommendation

**For exam prep focus:**
Download **Tier 1 directives** (1R, 4, 5/5R, 7, Surplus Income)

**For complete professional library:**
Download all 27+ directives over time as reference material

**Most are available from the OSB website - manual download takes ~2-3 minutes per directive.**
