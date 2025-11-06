# Crash Pattern Analysis

## What Actually Happened

### MY Tests (Using Task tool directly):
1. test-plain → I invoked → ✅ Returned output (no crash)
2. test-special-chars → I invoked → ✅ Returned output (no crash)
3. test-code-blocks → I invoked → ✅ Returned output (no crash)
4. test-sidebar → I invoked → ✅ Returned output (no crash)
5. test-combined → I invoked → ✅ Returned output (partial but no crash)
6. insolvency-simple → I invoked → ✅ PERFECT sidebar output (no crash)

### USER's Tests (Asking questions → I delegate):
1. exam-assistant (l-extract) → User asked question → I delegated → ❌ CRASH
2. exam-assistant-minimal → User asked → I delegated → ❌ CRASH
3. test-no-crossrefs → User asked → I delegated → ❌ CRASH
4. insolvency-test → User asked → I delegated → ❌ CRASH

## THE PATTERN

**When I invoke agents directly using Task tool for testing:** ✅ Works
**When I invoke agents as part of my workflow (delegating user questions):** ❌ Crashes

## What This Means

The crash is NOT in the agents themselves.
The crash is in MY (main Claude's) delegation/invocation mechanism when responding to user questions.

The agents execute fine in isolation.
But when invoked through my normal question-answering workflow, something in MY execution context causes heap exhaustion.

## Why This Matters

The problem is NOT:
- Agent file size
- Agent complexity  
- Cross-reference following
- CSV tracking
- Dynamic queries
- The agents themselves

The problem IS:
- How I (main Claude) invoke agents when delegating user questions
- Something in my execution context
- My workflow/delegation mechanism
