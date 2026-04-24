# Vector Databases — Interview Q&A

## Beginner

**Q1: What is a vector database and why can't we use a regular database for this?**

<details>
<summary>💡 Show Answer</summary>

A vector database is a database designed specifically to store, index, and search high-dimensional float vectors (embeddings). Regular relational databases like PostgreSQL are designed for exact matches and range queries — `WHERE name = 'John'` or `WHERE price < 100`. They have no concept of "similarity" between vectors.

If you stored 1 million 1536-dimensional vectors in a SQL table and wanted to find the 10 most similar to a query vector, you'd need to compare your query against all 1 million — computing 1 million dot products every time. That's too slow for real-time use. Vector databases use specialized indexing structures (HNSW, IVF) that can find the top-10 similar vectors in milliseconds across hundreds of millions of entries.

</details>

---

**Q2: What is HNSW and why is it the most popular vector index algorithm?**

<details>
<summary>💡 Show Answer</summary>

HNSW stands for Hierarchical Navigable Small World. It's a graph-based data structure that enables approximate nearest neighbor (ANN) search very efficiently.

Imagine each vector as a city on a map. HNSW builds a multi-layer map. The top layer has only a few "highway-connected" cities. Each lower layer adds more cities with shorter connections. To find the nearest neighbor to a query, you start at the top layer, greedily navigate toward the query point, then descend to finer layers for refinement — like zooming in on a map from continent to street.

It's popular because: (1) Very fast query time even at millions of vectors. (2) Good recall (finds the true nearest neighbor most of the time). (3) Efficient memory usage. (4) Supports incremental inserts without full reindexing.

</details>

---

**Q3: What is the difference between an exact nearest neighbor search and an approximate nearest neighbor search?**

<details>
<summary>💡 Show Answer</summary>

Exact nearest neighbor (ENN): guarantees you find the single most similar vector. Requires comparing the query to every vector in the database — O(n) cost. Fine for small collections (< 10K vectors), too slow for large ones.

Approximate nearest neighbor (ANN): finds vectors that are very likely the most similar, but doesn't guarantee it for every single query. Uses smart indexing (HNSW, IVF) to skip most comparisons — sublinear search cost. In practice, ANN algorithms achieve 95–99.9% recall (they find the true nearest neighbor 95–99.9% of the time) while being 100–1000x faster than exact search.

For RAG and semantic search applications, ANN is always used. If you occasionally miss the #1 match and return #2 instead, the downstream quality impact is negligible.

</details>

---

## Intermediate

**Q4: Explain metadata filtering in vector databases. Why is it important for enterprise RAG?**

<details>
<summary>💡 Show Answer</summary>

Metadata filtering lets you combine vector similarity search with exact attribute filters — essentially, semantic search with SQL WHERE clauses applied simultaneously.

Example: "Find the 5 most similar documents to my query, but only consider documents from department='finance' AND year >= 2024."

Why this matters for enterprise RAG: Without filtering, a query from a sales rep might retrieve documents from legal, HR, or engineering — wrong context, wrong data, potential compliance issues. With metadata filtering, you can scope results to the user's business unit, document access level, recency requirements, language, and more.

Implementation note: metadata filtering happens before or during the ANN search, not after. Filtering after would mean you retrieve 1000 candidates then filter to 5 — wasting the speed advantage. Good vector DBs integrate filtering into the index traversal.

</details>

---

**Q5: How would you handle a situation where your vector database is becoming a bottleneck in production?**

<details>
<summary>💡 Show Answer</summary>

Diagnose first: is the bottleneck query latency, insert throughput, or memory?

For query latency: (1) Reduce dimensionality — use Matryoshka embeddings at 256 dims instead of 1536. (2) Tune HNSW parameters — increase ef_search for better recall but higher latency, decrease for faster but less accurate. (3) Add read replicas. (4) Cache frequent queries.

For insert throughput: (1) Batch upserts instead of single inserts. (2) Build index offline then swap in.

For memory: (1) Use product quantization (PQ) to compress vectors. (2) Shard across multiple nodes. (3) Use a disk-based index for rarely accessed vectors.

Also consider: are you using the right tool? pgvector is great for small to medium scale. For 10M+ vectors with high QPS, dedicated vector DBs (Pinecone, Weaviate, Qdrant) are purpose-built.

</details>

---

**Q6: What is the difference between cosine similarity, dot product, and Euclidean distance as distance metrics?**

<details>
<summary>💡 Show Answer</summary>

Cosine similarity: measures the angle between vectors, ignoring magnitude. A score of 1 = same direction (identical meaning), 0 = orthogonal (unrelated). Standard for text embeddings because it's scale-invariant — a short sentence and a long paragraph about the same topic can have high similarity.

Dot product: multiplied sum of corresponding elements. Essentially cosine similarity scaled by vector magnitudes. If your embedding model normalizes its output to unit vectors (magnitude = 1), then dot product equals cosine similarity and is slightly faster to compute.

Euclidean (L2) distance: straight-line distance in vector space. Lower = more similar. Sensitive to magnitude — vectors of different lengths can be "far apart" even if they point in the same direction. Less common for text but used in image and audio embeddings.

Rule of thumb: for text with OpenAI or sentence-transformers embeddings, use cosine similarity or dot product (models often normalize output). Check your embedding model's recommendation.

</details>

---

## Advanced

**Q7: How do you build a multi-tenant vector database system where different users can't see each other's data?**

<details>
<summary>💡 Show Answer</summary>

Three common approaches:

(1) Namespace/collection per tenant: each customer gets their own collection. Simple, strong isolation, but doesn't scale past a few thousand tenants (each collection has overhead).

(2) Metadata filtering with tenant_id: all vectors in one collection, every vector tagged with `{"tenant_id": "customer_123"}`. Every query filters by tenant_id. Fast and scalable, but you must be careful never to forget the filter — one missing filter leaks all data.

(3) Separate vector DB instances: full isolation, but operationally expensive. Used in high-compliance environments.

For most SaaS: approach (2) with mandatory application-level enforcement of tenant_id filtering. Add integration tests that verify tenant isolation never leaks. Log and alert on any query missing the tenant_id filter.

</details>

---

**Q8: Explain product quantization (PQ) and when you'd use it.**

<details>
<summary>💡 Show Answer</summary>

Product quantization is a vector compression technique that reduces storage and speeds up search at the cost of some accuracy.

How it works: split each 1536-dim vector into M subvectors (e.g., 16 subvectors of 96 dims each). For each subspace, cluster the data into K centroids (typically 256). Replace each subvector with the index of its nearest centroid — just 1 byte instead of 96 floats. Total compression: 1536 floats (6KB) → 16 bytes.

Distance computation: instead of comparing raw vectors, compare compressed codes using precomputed lookup tables. Much faster.

When to use: when memory is the bottleneck, you have 50M+ vectors, and you can tolerate a 5–10% recall drop. Not worth it for small to medium collections where HNSW already fits in RAM.

</details>

---

**Q9: What are the tradeoffs between pgvector and a dedicated vector database like Pinecone?**

<details>
<summary>💡 Show Answer</summary>

pgvector is a PostgreSQL extension that adds vector column types and HNSW/IVF index support. Dedicated databases like Pinecone are purpose-built for vector search.

pgvector advantages: you already have PostgreSQL — no new infrastructure, no data sync, ACID transactions with your regular data, JOIN vector results with relational data in one query, familiar SQL interface.

pgvector limitations: not optimized for scale beyond ~5M vectors. Under high concurrent query load, PostgreSQL's general-purpose architecture adds overhead. Horizontal scaling requires custom sharding.

Pinecone advantages: built for horizontal scale, managed service (no infra ops), built-in namespacing, very fast at 10M+ vectors.

Pinecone limitations: cost (pricing per pod), vendor lock-in, data leaves your infrastructure, no SQL joins.

Decision: if you're at < 5M vectors, have PostgreSQL, and want simplicity — pgvector. If you're at production scale with millions of vectors, high QPS requirements, and cost isn't a concern — Pinecone or Weaviate.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |
| [📄 Comparison.md](./Comparison.md) | Vector database comparison |

⬅️ **Prev:** [04 Embeddings](../04_Embeddings/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [06 Semantic Search](../06_Semantic_Search/Theory.md)
