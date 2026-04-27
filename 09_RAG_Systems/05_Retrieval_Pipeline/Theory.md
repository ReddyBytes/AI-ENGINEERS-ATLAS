# Retrieval Pipeline — Theory

A user types a question. Somewhere in your 10,000 documents, there are 3 chunks that directly answer it. The retrieval pipeline's job: find those 3 chunks in milliseconds — like a fingerprint matching system. Every chunk has a "fingerprint" (its embedding). The question gets a fingerprint using the same method. Then you find the database fingerprints most similar to the question's.

👉 This is why we need the **Retrieval Pipeline** — converting a user question into the same "language" as indexed documents so we can find the most relevant ones instantly.

---

## 📌 Learning Priority

**Must Learn** — core concepts, needed to understand the rest of this file:
[Retrieval Steps](#the-retrieval-steps) · [Top-K Selection](#top-k-how-many-to-retrieve) · [What Results Look Like](#what-the-results-look-like)

**Should Learn** — important for real projects and interviews:
[Metadata Filtering](#metadata-filtering) · [Retrieval Quality Problem](#the-retrieval-quality-problem)

**Good to Know** — useful in specific situations, not needed daily:
[Cosine Similarity at Retrieval](#cosine-similarity-at-retrieval-time)

---

## The Retrieval Steps

```mermaid
flowchart LR
    A[User Question] --> B[Embed with\nsame model]
    B --> C[Query Vector]
    C --> D[(Vector DB\nANN Search)]
    D --> E[Top-K Chunks\nwith scores]
    E --> F[Filter by\nmetadata optional]
    F --> G[Return ranked\nchunks + metadata]
```

1. **Embed the query** — pass the user's question through the same embedding model used at indexing time, putting the question in the same vector space as stored chunks.
2. **ANN search** — the vector DB finds the K stored vectors most similar to the query vector (cosine similarity or dot product).
3. **Return results** — top-K chunks with text, metadata, and similarity scores.

---

## Cosine Similarity at Retrieval Time

In ChromaDB: `distances` are cosine distances (0 = identical, 2 = opposite). Convert to similarity with `1 - distance`.

```python
# Simplified — ChromaDB does this internally
query_vector = embed("what's the refund timeline?")
# Compares against all 20,000 stored vectors, returns top-3 by cosine similarity
```

---

## Top-K: How Many to Retrieve?

K is a hyperparameter. Typical values: 3–10.
- Too few (K=1–2): might miss the right chunk
- Too many (K=10–20): irrelevant chunks confuse the LLM, increases token cost

Start with K=3–5. If answers are missing information, increase K. If answers are vague or conflated, decrease K.

---

## Metadata Filtering

Combine semantic search with exact attribute filters:

```python
results = collection.query(
    query_texts=["termination conditions"],
    n_results=5,
    where={"document_type": "contract", "year": {"$gte": 2023}}
)
```

Documents that don't match the metadata filter are excluded before similarity ranking.

---

## What the Results Look Like

```python
results = collection.query(...)

# results["documents"][0]  = list of text chunks
# results["metadatas"][0]  = list of metadata dicts
# results["distances"][0]  = list of cosine distances (lower = more similar)
# results["ids"][0]        = list of chunk IDs

for doc, meta, dist in zip(
    results["documents"][0],
    results["metadatas"][0],
    results["distances"][0]
):
    similarity = 1 - dist
    print(f"[{similarity:.3f}] {meta['source']}, p.{meta.get('page', '?')}")
    print(f"  {doc[:100]}")
```

---

## The Retrieval Quality Problem

Retrieval quality is the #1 factor in RAG accuracy. Common failures:
- Query asks about "30-day refund" but the chunk says "one month return window" — semantics missed
- The relevant information spans two chunks — neither chunk alone answers completely
- The chunk is retrieved but it's from the wrong product version

Fixes: hybrid search (semantic + keyword), better chunking, re-ranking (see Advanced RAG section).

---

✅ **What you just learned:** The retrieval pipeline embeds the user's query with the same model used at indexing time, runs an ANN search in the vector database, and returns the top-K most semantically similar chunks with their metadata and scores.

🔨 **Build this now:** Use the ChromaDB collection from the previous section. Write a `retrieve(query, top_k=3)` function. Test it with 5 different questions and print the similarity scores and chunk text for each.

➡️ **Next step:** Context Assembly → `09_RAG_Systems/06_Context_Assembly/Theory.md`

---

## 🛠️ Practice Project

Apply what you just learned → **[I2: Personal Knowledge Base (RAG)](../../22_Capstone_Projects/07_Personal_Knowledge_Base_RAG/03_GUIDE.md)**
> This project uses: querying the vector store, returning top-K chunks, filtering by metadata


---

## 📝 Practice Questions

- 📝 [Q58 · retrieval-pipeline](../../ai_practice_questions_100.md#q58--critical--retrieval-pipeline)


---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| 📄 **Theory.md** | ← you are here |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [04 Embedding and Indexing](../04_Embedding_and_Indexing/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [06 Context Assembly](../06_Context_Assembly/Theory.md)
