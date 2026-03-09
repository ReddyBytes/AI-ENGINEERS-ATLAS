# Embedding and Indexing — Cheatsheet

**One-liner:** Embedding converts each text chunk to a meaning-vector. Indexing stores those vectors in a database with an HNSW index for millisecond-speed nearest-neighbor search.

---

## Key Terms

| Term | Definition |
|------|-----------|
| **Embedding** | Converting a text chunk to a fixed-length vector of floats |
| **Vector** | The numeric representation of text meaning (e.g., 1536 floats) |
| **Indexing** | Building a data structure (HNSW) over vectors for fast search |
| **HNSW** | Hierarchical Navigable Small World — the standard ANN index |
| **Batch embedding** | Embedding many chunks at once (much faster than one at a time) |
| **Upsert** | Insert if not exists, update if exists — idempotent |
| **Deterministic ID** | Chunk ID based on content hash — prevents duplicate inserts |
| **Collection** | A named group of vectors in ChromaDB (like a table) |
| **Embedding drift** | Vectors becoming mismatched when you change embedding models |

---

## Embedding Pipeline

```
text chunks
  → batch embed (all at once)
  → store in vector DB (with metadata + IDs)
  → vector DB builds HNSW index
  → ready for millisecond ANN search
```

---

## Batch Embedding Code Patterns

```python
# sentence-transformers (local, free)
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(chunks, batch_size=64, show_progress_bar=True)

# OpenAI API (cloud, paid)
from openai import OpenAI
client = OpenAI()
response = client.embeddings.create(model="text-embedding-3-small", input=chunks)
embeddings = [item.embedding for item in response.data]
```

---

## When to Use / Not Use

| Use when... | Don't use when... |
|-------------|------------------|
| Building a RAG retrieval pipeline | Small corpus fits in LLM context |
| Need semantic search at scale | Real-time text with no latency budget for embedding |
| Documents indexed once, queried many times | Frequent model changes (causes embedding drift) |

---

## Golden Rules

1. **Always use the same model for indexing and querying** — mixing models produces garbage results.
2. **Batch embed** — never embed one chunk at a time. Group into batches of 64–256.
3. **Use deterministic chunk IDs** — content hash prevents duplicate entries on re-runs.
4. **Persist your index** — use `PersistentClient` in ChromaDB; rebuilding from scratch is expensive.
5. **Store metadata with every vector** — source, page, section at minimum.
6. **When you change embedding models, re-index everything** — partial re-indexing is wrong.
7. **Track your embedding model version** — document it alongside the index.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [03 Chunking Strategies](../03_Chunking_Strategies/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 Retrieval Pipeline](../05_Retrieval_Pipeline/Theory.md)
