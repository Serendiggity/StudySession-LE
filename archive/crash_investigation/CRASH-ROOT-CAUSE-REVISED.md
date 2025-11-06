# Agent Crash - Root Cause Analysis (REVISED)

**Date:** 2025-11-05
**Status:** 🔴 INVESTIGATION ONGOING - Previous hypothesis WRONG

---

## What We Learned

### ❌ Previous Hypothesis: File Size
**Thought:** Files >10KB trigger crash
**Test Result:** exam-assistant-minimal (1.2KB) also crashed
**Conclusion:** File size is NOT the root cause

###  ✅ Working Agents

| Agent | Size | Behavior | Result |
|-------|------|----------|--------|
| insolvency-simple | 383 bytes | Simple query, return result | ✅ WORKS |
| test-plain | 201 bytes | Static text | ✅ WORKS |
| test-sidebar | 196 bytes | Static sidebar | ✅ WORKS |
| All test agents | <500 bytes | Simple, single operation | ✅ ALL WORK |

### ❌ Crashing Agents

| Agent | Size | Behavior | Result |
|-------|------|----------|--------|
| exam-assistant | 12KB | Complex workflow + cross-refs + CSV | ❌ CRASH |
| exam-assistant-minimal | 1.2KB | Workflow + cross-refs + CSV | ❌ CRASH |

---

## Key Difference: BEHAVIOR, not SIZE

**Working agents:**
- Simple, single-step operations
- No recursive operations
- No file I/O
- Return immediately

**Crashing agents:**
- Multi-step workflows
- **"Follow all cross-references"** instruction
- CSV file tracking
- Multiple database queries

---

## New Hypothesis: Unbounded Operations

### Suspect #1: Cross-Reference Following (PRIMARY SUSPECT)

**The instruction:**
```
Follow all cross-references
```

**The problem:**
- BIA sections reference each other
- Section 172 → references § 173
- Section 173 → references § 172
- Agent follows references recursively
- **Infinite loop = heap exhaustion**

**Stack trace evidence:**
```
AsyncFunctionAwaitResolveClosure
PromiseFulfillReactionJob
RunMicrotasks
```
→ Promises piling up in infinite async recursion

### Suspect #2: CSV Tracking

**The instruction:**
```
Record every answer to CSV
```

**Potential problem:**
- File I/O operations
- Appending to CSV
- Memory accumulation during write operations

### Suspect #3: FTS5 Query with LIMIT 10

**The query:**
```sql
SELECT ... JOIN ... WHERE MATCH 'keywords' ORDER BY rank LIMIT 10
```

**Potential problem:**
- Returns 10 results
- Agent processes all 10
- For each result, follows cross-references
- 10 × N references = exponential growth

---

## Test Plan (Revised)

### Test A: Remove Cross-Reference Following

**Agent:** test-no-crossrefs
**Changes:**
- ✅ Keep database query
- ✅ Keep sidebar format
- ❌ Remove "Follow all cross-references"
- ❌ Remove CSV tracking
- Limit to 3 results

**If this works:** Cross-reference following is the culprit

### Test B: Add Back CSV (after A works)

**If A works, create test-with-csv:**
- ✅ Same as test-no-crossrefs
- ✅ Add CSV tracking back

**If this crashes:** CSV tracking is problematic

### Test C: Add Bounded Cross-References (after B works)

**If B works, create test-limited-crossrefs:**
- ✅ Follow cross-references
- ✅ But LIMIT to 1 level (no recursion)
- ✅ Max 3 references total

**If this works:** Unbounded recursion was the issue

---

## Predicted Outcome

**Most likely:**
"Follow all cross-references" causes infinite recursion when BIA sections have circular references (172 ↔ 173).

**Solution:**
Either:
1. Remove cross-reference following entirely
2. Add recursion limit (max depth = 1)
3. Track already-visited sections to avoid loops

---

## Next Steps

1. **Restart Claude Code** (load test-no-crossrefs agent)
2. **Test:** Invoke test-no-crossrefs with same question
3. **If it works:** Cross-references confirmed as culprit
4. **Create fixed agent:** exam-assistant without unbounded cross-ref following
5. **Test again:** Verify fix works

---

## Files Created

**Test Agents:**
- `test-ultra-minimal.md` (baseline, exactly like insolvency-simple)
- `test-no-crossrefs.md` (no cross-reference following) ⭐ TEST THIS

**Documentation:**
- `CRASH-ROOT-CAUSE-REVISED.md` (this file)

---

**Status:** Ready to test new hypothesis - cross-reference recursion
