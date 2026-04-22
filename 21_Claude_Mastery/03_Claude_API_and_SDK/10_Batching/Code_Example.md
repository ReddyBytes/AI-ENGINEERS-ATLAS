# Batching — Code Examples

## Example 1: Submit, poll, retrieve — complete pipeline

```python
import anthropic
import time
import json

client = anthropic.Anthropic()

# Data to process
product_reviews = [
    "Amazing product! Works perfectly.",
    "Terrible quality, broke after one day.",
    "Decent product, nothing special.",
    "Best purchase I've made this year!",
    "Arrived damaged, very disappointed.",
]

# 1. Submit batch
batch = client.beta.messages.batches.create(
    requests=[
        {
            "custom_id": f"review-{i}",
            "params": {
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 16,
                "temperature": 0.0,
                "messages": [{
                    "role": "user",
                    "content": f"Classify as POSITIVE, NEGATIVE, or NEUTRAL. Return label only:\n{review}"
                }]
            }
        }
        for i, review in enumerate(product_reviews)
    ]
)

print(f"Submitted batch: {batch.id}")
print(f"Status: {batch.processing_status}")

# 2. Poll for completion
print("Waiting for completion...")
while True:
    batch = client.beta.messages.batches.retrieve(batch.id)
    counts = batch.request_counts
    print(f"  Processing: {counts.processing} | Done: {counts.succeeded + counts.errored}")
    
    if batch.processing_status == "ended":
        break
    time.sleep(10)  # short poll for demo; use 30-60s in production

# 3. Retrieve results
results = {}
for result in client.beta.messages.batches.results(batch.id):
    if result.result.type == "succeeded":
        results[result.custom_id] = result.result.message.content[0].text.strip()
    else:
        results[result.custom_id] = f"ERROR: {result.result}"

# 4. Match results to original data
print("\nResults:")
for i, review in enumerate(product_reviews):
    label = results.get(f"review-{i}", "MISSING")
    print(f"  [{label}] {review[:50]}")
```

---

## Example 2: Large-scale annotation job with error handling

```python
import anthropic
import time
import json
from pathlib import Path

client = anthropic.Anthropic()

def batch_classify(items: list[dict], output_path: str) -> dict:
    """
    items: list of {"id": str, "text": str}
    Returns: dict of {id: classification}
    """
    # Submit
    batch = client.beta.messages.batches.create(
        requests=[
            {
                "custom_id": item["id"],
                "params": {
                    "model": "claude-haiku-4-5-20251001",
                    "max_tokens": 32,
                    "temperature": 0.0,
                    "system": "Classify text. Return only: POSITIVE, NEGATIVE, or NEUTRAL.",
                    "messages": [{"role": "user", "content": item["text"]}]
                }
            }
            for item in items
        ]
    )
    
    print(f"Batch {batch.id} submitted ({len(items)} items)")
    
    # Poll with timeout
    max_wait = 3600  # 1 hour max
    start = time.time()
    
    while time.time() - start < max_wait:
        batch = client.beta.messages.batches.retrieve(batch.id)
        if batch.processing_status == "ended":
            break
        time.sleep(30)
    else:
        raise TimeoutError(f"Batch {batch.id} did not complete in {max_wait}s")
    
    # Collect results
    succeeded = {}
    errors = []
    
    for result in client.beta.messages.batches.results(batch.id):
        cid = result.custom_id
        
        if result.result.type == "succeeded":
            succeeded[cid] = result.result.message.content[0].text.strip()
        elif result.result.type == "errored":
            errors.append({"id": cid, "error": str(result.result.error)})
        elif result.result.type == "expired":
            errors.append({"id": cid, "error": "expired"})
    
    # Save results
    output = {"succeeded": succeeded, "errors": errors}
    Path(output_path).write_text(json.dumps(output, indent=2))
    
    print(f"Succeeded: {len(succeeded)}, Errors: {len(errors)}")
    return succeeded

# Usage
items = [{"id": f"doc-{i}", "text": f"Sample text {i}"} for i in range(50)]
results = batch_classify(items, "batch_results.json")
```

---

## Example 3: Cancel a batch in progress

```python
import anthropic

client = anthropic.Anthropic()

# Submit a batch
batch = client.beta.messages.batches.create(
    requests=[
        {
            "custom_id": f"req-{i}",
            "params": {
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 64,
                "messages": [{"role": "user", "content": f"Summarize: item {i}"}]
            }
        }
        for i in range(100)
    ]
)

print(f"Submitted: {batch.id}")

# Cancel if you change your mind
cancel_result = client.beta.messages.batches.cancel(batch.id)
print(f"Cancel status: {cancel_result.processing_status}")  # "canceling" or "canceled"
```

---

## Example 4: List all batches and their status

```python
import anthropic

client = anthropic.Anthropic()

print("Recent batches:")
for batch in client.beta.messages.batches.list(limit=10):
    counts = batch.request_counts
    total = counts.processing + counts.succeeded + counts.errored + counts.canceled + counts.expired
    print(f"  {batch.id} | {batch.processing_status} | "
          f"✓{counts.succeeded} ✗{counts.errored} ⏳{counts.processing} / {total}")
```

---

## Example 5: Production pipeline with database storage

```python
import anthropic
import time
import sqlite3
import json

client = anthropic.Anthropic()

# Setup SQLite for tracking (use PostgreSQL in production)
conn = sqlite3.connect("batch_tracker.db")
conn.execute("""
    CREATE TABLE IF NOT EXISTS batch_jobs (
        batch_id TEXT PRIMARY KEY,
        status TEXT,
        submitted_at INTEGER,
        completed_at INTEGER,
        total_requests INTEGER,
        succeeded INTEGER DEFAULT 0,
        errored INTEGER DEFAULT 0
    )
""")
conn.execute("""
    CREATE TABLE IF NOT EXISTS results (
        custom_id TEXT PRIMARY KEY,
        batch_id TEXT,
        status TEXT,
        response TEXT,
        error TEXT
    )
""")
conn.commit()

def submit_and_track(texts: list[str]) -> str:
    """Submit batch and record in DB."""
    requests = [
        {"custom_id": f"text-{i}", "params": {"model": "claude-haiku-4-5-20251001", "max_tokens": 32,
         "messages": [{"role":"user","content":f"Classify sentiment: {t}"}]}}
        for i, t in enumerate(texts)
    ]
    batch = client.beta.messages.batches.create(requests=requests)
    
    conn.execute("INSERT INTO batch_jobs VALUES (?,?,?,?,?,?,?)",
                 (batch.id, "in_progress", int(time.time()), None, len(texts), 0, 0))
    conn.commit()
    return batch.id

def collect_results(batch_id: str):
    """Collect and store results when batch completes."""
    batch = client.beta.messages.batches.retrieve(batch_id)
    if batch.processing_status != "ended":
        return
    
    for result in client.beta.messages.batches.results(batch_id):
        if result.result.type == "succeeded":
            conn.execute("INSERT OR REPLACE INTO results VALUES (?,?,?,?,?)",
                        (result.custom_id, batch_id, "succeeded",
                         result.result.message.content[0].text, None))
        else:
            conn.execute("INSERT OR REPLACE INTO results VALUES (?,?,?,?,?)",
                        (result.custom_id, batch_id, result.result.type, None, str(result.result)))
    
    counts = batch.request_counts
    conn.execute("UPDATE batch_jobs SET status='completed', completed_at=?, succeeded=?, errored=? WHERE batch_id=?",
                 (int(time.time()), counts.succeeded, counts.errored, batch_id))
    conn.commit()
    print(f"Collected {counts.succeeded} results for {batch_id}")

# Usage
batch_id = submit_and_track(["Great product", "Terrible service", "Average quality"])
time.sleep(60)  # wait in real usage
collect_results(batch_id)
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

⬅️ **Prev:** [Prompt Caching](../09_Prompt_Caching/Code_Example.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Cost Optimization](../11_Cost_Optimization/Code_Example.md)
