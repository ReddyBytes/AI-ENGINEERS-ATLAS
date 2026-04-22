# Cost Optimization — Cheatsheet

## The Five Levers

| Lever | Saving | When applicable |
|---|---|---|
| Model routing | 5-10× | When Haiku can do the task |
| Prompt caching | 90% on cached tokens | System prompt >1K tokens, repeated calls |
| Batching | 50% | Non-real-time workloads |
| Output length control | 30-60% on output | When brevity is enough |
| Token counting | Prevent waste | Before bulk jobs |

---

## Token Counting (Before Sending)

```python
count = client.messages.count_tokens(
    model="claude-sonnet-4-6",
    system="...",
    messages=[{"role": "user", "content": "..."}]
)
print(count.input_tokens)
```

---

## Model Routing Skeleton

```python
def select_model(task: str) -> str:
    simple = {"classify", "extract", "format", "translate", "summarize_short"}
    complex_ = {"research", "multi_step", "expert_analysis"}
    
    if task in simple:
        return "claude-haiku-4-5-20251001"
    elif task in complex_:
        return "claude-opus-4-6"
    return "claude-sonnet-4-6"  # default
```

---

## Output Length Control

```python
# Set max_tokens to the minimum viable value
client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=8,   # classification → one word
    messages=[{"role": "user", "content": "Classify as POSITIVE or NEGATIVE: 'Great!'"}]
)

# Use prompt instructions
"Respond in one sentence."
"Answer with a single word: YES or NO."
"List exactly 3 bullet points. Max 10 words each."

# Use stop sequences for early termination
stop_sequences=[".", "\n"]
```

---

## Token Tracker

```python
class TokenTracker:
    def __init__(self):
        self.calls = 0
        self.input = self.output = self.cache_read = self.cache_write = 0
    
    def record(self, usage):
        self.calls += 1
        self.input += usage.input_tokens
        self.output += usage.output_tokens
        self.cache_read += usage.cache_read_input_tokens
        self.cache_write += usage.cache_creation_input_tokens
    
    def summary(self):
        return {
            "calls": self.calls,
            "avg_input": self.input / max(self.calls, 1),
            "avg_output": self.output / max(self.calls, 1),
            "cache_hit_ratio": self.cache_read / max(self.cache_read + self.cache_write, 1)
        }
```

---

## Cost Math (Sonnet pricing example)

```
Input:  $3.00 / 1M tokens
Output: $15.00 / 1M tokens

1000 calls × 500 input + 200 output:
= (500,000 × $0.000003) + (200,000 × $0.000015)
= $1.50 + $3.00
= $4.50 / day

With 2000-token system prompt + caching:
= $4.50 - (2M cached input tokens × $0.000003 × 0.9 savings)
≈ much less
```

---

## Pricing Summary (Representative)

| Model | Input | Output |
|---|---|---|
| Haiku 4.5 | $0.80/MTok | $4.00/MTok |
| Sonnet 4.6 | $3.00/MTok | $15.00/MTok |
| Opus 4.6 | $15.00/MTok | $75.00/MTok |

Check [anthropic.com/pricing](https://www.anthropic.com/pricing) for current rates.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept guide |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Comparison.md](./Comparison.md) | Strategy comparison |

⬅️ **Prev:** [Batching](../10_Batching/Cheatsheet.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Error Handling](../12_Error_Handling/Cheatsheet.md)
