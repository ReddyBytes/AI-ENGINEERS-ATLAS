# Project 5 — Intelligent Document Analyzer

## The Story

You work at a law firm. Every week, 200 contracts arrive. Your job is to read each one, pull out the key parties and dates, summarize the obligations, answer your team's questions about specific clauses, and quiz the junior associates to make sure they understood the content.

That job takes 40 hours a week when done manually. It takes about 400 lines of Python when done with an LLM — if you know how to engineer the prompts correctly.

The core insight of this project is **prompt chaining**: rather than one massive prompt that tries to do everything, you build a pipeline of small, focused API calls. One call summarizes. A second extracts structured data. A third answers questions with strict grounding rules. A fourth generates a quiz. Each step is isolated, testable, and produces a verifiable output.

This is how every serious LLM application is actually built. Not a single giant prompt. A carefully engineered sequence of smaller, verifiable steps — each with its own output contract.

---

## What You Build

A Python CLI application that accepts any text file and runs 4 analysis tasks:

1. **Summarize** — Generate a concise 3 to 5 sentence summary
2. **Extract entities** — Return key entities as structured JSON: people, organizations, dates, key topics
3. **Q&A mode** — Answer user questions strictly about the document (with anti-hallucination instructions)
4. **Quiz generator** — Generate 5 multiple-choice questions to test comprehension

---

## Concepts Covered

| Phase | Topic | Concept Applied |
|---|---|---|
| Phase 7 | Prompt Engineering | System prompt design, JSON extraction prompts |
| Phase 7 | Using LLM APIs | Multiple API calls, response parsing |
| Phase 7 | Structured Outputs | JSON schema in prompt, pydantic validation |
| Phase 7 | Embeddings | Why document retrieval matters for long docs |
| Phase 6 | Hallucination and Alignment | Grounding instructions, "only use what's in the document" |

---

## Prerequisites

- Completed Project 4 (or comfortable with the Anthropic API)
- Python 3.9+
- An Anthropic API key
- Libraries: `anthropic`, `pydantic`

---

## What Success Looks Like

```
=================================================
  Intelligent Document Analyzer
  Powered by Claude claude-opus-4-6
=================================================

Document loaded: research_paper.txt (4,823 characters)

[1] Summarize
[2] Extract Entities
[3] Ask a Question
[4] Generate Quiz
[5] Run All
[q] Quit

> 2

--- ENTITIES ---
{
  "people": ["Dr. Sarah Chen", "Prof. Marcus Williams"],
  "organizations": ["Stanford NLP Group", "DeepMind"],
  "dates": ["March 2024", "2023"],
  "key_topics": ["RAG", "dense retrieval", "hallucination", "open-domain QA"]
}
```

---

## Learning Format

**Difficulty:** Medium-Hard — 4 to 6 hours

**Format:** The complexity is in prompt engineering, not code volume. Spend extra time writing and refining prompts — small wording changes can dramatically change the reliability of structured output. Every function is testable in isolation.

---

## Key Terms

- **Prompt chaining**: Each task is a separate, focused API call. The document is provided as context in every call.
- **Structured output**: Ask the model to return JSON in a specific schema; use pydantic to validate it.
- **Grounding**: The instruction "Only use information from the document provided. Do not add external knowledge." reduces hallucination.
- **Context window awareness**: For very long documents, you may need to truncate. This project handles truncation as a first approach.
- **Pydantic validation**: If the LLM returns malformed JSON, catch the `ValidationError` and retry with a more explicit prompt.

---

## 📂 Navigation

| File | |
|---|---|
| **01_MISSION.md** | You are here |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design and diagrams |
| [03_GUIDE.md](./03_GUIDE.md) | Step-by-step build guide |
| [src/starter.py](./src/starter.py) | Starter code with TODOs |
| [04_RECAP.md](./04_RECAP.md) | What you built and what comes next |

**Project Series:** Project 5 of 5 — Beginner Projects
⬅️ **Previous:** [04 — LLM Chatbot with Memory](../04_LLM_Chatbot_with_Memory/01_MISSION.md)
➡️ **Next:** Intermediate Projects (coming soon)
