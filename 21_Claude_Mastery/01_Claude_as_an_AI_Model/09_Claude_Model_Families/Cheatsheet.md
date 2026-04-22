# Claude Model Families — Cheatsheet

**One-liner:** Three tiers — Haiku (fastest/cheapest), Sonnet (production default), Opus (highest capability) — with 200k context windows across all; route tasks by complexity to optimize cost without sacrificing quality.

---

## Current model IDs (mid-2025)

| Model ID | Tier | Context |
|----------|------|---------|
| `claude-haiku-4-5` | Haiku | 200,000 tokens |
| `claude-sonnet-4-6` | Sonnet | 200,000 tokens |
| `claude-opus-4` | Opus | 200,000 tokens |

Always check anthropic.com/api for the most current IDs. Pin exact IDs in production.

---

## Tier comparison

| Dimension | Haiku | Sonnet | Opus |
|-----------|-------|--------|------|
| Speed | Fastest | Fast | Moderate |
| Intelligence | Good | Excellent | Best |
| Input cost | ~$0.25/M | ~$3/M | ~$15/M |
| Output cost | ~$1.25/M | ~$15/M | ~$75/M |
| Use for | Volume, simple | Most tasks | Hardest problems |

Approximate ratios (Haiku = 1x baseline):
- Haiku is ~12x cheaper than Sonnet, ~60x cheaper than Opus

---

## Task routing guide

| Task type | Use model | Why |
|-----------|-----------|-----|
| Classification, routing, tagging | Haiku | Simple, high-volume |
| Simple Q&A, FAQ | Haiku | Fast, cost-effective |
| Code generation, debugging | Sonnet | Quality matters, speed acceptable |
| Document analysis, summarization | Sonnet | Good default |
| Agents and tool use | Sonnet | Strong instruction following |
| Complex research synthesis | Opus | Depth of reasoning needed |
| Graduate-level math | Opus | Most capable at hard reasoning |
| Legal/financial complex analysis | Opus | Accuracy-critical |

---

## Routing pattern

```python
def route_to_model(task_type: str, complexity: str) -> str:
    if complexity == "simple" or task_type == "classification":
        return "claude-haiku-4-5"
    elif complexity == "hard" or task_type in ["research", "math"]:
        return "claude-opus-4"
    else:
        return "claude-sonnet-4-6"  # safe default
```

---

## Cost calculation

```python
PRICES = {
    "claude-haiku-4-5":  {"input": 0.25,  "output": 1.25},   # per million tokens
    "claude-sonnet-4-6": {"input": 3.00,  "output": 15.00},
    "claude-opus-4":     {"input": 15.00, "output": 75.00},
}

def estimate(model, input_tok, output_tok):
    r = PRICES[model]
    return (input_tok * r["input"] + output_tok * r["output"]) / 1_000_000
```

---

## Golden rules

1. Sonnet is the right default — it handles 90%+ of tasks excellently
2. Never use Opus as a default — reserve it for problems that Sonnet genuinely struggles with
3. Benchmark before choosing — test both tiers on your actual task, not hypothetical complexity
4. Pin model IDs in production — behavior can change across minor versions
5. Route by task type, not by user importance — VIP users still get Haiku for simple questions
6. Output tokens cost 5x more than input — keep responses concise for cost-sensitive endpoints

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Comparison.md](./Comparison.md) | Detailed model comparison |

⬅️ **Prev:** [08 Extended Thinking](../08_Extended_Thinking/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [10 Safety Layers](../10_Safety_Layers/Theory.md)
