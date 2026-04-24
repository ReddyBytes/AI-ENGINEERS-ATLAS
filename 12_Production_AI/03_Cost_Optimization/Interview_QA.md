# Interview QA — Cost Optimization

## Beginner

**Q1: What are the two main cost models for running AI in production, and how do you choose between them?**

<details>
<summary>💡 Show Answer</summary>

**A:** The two models are **pay-per-token (API)** and **pay-per-hour (self-hosting)**.

With pay-per-token, you call a provider like OpenAI or Anthropic and pay for each input and output token. Cost = `(input_tokens × input_price) + (output_tokens × output_price)`. Zero infrastructure overhead, but cost scales linearly with volume and you have no control over the model.

With self-hosting, you pay for GPU instance hours (e.g., an A100 at $5/hour) and run the model yourself. Cost per request = `instance_cost / requests_per_hour`. Higher fixed overhead (engineering time, infrastructure), but cost per request can be 10-50x lower at high volume.

The choice comes down to volume and break-even analysis. At low volume (< a few thousand requests/day), API wins because you avoid fixed infrastructure costs. At high volume, self-hosting wins because the per-request cost is far lower. Run the numbers for your specific workload — the break-even is often around 10,000-100,000 requests/day depending on the model.

</details>

---

<br>

**Q2: What is prompt caching and how does it reduce costs?**

<details>
<summary>💡 Show Answer</summary>

**A:** Prompt caching is a feature offered by Anthropic and OpenAI where the provider caches the internal KV (key-value) state computed from a repeated prompt prefix. When the next request arrives with the same prefix, the cached computation is reused instead of reprocessing those tokens.

Practical example: You have a 10,000-token system prompt that lists your company's entire product catalog and policies. Without caching, every request processes all 10,000 tokens. With caching, those tokens are processed once per cache period (typically minutes to hours). On Anthropic's API, cached tokens are billed at 10% of the normal input price — a 90% discount.

You enable it by explicitly marking the cacheable part of your prompt with a `cache_control` parameter. It is most valuable when: system prompts are long (> 1,000 tokens), the same context documents are injected repeatedly (RAG), or many users share the same system configuration.

</details>

---

<br>

**Q3: What are the most impactful quick wins for reducing LLM API costs?**

<details>
<summary>💡 Show Answer</summary>

**A:** In priority order:

1. **Switch to a cheaper model first**: For many tasks (classification, simple Q&A, text extraction), GPT-4o-mini or Claude Haiku delivers 90%+ of the quality at 3-5% of the cost. Try the cheap model first, evaluate quality, and only upgrade if needed.

2. **Enable prompt caching**: If your system prompt is more than a few hundred tokens and is reused across requests, this gives a free 40-90% discount on cached tokens. Takes 5 minutes to implement.

3. **Limit max_tokens**: If you do not set `max_tokens`, the model can generate very long responses. For tasks where 200 tokens is enough, capping at 200 can cut output costs by 60-80%.

4. **Add explicit brevity instructions**: "Answer in 2-3 sentences" or "Be concise" in your system prompt typically reduces output length by 40-60% with negligible quality impact.

5. **Compress context / implement RAG**: If you are injecting entire documents as context, switch to RAG (only inject the relevant 3-5 chunks). This can reduce input tokens by 80-95%.

</details>

---

## Intermediate

**Q4: Describe a model routing architecture that minimizes cost while maintaining quality.**

<details>
<summary>💡 Show Answer</summary>

**A:** Model routing (also called the "cascade" or "tiered" architecture) classifies incoming requests by complexity and routes them to the appropriate cost tier.

Architecture:
1. **Classifier layer**: A tiny, fast model (< 1B parameters or a simple ML classifier) analyzes the incoming request and assigns a complexity score. Signals: request length, presence of keywords indicating complex reasoning, the user's tier/subscription level.

2. **Cheap tier**: 70-80% of requests go here — a small/cheap model (Haiku, GPT-4o-mini, Mistral-7B). Handles FAQs, structured extraction, simple reformatting.

3. **Expensive tier**: 20-30% of requests — a large capable model for complex reasoning, nuanced writing, or difficult code.

4. **Evaluation loop**: Periodically sample requests from the cheap tier and run them through the expensive model. If the expensive model rates quality significantly higher, the routing threshold is too aggressive — bump more requests up.

Real savings: 60-85% cost reduction with less than 5% quality degradation (when thresholds are well-tuned). Key risk: the cheap tier silently delivers poor quality for edge cases — monitoring and periodic quality audits are essential.

</details>

---

<br>

**Q5: How would you calculate the break-even point between using an LLM API vs self-hosting?**

<details>
<summary>💡 Show Answer</summary>

**A:** The break-even analysis requires estimating costs on both sides:

**API cost (monthly):**
```
Monthly_API_cost = daily_requests × 30 × (avg_input_tokens × input_$/M + avg_output_tokens × output_$/M) / 1,000,000
```

**Self-hosting cost (monthly):**
```
GPU_cost = num_GPUs × $/hour × 24 × 30
Engineering overhead = estimated_hours × engineer_hourly_rate
Total_selfhost = GPU_cost + Engineering overhead
```

**Break-even request volume:**
```
Break-even = Monthly_overhead / (API_cost_per_req - SH_cost_per_req)
```

Example: A 7B model on a single T4 ($0.35/hour = $252/month) handles 500 requests/hour = 360,000 requests/month. Cost per request = $252 / 360,000 = $0.0007. Add $2,000/month engineering time = $2,252/month.

API (GPT-4o-mini): $0.000465/request. Break-even = $2,252 / ($0.000465 - $0.0007) = negative (API is cheaper per request here, self-hosting only makes sense at massive scale with engineering efficiency).

The analysis often reveals: self-hosting only makes economic sense when you can saturate your GPU instances (> 60% utilization) AND engineering overhead is amortized over very high volume.

</details>

---

<br>

**Q6: What is context compression and what techniques are available?**

<details>
<summary>💡 Show Answer</summary>

**A:** Context compression reduces the number of input tokens sent to the model, directly reducing cost. The goal: retain all information the model needs while removing everything else.

**Techniques:**

1. **RAG instead of full document**: Send the 3 most relevant paragraphs instead of the entire document. Reduces context from 50,000 tokens to 500. Requires embedding-based retrieval.

2. **Rolling summary of chat history**: Instead of appending the full conversation indefinitely, maintain a running summary of older messages. Keep the last 5 messages verbatim, summarize everything older. Typically reduces context by 60-80% for long conversations.

3. **Aggressive system prompt trimming**: Audit your system prompt. Remove examples that are not improving quality. Use more concise instructions. Remove repetitive constraints. Typical system prompts can be cut 30-50% without quality loss.

4. **Selective tool result inclusion**: In agentic systems, tool call results can be enormous (full web pages, large code files). Truncate or summarize tool results before including them in context.

5. **Structured output formats**: Ask for JSON instead of prose explanations. "Return JSON: {answer: string, confidence: float}" vs "Please explain your reasoning and then provide the answer..." — often 60-70% fewer output tokens.

</details>

---

## Advanced

**Q7: How would you design a cost monitoring and alerting system for an LLM-based product?**

<details>
<summary>💡 Show Answer</summary>

**A:** A production cost monitoring system needs real-time visibility and automated controls:

**Data collection layer:**
- Instrument every LLM API call: log `model`, `input_tokens`, `output_tokens`, `timestamp`, `user_id`, `request_type`, `latency`
- Compute `cost = input_tokens × input_rate + output_tokens × output_rate` in real time
- Push to a time-series database (InfluxDB, Prometheus) or a cost-specific table in your data warehouse

**Dashboards:**
- Cost per request (P50/P95)
- Daily / weekly / monthly total cost
- Cost by model (shows if expensive model is being over-used)
- Cost by request type (shows which features are most expensive)
- Cost per user / per account (for billing and abuse detection)

**Alerts:**
- **Budget alerts**: Daily cost > 120% of rolling 7-day average → PagerDuty
- **Runaway request alert**: Single user consuming > X% of daily budget → throttle + investigate
- **Anomaly detection**: Sudden spike in input token length (someone injecting a huge document) → alert + investigate

**Automated controls:**
- **Per-user token budgets**: Cap each user at 50,000 tokens/day in your app logic
- **Request cost ceiling**: Reject requests where estimated cost > threshold
- **Circuit breaker**: If hourly spend > 2x expected, automatically fall back to cheaper model

</details>

---

<br>

**Q8: When does fine-tuning a smaller model become more cost-effective than using a larger frontier model via API?**

<details>
<summary>💡 Show Answer</summary>

**A:** Fine-tuning a smaller model on your specific task can match the quality of a 10-100x larger model — but it requires upfront investment. The cost calculation has three parts:

**Fine-tuning cost (one-time):**
```
Fine_tuning_cost = training_compute_hours × $/hr + data_preparation_time × engineer_rate
Typical: $100-500 to fine-tune a 7B model on 10,000 examples
```

**Serving cost comparison (ongoing):**
```
API (GPT-4o): $15/M output tokens
Fine-tuned 7B (self-hosted T4): $0.35/hr ÷ 2,000 req/hr × 500 avg output tokens = $0.0000875/req ≈ $0.18/M output tokens
Cost ratio: 83x cheaper per token
```

**Break-even:**
```
Months to break even = Fine_tuning_cost / (Monthly_API_savings)
If fine-tuning cost = $500, monthly savings = $5,000 → break even in < 1 month
```

Fine-tuning makes sense when:
- The task is well-defined and stable (not changing constantly)
- You have > 500 high-quality training examples
- Monthly API spend on that task is > $500 (making the one-time cost worth it)
- You need consistent format/style that a smaller model learns well from examples
- Latency is important (smaller models are faster)

Fine-tuning does NOT make sense when: you need the latest knowledge (fine-tuning doesn't update knowledge cutoff), the task varies widely (the model won't generalize), or you have limited labeled data.

</details>

---

## 📂 Navigation
