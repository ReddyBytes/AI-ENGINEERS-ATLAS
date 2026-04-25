# Project 24 — Recap

## What You Built

A local RAG agent that autonomously monitors a folder, ingests documents of three formats, stores them in a vector database, and answers natural language questions with grounded, cited answers. Every component in this system is a production-grade pattern used by real AI products.

---

## Core Patterns You Now Own

### The RAG Pipeline

You implemented the canonical retrieval-augmented generation loop:

```
Document → Parse → Chunk → Embed → Store → [at query time] Retrieve → Augment → Generate
```

This is the same pipeline that powers enterprise knowledge bases, customer support bots, legal document search, and developer documentation tools. The specific libraries change; the pattern does not.

### Event-Driven Ingestion

The watchdog file watcher is an example of event-driven architecture. Instead of polling (check the folder every N seconds), you registered a callback that fires only when something changes. This is the pattern behind every file sync system, every CI trigger, and every streaming data pipeline.

### Deterministic IDs for Idempotent Upserts

Using `sha256(filename + chunk_index)` as the ChromaDB document ID means you can re-ingest any file any number of times without creating duplicates. The upsert operation is **idempotent** — running it twice produces the same result as running it once. This is a critical property for any production data pipeline.

### Separation of Ingestion and Retrieval

The ingestion pipeline runs asynchronously (triggered by the file watcher). The query agent runs synchronously when the user asks a question. They share only the ChromaDB collection. This separation means you can add a web scraper as another ingestion source without touching the query code.

---

## What Could Break in Production

| Issue | Why | Fix |
|-------|-----|-----|
| Large PDFs (300+ pages) | Ingestion takes 30+ seconds | Async queue (Celery, Redis) |
| OCR-only PDFs | pdfplumber extracts no text | Add pytesseract OCR fallback |
| Near-duplicate chunks | Same paragraph indexed twice | Deduplication before upsert |
| Model drift | Embeddings from v1 model differ from v2 | Re-embed entire collection on model upgrade |
| Context window overflow | 5 large chunks exceed Claude's prompt budget | Track token count, cap context |

---

## Career Framing

### AI Engineer

You can describe this project as: "Built a local RAG system that auto-ingests multi-format documents (PDF, markdown, text) into a ChromaDB vector store using a watchdog file monitor, and answers natural language queries with Claude-generated responses grounded in retrieved chunks." This is a complete RAG implementation that most job descriptions specifically ask for.

### ML Engineer / Data Engineer

The ingestion pipeline — parse, chunk, embed, store — is the same pattern used to build training data pipelines, feature stores, and embedding databases. Understanding how vectors are generated and stored is prerequisite knowledge for any embedding-heavy ML system.

### Platform Engineer / Full-Stack AI

The CLI architecture (click + two modes + shared state via ChromaDB) is a clean pattern for any agent that has both a background daemon and an interactive query interface. The same structure scales to a FastAPI backend with a React frontend.

---

## What to Build Next

- Replace the CLI with a FastAPI server and a simple HTML frontend
- Add a `--reindex` command that re-embeds the entire vault after changing models
- Swap ChromaDB for a hosted vector store (Pinecone, Weaviate) to support multi-user access
- Add multi-hop retrieval: retrieve top-5, ask Claude to generate a better query, retrieve again
- Project 25: Multi-Agent Portfolio Manager — apply orchestration patterns to financial analysis

---

## 📂 Navigation

| File | |
|------|---|
| [01_MISSION.md](./01_MISSION.md) | Project brief |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design |
| [03_GUIDE.md](./03_GUIDE.md) | 10-step build guide |
| [src/starter.py](./src/starter.py) | Starter scaffold |
| [src/solution.py](./src/solution.py) | Complete reference solution |
| **04_RECAP.md** | You are here |

**Next project:** [25 — Multi-Agent Portfolio Manager](../25_Multi_Agent_Portfolio_Manager/01_MISSION.md)
