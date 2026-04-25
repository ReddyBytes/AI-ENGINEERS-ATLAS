# Project 11 — Advanced RAG with Reranking: Recap

## What You Built

A multi-stage RAG pipeline that layers three retrieval improvements on top of a basic vector search baseline: HyDE closes the vocabulary gap between a short question and a full answer document; hybrid BM25+vector search combines exact-term matching with semantic similarity; cross-encoder reranking applies the most accurate relevance model only to the candidates that survived earlier stages. RAGAS evaluation provides objective measurement of all three stages simultaneously.

---

## Concepts Applied

| Concept | How You Applied It |
|---|---|
| HyDE | Generated hypothetical answers with Claude and used those as vector search queries instead of the raw question — improving recall on short or ambiguous queries |
| BM25 Keyword Search | Built a `BM25Okapi` index in parallel with ChromaDB; tokenized documents at index time; used original question for BM25 to preserve exact term matching |
| Reciprocal Rank Fusion | Combined two ranked lists into one with the formula `1/(k+rank)`, summing scores for documents appearing in both lists — no need to calibrate incompatible score scales |
| Cross-Encoder Reranking | Ran `cross-encoder/ms-marco-MiniLM-L-6-v2` on all ~20 candidate pairs (query, passage) to get joint attention relevance scores; kept only top 5 |
| RAGAS Faithfulness | Measured whether every claim in the generated answer is grounded in the retrieved context |
| RAGAS Answer Relevance | Measured whether the answer addresses the original question |
| RAGAS Context Recall | Measured whether the retrieved chunks cover the ground-truth answer |

---

## Extension Ideas

**1. Query rewriting as a fourth retrieval signal**
Before HyDE, add a query rewriting step that expands ambiguous questions into multiple sub-queries. Retrieve for each sub-query separately, then merge all results into the RRF pool. This catches cases where a user's phrasing misses key domain terms.

**2. RAPTOR-style recursive summarization**
For long documents, build a hierarchy: chunk the document, summarize clusters of chunks, embed the summaries. During retrieval, search at multiple levels of abstraction. Useful for technical specifications or books where the answer requires synthesizing multiple sections.

**3. Evaluation dashboard**
Use `pandas` and `matplotlib` to plot RAGAS metric trends across your 20 golden questions, identifying which question types perform worst. A score breakdown by question category (factual, conceptual, multi-hop) reveals which pipeline stage is the bottleneck.

---

## Job Mapping

| Role | How this project applies |
|---|---|
| ML Engineer | Builds and tunes multi-stage retrieval pipelines; measures each stage's contribution to end quality |
| Search Engineer | Implements hybrid BM25+vector retrieval with RRF; tunes k and top-N hyperparameters |
| AI Research Engineer | Applies and adapts academic techniques (HyDE, RRF, cross-encoders) to practical pipelines |
| LLM Evaluation Engineer | Designs golden datasets; runs RAGAS; interprets faithfulness and recall scores to guide improvements |
| Backend Engineer | Integrates a ChromaDB vector store with a BM25 index and a cross-encoder model into a single production-ready query handler |

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [01_MISSION.md](./01_MISSION.md) | Project context and motivation |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design and component table |
| [03_GUIDE.md](./03_GUIDE.md) | Progressive build steps |
| [src/starter.py](./src/starter.py) | Runnable Python skeleton |
| 04_RECAP.md | you are here |

⬅️ **Prev:** [10 — Production RAG System](../10_Production_RAG_System/01_MISSION.md)
➡️ **Next:** [12 — LangGraph Support Bot](../12_LangGraph_Support_Bot/01_MISSION.md)
