# Project 1: Advanced RAG with Reranking

## Why This Project Matters

In 2023, a legal-tech startup deployed a RAG chatbot to answer questions from their corpus of 50,000 case files. It worked well enough in demos. Then a lawyer asked about a specific precedent case — and the bot confidently cited a document that didn't exist. The retrieval step had pulled semantically adjacent documents, not the actually relevant one. The fix wasn't a bigger model. It was better retrieval.

This project teaches you three techniques that separate production RAG from demo RAG:

1. **HyDE** — instead of embedding the user's question (which is short and semantically sparse), you generate a hypothetical answer first and embed *that*. This dramatically improves first-stage recall.
2. **Hybrid Search** — keyword-based BM25 finds exact term matches that semantic search misses. Combining both is nearly always better than either alone.
3. **Cross-Encoder Reranking** — your fast bi-encoder retrieves 20 candidates; a slower but more accurate cross-encoder rescores all 20 and keeps only the top 5. This is how serious search systems work.

Add RAGAS evaluation and you have a pipeline you can actually measure, improve, and defend to stakeholders.

---

## What You'll Build

A complete advanced RAG pipeline that accepts a natural language question and returns a grounded answer, measured across three RAGAS metrics.

**Pipeline flow:**
```
User question
    → HyDE: Generate hypothetical answer
    → Hybrid retrieval: BM25 + vector search on ChromaDB
    → Merge & deduplicate candidates (top 20)
    → Cross-encoder reranker → top 5
    → Claude claude-sonnet-4-6 answer generation
    → RAGAS evaluation (faithfulness, answer relevance, context recall)
```

**Deliverable:** A runnable Python script that queries a document corpus, returns an answer with cited sources, and prints RAGAS scores.

---

## Learning Objectives

By completing this project, you will:

- Implement HyDE from scratch using the Anthropic SDK
- Build a hybrid retriever combining BM25 (`rank_bm25`) with ChromaDB vector search
- Apply a `sentence-transformers` cross-encoder to rerank candidates
- Measure retrieval and generation quality using RAGAS
- Understand the trade-offs between recall and precision in multi-stage retrieval
- Read and apply theory from: Advanced RAG Techniques (Topic 6), RAG Evaluation/RAGAS (Topic 7)

---

## Topics Covered

| Advanced Path Topic | What You Apply Here |
|---|---|
| Topic 6 — Advanced RAG Techniques | HyDE, hybrid search, reranking |
| Topic 7 — RAG Evaluation (RAGAS) | Faithfulness, answer relevance, context recall |
| Topic 9 — Full RAG Pipeline | End-to-end pipeline assembly |

---

## Prerequisites

- Comfortable with basic RAG (chunking, embedding, ChromaDB, LLM call)
- Python intermediate level: classes, async basics, dataclasses
- Anthropic SDK installed and API key set
- Completed Intermediate Path or equivalent experience

---

## Difficulty

**3 / 5 — Medium**

The individual components are well-documented. The challenge is wiring them together correctly and understanding why each stage exists.

---

## Tools & Libraries

| Tool | Purpose |
|---|---|
| `anthropic` | LLM calls for HyDE generation and final answer |
| `chromadb` | Vector store for semantic retrieval |
| `rank_bm25` | BM25 keyword retrieval |
| `sentence-transformers` | Cross-encoder reranker (`cross-encoder/ms-marco-MiniLM-L-6-v2`) |
| `ragas` | Evaluation metrics |
| `langchain` | Document abstraction for RAGAS integration |
| `datasets` | Golden dataset for evaluation |

---

## Expected Output

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

## Extension Challenges

1. Add query rewriting as a fourth retrieval signal (alongside HyDE)
2. Implement RAPTOR-style recursive summarization for long documents
3. Add a semantic cache layer so repeated queries skip retrieval
4. Build a Streamlit UI showing which chunks contributed to the answer
5. Run RAGAS over a 50-question golden set and plot metric trends

---

## Theory Files to Read First

Before coding, read:
- `09_RAG_Systems/07_Advanced_RAG_Techniques/Theory.md`
- `09_RAG_Systems/07_Advanced_RAG_Techniques/Hybrid_Search.md`
- `09_RAG_Systems/07_Advanced_RAG_Techniques/Reranking.md`
- `09_RAG_Systems/08_RAG_Evaluation/Theory.md`
- `09_RAG_Systems/08_RAG_Evaluation/Metrics_Guide.md`
