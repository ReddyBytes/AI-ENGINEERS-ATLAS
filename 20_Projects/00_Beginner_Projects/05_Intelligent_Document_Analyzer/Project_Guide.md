# Project 5 — Intelligent Document Analyzer

## The Story: Why This Project Matters

You've built a chatbot. That's a general-purpose conversational interface. Now imagine you work at a law firm, a research lab, or a publishing company. You receive hundreds of documents every week — contracts, papers, reports. Your job is to read them, extract the key information, answer questions about them, and quiz your team to make sure they understood the content.

That job is tedious, error-prone, and time-consuming when done manually. It's almost trivially automatable with an LLM — if you know how to engineer the prompts correctly.

This project is about **prompt chaining**: breaking a complex task into a pipeline of focused LLM calls, each with a specific, well-defined prompt. One call summarizes. Another call extracts structured data. A third answers questions. A fourth generates quiz questions. Each step is isolated, testable, and produces a specific output format.

This is real-world LLM application architecture. It's how every serious LLM product is built — not a single giant prompt, but a carefully engineered sequence of smaller, verifiable steps.

You'll also learn structured output — how to make the LLM return reliable, machine-readable JSON instead of freeform prose. And you'll learn about hallucination: why the model might make up facts about your document, and the pragmatic techniques for reducing it.

After this project, you'll have the full skill set to build production LLM applications.

---

## What You'll Build

A Python CLI application that accepts any text file (or piped text) and runs 4 analysis tasks using the Claude API:

1. **Summarize** — Generate a concise summary (3–5 sentences)
2. **Extract entities** — Return key entities as structured JSON: people, organizations, dates, key topics
3. **Q&A mode** — Answer user questions specifically about the document (with a "don't hallucinate" instruction)
4. **Quiz generator** — Generate 5 multiple-choice questions to test comprehension

---

## Learning Objectives

By completing this project, you will be able to:

- Design prompt chains: break a complex task into multiple focused LLM calls
- Write prompts that reliably return JSON and validate the output with pydantic
- Explain what a hallucination is and write prompts that reduce its occurrence
- Manage long documents by understanding context window limits
- Use `pydantic` to validate structured LLM outputs
- Build a multi-step LLM pipeline where each step's output feeds into the next

---

## Topics Covered

| Phase | Topic | Concept Applied |
|---|---|---|
| Phase 7 | Prompt Engineering (Topic 26) | System prompt design, JSON extraction prompts |
| Phase 7 | Using LLM APIs (Topic 27) | Multiple API calls, response parsing |
| Phase 7 | Structured Outputs (Topic 28) | JSON schema in prompt, pydantic validation |
| Phase 7 | Embeddings (Topic 29) | Context: why document retrieval matters for long docs |
| Phase 6 | Hallucination & Alignment (Topic 25) | Grounding instructions, "only use what's in the document" |

---

## Prerequisites

- Completed Project 4 (or comfortable with the Anthropic API)
- Python 3.9+
- An Anthropic API key
- Libraries: `anthropic`, `pydantic`

---

## Difficulty

Medium-Hard — 4–6 hours. The prompt engineering and pydantic validation require careful attention. The architecture is more complex than previous projects.

---

## Tools & Libraries

| Tool | Purpose |
|---|---|
| `anthropic` SDK | All API calls to Claude |
| `pydantic` | Validate and parse structured JSON from the LLM |
| `json` | Parse LLM JSON output |
| `argparse` | CLI argument parsing |

---

## Expected Interaction

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

> 5

--- [1] SUMMARY ---
This paper presents a novel approach to retrieval-augmented generation (RAG)
that improves factual accuracy by 23% on standard benchmarks. The authors
propose a hybrid retrieval strategy combining dense and sparse retrieval,
evaluated on three open-domain QA datasets. Key findings suggest that
re-ranking retrieved passages before generation significantly reduces
hallucination rates...

--- [2] ENTITIES ---
{
  "people": ["Dr. Sarah Chen", "Prof. Marcus Williams"],
  "organizations": ["Stanford NLP Group", "DeepMind"],
  "dates": ["March 2024", "2023"],
  "key_topics": ["RAG", "dense retrieval", "hallucination", "open-domain QA"]
}

--- [3] Q&A ---
Your question: What datasets were used for evaluation?
Answer: According to the document, the authors evaluated their method on
three open-domain QA datasets: Natural Questions, TriviaQA, and WebQ.
[Source: Section 4.2 of the document]

--- [4] QUIZ ---
Q1: What is the primary contribution of this paper?
  A) A new language model architecture
  B) A hybrid retrieval strategy for RAG
  C) A new training procedure for dense retrievers
  D) A benchmark dataset for QA evaluation
Correct answer: B

...
```

---

## Key Learning: Concepts You'll Apply

- **Prompt chaining**: Each task is a separate, focused API call. The document is provided as context in every call.
- **Structured output**: Ask the model to return JSON in a specific schema. Use pydantic to validate it.
- **Grounding**: Include the instruction "Only use information from the document provided. Do not add external knowledge." to reduce hallucination.
- **Context window awareness**: For very long documents, you may need to truncate or chunk. This project handles truncation as a simple first approach.
- **Pydantic validation**: If the LLM returns malformed JSON, catch the `ValidationError` and retry with a more explicit prompt.

---

## Extension Challenges

1. Add document chunking: split very long documents into chunks, summarize each chunk, then summarize the summaries
2. Add a `--compare` flag that analyzes two documents and generates a comparison report
3. Validate quiz answers: ask the model to generate an answer key and then grade user responses
4. Add sentence-level citation: ask the model to quote the specific sentence from the document that supports each entity extraction

---

## 📂 Navigation

| File | |
|---|---|
| **Project_Guide.md** | You are here — overview and objectives |
| [Step_by_Step.md](./Step_by_Step.md) | Detailed build instructions |
| [Starter_Code.md](./Starter_Code.md) | Python starter code with TODOs |
| [Architecture_Blueprint.md](./Architecture_Blueprint.md) | System diagram |

**Project Series:** Project 5 of 5 — Beginner Projects
⬅️ **Previous:** [04 — LLM Chatbot with Memory](../04_LLM_Chatbot_with_Memory/Project_Guide.md)
➡️ **Next:** Intermediate Projects (coming soon)
