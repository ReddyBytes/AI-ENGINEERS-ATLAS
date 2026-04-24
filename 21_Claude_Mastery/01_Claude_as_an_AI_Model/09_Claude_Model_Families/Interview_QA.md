# Claude Model Families — Interview Q&A

## Beginner

**Q1: What are the three Claude model tiers and when should you use each?**

<details>
<summary>💡 Show Answer</summary>

The three tiers are Haiku, Sonnet, and Opus — ordered from fastest/cheapest to most capable/expensive.

**Haiku**: Best for high-volume applications where tasks are well-defined and speed matters. Classification, routing, simple Q&A, entity extraction. Roughly 12x cheaper than Sonnet per token.

**Sonnet**: The production default for most workloads. General-purpose coding, document analysis, agent systems, chat. This is the model powering Claude Code. Use this as your starting point for any new application.

**Opus**: Reserved for the hardest reasoning problems where quality is the only constraint. Graduate-level research, complex legal analysis, multi-step mathematical proofs. Can be 4–5x more expensive than Sonnet.

The mental model: Haiku for scale, Sonnet for quality, Opus for when Sonnet isn't enough.

</details>

---

<br>

**Q2: Why shouldn't you just always use Opus since it's the most capable?**

<details>
<summary>💡 Show Answer</summary>

Three reasons:

1. **Cost**: Opus is approximately 60x more expensive than Haiku and 5x more expensive than Sonnet per million tokens. For an application making 100,000 API calls per day, the difference between Sonnet and Opus can be $10,000+ per month.

2. **Latency**: Opus is slower — roughly 2–3x slower time-to-first-token than Sonnet. For user-facing features, this degrades the experience.

3. **Diminishing returns**: The vast majority of real-world tasks (simple Q&A, document summarization, standard code generation) show no measurable quality improvement with Opus over Sonnet. You're paying for capability you're not using.

The engineering discipline is matching the model to the task — the same way you wouldn't use a supercomputer to run a to-do list app.

</details>

---

<br>

**Q3: What does it mean to "pin" a model ID in production?**

<details>
<summary>💡 Show Answer</summary>

Pinning means using the exact versioned model ID (`claude-sonnet-4-6`) rather than an alias that might update (`claude-sonnet-latest`).

Why it matters: Anthropic updates models periodically. A model alias pointing to the "latest" version might update, introducing subtle behavior changes that break your application, change output format, or affect safety behaviors.

By pinning to a specific model ID:
- Your application behaves consistently until you explicitly update
- You can test new model versions in staging before updating production
- Debugging is cleaner — you know exactly which model was used when

Best practice: pin model IDs, test new versions in a branch/staging environment, update production only after validation.

</details>

---

## Intermediate

**Q4: How do you build a model routing system in production?**

<details>
<summary>💡 Show Answer</summary>

A model routing system automatically selects the right Claude model based on task characteristics:

```python
class ModelRouter:
    MODELS = {
        "haiku": "claude-haiku-4-5",
        "sonnet": "claude-sonnet-4-6",
        "opus": "claude-opus-4",
    }
    
    def route(self, task: dict) -> str:
        # Hard-code high-volume simple tasks to Haiku
        if task["type"] in ["classify", "extract", "route"]:
            return self.MODELS["haiku"]
        
        # Hard-code complex reasoning to Opus
        if task["type"] in ["research", "math"] and task.get("complexity") == "hard":
            return self.MODELS["opus"]
        
        # Estimate complexity from input length + type
        token_count = task.get("estimated_tokens", 0)
        if token_count > 50_000 or task.get("requires_multi_step"):
            return self.MODELS["sonnet"]
        
        # Default
        return self.MODELS["sonnet"]
```

More sophisticated approaches:
- Use Haiku to classify whether a task needs Sonnet/Opus
- Cascade: try Haiku first, escalate if confidence below threshold
- Budget-aware: route to Haiku when daily token budget is 80% consumed
- A/B test: route 5% of requests to Opus, compare quality, calibrate

</details>

---

<br>

**Q5: What is the performance difference between Claude model generations (e.g., Sonnet vs Sonnet 4.5 vs Sonnet 4.6)?**

<details>
<summary>💡 Show Answer</summary>

Within the same tier (Sonnet), newer generation models are generally:
- More capable (better benchmark scores, better instruction following)
- Often similar or lower cost per token
- Not always backward compatible — subtle behavior changes

The version numbering generally follows: `claude-[tier]-[generation]` (e.g., `claude-sonnet-4-6`). Higher numbers = newer release.

Upgrade strategy:
1. Check Anthropic's release notes for what changed
2. Run your existing eval suite on the new model
3. Test edge cases and safety-sensitive prompts
4. A/B test in production with a small traffic percentage
5. Update the pinned model ID after validation

Never upgrade production model IDs without testing — even "improvements" can change behavior in ways that affect your specific use case.

</details>

---

<br>

**Q6: How do you measure whether a cheaper model is "good enough" for your use case?**

<details>
<summary>💡 Show Answer</summary>

This requires building an evaluation framework:

1. **Collect a representative test set**: 100–500 real prompts from your use case, covering easy, medium, and hard cases

2. **Define quality criteria**: What does "good" mean for your task? Options:
   - Automated metrics (ROUGE score, exact match, JSON validity)
   - LLM-as-judge (use a capable model to grade outputs)
   - Human eval on a sample

3. **Run the test set on multiple models**: Compare Haiku vs Sonnet on the same prompts

4. **Set a quality threshold**: "We accept models that score ≥ 95% on our eval suite"

5. **Calculate break-even cost**: If Haiku is 12x cheaper but only 5% worse quality, is that acceptable for your use case? Depends on volume and stakes.

6. **Monitor in production**: Quality metrics can drift as prompts change. Continuously monitor and re-evaluate.

</details>

---

## Advanced

**Q7: How does Anthropic decide when to add a new model or update an existing tier?**

<details>
<summary>💡 Show Answer</summary>

Based on Anthropic's public communications, new model releases are driven by several factors:

1. **Research milestones**: When a new pretraining run + RLHF cycle produces meaningfully better capability on targeted benchmarks (especially reasoning, coding, instruction following)

2. **Responsible Scaling Policy**: New models are only released after passing safety evaluations at the relevant AI Safety Level (ASL). This gates deployment regardless of capability improvements.

3. **Competitive response**: The AI model market moves quickly; new releases from competitors may trigger accelerated deployment of models that were training

4. **Infrastructure readiness**: Serving a frontier model reliably at scale requires infrastructure preparation — routing, latency guarantees, prompt caching support

5. **Customer demand**: Enterprise customers provide feedback on capability gaps; common themes influence what the next generation prioritizes

For engineers: track the Anthropic model release blog and check model IDs quarterly to avoid running on deprecated models.

</details>

---

<br>

**Q8: How do context window size and model tier interact for cost and quality?**

<details>
<summary>💡 Show Answer</summary>

All current Claude models support 200k tokens, but using a large context has cost and quality implications:

**Cost**: Every token in the input (including the full 200k if you use it) is billed at the input rate. A 200k token prompt costs:
- Haiku: (200,000 / 1,000,000) × $0.25 = $0.05 per call
- Sonnet: (200,000 / 1,000,000) × $3.00 = $0.60 per call
- Opus: (200,000 / 1,000,000) × $15.00 = $3.00 per call

For high-context use cases (analyzing 200-page documents), Opus becomes prohibitively expensive. This is often where Sonnet or even Haiku with well-chunked input is the practical choice.

**Quality**: Very long contexts can degrade quality due to the "lost in the middle" problem — models recall information at the start and end of context better than the middle. Opus may handle very long contexts more reliably than Haiku, but the quality gap narrows for well-structured long-context tasks.

**Prompt caching**: Anthropic's prompt caching feature reduces costs for repeated long context by ~90%. For use cases with large fixed system prompts (documentation, rules), caching is essential regardless of model tier.

</details>

---

<br>

**Q9: What is the tradeoff between using Haiku with a more complex prompt vs Sonnet with a simpler prompt?**

<details>
<summary>💡 Show Answer</summary>

This is a real cost optimization question. A more complex prompt (more tokens) on Haiku costs more in input tokens but less on the output side. Sonnet with a minimal prompt is cheaper per token but is billed at a higher rate.

The math:
```
Option A: Haiku + complex prompt (500 input, 100 output)
  Cost = (500 × $0.25 + 100 × $1.25) / 1M = $0.000250

Option B: Sonnet + minimal prompt (100 input, 100 output)  
  Cost = (100 × $3.00 + 100 × $15.00) / 1M = $0.001800

Option A is 7x cheaper for similar task quality.
```

But quality matters too: Haiku + complex prompt may still produce worse output than Sonnet + minimal prompt for hard tasks. The right trade is:

1. Benchmark both approaches on your actual task
2. If Haiku + extra prompt context achieves acceptable quality: use it, save money
3. If Haiku can't be made to work with prompting: use Sonnet

The key insight: adding few-shot examples, explicit instructions, or step-by-step guidance to a Haiku prompt can dramatically improve quality — sometimes enough to match Sonnet on specific, well-defined tasks.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Comparison.md](./Comparison.md) | Detailed model comparison |

⬅️ **Prev:** [08 Extended Thinking](../08_Extended_Thinking/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [10 Safety Layers](../10_Safety_Layers/Theory.md)
