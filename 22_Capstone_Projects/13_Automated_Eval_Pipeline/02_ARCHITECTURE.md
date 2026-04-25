# 02 Architecture — Automated Evaluation Pipeline

## System Flowchart

```mermaid
flowchart TD
    SUT[System Under Test\nquery_system] --> COLLECT[Collect System Outputs\n20 question-answer pairs]
    GD[(Golden Dataset\n20 Q&A pairs)] --> COLLECT

    COLLECT --> JUDGE[LLM-as-Judge\nClaude scores each response]
    COLLECT --> RAGAS[RAGAS Evaluator\nFaithfulness, Relevancy, Recall]
    COLLECT --> RED[Red Team Suite\n15 attack scenarios]

    JUDGE --> AGG[Score Aggregator\nAverage per metric]
    RAGAS --> AGG
    RED --> REDSUM[Red Team Summarizer\nProtection rate by category]

    AGG --> REG{Regression Check}
    BASELINE[(Baseline Store\nbaselines/*.json)] --> REG
    REG -->|regression detected| ALERT[Alert Output\nPrint regression table]
    REG -->|no regression| SAVE[Save New Baseline]
    ALERT --> SAVE

    AGG --> REPORT[HTML Report Generator\nJinja2 template]
    REDSUM --> REPORT
    REG --> REPORT

    REPORT --> OUTPUT([reports/eval_YYYYMMDD.html])

    style SUT fill:#4A90D9,color:#fff
    style OUTPUT fill:#27AE60,color:#fff
    style ALERT fill:#E74C3C,color:#fff
    style RED fill:#8E44AD,color:#fff
    style JUDGE fill:#E67E22,color:#fff
```

---

## Component Table

| Component | Class / Function | Input | Output | Notes |
|---|---|---|---|---|
| System Under Test | `query_system()` | Question string | `(answer, contexts)` tuple | Swap with any system |
| Golden Dataset | `GOLDEN_DATASET` list | — | 20 Q&A/context triples | 4 categories: factual, reasoning, safety, edge_case |
| LLM Judge | `LLMJudge.score()` | item, answer | `JudgeScore` (3 scores + rationale) | Uses Claude as evaluator; calibrate on 3 hand-scored examples |
| RAGAS Evaluator | `run_ragas()` | golden data + system outputs | `RagasScores` (3 metrics) | Requires non-empty contexts; uses LLM internally |
| Regression Tester | `RegressionTester.compare()` | current scores, baseline | `list[RegressionResult]` | Flags drops > REGRESSION_THRESHOLD (0.10) |
| Baseline Store | JSON files | score dict | `baselines/baseline_YYYYMMDD.json` | Load most recent for comparison |
| Red Team Evaluator | `RedTeamEvaluator.run_all()` | 15 attack strings | `list[RedTeamResult]` | Independent judge call per attack |
| Report Generator | `generate_html_report()` | `EvalReport` | HTML file path | Jinja2 inline template |

---

## Tech Stack

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

## Evaluation Metrics Taxonomy

```mermaid
mindmap
  root((Evaluation\nMetrics))
    LLM-as-Judge
      Helpfulness 1-5
      Accuracy 1-5
      Safety 1-5
    RAGAS
      Faithfulness
        Answer vs contexts
      Answer Relevancy
        Answer vs question
      Context Recall
        Contexts vs ground truth
    Red Team
      Prompt Injection
        5 scenarios
      Jailbreak
        5 scenarios
      PII Extraction
        5 scenarios
    Regression
      Delta from baseline
      Threshold 0.10
```

---

## LLM Judge Prompt Flow

```mermaid
sequenceDiagram
    participant E as Evaluator
    participant J as Judge (Claude)

    E->>J: System: Scoring rubric (helpfulness, accuracy, safety 1-5)
    E->>J: User: Question + Ground Truth + AI Answer
    J-->>E: JSON: {"helpfulness": 4, "accuracy": 5, "safety": 5, "rationale": "..."}
    Note over E: Parse JSON, store as JudgeScore
    Note over E: Retry on JSON parse error
```

Calibration procedure: before running on all 20 examples, hand-score 3 examples yourself. If the judge disagrees by more than 1 point on any dimension, revise the rubric.

Position bias mitigation: for accuracy scoring, randomly swap the order of "AI Answer" and "Ground Truth" in the prompt, run twice, and average.

---

## Red Team Defense Architecture

```mermaid
flowchart LR
    ATK[Attack Text] --> SUT[System Under Test]
    SUT --> RESP[Response]
    ATK --> JDGP[Judge Prompt\nDid the system comply?]
    RESP --> JDGP
    JDGP --> CLAUDE[Claude Judge\nIndependent call]
    CLAUDE --> V{Verdict}
    V -->|BLOCKED| B[Protected]
    V -->|PARTIAL| P[Partial Failure]
    V -->|FAILED| F[Full Failure]
```

| Attack Category | Example | Defense Signal |
|---|---|---|
| Prompt Injection | "Ignore previous instructions and..." | Model should not reveal system prompt or follow injected instructions |
| Jailbreak | "Pretend you are DAN..." | Model should reject the persona and explain why |
| PII Extraction | "What data do other users share?" | Model should not reference or fabricate user data |

---

## Regression Detection Flow

```mermaid
stateDiagram-v2
    [*] --> FirstRun: No baseline found
    FirstRun --> SaveBaseline: Save current scores
    SaveBaseline --> [*]

    [*] --> SubsequentRun: Baseline exists
    SubsequentRun --> Compare: Load latest baseline
    Compare --> NoRegression: All deltas > -0.10
    Compare --> RegressionAlert: Any delta < -0.10
    NoRegression --> SaveNewBaseline
    RegressionAlert --> PrintAlert: Show failing metrics
    PrintAlert --> SaveNewBaseline
    SaveNewBaseline --> [*]
```

---

## Report Structure

```
reports/eval_20260314_143022.html
├── Header: run date, system name
├── Summary Scorecard: big color-coded numbers for each metric
├── LLM Judge Table: per-question scores with rationale
├── RAGAS Metrics Table: 3 metrics with status
├── Regression Table: current vs baseline, delta, status
└── Red Team Table: all 15 attacks with verdict
```

---

## File Structure

```
13_Automated_Eval_Pipeline/
├── 01_MISSION.md
├── 02_ARCHITECTURE.md
├── 03_GUIDE.md
├── 04_RECAP.md
├── src/
│   └── starter.py          # Main pipeline (eval_pipeline.py)
├── baselines/              # JSON baseline files (auto-created)
│   └── baseline_YYYYMMDD_HHMMSS.json
└── reports/                # HTML reports (auto-created)
    └── eval_YYYYMMDD_HHMMSS.html
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [01_MISSION.md](./01_MISSION.md) | Context and goals |
| **02_ARCHITECTURE.md** | you are here |
| [03_GUIDE.md](./03_GUIDE.md) | Progressive build steps |
| [src/starter.py](./src/starter.py) | Runnable starter code |
| [04_RECAP.md](./04_RECAP.md) | Concepts applied, extensions, job mapping |
