# Component Breakdown
## Design Case 08: Cost-Aware AI Router

Deep dive into each component — design choices, failure modes, and implementation details.

---

## 1. Complexity Classifier

The classifier is the brain of the router. Its job: given an incoming request, predict which model tier can handle it correctly, in ~50ms, at near-zero cost.

### Why Not Just Use Rules?

A pure rules-based approach ("if length > 500 tokens → mid tier") works for obvious cases but fails on nuance:

- "What is 2+2?" is 7 tokens but is definitely nano tier
- "Classify this sentence into one of 47 categories" is medium-length but computationally nano-appropriate
- "Explain the geopolitical implications of the Treaty of Westphalia in the context of modern AI governance" is 20 tokens but frontier territory

A trained classifier captures these patterns better than rules.

### Classifier Architecture

```
Input features:
  - Request text (tokenized, truncated to 512 tokens)
  - Metadata signals:
      - Token count of request
      - Presence/count of reasoning keywords
      - Presence of code blocks
      - Number of sub-questions
      - Required output format (json/prose/code)
      - Caller-specified max_latency_ms hint
      - Caller-specified required_capabilities list

Model options:
  Option A: Fine-tuned DistilBERT (66M params, CPU inference, ~20ms)
  Option B: Claude Haiku with a classification prompt (~50ms, $0.0001/call)

Output: {tier: "nano" | "mid" | "frontier", confidence: 0.0–1.0}
```

**Option A vs Option B:** DistilBERT is cheaper at scale (no per-token cost after training) but requires ML infrastructure to train and serve. Haiku requires no ML infrastructure but costs ~$3/day at 1M requests/day. At low-to-medium scale, Haiku is simpler. At high scale, DistilBERT is worth the operational investment.

### Classifier Training Data

Bootstrap from logs:

1. Pull 30,000 historical requests with known outcomes (which model actually handled them well, from user feedback or eval scores)
2. Label: nano=good, mid=needed, frontier=needed
3. Fine-tune DistilBERT for 3 epochs
4. Evaluate on held-out set: target F1 > 0.85 per class

Re-train monthly as the routing log accumulates more outcome data. The classifier gets better as more real routing decisions and their outcomes are logged.

---

## 2. Model Capability Registry

The registry is not just a config file — it's a live data source that the routing engine queries before every dispatch decision.

### Registry Data Model

```python
@dataclass
class ModelRecord:
    model_id: str
    tier: str                          # nano | mid | frontier
    provider: str                      # anthropic | openai | google | self_hosted
    status: ModelStatus                # active | shadow | circuit_open | deprecated
    pricing: PricingConfig
    latency_p50_ms: int
    latency_p99_ms: int
    context_window_tokens: int
    capabilities: List[str]            # list of capability tags
    not_suitable_for: List[str]        # explicit exclusions
    max_concurrent_requests: int
    current_error_rate: float          # updated by circuit breaker
    current_queue_depth: int           # updated by load monitor

@dataclass
class PricingConfig:
    input_per_1m: float
    output_per_1m: float
    cached_input_per_1m: float
    batch_discount: float              # 0.5 = 50% off for async batch requests
```

### Registry Updates

The registry is updated from two sources:

1. **Manual updates (config file):** New models, pricing changes, capability additions. These go through a pull request review process and are deployed via Kubernetes ConfigMap update — no restart required, the service watches for config changes.

2. **Automatic updates (circuit breaker feedback):** If a model's error rate crosses 5%, its `status` is automatically set to `circuit_open` by the circuit breaker component. The routing engine skips circuit-open models. When error rate drops below 1% (tracked over a rolling 5-minute window), the circuit closes automatically.

### Pricing Update Cadence

Model providers change prices frequently. Missing a price update means routing decisions are based on stale data — you might route to a model that's no longer cheapest. Mitigation:

- Automated check of provider pricing pages weekly (web scraping or official pricing APIs)
- Slack alert when a price difference > 20% is detected between registry and scraped price
- Manual review + approval before updating registry (prevents bad data from a scraping error)

---

## 3. Fallback Chain

The fallback chain ensures that a single model's unavailability or poor performance doesn't result in a failed request to the user.

### Fallback Triggers

```
Trigger 1: HTTP 429 (rate limited)
  → Wait 0ms, immediately try next model in tier
  → Log: {trigger: "rate_limit", model: "haiku", fallback_to: "gpt-4o-mini"}

Trigger 2: HTTP 500 / 503 (model provider error)
  → Retry same model once with 100ms delay
  → If still failing: try next model in tier
  → Log: {trigger: "provider_error", model: "haiku", retries: 1}

Trigger 3: Timeout (request exceeds max_latency_ms from client)
  → Abort current call, immediately try faster model if available
  → Otherwise: escalate to next tier (which may be slower — trade off cost for availability)
  → Log: {trigger: "timeout", latency_ms: 1250, sla_ms: 1000}

Trigger 4: Low confidence escalation (optional, caller-enabled)
  → Response from nano model contains hedge phrases or explicit uncertainty
  → Caller has set escalate_on_uncertainty: true
  → Automatically re-run with mid-tier model
  → Log: {trigger: "low_confidence", original_model: "haiku", escalated_to: "sonnet"}
```

### Fallback Chain Configuration

```yaml
fallback_chains:
  nano_failed:
    - provider: anthropic, model: claude-haiku-3-5   # primary
    - provider: openai,    model: gpt-4o-mini         # fallback 1
    - provider: google,    model: gemini-flash         # fallback 2
    - tier_escalate: mid                               # final fallback: go up a tier

  mid_failed:
    - provider: anthropic, model: claude-sonnet-4     # primary
    - provider: openai,    model: gpt-4o               # fallback 1
    - tier_escalate: frontier                          # final fallback

  frontier_failed:
    - provider: anthropic, model: claude-opus-4       # primary
    - provider: openai,    model: o1                   # fallback 1
    # No further fallback: if frontier is unavailable, return 503 with retry hint
```

**Why multi-provider fallback?** A single provider having an outage (Anthropic API incident, OpenAI rate limits during peak) should not affect your system's availability. Multi-provider fallback provides geographic and organizational redundancy.

**The cost transparency requirement:** When a fallback occurs (especially tier escalation), log the reason and the cost differential. A nano request that falls back to frontier costs 100x more than expected. If this is happening frequently, the alert system should surface it as a budget anomaly.

---

## 4. Budget Enforcement

Budget enforcement is a two-layer system: fast Redis check (per request) and authoritative PostgreSQL ledger (for billing and reporting).

### Redis Counter Design

```
Key schema: budget:{scope}:{entity_id}:{period}

Examples:
  budget:user:usr_abc123:2025-04       # user's April 2025 spend
  budget:org:org_xyz789:2025-04        # org's April 2025 spend
  budget:global:platform:2025-04       # platform-wide ceiling

Value: integer (spend in microdollars, e.g., 1000000 = $1.00)
TTL: set to end of month + 7 days (for grace period)
```

**Why microdollars?** Redis integers are 64-bit. Using microdollars (millionths of a dollar) allows tracking up to $9.2 trillion before overflow — more than enough. Integer operations are atomic, preventing race conditions in concurrent increment operations.

**Redis INCR atomicity:**
```python
def record_cost_and_check_budget(user_id: str, cost_usd: float) -> bool:
    """
    Returns True if within budget, False if exceeded.
    Atomic: increment happens before check, so the check is always consistent.
    """
    cost_microdollars = int(cost_usd * 1_000_000)
    key = f"budget:user:{user_id}:{current_month()}"
    limit_microdollars = int(get_user_budget(user_id) * 1_000_000)

    new_total = redis.incr(key, cost_microdollars)  # atomic increment
    redis.expire(key, 40 * 24 * 3600)               # 40-day TTL

    return new_total <= limit_microdollars
```

**The pre-check problem:** The budget check happens before the model call (to prevent overspend). But you don't know the exact cost until the model responds (token count is unknown upfront). Solution: estimate based on max expected tokens for the complexity tier, then reconcile with actual cost post-response.

```
Pre-call: check against estimated cost (conservative upper bound)
  Nano estimate: 2,000 tokens × $0.25/1M = $0.0005
  Mid estimate:  4,000 tokens × $3/1M   = $0.012
  Frontier est: 8,000 tokens × $15/1M  = $0.12

Post-call: update ledger with actual cost
  Actual: 1,200 tokens × $0.25/1M = $0.0003
  Refund the difference: -$0.0002 (subtract from running total)
```

---

## 5. Shadow Mode Testing

Shadow mode is the safe path to promoting new models into production.

### Shadow Traffic Routing

```python
class ShadowRouter:
    def should_shadow(self, request: Request, candidate_model: str) -> bool:
        """Determines if this request should be sent to the shadow model."""
        # Only shadow a configured percentage of traffic
        shadow_rate = self.registry.get_shadow_rate(candidate_model)  # e.g., 0.10
        return random.random() < shadow_rate

    async def shadow_call(self, request: Request, candidate_model: str,
                          prod_response: Response) -> None:
        """
        Makes shadow call asynchronously (does not block production response).
        Compares shadow response to production response and logs results.
        """
        try:
            shadow_response = await self.call_model(candidate_model, request, timeout=30)
            await self.compare_and_log(
                request=request,
                prod_model=self.current_production_model(request),
                prod_response=prod_response,
                shadow_model=candidate_model,
                shadow_response=shadow_response
            )
        except Exception as e:
            # Shadow failures never affect the user
            self.log_shadow_failure(candidate_model, str(e))
```

### Shadow Comparison Metrics

For every shadow call, five metrics are computed and stored:

| Metric | How Computed | What It Means |
|---|---|---|
| Quality delta | LLM judge scores both responses (0-5), compute difference | Is candidate response better or worse? |
| Cost delta | (shadow cost - prod cost) / prod cost | How much cheaper/more expensive? |
| Latency delta | (shadow latency - prod latency) / prod latency | How much faster/slower? |
| Format compliance | Does response match required format (JSON schema, etc.)? | Functional correctness |
| Catastrophic failure rate | % of shadow responses that are empty, garbled, or refused | Hard quality floor |

**Promotion criteria (must meet all):**
- Quality delta > -5% (candidate is at most 5% worse in quality)
- Cost delta < 0 (candidate is cheaper) OR quality delta > +10% (worth the extra cost)
- Latency delta within ±20% of production
- Format compliance rate > 99%
- Catastrophic failure rate < 0.1%

---

## 6. Observability and the Cost Dashboard

The cost dashboard is the primary interface for understanding where money goes and where to optimize next.

### Key Dashboard Panels

```
Panel 1: Real-Time Cost Rate
  ├── Current spend rate ($/hour)
  ├── Projected monthly spend at current rate
  └── Alert threshold markers (80%, 95%, 100%)

Panel 2: Cost by Model Tier (last 30 days)
  ├── Nano tier: $X total, Y% of requests
  ├── Mid tier:  $X total, Y% of requests
  └── Frontier tier: $X total, Y% of requests

Panel 3: Routing Distribution
  ├── % requests handled by each tier
  ├── Escalation rate (nano → mid, mid → frontier)
  ├── Fallback rate (by trigger type: timeout, rate_limit, error)
  └── Tier distribution over time (detect drift)

Panel 4: Shadow Mode Results (when active)
  ├── Candidate model vs production quality delta
  ├── Cost delta
  ├── Latency delta
  └── Promotion readiness indicator

Panel 5: Budget Consumption by Entity
  ├── Top 10 highest-spend users
  ├── Top 5 highest-spend organizations
  └── Budget utilization (% consumed for each entity)
```

### Alerting Rules

| Alert | Condition | Action |
|---|---|---|
| Budget approaching | Any entity at 80% of monthly budget | Email user/org admin |
| Budget enforcement imminent | Any entity at 95% | Throttle to nano-only mode |
| Budget hit | Any entity at 100% | Reject all requests, notify |
| Escalation spike | Escalation rate > 20% over 15-min window | Page on-call (classifier may be broken) |
| Fallback spike | Fallback rate > 5% over 5-min window | Page on-call (provider may be down) |
| Cost anomaly | Hourly spend > 3× 7-day average | Page on-call (possible runaway cost) |

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Architecture_Blueprint.md](./Architecture_Blueprint.md) | System architecture blueprint |
| 📄 **Component_Breakdown.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |

⬅️ **Prev:** [07 AI Content Moderation Pipeline](../07_AI_Content_Moderation_Pipeline/Architecture_Blueprint.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Section 14 — Hugging Face Ecosystem](../../14_Hugging_Face_Ecosystem/01_Hub_and_Model_Cards/Theory.md)
