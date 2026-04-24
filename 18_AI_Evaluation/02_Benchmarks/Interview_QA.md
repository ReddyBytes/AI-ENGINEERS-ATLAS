# Benchmarks — Interview Q&A

## Beginner Level

**Q1: What is MMLU and what does it measure?**

<details>
<summary>💡 Show Answer</summary>

**A:** MMLU (Massive Multitask Language Understanding) is a multiple-choice benchmark covering 57 academic subjects — from elementary school math to graduate-level law, medicine, chemistry, and philosophy. Each question has 4 answer choices. It measures a model's breadth of world knowledge and reasoning across diverse domains. Human experts score around 88%; random chance is 25%. It's the most widely used general capability benchmark for LLMs.

</details>

**Q2: What is HumanEval and how is it scored?**

<details>
<summary>💡 Show Answer</summary>

**A:** HumanEval is a code generation benchmark with 164 Python programming problems. Each problem provides a function signature and docstring; the model must generate working code. The metric is pass@1 — the percentage of problems where the first generated attempt passes all hidden unit tests. This makes it objectively measurable: code either passes tests or it doesn't. Top models score 85–92% pass@1.

</details>

**Q3: What does it mean when benchmarks become "saturated"?**

<details>
<summary>💡 Show Answer</summary>

**A:** A benchmark is saturated when top models all score near the maximum (e.g., 95%+), making it impossible to differentiate between them. GSM8K has become saturated — most frontier models score over 95%, so it can no longer tell you which model is better at math. When saturation happens, the field moves to harder benchmarks: from GSM8K to MATH, from MATH to GPQA/AIME. A good benchmark has a wide range of scores across different model capabilities.

</details>

---

## Intermediate Level

**Q4: Explain the difference between zero-shot and few-shot benchmark evaluation.**

<details>
<summary>💡 Show Answer</summary>

**A:** Zero-shot evaluation: the model receives only the question (and task instructions) — no examples. This tests the model's innate knowledge from training. Few-shot evaluation: the model receives k examples of (question, correct answer) pairs before the question. 5-shot is common for MMLU. Few-shot prompts the model to understand the expected format and can significantly improve accuracy. When comparing models, you must use the same shot setting — a model evaluated 5-shot will score higher than the same model evaluated zero-shot, making comparisons across settings misleading.

</details>

**Q5: What is benchmark contamination and why is it a problem?**

<details>
<summary>💡 Show Answer</summary>

**A:** Benchmark contamination occurs when a model's training data includes the benchmark questions and/or answers. If MMLU questions appear in web scraping that went into training, the model may have effectively memorized the answers rather than demonstrating genuine reasoning ability. This inflates scores without reflecting real capability. It's hard to detect and is a significant concern for models trained on large undisclosed web crawls. Signs: unrealistically high scores for model size, dramatic jumps from one version to next, performance drops on alternative benchmark versions (MMLU-Pro).

</details>

**Q6: Why should you always run task-specific evals in addition to looking at benchmark scores?**

<details>
<summary>💡 Show Answer</summary>

**A:** Benchmarks measure average capability across standardized tasks. They don't predict performance on your specific use case because: (1) your task domain may be different from benchmark domains, (2) your input distribution may be different (longer documents, specific jargon, unusual formats), (3) benchmarks test capability but not instruction following, response format compliance, or domain-specific reasoning, (4) benchmark tasks have neat, well-defined correct answers — your task may be more open-ended. Rule: use benchmarks to shortlist 2–3 candidate models, then evaluate those candidates specifically on your task.

</details>

---

## Advanced Level

**Q7: How would you design a better benchmark for evaluating an AI system for legal document analysis?**

<details>
<summary>💡 Show Answer</summary>

**A:** A task-specific benchmark for legal document analysis:
1. **Task definition**: Extract clauses, identify legal issues, summarize obligations, answer questions about documents
2. **Data collection**: Real legal documents (anonymized), covering multiple document types (contracts, pleadings, regulations, case law)
3. **Annotation**: Legal professionals annotate ground truth answers for each question
4. **Metrics**: Exact clause extraction (precision/recall), legal issue identification accuracy, answer quality (LLM-as-judge with legal expert calibration), citation accuracy
5. **Contamination prevention**: Use documents from after the model cutoff date, or proprietary documents not on the web
6. **Difficulty distribution**: Easy (simple contract questions) to hard (multi-document synthesis, jurisdictional conflicts)
7. **Human baseline**: Measure junior paralegal and senior attorney performance
Why it beats MMLU: directly measures the capability you need; uses the exact document types and question styles your system will face; catches failure modes invisible in general benchmarks.

</details>

**Q8: What is the LMSYS Chatbot Arena and why is it different from other benchmarks?**

<details>
<summary>💡 Show Answer</summary>

**A:** LMSYS Chatbot Arena is a continuously updated platform where human users interact with two anonymous AI models simultaneously and vote for which response they prefer. The votes generate Elo ratings — the same system used in chess. It's different because: (1) it measures real human preference, not academic task performance, (2) the questions come from actual users with diverse real-world needs, (3) the evaluation is blind (users don't know which model they're comparing), reducing brand bias, (4) it's continuously updated with new models and new questions. The Elo rankings often differ significantly from academic benchmark rankings — a model can score highly on MMLU but rank lower in Arena because users care about helpfulness, clarity, and format, not just factual correctness.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Benchmark_Comparison.md](./Benchmark_Comparison.md) | All benchmarks comparison table |

⬅️ **Prev:** [01 — Evaluation Fundamentals](../01_Evaluation_Fundamentals/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 — LLM as Judge](../03_LLM_as_Judge/Theory.md)
