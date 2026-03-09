# Cheatsheet — Scaling AI Apps

**Scaling** is the ability to handle growing traffic — more requests, more users, more data — while maintaining acceptable latency, throughput, and reliability.

---

## Key Terms

| Term | Definition |
|---|---|
| **Horizontal scaling** | Adding more server instances behind a load balancer |
| **Vertical scaling** | Upgrading to a bigger/faster machine (more GPU, more RAM) |
| **Auto-scaling** | Automatically adding/removing instances based on load metrics |
| **Load balancer** | Distributes incoming requests across multiple server instances |
| **Request queue** | Buffer that holds incoming requests; protects servers from traffic spikes |
| **Backpressure** | Signal to clients that the system is at capacity; slow down requests |
| **Model routing** | Directing requests to different models based on complexity/cost requirements |
| **Warm instances** | Pre-started servers with models already loaded; avoids cold start latency |
| **Cold start** | Latency penalty when spinning up a new server (model loading: 30-90 seconds) |
| **SLA** | Service Level Agreement — contractual performance commitment |
| **SLO** | Service Level Objective — internal performance target (e.g., P99 < 2s) |
| **Circuit breaker** | Pattern that fails fast when a dependency is unhealthy |
| **Degraded mode** | Serving reduced functionality (e.g., cached responses) when system is under stress |

---

## Scaling Strategies Comparison

| Strategy | When to Use | Pros | Cons |
|---|---|---|---|
| **Horizontal scaling** | High request volume | Near-linear throughput increase; fault tolerant | Requires load balancer, session management |
| **Vertical scaling** | Model too large for current GPU | Simple; no architecture change | Hardware ceiling; expensive; single point of failure |
| **Auto-scaling** | Variable/bursty traffic | Cost-efficient; handles spikes | Cold start delay; warm instances needed |
| **Request queuing** | Traffic spikes, async workloads | Prevents cascades; natural backpressure | Adds latency; requires async client |
| **Model routing** | Mixed query complexity | Major cost savings; right model for each task | Routing overhead; routing classifier needed |
| **Geographic distribution** | Global users; compliance | Latency reduction; data residency | High infrastructure complexity and cost |
| **Caching** | Repeated inputs | Near-zero cost/latency for hits | Memory cost; invalidation complexity |

---

## Auto-Scaling Triggers

| Trigger Metric | Scale Up When | Scale Down When |
|---|---|---|
| **GPU utilization** | > 80% for 2 minutes | < 30% for 10 minutes |
| **Request queue depth** | > 100 requests waiting | < 10 requests waiting |
| **P99 latency** | > 2× baseline for 3 minutes | < 0.8× baseline for 10 minutes |
| **Requests/second** | > 70% of max capacity | < 30% of max capacity |

---

## Kubernetes HPA Example for LLM Serving

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: llm-inference-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: llm-inference
  minReplicas: 2        # Always keep 2 warm (avoid cold starts)
  maxReplicas: 20       # Cap at 20 (cost control)
  metrics:
  - type: External
    external:
      metric:
        name: queue_depth
      target:
        type: AverageValue
        averageValue: "50"   # Scale up when avg queue > 50 requests per pod
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60      # Wait 60s before scaling up again
      policies:
      - type: Pods
        value: 2                          # Add max 2 pods at a time
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300     # Wait 5 min before scaling down
```

---

## Request Queue Pattern

```python
# Async queue-based architecture
# Producer (API endpoint):
import redis
import json

r = redis.Redis()

def submit_request(user_input: str, callback_url: str) -> str:
    job_id = generate_id()
    r.lpush("inference_queue", json.dumps({
        "job_id": job_id,
        "input": user_input,
        "callback_url": callback_url,
        "timestamp": time.time()
    }))
    return job_id  # Return immediately; don't wait for inference

# Consumer (worker process):
def process_queue():
    while True:
        _, job_json = r.brpop("inference_queue", timeout=5)
        job = json.loads(job_json)
        result = run_inference(job["input"])
        # Notify client via callback or store result
        r.setex(f"result:{job['job_id']}", 3600, result)
```

---

## Model Routing Pattern

```python
def route_request(query: str) -> str:
    """Route to cheap or expensive model based on query complexity."""
    # Cheap heuristics (no LLM call):
    token_count = len(query.split())

    # Simple: short query with common patterns → cheap model
    if token_count < 50 and not needs_reasoning(query):
        return "claude-3-haiku-20240307"   # 25x cheaper

    # Complex: long query or reasoning needed → powerful model
    return "claude-3-5-sonnet-20241022"

def needs_reasoning(query: str) -> bool:
    """Quick check if query needs multi-step reasoning."""
    reasoning_signals = ["why", "analyze", "compare", "explain how", "what would happen"]
    return any(signal in query.lower() for signal in reasoning_signals)
```

---

## SLA Design Template

| Tier | P50 Latency | P99 Latency | Availability | Error Rate |
|---|---|---|---|---|
| **Interactive (chat)** | < 500ms | < 2,000ms | 99.9% | < 0.1% |
| **Near-real-time (API)** | < 1,000ms | < 5,000ms | 99.5% | < 0.5% |
| **Batch processing** | N/A (throughput) | < 30 min/job | 99% | < 1% |
| **Background jobs** | N/A | Best effort | 99% | < 2% |

---

## Degraded Mode Strategies

When your system is under extreme load, serve a degraded experience instead of failing:

| Strategy | Implementation | User Experience |
|---|---|---|
| **Cached responses** | Return stale-but-valid cached answer | Slightly outdated, but instant |
| **Simplified model** | Fall back to a smaller, faster model | Lower quality, but responds |
| **Queued with ETA** | Accept request, return estimated wait time | User waits, doesn't abandon |
| **Feature disable** | Disable non-essential features (e.g., streaming) | Core functionality maintained |
| **Rate limiting** | Return 429, tell user to retry later | Some users rejected gracefully |

---

## Geographic Distribution Considerations

| Concern | Solution |
|---|---|
| **Latency** | Deploy inference servers in regions close to users (US-East, EU-West, AP) |
| **Data residency (GDPR)** | EU user data must not leave EU → route EU users to EU region |
| **Failover** | If US-East fails, route traffic to US-West or EU |
| **Model replication** | Maintain the same model version in all regions (deployment automation needed) |
| **Cost** | Regions have different GPU pricing; consider latency vs cost tradeoff |

---

## Golden Rules

- **Design for horizontal scaling from day one** — adding a load balancer later is an architecture refactor
- **Queue async tasks** — anything taking > 2 seconds should be asynchronous
- **Keep minimum 2 warm instances** — never scale to zero for real-time applications
- **Set auto-scaling targets at 70% GPU utilization** — leave headroom for spikes
- **Rate limit at the API gateway** — before requests hit expensive inference
- **Circuit breaker for external dependencies** — if your vector DB is slow, fail fast rather than queue up
- **Test your scaling limits** — load test before launch, not after a viral moment
- **Have a degraded mode plan** — what do you serve when at 200% capacity?

---

## 📂 Navigation
