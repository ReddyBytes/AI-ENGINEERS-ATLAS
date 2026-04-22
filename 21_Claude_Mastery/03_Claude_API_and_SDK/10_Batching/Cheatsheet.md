# Batching — Cheatsheet

## Create a Batch

```python
import anthropic
client = anthropic.Anthropic()

batch = client.beta.messages.batches.create(
    requests=[
        {
            "custom_id": "req-001",           # your unique ID per request
            "params": {
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 256,
                "messages": [{"role": "user", "content": "Hello!"}]
            }
        },
        # ... up to 10,000 requests
    ]
)
print(batch.id)              # "msgbatch_01..."
print(batch.processing_status)  # "in_progress"
```

---

## Poll for Completion

```python
import time

while True:
    batch = client.beta.messages.batches.retrieve(batch_id)
    if batch.processing_status == "ended":
        break
    time.sleep(30)  # poll every 30 seconds
```

---

## Retrieve Results (JSONL stream)

```python
results = {}
for result in client.beta.messages.batches.results(batch_id):
    if result.result.type == "succeeded":
        results[result.custom_id] = result.result.message.content[0].text
    elif result.result.type == "errored":
        results[result.custom_id] = f"ERROR: {result.result.error}"
```

---

## Batch Status Values

| Status | Meaning |
|---|---|
| `in_progress` | Processing |
| `ended` | All done — retrieve results |
| `errored` | Batch-level failure |
| `canceling` | Cancellation in progress |
| `canceled` | Cancelled |

---

## Result Types

| Type | Meaning | Access |
|---|---|---|
| `succeeded` | OK | `result.result.message.content[0].text` |
| `errored` | Failed | `result.result.error` |
| `expired` | Timed out | Resubmit |

---

## Key Facts

| Property | Value |
|---|---|
| Cost reduction | 50% vs standard API |
| Max requests per batch | 10,000 |
| Result expiry | 24 hours |
| Processing time | Minutes to hours |
| Rate limits | Separate from real-time limits |

---

## When to Use

| Use batching | Use real-time |
|---|---|
| Data annotation | User-facing chat |
| Nightly processing jobs | Agent tool loops |
| Evaluation runs | Streaming responses |
| Content classification at scale | Any live user interaction |

---

## Batch Request Params

Same as `messages.create()`:
```python
"params": {
    "model": "...",
    "max_tokens": int,
    "messages": [...],
    "system": "...",         # optional
    "temperature": float,    # optional
    "tools": [...],          # optional
}
```

---

## Golden Rules

1. Always use meaningful `custom_id` values (database ID, filename)
2. Save results to your own storage before 24h expiry
3. Check `result.result.type` — don't assume all results succeeded
4. Poll every 30-60 seconds — not every second
5. Never use batching when a user is waiting for the response

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept guide |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Working code |

⬅️ **Prev:** [Prompt Caching](../09_Prompt_Caching/Cheatsheet.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Cost Optimization](../11_Cost_Optimization/Cheatsheet.md)
