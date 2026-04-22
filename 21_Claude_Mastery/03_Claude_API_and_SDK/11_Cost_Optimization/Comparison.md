# Cost Optimization — Strategy Comparison

## Strategy Comparison Matrix

| Strategy | Cost Reduction | When to Apply | Tradeoffs |
|---|---|---|---|
| Model routing (Haiku) | 5-10× on routed tasks | Simple tasks: classify, extract, translate | Must benchmark quality |
| Prompt caching | 90% on cached tokens | >1K token system prompt, repeated calls | 5min TTL, write overhead |
| Message Batches | 50% on all tokens | Non-real-time workloads | Latency: minutes to hours |
| Output length control | 30-60% on output tokens | All tasks | Requires prompt tuning |
| Token counting | Preventive | Before bulk jobs | Adds API call overhead |

---

## Which Strategies Can Be Combined?

All five strategies are orthogonal and additive:

```
Base cost: 100%

Apply model routing (use Haiku instead of Sonnet for eligible tasks):
→ ~85% of calls now cost 80% less on eligible tasks
→ Effective reduction: 40-60%

Apply prompt caching (2000-token system prompt):
→ Reduces system prompt cost by 90% after warm
→ Additional reduction on input tokens: ~20-30%

Apply batching (for offline workloads):
→ Additional 50% reduction on batch jobs

Apply output length control:
→ Additional 30-50% on output tokens

Combined effective savings vs naive: 70-90%+
```

---

## Choosing the Right Strategy First

| Starting point | First strategy to try |
|---|---|
| Output tokens dominate your bill | Output length control |
| Input tokens dominate | Prompt caching (if prefix is static) |
| Many simple tasks using Sonnet | Model routing to Haiku |
| Large nightly or batch jobs | Batches API |
| Unknown — need to investigate | Token counting + monitoring first |

---

## Strategy Deep Dive: Model Routing ROI

Assuming 10,000 calls/day, mixed tasks:

| Scenario | Daily tokens | Cost (Sonnet) | Cost (Haiku) | Savings |
|---|---|---|---|---|
| 5K simple calls × 500 tokens | 2.5M in, 0.5M out | $7.50 + $7.50 | $2.00 + $2.00 | $11/day |
| 5K complex calls × 1K tokens | 5M in, 1M out | $15 + $15 | Stay on Sonnet | $0 |
| **Total** | — | **$45/day** | **$34/day** | **$11/day = $4K/year** |

---

## Strategy Deep Dive: Prompt Caching ROI

System prompt: 3,000 tokens, Sonnet pricing, 1,000 calls/day

| Metric | Without cache | With cache |
|---|---|---|
| Daily input tokens (system) | 3M | 3K (write) + 997K (read at 0.1×) |
| Effective cost | $9.00/day | $0.009 + $0.30 = $0.31/day |
| Monthly savings | — | ~$260/month |

---

## Strategy Deep Dive: Batch vs Real-Time

| Dimension | Real-Time | Batch API |
|---|---|---|
| Cost | 100% | 50% |
| Latency | Seconds | Minutes-hours |
| Rate limits | Shared with production | Separate queue |
| Use case | User-facing | Offline pipelines |
| Max per submission | 1 | 10,000 |

---

## Monitoring Dashboard: What to Track

| Metric | Formula | Alert threshold |
|---|---|---|
| Daily API cost | sum(token costs) × prices | > $X budget |
| Cache hit rate | cache_reads / (cache_reads + writes) | < 80% (if caching is on) |
| Model distribution | % haiku / sonnet / opus per day | Unexpected drift |
| Avg output tokens | total_output / calls | Growing >10%/week |
| Input token anomalies | max(input_tokens) per call | > 5× average |

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept guide |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Comparison.md** | ← you are here |

⬅️ **Prev:** [Batching](../10_Batching/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Error Handling](../12_Error_Handling/Theory.md)
