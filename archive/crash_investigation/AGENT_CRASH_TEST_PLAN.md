# Agent Crash Investigation - Test Plan

**Objective:** Isolate the exact trigger causing Node.js heap exhaustion during agent execution.

**Hypothesis:** Claude Code framework has a bug in result processing triggered by specific formatting elements.

---

## Test Suite

### Test 1: Plain Text Only
**Agent:** `test-plain`
**Output:** Pure text, no special formatting, no code blocks, no special characters
**Expected:** If this crashes, framework is fundamentally broken
**Test command:** User invokes test-plain agent

### Test 2: Sidebar Format Only
**Agent:** `test-sidebar`
**Output:** Only box-drawing characters (┌─ ├─ └─), minimal text
**Expected:** If this crashes, sidebar format is the trigger
**Test command:** User invokes test-sidebar agent

### Test 3: Special Characters Only
**Agent:** `test-special-chars`
**Output:** § symbols, ✅ emoji, unicode characters, no sidebar
**Expected:** If this crashes, unicode handling is broken
**Test command:** User invokes test-special-chars agent

### Test 4: Code Blocks Only
**Agent:** `test-code-blocks`
**Output:** Multiple code blocks (SQL, bash, CSV), no sidebar
**Expected:** If this crashes, code block parsing has issue
**Test command:** User invokes test-code-blocks agent

### Test 5: Combined Format
**Agent:** `test-combined`
**Output:** Sidebar + special chars + code blocks
**Expected:** If this crashes but others don't, combination triggers it
**Test command:** User invokes test-combined agent

### Test 6: Existing Minimal
**Agent:** `insolvency-simple`
**Output:** Simple sidebar with one SQL query
**Expected:** Baseline test of existing minimal agent
**Test command:** User invokes insolvency-simple agent

---

## Test Execution Order

**IMPORTANT:** After creating test agents, restart Claude Code to reload agent definitions.

1. **Start safest → most complex:**
   - test-plain (safest)
   - test-special-chars (unicode only)
   - test-code-blocks (code only)
   - test-sidebar (sidebar only)
   - insolvency-simple (existing minimal)
   - test-combined (all features)

2. **Stop at first crash** - We've identified the trigger

3. **If all pass** - Problem is in exam-assistant content/complexity, not formatting

---

## Expected Outcomes

### Scenario A: test-plain crashes
**Conclusion:** Framework fundamentally broken, not formatting-specific
**Solution:** Report to Anthropic, use MCP instead

### Scenario B: test-sidebar crashes
**Conclusion:** Box-drawing characters trigger markdown parser bug
**Solution:** Create plain-text version of exam-assistant

### Scenario C: test-special-chars crashes
**Conclusion:** Unicode handling (§ ✅) triggers issue
**Solution:** Replace special chars with ASCII equivalents

### Scenario D: test-code-blocks crashes
**Conclusion:** Multiple code blocks cause parsing loop
**Solution:** Reduce/remove code examples from agent

### Scenario E: test-combined crashes (but individuals pass)
**Conclusion:** Combination of elements triggers exponential parsing
**Solution:** Simplify output format, avoid mixing sidebar + code blocks

### Scenario F: All pass, only exam-assistant crashes
**Conclusion:** Large agent file size or complex instructions cause issue
**Solution:** Simplify exam-assistant instructions, reduce examples

---

## Data Collection

For each test, record:
- ✅ Success / ❌ Crash
- Time to completion (if success)
- Memory usage pattern (if visible)
- Error message (if crash)
- Exact crash phase (Transfiguring, etc.)

---

## Created Agents

Location: `.claude/agents/`

- `test-plain.md` (169 bytes)
- `test-sidebar.md` (185 bytes)
- `test-special-chars.md` (243 bytes)
- `test-code-blocks.md` (341 bytes)
- `test-combined.md` (380 bytes)

All agents use minimal tool access (Bash only) to reduce variables.

---

## Next Steps After Testing

Once trigger identified:
1. Create workaround agent (trigger-free version)
2. Document bug for Anthropic
3. Implement permanent solution
4. Clean up test agents

---

**Status:** Test agents created, ready for execution
**Date:** 2025-11-05
**Created by:** Claude Code (Main)
