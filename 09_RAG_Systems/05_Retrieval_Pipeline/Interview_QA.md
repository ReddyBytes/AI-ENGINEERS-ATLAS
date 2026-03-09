# Retrieval Pipeline — Interview Q&A

## Beginner

**Q1: What does the retrieval pipeline do in a RAG system?**

The retrieval pipeline takes the user's question, converts it into a vector using the same embedding model that was used to index the documents, then searches the vector database for the chunks most semantically similar to that question.

The output is a ranked list of the top-K chunks with their text, metadata, and similarity scores. These chunks are then passed to the LLM as context to generate the answer.

The critical detail: you must use the same embedding model for both indexing and retrieval. The model defines the vector space. If you index with model A and query with model B, you're comparing vectors from two incompatible spaces and retrieval will completely break.

---

**Q2: What is cosine similarity and why do we use it for retrieval?**

Cosine similarity measures how similar two vectors are based on the angle between them, not their length. It returns a value between -1 and 1, where 1 means identical direction (same meaning) and 0 means unrelated.

We use it for text retrieval because embedding models are trained to place semantically similar sentences near each other in vector space. Two sentences with the same meaning will point in nearly the same direction even if they use completely different words. "I need to return a purchase" and "product return policy" will have high cosine similarity because the model learned they're related.

ChromaDB actually returns cosine distance (0 = identical, 2 = opposite), which you convert to similarity with `1 - distance`.

---

**Q3: What does top-K mean in retrieval, and how do you choose K?**

Top-K means the K most similar chunks to the query are returned. K is a hyperparameter — you pick the value.

Typical starting point: K=3. The reasoning:
- Too small (K=1–2): you might miss the right chunk, especially if the answer spans multiple chunks
- Too large (K=10+): you start including weakly relevant chunks that add noise and confuse the LLM, plus cost increases with more tokens

How to tune K: run your test questions with K=3, K=5, and K=7. Measure answer quality. If answers are consistently missing information, increase K. If answers are vague or mixing up details from unrelated chunks, decrease K.

---

## Intermediate

**Q4: What is metadata filtering and how does it interact with vector search?**

Metadata filtering adds exact-match constraints to the vector search. Instead of searching all stored vectors, you first filter to only the documents matching your criteria, then do the similarity search within that subset.

Example: `where={"section": "returns"}` retrieves only chunks tagged with the "returns" section. This is efficient because the filter runs before similarity ranking, reducing the search space.

This is essential for:
- Multi-tenant systems (user A should only see their documents)
- Versioned documents (only search the current version)
- Scoped queries (a question about HR policy shouldn't pull results from engineering docs)

ChromaDB supports: `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$in`, `$nin`, `$and`, `$or` in the `where` clause.

---

**Q5: How do similarity scores help detect out-of-scope queries?**

Every retrieved chunk comes with a similarity score (0–1). If the user asks about something not in your knowledge base, the best matching chunks will have low scores — say 0.3–0.4 — because even the "closest" document isn't really related.

Pattern:
```python
results = retrieve(query, top_k=5)
if results[0]["similarity"] < 0.5:
    return "I don't have information about that in our knowledge base."
```

This is much better than passing low-quality chunks to the LLM and letting it hallucinate an answer. A 0.4 similarity score means the chunk is only weakly related — the LLM will either make up details or give a confusing answer.

Rule of thumb: >0.7 = strong match, 0.5–0.7 = okay, <0.5 = likely out of scope. These thresholds depend on your embedding model and data; calibrate on your own examples.

---

**Q6: What are the main causes of retrieval failure, and how do you fix each one?**

Three common failure modes:

**Vocabulary mismatch**: the query uses different words than the document. "30-day refund" vs "one month return window." Semantic embeddings usually handle this, but for very domain-specific terms (product codes, legal phrases) they can fail. Fix: hybrid search — combine semantic vectors with BM25 keyword search.

**Answer spans multiple chunks**: the complete answer requires information from two different chunks, but neither chunk alone scores high enough. Fix: increase K, or use parent-child chunking where retrieving a child chunk automatically includes its parent (full section).

**Stale or wrong version**: retrieved chunk is from an outdated policy. Fix: store a `version` or `last_updated` field as metadata, and filter to only current documents: `where={"version": "current"}`.

The best diagnostic tool: log the retrieved chunks and their scores for every query that gives a wrong answer. The failure mode is immediately visible.

---

## Advanced

**Q7: Explain how ANN (Approximate Nearest Neighbor) search works in a vector database.**

Exact nearest neighbor search requires comparing the query vector to every stored vector — O(n) comparisons. For a database with 10 million vectors of 384 dimensions, that's 3.84 billion floating-point operations per query. Too slow.

ANN trades a small amount of accuracy for a massive speed improvement. Most vector databases use HNSW (Hierarchical Navigable Small World), a graph-based index:

- Vectors are organized into a multi-layer graph. Top layers are sparse (few nodes, long-range connections). Bottom layers are dense (many nodes, short-range connections).
- At search time: start at the top layer, greedily move toward the nearest neighbor at each layer, descend to the next layer, repeat.
- This is like GPS navigation: first route at the highway level, then local roads, then specific streets — skipping most of the graph at each level.
- HNSW query time is roughly O(log n), which is why searching 10M vectors is nearly as fast as searching 1M.

The "approximate" means occasionally the true nearest neighbor is missed, but the error rate is typically <1% with default settings.

---

**Q8: How would you build a retrieval pipeline that gracefully handles queries in multiple languages?**

The core problem: if your index was built with an English embedding model, non-English queries will produce vectors in a different region of the space — retrieval will fail even if a translated version of the answer exists.

Solution options:

**Option 1 — Multilingual embedding model**: use a model like `multilingual-e5-large` or `paraphrase-multilingual-MiniLM-L12-v2` that was trained on 100+ languages. All queries — regardless of language — map to the same shared vector space. One index, no language detection needed. Trade-off: slightly lower quality for any single language compared to a specialized model.

**Option 2 — Language routing**: detect the query language, translate to English (or the index language) before embedding, retrieve, then translate the answer back. More complex pipeline, but keeps high accuracy with a monolingual embedding model.

**Option 3 — Parallel language indexes**: index your documents in multiple languages (original + translations). Maintain a separate ChromaDB collection per language. Route queries to the matching collection based on detected language.

For most production cases: multilingual model is the right answer unless you have specific accuracy requirements that justify the complexity of routing.

---

**Q9: How do you evaluate retrieval quality separately from generation quality in a RAG system?**

Retrieval quality and generation quality are separate and must be measured separately. A system can have great retrieval but poor generation (the right chunks were found but the LLM summarized them badly), or good generation but poor retrieval (the LLM sounds confident but answered from the wrong chunks).

**Measuring retrieval quality:**

Create a test set of (question, expected_chunk) pairs. For each question, run retrieval and check:
- **Hit rate at K**: was the expected chunk in the top-K results? (binary 0/1 per question)
- **MRR (Mean Reciprocal Rank)**: `1/rank` where rank is the position of the expected chunk. Hit at position 1 = 1.0, position 2 = 0.5, position 3 = 0.33. Average across all questions.
- **NDCG**: a graded version that rewards finding the right chunk at a higher position more than a lower one.

```python
def hit_rate_at_k(retrieved_ids, expected_id, k):
    return expected_id in retrieved_ids[:k]

def mrr(retrieved_ids, expected_id):
    if expected_id in retrieved_ids:
        return 1 / (retrieved_ids.index(expected_id) + 1)
    return 0
```

Target benchmarks: hit rate @3 > 0.85 is good for most RAG applications. If you're below 0.7, fix retrieval before touching generation — generation quality is bounded by retrieval quality.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [04 Embedding and Indexing](../04_Embedding_and_Indexing/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [06 Context Assembly](../06_Context_Assembly/Theory.md)
