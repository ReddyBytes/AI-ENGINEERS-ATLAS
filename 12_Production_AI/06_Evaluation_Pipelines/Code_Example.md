# Code Example — Evaluation Pipelines

Complete, runnable Python examples for building evaluation pipelines.

---

## Pattern 1: Simple LLM-as-Judge Evaluation Pipeline

```python
"""
Simple evaluation pipeline using LLM-as-judge.
Runs a test set, scores with Claude, reports pass/fail.
Requirements: pip install anthropic
"""
import json
import time
from dataclasses import dataclass
from typing import Optional
import anthropic

client = anthropic.Anthropic()

# ─── Test Dataset ────────────────────────────────────────────────────────────
# Format: list of (question, reference_answer) pairs
TEST_CASES = [
    {
        "id": "tc_001",
        "question": "What is the capital of France?",
        "reference": "Paris is the capital of France.",
        "category": "geography"
    },
    {
        "id": "tc_002",
        "question": "Explain what a neural network is in simple terms.",
        "reference": "A neural network is a computing system inspired by the human brain, made up of connected nodes that process information and learn from examples.",
        "category": "ml_concepts"
    },
    {
        "id": "tc_003",
        "question": "What does HTTP stand for?",
        "reference": "HTTP stands for HyperText Transfer Protocol, the foundation of data communication on the web.",
        "category": "technology"
    },
    # Add more test cases from your actual use cases
]

# ─── Model Being Evaluated ───────────────────────────────────────────────────
SYSTEM_PROMPT = "You are a helpful assistant. Answer questions clearly and concisely."

def run_model(question: str) -> str:
    """Run the model being evaluated."""
    response = client.messages.create(
        model="claude-3-haiku-20240307",  # Model under evaluation
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": question}]
    )
    return response.content[0].text

# ─── LLM Judge ───────────────────────────────────────────────────────────────
JUDGE_PROMPT = """You are an expert evaluator. Evaluate the quality of this AI response.

Question: {question}
Reference Answer: {reference}
Model Response: {response}

Rate the response on these criteria (1-5 each, where 5 = excellent):
- accuracy: Is the information factually correct?
- completeness: Does it cover the key points from the reference?
- clarity: Is it well-written and easy to understand?
- helpfulness: Would this answer satisfy someone asking the question?

Return ONLY valid JSON with this format:
{{"accuracy": int, "completeness": int, "clarity": int, "helpfulness": int, "overall": int, "pass": bool, "reasoning": "brief explanation"}}

Set "pass" to true if overall >= 4, false otherwise."""

def llm_judge(question: str, reference: str, response: str) -> dict:
    """Use Claude Sonnet as judge to evaluate a response."""
    judge_input = JUDGE_PROMPT.format(
        question=question,
        reference=reference,
        response=response
    )

    judge_response = client.messages.create(
        model="claude-3-5-sonnet-20241022",  # Use a different/stronger model as judge
        max_tokens=256,
        messages=[{"role": "user", "content": judge_input}]
    )

    try:
        return json.loads(judge_response.content[0].text)
    except json.JSONDecodeError:
        return {"overall": 1, "pass": False, "reasoning": "Judge returned invalid JSON"}

# ─── Evaluation Runner ────────────────────────────────────────────────────────
@dataclass
class EvalResult:
    test_case_id: str
    question: str
    model_response: str
    scores: dict
    passed: bool
    latency_ms: float

def run_evaluation(test_cases: list, pass_threshold: float = 0.90) -> dict:
    """
    Run full evaluation pipeline.
    Returns a report with pass rate and detailed results.
    """
    results = []

    print(f"Running evaluation on {len(test_cases)} test cases...")

    for i, tc in enumerate(test_cases):
        print(f"  [{i+1}/{len(test_cases)}] {tc['id']}: {tc['question'][:50]}...")

        # Run the model
        start = time.time()
        model_response = run_model(tc["question"])
        latency_ms = (time.time() - start) * 1000

        # Judge the response
        scores = llm_judge(tc["question"], tc["reference"], model_response)

        results.append(EvalResult(
            test_case_id=tc["id"],
            question=tc["question"],
            model_response=model_response,
            scores=scores,
            passed=scores.get("pass", False),
            latency_ms=latency_ms
        ))

    # ─── Generate Report ─────────────────────────────────────────────────────
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    pass_rate = passed / total
    avg_overall = sum(r.scores.get("overall", 0) for r in results) / total

    # Failures
    failures = [r for r in results if not r.passed]

    report = {
        "summary": {
            "total": total,
            "passed": passed,
            "failed": len(failures),
            "pass_rate": round(pass_rate, 3),
            "avg_score": round(avg_overall, 2),
            "threshold": pass_threshold,
            "gate_passed": pass_rate >= pass_threshold
        },
        "failures": [
            {
                "id": r.test_case_id,
                "question": r.question,
                "response": r.model_response[:200],
                "scores": r.scores,
                "reasoning": r.scores.get("reasoning", "")
            }
            for r in failures
        ],
        "all_results": [
            {
                "id": r.test_case_id,
                "passed": r.passed,
                "overall_score": r.scores.get("overall"),
                "latency_ms": r.latency_ms
            }
            for r in results
        ]
    }

    return report

def print_report(report: dict):
    """Print a human-readable evaluation report."""
    s = report["summary"]
    print(f"\n{'='*50}")
    print(f"EVALUATION REPORT")
    print(f"{'='*50}")
    print(f"Pass rate:    {s['pass_rate']:.1%}  (threshold: {s['threshold']:.1%})")
    print(f"Avg score:    {s['avg_score']}/5")
    print(f"Results:      {s['passed']}/{s['total']} passed")
    print(f"Gate status:  {'✅ PASSED' if s['gate_passed'] else '❌ FAILED — DO NOT DEPLOY'}")

    if report["failures"]:
        print(f"\nFAILURES ({len(report['failures'])} cases):")
        for f in report["failures"][:3]:  # Show first 3 failures
            print(f"  [{f['id']}] {f['question'][:60]}")
            print(f"    Score: {f['scores'].get('overall')}/5 — {f['reasoning'][:100]}")
    print(f"{'='*50}\n")

# ─── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    report = run_evaluation(TEST_CASES, pass_threshold=0.90)
    print_report(report)

    # Save detailed results
    with open("eval_results.json", "w") as f:
        json.dump(report, f, indent=2)
    print("Detailed results saved to eval_results.json")

    # Exit with non-zero code if eval failed (for CI/CD integration)
    import sys
    if not report["summary"]["gate_passed"]:
        sys.exit(1)
```

---

## Pattern 2: RAGAS Evaluation for RAG Systems

```python
"""
RAG system evaluation using the RAGAS framework.
Evaluates faithfulness, answer relevance, context precision, and recall.
Requirements: pip install ragas langchain anthropic
"""
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)
from datasets import Dataset

# ─── Your RAG pipeline output ────────────────────────────────────────────────
# Collect these from running your RAG system on test questions
rag_results = {
    "question": [
        "What is the return policy for electronics?",
        "How do I cancel my subscription?",
        "What payment methods do you accept?",
    ],
    "answer": [
        "Electronics can be returned within 30 days of purchase with original packaging.",
        "You can cancel your subscription from the Account Settings page at any time.",
        "We accept Visa, Mastercard, American Express, and PayPal.",
    ],
    "contexts": [
        # Retrieved context chunks used to generate each answer
        ["Our return policy: Electronics and appliances may be returned within 30 days "
         "of the original purchase date. Items must be in original packaging."],
        ["Account management: Navigate to Settings > Subscription > Cancel. "
         "Cancellations take effect at the end of the billing period."],
        ["Payment methods accepted: We accept all major credit cards (Visa, MC, Amex), "
         "PayPal, and bank transfers for orders over $500."],
    ],
    "ground_truths": [
        # Optional: known correct answers for context recall calculation
        ["Electronics have a 30-day return window and must be in original packaging."],
        ["Cancel from Account Settings page; cancellations are at end of billing period."],
        ["Accepted: Visa, Mastercard, American Express, PayPal, and bank transfer for large orders."],
    ]
}

def run_ragas_evaluation():
    """Run RAGAS evaluation on RAG pipeline outputs."""
    dataset = Dataset.from_dict(rag_results)

    results = evaluate(
        dataset=dataset,
        metrics=[
            faithfulness,       # Does answer contradict the context?
            answer_relevancy,   # Does answer address the question?
            context_precision,  # Are retrieved chunks relevant?
            context_recall,     # Did we retrieve all needed info?
        ]
    )

    print("RAGAS Evaluation Results:")
    print(f"  Faithfulness:       {results['faithfulness']:.3f}  (target: > 0.85)")
    print(f"  Answer Relevancy:   {results['answer_relevancy']:.3f}  (target: > 0.80)")
    print(f"  Context Precision:  {results['context_precision']:.3f}  (target: > 0.75)")
    print(f"  Context Recall:     {results['context_recall']:.3f}  (target: > 0.70)")

    # Convert to DataFrame for detailed analysis
    df = results.to_pandas()

    # Find low-faithfulness answers (potential hallucinations)
    low_faithfulness = df[df['faithfulness'] < 0.7]
    if not low_faithfulness.empty:
        print(f"\nWarning: {len(low_faithfulness)} answers have low faithfulness:")
        for _, row in low_faithfulness.iterrows():
            print(f"  Q: {row['question'][:60]}")
            print(f"  Faithfulness: {row['faithfulness']:.2f}")

    return results

if __name__ == "__main__":
    results = run_ragas_evaluation()
```

---

## Pattern 3: A/B Evaluation Between Two Prompts

```python
"""
A/B evaluation: compare two prompt versions on the same test set.
Determines which prompt produces better responses.
Requirements: pip install anthropic scipy
"""
import json
from scipy import stats
import anthropic

client = anthropic.Anthropic()

# Two prompt versions to compare
PROMPT_A = "Answer the following question concisely and accurately."
PROMPT_B = "You are an expert. Answer the following question with clear reasoning. Be thorough but concise."

TEST_QUESTIONS = [
    "What causes inflation?",
    "Explain recursion in programming.",
    "How does a vaccine work?",
    "What is the difference between a list and a tuple in Python?",
    "Why is the sky blue?",
]

JUDGE_COMPARISON_PROMPT = """Compare these two responses to the same question and pick the better one.

Question: {question}
Response A: {response_a}
Response B: {response_b}

Which response is better overall? Consider: accuracy, clarity, and helpfulness.
Return ONLY JSON: {{"winner": "A" or "B", "margin": "slight" or "clear", "reasoning": "brief explanation"}}"""

def get_response(question: str, system_prompt: str) -> str:
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=256,
        system=system_prompt,
        messages=[{"role": "user", "content": question}]
    )
    return response.content[0].text

def compare_responses(question: str, response_a: str, response_b: str) -> dict:
    judge_input = JUDGE_COMPARISON_PROMPT.format(
        question=question, response_a=response_a, response_b=response_b
    )
    result = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=128,
        messages=[{"role": "user", "content": judge_input}]
    )
    try:
        return json.loads(result.content[0].text)
    except:
        return {"winner": "A", "margin": "slight", "reasoning": "parse error"}

def run_ab_eval():
    results = []
    for q in TEST_QUESTIONS:
        # Run both prompts
        resp_a = get_response(q, PROMPT_A)
        resp_b = get_response(q, PROMPT_B)

        # Randomize order to reduce position bias
        import random
        if random.random() > 0.5:
            comparison = compare_responses(q, resp_a, resp_b)
        else:
            comparison = compare_responses(q, resp_b, resp_a)
            comparison["winner"] = "B" if comparison["winner"] == "A" else "A"

        results.append({"question": q, "winner": comparison["winner"],
                        "reasoning": comparison["reasoning"]})
        print(f"  Q: {q[:50]} → Winner: Prompt {comparison['winner']}")

    wins_a = sum(1 for r in results if r["winner"] == "A")
    wins_b = sum(1 for r in results if r["winner"] == "B")

    print(f"\nA/B Test Results:")
    print(f"  Prompt A wins: {wins_a}/{len(results)}")
    print(f"  Prompt B wins: {wins_b}/{len(results)}")

    if wins_b > wins_a:
        print(f"  → Recommend: Deploy Prompt B")
    else:
        print(f"  → Recommend: Keep Prompt A")

if __name__ == "__main__":
    run_ab_eval()
```

---

## 📂 Navigation
