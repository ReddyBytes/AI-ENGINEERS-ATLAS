# Project 19 — Research Paper to Podcast Agent: Recap

## What You Built

An agent that reads an academic paper — from arXiv or a local file — and produces three publishable outputs: an audio episode, a transcript, and a key points summary.

You built a real content pipeline. The same architecture is used by tools like NotebookLM, Perplexity's podcast mode, and enterprise document summarization systems.

---

## Core Concepts Applied

| Concept | Where it appeared |
|---|---|
| PDF text extraction | pdfplumber parsing with page iteration |
| HTTP file download | requests.get() with User-Agent headers |
| Structured prompt design | Two separate Claude calls with focused personas |
| LLM for content transformation | Academic text → conversational podcast script |
| Text-to-speech conversion | gTTS audio generation |
| Multi-file output pipeline | Three outputs from a single pipeline run |
| CLI argument handling | argparse with mutually exclusive input group |
| Content truncation strategy | 8000-char limit to control costs and focus |

---

## Patterns Worth Naming

**The transform pipeline pattern.** Every stage takes one format and produces another:

```
PDF bytes → structured dict → truncated string → podcast script → .mp3
```

This is composable. Each function has one responsibility. You can test each stage independently.

**Two-call prompt separation.** The podcast script and key points are different cognitive tasks. A single prompt asking for "a script and five bullet points" produces mixed results. Two focused calls give you cleaner, higher-quality outputs from the same input.

**Content truncation as a feature.** Truncating paper content to 8000 characters is not a limitation — it is a design choice. A podcast host does not read the entire paper either. They read the abstract, the intro, and the conclusion. Your truncation simulates that editorial judgment.

---

## 3 Extensions to Try

**Extension 1 — Batch arXiv topic feed.**
Fetch the latest 10 papers from an arXiv RSS feed on a topic (e.g., `https://rss.arxiv.org/rss/cs.AI`). Parse the feed with feedparser, extract paper URLs, and run the agent on each. This turns your single-paper agent into a daily podcast series generator.

**Extension 2 — Two-host dialogue format.**
Modify the podcast script system prompt to request a dialogue between two hosts: one who explains the paper and one who asks clarifying questions. The resulting script is more engaging and forces the explanations to be conversational. This is exactly how NotebookLM's podcast mode works.

**Extension 3 — Speaker voice selection.**
Replace gTTS with OpenAI's TTS API, which offers six voice options (`alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`). Add a `--voice` CLI argument. This teaches you about different TTS provider APIs and their tradeoffs (cost, quality, latency).

---

## Job Mapping

| What you built | Job title that cares |
|---|---|
| PDF parsing pipeline | Data Engineer, ML Engineer |
| LLM-powered content transformation | AI Engineer, Content AI Engineer |
| TTS integration | Multimodal AI Engineer, Voice AI Engineer |
| Multi-output pipeline from single input | Data Engineer, Backend Engineer |
| Structured prompt design for transformation | AI Engineer, Prompt Engineer |
| CLI tool design | Platform Engineer, Dev Tools Engineer |

This project stands out in a portfolio because it demonstrates a complete, production-shaped pipeline. It is not a chatbot or a RAG demo. It takes a real artifact (a PDF), transforms it through multiple stages, and produces three genuinely useful outputs. That is the kind of project that prompts a "how did you build this?" question in an interview.

---

## 📂 Navigation

| File | |
|---|---|
| [01_MISSION.md](./01_MISSION.md) | Context and goals |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System diagram |
| [03_GUIDE.md](./03_GUIDE.md) | Step-by-step build guide |
| **04_RECAP.md** | ← you are here |
| [src/starter.py](./src/starter.py) | Skeleton with TODO markers |
| [src/solution.py](./src/solution.py) | Complete working solution |
