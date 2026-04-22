# Prompt Engineering

## The Story 📖

Imagine you're delegating a task to a brilliant but literal-minded contractor. You could say "write me something about dogs" — and you'd get something. But if you said "write a 200-word educational summary of dog breeds, structured as: intro paragraph, three bullet points (breed name, origin, temperament), closing sentence" — you'd get exactly what you needed.

The contractor has the same capability in both cases. What changed was the quality of your instruction. That's **prompt engineering**: the craft of writing instructions that extract the precise output you need from a model's existing capability.

This isn't magic — it's communication. Claude is extraordinarily capable, but it can only produce what the prompt asks for (explicitly or implicitly). The difference between a mediocre and excellent prompt can be the difference between hours of post-processing and zero post-processing.

👉 This is why we need **prompt engineering** — raw capability means nothing without the ability to reliably direct it toward the right output.

---

## What is Prompt Engineering? 🎯

**Prompt engineering** is the practice of designing, structuring, and iterating on inputs (prompts) to language models to achieve consistent, high-quality outputs for a specific task.

It is not a workaround for model limitations — it's how you communicate clearly with a powerful but literal system. Just as you'd write a clear spec for a software engineer, you write clear prompts for Claude.

Key domains of prompt engineering for Claude:
- Zero-shot prompting
- Few-shot prompting
- Chain-of-thought reasoning
- XML structural tags
- Role prompting
- Output format specification
- Prefilling the assistant turn
- Claude-specific techniques

---

## Zero-Shot Prompting 🚀

**Zero-shot** means asking the model to perform a task without providing any examples. You describe what you want and rely on the model's trained knowledge.

```python
# Zero-shot — no examples
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=512,
    messages=[{
        "role": "user",
        "content": "Classify this customer review as POSITIVE, NEGATIVE, or NEUTRAL:\n\n'The shipping was fast but the product quality was disappointing.'"
    }]
)
```

Zero-shot works well for tasks where Claude has strong training signal (classification, translation, summarization, Q&A). It fails when the output format must be very specific or when the task is unusual enough that more guidance is needed.

---

## Few-Shot Prompting 📚

**Few-shot** means providing 1-5 examples of the task before asking Claude to do the same. Examples teach format, tone, and the exact output structure you need.

```python
FEW_SHOT_PROMPT = """Classify customer reviews.

Review: "Best product I've ever bought. Arrived early!"
Classification: POSITIVE

Review: "It broke after one day. Terrible quality."
Classification: NEGATIVE

Review: "Package arrived on time. Product is okay."
Classification: NEUTRAL

Review: "The color is different from the photo but it works fine."
Classification:"""
```

Few-shot examples should:
- Cover the range of cases (edge cases too)
- Have the exact format you want in the output
- Be labeled consistently
- Be 2-5 examples (more than 5 rarely helps and adds tokens)

---

## Chain-of-Thought (CoT) Reasoning 🧠

**Chain-of-thought** prompting asks Claude to reason step by step before giving a final answer. This dramatically improves accuracy on complex reasoning, math, and multi-step problems.

```python
# Without CoT — Claude guesses
"Q: Roger has 5 tennis balls. He buys 2 more cans of 3 balls. How many?"

# With CoT — Claude reasons
"Q: Roger has 5 tennis balls. He buys 2 more cans of 3 balls. How many? Think step by step."

# Claude's response:
# Step 1: Roger starts with 5 tennis balls.
# Step 2: He buys 2 cans × 3 balls per can = 6 new balls.
# Step 3: Total = 5 + 6 = 11 tennis balls.
# Answer: 11
```

Trigger phrases for CoT:
- "Think step by step"
- "Let's work through this carefully"
- "Show your reasoning before giving the answer"
- "First, analyze X. Then, determine Y. Finally, conclude Z."

For Claude specifically, you can use **extended thinking** (separate parameter) for even deeper reasoning on complex problems.

---

## XML Tags for Structure 🏷️

Claude was trained on large amounts of XML-structured text and responds particularly well to XML tags as organizing containers. XML tags help Claude distinguish between different parts of a complex prompt.

```python
system = """
<task>
You analyze customer feedback and extract actionable insights.
</task>

<output_format>
Return a JSON object with:
- summary: one sentence overview
- sentiment: POSITIVE/NEGATIVE/NEUTRAL/MIXED
- issues: list of identified problems (empty list if none)
- suggestions: list of improvement suggestions (empty list if none)
</output_format>

<rules>
- Keep the summary under 20 words
- List maximum 5 issues and 5 suggestions
- Be specific, not generic ("improve shipping speed" not "improve service")
</rules>
"""
```

Use XML tags to separate:
- Task definition from constraints
- Examples from instructions
- Input data from formatting requirements
- Rules from context

---

## Role Prompting 🎭

**Role prompting** tells Claude to act as a specific expert or persona. This activates relevant knowledge and communication patterns.

```python
# Generic
"Explain gradient descent"

# Role-based
"You are a university professor teaching machine learning to undergraduate students. Explain gradient descent using a concrete everyday analogy before introducing any math."

# Expert role
"You are a senior security engineer performing a code review. Analyze this Python function for security vulnerabilities: [code]"
```

Role prompting works because Claude's training included examples of how different types of experts communicate. Activating a role activates the associated vocabulary, structure, and level of detail.

---

## Structured Output Extraction 📊

For applications that consume Claude's output programmatically, you need predictable structure. Two patterns:

### JSON output

```python
system = """Return only valid JSON. No prose before or after.
Schema: {"name": string, "age": integer, "email": string | null}"""

# Prefill the assistant turn to guarantee JSON starts immediately
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=512,
    system=system,
    messages=[
        {"role": "user", "content": "Extract contact info: John Smith, 34, john@example.com"},
        {"role": "assistant", "content": "{"}  # prefill forces JSON
    ]
)
# response.content[0].text starts with the JSON body (after the prefilled "{")
full_json = "{" + response.content[0].text
```

### Prefilling the assistant turn

**Prefilling** adds an incomplete assistant message to the end of the messages array. Claude must continue from exactly where you left it:

```python
messages = [
    {"role": "user", "content": "Answer in exactly 3 words:"},
    {"role": "assistant", "content": "The answer is:"}  # Claude MUST continue from here
]
```

Prefilling guarantees output format at the start — useful for JSON, XML, code blocks, and other structured starts.

---

## Claude-Specific Tips 🎯

### 1. Be direct, not polite

Claude doesn't need please and thank you in every prompt. Directness improves reliability.

```
Weak:  "Could you possibly help me understand..."
Better: "Explain X. Use 3 bullet points."
```

### 2. State what you want, not what you don't want

```
Weak:  "Don't use jargon. Don't be verbose. Don't use passive voice."
Better: "Use simple words. Keep each sentence under 15 words. Use active voice."
```

### 3. Give Claude an "out" on uncertainty

```python
"If you don't know the answer with confidence, say 'I'm not certain' rather than guessing."
```

This reduces hallucination for factual questions.

### 4. Use the `<thinking>` tag for complex tasks

For tasks where you want Claude to reason before answering but keep the reasoning separate from the response:

```python
system = "For complex questions, put your reasoning in <thinking> tags first, then give your final answer outside those tags."
```

### 5. Temperature control for creativity vs consistency

```python
# Deterministic, consistent output (classification, extraction)
temperature=0.0

# Balanced (most tasks)
temperature=0.7   # default

# Creative, varied (brainstorming, writing)
temperature=1.0
```

---

## The Prompt Engineering Iteration Loop 🔄

```mermaid
flowchart LR
    A["Write initial prompt"] --> B["Test on 5-10 examples"]
    B --> C{Failures?}
    C -->|Yes| D["Identify failure pattern"]
    D --> E["Add examples / clearer instructions"]
    E --> B
    C -->|No failures\n(in test set)| F["Test on edge cases"]
    F --> G{Pass?}
    G -->|Yes| H["Production ready"]
    G -->|No| D
```

---

## Common Mistakes to Avoid ⚠️

- **Mistake 1 — Asking for multiple things in one prompt:** "Summarize this, translate it to French, and then classify the sentiment." Split into separate calls for reliability.
- **Mistake 2 — No output format specification:** Unspecified format = unpredictable format. Always state: number of words, JSON vs text, bullet points vs prose.
- **Mistake 3 — Vague evaluation:** "Test if the output looks good." Define success criteria before you start. What percentage of test cases must pass?
- **Mistake 4 — Forgetting that Claude is literal:** If you say "write a story," you get a story. If you want a specific structure, describe the structure explicitly.
- **Mistake 5 — Over-constraining:** Too many rules create contradictions. Priority rank your constraints and resolve conflicts.

---

## Connection to Other Concepts 🔗

- Relates to **System Prompts** (Topic 04) because most prompt engineering techniques are applied inside the system parameter
- Relates to **Few-Shot** pattern and **CoT** in Section 08 (LLM Applications) for deeper treatment of these techniques
- Relates to **Extended Thinking** in Track 1 Topic 08 for Claude's native reasoning mode
- Relates to **Cost Optimization** (Topic 11) because better prompts produce shorter, more precise outputs — reducing output token costs

---

✅ **What you just learned:** Prompt engineering techniques — zero-shot, few-shot, CoT, XML tags, role prompting, prefilling, and output format specification — let you reliably extract precise outputs from Claude's capability.

🔨 **Build this now:** Take a complex extraction task (e.g., extract structured data from messy text). Write the prompt three ways: zero-shot, few-shot (3 examples), and with XML structure tags. Compare quality and consistency across 10 test cases.

➡️ **Next step:** [Prompt Caching](../09_Prompt_Caching/Theory.md) — learn how to reuse expensive prompt tokens across multiple calls to cut costs.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| 📄 **Theory.md** | ← you are here |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Common_Mistakes.md](./Common_Mistakes.md) | Common mistakes guide |
| [📄 Code_Example.md](./Code_Example.md) | Working code |

⬅️ **Prev:** [Vision](../07_Vision/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Prompt Caching](../09_Prompt_Caching/Theory.md)
