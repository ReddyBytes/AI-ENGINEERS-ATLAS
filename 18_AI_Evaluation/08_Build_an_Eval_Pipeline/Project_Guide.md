# Build an Eval Pipeline — Project Guide

## The Story: From "It Seems to Work" to "We Know It Works"

A fintech startup launches an AI-powered financial advisor chatbot. For the first few weeks, the founders test it manually — ask it some questions, read the answers, nod approvingly. "Looks good!"

Then a user asks about tax-loss harvesting and the bot confidently gives advice based on 2021 tax law. The rules changed. No one caught it because no one was systematically testing it.

They hire a machine learning engineer. Her first week: she doesn't write a single new feature. Instead, she builds an eval pipeline. By Friday, the pipeline has already caught three more outdated answers and two cases where the bot confidently fabricated a regulation that doesn't exist.

This is what a real eval pipeline does. It converts "we think it works" into "we know it works, to within X%."

---

## What You'll Build

A complete end-to-end evaluation pipeline for an LLM application, covering:

1. **Test dataset** — golden examples, edge cases, adversarial inputs
2. **Automated evaluators** — deterministic assertions + LLM-as-judge
3. **CI/CD integration** — eval runs on every code change
4. **Metrics dashboard** — track quality over time
5. **Human review loop** — keep the dataset fresh

---

## Project Structure

```
eval_pipeline/
├── data/
│   ├── golden_set.json         # hand-verified test cases
│   ├── edge_cases.json         # boundary conditions
│   └── adversarial.json        # safety/robustness tests
├── evaluators/
│   ├── deterministic.py        # string match, regex, JSON checks
│   ├── llm_judge.py            # LLM-as-judge evaluators
│   └── domain_specific.py      # custom business logic checks
├── pipeline/
│   ├── runner.py               # orchestrates the full eval run
│   ├── reporter.py             # generates reports and alerts
│   └── dataset_manager.py      # manages test data versioning
├── promptfooconfig.yaml        # Promptfoo config for CI
├── .github/workflows/eval.yml  # GitHub Actions integration
└── results/                    # stored eval results (git-ignored)
```

---

## Phase 1: Build Your Test Dataset

### The Golden Set (100–500 cases)
Your most important asset. These are:
- Hand-verified input/output pairs
- Representative of real user queries
- Manually checked by a domain expert
- Never automatically modified

```json
// data/golden_set.json
[
  {
    "id": "tax-loss-harvesting-basic",
    "category": "tax",
    "input": "What is tax-loss harvesting?",
    "expected_key_points": [
      "selling investments at a loss",
      "offset capital gains",
      "tax liability"
    ],
    "not_expected": ["specific dollar amounts", "legal advice disclaimer missing"],
    "metadata": {
      "added_by": "sarah@company.com",
      "added_date": "2024-01-15",
      "verified_by": "financial_expert",
      "priority": "high"
    }
  }
]
```

### The Edge Case Set (50–100 cases)
Boundary conditions that reveal brittleness:
- Very short inputs ("help")
- Very long inputs (500+ words)
- Ambiguous questions
- Questions with wrong premises
- Multi-language inputs
- Typos and misspellings

### The Adversarial Set (20–50 cases)
Intentionally challenging inputs:
- Jailbreak attempts
- Prompt injection attacks
- Questions designed to elicit hallucinations
- Out-of-scope requests
- Contradictory instructions

---

## Phase 2: Build Your Evaluators

### Tiered Evaluation Strategy

```
Tier 1: Deterministic Checks (fast, free, always run)
  - Contains required keywords
  - Doesn't contain forbidden phrases
  - Output is valid JSON (if structured output)
  - Length within bounds
  - Response time < 5s

Tier 2: LLM-as-Judge (slower, costs $, run selectively)
  - Factual accuracy
  - Helpfulness
  - Tone/safety
  - Task completion

Tier 3: Domain Expert Review (slow, expensive, monthly)
  - Compliance correctness
  - Subtle accuracy issues
  - Novel failure modes
```

### Evaluator Selection by Task

| Task Type | Primary Evaluator | Secondary Evaluator |
|-----------|-------------------|---------------------|
| QA / factual | LLM-judge accuracy | String match on key facts |
| Summarization | LLM-judge coverage | Length ratio check |
| Code generation | Execute and test | LLM-judge code quality |
| Classification | Exact match accuracy | Confusion matrix |
| Structured output | JSON schema validation | Field completeness check |
| Safety/tone | String match (forbidden words) | LLM safety judge |

---

## Phase 3: CI/CD Integration

### Three Modes

**Smoke test** (every PR, < 2 min):
- 50 most critical test cases
- Deterministic checks only
- Blocks merge if any failure

**Standard eval** (every merge to main, < 15 min):
- Full golden set (300–500 cases)
- Deterministic + LLM judge
- Sends Slack alert if regression > 3%

**Full regression** (weekly/on release, < 2 hrs):
- All test sets including adversarial
- Full LLM judge suite
- Human-readable report to stakeholders

---

## Phase 4: Metrics to Track

### Core Health Metrics

| Metric | Formula | Target | Alert |
|--------|---------|--------|-------|
| Pass rate | passed / total | > 85% | < 75% |
| Regression rate | failures newly introduced | 0% | > 2% |
| Average quality score | mean(judge_scores) | > 7.5/10 | < 6.0 |
| Error rate | exceptions / total | < 1% | > 5% |
| P95 latency | 95th percentile latency | < 3s | > 8s |
| Cost per eval run | total_tokens × $/token | < $5 | > $20 |

### Track Over Time

Plot these metrics per eval run to detect:
- **Sudden drops**: model API changed, prompt bug introduced
- **Gradual decline**: distribution shift (new user patterns not in test set)
- **Saturation**: all cases passing, time to add harder cases

---

## Phase 5: Human Review Loop

The pipeline is only as good as its test data. Keep it fresh:

**Weekly (30 min)**:
- Sample 20 production conversations
- Check 5 LLM-judge scores by hand
- If human and judge disagree 3+ times, recalibrate judge prompt

**Monthly (2 hours)**:
- Review all thumbs-down feedback from production
- Add 10–20 new test cases based on real failures
- Retire test cases that consistently pass (move to archived)

**Quarterly (half-day)**:
- Full dataset audit with domain expert
- Update expected answers for any changed facts/policies
- Add adversarial cases for newly discovered attack patterns
- Recalibrate judge model if new version available

---

## Checklist: Eval Pipeline Readiness

### Dataset
- [ ] 100+ golden test cases, manually verified
- [ ] Edge cases for boundary conditions
- [ ] Adversarial test cases for safety
- [ ] Dataset is versioned in git
- [ ] Process to add new cases from production failures

### Evaluators
- [ ] Deterministic checks for format/structure
- [ ] LLM-judge for quality metrics
- [ ] Domain-specific checks for business rules
- [ ] Inter-rater agreement validated (κ > 0.7)

### Infrastructure
- [ ] Eval runs automatically on PR
- [ ] Results are stored and queryable
- [ ] Regression detection is automated
- [ ] Alerts go to Slack/email on failures
- [ ] Dashboard shows trends over time

### Process
- [ ] Team knows how to add new test cases
- [ ] Human review happens monthly
- [ ] Eval results reviewed before each release
- [ ] Clear owner for eval infrastructure

---

## 📂 Navigation

- Parent: [18_AI_Evaluation](../)
- Step-by-Step Guide: [Step_by_Step.md](Step_by_Step.md)
- Code Example: [Code_Example.md](Code_Example.md)
- Metrics Guide: [Metrics_Guide.md](Metrics_Guide.md)
- Previous: [07_Eval_Frameworks](../07_Eval_Frameworks/)
- Section root: [Evaluation_Checklist.md](../Evaluation_Checklist.md)
