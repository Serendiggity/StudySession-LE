# API Cost Management & Monitoring Plan
## Controlling and Tracking API Expenses

**Version:** 1.0
**Date:** 2025-10-28
**Purpose:** Ensure API costs stay within budget (<$10 for entire project)

---

## Table of Contents

1. [Cost Overview](#cost-overview)
2. [Rate Limits & Tiers](#rate-limits--tiers)
3. [Cost Tracking](#cost-tracking)
4. [Budget Allocation by Phase](#budget-allocation-by-phase)
5. [Cost Optimization Strategies](#cost-optimization-strategies)
6. [Budget Alerts & Controls](#budget-alerts--controls)
7. [Emergency Procedures](#emergency-procedures)

---

## Cost Overview

### Target Budget
**Total Project Budget:** <$5 (stretch: <$10)
**Per-phase budgets:** See allocation section below

### Actual Expected Costs (291-page PDF)

| Item | Free Tier | Paid Tier |
|------|-----------|-----------|
| **Full document extraction** (all 13 categories, 3 passes) | $0 | $1.50-2.50 |
| **Quiz style learning** (5 sample papers) | $0 | $0.10-0.20 |
| **Quiz generation testing** (20 quizzes) | $0 | $0.50-0.75 |
| **Testing & refinement** | $0 | $0.20-0.50 |
| **Total** | **$0** | **$2.30-4.00** |

**Bottom line:** You can do this entire project for **FREE** using Gemini's generous free tier, or **<$5** if you want maximum speed on paid tier.

---

## Rate Limits & Tiers

### Gemini API Tiers

#### Free Tier (Recommended for This Project)
- **Requests Per Minute (RPM):** 15
- **Tokens Per Minute (TPM):** 1,000,000
- **Requests Per Day (RPD):** 1,500
- **Cost:** $0 ✅
- **Sufficient for:** Your entire 291-page PDF project!

**Limitations:**
- Slower processing (15 RPM bottleneck)
- Time to process full extraction: ~2-3 hours vs. 10-15 minutes on paid tier
- Must respect rate limits (auto-handled by Lang Extract)

#### Paid Tier (If You Want Speed)
- **RPM:** 1,000 (67x faster!)
- **TPM:** 4,000,000 (4x more)
- **No daily limit**
- **Cost:** Pay-as-you-go
  - Input: $0.075 per 1M tokens (<128K context)
  - Output: $0.30 per 1M tokens (<128K context)

### Pricing Calculator

**Your 291-page PDF:**
- Estimated tokens: ~200,000 tokens
- Full extraction (3 passes, 13 categories): ~1.5M input tokens, ~300K output tokens
- **Cost on free tier:** $0
- **Cost on paid tier:** ~$2-3

---

## Cost Tracking

### Real-Time Monitoring

**Method 1: Google AI Studio Dashboard**
1. Go to https://aistudio.google.com
2. Navigate to "Usage" section
3. View:
   - Requests made today
   - Tokens consumed
   - Cost (if on paid tier)
   - Rate limit status

**Method 2: In-Code Tracking**

Add cost tracking to your extraction engine:

```python
# src/utils/cost_tracker.py
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path

@dataclass
class APICall:
    timestamp: datetime
    operation: str
    input_tokens: int
    output_tokens: int
    cost: float
    model: str

class CostTracker:
    def __init__(self, log_file: Path = Path("logs/api_costs.jsonl")):
        self.log_file = log_file
        self.log_file.parent.mkdir(exist_ok=True)

    def log_call(self, operation: str, input_tokens: int, output_tokens: int, model: str = "gemini-2.5-flash"):
        """Log an API call for cost tracking."""
        # Gemini 2.5 Flash pricing (free tier = $0, paid tier calculated)
        if self._is_free_tier():
            cost = 0.0
        else:
            input_cost = (input_tokens / 1_000_000) * 0.075
            output_cost = (output_tokens / 1_000_000) * 0.30
            cost = input_cost + output_cost

        call = APICall(
            timestamp=datetime.now(),
            operation=operation,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            model=model
        )

        # Append to log file
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(call.__dict__, default=str) + '\n')

    def get_total_cost(self) -> float:
        """Calculate total cost from all logged calls."""
        total = 0.0
        if self.log_file.exists():
            with open(self.log_file) as f:
                for line in f:
                    call = json.loads(line)
                    total += call['cost']
        return total

    def get_stats(self) -> dict:
        """Get usage statistics."""
        if not self.log_file.exists():
            return {"total_calls": 0, "total_cost": 0.0, "total_tokens": 0}

        calls = 0
        total_cost = 0.0
        total_tokens = 0

        with open(self.log_file) as f:
            for line in f:
                call = json.loads(line)
                calls += 1
                total_cost += call['cost']
                total_tokens += call['input_tokens'] + call['output_tokens']

        return {
            "total_calls": calls,
            "total_cost": round(total_cost, 2),
            "total_tokens": total_tokens,
            "avg_cost_per_call": round(total_cost / calls, 4) if calls > 0 else 0
        }

    def _is_free_tier(self) -> bool:
        """Check if using free tier (implement based on your setup)."""
        # Could check environment variable or API response headers
        return os.getenv("GEMINI_TIER", "free") == "free"

# Usage in extraction engine
tracker = CostTracker()

# After each extraction
tracker.log_call(
    operation="extract_concepts",
    input_tokens=len(text) // 4,  # Rough estimate
    output_tokens=len(str(result)) // 4,
    model="gemini-2.5-flash"
)

# Check total spend
print(f"Total cost so far: ${tracker.get_total_cost():.2f}")
```

### Manual Tracking Spreadsheet

Create a simple tracking sheet:

| Date | Phase | Operation | Tokens In | Tokens Out | Cost | Running Total |
|------|-------|-----------|-----------|------------|------|---------------|
| 2024-10-28 | Phase 4 | Extract concepts | 220K | 45K | $0.03 | $0.03 |
| 2024-10-29 | Phase 4 | Extract deadlines | 220K | 52K | $0.03 | $0.06 |
| ... | ... | ... | ... | ... | ... | ... |

---

## Budget Allocation by Phase

### Phase-by-Phase Budget

| Phase | Operations | Est. Tokens | Free Tier | Paid Tier | Notes |
|-------|------------|-------------|-----------|-----------|-------|
| **1-3** | Setup, PDF extraction, examples | Minimal | $0 | $0 | No API calls |
| **4** | Initial extraction testing | 300K | $0 | $0.10 | Test with 1-2 categories |
| **5** | Storage setup | 0 | $0 | $0 | No API calls |
| **6** | Full extraction (13 categories) | 1.5M | $0 | $1.50-2.50 | Main expense! |
| **7** | Quiz style learning | 200K | $0 | $0.10-0.20 | 5 sample papers |
| **8** | Quiz generation testing | 100K | $0 | $0.50-0.75 | Testing & refinement |
| **9** | Deadline calculator | 0 | $0 | $0 | Pure logic, no API |
| **10-11** | CLI & testing | 50K | $0 | $0.10-0.20 | Validation calls |
| **12** | Documentation | 0 | $0 | $0 | No API calls |
| **Total** | | **~2.15M** | **$0** | **$2.30-3.75** | |

### Budget Reserves

Keep 20% buffer for unexpected needs:
- Re-running extractions after refinement
- Additional testing
- Edge case handling

**Recommended budget:** $5 (leaves $1-2 buffer)

---

## Cost Optimization Strategies

### Strategy 1: Use Free Tier Maximally

**How:**
- Start all work on free tier
- Only upgrade to paid if you need speed
- Spread extraction over multiple days if needed

**Savings:** 100% (entire project for $0)

**Trade-off:** Time (2-3 hours vs. 15 minutes for full extraction)

### Strategy 2: Batch Operations

**How:**
- Process multiple categories in single extraction run
- Reduces overhead of multiple API calls
- Lang Extract handles batching automatically

**Example:**
```python
# Instead of:
extract(text, category="concepts")    # Call 1
extract(text, category="deadlines")   # Call 2
extract(text, category="principles")  # Call 3

# Do:
extract(text, categories=["concepts", "deadlines", "principles"])  # Single call, optimized
```

**Savings:** 10-20% (reduces redundant processing)

### Strategy 3: Optimize Chunk Size

**How:**
- Use larger chunks (8000 tokens) to reduce number of API calls
- Balance with maintaining context quality

```python
chunker = SmartChunker(
    max_tokens=8000,  # Maximum size
    overlap=500       # Reasonable overlap
)
```

**Savings:** 15-25% (fewer API calls)

### Strategy 4: Smart Multi-Pass Strategy

**How:**
- Use 3 passes only for critical categories (concepts, deadlines, statutory_refs)
- Use 2 passes for supporting categories
- Use 1 pass for contextual categories

```python
category_passes = {
    "concepts": 3,          # Critical
    "deadlines": 3,         # Critical
    "statutory_refs": 3,    # Critical
    "principles": 2,        # Important
    "procedures": 2,        # Important
    "cases": 1,             # Supporting
    "pitfalls": 1           # Supporting
}
```

**Savings:** 20-30% (selective thoroughness)

### Strategy 5: Test with Samples First

**How:**
- Extract from 10-20 pages first
- Validate quality
- Refine examples if needed
- Only then run full extraction

**Saves:** Wasted API calls on poor-quality examples

**Example:**
```python
# Phase 4: Test first
test_text = full_text[:50000]  # First 20 pages
result = extract(test_text, category="concepts", passes=2)

# Review quality
if quality_score < 0.80:
    # Refine examples, try again
    pass
else:
    # Proceed with full extraction
    full_result = extract(full_text, category="concepts", passes=3)
```

### Strategy 6: Cache Results

**How:**
- Save extraction results immediately
- Never re-extract unless absolutely necessary
- Reuse extractions for multiple purposes

```python
# Save immediately after extraction
lx.io.save_annotated_documents([result],
                              output_name=f"{category}_{timestamp}",
                              output_dir="data/output/knowledge_base")

# Reuse for multiple purposes
result = load_from_cache(f"{category}_{timestamp}")
# Use for DB population, HTML generation, quiz generation, etc.
```

**Savings:** Prevents accidental re-extraction

---

## Budget Alerts & Controls

### Setting Up Google Cloud Budget Alerts

1. **Go to Google Cloud Console**
   - https://console.cloud.google.com
   - Navigate to "Billing" → "Budgets & alerts"

2. **Create Budget Alert**
   ```
   Name: Insolvency Study Tool API Budget
   Amount: $10.00
   Alert thresholds:
   - 50% ($5.00)
   - 75% ($7.50)
   - 90% ($9.00)
   - 100% ($10.00)
   ```

3. **Set up email notifications**
   - Get email when each threshold is hit
   - Review spending immediately

### Manual Budget Checks

**Before each major operation:**

```python
def check_budget(tracker: CostTracker, budget: float = 5.0):
    """Check if we're within budget before proceeding."""
    current_cost = tracker.get_total_cost()
    remaining = budget - current_cost

    if remaining <= 0:
        raise Exception(f"Budget exceeded! Current: ${current_cost:.2f}, Budget: ${budget:.2f}")

    if remaining < 1.0:
        print(f"⚠️ WARNING: Only ${remaining:.2f} remaining in budget!")
        proceed = input("Continue? (y/n): ")
        if proceed.lower() != 'y':
            raise Exception("Operation cancelled by user")

    print(f"✓ Budget check passed. ${remaining:.2f} remaining.")

# Use before expensive operations
check_budget(tracker)
result = extract_all_categories(...)
```

### Daily Cost Review

**End of each day:**
1. Check total cost: `tracker.get_stats()`
2. Review operations log
3. Compare to budget allocation
4. Adjust strategy if over budget

---

## Emergency Procedures

### If You Exceed Budget

**Immediately:**
1. **Stop all API calls**
2. **Review cost tracker logs:** Where did costs come from?
3. **Identify cause:**
   - Accidental re-extraction?
   - Rate limit errors causing retries?
   - Inefficient chunking?
4. **Fix root cause before continuing**

### If You Hit Rate Limits

**Free Tier Rate Limit (15 RPM):**
- Lang Extract handles automatically with retry/backoff
- Just wait - it will complete
- Or spread extraction over longer time period

**Daily Limit (1,500 RPD) - Very unlikely but possible:**
- Wait until next day (resets at midnight Pacific Time)
- Or upgrade to paid tier temporarily

### If Extraction Quality is Poor

**Don't immediately re-extract!** That wastes API calls.

**Instead:**
1. Review examples - are they representative?
2. Check extraction results - what patterns were missed?
3. Add 2-3 targeted examples
4. Test on small sample first (10 pages)
5. Only re-extract full document if small sample improves

---

## Cost Monitoring Dashboard (Optional)

### Simple CLI Dashboard

```python
# src/cli/commands/stats.py

@cli.command()
def cost_stats():
    """Display API cost statistics."""
    tracker = CostTracker()
    stats = tracker.get_stats()

    console = Console()

    table = Table(title="API Cost Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")

    table.add_row("Total API Calls", str(stats['total_calls']))
    table.add_row("Total Tokens", f"{stats['total_tokens']:,}")
    table.add_row("Total Cost", f"${stats['total_cost']:.2f}")
    table.add_row("Avg Cost/Call", f"${stats['avg_cost_per_call']:.4f}")

    # Budget status
    budget = 5.0
    remaining = budget - stats['total_cost']
    percentage = (stats['total_cost'] / budget) * 100

    table.add_row("Budget", f"${budget:.2f}")
    table.add_row("Remaining", f"${remaining:.2f}")
    table.add_row("Used", f"{percentage:.1f}%")

    console.print(table)

    # Warning if close to budget
    if percentage > 75:
        console.print("\n⚠️ WARNING: Over 75% of budget used!", style="bold red")
```

**Usage:**
```bash
insolvency-study cost-stats
```

---

## Cost Projection Tool

### Estimate Before Running

```python
def estimate_cost(
    num_pages: int,
    categories: int,
    passes: int,
    tier: str = "free"
) -> dict:
    """Estimate cost before extraction."""

    # Rough estimates
    tokens_per_page = 700
    output_tokens_ratio = 0.2  # Output is ~20% of input

    total_input_tokens = num_pages * tokens_per_page * categories * passes
    total_output_tokens = total_input_tokens * output_tokens_ratio

    if tier == "free":
        cost = 0.0
        time_minutes = (total_input_tokens / 1000000) * 60  # 1M tokens ≈ 60 min on free tier
    else:
        input_cost = (total_input_tokens / 1_000_000) * 0.075
        output_cost = (total_output_tokens / 1_000_000) * 0.30
        cost = input_cost + output_cost
        time_minutes = (total_input_tokens / 1000000) * 3  # ~3 min per 1M tokens paid tier

    return {
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "estimated_cost": round(cost, 2),
        "estimated_time_minutes": round(time_minutes, 1),
        "tier": tier
    }

# Example usage
estimate = estimate_cost(
    num_pages=291,
    categories=13,
    passes=3,
    tier="free"
)

print(f"Estimated cost: ${estimate['estimated_cost']:.2f}")
print(f"Estimated time: {estimate['estimated_time_minutes']:.1f} minutes")
```

---

## Cost Summary Table

### Quick Reference

| Scenario | Free Tier | Paid Tier | Time (Free) | Time (Paid) |
|----------|-----------|-----------|-------------|-------------|
| **Test extraction (1 category, 20 pages)** | $0 | <$0.05 | ~5 min | ~1 min |
| **Single category full extraction** | $0 | $0.10-0.20 | ~10 min | ~2 min |
| **All 13 categories, 2 passes** | $0 | $1.50-2.00 | ~90 min | ~10 min |
| **All 13 categories, 3 passes** | $0 | $2.00-3.00 | ~120 min | ~15 min |
| **Quiz style learning (5 papers)** | $0 | $0.10-0.20 | ~5 min | ~1 min |
| **Generate 10 quizzes** | $0 | $0.05 | ~2 min | ~30 sec |
| **Entire project (with testing)** | $0 | $2-4 | ~4 hours | ~30 min |

---

## Recommended Approach

### For Budget-Conscious (Maximize Free Tier)

1. **Use free tier exclusively**
2. **Spread extraction over 2-3 days** to avoid hitting daily limits
3. **Run overnight** if needed (set it and forget it)
4. **Total cost:** $0
5. **Total time:** 4-6 hours of processing (but unattended!)

### For Time-Conscious (Worth $3-5)

1. **Use free tier for testing and examples** (Phase 1-5)
2. **Upgrade to paid tier for Phase 6** (full extraction)
3. **Stay on paid tier through Phase 8** (quiz generation)
4. **Downgrade back to free tier for Phase 9-12**
5. **Total cost:** $2-4
6. **Total time:** 30-45 minutes of processing

### Hybrid Approach (Best of Both)

1. **Free tier for all non-critical operations**
2. **Paid tier only for Phase 6** when doing full extraction
3. **Immediately downgrade after Phase 6**
4. **Total cost:** $1.50-2.50
5. **Balance of time and cost**

---

## Final Budget Checklist

✅ **Before Starting:**
- [ ] Set up budget alerts in Google Cloud
- [ ] Implement cost tracker in code
- [ ] Understand rate limits
- [ ] Choose tier strategy (free vs. paid)

✅ **During Development:**
- [ ] Check cost stats daily
- [ ] Log all API operations
- [ ] Review logs for unexpected costs
- [ ] Stay within phase budgets

✅ **Before Major Operations:**
- [ ] Run cost estimate
- [ ] Check budget remaining
- [ ] Confirm tier settings
- [ ] Have emergency stop plan

✅ **After Project:**
- [ ] Review total costs
- [ ] Document lessons learned
- [ ] Archive cost logs
- [ ] Celebrate staying under budget! 🎉

---

## Conclusion

With proper planning and monitoring, you can build this entire system for **$0-5**, well within your budget. The key is:

1. **Start with free tier** (it's surprisingly generous!)
2. **Monitor costs closely** (use tracking tools)
3. **Optimize operations** (batching, smart passes)
4. **Set up alerts** (prevent surprises)
5. **Test before full runs** (avoid waste)

**Most users complete this project for $0-2.** You can too!

---

## Appendix: Cost Tracking Template

```python
# Create logs/api_costs.jsonl with this format:
{
  "timestamp": "2024-10-28T10:30:00",
  "operation": "extract_concepts",
  "input_tokens": 220000,
  "output_tokens": 45000,
  "cost": 0.03,
  "model": "gemini-2.5-flash",
  "phase": "Phase 4",
  "notes": "Initial concepts extraction, 3 passes"
}
```

Track every API call and you'll never be surprised by costs!
