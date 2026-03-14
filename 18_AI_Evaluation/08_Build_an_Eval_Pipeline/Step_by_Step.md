# Build an Eval Pipeline — Step by Step

## Overview

This guide walks you through building a complete eval pipeline from scratch over five steps. By the end, you have automated quality measurement that runs on every code change.

**Time required**: 4–8 hours
**Prerequisites**: Python 3.11+, an LLM API key, basic git/GitHub knowledge

---

## Step 1: Create Your First Test Dataset (30 min)

### 1.1 Start with 10 Handcrafted Cases

Don't start with 1000 cases. Start with 10 excellent ones.

For each case, ask: *"If my system fails this, I would be embarrassed."*

```python
# eval/data/golden_set.py
GOLDEN_CASES = [
    {
        "id": "basic-greeting",
        "input": "Hello, I need help with my account",
        "must_contain": [],
        "must_not_contain": ["I cannot help", "I don't know"],
        "quality_criteria": "Responds warmly and asks how to help",
        "tags": ["onboarding", "basic"]
    },
    {
        "id": "policy-question",
        "input": "What is your return policy?",
        "must_contain": ["30"],  # must mention 30-day window
        "must_not_contain": ["error", "sorry, I can't"],
        "quality_criteria": "Accurately describes the return policy",
        "tags": ["policy", "high-priority"]
    },
    {
        "id": "out-of-scope",
        "input": "What's the best restaurant in Paris?",
        "must_contain": [],
        "must_not_contain": [],
        "quality_criteria": "Politely redirects without being unhelpful",
        "tags": ["scope", "edge-case"]
    },
    # ... add 7 more
]
```

### 1.2 Save as JSON

```python
import json
import pathlib

output_path = pathlib.Path("eval/data/golden_set.json")
output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(json.dumps(GOLDEN_CASES, indent=2))
print(f"Saved {len(GOLDEN_CASES)} test cases")
```

### 1.3 Grow the Dataset Systematically

After your first 10, add cases from:
1. **Real user questions** — export from your chat logs, pick the most common 50
2. **Known failures** — any bug report or user complaint becomes a test case
3. **Edge cases** — what if the user types in all caps? Uses emojis? Asks in French?
4. **Adversarial** — what if someone tries to jailbreak the system?

Target: 100+ cases before considering the dataset production-ready.

---

## Step 2: Build Deterministic Evaluators (45 min)

These are fast, free checks. Run them on every eval case before using the LLM judge.

```python
# eval/evaluators/deterministic.py
import re
import json
import time
from dataclasses import dataclass


@dataclass
class CheckResult:
    passed: bool
    check_name: str
    message: str


def check_contains(output: str, phrases: list[str]) -> list[CheckResult]:
    """Verify output contains required phrases."""
    results = []
    for phrase in phrases:
        passed = phrase.lower() in output.lower()
        results.append(CheckResult(
            passed=passed,
            check_name=f"contains:'{phrase}'",
            message="" if passed else f"Missing required phrase: '{phrase}'"
        ))
    return results


def check_not_contains(output: str, phrases: list[str]) -> list[CheckResult]:
    """Verify output does NOT contain forbidden phrases."""
    results = []
    for phrase in phrases:
        passed = phrase.lower() not in output.lower()
        results.append(CheckResult(
            passed=passed,
            check_name=f"not_contains:'{phrase}'",
            message="" if passed else f"Forbidden phrase found: '{phrase}'"
        ))
    return results


def check_length(output: str, min_chars: int = 10, max_chars: int = 5000) -> CheckResult:
    """Verify output length is within bounds."""
    length = len(output)
    passed = min_chars <= length <= max_chars
    return CheckResult(
        passed=passed,
        check_name="length_check",
        message="" if passed else f"Length {length} outside [{min_chars}, {max_chars}]"
    )


def check_json_valid(output: str) -> CheckResult:
    """Verify output is valid JSON."""
    try:
        json.loads(output)
        return CheckResult(passed=True, check_name="json_valid", message="")
    except json.JSONDecodeError as e:
        return CheckResult(passed=False, check_name="json_valid", message=str(e))


def check_latency(latency_ms: float, max_ms: float = 5000) -> CheckResult:
    """Verify response time is within limit."""
    passed = latency_ms <= max_ms
    return CheckResult(
        passed=passed,
        check_name="latency",
        message="" if passed else f"Latency {latency_ms:.0f}ms > {max_ms}ms"
    )


def run_deterministic_checks(
    output: str,
    test_case: dict,
    latency_ms: float = 0
) -> tuple[bool, list[CheckResult]]:
    """Run all deterministic checks for a test case."""
    all_results = []

    # Required phrases
    if must_contain := test_case.get("must_contain", []):
        all_results.extend(check_contains(output, must_contain))

    # Forbidden phrases
    if must_not_contain := test_case.get("must_not_contain", []):
        all_results.extend(check_not_contains(output, must_not_contain))

    # JSON check (if required)
    if test_case.get("requires_json", False):
        all_results.append(check_json_valid(output))

    # Latency
    if latency_ms > 0:
        all_results.append(check_latency(latency_ms))

    overall_pass = all(r.passed for r in all_results)
    return overall_pass, all_results
```

---

## Step 3: Build the LLM Judge (1 hour)

```python
# eval/evaluators/llm_judge.py
import json
from anthropic import Anthropic

client = Anthropic()

JUDGE_PROMPT = """You are evaluating an AI assistant response.

User question: {question}
AI response: {response}
Quality criteria: {criteria}

Score the response from 1–10 based on the criteria.
Be strict: a 7 means "good but has room for improvement."
A 10 should be rare and genuinely excellent.

Respond with JSON only:
{{
  "score": <1-10>,
  "passed": <true if score >= 7>,
  "reasoning": "<one concise sentence>",
  "issues": ["<issue 1>", "<issue 2>"]  // empty if none
}}"""


def judge_response(
    question: str,
    response: str,
    criteria: str,
    judge_model: str = "claude-opus-4-6"
) -> dict:
    """
    Judge a response using LLM.
    Returns: {score, passed, reasoning, issues}
    """
    prompt = JUDGE_PROMPT.format(
        question=question,
        response=response,
        criteria=criteria
    )

    result = client.messages.create(
        model=judge_model,
        max_tokens=256,
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        return json.loads(result.content[0].text)
    except (json.JSONDecodeError, IndexError):
        return {
            "score": 5,
            "passed": False,
            "reasoning": "Judge parsing failed",
            "issues": ["Could not parse judge output"]
        }
```

---

## Step 4: Build the Pipeline Runner (1 hour)

```python
# eval/pipeline/runner.py
import json
import time
import pathlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field

from anthropic import Anthropic
from evaluators.deterministic import run_deterministic_checks
from evaluators.llm_judge import judge_response

client = Anthropic()


@dataclass
class EvalResult:
    test_id: str
    input: str
    output: str
    passed: bool
    det_passed: bool
    judge_score: float
    judge_passed: bool
    latency_ms: float
    failed_checks: list[str] = field(default_factory=list)
    judge_reasoning: str = ""
    error: str | None = None


def run_model(question: str) -> tuple[str, float]:
    """Call your actual LLM app. Replace with your real implementation."""
    start = time.time()
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        system="You are a helpful customer support agent for AcmeCorp.",
        messages=[{"role": "user", "content": question}]
    )
    latency_ms = (time.time() - start) * 1000
    return response.content[0].text, latency_ms


def evaluate_single(test_case: dict, use_llm_judge: bool = True) -> EvalResult:
    """Evaluate one test case end-to-end."""
    try:
        # Run the model
        output, latency_ms = run_model(test_case["input"])

        # Deterministic checks
        det_passed, det_results = run_deterministic_checks(output, test_case, latency_ms)
        failed_checks = [r.check_name for r in det_results if not r.passed]

        # LLM judge (only if deterministic checks pass, to save cost)
        judge_score = 0.0
        judge_passed = False
        judge_reasoning = ""
        if use_llm_judge and test_case.get("quality_criteria"):
            result = judge_response(
                question=test_case["input"],
                response=output,
                criteria=test_case["quality_criteria"]
            )
            judge_score = result["score"]
            judge_passed = result["passed"]
            judge_reasoning = result["reasoning"]

        overall_passed = det_passed and (judge_passed if use_llm_judge else True)

        return EvalResult(
            test_id=test_case["id"],
            input=test_case["input"],
            output=output,
            passed=overall_passed,
            det_passed=det_passed,
            judge_score=judge_score,
            judge_passed=judge_passed,
            latency_ms=latency_ms,
            failed_checks=failed_checks,
            judge_reasoning=judge_reasoning
        )

    except Exception as e:
        return EvalResult(
            test_id=test_case.get("id", "unknown"),
            input=test_case.get("input", ""),
            output="",
            passed=False,
            det_passed=False,
            judge_score=0.0,
            judge_passed=False,
            latency_ms=0.0,
            error=str(e)
        )


def run_pipeline(
    test_cases: list[dict],
    use_llm_judge: bool = True,
    max_workers: int = 5,
    tag_filter: str | None = None
) -> list[EvalResult]:
    """Run the full evaluation pipeline."""
    # Optionally filter by tag
    if tag_filter:
        test_cases = [tc for tc in test_cases if tag_filter in tc.get("tags", [])]

    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(evaluate_single, tc, use_llm_judge): tc
            for tc in test_cases
        }
        for i, future in enumerate(as_completed(futures)):
            result = future.result()
            results.append(result)
            status = "PASS" if result.passed else "FAIL"
            print(f"[{i+1}/{len(test_cases)}] {status} — {result.test_id}")

    return sorted(results, key=lambda r: r.test_id)
```

---

## Step 5: Add Reporting and CI Integration (1 hour)

```python
# eval/pipeline/reporter.py
import json
import sys
from datetime import datetime
from pathlib import Path


def generate_report(results: list, pass_rate_threshold: float = 0.85) -> dict:
    """Generate summary report and determine pass/fail."""
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    pass_rate = passed / total if total > 0 else 0

    avg_score = sum(r.judge_score for r in results if r.judge_score > 0)
    scored_count = sum(1 for r in results if r.judge_score > 0)
    avg_score = avg_score / scored_count if scored_count > 0 else 0

    avg_latency = sum(r.latency_ms for r in results) / total
    errors = [r for r in results if r.error]

    summary = {
        "timestamp": datetime.now().isoformat(),
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate": pass_rate,
        "avg_judge_score": round(avg_score, 2),
        "avg_latency_ms": round(avg_latency, 0),
        "error_count": len(errors),
        "ci_passed": pass_rate >= pass_rate_threshold
    }

    return summary


def print_summary(summary: dict, results: list):
    """Print human-readable report."""
    print(f"\n{'='*60}")
    print(f"EVAL REPORT — {summary['timestamp'][:19]}")
    print(f"{'='*60}")
    print(f"Result:   {'PASS' if summary['ci_passed'] else 'FAIL'}")
    print(f"Cases:    {summary['passed']}/{summary['total']} passed ({100*summary['pass_rate']:.1f}%)")
    print(f"Quality:  avg judge score {summary['avg_judge_score']:.1f}/10")
    print(f"Speed:    avg latency {summary['avg_latency_ms']:.0f}ms")
    print(f"Errors:   {summary['error_count']}")

    failures = [r for r in results if not r.passed]
    if failures:
        print(f"\nFAILURES ({len(failures)}):")
        for r in failures[:10]:  # show max 10
            checks = ", ".join(r.failed_checks) if r.failed_checks else ""
            judge_note = f"judge={r.judge_score}/10" if r.judge_score else ""
            print(f"  [{r.test_id}] {checks} {judge_note}")
            if r.judge_reasoning:
                print(f"    {r.judge_reasoning}")


def save_results(results: list, summary: dict, output_dir: str = "results"):
    """Save results to disk for trend analysis."""
    path = Path(output_dir)
    path.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = path / f"eval_{timestamp}.json"

    data = {
        "summary": summary,
        "results": [
            {
                "id": r.test_id,
                "passed": r.passed,
                "judge_score": r.judge_score,
                "latency_ms": r.latency_ms,
                "failed_checks": r.failed_checks,
                "judge_reasoning": r.judge_reasoning
            }
            for r in results
        ]
    }

    output_file.write_text(json.dumps(data, indent=2))
    print(f"\nResults saved to {output_file}")


def ci_exit(summary: dict):
    """Exit with appropriate code for CI."""
    if not summary["ci_passed"]:
        print(f"\nFAIL: Pass rate {summary['pass_rate']:.1%} below threshold")
        sys.exit(1)
    else:
        print(f"\nPASS: Pass rate {summary['pass_rate']:.1%}")
        sys.exit(0)
```

### Main Entry Point

```python
# eval/run_eval.py
import json
import argparse
from pathlib import Path

from pipeline.runner import run_pipeline
from pipeline.reporter import generate_report, print_summary, save_results, ci_exit


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="data/golden_set.json")
    parser.add_argument("--tag", help="Filter by tag (e.g., 'high-priority')")
    parser.add_argument("--no-judge", action="store_true", help="Skip LLM judge (faster)")
    parser.add_argument("--threshold", type=float, default=0.85)
    parser.add_argument("--ci", action="store_true", help="Exit with code 1 on failure")
    args = parser.parse_args()

    # Load test cases
    test_cases = json.loads(Path(args.dataset).read_text())
    print(f"Loaded {len(test_cases)} test cases from {args.dataset}")

    # Run pipeline
    results = run_pipeline(
        test_cases=test_cases,
        use_llm_judge=not args.no_judge,
        tag_filter=args.tag
    )

    # Report
    summary = generate_report(results, pass_rate_threshold=args.threshold)
    print_summary(summary, results)
    save_results(results, summary)

    # CI exit
    if args.ci:
        ci_exit(summary)


if __name__ == "__main__":
    main()
```

---

## Running the Pipeline

```bash
# Quick smoke test (no LLM judge)
python eval/run_eval.py --no-judge --tag high-priority

# Full eval with judge
python eval/run_eval.py

# CI mode (exits with code 1 if < 85% pass rate)
python eval/run_eval.py --ci --threshold 0.85

# Filter to safety tests only
python eval/run_eval.py --tag safety --ci --threshold 1.0  # 100% required for safety
```

---

## 📂 Navigation

- Parent: [08_Build_an_Eval_Pipeline](./)
- Project Guide: [Project_Guide.md](Project_Guide.md)
- Code Example: [Code_Example.md](Code_Example.md)
- Metrics Guide: [Metrics_Guide.md](Metrics_Guide.md)
- Previous: [07_Eval_Frameworks](../07_Eval_Frameworks/)
