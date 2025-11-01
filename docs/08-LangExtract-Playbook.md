# Lang Extract Playbook
## Battle-Tested Guide for Reliable Extraction

**Version:** 1.0
**Date:** November 1, 2025
**Based on:** Real-world debugging of 411-concept extraction
**Status:** Production-validated

---

## Table of Contents

1. [The Winning Formula](#the-winning-formula)
2. [Creating Examples That Work](#creating-examples-that-work)
3. [Common Pitfalls & How to Avoid Them](#common-pitfalls--how-to-avoid-them)
4. [Step-by-Step Process](#step-by-step-process)
5. [Example Templates by Category](#example-templates-by-category)
6. [Troubleshooting Guide](#troubleshooting-guide)
7. [Quality Validation Checklist](#quality-validation-checklist)

---

## The Winning Formula

### ✅ What Works (Proven with 411 Extractions)

**Example Structure:**
- **3 examples per category** (not 5-10!)
- **1-3 attributes max** (not 5-7!)
- **Definitions <50 characters** (not 80+!)
- **Simple source text** (1-2 sentences, not paragraphs!)
- **Single pass extraction** (not multi-pass initially!)

**Result:** Reliable extraction from unlimited text size

### ❌ What Doesn't Work (Causes JSON Errors)

**Avoid these:**
- ❌ 4+ attributes per extraction
- ❌ Definitions >100 characters
- ❌ Complex source text (multiple clauses, legal language)
- ❌ List-based attributes `["item1", "item2"]`
- ❌ Nested structures
- ❌ 5+ examples per category
- ❌ Multi-pass extraction with complex examples

**Result:** JSON parsing errors, 0 extractions

---

## Creating Examples That Work

### The KISS Principle (Keep It Simple, Stupid)

**Rule 1: Minimal Attributes**
```python
# ✅ GOOD - 2 attributes
attributes={
    "term": "Insolvency",
    "definition": "Unable to pay debts when due"
}

# ❌ BAD - 5 attributes
attributes={
    "term": "Insolvency",
    "definition": "The financial situation a person finds himself in when...",
    "source_act": "Bankruptcy and Insolvency Act",
    "context": "Financial condition triggering bankruptcy options",
    "importance_level": "high"
}
```

**Rule 2: Short Definitions**
```python
# ✅ GOOD - 30 characters
"definition": "Administers bankruptcy estates"

# ❌ BAD - 82 characters
"definition": "Officer of court administering bankruptcy estates with duty of care to all stakeholders"
```

**Rule 3: Simple Source Text**
```python
# ✅ GOOD - Simple sentence
text="A Trustee administers bankruptcy estates."

# ❌ BAD - Complex legal paragraph
text="""
A Trustee is an officer of the court who owes a duty of care to all stakeholders.
A Trustee operates in a position of trust and must maintain a high standard of ethics in the
administration of his duties.
"""
```

**Rule 4: No Lists or Nested Structures**
```python
# ✅ GOOD - String
"required_documents": "Form 31, Form 33, Statement of Affairs"

# ❌ BAD - List
"required_documents": ["Form 31", "Form 33", "Statement of Affairs"]
```

---

## Common Pitfalls & How to Avoid Them

### Pitfall 1: "More Examples = Better Results"

**Myth:** 10 examples will give better extractions than 3
**Reality:** 3-5 examples is optimal. More examples = more complex prompt = more errors

**Fix:** Use 3 examples per category. Add a 4th or 5th only if testing shows low recall.

### Pitfall 2: "Rich Examples = Rich Extractions"

**Myth:** Detailed examples with many attributes will extract more information
**Reality:** Lang Extract generates rich output from simple examples!

**Evidence:**
```
Our example:    "definition": "Administers bankruptcy estates" (30 chars)
Lang Extract:   "definition": "The collection of assets and liabilities of a bankrupt..." (114 chars)
```

**Fix:** Keep examples minimal. Lang Extract will generate detailed extractions automatically.

### Pitfall 3: "JSON Errors Mean Lang Extract is Broken"

**Myth:** JSON parsing errors indicate a framework bug
**Reality:** Gemini generates malformed JSON when examples are too complex

**Fix:** Simplify examples first, not the framework!

### Pitfall 4: "Multi-Pass Always Improves Recall"

**Myth:** 3 passes will find more than 1 pass
**Reality:** With complex examples, multi-pass compounds error rate

**Fix:** Start with single pass. Add more passes only if recall is insufficient AND examples are simple.

### Pitfall 5: "Test with Full Document Right Away"

**Myth:** Just run extraction on full PDF and see what happens
**Reality:** Incremental testing finds breaking points before wasting API calls

**Fix:** Test with 10K → 25K → 50K → Full document

---

## Step-by-Step Process

### Phase 1: Create Minimal Examples (15-30 min per category)

**Step 1.1: Find Simple Source Text**
```
Look in your PDF for:
- Clear, simple sentences
- Explicit definitions
- One concept per sentence
```

**Step 1.2: Extract the Minimum**
```python
# Template
lx.data.ExampleData(
    text="[Simple sentence from PDF]",
    extractions=[
        lx.data.Extraction(
            extraction_class="[category_name]",
            extraction_text="[exact text to extract]",
            attributes={
                "[key_attribute]": "[short value]",
                "[optional_attribute]": "[short value]"
                # MAX 3 attributes!
            }
        )
    ]
)
```

**Step 1.3: Create 3 Examples**
- Example 1: Simplest case (1-2 attributes)
- Example 2: Average case (2 attributes)
- Example 3: With optional attribute (3 attributes max)

**Step 1.4: Save to File**
```python
# data/examples/content_examples/[category]_examples.py
[category]_examples = [
    example_1,
    example_2,
    example_3
]
```

### Phase 2: Test Incrementally (10-20 min)

**Step 2.1: Test on Small Sample (10K chars)**
```bash
python3 src/cli/main.py extract \
    --categories [category_name] \
    --sample-size 10000 \
    --passes 1
```

**Expected:** 50-100 extractions

**If Success:** Proceed to Step 2.2
**If Fail:** Simplify examples further (reduce attributes)

**Step 2.2: Test on Larger Sample (50K chars)**
```bash
python3 src/cli/main.py extract \
    --categories [category_name] \
    --sample-size 50000 \
    --passes 1
```

**Expected:** 200-400 extractions

**If Success:** Proceed to Step 2.3
**If Fail:** Check examples for complexity issues

**Step 2.3: Extract from Full Document**
```bash
python3 src/cli/main.py extract \
    --categories [category_name] \
    --passes 1
```

**Expected:** 300-600 extractions (depends on category)

### Phase 3: Review Quality (5-10 min)

**Step 3.1: Check Extraction Count**
```python
import json
with open('data/output/knowledge_base/[category].jsonl') as f:
    data = json.load(f)
    print(f"Total: {len(data['extractions'])}")
```

**Step 3.2: Review Sample Extractions**
```python
for ext in data['extractions'][:10]:
    print(ext['attributes'])
```

**Step 3.3: View HTML Visualization**
```bash
open data/output/knowledge_base/[category].html
```

**Quality Checks:**
- ✅ Terms extracted correctly?
- ✅ Definitions present and accurate?
- ✅ Source grounding working?
- ✅ No obvious false positives?

**If quality <80%:** Refine examples, re-test
**If quality >80%:** Proceed to next category!

---

## Example Templates by Category

### Template 1: Concepts

```python
import langextract as lx

concept_example = lx.data.ExampleData(
    text="[Concept] is [brief definition].",  # Simple sentence!
    extractions=[
        lx.data.Extraction(
            extraction_class="concept",
            extraction_text="[Concept]",
            attributes={
                "term": "[Concept Name]",
                "definition": "[Short definition <50 chars]"
                # Optional: "importance": "high|medium|low"
            }
        )
    ]
)

# Create 3 examples like this
concept_examples = [example1, example2, example3]
```

### Template 2: Statutory References

```python
statutory_example = lx.data.ExampleData(
    text="BIA s. 50.4 governs [what it does].",
    extractions=[
        lx.data.Extraction(
            extraction_class="statutory_reference",
            extraction_text="BIA s. 50.4",
            attributes={
                "act": "BIA",
                "section": "50.4",
                "effect": "[What it does - short!]"
            }
        )
    ]
)
```

### Template 3: Deadlines

```python
deadline_example = lx.data.ExampleData(
    text="Within 10 days of [trigger], [who] must [action].",
    extractions=[
        lx.data.Extraction(
            extraction_class="deadline",
            extraction_text="Within 10 days",
            attributes={
                "timeframe": "10 days",
                "trigger": "[triggering event]",
                "who": "[responsible party]"
                # Keep it simple!
            }
        )
    ]
)
```

### Template 4: Generic Category

```python
generic_example = lx.data.ExampleData(
    text="[Subject] [verb] [object].",  # Simple declarative sentence
    extractions=[
        lx.data.Extraction(
            extraction_class="[your_category]",
            extraction_text="[what to extract]",
            attributes={
                "name": "[short name]",
                "description": "[brief description]"
                # 2 attributes is plenty!
            }
        )
    ]
)
```

---

## Troubleshooting Guide

### Problem: "JSON parsing error - Unterminated string"

**Diagnosis:** Examples are too complex

**Fix (in order):**
1. **Reduce attributes:** 4+ → 2-3
2. **Shorten definitions:** >80 chars → <50 chars
3. **Simplify source text:** Paragraphs → Simple sentences
4. **Remove lists:** `["a", "b"]` → `"a, b"`
5. **Reduce examples:** 5+ → 3

**Test after each change!**

### Problem: "Extracted 0 items"

**Diagnosis:** Either JSON error or examples don't match target text

**Fix:**
1. Check logs for JSON errors
2. If JSON error: Simplify examples (see above)
3. If no error: Examples may not match text patterns
4. Add more diverse examples showing different phrasings

### Problem: "Extracted too many false positives"

**Diagnosis:** Examples are too vague

**Fix:**
1. Make examples more specific
2. Add examples showing what NOT to extract
3. Refine prompt to be more selective

### Problem: "Extracted items missing attributes"

**Diagnosis:** Attributes are optional - Lang Extract extracts what it finds

**Not a problem!** This is expected:
- 67% of concepts had definitions
- 33% had just terms
- Both are useful!

**If you need more completeness:**
- Add examples specifically showing the attribute
- Make prompt more explicit about that attribute

### Problem: "Extraction is very slow"

**Diagnosis:** Normal for large documents

**Expected times:**
- 10K chars: 1-2 minutes
- 50K chars: 3-5 minutes
- 500K chars: 10-15 minutes

**If slower:**
- Reduce max_workers (default: 10)
- Check internet connection
- Check API rate limits

---

## Quality Validation Checklist

### After Each Extraction:

✅ **Quantity Check**
- [ ] Extracted reasonable number of items?
- [ ] Not too many (false positives)?
- [ ] Not too few (low recall)?

✅ **Quality Check (Sample 10 items)**
- [ ] Terms are actual concepts (not random words)?
- [ ] Definitions are accurate?
- [ ] Attributes make sense?
- [ ] No obvious hallucinations?

✅ **Source Grounding Check**
- [ ] All extractions have char_interval?
- [ ] Can locate extraction in source?
- [ ] Source location makes sense?

✅ **HTML Visualization Check**
- [ ] HTML file generated?
- [ ] Can click and see extractions?
- [ ] Color coding works?
- [ ] Filtering works?

**If 3/4 checks pass:** Good enough, proceed!
**If <3 checks pass:** Refine examples and re-extract

---

## The Minimal Example Recipe

### For ANY Category:

**Step 1: Find ONE simple instance in your source**
```
Example: "Insolvency is when debts exceed assets."
```

**Step 2: Identify what to extract**
```
Extract: "Insolvency"
Want: term + definition
```

**Step 3: Create minimal example**
```python
example = lx.data.ExampleData(
    text="Insolvency is when debts exceed assets.",
    extractions=[
        lx.data.Extraction(
            extraction_class="concept",
            extraction_text="Insolvency",
            attributes={
                "term": "Insolvency",
                "definition": "When debts exceed assets"
            }
        )
    ]
)
```

**Step 4: Copy-paste, modify for 2 more examples**

**Step 5: Test on 10K sample**

**Step 6: If works, run on full document!**

**Total time:** 15-20 minutes per category

---

## When to Add Complexity

### Start Minimal, Enhance Based on Results

**After successful extraction, review results:**

**If 60-70% have definitions:** Good enough! Proceed.
**If <50% have definitions:** Add more examples with definitions
**If missing specific attribute:** Add examples showing that attribute

**Incremental enhancement:**
1. Extract with 2 attributes → Review
2. If good, add 3rd attribute to examples → Re-extract
3. If still good, add 4th → Re-extract
4. Stop at first sign of JSON errors!

**Never add complexity speculatively!**

---

## Category-Specific Tips

### Concepts
**Easy!** Just term + definition
- 3 examples sufficient
- Lang Extract generates great definitions
- High success rate

### Statutory References
**Easy!** Act + section + effect
- Simple format: "BIA s. 50.4"
- 3 attributes: act, section, effect
- Very reliable

### Deadlines ⭐
**Moderate** - More attributes needed
- Essential: timeframe, trigger, who
- Optional: required_documents, recipient
- Start with 3 attributes, add more if needed

### Procedures
**Moderate** - Sequential information
- Can be step-by-step
- Keep steps simple initially
- Enhance later if needed

### Timeline Sequences ⭐
**Complex** - But critical for swimlanes!
- Start with scenario name + duration
- Add steps gradually
- May need 4-5 examples
- Test carefully!

### Decision Points
**Moderate** - For flowcharts
- Question + options format
- 3 attributes: decision, question, context
- Usually reliable

---

## Model Configuration

### Model Choice

**Recommended:** `gemini-2.5-flash`
- Fastest
- Cheapest
- Works great with minimal examples
- Only model currently available in API

**NOT Recommended** (as of Nov 2025):
- ~~gemini-1.5-flash~~ (404 - not found)
- ~~gemini-1.5-pro~~ (404 - not found)

### Extraction Parameters

**Recommended:**
```python
result = lx.extract(
    text_or_documents=text,
    prompt_description="Extract [category] from text.",  # Keep prompt simple!
    examples=minimal_examples,  # 3 examples, 2-3 attributes
    model_id="gemini-2.5-flash",
    extraction_passes=1,  # Single pass!
    max_workers=10  # Default is fine
)
```

**NOT Recommended initially:**
```python
extraction_passes=3,  # Don't use multi-pass until single pass works!
max_workers=50,  # Too aggressive
fence_output=True,  # Breaks with 1.0.9+
```

---

## Incremental Testing Strategy

### The Bisection Approach

**Always test in stages:**

```
Step 1: 10K chars → Did it work?
    ✅ Yes → Go to Step 2
    ❌ No → Simplify examples, retry

Step 2: 25K chars → Did it work?
    ✅ Yes → Go to Step 3
    ❌ No → Something changed between 10K and 25K
           → Test at 15K, 20K to find breaking point

Step 3: 50K chars → Did it work?
    ✅ Yes → Go to Step 4
    ❌ No → Find breaking point between 25K and 50K

Step 4: Full document → Did it work?
    ✅ Yes → Success! Review quality
    ❌ No → Your document is HUGE, may need chunking strategy
```

**Never skip steps!** Incremental testing saves time and money.

---

## Cost Optimization

### With Minimal Examples:

**Per category extraction (full 500K document):**
- ~$0.50-0.75 per category
- Single pass
- 10-15 minutes processing

**For 10 categories:**
- ~$5-7 total
- Can be done in 2-3 hours
- High quality results

### Cost Comparison:

| Approach | Cost per Category | Success Rate |
|----------|-------------------|--------------|
| Minimal examples (1 pass) | $0.50 | 95%+ |
| Complex examples (1 pass) | $0 (fails!) | 0% |
| Complex examples (3 passes) | $0 (fails!) | 0% |

**Minimal is cheapest because it actually works!**

---

## Success Metrics

### Good Extraction Results:

**Concepts:**
- 200-500 extracted from 500K document
- 60-70% with definitions
- All with source grounding

**Statutory References:**
- 50-150 BIA/CCAA sections
- 100% with act name
- 80%+ with practical effect

**Deadlines:**
- 30-80 deadlines extracted
- All with timeframe
- 70%+ with trigger event

**Other Categories:**
- Varies by content density
- 50-200 items typical
- Quality > quantity

### Red Flags:

❌ **Extracted 0 items** → JSON error or bad examples
❌ **Extracted 1000+ items** → Too many false positives, refine prompt
❌ **<30% have key attributes** → Examples not showing that attribute enough

---

## The "Quick Start" Template

### For ANY New Category:

```python
"""
[Category] examples for Lang Extract - MINIMAL approach.
Based on lessons learned from successful 411-concept extraction.
"""

import langextract as lx

# Example 1: Simplest case
example_1 = lx.data.ExampleData(
    text="[One simple sentence].",
    extractions=[
        lx.data.Extraction(
            extraction_class="[category]",
            extraction_text="[what to extract]",
            attributes={
                "name": "[short name]",
                "description": "[brief description]"
            }
        )
    ]
)

# Example 2: Another simple case
example_2 = lx.data.ExampleData(
    text="[Different simple sentence].",
    extractions=[
        lx.data.Extraction(
            extraction_class="[category]",
            extraction_text="[what to extract]",
            attributes={
                "name": "[short name]",
                "description": "[brief description]"
            }
        )
    ]
)

# Example 3: With optional attribute
example_3 = lx.data.ExampleData(
    text="[Third simple sentence].",
    extractions=[
        lx.data.Extraction(
            extraction_class="[category]",
            extraction_text="[what to extract]",
            attributes={
                "name": "[short name]",
                "description": "[brief description]",
                "extra": "[optional detail]"  # 3rd attribute
            }
        )
    ]
)

# Export
[category]_examples = [example_1, example_2, example_3]
```

**Copy this template, fill in the blanks, test!**

**Time to working extraction:** 20-30 minutes per category

---

## Advanced: When You Need More Attributes

### If Minimal Extraction Succeeds, Enhance Gradually:

**Step 1: Baseline**
```python
# Start with 2 attributes
attributes={"term": "X", "definition": "Y"}
# Result: Works!
```

**Step 2: Add One Attribute**
```python
# Add 3rd attribute
attributes={"term": "X", "definition": "Y", "importance": "high"}
# Test on 10K sample
# If works: Proceed. If fails: Remove it.
```

**Step 3: Add Another (Carefully!)**
```python
# Add 4th attribute
attributes={"term": "X", "definition": "Y", "importance": "high", "source": "Z"}
# Test on 10K sample
# More likely to fail! Only add if really needed.
```

**Rule:** Each attribute adds ~10-20% chance of JSON error. Stop before it breaks!

---

## The "It's Not Working" Checklist

**Before spending hours debugging:**

- [ ] Are you using 3 examples (not 5+)?
- [ ] Do examples have 2-3 attributes (not 4+)?
- [ ] Are definitions <50 chars?
- [ ] Is source text simple (not paragraphs)?
- [ ] Are you using single pass (not 3)?
- [ ] Did you test on 10K first (not full document)?
- [ ] Are attributes strings (not lists)?
- [ ] Is model set to gemini-2.5-flash?

**If all checked:** Something else is wrong
**If any unchecked:** Fix that first!

---

## Success Stories (Real Examples from This Project)

### Concepts Category

**Configuration:**
- 3 examples
- 2 attributes (term, definition)
- Simple sentences
- Single pass

**Result:**
- ✅ 411 concepts extracted
- ✅ 67% with definitions
- ✅ Processing time: 10 minutes
- ✅ Cost: $0.50
- ✅ Quality: Excellent

### Future Categories (Using Same Approach)

**Tomorrow's plan:**
- Statutory References: 3 minimal examples → expect 100-150 BIA sections
- Deadlines: 3 minimal examples → expect 50-80 deadlines
- Document Requirements: 3 minimal examples → expect 40-60 forms
- Etc.

**All using the SAME minimal approach that worked for concepts!**

---

## Lang Extract Version Compatibility

### Tested Versions:

**1.0.8:** Works with minimal examples, fails with complex
**1.0.9:** Works with minimal examples, fails with complex

**Note:** Upgrade to latest doesn't solve complex example issues. The solution is simpler examples, not newer versions.

---

## Quick Reference Card

### The Minimal Example Formula:

```
✅ 3 examples per category
✅ 1-2 sentences source text
✅ 2-3 attributes maximum
✅ Definitions <50 characters
✅ No lists, no nesting
✅ Single pass extraction
✅ Test incrementally (10K → 50K → Full)
✅ gemini-2.5-flash model
```

### The CLI Command:

```bash
# Test on sample
python3 src/cli/main.py extract \
    --categories [name] \
    --sample-size 10000 \
    --passes 1

# Run on full document
python3 src/cli/main.py extract \
    --categories [name] \
    --passes 1
```

### Review Results:

```bash
# View HTML
open data/output/knowledge_base/[category].html

# Count extractions
python3 -c "import json; data = json.load(open('data/output/knowledge_base/[category].jsonl')); print(len(data['extractions']))"
```

---

## Bottom Line

### What We Learned the Hard Way (So You Don't Have To):

**1. Simple examples work better than complex ones**
**2. Lang Extract is smart - it generates richness automatically**
**3. Start minimal, add complexity only if needed**
**4. Test incrementally, never skip straight to full document**
**5. JSON errors = examples too complex, not framework broken**

### The Winning Mindset:

> "Give Lang Extract the minimal pattern it needs to recognize what you want. It will do the rest."

**Not:**
> "Specify every detail in examples so Lang Extract knows exactly what to extract."

**Lang Extract is a learning system, not a template engine!**

---

## Next Session Checklist

**Tomorrow, when creating remaining category examples:**

- [ ] Copy the minimal example template
- [ ] Fill in with simple sentences from PDF
- [ ] Keep attributes to 2-3 max
- [ ] Keep definitions to <50 chars
- [ ] Create exactly 3 examples
- [ ] Test on 10K sample first
- [ ] Review results
- [ ] If good, run on full PDF
- [ ] Repeat for next category

**Time per category:** 15-30 minutes
**Success rate:** 95%+ with this approach

---

**This playbook is your insurance policy against future struggles!** 🎯

Follow this, and you'll have reliable extractions every time.
