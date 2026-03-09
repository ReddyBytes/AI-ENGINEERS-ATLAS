# Advanced RAG Techniques — Cheatsheet

**One-liner:** Advanced RAG improves retrieval quality by transforming the query before search, combining semantic + keyword search, and reranking results with a more accurate model after initial retrieval.

---

## Key Terms

| Term | What it means |
|---|---|
| **Hybrid search** | Combining semantic vector search with keyword (BM25) search |
| **BM25** | A classic keyword ranking algorithm — good at exact term matching |
| **RRF (Reciprocal Rank Fusion)** | Formula for combining ranked lists from different search methods |
| **Reranking** | Using a cross-encoder to re-score the top retrieved chunks for accuracy |
| **Cross-encoder** | A model that scores (query, document) pairs together — more accurate but slower |
| **Bi-encoder** | An embedding model that encodes query and document separately — fast but less precise |
| **Query rewriting** | Using an LLM to reformulate the user's question before retrieval |
| **Multi-query** | Generating multiple question variants and merging their retrieval results |
| **HyDE** | Hypothetical Document Embeddings — generate a fake answer, embed it, search |

---

## The Three Levers

```
Before retrieval:  Query Transformation (rewrite, multi-query, HyDE)
During retrieval:  Hybrid Search (semantic + BM25 + RRF)
After retrieval:   Reranking (cross-encoder re-scoring of top-N candidates)
```

---

## Hybrid Search: RRF Formula

```python
def rrf_score(rank, k=60):
    return 1 / (k + rank)

# Combine semantic and keyword ranked lists
combined = {}
for rank, chunk_id in enumerate(semantic_results):
    combined[chunk_id] = combined.get(chunk_id, 0) + rrf_score(rank)
for rank, chunk_id in enumerate(keyword_results):
    combined[chunk_id] = combined.get(chunk_id, 0) + rrf_score(rank)

# Sort by combined score, descending
reranked = sorted(combined.items(), key=lambda x: x[1], reverse=True)
```

k=60 is the standard default. Rarely needs tuning.

---

## Reranking Pipeline

```
1. Retrieve top-20 candidates with fast ANN search
2. Pass each (query, chunk) pair to cross-encoder
3. Cross-encoder outputs a relevance score per pair
4. Sort by cross-encoder score
5. Keep top-3 for context assembly
```

```python
from sentence_transformers import CrossEncoder

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
pairs = [(query, chunk["text"]) for chunk in candidates]
scores = reranker.predict(pairs)
reranked = sorted(zip(scores, candidates), reverse=True)
top_3 = [chunk for _, chunk in reranked[:3]]
```

---

## Query Transformation Patterns

| Technique | When to use | Latency cost |
|---|---|---|
| Query rewriting | User asks a vague 2-word question | +1 LLM call (~500ms) |
| Multi-query (3 variants) | Complex questions with multiple angles | +1 LLM call + 3x retrieval |
| HyDE | Abstract/conceptual questions; factual knowledge base | +1 LLM call |

```python
# Multi-query pattern
def multi_query_retrieve(question, n_variants=3):
    variants = llm_generate_variants(question, n=n_variants)
    all_chunks = []
    seen_ids = set()
    for q in [question] + variants:
        for chunk in retrieve(q, top_k=5):
            if chunk["id"] not in seen_ids:
                all_chunks.append(chunk)
                seen_ids.add(chunk["id"])
    return all_chunks
```

---

## When to Use Each Technique

| Your problem | Solution |
|---|---|
| Exact terms (names, codes) not found | Add BM25 hybrid search |
| Top retrieved chunk is #3 or #4, not #1 | Add reranking |
| User questions are short or vague | Add query rewriting |
| One question has multiple angles | Add multi-query |
| Questions are abstract, documents are concrete | Add HyDE |
| Latency is critical (<200ms) | Skip all transformations, optimize chunking |

---

## Latency Cost Summary

| Technique | Added latency | Worth it? |
|---|---|---|
| Hybrid search (BM25) | +20–50ms | Almost always yes |
| Reranking (local model) | +100–300ms | Yes for quality-sensitive apps |
| Reranking (API, e.g. Cohere) | +200–500ms | Yes if API budget allows |
| Query rewriting (LLM call) | +500–1000ms | Only if vague queries are common |
| Multi-query (3 variants) | +500ms + 3x retrieve | Only if coverage gaps are significant |

---

## Golden Rules

1. **Fix retrieval before adding complexity** — hybrid search + reranking fix 80% of retrieval failures.
2. **Retrieve more candidates than you keep** — retrieve top-20, rerank, keep top-3.
3. **Deduplicate after multi-query** — use chunk IDs to avoid passing the same chunk twice.
4. **RRF k=60 is the standard** — don't tune this unless you have strong evidence to do so.
5. **Cross-encoders are too slow for first-pass retrieval** — use them only for reranking a small candidate set.
6. **HyDE works best when questions are abstract** — less useful when questions are already specific.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Hybrid_Search.md](./Hybrid_Search.md) | Hybrid search techniques |
| [📄 Query_Transformation.md](./Query_Transformation.md) | Query transformation strategies |
| [📄 Reranking.md](./Reranking.md) | Reranking approaches |

⬅️ **Prev:** [06 Context Assembly](../06_Context_Assembly/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [08 RAG Evaluation](../08_RAG_Evaluation/Theory.md)
