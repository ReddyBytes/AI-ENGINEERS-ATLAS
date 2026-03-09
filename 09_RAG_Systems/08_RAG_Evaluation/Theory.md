# RAG Evaluation — Theory

You shipped a RAG system. Your manager asks: "Is it working?" You say "It seems pretty good." That's not an answer. Without measuring, you don't know if the system is 60% accurate or 90% accurate. You don't know if changing the chunk size helped or hurt. You can't make it better because you can't tell if your changes are improvements.

The same problem exists in every engineering discipline. You don't improve what you don't measure.

👉 This is why we need **RAG Evaluation** — to turn "it seems pretty good" into concrete scores you can track, compare, and improve.

---

## What Can Go Wrong in a RAG Pipeline

RAG has two separate stages, and each can fail independently:

```mermaid
flowchart LR
    A[Question] --> B[Retrieval]
    B --> C[Context Assembly]
    C --> D[Generation]
    D --> E[Answer]

    style B fill:#ff9999
    style D fill:#ff9999
```

**Retrieval failures:**
- The right chunk wasn't in the top-K results (low recall)
- Wrong chunks were retrieved (low precision)

**Generation failures:**
- The LLM made up facts not in the retrieved chunks (hallucination)
- The LLM ignored relevant information in the chunks
- The answer didn't address the actual question

You need metrics for both stages separately. A system with perfect retrieval but bad generation will fail. A system with great generation but missing key chunks will also fail.

---

## The Four Core RAGAS Metrics

RAGAS is the standard evaluation framework for RAG systems. It measures four things:

**1. Faithfulness** — Does the answer stick to the retrieved context?
- Question: Did the LLM invent facts?
- Checks: each claim in the answer → can it be traced to the context?
- Score: 0–1 (1 = every claim is grounded in context)

**2. Answer Relevancy** — Does the answer address the question?
- Question: Did the LLM go off-topic?
- Checks: does the answer actually answer what was asked?
- Score: 0–1 (1 = directly answers the question)

**3. Context Precision** — Were the right chunks retrieved?
- Question: Is the retrieved context actually useful?
- Checks: how many of the retrieved chunks contain relevant information?
- Score: 0–1 (1 = every retrieved chunk was relevant)

**4. Context Recall** — Did retrieval find everything it needed?
- Question: Were any necessary chunks missed?
- Checks: does the retrieved context contain all information needed for the correct answer?
- Score: 0–1 (1 = all necessary information was retrieved)

---

## The Evaluation Triangle

```mermaid
flowchart TD
    A[Test Set\nquestion + ground truth answer] --> B[Run RAG Pipeline]
    B --> C[Retrieved chunks]
    B --> D[Generated answer]
    C --> E[Context Precision\nContext Recall]
    D --> F[Faithfulness\nAnswer Relevancy]
```

You need a test set: a collection of (question, expected_answer) pairs. The expected answer is the "ground truth" — what the correct answer should be.

For each question in the test set, you run the full RAG pipeline and score the result on all four metrics. Then you average across all questions.

---

## How to Create a Test Set

Three approaches:

**1. Manual** — domain experts write questions and answers. Highest quality, expensive, slow.

**2. LLM-generated** — use an LLM to generate question/answer pairs from your documents:
```python
prompt = f"""Read this document excerpt and generate 3 question-answer pairs.
Each pair should test factual recall. Format: Q: / A: on separate lines.

Document: {chunk_text}"""
```

**3. Production logs** — collect real user questions from a deployed system. Manually label the correct answers. Most representative of actual usage.

Start with 20–50 high-quality manually written examples. Use LLM-generated pairs to scale to 200+.

---

## Retrieval-Only Metrics

For the retrieval stage specifically:

- **Hit rate @ K**: what fraction of questions had the correct chunk in the top-K results?
- **MRR (Mean Reciprocal Rank)**: average of `1/rank` for the correct chunk across all questions

```python
def mrr(retrieved_ids: list[str], expected_id: str) -> float:
    if expected_id in retrieved_ids:
        return 1 / (retrieved_ids.index(expected_id) + 1)
    return 0.0

# Average across your test set
mrr_score = sum(mrr(r, e) for r, e in test_cases) / len(test_cases)
```

Target: MRR > 0.8 means the correct chunk is typically in the top 1–2 results. Below 0.5 means retrieval is broken and must be fixed before improving generation.

---

## LLM-as-Judge Evaluation

For faithfulness and answer relevancy, you use an LLM to judge the quality of another LLM's answers. This is the standard approach in RAGAS.

```python
faithfulness_judge_prompt = """You are evaluating an AI assistant's answer.

Question: {question}
Context provided: {context}
Answer given: {answer}

Does the answer contain ONLY information that can be found in the context?
Are there any claims in the answer that are NOT supported by the context?

Score from 0 to 1, where 1 means every claim in the answer is grounded in the context.
Return: {{"score": 0.0-1.0, "reason": "brief explanation"}}"""
```

This scales to large test sets without needing human reviewers for every example.

---

## Benchmark Targets

| Metric | Needs work | Acceptable | Good |
|---|---|---|---|
| Faithfulness | < 0.7 | 0.7–0.85 | > 0.85 |
| Answer Relevancy | < 0.7 | 0.7–0.85 | > 0.85 |
| Context Precision | < 0.6 | 0.6–0.8 | > 0.8 |
| Context Recall | < 0.7 | 0.7–0.85 | > 0.85 |
| Hit Rate @ 3 | < 0.7 | 0.7–0.85 | > 0.85 |

These are rough guidelines. Set your own targets based on your use case — a medical information system needs higher faithfulness thresholds than a general FAQ bot.

---

✅ **What you just learned:** RAG evaluation measures retrieval quality (context precision/recall, hit rate) and generation quality (faithfulness, answer relevancy) separately using a test set of (question, expected answer) pairs. RAGAS is the standard framework; LLM-as-judge scales evaluation without human reviewers for every test case.

🔨 **Build this now:** Create a test set of 20 questions with expected answers for your RAG system. Compute hit rate @ 3 (does the correct chunk appear in the top-3 results?). If it's below 0.75, your retrieval needs work before improving generation.

➡️ **Next step:** Build a RAG App → `09_RAG_Systems/09_Build_a_RAG_App/Project_Guide.md`

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| 📄 **Theory.md** | ← you are here |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |
| [📄 Metrics_Guide.md](./Metrics_Guide.md) | RAG evaluation metrics guide |

⬅️ **Prev:** [07 Advanced RAG Techniques](../07_Advanced_RAG_Techniques/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [09 Build a RAG App](../09_Build_a_RAG_App/Project_Guide.md)
