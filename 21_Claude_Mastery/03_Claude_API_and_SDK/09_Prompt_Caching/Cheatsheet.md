# Prompt Caching — Cheatsheet

## Enable Caching — System Prompt

```python
client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    system=[
        {
            "type": "text",
            "text": YOUR_LARGE_SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"}  # ← marks for caching
        }
    ],
    messages=[{"role": "user", "content": user_input}]
)
```

---

## Enable Caching — Tools

```python
tools = [
    tool1,
    tool2,
    {
        **tool3,
        "cache_control": {"type": "ephemeral"}  # cache up to tool3
    }
]
```

---

## Enable Caching — Document in Messages

```python
messages = [
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "Here is the document:"},
            {
                "type": "text",
                "text": LONG_DOCUMENT,
                "cache_control": {"type": "ephemeral"}  # cache doc prefix
            }
        ]
    },
    {"role": "assistant", "content": "I've read it."},
    {"role": "user", "content": [{"type": "text", "text": question}]}
]
```

---

## Check Cache Activity in Response

```python
response = client.messages.create(...)

print(response.usage.input_tokens)                  # uncached tokens
print(response.usage.cache_creation_input_tokens)   # tokens written to cache (first call)
print(response.usage.cache_read_input_tokens)       # tokens read from cache (hits)
```

---

## Cache Economics

| Event | Cost multiplier |
|---|---|
| Cache write (first call) | 1.25× standard input |
| Cache read (subsequent calls) | 0.10× standard input |
| Uncached input | 1.0× |
| Output tokens | Always full price |

Break-even: 2+ cache reads cover the write premium.

---

## TTL and Minimums

| Property | Value |
|---|---|
| Cache TTL | 5 minutes (resets on each hit) |
| Min cacheable tokens (Sonnet/Opus) | 1,024 tokens |
| Min cacheable tokens (Haiku) | 2,048 tokens |
| Max cache_control markers per request | 4 |

---

## Common Pitfalls

| Pitfall | Fix |
|---|---|
| `system="..."` string — can't cache | Use `system=[{"type":"text","text":"...","cache_control":{...}}]` |
| Prefix below minimum tokens | Need 1024+ tokens (Sonnet) for caching to activate |
| Dynamic content in cached prefix | Cache key changes on every call — no hits |
| Low traffic app | Cache expires before next call — test your call rate |

---

## When Caching Saves Money

```
Need ALL of:
✓ Prefix > 1024 tokens (Sonnet) or > 2048 (Haiku)
✓ Same prefix across multiple calls
✓ > 1 call every 5 minutes
```

---

## Savings Calculation

```python
# Without caching — 10,000 calls × 2,000 token system prompt
uncached_cost = 10_000 * 2_000 * input_price_per_token

# With caching — 1 write + 9,999 reads
write_cost = 1 * 2_000 * input_price_per_token * 1.25
read_cost = 9_999 * 2_000 * input_price_per_token * 0.10
cached_cost = write_cost + read_cost
# ~9x cheaper
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept guide |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Working code |

⬅️ **Prev:** [Prompt Engineering](../08_Prompt_Engineering/Cheatsheet.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Batching](../10_Batching/Cheatsheet.md)
