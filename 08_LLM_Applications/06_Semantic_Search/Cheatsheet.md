# Semantic Search — Cheatsheet

**One-liner:** Semantic search finds documents by meaning rather than keywords — converting both the query and documents to embeddings and measuring vector similarity.

---

## Key Terms

| Term | Definition |
|------|-----------|
| **Semantic search** | Retrieve documents by meaning similarity, not keyword matching |
| **Keyword search** | Match exact words using inverted index (BM25, TF-IDF) |
| **BM25** | A strong keyword ranking algorithm — the "gold standard" for exact matches |
| **Hybrid search** | Combine semantic + keyword scores for better overall retrieval |
| **RRF** | Reciprocal Rank Fusion — algorithm to merge ranking lists from multiple methods |
| **Re-ranking** | A second pass using a more powerful model to reorder top-K candidates |
| **Cross-encoder** | A model that takes query + document together to score relevance (used for re-ranking) |
| **Bi-encoder** | Encodes query and document separately — used for fast initial retrieval |
| **Recall** | How many relevant docs were found (out of all relevant docs) |
| **Precision** | How many returned docs are relevant (out of all returned) |

---

## Search Pipeline

```
Query
  → Embed (bi-encoder: fast)
  → Vector DB search → top-20
  → Optional: BM25 keyword search → top-20
  → Optional: RRF fusion → top-20 combined
  → Optional: Cross-encoder re-rank → top-5
  → Return to user
```

---

## When to Use Each Approach

| Approach | When to Use |
|----------|-------------|
| Pure semantic | General question/answer over conceptual documents |
| Pure keyword | Product codes, proper nouns, exact technical terms |
| Hybrid | Most real-world applications — gives you the best of both |
| + Re-ranking | When accuracy matters more than latency (adds ~50–200ms) |

---

## Golden Rules

1. **Embed query and documents with the same model** — different models produce incompatible vector spaces.
2. **Hybrid search beats pure semantic in most production cases** — add BM25 even if you're not sure.
3. **Re-ranking is worth it** — top-K cosine results aren't always in the best order; re-ranking fixes this.
4. **Chunk documents before embedding** — long documents produce diluted embeddings. 256–512 tokens per chunk is typical.
5. **Top-K is a hyperparameter** — retrieve more candidates than you show (e.g. top-20 → re-rank → show top-5).
6. **Evaluate with real queries** — don't assume it works. Build a test set of (query, expected_document) pairs and measure recall.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [05 Vector Databases](../05_Vector_Databases/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [07 Memory Systems](../07_Memory_Systems/Theory.md)
