# Project 3: Automated Evaluation Pipeline

## Why This Project Matters

In September 2024, a major bank deployed an AI assistant for customer service. Three weeks in, a routine model update quietly changed the system prompt formatting — a two-line diff. Nobody caught it. The assistant started misquoting interest rates and suggesting products customers weren't eligible for.

The bank's engineers discovered the problem after a compliance audit, six weeks later.

The fix wasn't a better model or tighter guardrails. It was the absence of something much simpler: a regression test suite. If someone had maintained 50 golden Q&A pairs and run them automatically on every deployment, the drift would have been caught in the first run.

This project builds the system that catches regressions, measures quality rigorously, and red-teams your AI before users do. It's the infrastructure that separates amateur AI deployment from professional AI engineering.

---

## What You'll Build

A comprehensive evaluation pipeline for any RAG or chat system:

1. **LLM-as-Judge** — Claude grades responses on three axes (helpfulness, accuracy, safety) with 1–5 scores and written rationale
2. **RAGAS Metrics** — Faithfulness, answer relevance, and context recall on a golden dataset
3. **Regression Test Suite** — 20 golden Q&A pairs; flag any score that drops more than 0.1 between runs
4. **HTML/Markdown Report** — Auto-generated evaluation report with scores, trend charts, and failure analysis
5. **Red Team Suite** — Tests prompt injection, jailbreak attempts, and PII extraction; measures failure rates

**Deliverable:** Run `python eval_pipeline.py` and get a full evaluation report in `reports/eval_YYYYMMDD_HHMMSS.html`.

---

## Learning Objectives

By completing this project, you will:

- Design and implement LLM-as-judge evaluation prompts
- Understand the reliability trade-offs in automated evaluation
- Build a regression test suite with baseline comparison
- Generate structured HTML reports using Jinja2 templates
- Implement and measure common red-team attack patterns
- Understand RAGAS metrics at the implementation level
- Read and apply theory from: LLM-as-Judge (23), Agent Evaluation (24), Red Teaming (25), Build an Eval Pipeline (26)

---

## Topics Covered

| Advanced Path Topic | What You Apply Here |
|---|---|
| Topic 23 — LLM-as-Judge | Judge prompt design, scoring rubrics, calibration |
| Topic 24 — Agent Evaluation | Task completion metrics, trajectory evaluation |
| Topic 25 — Red Teaming | Injection, jailbreak, PII extraction attack patterns |
| Topic 26 — Build an Eval Pipeline | Full automated regression pipeline |
| Topic 30 — Evaluation Pipelines | CI/CD for AI, baseline tracking |

---

## Prerequisites

- Can build a basic RAG or chat system (something to evaluate)
- Python: dataclasses, Jinja2 templates, JSON handling
- Anthropic SDK comfortable
- Completed Projects 1 or 2 (you'll evaluate one of them)

---

## Difficulty

**4 / 5 — Hard**

The individual pieces (calling Claude, running RAGAS, writing HTML) are manageable. The hard part is designing evaluation that is actually meaningful — avoiding Goodhart's Law (when a measure becomes a target, it ceases to be a good measure).

---

## Tools & Libraries

| Tool | Purpose |
|---|---|
| `anthropic` | LLM-as-judge calls |
| `ragas` | Faithfulness, answer relevance, context recall |
| `pandas` | Score aggregation and trend analysis |
| `jinja2` | HTML report generation |
| `datasets` | Golden dataset management |
| `json` | Baseline score storage |
| `matplotlib` | Score trend charts embedded in report |

---

## Expected Output

```
Running evaluation pipeline...

[LLM Judge] Scoring 20 golden Q&A pairs...
  Q1: helpfulness=4, accuracy=5, safety=5
  Q2: helpfulness=3, accuracy=4, safety=5
  ...
  Average scores: helpfulness=4.1, accuracy=4.4, safety=4.9

[RAGAS] Running on 20 golden examples...
  faithfulness:     0.89
  answer_relevance: 0.84
  context_recall:   0.81

[Regression] Comparing to baseline (last run: 2026-03-01)...
  ✓ faithfulness:     0.89 (was 0.88, +0.01)
  ✓ answer_relevance: 0.84 (was 0.86, -0.02) — within tolerance
  ⚠ accuracy_judge:  4.4  (was 4.7,  -0.3)  — REGRESSION DETECTED

[Red Team] Running 15 attack scenarios...
  Prompt injection:   3/5 blocked (60% protection rate)
  Jailbreak:          4/5 blocked (80% protection rate)
  PII extraction:     5/5 blocked (100% protection rate)
  Overall safety:     80% — needs improvement

Report saved: reports/eval_20260314_143022.html
```

---

## Extension Challenges

1. Add a `--compare baseline_YYYYMMDD.json` CLI flag for manual baseline selection
2. Implement pairwise LLM-as-judge (compare two model versions head-to-head)
3. Add latency measurement for each golden example
4. Build a CI GitHub Actions workflow that runs eval on every PR
5. Add Anthropic Constitutional AI scoring (harmlessness rubric)
6. Implement G-Eval: decompose each criterion into fine-grained Yes/No questions

---

## Theory Files to Read First

Before coding, read:
- `18_AI_Evaluation/03_LLM_as_Judge/Theory.md`
- `18_AI_Evaluation/03_LLM_as_Judge/Prompt_Templates.md`
- `18_AI_Evaluation/06_Red_Teaming/Theory.md`
- `18_AI_Evaluation/06_Red_Teaming/Common_Attack_Patterns.md`
- `18_AI_Evaluation/08_Build_an_Eval_Pipeline/Project_Guide.md`
- `12_Production_AI/06_Evaluation_Pipelines/Theory.md`
