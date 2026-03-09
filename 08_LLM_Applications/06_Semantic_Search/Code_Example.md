# Semantic Search — Code Example

Build semantic search over 10 documents using sentence-transformers. Shows both pure semantic and hybrid search with cosine similarity.

```python
# pip install sentence-transformers numpy
import numpy as np
from sentence_transformers import SentenceTransformer

# ─────────────────────────────────────────────
# Our document corpus — 10 documents on diverse topics
# ─────────────────────────────────────────────

documents = [
    # Programming
    "Python is widely used for data science and machine learning applications.",
    "JavaScript runs in the browser and is essential for web development.",
    "SQL is a language for querying relational databases efficiently.",

    # AI/ML
    "Gradient descent is an optimization algorithm that minimizes the loss function.",
    "Convolutional neural networks are very effective for image classification tasks.",
    "Transformers use self-attention to process sequential data in parallel.",

    # Health
    "Regular aerobic exercise improves cardiovascular health and reduces stress.",
    "A balanced diet rich in vegetables and protein supports immune function.",
    "Adequate sleep of 7-9 hours per night is critical for cognitive performance.",

    # Business
    "Customer retention is often more cost-effective than acquiring new customers.",
]

# ─────────────────────────────────────────────
# STEP 1: Build the search index
# Embed all documents and store them
# ─────────────────────────────────────────────

model = SentenceTransformer("all-MiniLM-L6-v2")

print("Embedding documents...")
doc_embeddings = model.encode(documents, show_progress_bar=False)
print(f"Index ready: {len(documents)} documents, {doc_embeddings.shape[1]} dimensions each")


# ─────────────────────────────────────────────
# STEP 2: Cosine similarity function
# ─────────────────────────────────────────────

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


# ─────────────────────────────────────────────
# STEP 3: Semantic search function
# Embed query, compare to all docs, return top-K
# ─────────────────────────────────────────────

def semantic_search(query: str, top_k: int = 3) -> list[dict]:
    """Search documents by semantic similarity."""
    query_embedding = model.encode([query])[0]

    scores = [cosine_similarity(query_embedding, doc_emb) for doc_emb in doc_embeddings]
    ranked_indices = np.argsort(scores)[::-1][:top_k]

    return [
        {"rank": i+1, "score": scores[idx], "document": documents[idx]}
        for i, idx in enumerate(ranked_indices)
    ]


# ─────────────────────────────────────────────
# STEP 4: BM25 keyword search (simple implementation)
# ─────────────────────────────────────────────

def simple_keyword_score(query: str, document: str) -> float:
    """Simple keyword overlap score (TF-based)."""
    query_words = set(query.lower().split())
    doc_words = document.lower().split()

    if not query_words:
        return 0.0

    matches = sum(1 for word in doc_words if word in query_words)
    return matches / (len(doc_words) ** 0.5)  # length normalization


def keyword_search(query: str, top_k: int = 3) -> list[dict]:
    """Search documents by keyword overlap."""
    scores = [simple_keyword_score(query, doc) for doc in documents]
    ranked_indices = np.argsort(scores)[::-1][:top_k]

    return [
        {"rank": i+1, "score": scores[idx], "document": documents[idx]}
        for i, idx in enumerate(ranked_indices)
    ]


# ─────────────────────────────────────────────
# STEP 5: Hybrid search with RRF fusion
# ─────────────────────────────────────────────

def reciprocal_rank_fusion(lists: list[list], k: int = 60) -> list[tuple]:
    """Combine multiple ranked lists using RRF scoring."""
    rrf_scores = {}

    for ranked_list in lists:
        for rank_position, item in enumerate(ranked_list):
            doc_idx = item["doc_idx"]
            rrf_scores[doc_idx] = rrf_scores.get(doc_idx, 0) + 1.0 / (k + rank_position + 1)

    return sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)


def hybrid_search(query: str, top_k: int = 3) -> list[dict]:
    """Combine semantic and keyword search with RRF fusion."""
    # Get all results from both methods
    query_embedding = model.encode([query])[0]
    semantic_scores = [cosine_similarity(query_embedding, d) for d in doc_embeddings]
    keyword_scores = [simple_keyword_score(query, doc) for doc in documents]

    # Convert to ranked lists with doc_idx
    semantic_ranked = [
        {"doc_idx": i, "score": s}
        for i, s in sorted(enumerate(semantic_scores), key=lambda x: x[1], reverse=True)
    ]
    keyword_ranked = [
        {"doc_idx": i, "score": s}
        for i, s in sorted(enumerate(keyword_scores), key=lambda x: x[1], reverse=True)
    ]

    # RRF fusion
    fused = reciprocal_rank_fusion([semantic_ranked, keyword_ranked])

    return [
        {"rank": i+1, "rrf_score": score, "document": documents[doc_idx]}
        for i, (doc_idx, score) in enumerate(fused[:top_k])
    ]


# ─────────────────────────────────────────────
# STEP 6: Run search queries
# ─────────────────────────────────────────────

def display_results(results: list[dict], method: str):
    print(f"\n  Method: {method}")
    for r in results:
        score_key = "score" if "score" in r else "rrf_score"
        print(f"  {r['rank']}. [{r[score_key]:.4f}] {r['document'][:70]}")


test_queries = [
    # Semantic wins — no keyword overlap
    "how do neural networks learn to improve?",
    # Keyword wins — exact technical terms
    "SQL database query",
    # Both methods useful
    "Python machine learning",
    # Cross-domain
    "staying healthy and productive",
]

print("\n" + "=" * 70)
print("SEARCH COMPARISON: Semantic vs Keyword vs Hybrid")
print("=" * 70)

for query in test_queries:
    print(f"\nQuery: '{query}'")
    display_results(semantic_search(query), "Semantic")
    display_results(keyword_search(query), "Keyword")
    display_results(hybrid_search(query), "Hybrid (RRF)")
    print("-" * 40)
```

**Key observations when you run this:**
- For "how do neural networks learn" — semantic finds ML docs despite no keyword overlap
- For "SQL database query" — keyword search wins with direct term matching
- For "staying healthy and productive" — hybrid blends exercise, diet, sleep, and customer retention results

**Install and run:**
```bash
pip install sentence-transformers numpy
python semantic_search.py
```

**Upgrading to production:**
- Replace the numpy cosine search with ChromaDB for scale
- Replace `simple_keyword_score` with `rank_bm25` library for proper BM25
- Add a cross-encoder re-ranker with `cross-encoder/ms-marco-MiniLM-L-6-v2`

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [05 Vector Databases](../05_Vector_Databases/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [07 Memory Systems](../07_Memory_Systems/Theory.md)
