# Code Example — Observability

Complete Python examples for instrumenting an LLM application with logging, cost tracking, and Langfuse integration.

---

## Pattern 1: LLM Call Wrapper with Full Instrumentation

```python
"""
Production-ready LLM call wrapper with:
- Latency tracking
- Token + cost logging
- Error handling
- Structured log output
Requirements: pip install anthropic
"""
import time
import json
import logging
import uuid
from dataclasses import dataclass, asdict
from typing import Optional
import anthropic

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'  # JSON will be the message
)
logger = logging.getLogger("llm_observability")

# Pricing lookup (update when pricing changes)
MODEL_PRICING = {
    "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
    "claude-3-5-haiku-20241022":  {"input": 0.80, "output": 4.00},
    "claude-3-haiku-20240307":    {"input": 0.25, "output": 1.25},
}

@dataclass
class LLMCallMetrics:
    request_id: str
    model: str
    request_type: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    ttft_ms: Optional[float]
    cost_usd: float
    cache_hit: bool
    error: Optional[str]
    guardrail_triggered: bool
    timestamp: str

def compute_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    pricing = MODEL_PRICING.get(model, {"input": 3.00, "output": 15.00})
    return (input_tokens * pricing["input"] / 1_000_000 +
            output_tokens * pricing["output"] / 1_000_000)

def log_metrics(metrics: LLMCallMetrics):
    """Emit structured JSON log for aggregation by ELK, Datadog, etc."""
    logger.info(json.dumps(asdict(metrics)))

def observed_llm_call(
    messages: list,
    model: str = "claude-3-haiku-20240307",
    max_tokens: int = 512,
    request_type: str = "chat",
    system: str = "",
) -> dict:
    """
    Instrumented LLM call that logs all observability data.
    Returns: {"text": str, "metrics": LLMCallMetrics}
    """
    client = anthropic.Anthropic()
    request_id = str(uuid.uuid4())[:8]
    error = None
    response_text = ""
    input_tokens = 0
    output_tokens = 0
    ttft_ms = None

    start_time = time.time()

    try:
        kwargs = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": messages,
        }
        if system:
            kwargs["system"] = system

        response = client.messages.create(**kwargs)

        latency_ms = (time.time() - start_time) * 1000
        response_text = response.content[0].text
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens

    except anthropic.APIError as e:
        latency_ms = (time.time() - start_time) * 1000
        error = str(e)

    cost = compute_cost(model, input_tokens, output_tokens)

    metrics = LLMCallMetrics(
        request_id=request_id,
        model=model,
        request_type=request_type,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        latency_ms=round(latency_ms, 1),
        ttft_ms=ttft_ms,
        cost_usd=round(cost, 6),
        cache_hit=False,
        error=error,
        guardrail_triggered=False,
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%S.") + f"{int(time.time() % 1 * 1000):03d}Z"
    )

    log_metrics(metrics)

    if error:
        raise RuntimeError(f"LLM call failed: {error}")

    return {"text": response_text, "metrics": metrics}

# Usage
if __name__ == "__main__":
    result = observed_llm_call(
        messages=[{"role": "user", "content": "What is machine learning?"}],
        model="claude-3-haiku-20240307",
        request_type="explainer"
    )
    print(f"Response: {result['text'][:100]}")
    print(f"Latency: {result['metrics'].latency_ms}ms")
    print(f"Cost: ${result['metrics'].cost_usd}")
```

---

## Pattern 2: Streaming LLM Call with TTFT Tracking

```python
"""
Streaming LLM call that measures Time To First Token (TTFT).
TTFT is the primary latency metric for interactive chat applications.
"""
import time
import anthropic

client = anthropic.Anthropic()

def streaming_call_with_ttft(
    messages: list,
    model: str = "claude-3-haiku-20240307",
    max_tokens: int = 512,
) -> dict:
    """
    Streaming LLM call that tracks TTFT and full latency.
    Yields: text chunks as they arrive, then final metrics.
    """
    start_time = time.time()
    first_token_time = None
    full_text = []
    input_tokens = 0
    output_tokens = 0

    with client.messages.stream(
        model=model,
        max_tokens=max_tokens,
        messages=messages,
    ) as stream:
        for text_chunk in stream.text_stream:
            if first_token_time is None:
                first_token_time = time.time()
                ttft_ms = (first_token_time - start_time) * 1000
                print(f"[TTFT: {ttft_ms:.0f}ms]", end="", flush=True)
            full_text.append(text_chunk)
            print(text_chunk, end="", flush=True)  # Stream to stdout

        # Get final usage from the completed message
        final_message = stream.get_final_message()
        input_tokens = final_message.usage.input_tokens
        output_tokens = final_message.usage.output_tokens

    total_latency_ms = (time.time() - start_time) * 1000
    ttft_ms = (first_token_time - start_time) * 1000 if first_token_time else None

    print()  # Newline after streaming

    return {
        "text": "".join(full_text),
        "ttft_ms": round(ttft_ms, 1) if ttft_ms else None,
        "total_latency_ms": round(total_latency_ms, 1),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "tokens_per_second": round(output_tokens / (total_latency_ms / 1000), 1)
    }

if __name__ == "__main__":
    result = streaming_call_with_ttft(
        messages=[{"role": "user", "content": "Explain quantum computing in simple terms."}]
    )
    print(f"\n--- Metrics ---")
    print(f"TTFT: {result['ttft_ms']}ms")
    print(f"Total latency: {result['total_latency_ms']}ms")
    print(f"Output speed: {result['tokens_per_second']} tokens/sec")
```

---

## Pattern 3: Langfuse Integration

```python
"""
Full Langfuse integration for LLM observability.
Langfuse logs prompts, responses, costs, and quality scores
in a web UI you can inspect.

Requirements: pip install langfuse anthropic
Setup: Set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY env vars
  (get free keys at langfuse.com)
"""
import os
import anthropic
from langfuse import Langfuse
from langfuse.decorators import observe, langfuse_context

# Initialize clients
anthropic_client = anthropic.Anthropic()
langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host="https://cloud.langfuse.com"  # or your self-hosted URL
)

@observe(name="llm-call")  # Decorator automatically traces this function
def call_llm_traced(user_message: str, session_id: str = None) -> str:
    """
    LLM call that is automatically traced by Langfuse.
    All calls appear in the Langfuse dashboard with latency, tokens, cost.
    """
    # Update Langfuse context with metadata
    langfuse_context.update_current_observation(
        input=user_message,
        metadata={"session_id": session_id}
    )

    response = anthropic_client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=512,
        messages=[{"role": "user", "content": user_message}]
    )

    output_text = response.content[0].text

    # Log usage to Langfuse
    langfuse_context.update_current_observation(
        output=output_text,
        usage={
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens,
            "unit": "TOKENS"
        },
        model="claude-3-haiku-20240307",
        model_parameters={"max_tokens": 512}
    )

    return output_text

@observe(name="customer-support-pipeline")
def handle_support_request(user_message: str, user_id: str) -> str:
    """
    Multi-step pipeline that Langfuse tracks end-to-end.
    Shows each step as a nested span in the Langfuse trace view.
    """
    # Update parent trace metadata
    langfuse_context.update_current_trace(
        user_id=user_id,
        tags=["customer-support", "production"]
    )

    # Each @observe'd function becomes a nested span
    response = call_llm_traced(
        user_message=user_message,
        session_id=f"support_{user_id}"
    )

    return response

# Score a response (for quality tracking)
def score_response(trace_id: str, score: float, comment: str = ""):
    """Add a human or automated quality score to a Langfuse trace."""
    langfuse.score(
        trace_id=trace_id,
        name="quality",
        value=score,  # 0-1 scale
        comment=comment
    )

if __name__ == "__main__":
    # This call will appear in your Langfuse dashboard
    response = handle_support_request(
        user_message="How do I reset my password?",
        user_id="user_123"
    )
    print(f"Response: {response}")

    # Flush to ensure data is sent to Langfuse before process exits
    langfuse.flush()
```

---

## Pattern 4: Simple In-Memory Metrics Aggregator

```python
"""
Lightweight in-process metrics aggregation for development or
small-scale production. For production at scale, use Prometheus.
"""
import time
import math
from collections import defaultdict, deque
from threading import Lock
from dataclasses import dataclass

@dataclass
class PercentileStats:
    p50: float
    p95: float
    p99: float
    avg: float
    count: int

class MetricsCollector:
    """Thread-safe in-memory metrics collector."""

    def __init__(self, window_seconds: int = 3600):
        self._lock = Lock()
        self.window_seconds = window_seconds
        self.latencies: deque = deque()  # (timestamp, value)
        self.costs: deque = deque()
        self.errors: deque = deque()
        self.cache_hits: int = 0
        self.cache_misses: int = 0

    def _cleanup_old(self):
        """Remove entries older than the window."""
        cutoff = time.time() - self.window_seconds
        while self.latencies and self.latencies[0][0] < cutoff:
            self.latencies.popleft()
        while self.costs and self.costs[0][0] < cutoff:
            self.costs.popleft()
        while self.errors and self.errors[0][0] < cutoff:
            self.errors.popleft()

    def record_request(self, latency_ms: float, cost_usd: float,
                       is_error: bool = False, cache_hit: bool = False):
        now = time.time()
        with self._lock:
            self.latencies.append((now, latency_ms))
            self.costs.append((now, cost_usd))
            if is_error:
                self.errors.append((now, 1))
            if cache_hit:
                self.cache_hits += 1
            else:
                self.cache_misses += 1
            self._cleanup_old()

    def get_latency_stats(self) -> PercentileStats:
        with self._lock:
            if not self.latencies:
                return PercentileStats(0, 0, 0, 0, 0)
            values = sorted(v for _, v in self.latencies)
            n = len(values)
            return PercentileStats(
                p50=values[int(n * 0.50)],
                p95=values[int(n * 0.95)],
                p99=values[int(n * 0.99)],
                avg=sum(values) / n,
                count=n
            )

    def get_error_rate(self) -> float:
        with self._lock:
            total = len(self.latencies)
            errors = len(self.errors)
            return errors / total if total > 0 else 0.0

    def get_cache_hit_rate(self) -> float:
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 0.0

    def get_total_cost(self) -> float:
        return sum(v for _, v in self.costs)

    def report(self):
        stats = self.get_latency_stats()
        print(f"=== Metrics Report (last {self.window_seconds}s) ===")
        print(f"Total requests: {stats.count}")
        print(f"Latency — P50: {stats.p50:.0f}ms, P95: {stats.p95:.0f}ms, P99: {stats.p99:.0f}ms")
        print(f"Error rate: {self.get_error_rate():.2%}")
        print(f"Cache hit rate: {self.get_cache_hit_rate():.2%}")
        print(f"Total cost: ${self.get_total_cost():.4f}")

# Global metrics instance
metrics = MetricsCollector(window_seconds=3600)

# Wrap any LLM call
def instrumented_call(messages, model="claude-3-haiku-20240307"):
    start = time.time()
    error = False
    try:
        result = observed_llm_call(messages, model)  # From Pattern 1
        cost = result["metrics"].cost_usd
        return result["text"]
    except Exception as e:
        error = True
        cost = 0
        raise
    finally:
        latency = (time.time() - start) * 1000
        metrics.record_request(latency, cost, error)
```

---

## 📂 Navigation
