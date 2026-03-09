# RAG Evaluation — Cheatsheet

**One-liner:** Evaluate RAG systems by measuring retrieval quality (did we find the right chunks?) and generation quality (did the LLM stay faithful to the context and answer the question?) separately using a test set of (question, expected answer) pairs.

---

## Key Terms

| Term | What it means |
|---|---|
| **RAGAS** | The standard RAG evaluation framework with 4 core metrics |
| **Faithfulness** | Does the answer contain only claims supported by the retrieved context? |
| **Answer Relevancy** | Does the answer actually address the question asked? |
| **Context Precision** | What fraction of retrieved chunks were actually useful? |
| **Context Recall** | Did retrieval find all the information needed to answer correctly? |
| **Hit rate @ K** | What fraction of questions had the correct chunk in the top-K results? |
| **MRR** | Mean Reciprocal Rank — average of 1/rank for the correct chunk |
| **LLM-as-judge** | Using an LLM to evaluate the quality of another LLM's answer |
| **Ground truth** | The correct expected answer for a test question |

---

## The Four RAGAS Metrics

| Metric | What it measures | Formula |
|---|---|---|
| Faithfulness | Claims in answer supported by context | supported claims / total claims |
| Answer Relevancy | How well the answer addresses the question | cosine similarity of reverse-engineered questions to original |
| Context Precision | Fraction of retrieved chunks that are relevant | relevant chunks / total retrieved chunks |
| Context Recall | Fraction of needed information that was retrieved | info found / info needed |

---

## Retrieval-Only Metrics

```python
# Hit rate @ K
def hit_rate(retrieved_ids, expected_id, k=3):
    return int(expected_id in retrieved_ids[:k])

# Mean Reciprocal Rank
def mrr(retrieved_ids, expected_id):
    if expected_id in retrieved_ids:
        return 1 / (retrieved_ids.index(expected_id) + 1)
    return 0.0

# Average across test set
hit_rate_score = sum(hit_rate(r, e) for r, e in cases) / len(cases)
mrr_score = sum(mrr(r, e) for r, e in cases) / len(cases)
```

---

## Benchmark Targets

| Metric | Needs work | Acceptable | Good |
|---|---|---|---|
| Faithfulness | < 0.7 | 0.7–0.85 | > 0.85 |
| Answer Relevancy | < 0.7 | 0.7–0.85 | > 0.85 |
| Context Precision | < 0.6 | 0.6–0.8 | > 0.8 |
| Context Recall | < 0.7 | 0.7–0.85 | > 0.85 |
| Hit Rate @ 3 | < 0.7 | 0.7–0.85 | > 0.85 |

---

## Diagnosis Guide

| Low score | Root cause | Fix |
|---|---|---|
| Low context recall | Right chunks not retrieved | Improve retrieval (K, embeddings, hybrid) |
| Low context precision | Too many irrelevant chunks retrieved | Reduce K, add similarity threshold |
| Low faithfulness | LLM hallucinating | Stronger grounding prompt, temperature=0 |
| Low answer relevancy | LLM going off-topic | Clearer question instruction in prompt |

Fix retrieval before generation. Generation quality is bounded by retrieval quality.

---

## Creating a Test Set

| Method | Quality | Scale | Cost |
|---|---|---|---|
| Manual expert | Highest | 20–50 Q&As | High |
| LLM-generated from docs | Good | 100–500 Q&As | Low |
| Production query logs | Most realistic | Unlimited | Medium (labeling) |

Minimum viable test set: **20 questions** across all major topics in your knowledge base.

---

## LLM-as-Judge Pattern

```python
judge_prompt = """Rate the following RAG answer on faithfulness (0-1).
Faithfulness = every claim in the answer can be verified from the context.

Context: {context}
Answer: {answer}

Return JSON: {"score": 0.0-1.0, "reason": "..."}"""
```

---

## When to Evaluate

| Trigger | What to measure |
|---|---|
| Before launching | Full RAGAS benchmark |
| After changing chunk size | Context recall + faithfulness |
| After changing embedding model | All retrieval metrics |
| After changing prompt | Faithfulness + answer relevancy |
| After adding new documents | Hit rate on new-document questions |
| Production monitoring | Faithfulness on sampled live queries |

---

## Golden Rules

1. **Separate retrieval from generation** — measure each independently to know what to fix.
2. **Fix retrieval first** — if retrieval is failing, generation improvements are wasted.
3. **20 questions minimum** — fewer than that and variance dominates.
4. **LLM-as-judge scales evaluation** — you can't manually review thousands of answers.
5. **Establish a baseline before optimizing** — you can't know if a change helped without a before/after score.
6. **Include edge cases** — out-of-scope questions, ambiguous queries, multi-part questions.
7. **Track scores over time** — evaluation is not a one-time thing; it's a continuous process.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |
| [📄 Metrics_Guide.md](./Metrics_Guide.md) | RAG evaluation metrics guide |

⬅️ **Prev:** [07 Advanced RAG Techniques](../07_Advanced_RAG_Techniques/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [09 Build a RAG App](../09_Build_a_RAG_App/Project_Guide.md)
