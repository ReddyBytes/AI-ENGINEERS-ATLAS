# Prompt Engineering — Cheatsheet

**One-liner:** Prompt engineering is the craft of writing instructions that reliably get the output you want from an LLM.

---

## Key Terms

| Term | Definition |
|------|-----------|
| **Prompt** | Everything you send to the model before it responds |
| **System message** | Persistent rules/role set before the conversation starts |
| **User message** | The per-turn request from the user |
| **Zero-shot** | No examples — just the instruction |
| **Few-shot** | 2–5 examples shown before the real task |
| **Chain-of-Thought (CoT)** | Asking the model to reason step-by-step before answering |
| **Role prompting** | Giving the model a specific identity ("You are a...") |
| **Temperature** | Controls randomness: 0 = deterministic, 1 = creative |
| **Token** | The unit the model reads/writes (roughly 0.75 words) |
| **Context window** | Max tokens the model can process at once |
| **Output format** | Explicit structure you ask the model to follow (JSON, table, etc.) |

---

## Prompting Techniques Quick Reference

| Technique | When to Use | Example Trigger |
|-----------|------------|-----------------|
| Zero-shot | Simple, well-known tasks | "Summarize this." |
| Few-shot | Custom formats, classification | Show 3 examples first |
| Chain-of-Thought | Math, logic, reasoning | "Think step by step." |
| Role prompting | Tone/expertise adjustment | "You are a senior engineer..." |
| Output format | Parsing, structured data | "Return as JSON with fields..." |
| Step-by-step | Complex multi-part tasks | "First do X, then Y, then Z." |

---

## When to Use / Not Use

| Use prompting when... | Don't rely on prompting alone when... |
|-----------------------|--------------------------------------|
| Task is well-defined and consistent | You need 100% guaranteed output format (use tool calling instead) |
| Examples make the pattern clear | The task requires real-time data (use tool calling) |
| You want low-cost, fast iteration | The model needs domain knowledge it wasn't trained on (consider fine-tuning) |
| Output varies slightly and that's OK | You need exact database-style precision |

---

## Temperature Guide

| Value | Behavior | Best For |
|-------|----------|----------|
| 0.0 | Fully deterministic | Facts, code, data extraction |
| 0.2–0.4 | Very focused | Customer support, classification |
| 0.5–0.7 | Balanced | Most production use cases |
| 0.8–1.0 | Creative and varied | Brainstorming, writing, ideation |

---

## Golden Rules

1. **Be specific** — vague instructions produce vague outputs.
2. **Give a role** — "You are a..." instantly improves quality.
3. **Show don't tell** — examples beat long descriptions every time.
4. **Specify the format** — if you need JSON, say so explicitly.
5. **Use step-by-step for reasoning** — always improves accuracy on logic tasks.
6. **Low temperature for consistency** — production prompts usually use 0.0–0.3.
7. **Test with edge cases** — what happens when the input is weird or empty?
8. **System message for persistent rules** — don't repeat instructions in every user turn.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |
| [📄 Common_Mistakes.md](./Common_Mistakes.md) | Common prompt engineering mistakes |
| [📄 Prompt_Patterns.md](./Prompt_Patterns.md) | Reusable prompt patterns |

⬅️ **Prev:** [09 Using LLM APIs](../../07_Large_Language_Models/09_Using_LLM_APIs/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [02 Tool Calling](../02_Tool_Calling/Theory.md)
