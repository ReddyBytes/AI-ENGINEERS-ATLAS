# Interview QA — Scaling AI Apps

## Beginner

**Q1: What is the difference between horizontal and vertical scaling for AI inference?**

<details>
<summary>💡 Show Answer</summary>

**A:** **Vertical scaling** means upgrading the individual machine: swap a T4 GPU for an A100, or add more RAM. It's simple — no architecture changes required — but it has a ceiling (there's no bigger machine than the biggest available GPU) and creates a single point of failure.

**Horizontal scaling** means adding more machines: instead of one inference server, you run three behind a load balancer. Traffic is distributed across all three. Benefits: near-linear throughput increase (3 servers ≈ 3x capacity), fault tolerance (if one server fails, the other two continue), and no single hardware ceiling. Downside: requires a load balancer and more complex infrastructure.

For AI specifically, vertical scaling matters because some models need a minimum VRAM threshold (e.g., a 70B float16 model needs 140GB VRAM — that's two A100 80GB GPUs). Once you've right-sized the hardware for the model, horizontal scaling handles traffic growth.

The practical approach: vertical scale to fit your model, then horizontal scale for traffic. Never try to handle 100x traffic with just a bigger GPU.

</details>

---

<br>

**Q2: Why is request queuing important for AI systems, and how does it protect against traffic spikes?**

<details>
<summary>💡 Show Answer</summary>

**A:** Without a queue, traffic spikes hit your inference servers directly. Inference servers have a fixed capacity — if you suddenly receive 10x normal traffic, each request waits in the server's internal queue, processing time increases, timeouts start happening, and the server may crash.

A **request queue** (Redis, SQS, Kafka) sits between the client and the inference server:
- Requests are immediately accepted and placed in the queue (fast, no model required)
- Worker processes pull from the queue at the rate they can handle
- The queue absorbs the spike: requests wait, but nothing crashes
- Clients either poll for results or receive a webhook when done

This provides **backpressure**: when the queue is full, you can return a "too busy, retry later" message rather than timing out. It's the difference between a graceful "please wait" and a catastrophic "error 503" under load.

For AI specifically, this matters because inference is slow (100ms-5s per request). Synchronous serving under heavy load immediately cascades into timeouts. Any LLM application expecting variable or growing traffic should use queue-based processing for requests that take more than ~500ms.

</details>

---

<br>

**Q3: What is a cold start in the context of AI serving and how do you mitigate it?**

<details>
<summary>💡 Show Answer</summary>

**A:** A **cold start** happens when a new inference server instance spins up and needs to load the model into GPU memory before it can serve requests. This takes 30-90 seconds for large models (loading billions of parameters from disk to VRAM).

This creates a problem with auto-scaling: if traffic suddenly spikes and you auto-scale from 2 to 6 instances, those 4 new instances are unavailable for 30-90 seconds. During that window, the existing 2 instances are overwhelmed. By the time new instances are ready, some users have already timed out.

**Mitigation strategies:**

1. **Minimum warm instances**: Configure auto-scaling to never scale below 2-3 instances. The minimum instances are always warm and ready. This has a cost (you're paying for idle capacity) but is essential for production SLAs.

2. **Over-provisioning for anticipated spikes**: If you know Monday mornings are 3x normal traffic, pre-scale before Monday arrives — don't wait for the spike to trigger auto-scaling.

3. **Container image optimization**: Keep model weights cached in the container image layer (not downloaded at startup). This can reduce cold start from 60s to 15s.

4. **Kubernetes KEDA (event-driven autoscaling)**: Scale up based on queue depth *before* servers are overwhelmed, giving new instances time to warm up.

5. **Serverless warm pools** (AWS Lambda Provisioned Concurrency, etc.): Keep N instances perpetually warm.

</details>

---

## Intermediate

**Q4: How would you design a multi-model routing architecture that balances cost and quality?**

<details>
<summary>💡 Show Answer</summary>

**A:** Multi-model routing (also called "cascade" or "tiered" serving) routes each request to the appropriate model tier based on estimated complexity.

**Architecture:**

1. **Routing layer** (fast, cheap): Classifies incoming requests into tiers. Options:
   - Rule-based: input length, presence of specific keywords, user tier
   - Small classifier: a 0.1B parameter classification model that runs in < 10ms
   - Embedding similarity: compare to examples of "simple" vs "complex" queries

2. **Tier 1 — Fast/Cheap model**: Handles 60-80% of requests. Small model or cheap API tier (Claude Haiku, GPT-4o-mini, Llama 7B). 10-25x cheaper than Tier 2.

3. **Tier 2 — Powerful model**: Handles 20-40% of requests. Large model for complex reasoning (Claude Sonnet/Opus, GPT-4o, Llama 70B).

4. **Confidence-based escalation**: If Tier 1's output confidence is low (e.g., log probability below threshold), automatically escalate to Tier 2. Requires calibrated confidence scores.

**Cost impact example:**
```
Without routing: 100% requests → GPT-4o at $0.015/request → $15,000/day at 1M req/day
With routing:    70% → GPT-4o-mini at $0.00046/request
                 30% → GPT-4o at $0.015/request
                 Blended cost: $0.007/request → $7,000/day
                 Savings: 53%
```

**Monitoring requirements:** Track quality metrics per tier. If Tier 1 quality drops, adjust routing threshold upward (send more to Tier 2). Quality and cost metrics must be tracked together.

</details>

---

<br>

**Q5: What is the circuit breaker pattern and how does it apply to AI systems?**

<details>
<summary>💡 Show Answer</summary>

**A:** The circuit breaker pattern prevents cascading failures when a dependency becomes slow or unavailable. It's named after an electrical circuit breaker that cuts power when there's a fault, preventing damage.

In software: instead of every request waiting indefinitely for a failing service, the circuit breaker "opens" after a threshold of failures — immediately returning an error to callers without waiting for the downstream service. This protects upstream services from backing up with stuck requests.

**States:**
- **Closed** (normal): Requests flow through. Monitor failure rate.
- **Open** (fault detected): Immediately return error/fallback without calling downstream. Reset timer starts.
- **Half-open** (testing recovery): Allow a few requests through. If they succeed → close. If they fail → open again.

**AI-specific applications:**

1. **LLM API circuit breaker**: If OpenAI/Anthropic API returns 5xx errors for 3 consecutive requests, open the circuit for 30 seconds. During this time, return cached responses or a simplified local model's output instead of waiting for timeouts.

```python
from pybreaker import CircuitBreaker

api_breaker = CircuitBreaker(
    fail_max=3,           # Open after 3 failures
    reset_timeout=30,     # Try again after 30 seconds
)

@api_breaker
def call_llm_api(prompt):
    return client.messages.create(...)  # Raises exception if circuit is open
```

2. **Vector DB circuit breaker**: If your vector database becomes slow (query latency > 2s), open the circuit and fall back to lexical search or skip retrieval entirely.

3. **Cascading failure prevention**: In a multi-step AI pipeline (retrieve → rerank → generate), if the reranker becomes slow, the circuit breaker ensures the generation step doesn't pile up waiting — it either skips reranking or uses a faster fallback.

</details>

---

<br>

**Q6: How would you implement geographic distribution for an AI application serving users globally, given that model weights are large?**

<details>
<summary>💡 Show Answer</summary>

**A:** Geographic distribution for AI is harder than for stateless web apps because model weights are large (7-140 GB) and must be loaded on every server in every region.

**Architecture approach:**

**Option A: Full replication**
Deploy the complete model + serving infrastructure in each region. All regions are identical. Global load balancer routes users to nearest region.
- Pros: Lowest latency; data stays in region (GDPR compliance)
- Cons: 3x infrastructure cost for 3 regions; deployment must update all regions

**Option B: Hub-and-spoke**
Only deploy large models in a few regions (hubs). For most users, route to nearest hub. Only deploy a lightweight model locally.
- Pros: Lower cost; easier to maintain
- Cons: Cross-region latency for users far from hubs

**Implementation components:**

1. **Anycast DNS or Global Load Balancer**: Routes users to nearest healthy region. Tools: AWS Route53 latency-based routing, GCP Global Load Balancer, Cloudflare.

2. **Model registry with regional replication**: Store model artifacts in a central registry (S3, GCS). On new deployment, all regions pull the same model version. This ensures consistency.

3. **Regional deployment automation**: Same Kubernetes manifests applied to all regions simultaneously. Tools: ArgoCD (GitOps), Helm with region-specific values.

4. **Cross-region failover**: If US-East is unavailable, traffic automatically reroutes to US-West or EU-West. Configure health check thresholds and failover policies.

5. **Data compliance routing**: Tag requests by user region. Force EU user data to stay in EU region (implement at the API gateway layer). This is required for GDPR compliance.

**Practical guidance for most teams**: Start with a single region. Add a second region when either (a) latency from Region A is causing user friction in Region B, or (b) you have compliance requirements. Don't prematurely distribute — it adds enormous complexity.

</details>

---

## Advanced

**Q7: How would you design a queue-based AI processing system that handles 10 million requests per day with variable latency requirements?**

<details>
<summary>💡 Show Answer</summary>

**A:** At 10M requests/day ≈ 116 requests/second average (with peaks potentially 5-10x that), a queue-based architecture is mandatory.

**Architecture:**

```
Tier 1 — Real-time queue (SLA: < 2s P99):
  Clients → API Gateway → "rt_queue" → Dedicated fast workers (8+ instances)
  Workers: Poll queue, process immediately, push result to result store
  Queue technology: Redis Streams (low latency, in-memory)

Tier 2 — Standard queue (SLA: < 30s P99):
  Clients → API Gateway → "standard_queue" → Standard workers (4 instances)
  Queue technology: SQS or Redis Streams with lower priority

Tier 3 — Batch queue (SLA: < 10 minutes P99):
  Clients → "batch_queue" → Batch workers (spot instances, scale to zero)
  Queue technology: SQS or Kafka
  Workers: Spin up spot instances when queue depth > 1,000
```

**Result store pattern:**
```python
# Client flow:
job_id = submit_to_queue(request, tier="realtime")
# Poll for result:
result = await poll_result(job_id, timeout=2.0)  # Tier 1 SLA
# Or use webhooks:
result = await wait_for_webhook(job_id, callback_url)
```

**Scaling the workers:**
- Real-time workers: HPA based on queue depth metric in Redis
- Batch workers: KEDA (Kubernetes Event-Driven Autoscaling) based on SQS queue depth
- Spot instances for batch (70-90% cost savings; interruptions handled by requeueing)

**At 10M/day with 50% caching:** 5M actual inference calls/day. At 116 RPS peak × 3 peak factor = 350 RPS. At 200ms inference: need ~70 concurrent workers. With 10 workers per inference server: 7 servers. This is manageable.

**Monitoring:**
- Queue depth per tier (alert: RT queue > 1,000 for > 30s)
- Job wait time per tier
- Worker utilization
- Expired/dead-letter jobs (jobs that failed or expired)

</details>

---

<br>

**Q8: How would you design a rollout strategy for a new model version in a high-traffic production AI system?**

<details>
<summary>💡 Show Answer</summary>

**A:** Rolling out a new model version to a production system with millions of users requires careful staging. The goal: catch regressions before they affect all users, with the ability to roll back within minutes.

**Phase 1: Shadow mode (1-2 days)**
Run the new model on a copy of 5-10% of live traffic (shadowed). Serve the old model's response to users. Compare new model's outputs to old model's outputs offline. No user impact if new model has issues.

```
Live request → Old Model → User receives response
              ↘ New Model → Result stored for offline comparison
```

**Phase 2: Canary (2-5 days)**
Route 1-5% of real traffic to the new model. Users in the canary group actually receive new model responses.
- Monitor: latency, error rate, quality scores, user signals (regenerations, etc.)
- Auto-rollback trigger: if error rate > 2x baseline or P99 latency > 3x baseline for 5 minutes

**Phase 3: Progressive rollout (1-2 weeks)**
Gradually increase traffic to new model: 5% → 10% → 25% → 50% → 100%
Each step: wait 24 hours, review metrics, proceed only if stable.

**Phase 4: Full rollout**
100% traffic to new model. Keep old model hot (loaded in memory) for 48 hours in case emergency rollback is needed.

**Implementation:**
- Feature flags control routing percentages (can be changed instantly without redeployment)
- Old model kept warm (not terminated) until rollout is complete and stable
- Automated rollback: SLO violation alert → Immediately flip feature flag to 0% → All traffic back to old model
- Never delete old model artifact until new model has been stable for 7+ days

**Key metrics for each rollout stage:**
- Technical: latency P50/P99, error rate, cost per request
- Quality: LLM judge score on sampled requests, user regeneration rate
- Business: task completion rate, session length, explicit feedback

</details>

---

## 📂 Navigation
