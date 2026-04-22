# Error Handling — Code Examples

## Example 1: Basic exception handling

```python
import anthropic

client = anthropic.Anthropic()

def safe_call(prompt: str) -> str:
    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    
    except anthropic.AuthenticationError as e:
        raise RuntimeError(f"Invalid API key: {e.message}") from e
    except anthropic.RateLimitError:
        raise  # handled by retry layer above
    except anthropic.BadRequestError as e:
        raise ValueError(f"Invalid request parameters: {e.message}") from e
    except anthropic.APIConnectionError as e:
        raise  # network issue — let retry layer handle
    except anthropic.APIStatusError as e:
        raise RuntimeError(f"API returned {e.status_code}: {e.message}") from e
```

---

## Example 2: Tenacity-based retry decorator

```python
import anthropic
from tenacity import (
    retry, stop_after_attempt,
    wait_exponential, wait_random,
    retry_if_exception_type,
    before_sleep_log,
)
import logging

logger = logging.getLogger(__name__)
client = anthropic.Anthropic()

RETRYABLE = (
    anthropic.RateLimitError,
    anthropic.APIConnectionError,
    anthropic.APITimeoutError,
    anthropic.InternalServerError,
)

@retry(
    retry=retry_if_exception_type(RETRYABLE),
    wait=wait_exponential(multiplier=1, min=1, max=60) + wait_random(0, 1),
    stop=stop_after_attempt(5),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
def call_with_retry(prompt: str, model: str = "claude-sonnet-4-6") -> str:
    response = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text

# Usage
try:
    result = call_with_retry("Explain quantum computing.")
    print(result)
except anthropic.RateLimitError:
    print("Rate limited after 5 attempts — try again later")
except anthropic.APIConnectionError:
    print("Network unreachable — check connection")
```

---

## Example 3: Manual backoff with logging

```python
import anthropic
import time
import random
import logging

logger = logging.getLogger(__name__)
client = anthropic.Anthropic()

def call_with_manual_backoff(prompt: str, max_attempts: int = 5) -> str:
    last_exception = None
    
    for attempt in range(1, max_attempts + 1):
        try:
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            logger.info(f"Success on attempt {attempt}")
            return response.content[0].text
        
        except anthropic.AuthenticationError:
            logger.error("Authentication failed — check ANTHROPIC_API_KEY")
            raise  # never retry
        
        except anthropic.BadRequestError as e:
            logger.error(f"Bad request: {e.message}")
            raise  # never retry
        
        except (anthropic.RateLimitError, anthropic.APIConnectionError,
                anthropic.InternalServerError) as e:
            last_exception = e
            if attempt == max_attempts:
                logger.error(f"Exhausted {max_attempts} attempts: {type(e).__name__}")
                raise
            
            wait = min(2 ** (attempt - 1), 60) + random.uniform(0, 1)
            logger.warning(
                f"Attempt {attempt} failed ({type(e).__name__}). "
                f"Retrying in {wait:.1f}s"
            )
            time.sleep(wait)
    
    raise last_exception
```

---

## Example 4: Circuit breaker implementation

```python
import anthropic
import time

class CircuitBreaker:
    """Simple circuit breaker for the Anthropic API."""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.opened_at = None
        self.state = "CLOSED"  # CLOSED | OPEN | HALF_OPEN
    
    def _can_pass(self) -> bool:
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            if time.time() - self.opened_at >= self.recovery_timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        if self.state == "HALF_OPEN":
            return True
        return False
    
    def _record_success(self):
        self.failures = 0
        self.state = "CLOSED"
    
    def _record_failure(self):
        self.failures += 1
        if self.failures >= self.failure_threshold or self.state == "HALF_OPEN":
            self.state = "OPEN"
            self.opened_at = time.time()
            print(f"Circuit OPENED after {self.failures} failures")
    
    def call(self, client, **kwargs):
        if not self._can_pass():
            remaining = self.recovery_timeout - (time.time() - self.opened_at)
            raise RuntimeError(f"Circuit OPEN. Retry in {remaining:.0f}s")
        
        try:
            response = client.messages.create(**kwargs)
            self._record_success()
            return response
        except (anthropic.InternalServerError, anthropic.APIConnectionError) as e:
            self._record_failure()
            raise

# Usage
client = anthropic.Anthropic()
cb = CircuitBreaker(failure_threshold=3, recovery_timeout=30)

try:
    resp = cb.call(client, model="claude-sonnet-4-6", max_tokens=128,
                   messages=[{"role": "user", "content": "Hello!"}])
    print(resp.content[0].text)
except RuntimeError as e:
    print(f"Circuit blocked: {e}")
```

---

## Example 5: Production client with full observability

```python
import anthropic
import time
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class ProductionClient:
    model: str = "claude-sonnet-4-6"
    max_retries: int = 5
    _client: anthropic.Anthropic = field(default_factory=anthropic.Anthropic)
    _total_calls: int = 0
    _total_errors: int = 0
    
    def create(self, **kwargs) -> anthropic.types.Message:
        self._total_calls += 1
        kwargs.setdefault("model", self.model)
        
        for attempt in range(1, self.max_retries + 1):
            start_time = time.monotonic()
            try:
                response = self._client.messages.create(**kwargs)
                latency_ms = (time.monotonic() - start_time) * 1000
                
                logger.info("api_success", extra={
                    "model": response.model,
                    "latency_ms": round(latency_ms),
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "cache_read": response.usage.cache_read_input_tokens,
                    "stop_reason": response.stop_reason,
                    "request_id": response.id,
                    "attempt": attempt,
                })
                return response
            
            except anthropic.AuthenticationError:
                logger.critical("auth_error — check ANTHROPIC_API_KEY")
                raise
            
            except anthropic.BadRequestError as e:
                logger.error("bad_request", extra={"message": e.message, "request_id": getattr(e, 'request_id', None)})
                raise
            
            except (anthropic.RateLimitError, anthropic.APIConnectionError, 
                    anthropic.InternalServerError) as e:
                self._total_errors += 1
                if attempt == self.max_retries:
                    logger.error("exhausted_retries", extra={"error_type": type(e).__name__})
                    raise
                
                wait = min(2 ** (attempt - 1), 60) + (time.time() % 1)  # jitter
                logger.warning("retrying", extra={
                    "attempt": attempt, "wait_s": round(wait, 1),
                    "error_type": type(e).__name__
                })
                time.sleep(wait)
    
    def stats(self) -> dict:
        return {
            "total_calls": self._total_calls,
            "total_errors": self._total_errors,
            "error_rate": self._total_errors / max(self._total_calls, 1),
        }

# Usage
prod_client = ProductionClient()
response = prod_client.create(
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.content[0].text)
print(prod_client.stats())
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept guide |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [Cost Optimization](../11_Cost_Optimization/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Model Reference](../13_Model_Reference/Theory.md)
