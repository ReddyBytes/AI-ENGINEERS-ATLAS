# Project 11 — Advanced RAG with Reranking

## The Real-World Story

In 2023, a legal-tech startup deployed a RAG chatbot to answer questions from their corpus of 50,000 case files. It worked well enough in demos. Then a lawyer asked about a specific precedent case — and the bot confidently cited a document that didn't exist. The retrieval step had pulled semantically adjacent documents, not the actually relevant one. The fix wasn't a bigger model. It was better retrieval.

This project teaches you three techniques that separate production RAG from demo RAG:

1. **HyDE** — instead of embedding the user's question (which is short and semantically sparse), you generate a hypothetical answer first and embed that. This dramatically improves first-stage recall.
2. **Hybrid Search** — keyword-based BM25 finds exact term matches that semantic search misses. Combining both is nearly always better than either alone.
3. **Cross-Encoder Reranking** — your fast bi-encoder retrieves 20 candidates; a slower but more accurate cross-encoder rescores all 20 and keeps only the top 5. This is how serious search systems work.

Add RAGAS evaluation and you have a pipeline you can actually measure, improve, and defend to stakeholders.

---

## What You Build

A complete advanced RAG pipeline that accepts a natural language question and returns a grounded answer, measured across three RAGAS metrics.

Pipeline flow:
```
User question
    -> HyDE: Generate hypothetical answer
    -> Hybrid retrieval: BM25 + vector search on ChromaDB
    -> Merge and deduplicate candidates (top 20)
    -> Cross-encoder reranker -> top 5
    -> Claude answer generation
    -> RAGAS evaluation (faithfulness, answer relevance, context recall)
```

Deliverable: A runnable Python script that queries a document corpus, returns an answer with cited sources, and prints RAGAS scores.

---

## What Success Looks Like

```
Query: "What are the main risks of using LLMs in medical diagnosis?"

[HyDE] Generated hypothetical answer (128 tokens)
[BM25]    Retrieved 10 candidates
[Vector]  Retrieved 10 candidates
[Merged]  18 unique candidates after dedup
[Rerank]  Top 5 selected by cross-encoder

Answer:
LLMs in medical diagnosis carry three primary risks: (1) hallucination of
clinical facts not present in training data, (2) distributional shift between
training corpora and current medical guidelines, and (3) lack of causal
reasoning about patient-specific factors. [Sources: doc_042, doc_017, doc_089]

RAGAS Evaluation:
  Faithfulness:       0.91
  Answer Relevance:   0.88
  Context Recall:     0.84
  Overall:            0.88
```

---

## Concepts Covered

| Concept | What You Learn |
|---|---|
| HyDE | Hypothetical document embedding, vocabulary gap problem, when HyDE helps vs. hurts |
| Hybrid Search | BM25 tokenization, RRF fusion formula, keyword vs. semantic query types |
| Cross-Encoder Reranking | Bi-encoder vs. cross-encoder trade-offs, logit scoring, top-N selection |
| RAGAS Faithfulness | LLM-based claim grounding check |
| RAGAS Answer Relevance | Hypothetical question generation, embedding similarity |
| RAGAS Context Recall | Whether retrieved chunks cover the ground-truth answer |

---

## Prerequisites

- Comfortable with basic RAG (chunking, embedding, ChromaDB, LLM call)
- Python intermediate level: classes, dataclasses
- Anthropic SDK installed and API key set
- Completed Intermediate Path or equivalent experience

---

## Learning Format

**Difficulty:** Medium (3 / 5)

The individual components are well-documented. The challenge is wiring them together correctly and understanding why each stage exists.

**Theory files to read first:**
- `09_RAG_Systems/07_Advanced_RAG_Techniques/Theory.md`
- `09_RAG_Systems/08_RAG_Evaluation/Theory.md`

**Tools and libraries:**
| Tool | Purpose |
|---|---|
| `anthropic` | LLM calls for HyDE generation and final answer |
| `chromadb` | Vector store for semantic retrieval |
| `rank_bm25` | BM25 keyword retrieval |
| `sentence-transformers` | Cross-encoder reranker (`cross-encoder/ms-marco-MiniLM-L-6-v2`) |
| `ragas` | Evaluation metrics |
| `datasets` | Golden dataset for evaluation |

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| 01_MISSION.md | you are here |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design and component table |
| [03_GUIDE.md](./03_GUIDE.md) | Progressive build steps |
| [src/starter.py](./src/starter.py) | Runnable Python skeleton |
| [04_RECAP.md](./04_RECAP.md) | What you learned, extensions, job mapping |

⬅️ **Prev:** [10 — Production RAG System](../10_Production_RAG_System/01_MISSION.md)
➡️ **Next:** [12 — LangGraph Support Bot](../12_LangGraph_Support_Bot/01_MISSION.md)
