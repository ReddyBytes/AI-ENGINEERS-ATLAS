# Model Reference — Full Comparison

## Model Identity Table

| Model | ID | Family | Released |
|---|---|---|---|
| Claude Haiku 4.5 | `claude-haiku-4-5-20251001` | Haiku | Oct 2025 |
| Claude Sonnet 4.6 | `claude-sonnet-4-6` | Sonnet | Feb 2025+ |
| Claude Opus 4.6 | `claude-opus-4-6` | Opus | Feb 2025+ |

---

## Performance vs Cost Matrix

```
              Intelligence ↑
                    |
         Opus       ●
                    |
         Sonnet  ●  |
                    |
         Haiku ●    |
                    |
                    +———————————→ Speed
              slow   fast
```

```
              Cost per call ↑
                    |
         Opus       ●
                    |
         Sonnet  ●  |
                    |
         Haiku ●    |
                    +———————————→ Task Simplicity
              complex  simple
```

---

## Context Window Comparison

| Model | Context Window | Max Output |
|---|---|---|
| Haiku 4.5 | 200,000 tokens | 8,192 tokens |
| Sonnet 4.6 | 200,000 tokens | 8,192 tokens |
| Opus 4.6 | 200,000 tokens | 32,000 tokens |

---

## Pricing Comparison (Representative — verify at anthropic.com/pricing)

| Model | Input $/MTok | Output $/MTok | Cache Write | Cache Read |
|---|---|---|---|---|
| Haiku 4.5 | $0.80 | $4.00 | $1.00 | $0.08 |
| Sonnet 4.6 | $3.00 | $15.00 | $3.75 | $0.30 |
| Opus 4.6 | $15.00 | $75.00 | $18.75 | $1.50 |
| **Sonnet/Haiku ratio** | 3.75× | 3.75× | 3.75× | 3.75× |
| **Opus/Sonnet ratio** | 5× | 5× | 5× | 5× |

---

## Capability Comparison

| Capability | Haiku 4.5 | Sonnet 4.6 | Opus 4.6 |
|---|---|---|---|
| Vision | Yes | Yes | Yes |
| Extended Thinking | No | Yes | Yes |
| Tool use / Function calling | Yes | Yes | Yes |
| Streaming | Yes | Yes | Yes |
| Message Batches API | Yes | Yes | Yes |
| Prompt caching | Yes (2K min) | Yes (1K min) | Yes (1K min) |
| Context window | 200K | 200K | 200K |
| Max output tokens | 8,192 | 8,192 | 32,000 |

---

## Task Routing Guide

| Task | Best Model | Why |
|---|---|---|
| Sentiment classification | Haiku | Simple labels, no reasoning needed |
| Named entity extraction | Haiku | Pattern matching |
| Language translation | Haiku | Well-learned, no complex reasoning |
| Simple Q&A (factual) | Haiku | Short, direct answers |
| High-volume data labeling | Haiku | Cheapest at scale |
| General chat | Sonnet | Quality UX, balanced cost |
| Code generation | Sonnet | Needs reasoning + context |
| Document analysis | Sonnet | Long context + nuanced analysis |
| Debugging complex bugs | Sonnet or Opus | Depends on depth |
| Research synthesis | Opus | Multi-document, deep reasoning |
| Expert-level writing | Opus | Nuance and quality required |
| Novel problem solving | Opus | No training-set shortcut |
| Math proofs, algorithms | Opus | Logical depth, Extended Thinking |

---

## Cost Comparison — 1,000 Calls

Assuming 500 input tokens + 200 output tokens per call:

| Model | Input cost | Output cost | Total |
|---|---|---|---|
| Haiku 4.5 | $0.40 | $0.80 | **$1.20** |
| Sonnet 4.6 | $1.50 | $3.00 | **$4.50** |
| Opus 4.6 | $7.50 | $15.00 | **$22.50** |

Routing 60% of calls to Haiku, 38% to Sonnet, 2% to Opus:
- Total ≈ (0.60 × $1.20) + (0.38 × $4.50) + (0.02 × $22.50)
- = $0.72 + $1.71 + $0.45 = **$2.88** vs $4.50 all-Sonnet = **36% savings**

---

## Model ID Versioning — When to Use Which

| Scenario | ID format | Example |
|---|---|---|
| Development | Latest (undated) | `claude-sonnet-4-6` |
| Staging/testing | Latest or pinned | `claude-sonnet-4-6` |
| Production | Pinned (dated) | `claude-sonnet-4-6-20250219` |
| Evaluation runs | Pinned | `claude-sonnet-4-6-20250219` |
| Config override via env | Variable | `os.environ.get("CLAUDE_MODEL", ...)` |

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept guide |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Comparison.md** | ← you are here |

⬅️ **Prev:** [Error Handling](../12_Error_Handling/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Track 4 — Agent SDK](../../04_Claude_Agent_SDK/)
