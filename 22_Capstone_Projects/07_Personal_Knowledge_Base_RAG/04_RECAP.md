# Project 07 — Personal Knowledge Base RAG: Recap

## What You Built

A full **Retrieval-Augmented Generation (RAG)** pipeline over a local document collection. The system ingests PDF and plain-text files, splits each document into overlapping character chunks, embeds them using `text-embedding-3-small`, and stores them in ChromaDB with metadata. When a user asks a question, the system embeds the query, finds the top-5 most similar chunks via cosine similarity, assembles them into a numbered source block, and sends them to Claude. Claude answers using only the provided context and cites each source as `[SOURCE N]`.

The pipeline runs in two modes: `--ingest` (offline indexing) and interactive Q&A.

---

## Concepts Applied

| Concept | Where it appeared |
|---|---|
| RAG pipeline | Two-phase architecture: offline ingestion + online query |
| Document ingestion | `pdfplumber` for PDFs, Python file I/O for text; metadata attached at load time |
| Chunking with overlap | Sliding window at character level; overlap prevents sentences splitting across boundaries |
| Embeddings | `text-embedding-3-small` via OpenAI API; 1536-d vectors per chunk |
| Vector store | ChromaDB `PersistentClient` with cosine distance space |
| Deduplication | `is_file_indexed()` guard prevents re-indexing on repeated `--ingest` runs |
| Retrieval | `collection.query()` returns top-k chunks with distances; converted to similarity scores |
| Context assembly | Numbered `[SOURCE N]` blocks; trimmed with `tiktoken` if over token budget |
| Grounded generation | System prompt instructs Claude to answer ONLY from provided sources |
| Citations | Metadata (source_file, page, chunk_index, char offsets) stored with every chunk |
| RAG evaluation | Faithfulness check: does Claude's answer match what the chunks actually say? |

---

## Extension Ideas

1. **Sentence-based chunking**: Split on sentence boundaries (`.`, `!`, `?`, `\n\n`) instead of fixed character counts. Compare retrieval precision between character-chunked and sentence-chunked indexes for the same document set. When does sentence chunking win?

2. **Multi-query retrieval**: For complex questions, generate 3 rephrased versions of the query (ask Claude to rephrase), run retrieval for each, deduplicate the chunk IDs, and merge. This catches relevant chunks that a single query formulation misses.

3. **Re-ranking with Claude**: After getting top-10 chunks from ChromaDB, ask Claude to score each chunk's relevance to the question on a 1–5 scale. Re-order by Claude's scores before assembling context. Measure whether this improves answer quality over raw embedding similarity.

---

## Job Role Mapping

| Role | How this project is relevant |
|---|---|
| ML Engineer | RAG is the dominant production pattern for grounding LLMs; you now know the full stack |
| Backend Engineer | Document ingestion, chunking, and vector database management are engineering problems, not ML |
| AI Product Engineer | RAG Q&A over private documents is a top enterprise AI use case you can now build end-to-end |
| Data Engineer | Ingestion pipelines, metadata design, and deduplication logic are core data engineering skills |
| AI Researcher | Understanding chunking and retrieval quality is prerequisite to reading advanced RAG papers |

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [01_MISSION.md](./01_MISSION.md) | Context and goals |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design and diagrams |
| [03_GUIDE.md](./03_GUIDE.md) | Progressive build steps |
| [src/starter.py](./src/starter.py) | Runnable starter code |
| 04_RECAP.md | you are here |

⬅️ **Prev:** [06 — Semantic Search Engine](../06_Semantic_Search_Engine/01_MISSION.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [08 — Multi-Tool Research Agent](../08_Multi_Tool_Research_Agent/01_MISSION.md)
