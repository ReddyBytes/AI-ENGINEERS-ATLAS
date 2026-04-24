# Model Reference — Interview Q&A

## Beginner Questions

**Q1: What are the three current Claude model families and their primary use cases?**

<details>
<summary>💡 Show Answer</summary>

A: (1) Claude Haiku 4.5 (`claude-haiku-4-5-20251001`) — fastest and cheapest, ideal for high-volume simple tasks like classification, extraction, translation, and simple Q&A. (2) Claude Sonnet 4.6 (`claude-sonnet-4-6`) — the balanced production workhorse, best for code generation, analysis, document processing, and general chat. (3) Claude Opus 4.6 (`claude-opus-4-6`) — highest intelligence, used for complex multi-step reasoning, expert analysis, and tasks where maximum quality is worth the cost premium.

</details>

---

<br>

**Q2: What is the context window for current Claude models?**

<details>
<summary>💡 Show Answer</summary>

A: All current Claude models (Haiku, Sonnet, Opus) share a 200,000-token context window. This is large enough to hold entire codebases, long legal documents, or full-length novels in a single conversation.

</details>

---

<br>

**Q3: What is the difference between a dated model ID like `claude-sonnet-4-6-20250219` and an undated one like `claude-sonnet-4-6`?**

<details>
<summary>💡 Show Answer</summary>

A: An undated ID always resolves to the latest version of that model family — useful in development to get the most recent improvements automatically. A dated ID is pinned to a specific model snapshot — guaranteed stable behavior, no surprise changes. Use undated IDs in development, dated IDs in production where reproducibility and stability matter.

</details>

---

<br>

**Q4: Which Claude model supports Extended Thinking?**

<details>
<summary>💡 Show Answer</summary>

A: Claude Sonnet 4.6 and Claude Opus 4.6 both support Extended Thinking (also called chain-of-thought reasoning tokens). Claude Haiku 4.5 does not support Extended Thinking. If your routing logic sends a request with Extended Thinking enabled to Haiku, it will fail.

</details>

---

## Intermediate Questions

**Q5: How do you decide between Haiku and Sonnet for a specific task?**

<details>
<summary>💡 Show Answer</summary>

A: Benchmark both models on 20-50 real examples from your task. Measure: output quality (does Haiku match Sonnet for this task?), output consistency (does Haiku produce the right format?), and failure rate. If Haiku's quality is acceptable, use it — it costs roughly 3.75× less per input token. Simple pattern matching tasks (classification, extraction, simple Q&A, translation) almost always pass the benchmark. Reasoning, code generation, and nuanced analysis typically need Sonnet or higher.

</details>

---

<br>

**Q6: What are the relative pricing differences between Haiku, Sonnet, and Opus?**

<details>
<summary>💡 Show Answer</summary>

A: Using representative input prices: Haiku = $0.80/MTok, Sonnet = $3.00/MTok, Opus = $15.00/MTok. So Sonnet costs roughly 3.75× more than Haiku, and Opus costs roughly 5× more than Sonnet (19× more than Haiku). For output tokens: Haiku = $4.00/MTok, Sonnet = $15.00/MTok, Opus = $75.00/MTok. For a production system processing 1 million tokens/day: Haiku = ~$4/day, Sonnet = ~$15/day, Opus = ~$75/day.

</details>

---

<br>

**Q7: How do you handle model deprecation in a production system?**

<details>
<summary>💡 Show Answer</summary>

A: (1) Always use dated model IDs in production (`claude-sonnet-4-6-20250219`) for stability. (2) Log `response.model` (the dated ID from the response) to your monitoring system. (3) Subscribe to Anthropic's deprecation announcements. (4) Set up an alert for when your logged model ID matches a deprecated version. (5) Test the new model ID on a sample of your production traffic before switching. (6) Update your config variable (not hardcoded strings) and deploy. Build the model ID into a config value, not a hardcoded string: `MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6")`.

</details>

---

<br>

**Q8: Why do all three model families share the same context window?**

<details>
<summary>💡 Show Answer</summary>

A: The 200K context window is a capability of the model architecture (specifically, efficient attention mechanisms that scale to long sequences) rather than an intelligence measure. Smaller models can support large context windows because the context window is about memory capacity, not reasoning ability. The trade-off for Haiku is in quality of reasoning on complex tasks, not in how much content it can read.

</details>

---

## Advanced Questions

**Q9: Design a model routing system for a SaaS platform that handles both user-facing chat and background analytics jobs.**

<details>
<summary>💡 Show Answer</summary>

A: Two routing layers: (1) Real-time routing: incoming chat messages are classified by complexity. Use a Haiku meta-classifier (10-token output: simple/medium/complex) to assign each message. Simple → Haiku (FAQ, greetings, lookups); medium → Sonnet (analysis, coding, document questions); complex → Sonnet or Opus flag for human review. Cost optimization: ~60-70% of messages are simple → Haiku, saving 70%+ on input costs. (2) Background routing: all analytics jobs → Batch API. Simple analysis → Haiku; complex synthesis → Sonnet. Combine with prompt caching for repeated analytical frameworks. (3) Circuit breaker and model fallback: if Sonnet is degraded, temporarily fall back to Sonnet with a larger Haiku model. Log fallbacks for audit.

</details>

---

<br>

**Q10: Explain the architectural reason output tokens are priced higher than input tokens across all Claude models.**

<details>
<summary>💡 Show Answer</summary>

A: Input tokens are processed in a single parallel forward pass through the transformer. The attention mechanism computes pairwise relationships, but all tokens in the input are processed together in O(n²) memory but one forward pass. Output tokens use autoregressive generation: each new token requires a full forward pass of the entire model, attending to all previous context. For a 1,000-token output, that's 1,000 separate forward passes, each full-model size. This is computationally much more expensive per token than the single input processing pass. Additionally, output generation is sequential and cannot be parallelized — you must wait for token N before generating token N+1.

</details>

---

<br>

**Q11: How does model selection interact with Extended Thinking, and when should you use it?**

<details>
<summary>💡 Show Answer</summary>

A: Extended Thinking is available on Sonnet 4.6 and Opus 4.6. When enabled, the model generates "reasoning tokens" — internal chain-of-thought — before producing the final answer. These reasoning tokens are billed as output tokens (most expensive category). You should enable Extended Thinking when: (1) The task requires multi-step mathematical or logical reasoning. (2) Code correctness is critical (debugging, algorithm design). (3) Complex analysis with multiple dependencies (financial models, legal reasoning). Don't enable it for simple tasks — you pay for reasoning tokens with no quality benefit. For Haiku routing: since Haiku doesn't support Extended Thinking, any task requiring it must route to Sonnet or Opus regardless of the complexity routing logic.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept guide |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Comparison.md](./Comparison.md) | Full model comparison |

⬅️ **Prev:** [Error Handling](../12_Error_Handling/Interview_QA.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Track 4 — Agent SDK](../../04_Claude_Agent_SDK/)
