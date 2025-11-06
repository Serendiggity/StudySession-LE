# Quick Test Instructions - Agent Crash Investigation

## Prerequisites

**You MUST restart Claude Code** before testing to load new agents.

---

## Test Sequence (Run in Order)

### Test 1: Plain Text (Safest)
```
Invoke agent: test-plain
Question: anything
Expected: Returns plain text answer
```
**If crashes:** Framework is fundamentally broken → Use MCP instead

---

### Test 2: Special Characters Only
```
Invoke agent: test-special-chars
Question: anything
Expected: Returns text with § and ✅ symbols
```
**If crashes:** Unicode handling broken → Use ASCII only

---

### Test 3: Code Blocks Only
```
Invoke agent: test-code-blocks
Question: anything
Expected: Returns multiple code blocks
```
**If crashes:** Code block parser broken → Remove examples from agents

---

### Test 4: Sidebar Format Only
```
Invoke agent: test-sidebar
Question: anything
Expected: Returns sidebar box format
```
**If crashes:** Box-drawing characters broken → Use plain text format

---

### Test 5: Combined Format
```
Invoke agent: test-combined
Question: anything
Expected: Returns sidebar + code + special chars
```
**If crashes (but tests 1-4 passed):** Combination triggers exponential parsing → Simplify

---

### Test 6: Original Minimal
```
Invoke agent: insolvency-simple
Question: anything
Expected: Returns simple sidebar
```
**Reference test:** Compare with test-sidebar to validate

---

## How to Execute in Claude Code

1. Restart Claude Code (to load test agents)
2. Type your request to invoke agent:
   - "Use test-plain agent to answer: test"
   - "Invoke test-sidebar agent with: test"
   - Or wait for Claude to delegate based on description
3. Watch for crash or success
4. Record result
5. Move to next test

---

## What to Record

For each test:
- **✅ PASS** - Agent completed, returned result
- **❌ CRASH** - Node.js heap error, Claude Code died
- **Time** - How long it took
- **Phase** - Where it crashed (if visible)

---

## Interpreting Results

| Test Crashes | Trigger Identified | Solution |
|-------------|-------------------|----------|
| test-plain | Framework broken | Use MCP only |
| test-special-chars | Unicode (§ ✅) | Remove special chars |
| test-code-blocks | Code blocks | Remove examples |
| test-sidebar | Box drawing (┌├└) | Plain text format |
| test-combined | Combination | Simplify format |
| All pass | exam-assistant complexity | Reduce agent size |

---

## Quick Decision Tree

```
test-plain crashes?
├─ YES → Framework broken, abandon agents, use MCP
└─ NO → Continue testing

test-special-chars crashes?
├─ YES → Unicode problem, use ASCII
└─ NO → Continue testing

test-code-blocks crashes?
├─ YES → Code block problem, remove examples
└─ NO → Continue testing

test-sidebar crashes?
├─ YES → Box characters problem, use plain text
└─ NO → Continue testing

test-combined crashes?
├─ YES → Combination problem, simplify
└─ NO → Problem is exam-assistant specific

All tests pass?
└─ YES → exam-assistant too large/complex, simplify
```

---

## After Identifying Trigger

1. **Document finding** in test plan
2. **Create fixed agent** without trigger
3. **Test fixed agent** with real question
4. **Delete test agents** (cleanup)
5. **Report bug** to Anthropic (optional)

---

**Status:** Ready to execute
**Test agents created:** 5
**Restart required:** YES
