# Cheatsheet — Cost Optimization

**Cost optimization** is the practice of minimizing the monetary cost per AI inference request without degrading quality below acceptable thresholds.

---

## Key Terms

| Term | Definition |
|---|---|
| **Input tokens** | Tokens in the prompt (system prompt + user message + context) |
| **Output tokens** | Tokens generated in the response. Usually 3-5x pricier per token than input |
| **Prompt caching** | Provider-side caching of KV state for repeated prompt prefixes (90% discount) |
| **Semantic caching** | App-side caching using embeddings to find similar past queries |
| **Model routing** | Sending simple requests to cheap models, complex to expensive ones |
| **Spot instance** | Cloud GPU with 60-90% discount; can be interrupted with ~2 min notice |
| **Break-even point** | Volume where self-hosting cost per request equals API cost per request |
| **Token budget** | A hard limit on total tokens per request to cap cost |
| **Context compression** | Summarizing or truncating history to reduce input tokens |

---

## API Cost Model

```
Cost per request = (input_tokens × input_$/M) / 1,000,000
                 + (output_tokens × output_$/M) / 1,000,000

Example: GPT-4o
  Input: 1,500 tokens × $5/M = $0.0075
  Output: 400 tokens × $15/M = $0.006
  Total: $0.0135 per request
  At 100,000 req/day: $1,350/day = ~$40,000/month

Example: GPT-4o-mini (same task)
  Input: 1,500 tokens × $0.15/M = $0.000225
  Output: 400 tokens × $0.60/M = $0.00024
  Total: $0.000465 per request
  At 100,000 req/day: $46.50/day = ~$1,400/month
  Savings: 97%
```

---

## Self-Hosting Cost Model

```
Cost per request = GPU_instance_$/hour / requests_per_hour

Example: A100 80GB ($5/hour) running a 70B model
  Throughput: ~200 requests/hour (at avg 500 output tokens)
  Cost per request: $5 / 200 = $0.025

Example: T4 ($0.35/hour) running a 7B model
  Throughput: ~1,000 requests/hour
  Cost per request: $0.35 / 1,000 = $0.00035
```

---

## Break-Even Analysis

```
Break-even volume = (fixed_cost_$/month) / (API_cost - selfhost_cost per request)

Example:
  API cost:       $0.015 / request
  Self-host cost: $0.001 / request (A100 amortized)
  Self-host overhead (ops): $3,000/month

  Break-even = $3,000 / ($0.015 - $0.001) = 214,286 requests/month
             = ~7,000 requests/day

If you have > 7,000 requests/day → self-hosting wins
If you have < 7,000 requests/day → API wins
```

---

## Cost Reduction Levers — Priority Order

| Priority | Technique | Typical Savings | Effort |
|---|---|---|---|
| 1 | **Smaller/cheaper model** (if quality holds) | 50-97% | Low |
| 2 | **Caching** (exact match) | 20-80% (by hit rate) | Low |
| 3 | **Prompt caching** (provider feature) | 40-90% on cached tokens | Very Low |
| 4 | **Context compression** (shorter prompts) | 30-70% on input cost | Medium |
| 5 | **Output length limits** (max_tokens) | 20-50% on output cost | Very Low |
| 6 | **Semantic caching** | 20-60% | Medium |
| 7 | **Request batching** (self-hosted) | 30-60% on GPU cost | Medium |
| 8 | **Spot instances** (self-hosted, batch jobs) | 60-90% on GPU cost | Medium |
| 9 | **Quantization** (self-hosted) | 50-75% on GPU memory → more requests per GPU | Low |
| 10 | **Self-hosting** (at scale) | 70-90% vs API | High |

---

## Model Cost Comparison (Approximate)

| Model | Input $/M | Output $/M | Relative Cost | Best For |
|---|---|---|---|---|
| GPT-4o | $5 | $15 | 100x | Complex reasoning, best quality |
| Claude 3.5 Sonnet | $3 | $15 | ~80x | Long context, coding |
| GPT-4o-mini | $0.15 | $0.60 | 3x | Structured extraction, routing |
| Claude 3 Haiku | $0.25 | $1.25 | 4x | Fast, cheap, good enough |
| Llama 3 70B (self-hosted) | ~$0.50 | ~$0.70 | ~8x | High volume, custom use |
| Llama 3 8B (self-hosted) | ~$0.05 | ~$0.07 | 1x | Very high volume, simple tasks |

*Prices change frequently — check current provider pricing pages.*

---

## Token Reduction Strategies

```python
# 1. Summarize chat history instead of sending it all
def get_context(messages, max_tokens=2000):
    if token_count(messages) < max_tokens:
        return messages
    # Summarize older messages
    summary = summarize(messages[:-5])  # keep last 5 fresh
    return [{"role": "system", "content": f"Summary: {summary}"}] + messages[-5:]

# 2. Extract only relevant chunks (RAG instead of full document)
relevant_chunks = vector_search(query, top_k=3)  # 800 tokens vs 50,000

# 3. Set explicit output length limits
response = client.messages.create(
    model="claude-3-haiku-20240307",
    max_tokens=200,  # Hard cap
    messages=messages
)

# 4. Instruct the model to be concise
system_prompt = "Answer in 2-3 sentences. Be direct and concise."
```

---

## Golden Rules

- **Track cost per request** before optimizing anything — you can't cut what you can't measure
- **Try the cheaper model first** — quality is often indistinguishable for common tasks
- **Cache aggressively** — cache hits have near-zero marginal cost
- **Output tokens cost more** — explicitly ask for concise answers
- **Enable prompt caching** if your system prompt is long and shared — it's a free discount
- **Use spot instances** for any workload that can checkpoint and retry
- **Re-evaluate self-hosting at 10x your current volume** — the math changes dramatically

---

## 📂 Navigation
