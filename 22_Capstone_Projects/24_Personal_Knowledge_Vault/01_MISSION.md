# Project 24 — Personal Knowledge Vault

## The Problem Worth Solving

Picture a research scientist who reads 40 papers a year. She saves PDFs to a folder, writes markdown notes after conferences, and drops plain text summaries into the same directory. Six months later she cannot remember which paper explained that optimization trick. She searches filenames. Nothing. She opens Finder and scrolls. Nothing. She opens each PDF manually until she finds it — twenty minutes wasted.

This happens because traditional file systems are organized by name and date, not by meaning. The only person who can search the folder is someone who already remembers what is in it.

A **Personal Knowledge Vault** solves this at the architecture level. Every document you drop into a folder is automatically read, split into semantically meaningful chunks, embedded into a vector space, and stored in a local database. When you ask a question in plain English, the system finds the most relevant passages across your entire library and gives you a grounded answer — with source attribution. It is like having a research assistant who has read everything you have ever saved.

---

## What You Build

A command-line application with two operating modes:

**Watch mode** — run `python vault.py watch` and the agent monitors `~/vault/` continuously. When you drop in a PDF, markdown file, or text file, it is automatically ingested within seconds.

**Ask mode** — run `python vault.py ask "What did I read about attention mechanisms?"` and the agent returns a cited answer drawing from every relevant document in your vault.

The system supports three document types:

| Format | Parser |
|--------|--------|
| PDF | pdfplumber — extracts text per page, handles multi-column layouts |
| Markdown | Python-markdown — strips HTML, preserves section structure |
| Plain text | Direct read, whitespace normalization |

After parsing, every document goes through the same pipeline: chunk into 500-token windows with 50-token overlap, embed each chunk, store the embedding plus metadata in ChromaDB.

**Expected CLI output:**

```
$ python vault.py ask "What is the difference between RAG and fine-tuning?"

Searching vault (47 documents, 1,203 chunks)...

Answer:
RAG retrieves relevant external knowledge at inference time and injects it into the
context window, making the model's knowledge updatable without retraining. Fine-tuning
bakes knowledge into model weights permanently, which is faster at inference but
requires retraining when knowledge changes (transformer_notes.md, chunk 3).

Sources:
  [1] transformer_notes.md — chunk 3 (added 2025-01-14)
  [2] rag_paper_summary.pdf — chunk 7 (added 2025-01-20)
  [3] llm_overview.txt — chunk 2 (added 2025-01-10)
```

---

## Concepts Applied

| Section | Topic | Applied As |
|---------|-------|-----------|
| 09 RAG Systems | Document ingestion | Multi-format parsing pipeline |
| 09 RAG Systems | Chunking strategies | Recursive text splitter, 500/50 overlap |
| 09 RAG Systems | Embedding and indexing | sentence-transformers → ChromaDB |
| 09 RAG Systems | Retrieval pipeline | Top-k cosine similarity retrieval |
| 09 RAG Systems | Context assembly | Retrieved chunks → Claude prompt |
| 08 LLM Applications | Embeddings | Dense vector representations |
| 10 AI Agents | Tool use | File watcher triggers ingestion pipeline |

---

## Difficulty

**Intermediate-Advanced.** You need to integrate five independent libraries (watchdog, pdfplumber, sentence-transformers, chromadb, anthropic), design a persistent data layer, and build a CLI with two operational modes. None of the individual pieces are hard in isolation — the challenge is making them work together correctly and handling edge cases (duplicate ingestion, file encoding errors, empty pages).

---

## Tech Stack

```
anthropic          — Claude claude-sonnet-4-6, answer generation
watchdog           — filesystem events, new/modified file detection
chromadb           — local vector database, no server required
pdfplumber         — PDF text extraction
sentence-transformers — local embedding model (all-MiniLM-L6-v2)
click              — CLI interface, command routing
python-dotenv      — .env loading for ANTHROPIC_API_KEY
```

---

## Prerequisites

- Python 3.10+
- Anthropic API key in `.env` file
- `pip install anthropic watchdog chromadb pdfplumber sentence-transformers click python-dotenv`

---

## 📂 Navigation

| File | |
|------|---|
| **01_MISSION.md** | You are here — project brief |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design and data flow |
| [03_GUIDE.md](./03_GUIDE.md) | 10-step build guide |
| [src/starter.py](./src/starter.py) | Starter scaffold |
| [src/solution.py](./src/solution.py) | Complete reference solution |
| [04_RECAP.md](./04_RECAP.md) | What you learned, career framing |

**Section:** [22 Capstone Projects](../) &nbsp;&nbsp; **Prev:** [23 — Codebase Review Agent](../23_Codebase_Review_Agent/01_MISSION.md) &nbsp;&nbsp; **Next:** [25 — Multi-Agent Portfolio Manager](../25_Multi_Agent_Portfolio_Manager/01_MISSION.md)
