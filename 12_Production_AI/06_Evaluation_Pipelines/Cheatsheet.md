# Cheatsheet — Evaluation Pipelines

**Evaluation pipelines** systematically measure AI output quality before deployment (offline) and in production (online), using automated metrics, LLM judges, and human review.

---

## Key Terms

| Term | Definition |
|---|---|
| **Offline evaluation** | Testing on a fixed benchmark before deployment. Gating deployments. |
| **Online evaluation** | Monitoring quality on live production traffic. Detecting drift. |
| **Test set** | Curated (input, expected_output) pairs used to evaluate quality |
| **LLM-as-judge** | Using a capable model (GPT-4, Claude) to score responses on a rubric |
| **BLEU** | Bilingual Evaluation Understudy — n-gram overlap metric for translation |
| **ROUGE** | Recall-Oriented Understudy for Gisting Evaluation — for summarization |
| **Exact match** | Whether predicted output exactly equals expected output (classification/extraction) |
| **F1 score** | Harmonic mean of precision and recall — for NER, extraction tasks |
| **RAGAS** | RAG Assessment framework — evaluates faithfulness, relevance, context precision |
| **Faithfulness** | Does the answer contradict the retrieved context? (RAG quality metric) |
| **Answer relevance** | Does the answer address the question that was asked? |
| **Pass rate** | Fraction of test cases that pass the quality threshold |
| **Regression** | A quality degradation on a previously passing metric |

---

## Evaluation Types by Task

| Task Type | Primary Metric | Secondary Metrics | Method |
|---|---|---|---|
| **Classification** | Accuracy, F1 | Precision, Recall, AUC | Exact match |
| **Named Entity Extraction** | F1 (token level) | Precision, Recall | Exact + partial match |
| **Summarization** | ROUGE-L | ROUGE-1, ROUGE-2, BERTScore | Statistical + LLM judge |
| **Translation** | BLEU | chrF, TER | Statistical |
| **Open-ended Q&A** | LLM judge score | Faithfulness, Answer relevance | LLM-as-judge |
| **RAG pipeline** | Faithfulness, Answer relevance | Context precision, recall | RAGAS |
| **Code generation** | Pass@k (unit tests) | Syntax validity | Test execution |
| **Dialogue / chatbot** | LLM judge score | User satisfaction | LLM-as-judge + human |
| **Structured output** | Schema validation rate | Field accuracy | Exact match |

---

## LLM-as-Judge Rubric Template

```
You are an expert evaluator. Rate the following response on a 1-5 scale.

Question: {question}
Response: {response}
Reference Answer (if available): {reference}

Criteria:
- Accuracy (1-5): Is the information correct?
- Helpfulness (1-5): Does it answer what was asked?
- Clarity (1-5): Is it well-written and easy to understand?
- Completeness (1-5): Does it cover all key points?
- Safety (1-5): Is it free of harmful or inappropriate content?

Score each criterion and provide an overall score (1-5, where 5 = excellent).
Return JSON: {"accuracy": int, "helpfulness": int, "clarity": int,
              "completeness": int, "safety": int, "overall": int, "reasoning": str}
```

---

## RAGAS Metrics (RAG Evaluation)

| Metric | Question | Formula (simplified) | Target |
|---|---|---|---|
| **Faithfulness** | Does the answer contradict the context? | % statements supported by context | > 0.85 |
| **Answer Relevance** | Does the answer address the question? | Similarity(question, answer) | > 0.80 |
| **Context Precision** | Are retrieved chunks relevant? | Proportion of relevant retrieved chunks | > 0.75 |
| **Context Recall** | Did we retrieve all necessary info? | Coverage of ground truth by context | > 0.70 |

---

## Evaluation Pipeline CI/CD Integration

```yaml
# .github/workflows/eval.yml — Run evals on every PR
name: Model Quality Gate

on:
  pull_request:
    paths:
      - 'prompts/**'
      - 'models/**'
      - 'src/llm/**'

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run evaluation
        run: python eval/run_eval.py --threshold 4.0 --min-pass-rate 0.90
      - name: Post results to PR
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const results = JSON.parse(fs.readFileSync('eval_results.json'));
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              body: `Eval results: ${results.pass_rate}% pass rate, avg score: ${results.avg_score}/5`
            });
```

---

## Test Set Design Principles

**A good test set includes:**
- 15-20% easy cases (model should always pass these)
- 60-70% typical production cases
- 15-20% hard/edge cases (adversarial, ambiguous, out-of-domain)
- Both positive examples (correct answers) and negative examples (wrong answers to reject)

**Test set size rules of thumb:**
- Minimum for meaningful results: 50 examples
- Adequate for most applications: 200-500 examples
- Rigorous for high-stakes applications: 1,000-5,000 examples
- Refresh interval: quarterly, or whenever major distribution shift detected

---

## Evaluation Thresholds

| Risk Level | Application Type | Suggested Pass Threshold |
|---|---|---|
| Low | Internal tools, B2B dashboards | 80% pass rate, avg score ≥ 3.5/5 |
| Medium | Consumer-facing features | 90% pass rate, avg score ≥ 4.0/5 |
| High | Healthcare, legal, finance | 95%+ pass rate, human review required |
| Critical | Medical diagnosis, legal advice | Human in the loop always |

---

## Golden Rules

- **Eval before every deployment** — treat it like unit tests; block merges that fail
- **Your test set IS your specification** — if you can't write a test for it, you don't know what "good" means
- **Use a different model as judge** — don't use GPT-4 to evaluate GPT-4
- **Track eval metrics over time** — a single score is less valuable than a trend
- **Refresh your test set regularly** — production distribution changes over time
- **Trace failing examples** — evals that just report a number without showing you the failures are useless
- **Include adversarial cases** — test the edge cases users will actually hit

---

## 📂 Navigation
