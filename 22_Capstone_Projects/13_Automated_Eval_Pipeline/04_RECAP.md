# 04 Recap — Automated Evaluation Pipeline

## What You Built

A production-grade evaluation pipeline that runs automatically against any RAG or chat system. The pipeline scores responses using three independent methods — an LLM-as-judge rubric, RAGAS retrieval metrics, and a red team attack suite — then compares results against a stored baseline and generates a color-coded HTML report. Running `python src/starter.py` on every model deployment catches quality regressions before users do.

---

## Concepts Applied

| Concept | How It Was Applied |
|---|---|
| LLM-as-Judge | Designed a 3-axis scoring rubric (helpfulness, accuracy, safety). Used Claude to evaluate Q&A pairs with explicit 1–5 criteria and JSON output. |
| Calibration | Hand-scored 3 examples before running on the full golden set. Compared judge scores against manual scores to validate the rubric. |
| Position bias mitigation | Randomized the order of AI answer vs. ground truth in the judge prompt to eliminate first-position favoritism. |
| RAGAS metrics | Ran faithfulness, answer relevancy, and context recall on a golden dataset with context-answer-ground_truth triplets. |
| Regression testing | Saved scores as JSON baselines and flagged any metric that dropped more than 0.10 between runs. |
| Red teaming | Ran 15 attack scenarios across prompt injection, jailbreak, and PII extraction categories. Used an independent Claude call to judge each response as BLOCKED/PARTIAL/FAILED. |
| Jinja2 report generation | Rendered an HTML report with embedded score tables, regression diff, and red team results from a single template string. |
| Goodhart's Law | Understanding why "optimize for the metric" is dangerous in evaluation design. |

---

## Extension Ideas

**1. CI/CD integration**
Add a GitHub Actions workflow that runs the pipeline on every pull request. Fail the PR if any metric drops below a threshold. Store baselines in a branch-specific JSON file so main-branch baselines are never overwritten by feature branches.

**2. G-Eval scoring**
Replace the 3-axis judge with G-Eval: decompose each criterion into 5–10 fine-grained Yes/No questions (e.g., "Does the answer mention a specific mechanism?"). Average the binary scores. This is more reliable than holistic 1–5 ratings because it reduces inter-rater variance.

**3. Pairwise comparison mode**
Add a `--compare-model` flag that runs two model versions head-to-head. Instead of absolute scores, use Claude to pick a winner for each golden example. Win rate is more informative than absolute score deltas when comparing similar systems.

---

## Job Mapping

| Role | How This Project Demonstrates Fit |
|---|---|
| ML Engineer | Built an automated quality gate — a prerequisite for any production AI deployment. Understand regression detection, golden datasets, and CI/CD for AI. |
| AI Safety Engineer | Implemented adversarial testing (red team) and measured protection rates across attack categories. Understand failure modes and how to measure them systematically. |
| Evaluation Researcher | Designed a judge rubric, calibrated it, and applied RAGAS metrics. Understand the trade-offs between automated and human evaluation. |
| LLM Product Engineer | Built the tooling that answers "is this model better or worse than last week?" — required for any team shipping AI to users. |

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [01_MISSION.md](./01_MISSION.md) | Context and goals |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design |
| [03_GUIDE.md](./03_GUIDE.md) | Progressive build steps |
| [src/starter.py](./src/starter.py) | Runnable starter code |
| **04_RECAP.md** | you are here |
