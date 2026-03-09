# RAG Evaluation — Metrics Guide

Complete reference for all RAG evaluation metrics: what they measure, how to compute them, and what scores to target.

---

## Metric Summary Table

| Metric | Stage | Measures | Needs ground truth? | Range |
|---|---|---|---|---|
| Hit Rate @ K | Retrieval | Correct chunk in top-K | Yes (chunk ID) | 0–1 |
| MRR | Retrieval | How early the correct chunk appears | Yes (chunk ID) | 0–1 |
| NDCG | Retrieval | Graded relevance at each position | Yes (relevance labels) | 0–1 |
| Context Precision | Retrieval | Fraction of retrieved chunks that are useful | Yes (relevance labels) | 0–1 |
| Context Recall | Retrieval | Fraction of needed info that was retrieved | Yes (ground truth answer) | 0–1 |
| Faithfulness | Generation | Claims supported by context | No (LLM judge) | 0–1 |
| Answer Relevancy | Generation | Answer addresses the question | No (LLM judge) | 0–1 |
| Answer Correctness | End-to-end | Answer matches ground truth | Yes (expected answer) | 0–1 |

---

## Retrieval Metrics

### Hit Rate @ K

The simplest retrieval metric. What fraction of test questions had the expected chunk appear in the top-K results?

```python
def hit_rate_at_k(retrieved_ids: list[str], expected_id: str, k: int) -> float:
    return 1.0 if expected_id in retrieved_ids[:k] else 0.0

# Compute across test set
scores = [hit_rate_at_k(r, e, k=3) for r, e in zip(all_retrieved, all_expected)]
hit_rate = sum(scores) / len(scores)
```

**Target**: > 0.85 at K=3 for a well-functioning system.
**If low**: check chunk overlap with expected, try increasing K, improve embeddings, add hybrid search.

---

### Mean Reciprocal Rank (MRR)

MRR rewards finding the correct chunk early. Being at rank 1 is worth `1/1 = 1.0`. Being at rank 2 is worth `1/2 = 0.5`. Rank 10 is worth `1/10 = 0.1`.

```python
def reciprocal_rank(retrieved_ids: list[str], expected_id: str) -> float:
    if expected_id in retrieved_ids:
        rank = retrieved_ids.index(expected_id) + 1  # 1-indexed
        return 1.0 / rank
    return 0.0

mrr = sum(reciprocal_rank(r, e) for r, e in zip(all_retrieved, all_expected)) / len(all_retrieved)
```

**Target**: MRR > 0.8 means the correct chunk is typically in the top 1–2 results.
**Interpret**: MRR = 0.5 means the correct chunk is on average at rank 2. MRR = 0.33 means rank 3.

---

### Context Precision

What fraction of the retrieved chunks actually contain relevant information?

```python
def context_precision(retrieved_chunks: list[dict], ground_truth_answer: str, judge_llm) -> float:
    """For each retrieved chunk, judge whether it's relevant."""
    relevant_count = 0
    for chunk in retrieved_chunks:
        judge_prompt = f"""Is this document chunk relevant to answering the question?
Ground truth answer: {ground_truth_answer}
Chunk: {chunk['text']}
Answer YES or NO."""
        if "YES" in judge_llm.complete(judge_prompt).upper():
            relevant_count += 1
    return relevant_count / len(retrieved_chunks)
```

**Target**: > 0.8
**If low**: reduce K, raise similarity threshold, improve chunk metadata for filtering.

---

### Context Recall

What fraction of the information needed for the correct answer was actually retrieved?

```python
def context_recall(retrieved_chunks: list[dict], expected_answer: str, judge_llm) -> float:
    """Decompose expected answer into claims, check which are in the retrieved context."""
    decompose_prompt = f"""Break this answer into individual factual claims, one per line:
Answer: {expected_answer}"""
    claims = judge_llm.complete(decompose_prompt).strip().split("\n")

    context_text = "\n\n".join(c["text"] for c in retrieved_chunks)

    found_count = 0
    for claim in claims:
        check_prompt = f"""Is this claim supported by the following context?
Claim: {claim}
Context: {context_text}
Answer YES or NO."""
        if "YES" in judge_llm.complete(check_prompt).upper():
            found_count += 1

    return found_count / len(claims) if claims else 0.0
```

**Target**: > 0.85
**If low**: increase K, improve chunking (chunks may be too small), add hybrid search.

---

## Generation Metrics

### Faithfulness

Are all claims in the generated answer supported by the retrieved context?

```python
def faithfulness(question: str, context: str, answer: str, judge_llm) -> dict:
    # Step 1: extract claims from the answer
    claim_prompt = f"""Extract all factual claims from this answer as a list, one per line:
Answer: {answer}"""
    claims = judge_llm.complete(claim_prompt).strip().split("\n")

    # Step 2: check each claim against context
    supported = 0
    for claim in claims:
        check_prompt = f"""Is this claim directly supported by the following context?
Claim: {claim}
Context: {context}
Answer YES or NO."""
        if "YES" in judge_llm.complete(check_prompt).upper():
            supported += 1

    score = supported / len(claims) if claims else 0.0
    return {"score": score, "total_claims": len(claims), "supported_claims": supported}
```

**Target**: > 0.85 for production systems. Higher for high-stakes domains.
**If low**: add "ONLY use context" instruction to prompt, use temperature=0, check if model is being asked questions it can't answer from context.

---

### Answer Relevancy

Does the generated answer actually address the question that was asked?

```python
import numpy as np

def cosine_similarity(v1: list, v2: list) -> float:
    a, b = np.array(v1), np.array(v2)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def answer_relevancy(question: str, answer: str, embed_fn, judge_llm, n_variants: int = 3) -> float:
    """Generate reverse questions from answer, measure similarity to original question."""
    gen_prompt = f"""Generate {n_variants} questions that this answer would be a response to.
Answer: {answer}
Return one question per line."""
    generated_qs = judge_llm.complete(gen_prompt).strip().split("\n")[:n_variants]

    # Embed original question and generated questions
    all_questions = [question] + generated_qs
    embeddings = embed_fn(all_questions)

    original_emb = embeddings[0]
    similarities = [cosine_similarity(original_emb, emb) for emb in embeddings[1:]]

    return sum(similarities) / len(similarities)
```

**Target**: > 0.85
**If low**: check if the system prompt is causing the LLM to go off-topic, or if the retrieved context is pulling the answer in a wrong direction.

---

### Answer Correctness (End-to-End)

Combines semantic similarity with factual overlap between the generated answer and ground truth.

```python
def answer_correctness(expected: str, generated: str, embed_fn, judge_llm) -> dict:
    # Semantic similarity
    embs = embed_fn([expected, generated])
    semantic_sim = cosine_similarity(embs[0], embs[1])

    # Factual overlap (F1 over extracted claims)
    expected_claims = set(extract_claims(expected, judge_llm))
    generated_claims = set(extract_claims(generated, judge_llm))

    tp = len(expected_claims & generated_claims)
    precision = tp / len(generated_claims) if generated_claims else 0
    recall = tp / len(expected_claims) if expected_claims else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    # Combined score
    combined = 0.5 * semantic_sim + 0.5 * f1

    return {
        "score": combined,
        "semantic_similarity": semantic_sim,
        "factual_f1": f1
    }
```

**Target**: > 0.75 combined score.

---

## Diagnostic Decision Tree

```
Start: what is failing?

Is context recall < 0.7?
  → Retrieval is missing relevant chunks
  → Try: increase K, better embeddings, hybrid search, larger chunks

Is context precision < 0.7?
  → Too many irrelevant chunks retrieved
  → Try: reduce K, raise similarity threshold, metadata filtering

Is faithfulness < 0.8?
  → LLM is adding information not in context
  → Try: stronger grounding instruction, temperature=0, check if question is out-of-scope

Is answer relevancy < 0.8?
  → LLM is going off-topic
  → Try: clearer question instruction, check if context is pulling in wrong direction

Is answer correctness < 0.7 but other metrics are fine?
  → Knowledge base may be missing information
  → Try: add more documents, improve chunking of existing documents
```

---

## Minimum Evaluation Setup

For a new RAG system, the minimum viable evaluation:

```python
# 1. Create 20 test questions with expected chunk IDs
test_set = [...]

# 2. Run retrieval for each question
results = [(retrieve(q["question"], top_k=3), q["expected_chunk_id"]) for q in test_set]

# 3. Compute hit rate @ 3
hit_rate = sum(hit_rate_at_k(r, e, k=3) for r, e in results) / len(results)
print(f"Hit rate @ 3: {hit_rate:.2f}")

# 4. If hit rate > 0.8, then evaluate faithfulness on a sample
if hit_rate > 0.8:
    sample = random.sample(test_set, 10)
    faithfulness_scores = [evaluate_faithfulness(q, ...) for q in sample]
    print(f"Faithfulness: {sum(faithfulness_scores)/len(faithfulness_scores):.2f}")
```

Start here. Add more sophisticated metrics only when you need to debug specific failure modes.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |
| 📄 **Metrics_Guide.md** | ← you are here |

⬅️ **Prev:** [07 Advanced RAG Techniques](../07_Advanced_RAG_Techniques/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [09 Build a RAG App](../09_Build_a_RAG_App/Project_Guide.md)
