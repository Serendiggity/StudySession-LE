# MCP Search Precision Improvements - Issue Tracker

**Created:** 2025-11-06
**Priority:** HIGH
**Status:** Open

---

## Problem Summary

The knowledge-based MCP tool has precision issues preventing it from finding relevant BIA sections for nuanced queries, particularly around consumer proposal discharge procedures.

**Impact:** Users get wrong sections or "not found" for common questions, reducing confidence in the tool.

---

## Specific Issues

### Issue 1: FTS5 Syntax Error with Section Numbers

**Problem:**
```
Query: "section 66.38 certificate"
Error: "fts5: syntax error near '.'"
```

**Root cause:** FTS5 interprets dots as special characters

**Fix needed:**
```python
# Escape dots in section numbers before querying
query = query.replace("66.38", "66\.38")  # Or use FTS5 phrase syntax
# OR: Strip section numbers from query, search separately
```

**Priority:** HIGH - This breaks direct section lookups

---

### Issue 2: Wrong Section Prioritization

**Problem:**
- Query about "certificate of full performance" returns §66.29 (property certificates)
- Should return §66.38 (certificate of full performance)

**Test case:**
```
Query: "consumer proposal certificate debtor discharged"
Expected: §66.38
Actual: §66.29
```

**Root cause:**
- Both sections contain "certificate" and "administrator"
- FTS5 BM25 ranking not capturing semantic difference
- §66.29 might appear earlier or have better keyword density

**Fix options:**
1. **Boost Division II sections** when query contains "consumer proposal"
2. **Add section context** to FTS5 index (section title, part/division)
3. **Use query expansion** - "certificate of full performance" → add "fully performed"
4. **Negative keywords** - exclude §66.29 when query is about discharge

**Proposed implementation:**
```python
def search_with_context_boost(query: str, context_hints: List[str]):
    # If query mentions "consumer proposal", boost Division II sections
    if "consumer proposal" in query.lower():
        # Add weight to sections 66.11-66.4
        boost_clause = "AND (section_number BETWEEN '66.11' AND '66.4')"

    # Semantic expansion
    if "certificate of full performance" in query or "fully performed" in query:
        # Exclude property certificate section
        boost_clause += " AND section_number != '66.29'"
```

**Priority:** HIGH - This is the primary user complaint

---

### Issue 3: Context Confusion (Bankruptcy vs Consumer Proposal)

**Problem:**
- Searching for "discharge" returns bankruptcy sections (§41) instead of consumer proposal sections (§66.38-66.39)

**Root cause:**
- Both bankruptcy and consumer proposals use similar terminology
- No context weighting for Division I vs Division II

**Fix needed:**
```python
# Detect proceeding type from query
proceeding_keywords = {
    'consumer_proposal': ['consumer proposal', 'Division II', 'administrator'],
    'bankruptcy': ['bankrupt', 'Division I', 'trustee'],
    'division_i_proposal': ['Division I proposal', 'inspectors']
}

# Boost sections from relevant division
if detected_type == 'consumer_proposal':
    boost_sections_66 = True
elif detected_type == 'bankruptcy':
    boost_sections_40_to_170 = True
```

**Priority:** MEDIUM - Affects cross-cutting queries

---

### Issue 4: Phrase Matching Issues

**Problem:**
"Certificate of full performance" not matching well - tool finds "certificate" generally

**Fix needed:**
- Use FTS5 phrase queries: `"certificate of full performance"`
- Add as exact phrase match with higher weight
- Current search might be tokenizing and losing phrase structure

**Implementation:**
```python
# Try exact phrase first
exact_phrase_query = f'"{key_phrase}"'
results_exact = query_fts5(exact_phrase_query)

if len(results_exact) > 0:
    return results_exact
else:
    # Fall back to keyword search
    return query_fts5(keywords)
```

**Priority:** MEDIUM

---

### Issue 5: Synonym/Term Variations

**Problem:**
- "Taxation of accounts" not matching well
- "Administrator discharge" concepts scattered

**Missing synonyms:**
```python
SYNONYMS = {
    'certificate of full performance': ['fully performed', 'completion certificate', 'Form 46'],
    'administrator discharge': ['taxation', 'deemed discharge', 'Form 58', 'final accounting'],
    'consumer debtor': ['debtor' + Division II context],
    'consumer proposal': ['Division II proposal']
}
```

**Fix:** Add synonym expansion in search preprocessing

**Priority:** LOW-MEDIUM

---

## Test Cases for Validation

Once fixes are implemented, test with:

```python
test_queries = [
    {
        'query': "consumer proposal certificate debtor discharged",
        'expected_top_3': ['66.38', '66.39', '66.28'],
        'must_not_include': ['66.29', '41']
    },
    {
        'query': "administrator discharge taxation accounts",
        'expected_top_3': ['66.39', '66.38'],
        'must_not_include': ['41', '151']  # bankruptcy sections
    },
    {
        'query': "section 66.38",
        'expected_top_1': ['66.38'],
        'must_not_error': True
    },
    {
        'query': "deemed accepted no meeting consumer proposal",
        'expected_top_1': ['66.18'],
        'must_not_include': ['54']  # Division I voting
    }
]
```

**Success criteria:** 90%+ of test queries return correct top-3 sections

---

## Proposed Solutions (Prioritized)

### Phase 1: Quick Fixes (1-2 hours)

1. **Escape section number dots** for FTS5
2. **Add Division II boost** when "consumer proposal" in query
3. **Exclude wrong certificates** (§66.29) for discharge queries

**Expected improvement:** 50-60% better precision

### Phase 2: Semantic Improvements (4-6 hours)

1. **Implement phrase matching** (exact quotes first, then keywords)
2. **Add synonym expansion** for common terms
3. **Context detection** (bankruptcy vs consumer proposal)

**Expected improvement:** 80-85% precision

### Phase 3: Advanced (8-12 hours)

1. **Fine-tune hybrid search weights** (FTS5 vs vector balance)
2. **Add query understanding** (extract intent before search)
3. **Implement re-ranking** based on section context metadata

**Expected improvement:** 90%+ precision

---

## Related Research

From Tier 1 research deliverables:
- **GraphRAG** could help (community summaries for "certificate" concept)
- **RAT** could help (iterative retrieval with refinement)
- **Query expansion** techniques documented in research

See: `docs/tier1-study-guide-improvements.md`

---

## Next Steps

1. Restart Claude Desktop with fixed MCP server
2. Implement Phase 1 quick fixes
3. Test with queries from this issue
4. Iterate based on results

---

**Issue remains OPEN until test case success rate ≥ 90%**
