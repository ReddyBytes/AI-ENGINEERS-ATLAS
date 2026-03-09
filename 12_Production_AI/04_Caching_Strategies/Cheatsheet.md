# Cheatsheet — Caching Strategies

**Caching** stores previously computed AI results so future identical or similar requests can be served instantly without calling the model, reducing both latency and cost.

---

## Key Terms

| Term | Definition |
|---|---|
| **Cache hit** | Request is answered from cached data — no inference needed |
| **Cache miss** | No cached result found — model inference is triggered |
| **Cache hit rate** | Fraction of requests served from cache (target: > 30%) |
| **TTL (Time To Live)** | How long a cached entry is valid before expiring |
| **Exact-match cache** | Key = hash of input; only works if input is byte-identical |
| **Semantic cache** | Key = embedding vector; works for paraphrases via similarity search |
| **KV cache** | In-model cache of attention key-value pairs (internal to the transformer) |
| **Prompt caching** | Provider-side KV cache for repeated prompt prefixes (Anthropic, OpenAI) |
| **Cache invalidation** | Process of removing stale cached entries |
| **Cosine similarity** | How "similar" two embeddings are (0 = unrelated, 1 = identical) |

---

## Cache Type Comparison

| Cache Type | When It Helps | Similarity Handling | Cost | Complexity |
|---|---|---|---|---|
| **Exact match (Redis)** | Repeated identical inputs | Exact only | Very Low | Low |
| **Semantic (embedding)** | Paraphrases / near-duplicates | Yes (cosine > threshold) | Low | Medium |
| **Prompt caching (Anthropic)** | Repeated long system prompts | Exact prefix only | 10% of input price | Very Low |
| **In-process (memory)** | Single-server, high repeat rate | Exact only | Free | Very Low |
| **CDN caching** | Public, non-personalized responses | Exact only | Low | Low |

---

## Similarity Threshold Guide

| Threshold | Behavior | Risk |
|---|---|---|
| 0.70 | Very permissive — many hits but risky | High — unrelated questions get same answer |
| 0.85 | Loose — works for very similar phrasing | Medium — occasional wrong cached answer |
| **0.92-0.95** | **Recommended default** | Low — catches paraphrases, rejects different questions |
| 0.98 | Very strict — only near-identical | Very Low — low hit rate, very safe |
| 1.00 | Exact match only (embedding level) | None | Low hit rate |

---

## Cache Invalidation Strategies

| Strategy | How | Best For |
|---|---|---|
| **TTL (time-based)** | Entries expire after N seconds | Content that changes on a schedule |
| **Event-based** | Invalidate when source data changes | Product catalog, pricing, policies |
| **Version-based** | Cache key includes a version number | Model updates, prompt version changes |
| **LRU eviction** | Remove least recently used when cache is full | General purpose |
| **Manual purge** | Admin/code explicitly deletes entries | Emergency fixes, data corrections |

---

## Exact-Match Cache Pattern

```python
import hashlib
import json
import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def cache_key(messages: list, model: str) -> str:
    """Create a deterministic cache key from messages."""
    content = json.dumps({"model": model, "messages": messages}, sort_keys=True)
    return f"llm:{hashlib.sha256(content.encode()).hexdigest()}"

def cached_llm_call(messages: list, model: str, ttl: int = 3600) -> str:
    key = cache_key(messages, model)
    cached = r.get(key)
    if cached:
        return cached  # Cache hit

    response = call_llm(messages, model)  # Cache miss
    r.setex(key, ttl, response)
    return response
```

---

## Semantic Cache Pattern (Quick Reference)

```python
# Embed query → search for similar cached entry → if similar enough, return cached
# else call LLM → embed response → store in vector cache

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

SIMILARITY_THRESHOLD = 0.93
cache_store = {}  # In practice: Redis with vector search, or Pinecone/Chroma

def semantic_cached_call(query: str) -> str:
    query_embedding = embed(query)

    # Search cache
    for cached_query, (cached_emb, cached_response) in cache_store.items():
        sim = cosine_similarity([query_embedding], [cached_emb])[0][0]
        if sim >= SIMILARITY_THRESHOLD:
            return cached_response  # Cache hit

    # Cache miss
    response = call_llm(query)
    cache_store[query] = (query_embedding, response)
    return response
```

---

## Prompt Caching (Anthropic API)

```python
# Mark system prompt for caching — Anthropic caches the K/V state
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    system=[{
        "type": "text",
        "text": "You are a helpful assistant. [Your 10,000-token system prompt here...]",
        "cache_control": {"type": "ephemeral"}  # ← This enables caching
    }],
    messages=[{"role": "user", "content": user_query}]
)

# Check if cache was used
cache_creation = response.usage.cache_creation_input_tokens  # First call
cache_read = response.usage.cache_read_input_tokens           # Subsequent calls
```

Cache read tokens cost ~10% of normal input price. Cache creation costs 25% extra (one-time).

---

## When to Use / When NOT to Use

**Use caching when:**
- Many users ask similar or identical questions (FAQ-style)
- You have a long shared system prompt (> 500 tokens)
- Your responses are not personalized / same for all users
- Responses are not time-sensitive (can tolerate being hours old)

**Do NOT use caching when:**
- Responses are personalized to the individual user's data
- Content changes frequently and stale responses are harmful
- Every request is genuinely unique (creative writing, unique queries)
- Responses must reflect real-time data (stock prices, live inventory)

---

## Golden Rules

- **Always set a TTL** — never cache indefinitely; information goes stale
- **Never cache personally identifiable or user-specific content** in a shared cache
- **Measure hit rate from day one** — target > 30% for it to be worth the complexity
- **Tune similarity threshold on real data** — 0.92-0.95 is a starting point, not gospel
- **Cache at the right layer** — exact match for FAQs, semantic for conversational, prompt caching for shared context
- **Log cache hits and misses separately** — track latency and quality per cache-hit vs miss to detect threshold issues
- **Include model version in cache key** — invalidate cache when you change the model

---

## 📂 Navigation
