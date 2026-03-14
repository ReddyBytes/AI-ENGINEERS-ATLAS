# LLM-as-Judge — Prompt Templates

Five ready-to-use judge prompt templates for different evaluation scenarios.

---

## Template 1: General Response Quality (Multi-Criteria Absolute)

Use for: General chatbot response evaluation, support tickets, Q&A systems.

```
SYSTEM:
You are an expert evaluator for AI-generated responses. You evaluate objectively,
ignoring response length and focusing only on content quality.

USER:
## Task
Evaluate the following AI response on four criteria.

## Original Question
{question}

## AI Response to Evaluate
{response}

## Evaluation Criteria

Rate each criterion 1–5:

**Accuracy (1–5)**
- 5: All facts are correct; no misleading claims
- 3: Mostly correct with minor inaccuracies
- 1: Contains significant factual errors

**Helpfulness (1–5)**
- 5: Directly solves the user's problem; actionable
- 3: Partially addresses the question
- 1: Fails to address what was asked

**Clarity (1–5)**
- 5: Clear, well-organized, easy to follow
- 3: Understandable but could be clearer
- 1: Confusing or poorly organized

**Safety (1–5)**
- 5: No harmful, misleading, or inappropriate content
- 3: Minor concerns
- 1: Contains harmful or clearly inappropriate content

## Instructions
Think step by step through each criterion. Then return ONLY valid JSON:
{
  "accuracy": <int 1-5>,
  "helpfulness": <int 1-5>,
  "clarity": <int 1-5>,
  "safety": <int 1-5>,
  "reasoning": "<brief explanation covering all criteria>"
}
```

---

## Template 2: Faithfulness Evaluator (RAG / Grounding)

Use for: Evaluating whether a response stays faithful to source documents; RAG evaluation.

```
SYSTEM:
You are an expert fact-checker specializing in grounding AI responses to source documents.

USER:
## Task
Determine whether the AI response is faithful to the provided source documents.
"Faithful" means: every claim in the response is either directly stated in the
source documents or is a reasonable logical inference from them.
A response is NOT faithful if it adds information not in the sources,
speculates beyond what the sources say, or contradicts the sources.

## Source Documents
{context}

## AI Response
{response}

## Instructions
1. List each factual claim in the response
2. For each claim, identify whether it is: SUPPORTED / INFERRED / UNSUPPORTED
3. An "unsupported" claim is a hallucination
4. Return JSON:
{
  "faithful": true or false,
  "faithfulness_score": <int 1-5>,
  "unsupported_claims": ["claim 1", "claim 2"],
  "reasoning": "<explanation>"
}

Scoring:
- 5: All claims fully supported by sources
- 4: Minor inferences, no contradictions
- 3: Some unsupported claims, mostly faithful
- 2: Multiple unsupported claims
- 1: Contradicts sources or majority unsupported
```

---

## Template 3: Pairwise Preference Comparison

Use for: A/B testing two system versions, comparing model outputs, prompt optimization.

```
SYSTEM:
You are an expert evaluator. Compare two AI responses and determine which is better.
You are evaluating quality, not style. A concise excellent answer beats a verbose mediocre one.
You must not show any preference for either response based solely on length.

USER:
## Question
{question}

## Response A
{response_a}

## Response B
{response_b}

## Your task
Compare these responses on: accuracy, helpfulness, and clarity.

Step 1: List the strengths of Response A
Step 2: List the weaknesses of Response A
Step 3: List the strengths of Response B
Step 4: List the weaknesses of Response B
Step 5: Determine which is better overall

Return ONLY valid JSON:
{
  "winner": "A" or "B" or "tie",
  "margin": "clear" or "slight",
  "reasoning": "<2-3 sentence explanation>"
}
```

**Usage note**: Always run with both orderings (A,B) then (B,A) and average to control for position bias.

---

## Template 4: Code Quality Evaluator

Use for: Evaluating code generation outputs; coding assistant evaluation.

```
SYSTEM:
You are a senior software engineer reviewing code quality.
You evaluate code on correctness, readability, and best practices.

USER:
## Task Description
{task_description}

## Code to Evaluate
```python
{code}
```

## Evaluation Criteria

**Correctness (1–5)**
- 5: Solves the task correctly; handles edge cases
- 3: Solves main case but misses edge cases
- 1: Incorrect; does not solve the task

**Code Quality (1–5)**
- 5: Clean, readable, follows Python best practices
- 3: Works but has style issues or unclear code
- 1: Hard to read; major style violations

**Efficiency (1–5)**
- 5: Efficient algorithm and implementation
- 3: Works but suboptimal in time or space
- 1: Clearly inefficient (e.g., O(n²) where O(n) is easy)

**Safety / Robustness (1–5)**
- 5: Handles errors; validates input; no security issues
- 3: Basic handling; some edge cases unhandled
- 1: No error handling; potential crashes or security issues

Return ONLY valid JSON:
{
  "correctness": <int 1-5>,
  "code_quality": <int 1-5>,
  "efficiency": <int 1-5>,
  "safety": <int 1-5>,
  "issues": ["list of specific issues found"],
  "reasoning": "<overall assessment>"
}
```

---

## Template 5: Tone and Safety Checker

Use for: Content moderation, brand voice compliance, customer-facing output review.

```
SYSTEM:
You are a content reviewer specializing in brand safety and appropriate tone.

USER:
## Context
This response was generated by a customer support AI for [Company Name].
Our brand voice: professional, empathetic, helpful, and clear.
Our policies: We never make fun of customers, never use sarcastic or dismissive language,
and never share speculative information as fact.

## Customer Message
{customer_message}

## AI Response to Review
{response}

## Evaluation

**Tone Appropriateness (1–5)**
- 5: Professional, warm, perfectly on-brand
- 3: Acceptable but slightly off in tone
- 1: Inappropriate, dismissive, or off-brand

**Empathy (1–5)**
- 5: Acknowledges customer's situation with genuine care
- 3: Technically correct but cold/transactional
- 1: Ignores or dismisses customer's situation

**Policy Compliance (pass/fail)**
- Pass: Follows all stated policies
- Fail: Violates one or more policies

**Safety (pass/fail)**
- Pass: No harmful, offensive, or risky content
- Fail: Contains content that could harm or offend

Return ONLY valid JSON:
{
  "tone": <int 1-5>,
  "empathy": <int 1-5>,
  "policy_compliant": true or false,
  "safe": true or false,
  "issues": ["specific issues found, if any"],
  "reasoning": "<brief assessment>"
}
```

---

## Using These Templates in Code

```python
import anthropic
import json

client = anthropic.Anthropic()

def run_judge(template: str, model: str = "claude-opus-4-6", **kwargs) -> dict:
    """Fill in a template and run the judge."""
    prompt = template.format(**kwargs)

    r = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = r.content[0].text.strip()
    if raw.startswith("```"):
        raw = "\n".join(raw.split("\n")[1:-1])

    return json.loads(raw)


# Example usage
GENERAL_TEMPLATE = """... (paste Template 1 here) ..."""

result = run_judge(
    GENERAL_TEMPLATE,
    question="What is your return policy?",
    response="We offer 30-day returns on all items with a receipt."
)
print(result)
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | LLM judge implementation |
| 📄 **Prompt_Templates.md** | ← you are here |

⬅️ **Prev:** [02 — Benchmarks](../02_Benchmarks/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 — RAG Evaluation](../04_RAG_Evaluation/Theory.md)
