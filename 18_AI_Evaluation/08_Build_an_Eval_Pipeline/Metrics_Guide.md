# Build an Eval Pipeline — Metrics Guide

## The Four Dimensions of LLM Quality

Every eval metric falls into one of four dimensions. Track all four — optimizing for just one leads to bad tradeoffs (e.g., a model that's extremely fast but completely wrong).

```
Quality      — Is the output correct, helpful, and appropriate?
Safety       — Does it avoid harmful, biased, or policy-violating outputs?
Latency      — Is it fast enough for the use case?
Cost         — Is it economically viable at scale?
```

---

## Quality Metrics

### 1. Pass Rate

The single most important eval metric.

```
pass_rate = num_cases_passed / total_cases
```

**Interpretation:**
| Score | Status |
|-------|--------|
| > 90% | Excellent — production ready |
| 80–90% | Good — monitor closely |
| 70–80% | Warning — investigate failures |
| < 70% | Fail — do not deploy |

**When to use**: Always. This is your headline metric.

**Pitfall**: A high pass rate on a weak test set is meaningless. The test set must be challenging.

---

### 2. Average Judge Score

When using LLM-as-judge on a 1–10 scale:

```
avg_score = sum(judge_scores) / num_judged_cases
```

**Interpretation (1–10 scale):**
| Score | Meaning |
|-------|---------|
| 9–10 | Excellent — sets industry standard |
| 7–8 | Good — meets user expectations |
| 5–6 | Mediocre — some users will be frustrated |
| 3–4 | Poor — users will churn |
| 1–2 | Terrible — do not ship |

**When to use**: When you need graded quality rather than binary pass/fail. Useful for detecting gradual degradation (score drops from 8.2 → 7.8 → 7.1 over time) before pass rate drops.

---

### 3. Task-Specific Metrics

Different task types need different primary metrics:

#### Text Classification
```python
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix

accuracy = accuracy_score(true_labels, pred_labels)
f1 = f1_score(true_labels, pred_labels, average='weighted')
```

**Use F1 over accuracy** when classes are imbalanced (e.g., 95% safe / 5% harmful).

#### Summarization
```python
# ROUGE scores (overlap with reference summary)
from rouge_score import rouge_scorer
scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'])
scores = scorer.score(reference, generated)
```

| Metric | What It Measures |
|--------|-----------------|
| ROUGE-1 | Unigram (word) overlap |
| ROUGE-2 | Bigram overlap |
| ROUGE-L | Longest common subsequence |

ROUGE is fast but doesn't capture paraphrasing. Use LLM judge for semantic quality.

#### Code Generation
```python
# pass@k: does at least 1 of k samples pass all tests?
def pass_at_k(n: int, c: int, k: int) -> float:
    """n=total samples, c=correct samples, k=budget"""
    if n - c < k:
        return 1.0
    return 1.0 - product((n-c-i)/(n-i) for i in range(k))

# In practice: pass@1 = fraction of problems where first attempt passes
pass_at_1 = sum(1 for result in results if result.tests_passed) / len(results)
```

#### RAG / Question Answering
- **Faithfulness**: Does the answer only claim what's in the retrieved context?
- **Answer relevance**: Does the answer address the question?
- **Context recall**: Did retrieval find the relevant passages?

(See `04_RAG_Evaluation/Metrics_Guide.md` for full RAGAS coverage.)

---

## Safety Metrics

### Attack Success Rate (ASR)

```
ASR = num_successful_attacks / total_attack_attempts
```

**Target**: ASR < 5% for jailbreaks, < 1% for prompt injection.

### False Positive Rate (Safety Classifier)

If your system has a safety classifier that blocks requests:

```
FPR = safe_requests_blocked / total_safe_requests
```

**Target**: FPR < 1% (blocking legitimate users is a real cost).

### Policy Violation Rate

In production:
```
violation_rate = flagged_outputs / total_outputs
```

Monitor over time. A spike indicates a jailbreak vector has been discovered in the wild.

---

## Latency Metrics

### Key Percentiles

Don't just track average latency — track percentiles:

```python
import numpy as np

latencies = [r.latency_ms for r in results]
p50 = np.percentile(latencies, 50)   # median
p95 = np.percentile(latencies, 95)   # 95% of users experience this or better
p99 = np.percentile(latencies, 99)   # worst 1% of users
```

**Why percentiles matter**: If average is 300ms but P99 is 8000ms, 1% of users are waiting 8 seconds — and those are often your most important users (complex queries).

**Targets by use case:**

| Use Case | P50 Target | P95 Target | P99 Target |
|----------|-----------|-----------|-----------|
| Chatbot (streaming) | 200ms TTFT | 500ms TTFT | 1s TTFT |
| Chatbot (non-streaming) | 1.5s | 3s | 6s |
| Background analysis | 5s | 15s | 30s |
| Batch processing | N/A | N/A | N/A |

*TTFT = Time to First Token*

### Time to First Token (TTFT) vs Total Time

For streaming responses, TTFT is what users perceive as "responsiveness":
```
TTFT = time from request to first token received
Total time = time from request to last token received
```

Optimize TTFT first — it has the biggest impact on perceived speed.

---

## Cost Metrics

### Cost Per Request

```python
def calculate_cost(
    input_tokens: int,
    output_tokens: int,
    model: str
) -> float:
    # Example: Claude claude-opus-4-6 pricing (check current pricing)
    PRICES = {
        "claude-opus-4-6": {"input": 15.00, "output": 75.00},   # per 1M tokens
        "claude-sonnet-4-5": {"input": 3.00, "output": 15.00},
        "claude-haiku-3-5": {"input": 0.80, "output": 4.00},
    }
    p = PRICES.get(model, {"input": 10.0, "output": 30.0})
    return (input_tokens * p["input"] + output_tokens * p["output"]) / 1_000_000
```

### Cost Per Eval Run

Track this to prevent surprise bills:

```python
def eval_run_cost(results: list) -> float:
    return sum(
        calculate_cost(r.input_tokens, r.output_tokens, r.model)
        for r in results
        if not r.error
    )
```

**Typical costs:**
| Eval Size | Model | Avg Cost |
|-----------|-------|---------|
| 50 cases (smoke test) | claude-opus-4-6 | ~$0.50 |
| 500 cases (full eval) | claude-opus-4-6 | ~$5 |
| 500 cases + judge | claude-opus-4-6 | ~$10 |
| 500 cases (haiku) | claude-haiku | ~$0.20 |

**Cost optimization**: Use a smaller model for deterministic checks and only use expensive models as judges for cases that failed cheap checks.

---

## Regression Detection

### Baseline Comparison

The most important use of metrics is detecting regressions — when a code or prompt change makes things worse:

```python
def detect_regression(
    current_results: list[EvalResult],
    baseline_results: list[EvalResult],
    threshold: float = 0.03  # 3% regression triggers alert
) -> dict:
    current_pass_rate = sum(r.passed for r in current_results) / len(current_results)
    baseline_pass_rate = sum(r.passed for r in baseline_results) / len(baseline_results)

    delta = current_pass_rate - baseline_pass_rate
    regressed = delta < -threshold

    # Find which specific cases newly failed
    baseline_passed = {r.test_id for r in baseline_results if r.passed}
    current_passed = {r.test_id for r in current_results if r.passed}
    newly_failed = baseline_passed - current_passed
    newly_fixed = current_passed - baseline_passed

    return {
        "regressed": regressed,
        "delta": delta,
        "current_pass_rate": current_pass_rate,
        "baseline_pass_rate": baseline_pass_rate,
        "newly_failed": sorted(newly_failed),
        "newly_fixed": sorted(newly_fixed)
    }
```

### Alerting Logic

```python
def should_alert(regression: dict) -> tuple[bool, str]:
    """Determine if regression warrants an alert."""
    if regression["regressed"]:
        newly_failed = regression["newly_failed"]
        delta_pct = abs(regression["delta"]) * 100
        return True, (
            f"Regression detected: pass rate dropped {delta_pct:.1f}%\n"
            f"Newly failing cases: {', '.join(newly_failed[:5])}"
        )
    return False, ""
```

---

## Metrics Dashboard Concept

Track these time-series metrics to understand quality trends:

```
Date    | Pass Rate | Avg Score | P95 Latency | Cost/Run | New Cases
--------|-----------|-----------|-------------|----------|----------
2024-01 |    82%    |    7.2    |    1.8s     |  $4.20   |    0
2024-02 |    85%    |    7.5    |    1.6s     |  $4.50   |   15
2024-03 |    91%    |    8.1    |    1.4s     |  $4.80   |   22
```

Alert triggers:
- Pass rate drops > 3% from prior week
- Avg score drops > 0.5 from prior week
- P95 latency increases > 30% from prior week
- Cost per run increases > 50% (unexpected token usage)

---

## Summary: Which Metric to Optimize First

1. **Pass rate < 75%?** Fix the fundamentals — your model or prompt is broken
2. **Safety violations?** Stop everything; fix safety before quality
3. **High latency?** Affects user experience; switch to faster model or add streaming
4. **High cost?** Optimize token usage, switch to smaller model for simpler cases
5. **Mediocre judge scores (6–7)?** Improve the prompt; add few-shot examples
6. **Good metrics, bad user feedback?** Your test set doesn't reflect real users — add more realistic cases

---

## 📂 Navigation

- Parent: [08_Build_an_Eval_Pipeline](./)
- Project Guide: [Project_Guide.md](Project_Guide.md)
- Step-by-Step: [Step_by_Step.md](Step_by_Step.md)
- Code Example: [Code_Example.md](Code_Example.md)
- Section checklist: [Evaluation_Checklist.md](../Evaluation_Checklist.md)
- Section 18 root: [18_AI_Evaluation](../)
