# Prompt Engineering — Cheatsheet

## Technique Quick Reference

| Technique | When to use | Key pattern |
|---|---|---|
| Zero-shot | Simple, well-defined tasks | Just describe the task |
| Few-shot | Format-critical tasks | 2-5 labeled examples |
| Chain-of-thought | Math, reasoning, multi-step | "Think step by step" |
| XML tags | Complex, multi-part prompts | `<task>`, `<rules>`, `<format>` |
| Role prompting | Expert knowledge, specific style | "You are a [expert]..." |
| Output prefilling | Guaranteed output format | Last msg = partial assistant |
| Temperature tuning | Control randomness | 0.0 extract, 0.7 default, 1.0 creative |

---

## Zero-Shot Template

```python
"[Task description]. [Output format]. [Constraints].\n\nInput: {input}"
```

Example:
```
Classify this review as POSITIVE, NEGATIVE, or NEUTRAL.
Return only the label, nothing else.

Review: "Fast shipping, product was damaged."
```

---

## Few-Shot Template

```
[Task description]

Input: [example 1 input]
Output: [example 1 output]

Input: [example 2 input]
Output: [example 2 output]

Input: {actual input}
Output:
```

---

## Chain-of-Thought Triggers

```
"Think step by step."
"Let's work through this carefully."
"First analyze X, then determine Y, finally conclude Z."
"Show your reasoning before giving the final answer."
```

---

## XML Structure Tags

```xml
<task>What to do</task>
<context>Background information</context>
<rules>Constraints and requirements</rules>
<examples>Sample inputs and outputs</examples>
<output_format>Exact structure required</output_format>
```

---

## Prefilling Assistant Turn (Guaranteed Format)

```python
messages = [
    {"role": "user", "content": "Extract info as JSON..."},
    {"role": "assistant", "content": "{"}  # forces JSON output
]
```

Claude MUST continue from the prefilled text.

---

## Temperature Guide

```python
temperature=0.0   # deterministic — extraction, classification, code
temperature=0.3   # mostly deterministic — factual Q&A
temperature=0.7   # balanced — general assistant (default)
temperature=1.0   # creative — brainstorming, stories, variety
```

---

## Role Prompting Patterns

```python
# Expert knowledge
"You are a senior [role] with 15 years of experience in [domain]."

# Audience-appropriate explanation
"You are a professor explaining [topic] to undergraduate students."

# Specific communication style
"You are a technical writer creating documentation for developers."

# Strict function
"You are a JSON extraction engine. Return only valid JSON. No prose."
```

---

## Output Format Rules

```python
# Explicit structure
"Respond with exactly 3 bullet points, each starting with a bold term."

# Word count
"Keep your answer under 50 words."

# Schema
"Return JSON with this exact schema: {field1: str, field2: int}"

# Code
"Return only the Python function. No explanation."
```

---

## Claude-Specific Tips

1. Be direct: `"List 5 examples."` not `"Could you possibly list some examples?"`
2. Positive framing: `"Use active voice."` not `"Don't use passive voice."`
3. Uncertainty escape: `"If unsure, say 'I don't know' rather than guessing."`
4. Split complex tasks: one call per task type, not 5 in one
5. Temperature = 0.0 for deterministic pipelines

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept guide |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Common_Mistakes.md](./Common_Mistakes.md) | Common mistakes |
| [📄 Code_Example.md](./Code_Example.md) | Working code |

⬅️ **Prev:** [Vision](../07_Vision/Cheatsheet.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Prompt Caching](../09_Prompt_Caching/Cheatsheet.md)
