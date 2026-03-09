# Code Example — Caching Strategies

Complete, runnable Python implementations of all three caching patterns.

---

## Pattern 1: Exact-Match Cache with Redis

The simplest and fastest caching pattern. Works when inputs repeat exactly.

```python
"""
Exact-match LLM caching with Redis.
Requirements: pip install redis anthropic
"""
import hashlib
import json
import time
import redis
import anthropic

# Redis connection
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Anthropic client
client = anthropic.Anthropic()

def make_cache_key(model: str, messages: list, max_tokens: int) -> str:
    """Create a deterministic, unique cache key from the full request parameters."""
    payload = json.dumps({
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens
    }, sort_keys=True)
    return f"llm_cache:{hashlib.sha256(payload.encode()).hexdigest()}"

def cached_llm_call(
    messages: list,
    model: str = "claude-3-haiku-20240307",
    max_tokens: int = 512,
    ttl_seconds: int = 3600,  # Cache for 1 hour
) -> dict:
    """
    Make an LLM call with exact-match caching.
    Returns the response text plus cache metadata.
    """
    key = make_cache_key(model, messages, max_tokens)

    # Check cache
    cached = r.get(key)
    if cached:
        return {
            "text": cached,
            "cached": True,
            "cache_key": key,
            "latency_ms": 0
        }

    # Cache miss — call LLM
    start = time.time()
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        messages=messages
    )
    latency_ms = (time.time() - start) * 1000

    response_text = response.content[0].text

    # Store in cache
    r.setex(key, ttl_seconds, response_text)

    return {
        "text": response_text,
        "cached": False,
        "cache_key": key,
        "latency_ms": round(latency_ms, 1),
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens
    }

# Usage example
if __name__ == "__main__":
    messages = [{"role": "user", "content": "What is the capital of France?"}]

    # First call — cache miss
    result = cached_llm_call(messages)
    print(f"Call 1: cached={result['cached']}, latency={result['latency_ms']}ms")
    print(f"Answer: {result['text']}")

    # Second call — cache hit (instant)
    result = cached_llm_call(messages)
    print(f"Call 2: cached={result['cached']}, latency={result['latency_ms']}ms")
```

---

## Pattern 2: Semantic Cache with Redis Vector Search

Handles paraphrases and similar questions using embeddings.

```python
"""
Semantic caching using Redis vector search.
Requirements: pip install redis anthropic openai numpy
Note: Requires Redis Stack (for vector search) — run with:
  docker run -d --name redis-stack -p 6379:6379 redis/redis-stack-server:latest
"""
import json
import time
import numpy as np
import redis
from redis.commands.search.field import VectorField, TextField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query
import anthropic
from openai import OpenAI

# Clients
anthropic_client = anthropic.Anthropic()
openai_client = OpenAI()
r = redis.Redis(host='localhost', port=6379, decode_responses=False)

SIMILARITY_THRESHOLD = 0.93
VECTOR_DIM = 1536  # text-embedding-3-small dimension
INDEX_NAME = "semantic_cache_idx"
CACHE_PREFIX = "sem_cache:"
TTL_SECONDS = 7200  # 2 hours

def setup_redis_index():
    """Create a Redis vector search index (run once)."""
    try:
        r.ft(INDEX_NAME).info()
        print("Index already exists")
    except Exception:
        schema = (
            TextField("$.query", as_name="query"),
            TextField("$.response", as_name="response"),
            VectorField(
                "$.embedding",
                "HNSW",
                {
                    "TYPE": "FLOAT32",
                    "DIM": VECTOR_DIM,
                    "DISTANCE_METRIC": "COSINE",
                },
                as_name="embedding"
            )
        )
        r.ft(INDEX_NAME).create_index(
            schema,
            definition=IndexDefinition(prefix=[CACHE_PREFIX], index_type=IndexType.JSON)
        )
        print(f"Created index: {INDEX_NAME}")

def get_embedding(text: str) -> list[float]:
    """Get text embedding using OpenAI's embedding model."""
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def search_cache(query_embedding: list[float], top_k: int = 1) -> list[dict]:
    """Search Redis for semantically similar cached queries."""
    query_vector = np.array(query_embedding, dtype=np.float32).tobytes()

    query = (
        Query(f"*=>[KNN {top_k} @embedding $vec AS score]")
        .sort_by("score")
        .return_fields("query", "response", "score")
        .dialect(2)
    )

    try:
        results = r.ft(INDEX_NAME).search(
            query,
            query_params={"vec": query_vector}
        )
        return [
            {
                "query": doc.query,
                "response": doc.response,
                "similarity": 1 - float(doc.score)  # COSINE distance → similarity
            }
            for doc in results.docs
        ]
    except Exception:
        return []

def store_in_cache(query: str, embedding: list[float], response: str, key: str):
    """Store a query-response pair in the semantic cache."""
    cache_data = {
        "query": query,
        "response": response,
        "embedding": embedding,
        "timestamp": time.time()
    }
    r.json().set(f"{CACHE_PREFIX}{key}", "$", cache_data)
    r.expire(f"{CACHE_PREFIX}{key}", TTL_SECONDS)

def semantic_cached_call(
    query: str,
    model: str = "claude-3-haiku-20240307",
    max_tokens: int = 512,
) -> dict:
    """
    Make an LLM call with semantic caching.
    Returns cached response if a similar-enough query exists.
    """
    # Step 1: Embed the query
    embed_start = time.time()
    query_embedding = get_embedding(query)
    embed_time = (time.time() - embed_start) * 1000

    # Step 2: Search cache
    search_start = time.time()
    results = search_cache(query_embedding)
    search_time = (time.time() - search_start) * 1000

    # Step 3: Check if top result is similar enough
    if results and results[0]["similarity"] >= SIMILARITY_THRESHOLD:
        top = results[0]
        return {
            "text": top["response"],
            "cached": True,
            "similarity": round(top["similarity"], 4),
            "matched_query": top["query"],
            "embed_time_ms": round(embed_time, 1),
            "search_time_ms": round(search_time, 1),
            "total_time_ms": round(embed_time + search_time, 1),
        }

    # Step 4: Cache miss — call LLM
    llm_start = time.time()
    response = anthropic_client.messages.create(
        model=model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": query}]
    )
    llm_time = (time.time() - llm_start) * 1000
    response_text = response.content[0].text

    # Step 5: Store in cache
    import hashlib
    cache_key = hashlib.md5(query.encode()).hexdigest()
    store_in_cache(query, query_embedding, response_text, cache_key)

    return {
        "text": response_text,
        "cached": False,
        "similarity": None,
        "embed_time_ms": round(embed_time, 1),
        "llm_time_ms": round(llm_time, 1),
        "total_time_ms": round(embed_time + llm_time, 1),
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }

# Usage example
if __name__ == "__main__":
    setup_redis_index()

    # First query — cache miss
    q1 = "What is the capital city of France?"
    r1 = semantic_cached_call(q1)
    print(f"\nQ1: {q1}")
    print(f"  Cached: {r1['cached']}, Time: {r1['total_time_ms']}ms")
    print(f"  Answer: {r1['text'][:100]}")

    # Similar query — should hit cache
    q2 = "Which city is the capital of France?"
    r2 = semantic_cached_call(q2)
    print(f"\nQ2: {q2}")
    print(f"  Cached: {r2['cached']}, Similarity: {r2.get('similarity')}, Time: {r2['total_time_ms']}ms")
    print(f"  Matched: {r2.get('matched_query')}")

    # Different query — should miss cache
    q3 = "What is the population of Brazil?"
    r3 = semantic_cached_call(q3)
    print(f"\nQ3: {q3}")
    print(f"  Cached: {r3['cached']}, Time: {r3['total_time_ms']}ms")
```

---

## Pattern 3: Prompt Caching (Anthropic API)

Caches long shared system prompts at the provider level.

```python
"""
Prompt caching with Anthropic's API.
Works when multiple requests share the same long system prompt.
Requirements: pip install anthropic
"""
import anthropic
import time

client = anthropic.Anthropic()

# Simulate a long shared system prompt (e.g., product catalog, policies)
LONG_SYSTEM_PROMPT = """
You are a customer support agent for TechCorp. Here is our complete product catalog and policies:

PRODUCTS:
- TechWidget Pro ($299): Our flagship widget with 4K display...
[Imagine this is 10,000+ tokens of product documentation]
""" + "." * 5000  # Pad to simulate long prompt

def call_with_prompt_cache(user_message: str) -> dict:
    """Make an LLM call with prompt caching enabled."""
    start = time.time()

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=512,
        system=[{
            "type": "text",
            "text": LONG_SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"}  # Enable caching
        }],
        messages=[{
            "role": "user",
            "content": user_message
        }]
    )

    elapsed_ms = (time.time() - start) * 1000

    usage = response.usage
    return {
        "text": response.content[0].text,
        "input_tokens": usage.input_tokens,
        "output_tokens": usage.output_tokens,
        "cache_creation_tokens": getattr(usage, 'cache_creation_input_tokens', 0),
        "cache_read_tokens": getattr(usage, 'cache_read_input_tokens', 0),
        "latency_ms": round(elapsed_ms, 1)
    }

def calculate_cost(result: dict) -> float:
    """Calculate request cost including cache discounts."""
    # Anthropic pricing (check current pricing at anthropic.com)
    NORMAL_INPUT_PER_M = 3.00
    CACHE_CREATION_PER_M = 3.75   # 25% premium for cache creation
    CACHE_READ_PER_M = 0.30       # 90% discount for cache reads
    OUTPUT_PER_M = 15.00

    cost = (
        result["input_tokens"] * NORMAL_INPUT_PER_M / 1_000_000 +
        result["cache_creation_tokens"] * CACHE_CREATION_PER_M / 1_000_000 +
        result["cache_read_tokens"] * CACHE_READ_PER_M / 1_000_000 +
        result["output_tokens"] * OUTPUT_PER_M / 1_000_000
    )
    return round(cost, 6)

if __name__ == "__main__":
    questions = [
        "What is the price of TechWidget Pro?",
        "Do you offer a student discount?",
        "How long is your return policy?",
    ]

    print("Prompt caching demo:\n")
    for i, q in enumerate(questions, 1):
        result = call_with_prompt_cache(q)
        cost = calculate_cost(result)

        print(f"Request {i}: {q}")
        print(f"  Latency: {result['latency_ms']}ms")
        print(f"  Tokens: {result['input_tokens']} input + {result['output_tokens']} output")
        print(f"  Cache: {result['cache_creation_tokens']} created, {result['cache_read_tokens']} read")
        print(f"  Cost: ${cost}")
        print(f"  Answer: {result['text'][:80]}...")
        print()
        # Note: First request creates cache, subsequent requests read from it
        # Cache read tokens are dramatically cheaper than normal input tokens
```

---

## Cache Hit Rate Tracker

Monitor your caching performance over time.

```python
"""
Simple cache metrics tracker.
Plug this into any of the caching patterns above.
"""
from dataclasses import dataclass, field
from typing import Optional
import time

@dataclass
class CacheMetrics:
    hits: int = 0
    misses: int = 0
    total_cache_latency_ms: float = 0.0
    total_llm_latency_ms: float = 0.0
    total_cost_usd: float = 0.0
    total_cost_with_cache_usd: float = 0.0

    def record_hit(self, latency_ms: float):
        self.hits += 1
        self.total_cache_latency_ms += latency_ms

    def record_miss(self, latency_ms: float, cost_usd: float):
        self.misses += 1
        self.total_llm_latency_ms += latency_ms
        self.total_cost_with_cache_usd += cost_usd

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0

    @property
    def avg_cache_latency(self) -> float:
        return self.total_cache_latency_ms / self.hits if self.hits > 0 else 0

    @property
    def avg_llm_latency(self) -> float:
        return self.total_llm_latency_ms / self.misses if self.misses > 0 else 0

    def report(self):
        print(f"Cache Hit Rate: {self.hit_rate:.1%}")
        print(f"Total requests: {self.hits + self.misses} ({self.hits} hits, {self.misses} misses)")
        print(f"Avg cache hit latency: {self.avg_cache_latency:.1f}ms")
        print(f"Avg LLM latency: {self.avg_llm_latency:.1f}ms")
        print(f"Latency improvement: {self.avg_llm_latency / max(self.avg_cache_latency, 1):.0f}x for cache hits")

# Global metrics (in practice, use a proper metrics system like Prometheus)
metrics = CacheMetrics()
```

---

## 📂 Navigation
