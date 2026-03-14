# Project 2 — Personal Knowledge Base RAG

## Why This Project Matters

A legal researcher at a 200-person law firm spent her days answering the same question in different forms: "Has our firm handled a case like this before?" The answer was always the same: "Check the case archive." The archive was 8,000 PDF files — briefs, contracts, research memos, court rulings — accumulated over 15 years and stored on a shared network drive. Full-text search existed, but it required knowing the right keywords. Most junior associates did not know the right keywords. Most senior partners did not have time to look.

She built a RAG system over a weekend. She ingested every PDF, chunked each document into 400-word segments, embedded them with a text embedding model, and stored them in a vector database. When a junior associate typed "precedents for breach of fiduciary duty in private equity transactions", the system retrieved 12 relevant case chunks — from 9 different files spanning 6 years — assembled them into a context window, and sent them to an LLM with the question. The answer included citations: which file, which page, which passage.

That is what RAG is. Not magic. A specific, learnable pipeline. You are about to build it.

---

## What You Will Build

A full **Retrieval-Augmented Generation (RAG)** system that:

1. **Ingests** a folder of PDF and plain-text files
2. **Chunks** each document into overlapping text segments
3. **Embeds** each chunk and **stores** them in ChromaDB (a local vector database)
4. **Retrieves** the most relevant chunks when a question is asked
5. **Assembles context** and sends it to Claude with the user's question
6. **Returns an answer with citations** — which file and chunk each fact came from

The final product is a command-line Q&A system over your own document collection.

---

## Learning Objectives

By completing this project you will be able to:

- Explain the full RAG pipeline from document to answer
- Implement three chunking strategies and choose between them
- Use ChromaDB to store, index, and query embeddings
- Assemble a context window that fits within the LLM's limit
- Show source citations in LLM responses
- Evaluate whether a RAG response is faithful to retrieved context

---

## Topics Covered

| Phase | Topic | Theory File |
|---|---|---|
| Phase 3 | RAG Fundamentals | `09_RAG_Systems/01_RAG_Fundamentals/Theory.md` |
| Phase 3 | Document Ingestion | `09_RAG_Systems/02_Document_Ingestion/Theory.md` |
| Phase 3 | Chunking Strategies | `09_RAG_Systems/03_Chunking_Strategies/Theory.md` |
| Phase 3 | Embedding & Indexing | `09_RAG_Systems/04_Embedding_and_Indexing/Theory.md` |
| Phase 3 | Retrieval Pipeline | `09_RAG_Systems/05_Retrieval_Pipeline/Theory.md` |
| Phase 3 | Context Assembly | `09_RAG_Systems/06_Context_Assembly/Theory.md` |
| Phase 3 | RAG Evaluation | `09_RAG_Systems/08_RAG_Evaluation/Theory.md` |

---

## Prerequisites

- Completed Project 1 (Semantic Search Engine) or equivalent
- Understand cosine similarity and embedding vectors
- Anthropic API key (Claude for generation + embeddings)
- Python 3.10+

---

## Difficulty

Medium (3 / 5 stars)

This project has more moving parts than Project 1 — a real vector database, PDF parsing, chunking logic, and multi-source context assembly. Each piece is manageable; the challenge is connecting them cleanly and handling edge cases in real documents (scanned PDFs, encoding errors, empty pages).

---

## Expected Output

```
RAG Knowledge Base loaded: 23 documents, 847 chunks indexed.

Ask a question (or 'quit'): What were the main findings about attention mechanisms?

Thinking...

Answer:
The attention mechanism allows a model to dynamically weight the importance of
different input tokens when producing each output token. Unlike RNNs, which
compress the entire input into a fixed-size hidden state, attention lets the
model "look back" at any part of the input at any step.

The key operation is computing a weighted sum of value vectors, where the weights
are determined by the compatibility between a query vector and a set of key vectors
(Vaswani et al., 2017).

Sources:
  [1] attention_mechanism.txt — Chunk 3 (chars 800–1200)
  [2] transformer_architecture.pdf — Page 2, Chunk 7 (chars 2100–2500)
  [3] llm_internals_notes.txt — Chunk 1 (chars 0–400)
```

---

## Key Concepts You Will Learn

**RAG vs Fine-tuning**: RAG injects knowledge at inference time through retrieved context. Fine-tuning bakes knowledge into model weights at training time. RAG is better when knowledge changes frequently or must be auditable.

**Chunking**: Documents must be split into segments small enough to fit in a context window alongside other chunks and the question. The chunk size and overlap are hyperparameters — too small loses context, too large wastes space.

**Vector Database**: ChromaDB stores (embedding, text, metadata) triples and provides fast approximate nearest-neighbor search. Unlike the numpy approach in Project 1, it persists to disk, supports metadata filtering, and scales to millions of chunks.

**Context Assembly**: After retrieval, chunks must be arranged into a prompt. You must respect the context window limit, decide how to order chunks, and format source citations so the LLM can reference them.

**Citations**: Metadata stored alongside each chunk (filename, page number, chunk index) enables the system to tell users exactly where each fact came from.

---

## Project Structure

```
02_Personal_Knowledge_Base_RAG/
├── Project_Guide.md
├── Step_by_Step.md
├── Starter_Code.md
├── Architecture_Blueprint.md
├── documents/               ← put your PDFs and .txt files here
│   ├── paper_01.pdf
│   ├── notes_02.txt
│   └── ...
├── chroma_db/               ← auto-created by ChromaDB
└── rag_pipeline.py          ← your implementation
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| Project_Guide.md | ← you are here |
| [Step_by_Step.md](./Step_by_Step.md) | Build instructions |
| [Starter_Code.md](./Starter_Code.md) | Code with TODOs |
| [Architecture_Blueprint.md](./Architecture_Blueprint.md) | System diagram |

⬅️ **Prev:** [01 — Semantic Search Engine](../01_Semantic_Search_Engine/Project_Guide.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 — Multi-Tool Research Agent](../03_Multi_Tool_Research_Agent/Project_Guide.md)
