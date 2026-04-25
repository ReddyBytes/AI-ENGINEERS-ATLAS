# Project 07 — Personal Knowledge Base RAG

## The Story

A legal researcher at a 200-person law firm spent her days answering the same question in different forms: "Has our firm handled a case like this before?" The answer was always the same: "Check the case archive." The archive was 8,000 PDF files — briefs, contracts, research memos, court rulings — accumulated over 15 years and stored on a shared network drive. Full-text search existed, but it required knowing the right keywords. Most junior associates did not know the right keywords. Most senior partners did not have time to look.

She built a RAG system over a weekend. She ingested every PDF, chunked each document into 400-word segments, embedded them with a text embedding model, and stored them in a vector database. When a junior associate typed "precedents for breach of fiduciary duty in private equity transactions", the system retrieved 12 relevant case chunks — from 9 different files spanning 6 years — assembled them into a context window, and sent them to an LLM with the question. The answer included citations: which file, which page, which passage.

That is what RAG is. Not magic. A specific, learnable pipeline. You are about to build it.

---

## What You Will Build

A full **Retrieval-Augmented Generation (RAG)** system that:

1. Ingests a folder of PDF and plain-text files
2. Chunks each document into overlapping text segments
3. Embeds each chunk and stores them in ChromaDB (a local vector database)
4. Retrieves the most relevant chunks when a question is asked
5. Assembles context and sends it to Claude with the user's question
6. Returns an answer with citations — which file and chunk each fact came from

The final product is a command-line Q&A system over your own document collection.

### Expected Output

```
RAG Knowledge Base loaded: 23 documents, 847 chunks indexed.

Ask a question (or 'quit'): What were the main findings about attention mechanisms?

Thinking...

Answer:
The attention mechanism allows a model to dynamically weight the importance of
different input tokens when producing each output token. Unlike RNNs, which
compress the entire input into a fixed-size hidden state, attention lets the
model "look back" at any part of the input at any step.

Sources:
  [1] attention_mechanism.txt — Chunk 3 (chars 800–1200)
  [2] transformer_architecture.pdf — Page 2, Chunk 7 (chars 2100–2500)
  [3] llm_internals_notes.txt — Chunk 1 (chars 0–400)
```

---

## Real-World Motivation

RAG is the dominant architecture for adding private, up-to-date knowledge to LLMs without retraining. It appears in:
- Enterprise search and document Q&A (legal, medical, financial)
- Customer support systems backed by knowledge bases
- Developer tools with codebase-aware assistants
- Research tools that query private paper collections

---

## Concepts Covered

| Concept | What You Learn |
|---|---|
| RAG pipeline | Full flow from document to grounded answer |
| Document ingestion | PDF and text parsing with metadata extraction |
| Chunking | Fixed-size overlapping chunks; when chunk size matters |
| Embeddings | Converting text to vectors; batched embedding API calls |
| ChromaDB | Persistent local vector store with cosine distance |
| Retrieval | Top-k nearest-neighbor search over embedded chunks |
| Context assembly | Formatting retrieved chunks as a numbered source block |
| Citations | Using stored metadata to tell users where facts came from |
| RAG evaluation | Faithfulness, relevance, and failure mode testing |

---

## Theory Files

| Section | Topic | File |
|---|---|---|
| 09_RAG_Systems | RAG Fundamentals | `09_RAG_Systems/01_RAG_Fundamentals/Theory.md` |
| 09_RAG_Systems | Document Ingestion | `09_RAG_Systems/02_Document_Ingestion/Theory.md` |
| 09_RAG_Systems | Chunking Strategies | `09_RAG_Systems/03_Chunking_Strategies/Theory.md` |
| 09_RAG_Systems | Embedding and Indexing | `09_RAG_Systems/04_Embedding_and_Indexing/Theory.md` |
| 09_RAG_Systems | Retrieval Pipeline | `09_RAG_Systems/05_Retrieval_Pipeline/Theory.md` |
| 09_RAG_Systems | Context Assembly | `09_RAG_Systems/06_Context_Assembly/Theory.md` |
| 09_RAG_Systems | RAG Evaluation | `09_RAG_Systems/08_RAG_Evaluation/Theory.md` |

---

## Prerequisites

- Completed a semantic search project or understand cosine similarity and embedding vectors
- Anthropic API key (Claude for generation)
- OpenAI API key (for `text-embedding-3-small` embeddings)
- Python 3.10+
- Comfortable with basic Python file I/O and list manipulation

---

## Learning Format

**Tier:** Intermediate (3 / 5 stars)

This project has more moving parts than a basic LLM call — a real vector database, PDF parsing, chunking logic, and multi-source context assembly. Each piece is manageable; the challenge is connecting them cleanly and handling edge cases in real documents (scanned PDFs, encoding errors, empty pages). Plan approximately 4 hours of focused build time.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| 01_MISSION.md | you are here |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design and diagrams |
| [03_GUIDE.md](./03_GUIDE.md) | Progressive build steps |
| [src/starter.py](./src/starter.py) | Runnable starter code |
| [04_RECAP.md](./04_RECAP.md) | What you built + next steps |

⬅️ **Prev:** [06 — Semantic Search Engine](../06_Semantic_Search_Engine/01_MISSION.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [08 — Multi-Tool Research Agent](../08_Multi_Tool_Research_Agent/01_MISSION.md)
