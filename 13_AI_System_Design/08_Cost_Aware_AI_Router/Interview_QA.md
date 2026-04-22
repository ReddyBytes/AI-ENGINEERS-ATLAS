# Interview Q&A
## Design Case 08: Cost-Aware AI Router

Nine system design interview questions at beginner, intermediate, and advanced levels.

---

## Beginner Questions

### Q1: What problem does a cost-aware AI router solve and why not just always use the best model?

**Answer:**

The problem is that **LLM quality and cost are not always correlated with task requirements**. A frontier model answering "what is the capital of France?" is like sending a specialist surgeon to give someone a band-aid. The quality difference is zero, but the cost difference is 100x.

At scale, this matters enormously. If you have 100,000 API calls/day across your product:

```
All-frontier approach:
  100,000 × 4,000 tokens × $15/1M input = $6,000/day = $180,000/month

Routed approach (70% nano, 25% mid, 5% frontier):
  70,000 × 2,000 × $0.08/1M  = $11.20/day   (nano)
  25,000 × 3,000 × $3/1M     = $225/day      (mid)
  5,000  × 8,000 × $15/1M    = $600/day      (frontier)
  Total: $836.20/day = $25,086/month
```

**The cost-aware router reduces spend by 86% with no meaningful quality regression** — because the quality of the response to "classify this as spam or not spam" from Haiku is identical to what Opus would produce.

The secondary benefit is latency: nano models respond in 400ms, frontier models in 3-8 seconds. Tasks that can use nano models get faster responses, improving user experience.

---

### Q2: What is a circuit breaker and why does the router need one?

**Answer:**

A **circuit breaker** is a pattern that detects when an external service (a model provider in this case) is failing, and temporarily stops sending requests to it to avoid cascading failures.

Think of it like a fuse box: if a circuit is drawing too much current (too many errors), the breaker trips. You don't keep sending current through a broken circuit — you route power elsewhere.

**Three states:**

1. **Closed (normal):** Requests flow through to the model. Error rate is tracked.
2. **Open (tripped):** Error rate exceeded threshold (e.g., > 5% in the last 5 minutes). No new requests are sent to this model. They're immediately routed to the fallback.
3. **Half-open (testing recovery):** After a cooldown period (e.g., 30 seconds), one test request is sent. If it succeeds, the circuit closes. If it fails, the circuit reopens.

**Why does the router need this?**

Without a circuit breaker, when Anthropic's API has an incident, every request to the router would: try Haiku → wait for the timeout (5-30 seconds) → fail → try fallback. This means every user waits for the full timeout before getting a response.

With a circuit breaker: after detecting the Anthropic outage (5% error rate in 5 minutes), the circuit opens. Subsequent requests immediately skip to the OpenAI fallback — no timeout wait, sub-millisecond routing decision.

**Business impact:** Circuit breakers are the difference between "our AI feature was slow during the Anthropic incident" and "our AI feature was completely unaffected by the Anthropic incident."

---

### Q3: How does the budget enforcement system prevent one user from spending all of an organization's budget?

**Answer:**

The budget system uses a **hierarchical budget structure** with independent enforcement at each level:

```
Platform global ceiling: $50,000/month
  └── Organization A: $500/month
       ├── User A1: $50/month
       ├── User A2: $50/month
       └── User A3: $50/month (if A3 spends $50, A1 and A2 still have $50 each)
  └── Organization B: $1,000/month
       └── ...
```

**The key design:** User budgets and organization budgets are tracked and enforced independently. A user who hits their $50 limit is rejected even if the organization still has $400 remaining. An organization that hits its $500 limit affects all users in that org — their individual counters no longer matter.

**Implementation:** Each request is checked against both the user's counter and the organization's counter in Redis before being processed. Both must be under their respective limits:

```python
def is_within_budget(user_id: str, org_id: str, estimated_cost: float) -> bool:
    user_counter = redis.get(f"budget:user:{user_id}:{month()}")
    org_counter  = redis.get(f"budget:org:{org_id}:{month()}")

    user_limit = get_user_limit(user_id)
    org_limit  = get_org_limit(org_id)

    return (user_counter + estimated_cost <= user_limit and
            org_counter  + estimated_cost <= org_limit)
```

**Practical notes:** In practice, orgs typically set user limits lower than the org limit, so individual user limits trip before the org limit. The org limit acts as a safety ceiling for runaway scripts or compromised accounts.

---

## Intermediate Questions

### Q4: The complexity classifier routes requests to tiers. How do you handle the case where the classifier is wrong?

**Answer:**

The classifier will occasionally mis-route. There are two types of mis-routing:

**Under-routing (nano when mid was needed):** The model gives a poor response. This is detected either by the calling application (if it evaluates the response) or by the user (feedback signal). The router can handle this via **confidence-based escalation**: if the response from the nano model contains hedge phrases or fails format validation, automatically re-try with the mid model. The caller pays the extra cost, but the user gets a good response.

**Over-routing (mid when nano would have sufficed):** No quality problem — just unnecessary cost. This is detected in aggregate: if you track quality scores and cost for each routed request, over-routing shows up as "mid-tier cost with nano-tier quality results." Use this data to retrain the classifier.

**Caller overrides:** The routing API exposes explicit tier hints. Callers who know their request is complex can override: `{"tier_hint": "frontier", "reason": "multi-document synthesis"}`. This bypasses the classifier for that request. Callers who know they need only nano can specify `{"tier_hint": "nano", "max_escalation": false}` to prevent auto-escalation.

**Continuous improvement:** Every routing decision is logged with its outcome (quality score, escalation, user feedback). A monthly retraining of the classifier on this logged data reduces mis-routing rate over time. The target is < 5% mis-routing rate; most mature systems land at 2-3%.

---

### Q5: How would you design the router to handle streaming responses?

**Answer:**

Streaming responses (Server-Sent Events, token-by-token delivery) complicate routing because you don't know the total token count — and therefore the cost — until the stream is complete.

**Challenge 1 — Pre-call budget check:**

You must estimate the cost before the call starts. Use a conservative upper bound based on the model tier's average output length:

```
Nano estimate:     500 output tokens
Mid estimate:    1,200 output tokens
Frontier estimate: 2,000 output tokens
```

Pre-authorize based on this estimate (reserve the budget). After the stream completes, reconcile: if actual was lower, return the difference to the budget. If actual was higher (rare — models usually respect max_tokens), charge the overage and log it.

**Challenge 2 — Fallback mid-stream:**

If the model stream starts and then fails mid-response (connection drop, provider error), you can't retry the same model mid-stream. Options:

1. **Buffer and retry:** Buffer the first N tokens received. If the stream fails, retry with the next fallback model, starting from the beginning. Send the buffered start + the fresh continuation to the user. Downside: user may see a glitch.
2. **Fail fast:** Return the partial response with an error indicator. Let the user re-request. Simpler but worse UX.
3. **Non-streaming fallback:** If a streaming call fails, fall back to a non-streaming call on the next model. Add a header to the response indicating the model switch. Cleaner UX.

**Challenge 3 — Cost metering during stream:**

Track tokens as they stream. Some providers report usage in the stream's final event. Others require a separate usage lookup. Build a token counter that estimates usage from character count if explicit token counts aren't available in the stream.

---

### Q6: How do you price the service if you're building the router as a product others use?

**Answer:**

If you're building this router as a service (rather than internal infrastructure), pricing strategy is a product design question with significant engineering implications.

**Model 1 — Pass-through + margin:**
Charge users the underlying model cost + a fixed markup (e.g., 15%). Simple, transparent, but your margin depends entirely on how much you can route to cheap models.

```
User pays: $0.0003 per request (routed to nano, underlying cost $0.00026)
Your margin: $0.00004 per request (~15%)
At 10M requests/day: $400/day margin = $12,000/month
```

**Model 2 — Subscription + included credits:**
$99/month plan includes $80 in underlying API costs. You keep the $19 margin. Users pay for overages at cost + 20%. Predictable revenue, aligns incentives (you want to route cheaply to protect your margin).

**Model 3 — Compute unit (CU) abstraction:**
Don't expose token costs. Instead, define a "compute unit" (1 CU = 1 standard API call equivalent). Nano calls = 0.1 CU, mid calls = 1 CU, frontier calls = 8 CU. Price at $0.001/CU. This hides model complexity from customers while giving you flexibility to change underlying models.

**Engineering implication of each model:** Pass-through requires real-time cost reporting per request. Subscription models require monthly reconciliation and overage tracking. CU abstraction requires a CU mapping table that must be updated when models change.

**The router's value proposition in pricing:** You're not just routing — you're providing reliability (multi-provider fallback), budget management, and vendor flexibility (swap providers without changing client code). These have value beyond just cost reduction. Price accordingly.

---

## Advanced Questions

### Q7: How would you handle a situation where the complexity classifier is costing more than it saves?

**Answer:**

This is a real failure mode. The classifier runs on Haiku at ~50ms and ~$0.0001/call. If most of your traffic is already well-suited for a single tier, the classifier's cost and latency may exceed the benefit.

**Detecting the problem:**

Track two metrics monthly:
1. **Routing diversity:** What % of requests route to each tier? If 95% go to the same tier, the classifier is providing little value.
2. **Classifier ROI:** Compare monthly classifier cost vs the savings from routing to cheaper models. If classifier cost > routing savings, it's net negative.

```
Example where classifier hurts:
  100K requests/day, 92% nano, 7% mid, 1% frontier
  
  With classifier:
    Classifier cost: 100K × $0.0001 = $10/day
    Routing savings from 8% non-nano traffic:
      8,000 × mid ($0.012) vs 8,000 × frontier ($0.12) = $864 saved
    Net benefit: $854/day ✓ (classifier pays off)

  Low-value case:
    If 99% of traffic is already nano, and your default (no routing) would also be nano:
    Savings from 1% non-nano traffic = $108/day
    Classifier cost: $10/day
    Net benefit: $98/day (still positive, but marginal)
```

**Solutions if classifier ROI is poor:**

1. **Hybrid routing:** Use free rule-based routing for unambiguous cases (very short requests, explicit simple task keywords). Only invoke the classifier for genuinely ambiguous cases. This reduces classifier calls by 50-70%.

2. **Inline routing:** Embed simple routing logic in the calling application rather than in a separate service. A few regex checks and length thresholds cover 70% of routing decisions at zero cost.

3. **Tier default tuning:** If 95% of your traffic should be nano, make nano the default and only invoke the classifier (and only call mid/frontier) when the client explicitly opts in or request signals demand it.

4. **Remove the classifier entirely:** If you have a predictable workload (e.g., it's always document classification), hard-code the tier. Re-introduce routing only when workload diversifies.

---

### Q8: How would you design the system to enforce a global cost budget for a platform with millions of users — without using a central Redis instance that becomes a bottleneck?

**Answer:**

Central Redis budget enforcement works at moderate scale but becomes a bottleneck at very high request rates (> 50K requests/second) or when Redis latency is critical to overall request latency.

**Approach 1 — Token bucket with local pre-allocation:**

Each router instance pre-allocates a "token bucket" from the global budget store at startup and periodically. Instead of checking Redis on every request, each instance checks its local bucket.

```
Global Redis budget: $10,000/hour remaining
10 router instances, each pre-allocates: $1,000/hour slice

Instance behavior:
  - Deduct from local bucket on each request (in-memory, ~0.01ms)
  - When local bucket < 10%: re-request allocation from Redis (background)
  - If Redis allocation fails: use remaining local budget, then start rejecting
  - Reconcile with Redis every 30 seconds

Trade-off: In a burst scenario, instances might over-allocate by up to
  (number of instances × local bucket size). With 10 instances and $1,000 each,
  you could overspend by ~$10,000 in the worst case before rejection kicks in.
  This is acceptable for most use cases with appropriate bucket sizing.
```

**Approach 2 — Approximate counting with probabilistic rejection:**

At very high scale, exact budget tracking is less important than approximate tracking. Use a **Count-Min Sketch** data structure (probabilistic, never under-counts) stored in Redis for approximate spend tracking. Error rate is configurable — a 5% error bound means you might let through 5% over-budget traffic before rejecting.

**Approach 3 — Budget tiers with centralized enforcement only at limits:**

Track spend with loose per-second rate limiting (Token Bucket algorithm per user). Only invoke the strict central budget check when a user is approaching their monthly limit (e.g., > 80% consumed). At 80%, they switch to checked mode.

```
User with $100 budget:
  < $80 spent:    Local rate limiting only ($1/second max), no Redis check per request
  $80 - $100:     Redis check on every request (strict mode)
  > $100:         Reject all requests
```

This keeps Redis at normal load for 95% of users, while enforcing strictly for the 5% near their limits.

---

### Q9: A customer asks: "Can you guarantee that sensitive data sent to your router is never stored or used to train models?" How do you design for this?

**Answer:**

Data privacy is a first-class architectural concern for a routing layer, not a policy promise. You need to build it into the system.

**At-rest data minimization:**

The router's job is to dispatch requests — it doesn't need to store request content. **The router should not log request content by default.** It logs metadata only:

```
What to log: {timestamp, user_id, model_selected, input_token_count,
              output_token_count, latency_ms, routing_reason, cost}
What NOT to log: {request_text, response_text, system_prompt}
```

This is the default. If debugging is needed, content logging must be explicitly opt-in, with a short retention window (7 days) and customer consent.

**In-transit encryption:**

All requests pass through the router over TLS. The router decrypts only to perform routing (token counting, complexity classification). It does not decrypt to store.

**The complexity classifier problem:**

The classifier must see the request text to classify it. If the text contains PII or sensitive data, the classifier processes it. Mitigations:
- Use a self-hosted classifier (DistilBERT) rather than Haiku for classification — the request text never leaves your infrastructure
- For Haiku-based classification: use only the first 200 tokens of the request (enough to understand complexity, not full content)
- Offer a "no-classification" tier for regulated industries (the router uses rule-based routing only, no ML model sees the content)

**Model provider pass-through:**

The router passes requests to model providers (Anthropic, OpenAI, etc.). The customer's contract with the router provider should explicitly state which model providers are used and that customer data is passed to them under the provider's data processing agreements (DPAs). Customers who cannot share data with any cloud provider need a self-hosted router with self-hosted models — which is a different product tier.

**Auditable non-retention:**

For regulated industries, implement cryptographic non-retention proofs: each request is assigned a temporary ID. The ID appears in the routing log. The content is never written to any persistent store. A Merkle tree of IDs, auditable by the customer, demonstrates that all logged IDs have metadata-only records.

The honest answer to the customer: "We log metadata only by default. Request content is never stored by our system. It is transmitted to your chosen model provider under your API keys and their DPA. Here is our architecture diagram showing exactly which components see what data."

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Architecture_Blueprint.md](./Architecture_Blueprint.md) | System architecture blueprint |
| [📄 Component_Breakdown.md](./Component_Breakdown.md) | Component deep dive |
| 📄 **Interview_QA.md** | ← you are here |

⬅️ **Prev:** [07 AI Content Moderation Pipeline](../07_AI_Content_Moderation_Pipeline/Architecture_Blueprint.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Section 14 — Hugging Face Ecosystem](../../14_Hugging_Face_Ecosystem/01_Hub_and_Model_Cards/Theory.md)
