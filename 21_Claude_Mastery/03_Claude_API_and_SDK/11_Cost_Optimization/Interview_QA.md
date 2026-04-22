# Cost Optimization — Interview Q&A

## Beginner Questions

**Q1: What are the five main levers for reducing Claude API costs?**

A: (1) Model routing — match each task to the cheapest model capable of doing it (Haiku for simple tasks, Sonnet for most production work, Opus for maximum quality). (2) Prompt caching — cache large static system prompts and documents at 0.1× cost on cache reads. (3) Batching — submit non-real-time workloads to the Batches API for 50% discount. (4) Output length control — right-size `max_tokens` and write prompts that produce concise outputs. (5) Token counting — use `count_tokens()` to predict cost before sending bulk requests.

---

**Q2: How do you count tokens before making an API call?**

A: Use `client.messages.count_tokens()` with the same parameters as your intended `messages.create()` call. It uses the identical tokenizer and returns the exact input token count without making the actual API call and incurring output costs.

---

**Q3: Why do output tokens cost more than input tokens?**

A: Output tokens require the model to do autoregressive generation — each token is computed one at a time with attention across all previous tokens. Input tokens are processed in a single parallel forward pass. The additional compute for generation justifies the higher per-token price. This asymmetry means that reducing output verbosity (shorter, more focused answers) often has a larger impact on cost than reducing input length.

---

**Q4: When should you use Haiku instead of Sonnet?**

A: When the task is simple and well-defined — classification, entity extraction, translation, simple Q&A, formatting. Haiku handles these reliably at roughly 10× lower cost. Use Sonnet when tasks require reasoning, code generation, analysis, or understanding of complex context. Always benchmark both models on 20-50 real examples before making the routing decision in production.

---

## Intermediate Questions

**Q5: How do you implement model routing in a production system?**

A: Build a routing layer that classifies each incoming request by task type and maps it to the appropriate model. Simple approach: a lookup dict of `{task_type: model_id}`. Sophisticated approach: a meta-classifier (itself a Haiku call) that reads the user's message and returns the appropriate routing label. Whichever approach you use, log `model_used` for every call — this lets you audit routing decisions and calculate actual costs per model.

---

**Q6: What monitoring should you build for cost optimization?**

A: Track per-call: `input_tokens`, `output_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens`, model used, and latency. Aggregate daily: total cost by model, cache hit rate, average tokens per call. Alert on: daily cost exceeding budget threshold, sudden spike in input tokens (possible prompt expansion bug), cache hit rate dropping below expected (dynamic prefix breaking caching), output tokens growing over time (response length drift).

---

**Q7: How does reducing output length affect both cost and quality?**

A: Output tokens cost 3-5× more than input tokens, so shorter outputs reduce cost significantly. Quality impact depends on the task: for classification (one word output), forcing brevity has zero quality cost. For explanations, summary, or reasoning, forcing too-short outputs hurts quality. The right approach is task-specific: write prompts that ask for the minimum needed output for that task. "Answer in one sentence" for simple facts. "List the top 5 bullet points" for analysis. Never set `max_tokens=4096` for a task where the answer is one word.

---

**Q8: Explain the ROI calculation for deciding whether to add prompt caching.**

A: Break-even calculation: Cache write costs 1.25× one call's input price. Cache reads cost 0.10×. Break-even is at ~1.4 reads (1.25 / (1-0.10) ≈ 1.39). After 2 reads, you're saving money. For a 2,000-token system prompt at $3/MTok (Sonnet): write cost = $0.0075. Each read saves $0.0054 (90% of $0.006). With 10 calls/day: daily savings = $0.054 - $0.0075 = $0.047/day = ~$17/year. With 1,000 calls/day: daily savings = $5.39/day = ~$1,967/year. Caching pays off at any scale above ~5 calls/day with a substantial system prompt.

---

## Advanced Questions

**Q9: Design a complete cost optimization strategy for a production customer support chatbot processing 50,000 conversations per day.**

A: Multi-layer strategy: (1) Routing: Build a classifier (Haiku, <10 tokens output) that labels each message as simple/medium/complex. Route: simple queries (FAQs, account lookups) → Haiku; conversation/analysis → Sonnet; escalation/complex → Sonnet. Expected: 60% Haiku, 38% Sonnet, 2% Opus. (2) Caching: System prompt (~3,000 tokens of business rules, persona, product knowledge) cached for all calls. At 50,000 calls/day: saves ~$135/day on Sonnet input alone. (3) Output control: System prompt specifies "respond in 2-3 sentences" for routine queries, allowing full responses for complex issues. (4) Session batching: End-of-day transcript analysis jobs use Batches API at 50% off. (5) Monitoring: Per-conversation cost tracked in database. Alert if average >$0.05/conversation.

---

**Q10: When is it more cost-effective to use few-shot examples vs a larger model for quality improvement?**

A: Few-shot adds input tokens (cost) but may produce the same quality as a larger model. Analysis: if 5 examples × 200 tokens = 1,000 additional input tokens per call, and there are 10,000 calls/day, that's 10M additional input tokens/day. At Haiku pricing ($0.80/MTok) = $8/day. Sonnet costs $3/MTok vs Haiku $0.80/MTok for input, or roughly 3.75× more. If the baseline input is 500 tokens: switching from Haiku to Sonnet costs $2.20 × 10,000 calls = $22/day extra. Using few-shot on Haiku ($8/day) beats upgrading to Sonnet ($22/day). But if few-shot quality still doesn't match Sonnet, you need to factor in the downstream cost of low-quality outputs (re-classification, human review).

---

**Q11: How do you prevent cost overruns from prompt injection or adversarial long inputs?**

A: Defense layers: (1) Input validation: enforce max input length before sending to the API. Reject or truncate inputs > N tokens. (2) Token counting: count tokens before every call; reject if > threshold. (3) `max_tokens` ceiling: always set a hard cap appropriate to the task — never unlimited. (4) Rate limiting: per-user request limits in your application layer prevent a single user from generating enormous API spend. (5) Spending alerts: set daily/hourly budget alerts in the Anthropic Console and via your observability stack. (6) Anomaly detection: if a specific user generates 100× the average token count, trigger an automatic review. (7) For public-facing apps: consider requiring authentication before API access and tracking spend per authenticated user.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept guide |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Comparison.md](./Comparison.md) | Strategy comparison |

⬅️ **Prev:** [Batching](../10_Batching/Interview_QA.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Error Handling](../12_Error_Handling/Interview_QA.md)
