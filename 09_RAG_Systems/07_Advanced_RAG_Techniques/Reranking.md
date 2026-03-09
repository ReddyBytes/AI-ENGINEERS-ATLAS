# Reranking

Reranking is a second-pass relevance scoring step. After retrieving a large candidate set with fast ANN search, a cross-encoder model scores each (query, chunk) pair together and re-orders the results — putting the truly most relevant chunks at the top.

---

## Why Reranking

The retrieval bi-encoder is fast because it embeds query and documents independently. But it can't model the direct interaction between them. A chunk about "refund processing time" might score similarly to a chunk about "shipping time" for the query "how long until I get my money back?" — both are about timelines. The cross-encoder, seeing both together, knows only the refund chunk is actually relevant.

```
First pass (fast):   retrieve top-20 with ANN cosine similarity
Second pass (slow):  cross-encoder scores each of the 20 (query, chunk) pairs
Final:               keep the top-3 by cross-encoder score
```

You get the speed of ANN (searching millions of vectors) AND the accuracy of direct pair comparison — just applied to a small candidate set.

---

## Cross-Encoder vs Bi-Encoder

| | Bi-encoder (retrieval) | Cross-encoder (reranking) |
|---|---|---|
| Input | Embed query separately, embed doc separately | (query, doc) pair together |
| Output | Two vectors, compare with cosine | Single relevance score 0–1 |
| Speed | Milliseconds (pre-computed doc vectors) | ~10ms per pair |
| Accuracy | Good — misses direct query-doc interactions | Better — sees full pair context |
| Use case | First-pass retrieval over millions of docs | Reranking top-20 to top-3 |

---

## Implementation: sentence-transformers CrossEncoder

```python
# pip install sentence-transformers
from sentence_transformers import CrossEncoder

# Load reranking model
# Options: cross-encoder/ms-marco-MiniLM-L-6-v2 (fast)
#          cross-encoder/ms-marco-electra-base (more accurate, slower)
#          BAAI/bge-reranker-large (high quality)
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


def rerank(query: str, chunks: list[dict], top_k: int = 3) -> list[dict]:
    """
    Re-order chunks using a cross-encoder.
    Returns the top_k most relevant chunks.
    """
    if not chunks:
        return []

    # Build (query, chunk_text) pairs
    pairs = [(query, chunk["text"]) for chunk in chunks]

    # Score each pair
    scores = reranker.predict(pairs)

    # Sort chunks by score, descending
    scored_chunks = sorted(
        zip(scores, chunks),
        key=lambda x: x[0],
        reverse=True
    )

    # Return top_k with reranker score added to metadata
    result = []
    for score, chunk in scored_chunks[:top_k]:
        chunk = chunk.copy()
        chunk["rerank_score"] = round(float(score), 4)
        result.append(chunk)

    return result
```

---

## Full Pipeline: Retrieve + Rerank

```python
# Step 1: retrieve a larger candidate set
candidates = retrieve(query, top_k=20)  # cast a wide net

# Step 2: rerank to find the truly relevant ones
top_chunks = rerank(query, candidates, top_k=3)

# Step 3: use top_chunks for context assembly
prompt = assemble_prompt(question, top_chunks)
```

Retrieve 20, rerank, keep 3. The wider the initial retrieval, the more candidates the reranker has to work with — and the better the final top-3 will be.

---

## Reranking Model Options

| Model | Speed | Quality | Notes |
|---|---|---|---|
| `cross-encoder/ms-marco-MiniLM-L-6-v2` | Fast (~5ms/pair) | Good | Best for latency-sensitive apps |
| `cross-encoder/ms-marco-electra-base` | Medium (~15ms/pair) | Better | Good balance |
| `BAAI/bge-reranker-large` | Slow (~30ms/pair) | High | Best quality locally |
| Cohere Rerank API | ~200ms (API call) | High | No GPU needed, per-API-call cost |
| Voyage AI Rerank | ~200ms (API call) | High | Strong for RAG use cases |

For development: `ms-marco-MiniLM-L-6-v2` is fast and free. For production: measure quality difference, decide if Cohere/Voyage API is worth the cost.

---

## Measuring Reranking Improvement

Before adding reranking, measure its impact:

```python
# Test: does the correct answer move from #4 to #1 after reranking?

def measure_reranking_benefit(test_cases: list[dict], top_k: int = 10):
    """
    test_cases: [{"query": "...", "expected_chunk_id": "..."}]
    """
    before_mrr = []
    after_mrr = []

    for case in test_cases:
        candidates = retrieve(case["query"], top_k=top_k)
        reranked = rerank(case["query"], candidates, top_k=top_k)

        # Position before reranking
        before_ids = [c["id"] for c in candidates]
        after_ids = [c["id"] for c in reranked]

        expected = case["expected_chunk_id"]

        before_rank = before_ids.index(expected) + 1 if expected in before_ids else 999
        after_rank = after_ids.index(expected) + 1 if expected in after_ids else 999

        before_mrr.append(1 / before_rank)
        after_mrr.append(1 / after_rank)

    print(f"MRR before reranking: {sum(before_mrr) / len(before_mrr):.3f}")
    print(f"MRR after reranking:  {sum(after_mrr) / len(after_mrr):.3f}")
```

If MRR improves by >5%, reranking is worth the latency cost.

---

## When to Add Reranking

Add it when:
- Evaluation shows the correct chunk is often in the top-10 but not the top-3
- Your use case is quality-sensitive (medical, legal, policy)
- Latency budget allows +100–300ms
- You have diverse document types where a single embedding model doesn't rank well uniformly

Skip it when:
- Latency is critical (<100ms total)
- Your retrieval hit rate is already >90% at top-3
- Your knowledge base is small and homogeneous

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Hybrid_Search.md](./Hybrid_Search.md) | Hybrid search techniques |
| [📄 Query_Transformation.md](./Query_Transformation.md) | Query transformation strategies |
| 📄 **Reranking.md** | ← you are here |

⬅️ **Prev:** [06 Context Assembly](../06_Context_Assembly/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [08 RAG Evaluation](../08_RAG_Evaluation/Theory.md)
