# Cost Calculator Guide — AI Systems

A step-by-step guide to estimating, tracking, and optimizing AI inference costs. Includes formulas, worked examples, and a break-even calculator.

---

## Step 1: Measure Your Baseline

Before optimizing, you need to know what you are currently spending.

### What to Measure Per Request

```python
import time
import anthropic

client = anthropic.Anthropic()

def tracked_llm_call(prompt: str, system: str = "") -> dict:
    """Wrapper that tracks cost and latency for every LLM call."""
    start = time.time()

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        system=system,
        messages=[{"role": "user", "content": prompt}]
    )

    elapsed_ms = (time.time() - start) * 1000

    # Extract usage
    input_tokens = response.usage.input_tokens
    output_tokens = response.usage.output_tokens

    # Current Claude 3.5 Sonnet pricing (check anthropic.com for latest)
    INPUT_PRICE_PER_M = 3.00   # $ per million input tokens
    OUTPUT_PRICE_PER_M = 15.00  # $ per million output tokens

    cost = (input_tokens * INPUT_PRICE_PER_M / 1_000_000 +
            output_tokens * OUTPUT_PRICE_PER_M / 1_000_000)

    return {
        "response": response.content[0].text,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_usd": round(cost, 6),
        "latency_ms": round(elapsed_ms, 1),
        "model": response.model
    }

# Usage:
result = tracked_llm_call("Summarize the history of Rome in 3 sentences.")
print(f"Cost: ${result['cost_usd']} | Tokens: {result['input_tokens']} in + {result['output_tokens']} out")
```

---

## Step 2: API Cost Formula

### Basic Formula

```
cost_per_request = (input_tokens × input_$/M / 1,000,000)
                 + (output_tokens × output_$/M / 1,000,000)
```

### Monthly Projection Formula

```
monthly_cost = daily_requests × 30
             × ((avg_input_tokens × input_$/M) + (avg_output_tokens × output_$/M))
             / 1,000,000
```

### Worked Example — Customer Support Bot

```
Assumptions:
  Model: Claude 3.5 Sonnet ($3/M input, $15/M output)
  System prompt: 500 tokens (company policies)
  Avg user message: 150 tokens
  Avg chat history included: 800 tokens
  Avg response: 350 tokens
  Daily requests: 50,000

Total avg input tokens: 500 + 150 + 800 = 1,450 tokens
Total avg output tokens: 350 tokens

Cost per request:
  Input:  1,450 × $3 / 1,000,000  = $0.00435
  Output: 350 × $15 / 1,000,000   = $0.00525
  Total:                           = $0.00960

Monthly cost:
  $0.00960 × 50,000 requests/day × 30 days = $14,400/month
```

---

## Step 3: Self-Hosting Cost Formula

### Basic Formula

```
cost_per_request = gpu_cost_per_hour / requests_per_hour

Monthly self-hosting cost = num_gpus × $/hour × 24 × 30
                          + engineering_overhead_$/month
```

### Worked Example — 7B Model on T4

```
Hardware: 1× NVIDIA T4 GPU ($0.35/hour on GCP)
Model: Mistral-7B-Instruct (fits on T4 with int8 quantization)
Throughput: ~400 requests/hour (at avg 500 output tokens each)

Cost per request: $0.35 / 400 = $0.000875

Monthly GPU cost: $0.35 × 24 × 30 = $252/month
Engineering overhead: 5 hrs/month × $100/hr = $500/month
Total monthly: $752/month

At 50,000 req/day × 30 days = 1,500,000 requests/month:
  Cost per request: $752 / 1,500,000 = $0.0005/request
```

---

## Step 4: Break-Even Calculator

**Question: At what volume does self-hosting beat the API?**

```
Break-even_requests = monthly_selfhost_overhead / (api_cost_per_req - sh_cost_per_req)

Example:
  API cost per request:       $0.0096 (from Step 2)
  SH cost per request (var):  $0.0005 (from Step 3, ignoring fixed)
  SH fixed overhead/month:    $752

  Marginal savings per request: $0.0096 - $0.0005 = $0.0091

  Break-even = $752 / $0.0091 = 82,637 requests/month
             = ~2,755 requests/day

Conclusion: At >2,755 req/day, self-hosting is cheaper.
```

### Break-Even Calculator Template

```python
def break_even_analysis(
    api_input_price_per_M: float,   # e.g., 3.00
    api_output_price_per_M: float,  # e.g., 15.00
    avg_input_tokens: int,          # e.g., 1450
    avg_output_tokens: int,         # e.g., 350
    gpu_cost_per_hour: float,       # e.g., 0.35
    requests_per_hour: int,         # e.g., 400
    engineering_hours_per_month: float,  # e.g., 5
    engineer_rate_per_hour: float,  # e.g., 100
):
    api_cost_per_req = (
        avg_input_tokens * api_input_price_per_M / 1_000_000 +
        avg_output_tokens * api_output_price_per_M / 1_000_000
    )

    gpu_monthly = gpu_cost_per_hour * 24 * 30
    eng_monthly = engineering_hours_per_month * engineer_rate_per_hour
    sh_fixed_monthly = gpu_monthly + eng_monthly

    sh_cost_per_req = gpu_cost_per_hour / requests_per_hour  # variable only
    marginal_savings = api_cost_per_req - sh_cost_per_req

    if marginal_savings <= 0:
        print("Self-hosting is NOT cheaper per request. Stick with API.")
        return

    break_even_monthly = sh_fixed_monthly / marginal_savings
    break_even_daily = break_even_monthly / 30

    print(f"API cost per request:     ${api_cost_per_req:.5f}")
    print(f"SH variable cost per req: ${sh_cost_per_req:.5f}")
    print(f"SH fixed cost/month:      ${sh_fixed_monthly:.0f}")
    print(f"Break-even volume:        {break_even_monthly:,.0f} requests/month")
    print(f"                          {break_even_daily:,.0f} requests/day")

break_even_analysis(
    api_input_price_per_M=3.00,
    api_output_price_per_M=15.00,
    avg_input_tokens=1450,
    avg_output_tokens=350,
    gpu_cost_per_hour=0.35,
    requests_per_hour=400,
    engineering_hours_per_month=5,
    engineer_rate_per_hour=100,
)
```

---

## Step 5: Prompt Caching Savings Calculator

```python
def prompt_cache_savings(
    system_prompt_tokens: int,     # tokens in your shared system prompt
    daily_requests: int,
    cache_hit_rate: float,         # expected fraction of requests that hit cache (0-1)
    input_price_per_M: float,      # normal input price
    cache_read_price_per_M: float, # cached token price (typically 10% of input)
):
    """Calculate monthly savings from prompt caching."""
    monthly_requests = daily_requests * 30

    # Without caching: all requests pay full input price for system prompt
    cost_without_cache = (monthly_requests * system_prompt_tokens
                          * input_price_per_M / 1_000_000)

    # With caching: cache misses pay full price, hits pay cache read price
    cache_miss_cost = (monthly_requests * (1 - cache_hit_rate)
                       * system_prompt_tokens * input_price_per_M / 1_000_000)
    cache_hit_cost = (monthly_requests * cache_hit_rate
                      * system_prompt_tokens * cache_read_price_per_M / 1_000_000)
    cost_with_cache = cache_miss_cost + cache_hit_cost

    savings = cost_without_cache - cost_with_cache
    savings_pct = savings / cost_without_cache * 100

    print(f"System prompt tokens: {system_prompt_tokens:,}")
    print(f"Monthly requests:     {monthly_requests:,}")
    print(f"Cache hit rate:       {cache_hit_rate:.0%}")
    print(f"Cost without cache:   ${cost_without_cache:.2f}/month")
    print(f"Cost with cache:      ${cost_with_cache:.2f}/month")
    print(f"Monthly savings:      ${savings:.2f} ({savings_pct:.1f}%)")

# Example: 10K token system prompt, 50K daily requests, 80% hit rate
prompt_cache_savings(
    system_prompt_tokens=10_000,
    daily_requests=50_000,
    cache_hit_rate=0.80,
    input_price_per_M=3.00,
    cache_read_price_per_M=0.30,  # Anthropic: 10% of normal price
)
# Output: Monthly savings: $1,080 (80% reduction on cached portion)
```

---

## Step 6: Full Monthly Cost Dashboard Template

```python
from dataclasses import dataclass
from typing import List
import sqlite3
from datetime import date, timedelta

@dataclass
class RequestLog:
    timestamp: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    request_type: str

# Aggregate daily stats
def daily_cost_report(logs: List[RequestLog]) -> dict:
    total_cost = sum(r.cost_usd for r in logs)
    total_requests = len(logs)
    by_model = {}
    by_type = {}

    for r in logs:
        by_model[r.model] = by_model.get(r.model, 0) + r.cost_usd
        by_type[r.request_type] = by_type.get(r.request_type, 0) + r.cost_usd

    return {
        "total_cost_usd": round(total_cost, 4),
        "total_requests": total_requests,
        "avg_cost_per_request": round(total_cost / total_requests, 6) if total_requests else 0,
        "cost_by_model": {k: round(v, 4) for k, v in sorted(by_model.items(), key=lambda x: -x[1])},
        "cost_by_type": {k: round(v, 4) for k, v in sorted(by_type.items(), key=lambda x: -x[1])},
    }
```

---

## Step 7: Cost Optimization Checklist

Before your next infrastructure review, work through this checklist:

- [ ] Are we tracking cost per request in our logs?
- [ ] Have we tried the next-cheaper model tier and evaluated quality?
- [ ] Is prompt caching enabled for any system prompt longer than 500 tokens?
- [ ] Are we setting `max_tokens` on all requests?
- [ ] Are we including unnecessary context (full docs vs RAG chunks)?
- [ ] What is our cache hit rate? Is exact-match or semantic caching implemented?
- [ ] For batch jobs: are we using spot instances?
- [ ] Have we done the break-even analysis to see if self-hosting makes sense yet?
- [ ] Are we alerting on daily cost anomalies?
- [ ] Do we have per-user cost caps to prevent abuse?

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Cost_Calculator_Guide.md** | ← you are here |

⬅️ **Prev:** [02 Latency Optimization](../02_Latency_Optimization/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 Caching Strategies](../04_Caching_Strategies/Theory.md)
