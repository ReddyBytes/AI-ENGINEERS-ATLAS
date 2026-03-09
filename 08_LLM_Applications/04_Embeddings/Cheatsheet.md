# Embeddings — Cheatsheet

**One-liner:** An embedding is a list of numbers that encodes the meaning of text — similar texts produce similar vectors, enabling you to measure semantic similarity and do meaning-based search.

---

## Key Terms

| Term | Definition |
|------|-----------|
| **Embedding** | A vector (list of floats) representing the semantic meaning of text |
| **Vector** | A fixed-length array of numbers — the "address" in meaning-space |
| **Dimension** | The length of the vector (e.g. 1536 dimensions = 1536 numbers) |
| **Cosine similarity** | Score from -1 to 1 measuring how similar two vectors are (1 = identical) |
| **Dense embedding** | Compact vector with all values filled, encodes meaning |
| **Sparse embedding** | Huge vector mostly filled with zeros, based on word presence |
| **Embedding model** | The model that converts text → vector (e.g. text-embedding-3-small) |
| **Semantic similarity** | Similarity based on meaning, not exact word matching |
| **Nearest neighbor search** | Finding the vectors most similar to a query vector |

---

## Popular Models Quick Reference

| Model | Provider | Dims | Best For |
|-------|----------|------|---------|
| text-embedding-3-small | OpenAI | 1536 | Production RAG, cost-efficient |
| text-embedding-3-large | OpenAI | 3072 | High accuracy needs |
| all-MiniLM-L6-v2 | HuggingFace | 384 | Local, fast, free |
| all-mpnet-base-v2 | HuggingFace | 768 | Better quality, still free |
| embed-english-v3.0 | Cohere | 1024 | Production alternative |

---

## Cosine Similarity Scale

| Score | Meaning |
|-------|---------|
| 0.95 – 1.0 | Near-identical meaning |
| 0.85 – 0.94 | Very similar (same topic) |
| 0.70 – 0.84 | Related but different angle |
| 0.50 – 0.69 | Loosely related |
| Below 0.50 | Different topics |

---

## When to Use / Not Use Embeddings

| Use embeddings when... | Don't use embeddings when... |
|------------------------|------------------------------|
| You need semantic/meaning-based search | You need exact keyword matching only |
| You want to find similar documents | You need precise boolean queries |
| You're building RAG retrieval | The corpus is tiny (< 50 docs) — just use LLM directly |
| Clustering or deduplication tasks | Real-time updates with no vector DB available |

---

## Golden Rules

1. **Use the same model for indexing and querying** — if you embed documents with model A, you must embed queries with model A too.
2. **Normalize inputs** — strip HTML, extra whitespace, and irrelevant metadata before embedding.
3. **Chunk large documents** — embeddings work best on short, focused text (100–512 tokens). Long documents lose specificity.
4. **Batch your API calls** — embedding 1000 documents individually is slow and expensive; batch them.
5. **Cache embeddings** — embeddings are deterministic. Don't re-embed the same content twice.
6. **Cosine similarity > Euclidean distance** for text similarity tasks.
7. **Dimensionality matters** — more dimensions = more expressive but slower search and more storage.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [03 Structured Outputs](../03_Structured_Outputs/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 Vector Databases](../05_Vector_Databases/Theory.md)
