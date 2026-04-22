# Model Reference — Cheatsheet

## Current Model IDs

```python
# Haiku — fastest, lowest cost, simple tasks
model = "claude-haiku-4-5-20251001"

# Sonnet — balanced, most production work
model = "claude-sonnet-4-6"

# Opus — highest quality, complex reasoning
model = "claude-opus-4-6"
```

---

## Context Window

All current models: **200,000 tokens**

| Content | Approx tokens |
|---|---|
| 1 page | ~500 |
| Short story | ~7,000 |
| Novel | ~110,000 |
| Code repo (medium) | ~50,000–150,000 |

---

## Pricing (Representative)

| Model | Input | Output | Cache Write | Cache Read |
|---|---|---|---|---|
| Haiku 4.5 | $0.80/MTok | $4.00/MTok | $1.00 | $0.08 |
| Sonnet 4.6 | $3.00/MTok | $15.00/MTok | $3.75 | $0.30 |
| Opus 4.6 | $15.00/MTok | $75.00/MTok | $18.75 | $1.50 |

Verify current rates: [anthropic.com/pricing](https://www.anthropic.com/pricing)

---

## Capabilities Matrix

| Feature | Haiku | Sonnet | Opus |
|---|---|---|---|
| Vision | Yes | Yes | Yes |
| Extended thinking | No | Yes | Yes |
| Tool use | Yes | Yes | Yes |
| Streaming | Yes | Yes | Yes |
| Batch API | Yes | Yes | Yes |
| Cache min tokens | 2,048 | 1,024 | 1,024 |

---

## Model Selection Rules

```python
def select_model(task_type: str) -> str:
    simple = {"classify", "extract", "translate", "format", "qa_simple"}
    complex_ = {"research", "expert_analysis", "multi_step_reasoning"}
    
    if task_type in simple:
        return "claude-haiku-4-5-20251001"
    elif task_type in complex_:
        return "claude-opus-4-6"
    return "claude-sonnet-4-6"  # default for most tasks
```

---

## Model ID Pattern

```
claude-{family}-{version}-{date}

claude-haiku-4-5-20251001   ← dated (pinned, production)
claude-sonnet-4-6            ← undated (latest, development)
```

---

## Relative Cost (1000 calls × 500 input + 200 output)

| Model | Cost |
|---|---|
| Haiku | ~$1.20 |
| Sonnet | ~$4.50 |
| Opus | ~$22.50 |

Use Haiku for eligible tasks: saves 73% vs Sonnet, 95% vs Opus.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept guide |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Comparison.md](./Comparison.md) | Full model comparison |

⬅️ **Prev:** [Error Handling](../12_Error_Handling/Cheatsheet.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Track 4 — Agent SDK](../../04_Claude_Agent_SDK/)
