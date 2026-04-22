# Error Handling — Cheatsheet

## Exception Hierarchy

```
anthropic.APIError
├── anthropic.APIStatusError
│   ├── anthropic.BadRequestError          # 400 — fix your request
│   ├── anthropic.AuthenticationError      # 401 — check API key
│   ├── anthropic.PermissionDeniedError    # 403 — check permissions
│   ├── anthropic.NotFoundError            # 404 — wrong model/endpoint
│   ├── anthropic.UnprocessableEntityError # 422 — invalid params
│   ├── anthropic.RateLimitError           # 429 — back off + retry
│   └── anthropic.InternalServerError      # 500/529 — retry
├── anthropic.APIConnectionError           # network failure — retry
└── anthropic.APITimeoutError              # timeout — retry
```

---

## Basic Error Handler

```python
try:
    response = client.messages.create(...)
except anthropic.AuthenticationError:
    raise  # fail fast — bad key, no retry
except anthropic.BadRequestError as e:
    raise ValueError(f"Bad request: {e.message}")  # fix code, no retry
except (anthropic.RateLimitError, anthropic.APIConnectionError,
        anthropic.InternalServerError):
    raise  # let retry logic handle these
except anthropic.APIStatusError as e:
    raise RuntimeError(f"API {e.status_code}: {e.message}")
```

---

## Retry with Tenacity (Recommended)

```python
from tenacity import retry, stop_after_attempt, wait_exponential, wait_random, retry_if_exception_type
import anthropic

RETRYABLE = (anthropic.RateLimitError, anthropic.APIConnectionError, 
             anthropic.APITimeoutError, anthropic.InternalServerError)

@retry(
    retry=retry_if_exception_type(RETRYABLE),
    wait=wait_exponential(min=1, max=60) + wait_random(0, 1),
    stop=stop_after_attempt(5),
    reraise=True,
)
def call_claude(prompt: str) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text
```

---

## Manual Backoff

```python
import time, random

for attempt in range(5):
    try:
        return client.messages.create(...)
    except (anthropic.RateLimitError, anthropic.APIConnectionError) as e:
        if attempt == 4:
            raise
        wait = (2 ** attempt) + random.uniform(0, 1)
        time.sleep(wait)
```

---

## Retry Decision Table

| Exception | Retry? | Action |
|---|---|---|
| `AuthenticationError` | Never | Fix API key |
| `BadRequestError` | Never | Fix request body |
| `PermissionDeniedError` | Never | Fix permissions |
| `RateLimitError` | Yes + backoff | Respect retry-after |
| `APIConnectionError` | Yes + backoff | Check network |
| `APITimeoutError` | Yes + backoff | Increase timeout |
| `InternalServerError` | Yes + backoff | Wait and retry |

---

## Error Logging Template

```python
except anthropic.APIStatusError as e:
    logger.error("api_error", extra={
        "status_code": e.status_code,
        "error_type": type(e).__name__,
        "message": e.message,
        "request_id": getattr(e, 'request_id', None),
    })
```

---

## Backoff Schedule (5 attempts)

| Attempt | Wait (approx) |
|---|---|
| 1 | Immediate |
| 2 | 1–2 seconds |
| 3 | 3–5 seconds |
| 4 | 9–13 seconds |
| 5 | 30–60 seconds |

Always add ±1s jitter to prevent thundering herd.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept guide |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Working code |

⬅️ **Prev:** [Cost Optimization](../11_Cost_Optimization/Cheatsheet.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Model Reference](../13_Model_Reference/Cheatsheet.md)
