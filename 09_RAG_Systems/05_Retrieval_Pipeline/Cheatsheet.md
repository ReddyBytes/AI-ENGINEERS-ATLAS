# Retrieval Pipeline — Cheatsheet

**One-liner:** Embed the user's question with the same model used at indexing time, run a nearest-neighbor search in the vector database, and return the top-K most semantically similar chunks.

---

## Key Terms

| Term | What it means |
|---|---|
| **Query embedding** | The vector representation of the user's question |
| **ANN search** | Approximate Nearest Neighbor — fast similarity search over stored vectors |
| **Top-K** | The K most similar chunks returned by the search |
| **Cosine distance** | How different two vectors are (0 = identical, 2 = opposite) |
| **Cosine similarity** | `1 - cosine_distance` (higher = more similar, range 0–1) |
| **Metadata filter** | An exact-match filter applied alongside the vector search |
| **Similarity threshold** | Minimum score a chunk must have to be included (e.g., 0.6) |
| **Recall** | Did we retrieve the right chunks? (missing chunks = wrong answers) |

---

## The Retrieval Steps

```
1. User types a question
2. Embed the question → query vector (same model as index)
3. ANN search → compare query vector to all stored vectors
4. Return top-K chunks sorted by similarity score
5. (Optional) Filter by metadata before or after search
6. (Optional) Drop chunks below a minimum similarity threshold
```

---

## Top-K: Quick Guide

| K value | Effect |
|---|---|
| K = 1–2 | Fast, cheap, but may miss the right chunk |
| K = 3–5 | Good default — enough context without noise |
| K = 10–20 | High recall, but irrelevant chunks confuse the LLM |

Start with K=3. If answers are missing info, increase. If answers are vague or conflated, decrease.

---

## Distance vs Similarity

ChromaDB returns **cosine distance** (lower = closer):

```python
# Convert ChromaDB distance to similarity
similarity = 1 - distance   # distance=0.2 → similarity=0.8

# Threshold rule of thumb
if similarity >= 0.7:   # strong match
if similarity >= 0.5:   # okay match
if similarity < 0.5:    # probably irrelevant — skip it
```

---

## Metadata Filtering

```python
# Filter BEFORE similarity search (most efficient)
collection.query(
    query_texts=["your question"],
    n_results=5,
    where={"section": "returns"}          # exact match
    # where={"year": {"$gte": 2023}}      # numeric comparison
    # where={"$and": [{"dept": "HR"}, {"year": {"$gte": 2023}}]}
)
```

Supported operators: `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$in`, `$nin`, `$and`, `$or`

---

## When to Use / Not Use Metadata Filtering

| Use filtering when... | Don't use it when... |
|---|---|
| You have structured, consistent metadata | Metadata is missing or inconsistent |
| User queries are clearly scoped (e.g., "HR only") | All documents are in the same scope |
| You have multiple document types/versions | You want broad semantic search |
| You need to exclude outdated documents | |

---

## The Quality Check Pattern

```python
def retrieve_with_threshold(query, top_k=5, min_sim=0.6):
    results = retrieve(query, top_k=top_k)
    good = [r for r in results if r["similarity"] >= min_sim]
    if not good:
        print(f"WARNING: Best match was {results[0]['similarity']:.3f}")
    return good
```

If nothing passes the threshold, the answer is likely out of scope. Return a "I don't have information on that" response rather than hallucinating.

---

## Golden Rules

1. **Use the same embedding model** for indexing and retrieval — mixing models breaks everything.
2. **Start with K=3** and tune from there.
3. **Use a similarity threshold** — don't pass low-quality chunks to the LLM.
4. **Add metadata at indexing time** — you can't filter on what you didn't store.
5. **Semantic search handles paraphrasing** — "30 days to return" and "one month return window" retrieve the same chunk.
6. **Retrieval quality is the #1 factor in RAG accuracy** — if the right chunk isn't retrieved, the LLM can't answer correctly.
7. **Log similarity scores** in development — they tell you exactly why retrieval is failing.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [04 Embedding and Indexing](../04_Embedding_and_Indexing/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [06 Context Assembly](../06_Context_Assembly/Theory.md)
