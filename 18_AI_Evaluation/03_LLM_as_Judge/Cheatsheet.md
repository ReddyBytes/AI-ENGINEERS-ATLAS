# LLM-as-Judge — Cheatsheet

## Key Terms

| Term | One-line meaning |
|------|-----------------|
| **LLM-as-judge** | Using a capable LLM to evaluate outputs of another AI system |
| **Absolute scoring** | Rate output on defined criteria (e.g., 1–5 scale) |
| **Pairwise comparison** | Which of two outputs (A vs B) is better? |
| **Reference-guided** | Compare output to a known ideal reference answer |
| **G-Eval** | Structured judge approach: rubric + CoT + multiple runs |
| **Position bias** | Judge prefers response A just because it appears first |
| **Length bias** | Judge prefers longer responses (looks more thorough) |
| **Self-preference** | GPT-4 judge preferring GPT-4 outputs |
| **Calibration** | Measuring agreement between LLM judge and human raters |
| **Cohen's Kappa** | Agreement metric corrected for chance; >0.6 is good |

---

## Minimal Judge Template

```python
import anthropic

client = anthropic.Anthropic()

def judge_response(question: str, response: str, criteria: dict[str, str]) -> dict:
    criteria_text = "\n".join([f"- {k}: {v}" for k, v in criteria.items()])

    prompt = f"""You are an expert evaluator. Rate the following AI response.

Question: {question}

AI Response:
{response}

Rate the response on these criteria (1-5 each):
{criteria_text}

First, think step by step about each criterion.
Then return ONLY JSON: {{"criterion_1": score, "reasoning": "..."}}"""

    r = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}]
    )
    import json
    raw = r.content[0].text.strip()
    if raw.startswith("```"):
        raw = "\n".join(raw.split("\n")[1:-1])
    return json.loads(raw)
```

---

## Absolute Scoring Format

```python
prompt = f"""
Question: {question}
Response to evaluate:
{response}

Score on scale 1–5:
- 5: Excellent — fully addresses question, accurate, clear
- 4: Good — mostly accurate, minor gaps
- 3: Adequate — partially correct, some issues
- 2: Poor — significant inaccuracies or missing info
- 1: Unacceptable — wrong, harmful, or off-topic

Think step by step, then return JSON: {{"score": int, "reasoning": "str"}}
"""
```

---

## Pairwise Comparison Format

```python
prompt = f"""
Question: {question}

Response A:
{response_a}

Response B:
{response_b}

Which response better answers the question? Consider accuracy, helpfulness, and clarity.
Think step by step, then return JSON:
{{"winner": "A" or "B" or "tie", "reasoning": "str"}}
"""
```

Always swap the order (A first, then B first) and average to control for position bias.

---

## Bias Mitigation Checklist

| Bias | Mitigation |
|------|-----------|
| Position bias (pairwise) | Run both orderings; average scores |
| Length bias | Explicitly instruct: "ignore length, rate content quality only" |
| Self-preference | Use a different model family as judge |
| Verbosity bias | "A concise correct answer scores higher than a verbose vague answer" |

---

## When to Trust LLM-as-Judge

| Trust level | Condition |
|-------------|-----------|
| High | Calibrated against >100 human examples; κ > 0.6 |
| Medium | Spot-checked against human raters; no obvious systematic bias |
| Low | No calibration; subjective criteria; small test set |
| Don't trust | Using same model as judge and evaluatee; no rubric |

---

## G-Eval Score Dimensions (Common Criteria)

| Criterion | What it measures |
|-----------|----------------|
| **Accuracy** | Factual correctness; no false claims |
| **Helpfulness** | Answers what was asked; actionable |
| **Relevance** | Stays on topic; no irrelevant content |
| **Clarity** | Easy to understand; well-organized |
| **Completeness** | Covers all important aspects |
| **Safety** | No harmful, offensive, or problematic content |
| **Faithfulness** | Only claims what's supported by source (RAG) |
| **Conciseness** | Appropriately brief; no unnecessary padding |

---

## Golden Rules

1. Always calibrate against human labels before trusting scores
2. Use a different model family as judge (not the same as what you're evaluating)
3. For pairwise: always run both orderings and average
4. Provide a clear rubric with score examples, not just a number scale
5. Use chain-of-thought reasoning in judge prompts — it improves consistency

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | LLM judge implementation |
| [📄 Prompt_Templates.md](./Prompt_Templates.md) | 5 judge prompt templates |

⬅️ **Prev:** [02 — Benchmarks](../02_Benchmarks/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 — RAG Evaluation](../04_RAG_Evaluation/Theory.md)
