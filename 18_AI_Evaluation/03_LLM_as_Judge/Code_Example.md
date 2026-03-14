# LLM-as-Judge — Code Example

## Complete LLM Judge Implementation

```python
"""
llm_judge.py — Production-ready LLM-as-judge evaluation framework
pip install anthropic
"""
import anthropic
import json
import time
from dataclasses import dataclass
from typing import Optional


client = anthropic.Anthropic()


@dataclass
class JudgeResult:
    """Result from a judge evaluation."""
    scores: dict[str, int]        # criterion → score (1–5)
    reasoning: str                 # explanation
    overall: float                 # weighted average
    raw_response: str              # full judge response


# ──────────────────────────────────────────────
# Core judge function
# ──────────────────────────────────────────────

def judge_absolute(
    question: str,
    response: str,
    criteria: dict[str, str],
    reference: Optional[str] = None,
    model: str = "claude-opus-4-6",
) -> JudgeResult:
    """
    Evaluate a response using absolute scoring.

    Args:
        question: The original user question
        response: The AI system's response to evaluate
        criteria: Dict of {criterion_name: criterion_description}
        reference: Optional ideal reference answer
        model: The judge model to use

    Returns: JudgeResult with scores and reasoning
    """
    criteria_text = "\n".join([f"- **{k}**: {v}" for k, v in criteria.items()])
    criteria_schema = {k: "int (1-5)" for k in criteria}
    criteria_schema["reasoning"] = "str (brief explanation)"

    reference_section = ""
    if reference:
        reference_section = f"\n\nReference answer (ideal response):\n{reference}\n"

    prompt = f"""You are an expert AI response evaluator. Your job is to rate AI responses objectively.

## Question asked:
{question}
{reference_section}
## Response to evaluate:
{response}

## Evaluation criteria (rate each 1–5):
{criteria_text}

## Scoring scale:
- 5: Excellent — exceeds expectations
- 4: Good — meets expectations with minor gaps
- 3: Adequate — partially meets expectations
- 2: Poor — significantly falls short
- 1: Unacceptable — completely fails

## Instructions:
1. First, think through each criterion carefully
2. Consider concrete evidence from the response
3. Assign scores based on the rubric above
4. Return ONLY a valid JSON object with this structure:
{json.dumps(criteria_schema, indent=2)}

Important: Ignore response length. A concise correct answer is as good as a long correct answer."""

    r = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = r.content[0].text.strip()
    if raw.startswith("```"):
        raw = "\n".join(raw.split("\n")[1:-1])

    data = json.loads(raw)
    reasoning = data.pop("reasoning", "")

    # Calculate weighted average
    scores = {k: v for k, v in data.items() if k in criteria}
    overall = sum(scores.values()) / len(scores) if scores else 0.0

    return JudgeResult(
        scores=scores,
        reasoning=reasoning,
        overall=overall,
        raw_response=r.content[0].text
    )


def judge_pairwise(
    question: str,
    response_a: str,
    response_b: str,
    criteria_description: str = "accuracy, helpfulness, and clarity",
    model: str = "claude-opus-4-6",
) -> dict:
    """
    Compare two responses and determine which is better.
    Runs both orderings to control for position bias.

    Returns dict with: winner, confidence, reasoning
    """

    def run_comparison(resp1: str, resp2: str, label1: str, label2: str) -> dict:
        prompt = f"""You are an expert AI response evaluator.

Question: {question}

Response {label1}:
{resp1}

Response {label2}:
{resp2}

Compare these two responses on: {criteria_description}

Think step by step about the strengths and weaknesses of each response.
Then return ONLY JSON:
{{"winner": "{label1}" or "{label2}" or "tie", "margin": "clear" or "slight", "reasoning": "str"}}"""

        r = client.messages.create(
            model=model, max_tokens=512,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = r.content[0].text.strip()
        if raw.startswith("```"):
            raw = "\n".join(raw.split("\n")[1:-1])
        return json.loads(raw)

    # Run both orderings
    result_ab = run_comparison(response_a, response_b, "A", "B")
    time.sleep(0.5)  # Brief pause between calls
    result_ba = run_comparison(response_b, response_a, "B", "A")

    # Normalize BA result (if A won in BA ordering, it means original response_b won)
    # Map back to original A/B labels
    if result_ba["winner"] == "B":  # B in BA = original A
        result_ba_normalized = "A"
    elif result_ba["winner"] == "A":  # A in BA = original B
        result_ba_normalized = "B"
    else:
        result_ba_normalized = "tie"

    # Determine consensus
    if result_ab["winner"] == result_ba_normalized:
        winner = result_ab["winner"]
        confidence = "high" if result_ab.get("margin") == "clear" else "medium"
    else:
        # Disagree — call it a tie
        winner = "tie"
        confidence = "low"

    return {
        "winner": winner,
        "confidence": confidence,
        "reasoning_ab": result_ab["reasoning"],
        "reasoning_ba": result_ba["reasoning"],
        "raw": {"ab": result_ab, "ba": result_ba}
    }


# ──────────────────────────────────────────────
# Batch evaluation
# ──────────────────────────────────────────────

def evaluate_batch(
    examples: list[dict],
    criteria: dict[str, str],
    max_workers: int = 5,
) -> list[dict]:
    """
    Run judge evaluation on a batch of examples in parallel.

    Each example should have: question, response (and optionally reference)
    Returns list of examples enriched with judge scores.
    """
    import concurrent.futures

    def evaluate_one(example: dict) -> dict:
        result = judge_absolute(
            question=example["question"],
            response=example["response"],
            criteria=criteria,
            reference=example.get("reference"),
        )
        return {
            **example,
            "scores": result.scores,
            "overall": result.overall,
            "judge_reasoning": result.reasoning,
        }

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(evaluate_one, examples))

    return results


def print_eval_summary(results: list[dict], criteria: dict[str, str]):
    """Print a summary of batch evaluation results."""
    print(f"\n{'='*50}")
    print(f"Evaluation Summary ({len(results)} examples)")
    print(f"{'='*50}")

    # Per-criterion averages
    for criterion in criteria:
        scores = [r["scores"].get(criterion, 0) for r in results]
        avg = sum(scores) / len(scores) if scores else 0
        print(f"  {criterion}: {avg:.2f}/5.0")

    # Overall
    overall_scores = [r["overall"] for r in results]
    print(f"\n  Overall: {sum(overall_scores)/len(overall_scores):.2f}/5.0")

    # Distribution
    score_dist = {}
    for r in results:
        score = round(r["overall"])
        score_dist[score] = score_dist.get(score, 0) + 1
    print("\n  Score distribution:")
    for score in sorted(score_dist):
        bar = "█" * score_dist[score]
        print(f"    {score}: {bar} ({score_dist[score]})")


# ──────────────────────────────────────────────
# Demo
# ──────────────────────────────────────────────

if __name__ == "__main__":
    # Define evaluation criteria
    SUPPORT_CRITERIA = {
        "accuracy": "Is the information factually correct? Does it match the actual policy?",
        "helpfulness": "Does it actually solve the customer's problem? Is it actionable?",
        "tone": "Is the tone professional, empathetic, and appropriate for customer support?"
    }

    # Test examples
    test_cases = [
        {
            "question": "Can I return a product after 30 days?",
            "response": "Returns are accepted within 30 days of purchase with original receipt. After 30 days, we cannot process returns unless the item is defective. Please contact our support team with your order number.",
            "reference": "Our standard return policy is 30 days with receipt. Defective items have extended coverage."
        },
        {
            "question": "My order hasn't arrived, what should I do?",
            "response": "That sucks. Try waiting longer.",
            "reference": "For delayed orders, customers should track their order, contact the carrier, and if still unresolved, contact support with their order number."
        },
        {
            "question": "How do I update my billing information?",
            "response": "You can update your billing information by going to Account Settings → Payment Methods. Click 'Edit' next to your current payment method or 'Add New Method' to add a new one. Changes take effect immediately for future orders.",
        }
    ]

    print("Running absolute scoring evaluation...")
    results = evaluate_batch(test_cases, SUPPORT_CRITERIA)
    print_eval_summary(results, SUPPORT_CRITERIA)

    # Show failing cases
    print("\nLow-scoring responses (overall < 3):")
    for r in results:
        if r["overall"] < 3:
            print(f"\n  Q: {r['question'][:60]}...")
            print(f"  Overall: {r['overall']:.1f}")
            print(f"  Reason: {r['judge_reasoning'][:150]}...")

    # Pairwise comparison example
    print("\n\nRunning pairwise comparison...")
    pairwise_result = judge_pairwise(
        question="What is machine learning?",
        response_a="Machine learning is a subset of artificial intelligence that enables systems to learn from data.",
        response_b="Machine learning is when computers learn patterns from data to make predictions or decisions, without being explicitly programmed for each task. For example, a spam filter learns from millions of emails to recognize spam.",
    )
    print(f"Winner: {pairwise_result['winner']} (confidence: {pairwise_result['confidence']})")
    print(f"Reasoning (AB): {pairwise_result['reasoning_ab'][:200]}...")
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |
| [📄 Prompt_Templates.md](./Prompt_Templates.md) | 5 judge prompt templates |

⬅️ **Prev:** [02 — Benchmarks](../02_Benchmarks/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 — RAG Evaluation](../04_RAG_Evaluation/Theory.md)
