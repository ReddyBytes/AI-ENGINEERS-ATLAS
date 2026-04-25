# Project 6 — Recap

## What You Built

A command-line semantic search engine over a corpus of plain-text documents. The system embeds all documents once using an embeddings API, persists the vectors to a JSON cache, and at query time embeds the user's query and computes cosine similarity against every document vector in a single vectorized numpy operation. Results are ranked by similarity score and displayed with excerpts.

---

## Concepts Applied

| Concept | Where it appeared |
|---|---|
| Embeddings | `get_embedding()` — converts text to a 1536-dimensional float vector via the API |
| Cosine similarity | `cosine_similarity_batch()` — measures the angle between query vector and each document vector |
| Vectorized math | `corpus_matrix @ query_vector` — all N dot products in one BLAS call, no Python loop |
| Nearest neighbor search | `np.argsort(similarities)[::-1][:top_k]` — top-k indices by descending score |
| Embedding cache | JSON file on disk — avoid re-paying API costs on every run |
| Document loading | Sorted `Path.glob("*.txt")` — deterministic order so cache rows match document list |
| Consistent model use | Same `EMBEDDING_MODEL` for both documents and queries — mixing models breaks search silently |
| Vector space model | Documents about similar topics cluster together; queries land near semantically related documents |
| `dtype=np.float32` | Halves memory usage compared to float64 with no meaningful precision loss for similarity |
| Rate limiting | `time.sleep(0.05)` between API calls — prevents hitting rate limits during corpus indexing |

---

## Extension Ideas

1. **Batch embeddings**: Replace the per-document API loop with a single batched request using `input=[list of all contents]`. Measure the time difference on a 50-document corpus.

2. **LLM re-ranking**: After retrieving the top-10 results by cosine similarity, send the query and top-10 excerpts to Claude and ask it to re-rank them by actual relevance. Compare the LLM-ranked order to the cosine-similarity order. This is a core technique in production RAG pipelines.

3. **ChromaDB upgrade**: Replace the numpy matrix and JSON cache with ChromaDB (a local vector database). Observe how persistence, filtering, and metadata queries work differently at scale.

---

## Job Mapping

| Role | How this project maps |
|---|---|
| AI Application Developer | Every RAG system starts here — embeddings, vector search, and nearest-neighbor retrieval are the foundation |
| ML Engineer | Vectorized numpy operations, embedding dimensionality, and cosine similarity appear in model serving pipelines |
| Data Engineer | Building and caching embedding indexes is a production data pipeline task |
| Search Engineer | Semantic search vs keyword search, embedding models, and re-ranking are the core of modern search infrastructure |
| Backend Engineer | The indexing/query split (write once, read many) is a fundamental architecture pattern in information retrieval |

---

## 📂 Navigation

| File | |
|---|---|
| [01_MISSION.md](./01_MISSION.md) | Context and objectives |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design and diagrams |
| [03_GUIDE.md](./03_GUIDE.md) | Step-by-step build guide |
| [src/starter.py](./src/starter.py) | Starter code with TODOs |
| **04_RECAP.md** | You are here |

**Project Series:** Project 1 of 5 — Intermediate Projects
⬅️ No previous project
➡️ **Next:** [02 — Personal Knowledge Base RAG](../07_Personal_Knowledge_Base_RAG/01_MISSION.md)
