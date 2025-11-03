# Debugging Analysis - JSON Parsing Issue
**Date:** 2025-11-01
**Lang Extract Version:** 1.0.9
**Issue:** JSON parsing errors preventing extraction on larger text

---

## System Overview

### Current Architecture

```
User → CLI (main.py) → ExtractionEngine → Lang Extract API → Gemini 2.5 Flash → JSON Response → Parser → Result
                                                                                                    ↑
                                                                                              FAILS HERE
```

### Core Components

**1. Example Files (data/examples/content_examples/):**
- concepts_examples.py (5 examples)
- statutory_examples.py (5 examples)
- deadlines_examples.py (5 examples)
- timeline_examples.py (3 examples)
- role_obligations_examples.py (4 examples)
- principles_examples.py (4 examples)
- procedures_examples.py (4 examples)
- decision_points_examples.py (3 examples)
- pitfalls_examples.py (3 examples)
- remaining_categories_examples.py (document_requirements, relationships - 6 examples)
- **Total:** 42 examples across 11 categories

**2. Extraction Engine (src/extraction/):**
- extractor.py: ExtractionEngine class
- schemas.py: Category definitions and prompts

**3. CLI (src/cli/main.py):**
- extract command with options

---

## Working vs. Non-Working Cases

### ✅ WORKING CASES

**Case 1: test_basic.py**
```python
- Example: 1 example, 1 attribute {"term": "Insolvency"}
- Text: 106 characters
- Result: SUCCESS - extracted 2 items in 3.93s
```

**Case 2: concepts_minimal test**
```python
- Examples: 3 examples, 1-3 attributes max
- Text: 170 characters
- Definitions: 3-5 words ("Administers bankruptcy estates")
- Result: SUCCESS - extracted 4 items in 3.03s
```

**Case 3: Direct lx.extract() with minimal config**
```python
result = lx.extract(
    text_or_documents=tiny_text,
    prompt_description="Extract concepts.",
    examples=[minimal_example],  # 1-2 attributes
    model_id="gemini-2.5-flash"
)
# Result: WORKS
```

### ❌ NON-WORKING CASES

**Case 1: CLI extraction with concepts_examples.py (V2)**
```python
- Examples: 5 examples, 3-4 attributes each
- Text: 50,000 characters
- Definitions: 10-15 words ("Officer of court administering bankruptcy estates with duty of care to all stakeholders")
- Result: JSON parsing error - "Unterminated string"
```

**Case 2: test_all_categories.py**
```python
- Examples: 4 categories, 3-5 examples each
- Text: 30,000 characters
- Result: JSON parsing errors on all categories
```

**Case 3: Any extraction with:**
- Multiple passes (passes=2 or 3)
- Larger text chunks (>10K chars)
- Definitions >50 characters
- 4+ attributes per extraction

---

## Key Differences Analysis

### Text Length
| Test | Text Size | Result |
|------|-----------|--------|
| Minimal | 40-170 chars | ✅ SUCCESS |
| Basic | 106 chars | ✅ SUCCESS |
| CLI Sample | 50,000 chars | ❌ FAIL |
| Test All | 30,000 chars | ❌ FAIL |

**Hypothesis:** Text chunking with larger documents triggers malformed JSON

### Attribute Complexity
| Test | Attributes | Definition Length | Result |
|------|------------|-------------------|--------|
| Minimal | 1-2 | 3-5 words | ✅ SUCCESS |
| Basic | 1 | N/A | ✅ SUCCESS |
| V2 | 3-4 | 10-15 words | ❌ FAIL |
| V1 | 5-7 | 20+ words | ❌ FAIL |

**Hypothesis:** Longer definitions increase chance of JSON errors

### Number of Examples
| Test | Examples | Result |
|------|----------|--------|
| Basic | 1 | ✅ SUCCESS |
| Minimal | 3 | ✅ SUCCESS |
| V2 | 5 | ❌ FAIL |

**Hypothesis:** More examples = more complex prompt = higher error rate

### Multi-Pass vs Single Pass
| Test | Passes | Result |
|------|--------|--------|
| Basic | 1 (default) | ✅ SUCCESS |
| Minimal | 1 | ✅ SUCCESS |
| CLI | 2-3 | ❌ FAIL |

**Hypothesis:** Multi-pass extraction compounds the JSON error rate

---

## Error Pattern

**Consistent error:**
```
json.decoder.JSONDecodeError: Unterminated string starting at: line X column Y (char Z)
```

**Where it fails:**
- In `resolver.py` when parsing LLM output
- After Gemini generates response
- Before extraction results are created

**What this means:**
- Gemini is generating malformed JSON
- Our examples are valid (simple tests work!)
- The issue is with HOW Gemini formats complex responses
- Lang Extract's parser can't handle the malformed output

---

## Core Structures to Preserve

### ✅ Must Keep (Working Well)

**1. Project Structure:**
```
src/
├── cli/main.py
├── extraction/
│   ├── extractor.py
│   └── schemas.py
├── document_processor/ (all files)
└── utils/logging_config.py

data/
├── examples/content_examples/ (all example files)
├── input/study_materials/insolvency_admin_extracted.txt
└── output/knowledge_base/
```

**2. ExtractionEngine Architecture:**
- Class structure
- Method signatures
- Logging approach
- Error handling pattern

**3. Example Structure (General):**
- lx.data.ExampleData format
- extraction_class naming
- extraction_text (exact from source)
- attributes dictionary

**4. CLI Integration:**
- Command structure
- Rich formatting
- Progress indicators

### ⚠️ Needs Adjustment

**1. Example Definitions:**
- Currently: 10-15 words
- Need: 5-10 words maximum
- Problem: Longer text = more chances for Gemini to generate bad JSON

**2. Number of Attributes:**
- Currently: 3-4 per extraction
- Need: Start with 2-3, test, then add more
- Problem: Complex attribute structure confuses model

**3. Multi-Pass Strategy:**
- Currently: 2-3 passes per category
- Need: Start with 1 pass, verify it works
- Problem: Multi-pass may compound errors

**4. Chunk Size:**
- Currently: Lang Extract default chunking
- Need: May need manual smaller chunks
- Problem: Large chunks = complex responses = JSON errors

---

## Hypothesized Root Causes (In Order of Likelihood)

### 1. **Definition Length in Source Text** (Most Likely)
Our example text contains 2-4 sentence definitions. When Lang Extract chunks this and sends to Gemini, the model must generate JSON with these long strings. Long strings with special characters (quotes, apostrophes) break JSON formatting.

**Evidence:**
- Minimal examples (1 sentence source) work
- V2 examples (2-4 sentence source) fail
- Even though extracted definition is short, the SOURCE text is long

### 2. **Text Chunking Strategy**
50,000 characters gets split into ~6-7 chunks. Each chunk goes to Gemini separately. With 5 examples showing how to extract, Gemini must:
- Process chunk
- Match patterns from examples
- Generate JSON for all extractions in that chunk
- More extractions = more complex JSON = higher error rate

**Evidence:**
- Small text (170 chars, 1 chunk) works
- Large text (50K chars, 6-7 chunks) fails

### 3. **Example Text Complexity**
Our examples use real legal text with:
- Formal language
- Embedded clauses
- "Section (subsection)" notation
- Quotes within text

Gemini must replicate this structure in JSON, which is error-prone.

**Evidence:**
- Simple sentence examples work ("BIA governs bankruptcy")
- Complex legal text examples fail ("A Trustee is an officer of the court who owes...")

### 4. **Gemini 2.5 Flash Specific Bug**
GitHub Issue #127 shows gemini-2.5-flash has JSON generation bugs that gemini-1.5-flash doesn't have.

**Evidence:**
- Issue reported specifically with 2.5-flash
- PR #239 attempted fix but doesn't fully resolve
- Our version (1.0.9) includes the fix but still fails

---

## Data Flow Trace

### Successful Extraction (test_basic.py)

```
1. Load 1 minimal example
   - text: "Insolvency is when a person cannot pay debts when due." (59 chars)
   - attributes: {"term": "Insolvency"}

2. Call lx.extract()
   - text_or_documents: "A Trustee is an officer..." (106 chars)
   - prompt: "Extract insolvency concepts."
   - examples: [simple_example]
   - model: gemini-2.5-flash

3. Lang Extract processes:
   - No chunking needed (text < threshold)
   - Single API call to Gemini
   - Gemini generates JSON: {"extractions": [{"concept": "Bankruptcy", "concept_attributes": {"term": "Bankruptcy"}}]}
   - JSON parses successfully ✓

4. Result:
   - 2 extractions
   - Clean attributes
   - Source grounding preserved
```

### Failed Extraction (CLI with 50K text)

```
1. Load 5 V2 examples
   - text: 2-4 sentences each (~150 chars each)
   - attributes: 3-4 per extraction

2. Call lx.extract() via ExtractionEngine
   - text_or_documents: 50,000 characters
   - prompt: Category.prompt_template
   - examples: concept_examples (5 items)
   - model: gemini-2.5-flash
   - passes: 2

3. Lang Extract processes:
   - Chunks text into ~6-7 pieces
   - First chunk processes...
   - Gemini generates response
   - JSON parser attempts to parse
   - ERROR: "Unterminated string starting at: line 17 column 23"
   - Parse fails, extraction aborts ✗

4. Result:
   - 0 extractions
   - Error logged
   - No output files
```

---

## Exact Failure Point

**File:** `/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/langextract/resolver.py`
**Line:** ~353
**Function:** `_extract_and_parse_content()`
**Action:** `json.loads(content)`

**What's happening:**
1. Gemini returns text response
2. Lang Extract's resolver tries to parse it as JSON
3. JSON is malformed (unterminated string)
4. Python's json.loads() raises JSONDecodeError
5. Lang Extract catches it, logs "Failed to parse content", continues
6. After all chunks fail, returns 0 extractions

**Why Gemini generates bad JSON:**
- Complex examples → complex prompt → complex expected output
- Longer text in examples → model must preserve structure in JSON
- Special characters in text ("officer's", "can't", quotes) → escaping issues
- Multi-attribute structure → nested JSON → more failure points

---

## Comparison: What Changed from Working to Non-Working

### test_basic.py (WORKS)
```python
simple_example = lx.data.ExampleData(
    text="Insolvency is when a person cannot pay debts when due.",  # ← 59 chars, simple
    extractions=[
        lx.data.Extraction(
            extraction_class="concept",
            extraction_text="Insolvency",  # ← Single word
            attributes={"term": "Insolvency"}  # ← 1 attribute
        )
    ]
)

test_text = "A Trustee is an officer of the court..." # ← 106 chars total

lx.extract(..., examples=[simple_example])  # ← 1 example
```

### concepts_examples.py V2 (FAILS)
```python
concept_v2_2 = lx.data.ExampleData(
    text="""
    A Trustee is an officer of the court who owes a duty of care to all stakeholders.
    A Trustee operates in a position of trust and must maintain a high standard of ethics.
    """,  # ← 160 chars, complex with multiple clauses
    extractions=[
        lx.data.Extraction(
            extraction_class="concept",
            extraction_text="Trustee",  # ← Single word
            attributes={
                "term": "Trustee",
                "definition": "Officer of court administering bankruptcy estates with duty of care to all stakeholders",  # ← 82 chars!
                "importance": "high"  # ← 3 attributes
            }
        )
    ]
)

test_text = [50,000 chars with hundreds of concepts]  # ← HUGE

lx.extract(..., examples=concept_examples, passes=2)  # ← 5 examples, multi-pass
```

**Key differences:**
1. Example text length: 59 chars vs. 160 chars (2.7x longer)
2. Extracted definition: N/A vs. 82 chars
3. Attributes: 1 vs. 3
4. Number of examples: 1 vs. 5
5. Target text: 106 chars vs. 50,000 chars (470x larger!)
6. Passes: 1 vs. 2

---

## Diagnosis: The Problem is Cumulative

It's NOT just one thing - it's the COMBINATION:

**Factors that increase JSON error rate:**
1. ❌ Longer example text (>100 chars)
2. ❌ Longer definitions in attributes (>50 chars)
3. ❌ More attributes per extraction (>2)
4. ❌ More examples (>3)
5. ❌ Larger target text (>10K chars)
6. ❌ Multi-pass extraction (>1 pass)

**Each factor multiplies the risk!**

With all 6 factors combined, JSON error rate approaches 100%.

---

## Solution Strategy

### Approach 1: Radical Simplification (Fastest)

**Make examples ultra-minimal:**
- 1 sentence source text
- 1-2 attributes only
- Definitions <20 characters
- 3 examples max
- Single pass
- Process in 10K chunks

**Trade-off:** Less rich data, but WORKS

### Approach 2: Gradual Complexity (Systematic)

**Start minimal, add one factor at a time:**
1. Test with 1 example, 2 attributes, tiny text → works?
2. Add 2 more examples → still works?
3. Increase text to 10K → still works?
4. Add 3rd attribute → still works?
5. Increase text to 50K → still works?
6. Add multi-pass → still works?

**Trade-off:** Time-consuming but finds exact breaking point

### Approach 3: Different Model (Quick Test)

**Switch to gemini-1.5-flash:**
- Reported as more stable
- Slightly slower
- Same cost
- May not have the JSON bug

**Trade-off:** Unknown if it works, but quick to test

### Approach 4: Process Differently (Workaround)

**Extract with minimal attributes, enhance post-processing:**
1. Extract with just {"term": "X"} initially
2. Save extractions
3. Second pass: enrich with definitions using different approach
4. Merge results

**Trade-off:** Two-stage process, more complex

---

## Recommended Fix Plan

### Phase 1: Get SOMETHING Working (30 min)

1. **Use concepts_minimal.py examples** (proven to work)
2. **Process in 10K chunks** manually
3. **Single pass only**
4. **Test extraction succeeds**

**Expected:** Extract ~100-150 concepts from full PDF

### Phase 2: Incremental Enhancement (1 hour)

1. **Add 3rd attribute** (definition) but keep it <20 chars
2. **Test** on 10K chunk
3. **If works:** Increase to 20K chunk
4. **If works:** Add 4th example
5. **If works:** Increase definition to 50 chars
6. **Stop at first failure,** use last working configuration

### Phase 3: Alternative Model Test (15 min)

1. **Switch to gemini-1.5-flash**
2. **Test with V2 examples**
3. **If works:** Use this model for project
4. **If fails:** Stick with minimal approach

---

## Core Structures - DO NOT CHANGE

✅ **Preserve these exactly:**

**1. File structure:**
- All directory organization
- Module names
- Import paths

**2. ExtractionEngine class:**
- Method signatures
- Parameter names
- Return types
- Error handling pattern

**3. Category schema structure:**
- ExtractionCategory dataclass
- create_*_category() function pattern
- ALL_CATEGORIES list

**4. Example file organization:**
- One file per category
- ALL_EXAMPLES dictionary in __init__.py
- Import structure

**5. CLI command structure:**
- Command names
- Option flags
- Rich formatting approach

**6. Data flow:**
- CLI → Engine → Lang Extract → Save → HTML
- Logging at each step
- JSONL + HTML output

✅ **Can safely change:**

**1. Example content:**
- Text length
- Definition length
- Number of attributes
- Attribute values

**2. Extraction parameters:**
- Number of passes
- max_workers
- Chunk size (if we add manual chunking)
- Model ID

**3. Number of examples:**
- Can use 1-3 instead of 5
- Can add more later if working

---

## Next Steps (Systematic Approach)

1. ✅ **Understand the codebase** (THIS DOCUMENT)
2. **Test minimal examples through CLI** (verify infrastructure works)
3. **Incrementally add complexity** until it breaks
4. **Use last working configuration**
5. **Extract full PDF with working config**
6. **Enhance later if needed**

---

## Success Criteria for Tonight

**Minimum:**
- Get ONE category extracting from 50K text
- Even if only 2 attributes
- Even if only 3 examples
- Prove the infrastructure works!

**Stretch:**
- All 11 categories extracting
- With reasonable attribute richness
- HTML visualizations generated
- Ready for Phase 5 tomorrow

---

**Status:** Analysis complete. Ready to implement systematic fix.
