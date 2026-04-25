# 01 Mission — Automated Evaluation Pipeline

## The Story

In September 2024, a major bank deployed an AI assistant for customer service. Three weeks in, a routine model update quietly changed the system prompt formatting — a two-line diff. Nobody caught it. The assistant started misquoting interest rates and suggesting products customers weren't eligible for.

The bank's engineers discovered the problem after a compliance audit, six weeks later.

The fix wasn't a better model or tighter guardrails. It was the absence of something much simpler: a regression test suite. If someone had maintained 50 golden Q&A pairs and run them automatically on every deployment, the drift would have been caught in the first run.

This project builds the system that catches regressions, measures quality rigorously, and red-teams your AI before users do.

---

## What You Build

A comprehensive evaluation pipeline for any RAG or chat system:

1. **LLM-as-Judge** — Claude grades responses on three axes (helpfulness, accuracy, safety) with 1–5 scores and written rationale
2. **RAGAS Metrics** — Faithfulness, answer relevance, and context recall on a golden dataset
3. **Regression Test Suite** — 20 golden Q&A pairs; flag any score that drops more than 0.1 between runs
4. **HTML/Markdown Report** — Auto-generated evaluation report with scores, trend charts, and failure analysis
5. **Red Team Suite** — Tests prompt injection, jailbreak attempts, and PII extraction; measures failure rates

**Deliverable:** Run `python src/starter.py` and get a full evaluation report in `reports/eval_YYYYMMDD_HHMMSS.html`.

---

## Concepts You Apply

| Topic | What You Apply |
|---|---|
| LLM-as-Judge | Judge prompt design, scoring rubrics, calibration |
| Agent Evaluation | Task completion metrics, trajectory evaluation |
| Red Teaming | Injection, jailbreak, PII extraction attack patterns |
| Eval Pipelines | Full automated regression pipeline, CI/CD for AI |

**Theory files to read first:**
- `18_AI_Evaluation/03_LLM_as_Judge/Theory.md`
- `18_AI_Evaluation/06_Red_Teaming/Theory.md`
- `12_Production_AI/06_Evaluation_Pipelines/Theory.md`

---

## Prerequisites

- Can build a basic RAG or chat system (something to evaluate)
- Python: dataclasses, Jinja2 templates, JSON handling
- Anthropic SDK comfortable
- Completed Projects 1 or 2 (you will evaluate one of them)

---

## Difficulty and Format

**Difficulty: 4 / 5 — Hard**

The individual pieces (calling Claude, running RAGAS, writing HTML) are manageable. The hard part is designing evaluation that is actually meaningful — avoiding Goodhart's Law: when a measure becomes a target, it ceases to be a good measure.

**Learning format tier: Advanced**

This is a guided build. The starter code gives you the skeleton and all data structures. You implement the logic inside each function by following the `# TODO:` markers. Each phase is independently runnable and testable.

---

## Success Looks Like

```
Running evaluation pipeline...

[LLM Judge] Scoring 20 golden Q&A pairs...
  Q1: helpfulness=4, accuracy=5, safety=5
  Average scores: helpfulness=4.1, accuracy=4.4, safety=4.9

[RAGAS] Running on 20 golden examples...
  faithfulness:     0.89
  answer_relevance: 0.84
  context_recall:   0.81

[Regression] Comparing to baseline (last run: 2026-03-01)...
  accuracy_judge: 4.4 (was 4.7, -0.3) -- REGRESSION DETECTED

[Red Team] Running 15 attack scenarios...
  Overall safety: 80%

Report saved: reports/eval_20260314_143022.html
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| **01_MISSION.md** | you are here |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design and component table |
| [03_GUIDE.md](./03_GUIDE.md) | Progressive build steps |
| [src/starter.py](./src/starter.py) | Runnable starter code |
| [04_RECAP.md](./04_RECAP.md) | Concepts applied, extensions, job mapping |

⬅️ **Prev:** [14_Multi_Agent_Research_System](../14_Multi_Agent_Research_System/01_MISSION.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [14_Multi_Agent_Research_System](../14_Multi_Agent_Research_System/01_MISSION.md)
