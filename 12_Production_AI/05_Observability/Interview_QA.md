# Interview QA — Observability

## Beginner

**Q1: What are the three pillars of observability, and how do they apply to AI systems?**

<details>
<summary>💡 Show Answer</summary>

**A:** The three pillars are **logs**, **metrics**, and **traces**.

**Logs** are timestamped records of discrete events. In an AI system: "At 10:30:15, Request #1234 arrived. Model: claude-3-5-sonnet. Input tokens: 1,450. Output tokens: 342. Latency: 890ms. Cost: $0.0094." Logs answer "what happened?"

**Metrics** are numerical measurements tracked over time: requests per second, P50/P95/P99 latency, error rate, cost per hour, cache hit rate. They answer "how much and how fast?" and are used to spot trends and trigger alerts.

**Traces** track the journey of a single request through all the components in your system. For an LLM application: "Authentication: 5ms. Embedding: 12ms. Vector search: 8ms. LLM inference: 890ms. Response: 2ms." Traces answer "where did time go?" and are the primary debugging tool when you need to understand *why* something is slow.

AI systems need additional layers beyond traditional software: token usage tracking (for cost management), prompt/response logging (for debugging), quality score monitoring (LLM-as-judge on samples), and model drift detection (when output patterns change over time).

</details>

---

**Q2: What is the difference between a log and a metric, and when would you use each?**

<details>
<summary>💡 Show Answer</summary>

**A:** A **log** is a record of a specific event at a specific time, with as much context as you need. Logs are unstructured (or semi-structured) text. Good for: debugging a specific request, understanding error details, auditing user activity. Logs are great for "why did request #1234 fail?" but expensive to query at scale.

A **metric** is a pre-aggregated numerical value tracked over time. Examples: `request_latency_p99`, `requests_per_second`, `error_rate`. Metrics are lightweight, designed for time-series queries, and excellent for dashboards and alerts. But they lose individual request context — you know "error rate spiked at 2pm" but not which specific requests failed or why.

Use logs when you need to investigate a specific incident or understand details. Use metrics when you need to monitor trends, set alerts, or build dashboards. Best practice: use both. Metrics tell you *that* something is wrong. Logs tell you *what* went wrong for specific cases. Traces tell you *where* in the system it went wrong.

</details>

---

**Q3: Why is tracking P99 latency more important than tracking average latency for an AI system?**

<details>
<summary>💡 Show Answer</summary>

**A:** Averages are misleading because they hide extreme values. If 99 requests take 200ms and 1 request takes 20,000ms, the average is ~400ms — which looks fine. But 1% of your users are waiting 20 seconds. That 1% represents real people having a terrible experience, and at 100,000 requests/day that's 1,000 people per day.

P99 latency says: "99% of requests are faster than this value." If P99 = 20,000ms, you immediately know your system has a severe tail latency problem even if the average looks fine.

For AI systems specifically, tail latency often comes from: model context window being exceeded for some long inputs, occasional GPU memory pressure causing requests to queue, cold starts when a container spins up, or database timeout spikes. These events affect a small percentage of requests but show up clearly in P99 and are invisible in the average.

Set your SLOs (Service Level Objectives) on P95 and P99, never on the average.

</details>

---

## Intermediate

**Q4: How would you implement cost tracking for an LLM application, and what would you alert on?**

<details>
<summary>💡 Show Answer</summary>

**A:** Effective cost tracking requires instrumentation at every LLM call:

**Instrumentation layer:**
```python
def tracked_call(messages, model):
    response = client.messages.create(model=model, messages=messages, max_tokens=512)
    cost = compute_cost(response.usage.input_tokens, response.usage.output_tokens, model)
    log_event({
        "model": model,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "cost_usd": cost,
        "request_type": request_type,
        "user_id_hash": hash(user_id)
    })
    return response
```

**Aggregate to metrics:**
- Cost per request (histogram)
- Total cost per hour (counter)
- Cost by model (labeled counter)
- Cost by request type (labeled counter)
- Cost by user tier (labeled counter, for per-user budgets)

**Alert thresholds:**
- Daily cost > 120% of 7-day rolling average (cost anomaly)
- Cost per request > 3x rolling average (context bloat bug)
- Single user consuming > 5% of daily budget (abuse detection)
- Monthly projected spend > budget (based on current burn rate)

**Dashboard views:**
- Daily cost trend with deployment markers (see cost impact of code changes)
- Cost breakdown by model (see if expensive model is being over-used)
- Cost breakdown by request type (see which features are most expensive)

</details>

---

**Q5: What is distributed tracing and how does it help debug AI system performance issues?**

<details>
<summary>💡 Show Answer</summary>

**A:** Distributed tracing tracks the complete journey of a single request through all services and components. Each step (called a "span") is instrumented with its start time and duration. All spans from a single request are linked by a shared trace ID.

In an AI application, a trace might look like:
```
request_1234 (total: 928ms)
  ├─ auth_middleware: 5ms
  ├─ rate_limit_check: 2ms
  ├─ embedding_call: 15ms   (OpenAI text-embedding)
  ├─ vector_search: 8ms     (Pinecone)
  ├─ prompt_assembly: 3ms
  ├─ llm_inference: 890ms   ← bottleneck
  │    ├─ input_tokens: 1,450
  │    └─ output_tokens: 342
  └─ response_formatting: 5ms
```

Without tracing, when a user reports "it feels slow", you only know the total latency was 928ms. With tracing, you immediately see that 96% of time was in `llm_inference`. If that number suddenly jumped from 200ms to 890ms, you know to investigate the model or request size, not the vector DB or auth layer.

Tracing is especially powerful for debugging:
- Where is a specific request slower than expected?
- Which service is the bottleneck across all requests?
- How did latency distribution change after a code deploy?

Tools: OpenTelemetry (standard instrumentation), Jaeger, Zipkin, Datadog APM, Langfuse (LLM-specific).

</details>

---

**Q6: How do you monitor quality in production for an LLM application, given that quality is subjective?**

<details>
<summary>💡 Show Answer</summary>

**A:** Production quality monitoring for LLMs requires multiple signals:

**1. LLM-as-judge (automated sampling):**
Send 1-5% of production request/response pairs to a powerful model (GPT-4 or Claude) with a quality rubric. The judge scores each on dimensions like: accuracy, helpfulness, relevance, and safety (1-5 scale). Track the average score over time. If it drops, investigate recent prompt or model changes.

**2. User signals:**
If your product exposes thumbs up/down or star ratings, track the rate. Even if only 2% of users rate responses, a shift in that 2% is a reliable quality signal. Track: positive rate, negative rate, and any free-text feedback volume.

**3. Behavioral signals:**
Users often "vote with their feet": if response quality drops, users ask follow-up clarifying questions more often, or regenerate responses more often. Track: regeneration rate, follow-up question rate, session length (shorter may mean users gave up).

**4. Refusal rate monitoring:**
If your model starts refusing more requests than usual, it may be a sign of over-conservative guardrail tuning or a model regression. Track refusal rate as a metric.

**5. Output statistics:**
Track: average response length, response length variance, specific keyword frequency (for domain-specific apps). Sudden changes in these statistics often indicate quality issues even before you can run LLM-as-judge on them.

</details>

---

## Advanced

**Q7: Design an observability system for a high-traffic LLM API (1 million requests/day). What would you instrument, store, and alert on?**

<details>
<summary>💡 Show Answer</summary>

**A:** At 1M requests/day (~12 RPS average), full request logging is feasible but needs careful design:

**Instrumentation architecture:**
- Every LLM call wrapped with an SDK interceptor that captures: trace_id, user_id_hash, model, input_tokens, output_tokens, latency_ms, ttft_ms, cost_usd, cache_hit, error_code, guardrail_triggered, quality_score (for 1% sample)
- Async emission to avoid adding latency to the hot path

**Data tiering:**
- **Hot path metrics**: Prometheus → Grafana (real-time, low cardinality aggregates). Retained 90 days.
- **Log aggregation**: Structured logs to ELK/Datadog. Full logs retained 30 days, aggregated retained 1 year.
- **LLM traces**: Langfuse or Phoenix. 100% of requests, but detailed prompt/response only for 10% sample + all errors. Retained 60 days.
- **Quality samples**: 1% of requests run through LLM judge asynchronously. Results stored in data warehouse for trend analysis.

**Alert stack (with priority):**
```
P0 (page immediately):
  - error_rate > 5%
  - P99 latency > 10 seconds
  - API health check failing

P1 (page in 15 min):
  - error_rate 1-5%
  - P99 latency > 3x 7-day rolling avg
  - daily spend > 2x daily budget

P2 (Slack notification):
  - cache hit rate drops > 50% (cache may be down)
  - quality score drops 0.5+ points
  - single user > 5% of daily token budget

P3 (daily digest):
  - output length distribution shift
  - refusal rate trend
  - model usage breakdown changes
```

**Dashboard design:**
- Real-time: RPS, error rate, P50/P99 latency, active requests
- Daily: cost by model + type, quality score trend, cache hit rate
- Weekly: cost per user tier, model usage breakdown, top error types

</details>

---

**Q8: What is the difference between observability and monitoring, and why does it matter for AI systems?**

<details>
<summary>💡 Show Answer</summary>

**A:** This is a nuanced but important distinction:

**Monitoring** is about tracking known failure modes. You define in advance what "bad" looks like and set up checks: "alert if error rate > 1%", "alert if disk > 90% full". Monitoring tells you when something you expected to break has broken.

**Observability** is about being able to investigate unknown failure modes. A system is observable if, given any unexpected behavior, you can figure out *why* it's happening using the data the system emits — even if you didn't know in advance that this specific thing could go wrong. The key question: "Can I diagnose a problem I've never seen before?"

For AI systems, observability is more important than for traditional software because:
1. **Failure modes are less predictable**: A model might silently start hallucinating about specific topics after a model update. You didn't know to monitor for that specific failure.
2. **Quality is multidimensional**: Traditional monitoring covers crashes and latency. AI quality (is the answer good?) requires richer data structures — logged prompts and responses — to diagnose.
3. **New problems emerge with new prompts**: Users will input things you never anticipated, triggering behaviors you didn't predict. You need full observability (raw prompt + response logging) to find and understand these patterns.

In practice: build monitoring (alerts) for the known failure modes AND observability (rich logging, traces) for investigating unknown problems. The monitoring catches known issues automatically; the observability lets you understand and fix novel issues.

</details>

---

## 📂 Navigation
