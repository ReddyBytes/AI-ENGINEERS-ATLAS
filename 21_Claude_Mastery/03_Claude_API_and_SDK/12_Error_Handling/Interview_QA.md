# Error Handling — Interview Q&A

## Beginner Questions

**Q1: What are the three types of errors you should NEVER retry with the Anthropic API?**

A: `AuthenticationError` (401 — bad API key, retrying won't fix it), `BadRequestError` (400 — your request body is malformed, retrying won't fix it), and `PermissionDeniedError` (403 — permission issue with your account/tier, retrying won't fix it). These require code or configuration changes, not retries.

---

**Q2: What is exponential backoff and why does it use jitter?**

A: Exponential backoff means waiting progressively longer between retry attempts — 1s, 2s, 4s, 8s, 16s, etc. This prevents hammering a struggling API with rapid retries. Jitter adds a small random amount (e.g., 0-1 second) to each wait. Without jitter, hundreds of clients that all hit a rate limit simultaneously will all wait the same amount and all retry at the same instant — creating a synchronized spike called the "thundering herd problem." Jitter desynchronizes retries, spreading the load.

---

**Q3: What exception does the SDK raise when you hit a rate limit?**

A: `anthropic.RateLimitError`. It corresponds to HTTP 429. The response includes `retry-after` and `x-ratelimit-reset-requests` headers indicating when you can retry. Your retry logic should respect this header when present.

---

**Q4: What is the `request_id` field and why should you log it?**

A: The `request_id` is a unique identifier for each API call assigned by Anthropic's servers. It appears on both successful responses (`response.id`) and in error exceptions. If you contact Anthropic support about a specific failed call, providing the `request_id` allows them to look up the exact request and diagnose the issue. Always log it alongside the error details.

---

## Intermediate Questions

**Q5: Write a retry decorator using tenacity for Claude API calls.**

A: 
```python
from tenacity import retry, stop_after_attempt, wait_exponential, wait_random, retry_if_exception_type
import anthropic

RETRYABLE = (anthropic.RateLimitError, anthropic.APIConnectionError, 
             anthropic.InternalServerError, anthropic.APITimeoutError)

@retry(
    retry=retry_if_exception_type(RETRYABLE),
    wait=wait_exponential(multiplier=1, min=1, max=60) + wait_random(0, 1),
    stop=stop_after_attempt(5),
    reraise=True,
)
def call_claude(prompt: str) -> str:
    return client.messages.create(
        model="claude-sonnet-4-6", max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    ).content[0].text
```

---

**Q6: What is the circuit breaker pattern and when is it useful for Claude API integrations?**

A: A circuit breaker monitors failure counts. When failures exceed a threshold, it "opens the circuit" — all subsequent calls are immediately rejected with an error without even hitting the API. After a cooldown period, it enters "half-open" state and allows one test call. If the test succeeds, the circuit closes and normal operation resumes. This prevents cascading failures where a slow/down API causes your application to queue up thousands of pending retries, consuming threads, memory, and rate-limit budget. Use it in high-traffic production systems where a downstream failure could take down your entire application.

---

**Q7: How should you handle the `BadRequestError` (400) in a production pipeline?**

A: Never retry it — the request body is invalid and retrying would just fail again. In a pipeline: (1) Log the full error message, the request parameters (sanitized of PII), and the `request_id`. (2) Alert your engineering team — this usually indicates a bug in prompt construction code. (3) Move the failing record to a "dead letter queue" for manual review. (4) Continue processing the rest of the batch. Common causes: invalid model ID, malformed messages array (consecutive same-role messages), max_tokens below minimum, or a parameter type mismatch.

---

**Q8: What is idempotency and why does it matter for retrying Claude API calls?**

A: Idempotency means calling an operation multiple times produces the same result as calling it once. The Claude messages API is naturally idempotent from a model perspective — retrying a call generates a new response (which may differ slightly), but no server-side state is mutated. The risk is on your application side: if you retry a call and your application processes the response twice (writes to database, sends email, charges a user), you have a non-idempotent side effect. Before retrying, ensure your application tracks whether the response has already been processed — use a `request_id` or `custom_id` as a deduplication key.

---

## Advanced Questions

**Q9: Design a production-grade API client wrapper with retry, circuit breaker, and observability.**

A:
```python
import time, random, logging
from dataclasses import dataclass
import anthropic

logger = logging.getLogger(__name__)

@dataclass
class APIClient:
    client: anthropic.Anthropic = None
    failures: int = 0
    failure_threshold: int = 5
    circuit_open_until: float = 0
    
    def __post_init__(self):
        self.client = anthropic.Anthropic()
    
    def create(self, **kwargs) -> anthropic.types.Message:
        # Circuit breaker check
        if time.time() < self.circuit_open_until:
            raise RuntimeError("Circuit OPEN — API calls blocked")
        
        for attempt in range(5):
            start = time.time()
            try:
                response = self.client.messages.create(**kwargs)
                self.failures = 0  # reset on success
                latency = (time.time() - start) * 1000
                logger.info("api_success", extra={
                    "attempt": attempt+1, "latency_ms": latency,
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "request_id": response.id,
                })
                return response
            except (anthropic.RateLimitError, anthropic.APIConnectionError,
                    anthropic.InternalServerError) as e:
                self.failures += 1
                if self.failures >= self.failure_threshold:
                    self.circuit_open_until = time.time() + 60
                    logger.error("circuit_opened")
                    raise RuntimeError("Circuit opened") from e
                if attempt == 4:
                    raise
                wait = (2**attempt) + random.uniform(0, 1)
                logger.warning(f"retry_{attempt+1}", extra={"wait_s": wait, "error": str(e)})
                time.sleep(wait)
            except (anthropic.AuthenticationError, anthropic.BadRequestError):
                raise  # never retry
```

---

**Q10: How do you handle errors differently in a synchronous web endpoint vs an async background job?**

A: In a synchronous web endpoint (e.g., FastAPI route), errors must be handled quickly to release the connection: catch retryable errors at most 2-3 times with short waits, then return an HTTP error to the client. Don't block a web worker for 60 seconds retrying. Better: push the work to a background queue and return a job ID immediately. In a background job (worker, batch processor), you can be more aggressive: 5 retry attempts, longer backoff, circuit breaker, dead-letter queue for ultimate failures, alerting. The key insight is that web endpoints must return in milliseconds-to-seconds; background jobs can spend minutes on retry logic.

---

**Q11: Explain how you would implement per-error-type alerting for a production Claude integration.**

A: Classify errors into categories and alert differently: (1) `AuthenticationError`: page on-call immediately — the integration is completely broken. (2) `RateLimitError` spike (>5% of calls in a 5-minute window): page engineering — something is hammering the API or traffic is growing beyond limits. (3) `InternalServerError` rate >1%: create a ticket — may indicate Anthropic service degradation. (4) `BadRequestError` any occurrence: create a bug ticket — indicates a code regression in prompt construction. (5) Latency p99 >30s: alert — something is wrong with the network or Anthropic performance. Use Prometheus counters per error type, Grafana dashboards, and PagerDuty for severity mapping.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept guide |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Working code |

⬅️ **Prev:** [Cost Optimization](../11_Cost_Optimization/Interview_QA.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Model Reference](../13_Model_Reference/Interview_QA.md)
