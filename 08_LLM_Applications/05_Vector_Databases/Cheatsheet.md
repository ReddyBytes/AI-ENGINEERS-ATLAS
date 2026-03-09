# Vector Databases — Cheatsheet

**One-liner:** A vector database stores and indexes embeddings (number vectors) so you can search millions of documents by semantic meaning in milliseconds — something regular SQL databases cannot do.

---

## Key Terms

| Term | Definition |
|------|-----------|
| **Vector database** | A database optimized for storing and searching high-dimensional vectors |
| **ANN** | Approximate Nearest Neighbor — fast search that trades tiny accuracy loss for massive speed |
| **HNSW** | Hierarchical Navigable Small World — the most common ANN index algorithm |
| **IVF** | Inverted File Index — another ANN approach, quantizes vectors into clusters |
| **Collection / Index** | A named set of related vectors (like a table in SQL) |
| **Top-K** | Return the K most similar results to the query |
| **Metadata filtering** | Combine vector search with SQL-like filters on stored metadata |
| **Namespace** | Logical partition within an index (Pinecone) / tenant isolation |
| **Distance metric** | How similarity is measured: cosine, dot product, or Euclidean |
| **Upsert** | Insert or update a vector by ID |

---

## ChromaDB Quick Reference

```python
import chromadb
client = chromadb.Client()

# Create collection
collection = client.create_collection("my_docs")

# Add documents
collection.add(
    documents=["doc text 1", "doc text 2"],
    ids=["id1", "id2"],
    metadatas=[{"source": "wiki"}, {"source": "blog"}]
)

# Query
results = collection.query(
    query_texts=["your question here"],
    n_results=3
)
```

---

## When to Use / Not Use a Vector Database

| Use vector DB when... | Don't use vector DB when... |
|-----------------------|-----------------------------|
| Corpus > 10K documents | Small corpus (< 1K docs) — use numpy |
| Need millisecond search | Batch processing offline |
| Need metadata filtering | Exact keyword search only — use SQL |
| Production RAG system | Prototype / exploration — Chroma in-memory is fine |

---

## Golden Rules

1. **Embed and store together** — when you add a document, embed it and store the vector immediately.
2. **Never mix embedding models** — all vectors in a collection must come from the same model.
3. **Choose your distance metric at creation time** — can't change it after indexing.
4. **Use metadata for scoping** — filter by user_id, document_type, date to improve relevance.
5. **ChromaDB for dev, Pinecone/Weaviate for prod** — don't let your vector DB be your scaling bottleneck.
6. **Back up your vectors** — re-embedding at scale is expensive. Persist and backup your index.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |
| [📄 Comparison.md](./Comparison.md) | Vector database comparison |

⬅️ **Prev:** [04 Embeddings](../04_Embeddings/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [06 Semantic Search](../06_Semantic_Search/Theory.md)
