# Hybrid Search

Hybrid search combines semantic vector search with keyword-based search (BM25) to get the strengths of both and compensate for each method's weaknesses.

---

## Why Hybrid Search

| Scenario | Semantic only | BM25 only | Hybrid |
|---|---|---|---|
| "How do I return a product?" | Finds "refund policy" | Only if those exact words appear | Both |
| "Error code API-2847" | May miss exact code | Exact match | Both |
| "v2.3.1 release notes" | May miss version string | Exact match | Both |
| "What is the company's data retention policy?" | Finds semantically similar docs | Depends on keyword overlap | Both |

The pattern: semantic search handles natural language and paraphrasing. BM25 handles specific terms, codes, names, and version numbers that don't paraphrase well.

---

## BM25: How It Works

BM25 (Best Match 25) is a probabilistic ranking algorithm. For a given query and document:

- Count how many query terms appear in the document
- Weight rare terms higher (IDF — Inverse Document Frequency): "the" scores low, "API-2847" scores high
- Normalize for document length (a short document that mentions "refund" once ranks higher than a long document that mentions it once)

```python
# pip install rank-bm25
from rank_bm25 import BM25Okapi

# Build index at startup
corpus_tokens = [doc.lower().split() for doc in document_texts]
bm25 = BM25Okapi(corpus_tokens)

# Search
query_tokens = "how do I return a product".split()
scores = bm25.get_scores(query_tokens)
top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:10]
```

BM25 is fast (CPU, no GPU needed), runs in-memory, and has no model to load. Add it alongside your vector DB.

---

## Reciprocal Rank Fusion (RRF)

RRF merges ranked result lists without worrying about their different score scales. It only uses the rank position:

```python
def reciprocal_rank_fusion(ranked_lists: list[list[str]], k: int = 60) -> dict[str, float]:
    """
    ranked_lists: each list is a list of chunk IDs ordered by relevance
    Returns: dict of chunk_id -> combined RRF score
    """
    scores = {}
    for ranked_list in ranked_lists:
        for rank, chunk_id in enumerate(ranked_list):
            if chunk_id not in scores:
                scores[chunk_id] = 0
            scores[chunk_id] += 1 / (k + rank + 1)  # +1 because rank is 0-indexed
    return scores


def hybrid_retrieve(query: str, semantic_ids: list[str], bm25_ids: list[str], top_k: int = 5):
    rrf_scores = reciprocal_rank_fusion([semantic_ids, bm25_ids])
    sorted_ids = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
    return [chunk_id for chunk_id, _ in sorted_ids[:top_k]]
```

Why k=60? The constant prevents a rank-1 result from completely dominating. With k=60, rank 1 gives `1/61 ≈ 0.016` and rank 10 gives `1/70 ≈ 0.014`. The gap is small, so a result that appears in both lists (both methods agree) consistently beats a result that appears in only one.

---

## Full Hybrid Retrieval Example

```python
# pip install chromadb sentence-transformers rank-bm25
import chromadb
from chromadb.utils import embedding_functions
from rank_bm25 import BM25Okapi

# ─────────────────────────────────────────────
# SETUP
# ─────────────────────────────────────────────

# Load all documents for BM25
# (In production, load these from your database)
documents = [
    {"id": "doc_1", "text": "All product returns must be initiated within 30 days of purchase."},
    {"id": "doc_2", "text": "Contact our support team at support@company.com or call 1-800-555-0100."},
    {"id": "doc_3", "text": "The API-2847 error indicates a malformed authentication token."},
    # ... more documents
]

# BM25 index (keyword search)
corpus_tokens = [doc["text"].lower().split() for doc in documents]
bm25 = BM25Okapi(corpus_tokens)
doc_ids = [doc["id"] for doc in documents]

# Vector index (semantic search)
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
client = chromadb.PersistentClient(path="./rag_index")
collection = client.get_or_create_collection("docs", embedding_function=embedding_fn)


# ─────────────────────────────────────────────
# HYBRID RETRIEVAL FUNCTION
# ─────────────────────────────────────────────

def hybrid_retrieve(query: str, top_k: int = 5) -> list[str]:
    """Return top_k chunk IDs using RRF over semantic + BM25 results."""
    candidate_pool = top_k * 4  # retrieve more candidates before merging

    # 1. Semantic search → ranked IDs
    semantic_results = collection.query(
        query_texts=[query], n_results=candidate_pool
    )
    semantic_ids = semantic_results["ids"][0]

    # 2. BM25 keyword search → ranked IDs
    query_tokens = query.lower().split()
    bm25_scores = bm25.get_scores(query_tokens)
    bm25_ranked_indices = sorted(
        range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True
    )[:candidate_pool]
    bm25_ids = [doc_ids[i] for i in bm25_ranked_indices]

    # 3. RRF fusion
    rrf_scores = {}
    k_rrf = 60
    for ranked_list in [semantic_ids, bm25_ids]:
        for rank, chunk_id in enumerate(ranked_list):
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0) + 1 / (k_rrf + rank + 1)

    # 4. Sort by combined score
    sorted_ids = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
    return [chunk_id for chunk_id, _ in sorted_ids[:top_k]]


# ─────────────────────────────────────────────
# TEST
# ─────────────────────────────────────────────

test_queries = [
    "how do I return a product",         # natural language → semantic wins
    "API-2847",                           # exact code → BM25 wins
    "contact email address support",      # both help
]

for q in test_queries:
    result_ids = hybrid_retrieve(q, top_k=3)
    print(f"\nQuery: '{q}'")
    print(f"Top results: {result_ids}")
```

---

## When to Add Hybrid Search

Add it when:
- Your knowledge base contains product codes, version numbers, error codes, names
- Users search for specific terms they expect exact matches on
- Pure semantic retrieval is missing obvious relevant documents

Skip it when:
- All queries are natural language questions with no specific terms
- Latency budget is very tight and semantic alone is sufficient
- Your knowledge base is small enough that all approaches work equally well

---

## Tuning BM25 + Semantic Balance

If you want to weight one method more heavily, multiply the RRF score:

```python
# Give semantic search 70% weight, keyword 30%
semantic_weight = 0.7
keyword_weight = 0.3

for rank, chunk_id in enumerate(semantic_ids):
    rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0) + semantic_weight / (k + rank + 1)
for rank, chunk_id in enumerate(bm25_ids):
    rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0) + keyword_weight / (k + rank + 1)
```

In practice: start with equal weights. Only tune if evaluation shows a clear direction.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Hybrid_Search.md** | ← you are here |
| [📄 Query_Transformation.md](./Query_Transformation.md) | Query transformation strategies |
| [📄 Reranking.md](./Reranking.md) | Reranking approaches |

⬅️ **Prev:** [06 Context Assembly](../06_Context_Assembly/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [08 RAG Evaluation](../08_RAG_Evaluation/Theory.md)
