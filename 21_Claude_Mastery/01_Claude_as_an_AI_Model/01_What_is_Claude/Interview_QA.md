# What is Claude? — Interview Q&A

## Beginner

**Q1: What is Claude and who makes it?**

<details>
<summary>💡 Show Answer</summary>

Claude is a family of large language models (LLMs) created by Anthropic, an AI safety company founded in 2021 by researchers who previously worked at OpenAI, including Dario and Daniela Amodei. Claude is a conversational AI that can write, reason, analyze, code, and understand images. Anthropic's distinguishing mission is building AI that is safe, interpretable, and beneficial — safety is a core design goal, not an afterthought.

</details>

---

**Q2: What are the three Claude tiers and when would you use each?**

<details>
<summary>💡 Show Answer</summary>

The three tiers are:

- **Haiku**: Fastest and cheapest. Use it for high-volume, simple tasks — classification, quick Q&A, simple transformations, routing decisions.
- **Sonnet**: Balanced speed and intelligence. Use it for most production workloads — agents, code generation, document analysis, complex chat. This is the default choice.
- **Opus**: Most capable but slowest and most expensive. Use it for the hardest reasoning tasks — complex research synthesis, difficult math, multi-step planning where quality matters more than speed.

A good mental model: Haiku for scale, Sonnet for quality at scale, Opus for when you need the absolute best answer.

</details>

---

**Q3: How is Claude different from ChatGPT?**

<details>
<summary>💡 Show Answer</summary>

Both are LLMs built on transformer architecture and refined with RLHF. The key differences:

1. **Maker**: Claude is made by Anthropic; ChatGPT is made by OpenAI (backed by Microsoft).
2. **Alignment method**: Claude uses Constitutional AI (self-critique guided by a principle set) in addition to RLHF; ChatGPT uses primarily RLHF.
3. **Safety focus**: Anthropic's entire company mission is AI safety research; OpenAI has broader commercial goals.
4. **Extended thinking**: Claude has native chain-of-thought reasoning via extended thinking; OpenAI has separate o1/o3 models for this.
5. **Context window**: Both support large contexts (Claude: 200k, GPT-4o: 128k).

In practice for engineers: both are excellent. Claude is often preferred for instruction following, long-document analysis, and safety-sensitive applications.

</details>

---

## Intermediate

**Q4: What does Anthropic mean by "helpful, harmless, and honest" (HHH)?**

<details>
<summary>💡 Show Answer</summary>

HHH is the guiding alignment objective for Claude:

- **Helpful**: Claude should genuinely assist users — not be evasive, overly cautious, or refuse legitimate requests. Unhelpfulness is explicitly treated as a failure mode.
- **Harmless**: Claude should not assist with actions that cause harm to users, third parties, or society. It should decline clearly harmful requests.
- **Honest**: Claude should not deceive, manipulate, or misrepresent. It should express uncertainty rather than confidently state falsehoods.

The key insight is that these three are in tension. Being maximally helpful could mean helping with harmful tasks. Being overly cautious (refusing too much) violates helpfulness. Claude's training tries to find the right balance — the Constitutional AI process explicitly tries to make the model helpful while avoiding harm.

</details>

---

**Q5: What is Claude's context window and why does it matter?**

<details>
<summary>💡 Show Answer</summary>

The context window is the maximum number of tokens (roughly word-pieces) Claude can process in a single API call — both the input you send and the output it generates. Current Claude models support up to 200,000 tokens, which is roughly 150,000 words or about 500 pages of text.

Why it matters:
- Determines how much document content you can process in one call
- Limits how much conversation history an agent can retain
- Affects cost — you pay per token, so longer contexts cost more
- Very long contexts can degrade quality (the "lost in the middle" problem)
- Sets the upper bound for what RAG systems need to handle

For most applications, 200k is sufficient. But engineers still need chunking strategies for very large codebases or document collections.

</details>

---

**Q6: What is Claude's knowledge cutoff and how should engineers handle it?**

<details>
<summary>💡 Show Answer</summary>

Claude's training data has a cutoff date — it has no information about events after that date. The exact cutoff varies by model version but is typically 6–12 months before the model's release.

How to handle it:

1. **Use Retrieval-Augmented Generation (RAG)**: Give Claude current documents via the context window, not via training
2. **Tool calling**: Give Claude a web search tool to retrieve current information
3. **Explicit prompting**: Tell Claude when it might have outdated information and ask it to flag uncertainty
4. **Don't ask for "current" data**: Prices, stock values, recent news — always externally sourced

Engineers building production systems should never rely on Claude's parametric knowledge for time-sensitive facts.

</details>

---

## Advanced

**Q7: How does Anthropic's Constitutional AI approach differ from standard RLHF in terms of scalability and alignment?**

<details>
<summary>💡 Show Answer</summary>

Standard RLHF requires human labelers to evaluate model outputs and train a reward model. This has two scaling problems:

1. **Human bottleneck**: Labeler capacity limits how much feedback you can generate
2. **Inconsistency**: Different labelers have different values and interpretations

Constitutional AI (CAI) replaces much of the human feedback with AI self-critique. The model critiques and revises its own outputs against a written constitution (a set of principles). This allows:

- Generating millions of training examples without proportional human annotation cost
- Explicit, auditable principles rather than implicit labeler preferences
- Systematic testing of specific behaviors (harmlessness in particular)

However, CAI doesn't replace humans entirely — the constitution itself must be written and refined by humans, and some human feedback is still used in the final RLHF stage. The advantage is that it massively scales the annotation throughput while making the value system inspectable.

</details>

---

**Q8: What are the practical implications of Claude having no persistent memory across sessions?**

<details>
<summary>💡 Show Answer</summary>

By default, each Claude API call is stateless — Claude has no memory of previous calls. This has several engineering implications:

1. **Conversation history**: You must manually include previous messages in each API request using the messages array. As conversations grow, this consumes more context window and costs more.

2. **Agent state**: Long-running agents must externally persist their state (tools used, observations made, decisions taken) and inject it back into context.

3. **User personalization**: User preferences, history, and context must be stored in an external database and retrieved for each session.

4. **Memory architecture**: Production applications need a memory system layer — typically: short-term (in-context), medium-term (recent summaries), long-term (vector DB retrieval).

This is an intentional design choice, not a limitation — statelessness makes the model simpler, more predictable, and easier to reason about. Engineers build the persistence layer on top.

</details>

---

**Q9: How should an engineer make the model tier routing decision programmatically?**

<details>
<summary>💡 Show Answer</summary>

Model routing is the practice of using the cheapest model sufficient for each task. A production system might route like this:

```
if task.is_simple_classification():
    model = "claude-haiku-4-5"
elif task.requires_complex_reasoning():
    model = "claude-opus-4"
else:
    model = "claude-sonnet-4-6"  # default
```

More sophisticated routing uses:

1. **Task complexity signals**: length of input, presence of multi-step reasoning requirements, tool calls needed
2. **Quality gates**: run Haiku first; if confidence is low (detected via output analysis), escalate to Sonnet
3. **Cost budgets**: hard cap on expensive model usage per user/day
4. **Latency requirements**: user-facing real-time chat → Haiku/Sonnet; async batch processing → Opus acceptable
5. **A/B testing**: route a percentage to both models and compare quality metrics

The routing logic itself can be a small classifier or rule-based system. The payoff at scale is significant — if 80% of requests can use Haiku instead of Sonnet, that's roughly a 4-5x cost reduction on that portion.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |

⬅️ **Prev:** [Section README](../Readme.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [02 How Claude Generates Text](../02_How_Claude_Generates_Text/Theory.md)
