# Advanced RAG Techniques — Theory

You build a RAG system. It works pretty well. But sometimes it gives wrong answers — the right chunk was in the database, but retrieval didn't find it. Or the user's question was vague, so the embedding matched a chunk that sort of answered it, but not the right one.

Basic RAG retrieves top-K chunks and passes them in. Advanced RAG asks: what if we improve the question before searching? What if we verify the ranking after searching?

👉 This is why we need **Advanced RAG Techniques** — because basic retrieval fails in predictable ways, and there are specific tools to fix each failure mode.

---

## The Three Levers

```mermaid
flowchart LR
    A[User Question] --> B[Query Transformation]
    B --> C[Retrieval]
    C --> D[Reranking]
    D --> E[Context Assembly]
    E --> F[LLM Answer]

    style B fill:#ffd700
    style D fill:#ffd700
```

1. **Before retrieval** — Query Transformation: rewrite, expand, or decompose the question.
2. **During retrieval** — Hybrid Search: combine semantic vectors with keyword search.
3. **After retrieval** — Reranking: use a slower, more accurate model to re-order results.

---

## 📌 Learning Priority

**Must Learn** — core concepts, needed to understand the rest of this file:
[The Three Levers](#the-three-levers) · [Hybrid Search](#hybrid-search) · [Reranking](#reranking)

**Should Learn** — important for real projects and interviews:
[Query Transformation](#query-transformation) · [When to Use Each](#when-to-use-each-technique)

**Good to Know** — useful in specific situations, not needed daily:
[HyDE Technique](#query-transformation)

---

## Hybrid Search

Pure semantic search misses exact keyword matches. Pure keyword search misses paraphrasing. Hybrid uses both.

| Search type | Finds | Misses |
|---|---|---|
| Semantic (vector) | "refund timeline" when document says "return window" | Exact product codes, names, IDs |
| Keyword (BM25) | "API-2847" exact match | Paraphrased questions |
| Hybrid | Both of the above | Less than either alone |

Scores are fused using **Reciprocal Rank Fusion (RRF)**:

```python
score = sum(1 / (k + rank) for rank in ranks)
# k=60 is standard. rank=1 (top result) → 1/61 ≈ 0.016
```

A chunk ranked #1 in both searches gets the highest combined score. A chunk appearing in only one list still gets partial credit.

---

## Reranking

First-pass retrieval uses fast approximate search (ANN). Reranking uses a slower, more accurate model to re-score the top results.

```mermaid
flowchart LR
    A[Query] --> B[Fast ANN\ntop-20 chunks]
    B --> C[Cross-encoder\nreranker]
    C --> D[Top-3 reranked\nchunks]
    D --> E[LLM]
```

- **Bi-encoder** (retrieval): embeds query and document separately. Fast, but loses the direct comparison.
- **Cross-encoder** (reranking): takes (query, document) as a pair, sees both simultaneously. More accurate, too slow for 10,000 chunks.

Pattern: retrieve 20 candidates fast → rerank to top 3 accurately. You get both speed and accuracy.

Popular reranking models: `cross-encoder/ms-marco-MiniLM-L-6-v2` (fast), `cohere-rerank-3`, `bge-reranker-large` (high accuracy).

---

## Query Transformation

A user types a short, vague question. The embedding doesn't match the detailed document that answers it. Three fixes:

**1. Query expansion / rewriting** — rewrite into a more detailed, retrieval-friendly form:
```
User: "return policy?"
Rewritten: "What is the product return policy, including the time window for returns and the refund process?"
```

**2. Multi-query** — generate N variations, retrieve for each, merge and deduplicate:
```
Original: "How do I get a refund?"
Variant 1: "What is the refund process?"
Variant 2: "How long does a refund take?"
Variant 3: "What steps do I follow to return a product for a refund?"
→ retrieve for all 3, merge, deduplicate → better coverage
```

**3. HyDE (Hypothetical Document Embeddings)** — ask the LLM to write a hypothetical document that would answer the question, then embed that document for retrieval:
```
Question: "What is the return window for electronics?"
→ LLM generates: "Electronics can be returned within 30 days of purchase..."
→ Embed the hypothetical doc and search
→ The hypothetical doc's embedding is closer to actual policy chunks than the short question
```

---

## When to Use Each Technique

| Technique | Use when... |
|---|---|
| Hybrid search | Queries mix natural language and specific terms (names, codes, dates) |
| Reranking | You can afford +100–300ms latency; quality matters more than speed |
| Query rewriting | Users ask short/vague questions; your knowledge base is detailed |
| Multi-query | Single questions can have multiple valid search angles |
| HyDE | Queries are abstract questions; documents are factual statements |

---

✅ **What you just learned:** Advanced RAG improves on basic RAG at three points — query transformation rewrites the question before retrieval, hybrid search combines semantic + keyword retrieval, and reranking uses a more accurate model to re-order results before passing them to the LLM.

🔨 **Build this now:** Take your basic RAG pipeline. Add a reranker using `sentence-transformers` with `cross-encoder/ms-marco-MiniLM-L-6-v2`. Retrieve top-10 with ANN, rerank, keep top-3. Measure whether answer quality improves on your test questions.

➡️ **Next step:** RAG Evaluation → `09_RAG_Systems/08_RAG_Evaluation/Theory.md`

---

## 🛠️ Practice Project

Apply what you just learned → **[A1: Advanced RAG with Reranking](../../22_Capstone_Projects/11_Advanced_RAG_with_Reranking/03_GUIDE.md)**
> This project uses: HyDE (generate fake answer → embed → retrieve), hybrid BM25+vector search, cross-encoder reranking top-20 → top-5


---

## 📝 Practice Questions

- 📝 [Q59 · advanced-rag](../../ai_practice_questions_100.md#q59--interview--advanced-rag)


---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| 📄 **Theory.md** | ← you are here |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Hybrid_Search.md](./Hybrid_Search.md) | Hybrid search techniques |
| [📄 Query_Transformation.md](./Query_Transformation.md) | Query transformation strategies |
| [📄 Reranking.md](./Reranking.md) | Reranking approaches |

⬅️ **Prev:** [06 Context Assembly](../06_Context_Assembly/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [08 RAG Evaluation](../08_RAG_Evaluation/Theory.md)
