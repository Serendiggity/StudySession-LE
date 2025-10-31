# Example Creation Guide
## How to Create High-Quality Examples for Lang Extract

**Version:** 1.0
**Date:** 2025-10-28
**Purpose:** Guide you through creating the 80-100 examples needed for Phase 3

---

## Table of Contents

1. [Overview](#overview)
2. [Why Examples Matter](#why-examples-matter)
3. [The Example Creation Process](#the-example-creation-process)
4. [Step-by-Step Walkthrough](#step-by-step-walkthrough)
5. [Example Templates by Category](#example-templates-by-category)
6. [Quality Checklist](#quality-checklist)
7. [Common Mistakes to Avoid](#common-mistakes-to-avoid)
8. [Troubleshooting](#troubleshooting)

---

## Overview

**What you're creating:** 80-100 training examples that teach Lang Extract how to extract knowledge from your insolvency PDF.

**Time required:** 5-10 days (Phase 3 of implementation)

**Difficulty:** Moderate - requires careful attention to detail but follows clear patterns

**Impact:** This is THE MOST IMPORTANT phase - quality here determines extraction quality for entire system!

---

## Why Examples Matter

Lang Extract is a **few-shot learning** system. It learns patterns from your examples and applies them to extract similar information from your full document.

**Good examples → High-quality extraction (90%+ recall)**
**Poor examples → Low-quality extraction (60-70% recall)**

### What Makes a Good Example?

✅ **Representative:** Shows typical pattern you want to extract
✅ **Diverse:** Covers simple and complex cases
✅ **Accurate:** Factually correct with no errors
✅ **Clear:** Attributes are well-defined
✅ **Complete:** All required fields present
✅ **Grounded:** From actual source text

---

## The Example Creation Process

### High-Level Workflow

```
1. Choose a category (e.g., "concepts")
2. Open your PDF to find relevant content
3. Identify 5-10 extraction candidates
4. For each candidate:
   a. Copy relevant text from PDF
   b. Identify what to extract
   c. Fill in attributes
   d. Format as ExampleData
   e. Validate
5. Save examples to file
6. Test with small sample
7. Refine if needed
```

### Time Breakdown (per category)

- **Finding candidates:** 15-20 minutes
- **Creating 5-10 examples:** 30-45 minutes
- **Formatting and validation:** 10-15 minutes
- **Total per category:** ~60-90 minutes

**For 13 categories:** 13-20 hours over 5-10 days

---

## Step-by-Step Walkthrough

Let's create a concept example together.

### Step 1: Choose Your Category

Start with **Concepts** - it's the most straightforward.

### Step 2: Find Candidate Text

Open your PDF and look for definitions or explanations of key terms.

**What to look for:**
- Sentences that start with "X is..." or "X means..."
- Bold or italicized terms followed by explanations
- Definition sections
- Glossary entries

**Example from PDF (hypothetical):**

> **Administration** is a procedure under the Insolvency Act 1986 whereby a licensed insolvency practitioner (administrator) is appointed to manage the affairs, business, and property of a company. The primary purpose is to rescue the company as a going concern.

### Step 3: Identify What to Extract

From the text above, identify:
- **Term:** "Administration"
- **Definition:** "A procedure under the Insolvency Act 1986 whereby a licensed insolvency practitioner is appointed to manage the affairs of a company"
- **Source Act:** "Insolvency Act 1986"
- **Context:** "rescue procedure for companies"
- **Importance Level:** "high" (central concept)

### Step 4: Format as ExampleData

```python
import langextract as lx

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
                "definition": "A procedure under the Insolvency Act 1986 whereby a licensed insolvency practitioner is appointed to manage the affairs of a company",
                "source_act": "Insolvency Act 1986",
                "context": "rescue procedure for companies",
                "importance_level": "high"
            }
        )
    ]
)
```

### Step 5: Validate

Run through the checklist:
- ✅ All required fields present (`term`, `definition`)
- ✅ Optional fields where applicable
- ✅ Factually accurate
- ✅ Text copied correctly from source
- ✅ Attributes match schema (see Schema Specification doc)
- ✅ No typos or formatting errors

### Step 6: Save to File

```python
# data/examples/content_examples/concepts_examples.py

import langextract as lx

# List to hold all concept examples
concept_examples = []

# Example 1
concept_examples.append(
    lx.data.ExampleData(
        text="""...""",
        extractions=[...]
    )
)

# Example 2
concept_examples.append(
    lx.data.ExampleData(
        text="""...""",
        extractions=[...]
    )
)

# ... continue for all examples
```

### Step 7: Test Early

After creating 3-5 examples, test them:

```python
from extraction.extractor import ExtractionEngine
from extraction.schemas import ExtractionCategory
from examples.content_examples.concepts_examples import concept_examples

# Create category with your examples
concepts_category = ExtractionCategory(
    name="concepts",
    description="Key terms and definitions",
    attributes=["term", "definition", "source_act", "importance_level"],
    prompt_template="Extract key insolvency concepts and their definitions from the text. Focus on terms central to insolvency law and practice.",
    examples=concept_examples,  # Your 3-5 examples
    priority=1
)

# Test on small text sample
test_text = """
[Copy 1-2 pages from your PDF that contain concepts]
"""

engine = ExtractionEngine()
result = engine.extract_category(test_text, concepts_category, passes=1)

print(f"Extracted {len(result.extractions)} concepts")
for extraction in result.extractions[:5]:  # Show first 5
    print(f"- {extraction.attributes.get('term')}: {extraction.attributes.get('definition')[:50]}...")
```

**Review results:**
- Did it extract concepts you expected?
- Are attributes filled in correctly?
- Any false positives?

**If quality is good:** Continue creating more examples
**If quality is poor:** Refine examples or add more diverse cases

---

## Example Templates by Category

### Template 1: Concepts

```python
lx.data.ExampleData(
    text="""
    [Paste text containing the concept definition.
    Include 2-4 sentences for context.
    Make sure the term and definition are clear.]
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="concept",
            extraction_text="[The specific term being defined]",
            attributes={
                "term": "[Term]",
                "definition": "[Clear, concise definition]",
                "source_act": "[Act name if applicable]",
                "section_reference": "[Section if applicable]",
                "context": "[When/where this applies]",
                "importance_level": "high|medium|low"
            }
        )
    ]
)
```

**Tips for concepts:**
- Look for explicit definitions
- Include the full sentence for context
- Note if term appears in legislation
- Mark importance based on exam relevance

### Template 2: Deadlines (CRITICAL!)

```python
lx.data.ExampleData(
    text="""
    [Paste text describing the deadline.
    MUST include: timeframe, what triggers it, who must act, what must be done.
    Look for phrases like "within X days", "at least X days", "immediately".]
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="deadline",
            extraction_text="[The phrase describing the deadline]",
            attributes={
                "deadline_type": "Filing|Notice|Meeting|Payment|Report",
                "timeframe": "[e.g., '10 days', '30 days', 'immediately']",
                "calculation_method": "business_days|calendar_days|clear_days",
                "day_type_specified": "[What statute actually says]",
                "triggering_event": "[What starts the clock - be specific!]",
                "required_action": "[What must be done]",
                "responsible_party": "[Who must act]",
                "recipient": "[Who receives/benefits]",
                "statutory_reference": "[BIA s. X]",
                "consequences_if_missed": "[What happens if deadline missed]",
                "common_pitfalls": "[Common mistakes]"
            }
        )
    ]
)
```

**Tips for deadlines:**
- **Most important:** Get calculation method right!
- Note if it says "business days" explicitly
- If unclear, assume "clear days" (default for "X days" language)
- Always include statutory reference
- Note what happens if missed

### Template 3: Statutory References

```python
lx.data.ExampleData(
    text="""
    [Paste text that cites a statute section AND explains what it does.
    Must include both the citation and practical effect.]
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="statutory_reference",
            extraction_text="[The statute citation]",
            attributes={
                "act_name": "Bankruptcy and Insolvency Act|Companies' Creditors Arrangement Act|etc.",
                "section_number": "[e.g., '43', '65.13']",
                "subsection": "[If applicable]",
                "provision_text": "[Brief quote if helpful]",
                "practical_effect": "[What this section DOES in practice - required!]",
                "related_sections": ["[Cross-references]"],
                "frequency_of_reference": "very_common|common|occasional|rare"
            }
        )
    ]
)
```

**Tips for statutory references:**
- MUST include practical effect (not just citation!)
- Format section consistently: "43" not "43.0" or "s.43"
- Note how common this section is (helpful for study priority)
- Include cross-references if mentioned

### Template 4: Role Obligations

```python
lx.data.ExampleData(
    text="""
    [Paste text describing what a specific role (Trustee, Receiver, etc.) must/can/cannot do.
    Should be specific, not vague.]
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="role_obligation",
            extraction_text="[The phrase describing the obligation]",
            attributes={
                "role_type": "Trustee|Receiver|Administrator|Proposal Trustee|Monitor|Debtor",
                "obligation_type": "Duty|Power|Prohibition|Discretion",
                "description": "[What the obligation entails]",
                "triggering_event": "[What activates this]",
                "timing_requirement": "[When must it be done]",
                "statutory_basis": "[BIA s. X]",
                "consequences_if_failed": "[Penalties, liability]",
                "to_whom_owed": "[Creditors, Court, OSB, etc.]"
            }
        )
    ]
)
```

**Tips for role obligations:**
- Be specific about which role
- Distinguish duty vs. power (duty = must, power = may)
- Note timing if applicable
- Include consequences (important for exam!)

### Template 5: Procedures

```python
lx.data.ExampleData(
    text="""
    [Paste text describing a multi-step process.
    Should show sequence of actions.]
    """,
    extractions=[
        lx.data.Extraction(
            extraction_class="procedure",
            extraction_text="[Name of the procedure]",
            attributes={
                "procedure_name": "[Clear name]",
                "purpose": "[What this accomplishes]",
                "initiating_event": "[What triggers this]",
                "steps": [
                    {
                        "step_number": 1,
                        "description": "[First step]",
                        "responsible_party": "[Who does it]"
                    },
                    {
                        "step_number": 2,
                        "description": "[Second step]",
                        "responsible_party": "[Who does it]",
                        "deadline": "[If applicable]"
                    }
                    # ... more steps
                ],
                "statutory_basis": "[BIA section]",
                "outcomes": ["[Possible results]"]
            }
        )
    ]
)
```

**Tips for procedures:**
- Number steps clearly
- Note who does each step
- Include deadlines where applicable
- Keep steps actionable

---

## Quality Checklist

### Before Saving Each Example

✅ **Accuracy**
- [ ] Information is factually correct (checked against source)
- [ ] No invented details
- [ ] Quotes are exact if quoted

✅ **Completeness**
- [ ] All required attributes present (see Schema doc)
- [ ] Optional attributes included where applicable
- [ ] Nothing critical is missing

✅ **Formatting**
- [ ] Follows ExampleData structure exactly
- [ ] No syntax errors (commas, quotes, brackets)
- [ ] Indentation is correct
- [ ] Enum values match schema

✅ **Clarity**
- [ ] Definitions are clear (no jargon without explanation)
- [ ] Attributes are well-defined
- [ ] Would make sense to someone unfamiliar with topic

✅ **Relevance**
- [ ] Information is exam-relevant
- [ ] Not overly obscure
- [ ] Appropriate importance/priority level

✅ **Diversity**
- [ ] Example adds something new (not duplicate pattern)
- [ ] Shows different aspect of category
- [ ] Includes both simple and complex cases in set

### After Creating 5-10 Examples per Category

✅ **Coverage**
- [ ] Examples cover main sub-types (e.g., different deadline types)
- [ ] Include both obvious and subtle cases
- [ ] Represent variety of topics

✅ **Testing**
- [ ] Tested on small text sample
- [ ] Extraction quality is good (80%+ accuracy)
- [ ] No obvious gaps in what's extracted

---

## Common Mistakes to Avoid

### Mistake 1: Vague or Incomplete Attributes

❌ **Bad:**
```python
attributes={
    "term": "Trustee",
    "definition": "Person who handles bankruptcy"
}
```

✅ **Good:**
```python
attributes={
    "term": "Trustee",
    "definition": "A licensed insolvency practitioner appointed to administer a bankrupt estate, realize assets, and distribute proceeds to creditors in accordance with the BIA",
    "source_act": "Bankruptcy and Insolvency Act",
    "importance_level": "high"
}
```

### Mistake 2: Inventing Information

❌ **Bad:**
```python
# Adding details not in the source text
attributes={
    "deadline_type": "Notice",
    "timeframe": "10 days",
    "calculation_method": "business_days"  # ← Not stated in source!
}
```

✅ **Good:**
```python
attributes={
    "deadline_type": "Notice",
    "timeframe": "10 days",
    "calculation_method": "clear_days",  # Based on Interpretation Act default
    "day_type_specified": "Statute says 'at least 10 days' without specifying business/calendar"
}
```

### Mistake 3: Copying Too Much or Too Little Text

❌ **Too much:**
```python
text="""
[Entire page of text when only one paragraph is relevant]
"""
```

❌ **Too little:**
```python
text="Administration is a procedure."  # Not enough context!
```

✅ **Just right:**
```python
text="""
Administration is a procedure under the Insolvency Act 1986 whereby
a licensed insolvency practitioner (administrator) is appointed to
manage the affairs, business, and property of a company. The primary
purpose is to rescue the company as a going concern.
"""
# 2-4 sentences providing complete context
```

### Mistake 4: Inconsistent Terminology

If you call something "Trustee in Bankruptcy" in one example and "Bankruptcy Trustee" in another, Lang Extract may treat them as different concepts.

✅ **Solution:** Pick one term and use it consistently across all examples.

### Mistake 5: Skipping Validation

Don't create all 100 examples before testing! Test early with 3-5 examples to catch issues.

### Mistake 6: Missing Required Fields

Every category has required fields (see Schema Specification). Missing them will cause errors.

✅ **Solution:** Keep Schema Specification doc open as reference.

### Mistake 7: Not Diverse Enough

If all your concept examples are simple one-sentence definitions, Lang Extract may miss complex multi-sentence definitions.

✅ **Solution:** Include variety - simple, complex, short, long, different formats.

---

## Troubleshooting

### Problem: Don't know if calculation method is business days or calendar days

**Solution 1:** Check if statute says explicitly
**Solution 2:** If unclear, use "clear_days" (default in Canadian law)
**Solution 3:** Note uncertainty in `day_type_specified` attribute:
```python
"day_type_specified": "Statute doesn't specify; default to clear days per Interpretation Act"
```

### Problem: Can't find enough examples for a category

**Possible reasons:**
1. Looking in wrong part of PDF
2. Category may not be heavily represented in this particular document
3. Being too strict about what counts

**Solutions:**
- For concepts: Look in glossary, definition sections, first mention of key terms
- For deadlines: Look for "days", "immediately", "before", "after", "within"
- For statutory references: Search for "s.", "section", "BIA", "CCAA"
- It's okay if some categories have fewer examples (5 minimum is fine)

### Problem: Examples feel repetitive

**This is normal!** Legal text is repetitive. As long as they show *slightly* different patterns, they're valuable.

**Example:**
- Example 1: 10 days notice (clear days)
- Example 2: 5 days filing deadline (business days)
- Example 3: 30 days report (calendar days)

These may seem similar but teach Lang Extract to distinguish calculation methods.

### Problem: Extraction quality is poor in testing

**Possible causes:**
1. Examples don't match patterns in full document
2. Not enough examples (need 5-10 minimum)
3. Examples are too similar (not diverse enough)
4. Attributes are vague or incorrect

**Solutions:**
- Review Schema Specification - are attributes correct?
- Add more diverse examples
- Check that examples are from actual source text
- Test with different text samples

### Problem: Formatting errors in Python

Common issues:
- Missing commas
- Unmatched quotes or brackets
- Wrong indentation

**Solution:** Use a Python-aware editor (VS Code, PyCharm) that highlights syntax errors.

---

## Tips for Efficiency

### Batch Similar Work

Don't switch categories constantly. Finish all examples for one category before moving to next.

**Efficient:**
1. Do all 10 concept examples
2. Do all 10 statutory reference examples
3. Do all 10 deadline examples
4. etc.

**Inefficient:**
1. Do 1 concept, 1 statutory ref, 1 deadline
2. Repeat
(Context switching slows you down)

### Use Templates

Copy-paste the templates from this guide. Fill in the blanks. Much faster than typing from scratch.

### Take Breaks

Example creation is tedious. Take a break every 60-90 minutes to stay sharp.

### Keep Notes

Track questions or uncertainties as you go:
```
Questions for Phase 6 refinement:
- Not sure if "10 days" in s. 102 is business or calendar days - flag for review
- Couldn't find good example of X - may need to add during refinement
```

### Test Frequently

Don't wait until all 100 examples are done! Test every 10-15 examples to catch issues early.

---

## Example Creation Schedule

### Recommended 10-Day Schedule

**Days 1-3: Critical Foundation**
- Day 1: Concepts (10 examples)
- Day 2: Statutory References (10 examples)
- Day 3: Deadlines (10 examples) + test with small sample

**Days 4-6: Core Knowledge**
- Day 4: Role Obligations (8 examples) + Principles (8 examples)
- Day 5: Procedures (8 examples)
- Day 6: Test all categories so far, refine if needed

**Days 7-8: Supporting Information**
- Day 7: Document Requirements (5), Event Triggers (5), Communication Requirements (5)
- Day 8: Relationships (5 examples)

**Days 9-10: Contextual**
- Day 9: Cases (5), Requirements (5), Exceptions (5)
- Day 10: Pitfalls (5) + final review and testing

**Total:** 93 examples over 10 days

---

## Final Checklist Before Moving to Phase 4

✅ **Quantity**
- [ ] At least 80 examples total
- [ ] Each category has minimum 5 examples
- [ ] Critical categories (concepts, deadlines, etc.) have 8-10 examples

✅ **Quality**
- [ ] All examples validated against checklist
- [ ] No obvious errors or typos
- [ ] Attributes match schema
- [ ] Diverse examples (simple & complex)

✅ **Testing**
- [ ] Tested with small text sample
- [ ] Extraction quality is acceptable (80%+)
- [ ] Made refinements based on test results

✅ **Organization**
- [ ] Examples saved in correct files
- [ ] File structure follows convention:
  ```
  data/examples/content_examples/
  ├── concepts_examples.py
  ├── deadlines_examples.py
  ├── statutory_examples.py
  └── etc.
  ```

✅ **Documentation**
- [ ] Notes on decisions made
- [ ] Questions flagged for later review
- [ ] Ready to proceed to Phase 4!

---

## You're Ready!

With this guide and the Schema Specification document, you have everything you need to create high-quality examples for Phase 3.

**Remember:**
- Quality > speed
- Test early and often
- Diversity matters
- Don't be afraid to refine

**This is the foundation of your entire system. Invest the time to do it right!**

Good luck with example creation! 🚀
