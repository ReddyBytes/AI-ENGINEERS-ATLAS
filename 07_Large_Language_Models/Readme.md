# 07 — Large Language Models

## What is this section about?

Large Language Models (LLMs) are the technology behind ChatGPT, Claude, Gemini, and most modern AI assistants. This section walks you from "what is an LLM?" all the way to "how do I build with one and keep costs under control?"

You don't need a PhD. You need curiosity and this guide.

---

## Why LLMs matter

A few years ago, getting a computer to write a coherent paragraph was hard. Now LLMs write code, pass bar exams, summarize documents, and hold conversations. Understanding how they work — and where they break — is the most valuable AI skill you can have right now.

---

## Section map

| # | Topic | What you will learn |
|---|-------|---------------------|
| 01 | LLM Fundamentals | What an LLM is, scale, emergent abilities, famous models |
| 02 | How LLMs Generate Text | Token-by-token prediction, temperature, sampling |
| 03 | Pretraining | Self-supervised learning, data, compute, what the model absorbs |
| 04 | Fine-Tuning | Specializing a model, LoRA, when to fine-tune vs prompt |
| 05 | Instruction Tuning | Why base models aren't chatbots, InstructGPT, FLAN |
| 06 | RLHF | Reinforcement Learning from Human Feedback, reward models, PPO |
| 07 | Context Windows and Tokens | What a token is, context limits, KV cache |
| 08 | Hallucination and Alignment | Why LLMs make things up, how to reduce it, Constitutional AI |
| 09 | Using LLM APIs | API calls, cost management, streaming, structured output |

---

## Recommended reading order

If you are brand new: go 01 → 02 → 07 → 08 → 09. That gives you the practical foundation.

If you want the full picture: go 01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09.

---

## Prerequisites

Before diving in, make sure you have covered:
- **06_Transformers** — LLMs are built on transformers. Understanding attention makes everything here click.
- **05_NLP_Foundations** — Helps with tokenization and vocabulary concepts.

---

## What you will be able to do after this section

- Explain what an LLM is and how it generates text, to anyone
- Understand the difference between pretraining, fine-tuning, and instruction tuning
- Know when to fine-tune vs when to just prompt engineer
- Understand why LLMs hallucinate and how to mitigate it
- Call LLM APIs, handle errors, stream responses, and manage costs
- Speak confidently in LLM interviews at beginner, intermediate, and advanced level

---

## Key files in each topic

Every topic folder contains:
- **Theory.md** — The concept explained simply, with diagrams
- **Cheatsheet.md** — Quick reference card
- **Interview_QA.md** — 9 interview questions with full answers

Some topics also include:
- **Timeline.md** — History of LLMs
- **Architecture_Deep_Dive.md** — How it works under the hood
- **Code_Example.md / Code_Cookbook.md** — Working code you can run
- **When_to_Use.md / Mitigation_Strategies.md / Cost_Guide.md** — Practical decision guides

---

## How long will this take?

| Goal | Time |
|------|------|
| Read Theory.md for all 9 topics | ~3–4 hours |
| Read everything + do all hands-on tasks | ~2–3 days |
| Deep study including code and architecture dives | ~1 week |

---

➡️ Start here: [01_LLM_Fundamentals/Theory.md](01_LLM_Fundamentals/Theory.md)

---

## 📂 Navigation

**In this section:**
| Folder | |
|---|---|
| [📁 01_LLM_Fundamentals](./01_LLM_Fundamentals/Theory.md) | What an LLM is, scale, emergent abilities, famous models |
| [📁 02_How_LLMs_Generate_Text](./02_How_LLMs_Generate_Text/Theory.md) | Token-by-token prediction, temperature, sampling |
| [📁 03_Pretraining](./03_Pretraining/Theory.md) | Self-supervised learning, data, compute, what the model absorbs |
| [📁 04_Fine_Tuning](./04_Fine_Tuning/Theory.md) | Specializing a model, LoRA, when to fine-tune vs prompt |
| [📁 05_Instruction_Tuning](./05_Instruction_Tuning/Theory.md) | Why base models aren't chatbots, InstructGPT, FLAN |
| [📁 06_RLHF](./06_RLHF/Theory.md) | Reinforcement Learning from Human Feedback, reward models, PPO |
| [📁 07_Context_Windows_and_Tokens](./07_Context_Windows_and_Tokens/Theory.md) | What a token is, context limits, KV cache |
| [📁 08_Hallucination_and_Alignment](./08_Hallucination_and_Alignment/Theory.md) | Why LLMs make things up, how to reduce it, Constitutional AI |
| [📁 09_Using_LLM_APIs](./09_Using_LLM_APIs/Theory.md) | API calls, cost management, streaming, structured output |

⬅️ **Prev:** [06 Transformers](../06_Transformers/) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [08 LLM Applications](../08_LLM_Applications/)
