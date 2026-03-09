# Embedding and Indexing — Interview Q&A

## Beginner

**Q1: What is the difference between embedding and indexing in a RAG pipeline?**

Embedding is the process of converting a text chunk into a vector — a fixed-size list of floating-point numbers that encodes the meaning of the text. You pass text through an embedding model and get back a vector like `[0.23, -0.45, 0.11, ...]`.

Indexing is what you do with those vectors after you create them. You store them in a vector database that builds a specialized search structure (usually HNSW) on top of the vectors. This structure allows you to find the vectors most similar to a query vector in milliseconds, without comparing against every stored vector one by one.

Think of it this way: embedding is the process of assigning a location code to each book. Indexing is building the shelf system that lets you find books by their location code quickly.

---

**Q2: Why should you batch-embed your chunks instead of embedding them one at a time?**

API-based embedding models have a fixed overhead for each HTTP request — typically 100–500ms just for network latency. If you embed 10,000 chunks one at a time, you make 10,000 API calls at ~300ms each = 50 minutes.

If you batch them into groups of 2,048 (the OpenAI limit), you make 5 API calls. Total time: seconds.

For local models like sentence-transformers, batching enables GPU parallelism — the model processes multiple inputs simultaneously on the GPU instead of sequentially. A batch of 64 takes roughly the same time as a batch of 1 on a GPU.

Always batch. For OpenAI: up to 2,048 per call. For sentence-transformers: `model.encode(chunks, batch_size=64)`.

---

**Q3: What is "embedding drift" and how does it break your RAG system?**

Embedding drift happens when the vectors in your database were created with one embedding model, but you later switch to a different model (or a different version of the same model).

Each model creates its own vector space with its own geometry. The word "dog" might be at coordinates [0.3, -0.7, ...] in model A, and at [0.8, 0.1, ...] in model B. These are completely different locations in completely different spaces.

If your database has vectors from model A and you embed a query with model B, you're comparing apples to oranges. The similarity scores are meaningless and retrieval breaks completely.

Fix: when you change embedding models, you must re-embed ALL documents in the database with the new model. There's no partial fix. This is why changing embedding models is a big operational decision.

---

## Intermediate

**Q4: How do you make your indexing pipeline idempotent so it can be safely re-run?**

An idempotent pipeline produces the same result whether run once or many times. This is critical for production — you'll need to re-run if new documents arrive, if chunks change, or if something fails partway through.

Three techniques:

(1) **Deterministic chunk IDs**: generate IDs from a hash of the chunk content (and optionally the source + position). If the same chunk is processed twice, it gets the same ID. The database upsert (insert or update by ID) safely handles duplicates.

```python
import hashlib
def chunk_id(text: str, source: str) -> str:
    return hashlib.md5(f"{source}:{text}".encode()).hexdigest()[:16]
```

(2) **Upsert semantics**: use `collection.upsert()` instead of `collection.add()`. Upsert: if ID exists, update; if not, insert. Never duplicates.

(3) **Change detection**: store a hash of each source document. Before re-indexing, check if the hash matches. If unchanged, skip. Only re-index modified documents.

---

**Q5: What should you store as metadata alongside each vector? Why does it matter?**

Metadata travels with the vector through indexing, retrieval, and into the final answer. At minimum store: `source` (filename/URL), `page` (for PDFs), and any field you'll want to filter by.

Why it matters:

**Citations**: when the LLM answers "The refund policy states 30 days," you can tell the user "Source: Company Handbook, page 3." Without `source` in metadata, you can't cite.

**Filtering**: "Only retrieve from the HR policy, not the general FAQ." Without `section` or `document_type` metadata, you can't scope.

**Debugging**: when retrieval returns wrong results, metadata tells you exactly which chunks were returned and from where. Without metadata, debugging is guesswork.

**Freshness filtering**: `last_updated` metadata lets you exclude outdated documents. "Only return results from documents updated after 2024-01-01."

The rule: store everything you might need downstream. Storage cost for metadata is negligible.

---

**Q6: How do you handle a large corpus of 500,000 documents efficiently during the indexing phase?**

The naive approach (embed one at a time, add one at a time) would take days. Efficient approach:

**Parallel embedding**: run multiple embedding worker processes. For API-based models: async HTTP calls to hit rate limits efficiently. For local models: multiple GPU workers. A 4x parallel pipeline cuts time by ~75%.

**Batch API calls**: embed in maximum batch sizes (2,048 for OpenAI). Each API call has fixed overhead; maximize tokens per call.

**Progress tracking**: maintain a processed_ids set (or a DB table). If the job fails at chunk 100,000 out of 500,000, resume from 100,001 instead of starting over.

**Rate limit handling**: OpenAI and other APIs have tokens-per-minute limits. Implement exponential backoff for 429 errors. Track token usage and throttle proactively.

**Incremental indexing**: don't re-index unchanged documents. Fingerprint (hash) each source document. Only process documents with new or changed fingerprints.

**Infrastructure**: for 500K documents, run on a machine with enough RAM to hold embeddings in memory before batch-inserting. Or stream-insert as you embed to avoid OOM.

---

## Advanced

**Q7: Explain the HNSW data structure. How does it achieve fast approximate nearest neighbor search?**

HNSW (Hierarchical Navigable Small World) is a graph-based ANN index. It organizes vectors into a multi-layer graph.

Each vector is a node. Each node is connected to its nearest neighbors in the same layer. The graph has multiple layers — higher layers are sparse (few nodes, long-range connections), lower layers are dense (many nodes, short-range connections).

To search: start at an entry point in the top layer. Greedily move toward the query — always jump to the neighbor closest to the query. When you can't get closer, descend to the next layer (more nodes, shorter connections, finer-grained navigation). Repeat until you reach the bottom layer. Return the K nearest nodes found.

This is like a GPS navigation: first navigate at the highway level (top layer), then local roads (middle layer), then specific streets (bottom layer). You skip most of the graph at each level, dramatically reducing the number of distance comparisons.

Construction is O(n log n) on average. Query time is roughly O(log n) — sublinear in the number of stored vectors. This is why searching 10 million vectors is nearly as fast as searching 1 million.

---

**Q8: What is the difference between using ChromaDB's built-in embedding function vs. pre-computing embeddings yourself?**

Built-in embedding function: you pass `embedding_function=SentenceTransformerEmbeddingFunction(...)` when creating the collection. ChromaDB embeds both your documents and queries automatically. Simple, fewer lines of code, but you have less control.

Pre-computing embeddings: you embed chunks yourself (using any library or API), then pass the raw vectors to `collection.add(embeddings=[...])`. ChromaDB stores and indexes them, but you control the embedding process entirely.

When to pre-compute: (1) You want to batch-embed efficiently with full control. (2) You need to embed with an API that ChromaDB doesn't support natively. (3) You want to cache embeddings separately (avoid re-embedding if the index is rebuilt). (4) You need to track the exact model version used for auditing.

When to use built-in: (1) Prototyping quickly. (2) Using a supported model (sentence-transformers, OpenAI). (3) You don't need external embedding cache.

Production recommendation: pre-compute and cache. More control, better debuggability, and you can switch vector DBs without re-embedding.

---

**Q9: How would you design an indexing system that supports multiple embedding models simultaneously?**

Use case: you want to experiment with different models or support different languages with specialized models.

Architecture: separate collections per model in the vector DB. Use a router layer that decides which collection(s) to query based on the request.

```python
# Each model gets its own collection
collections = {
    "english": chroma.get_or_create_collection("docs_english_minilm"),
    "multilingual": chroma.get_or_create_collection("docs_multilingual_e5"),
    "code": chroma.get_or_create_collection("docs_code_codebert"),
}

# Router
def route_query(query: str, doc_type: str) -> str:
    if doc_type == "code":
        return "code"
    if detect_language(query) != "en":
        return "multilingual"
    return "english"
```

Operational considerations: double the storage and embedding cost. Synchronized updates — when a document changes, update all relevant collections. Version tracking — each collection's metadata records which model version was used. Migration strategy — when a model is deprecated, re-index its collection with the replacement.

For most use cases, one well-chosen model is simpler and performs nearly as well. Only run multiple models when you have a measurable, specific reason.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [03 Chunking Strategies](../03_Chunking_Strategies/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 Retrieval Pipeline](../05_Retrieval_Pipeline/Theory.md)
