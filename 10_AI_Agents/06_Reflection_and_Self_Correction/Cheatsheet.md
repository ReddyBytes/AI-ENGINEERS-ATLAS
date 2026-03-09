# Reflection and Self-Correction — Cheatsheet

**One-liner:** Reflection is when an agent critiques its own output and improves it — generate → evaluate → revise → repeat — using a critic LLM, test results, or explicit quality criteria.

---

## Key Terms

| Term | What it means |
|---|---|
| **Reflection** | The agent reviewing its own output to identify flaws and improve it |
| **Self-critique** | Asking the same LLM to evaluate its own response |
| **Reflexion** | A 2023 framework: Actor generates → Evaluator scores → Agent reflects on failures → Stores reflection → Tries again |
| **Actor** | The agent component that generates outputs and takes actions |
| **Evaluator** | The component that judges output quality (can be LLM, test runner, function) |
| **Self-reflection** | The agent's verbal analysis of what went wrong — stored as memory for the next attempt |
| **Iterative refinement** | Running the generate-critique-revise loop multiple times |
| **Critique prompt** | A prompt that asks the model to find problems in its own output |
| **Exit condition** | When to stop the reflection loop — quality threshold met or max iterations |
| **Ground truth feedback** | Objective feedback like test pass/fail — the strongest signal for self-correction |

---

## The Reflection Loop

```
Draft N → Critic → Issues found? → Yes → Revise → Draft N+1 → Critic → ...
                                 → No  → Final Output
```

Or with a hard stop:
```
for attempt in range(max_attempts):
    output = generate(task)
    critique = evaluate(output)
    if critique.is_acceptable:
        return output
    task = refine(task, critique)
return output  # Best attempt after max tries
```

---

## Types of Evaluators

| Evaluator | How it works | Best for |
|---|---|---|
| Same LLM (self-critique) | Ask the LLM to critique its own output | Writing, reasoning, structure |
| Separate critic LLM | Different model/persona evaluates | When self-critique is too lenient |
| Code test runner | Run code, check if tests pass | Code generation |
| Regex/format checker | Validate structure (JSON, email format) | Structured output generation |
| Human reviewer | Person approves or rejects | High-stakes outputs |

---

## Self-Critique Prompt Template

```python
critique_prompt = """
Review the following output and identify specific issues:

OUTPUT TO REVIEW:
{output}

EVALUATION CRITERIA:
{criteria}

List exactly what is wrong (be specific, not vague).
If there are no significant issues, say "ACCEPTABLE".
"""
```

---

## When to Use Reflection

**High value:**
- Code generation (tests as evaluator)
- Structured output (JSON, SQL, YAML)
- Factual writing that needs accuracy
- Long documents that need consistency

**Lower value:**
- Simple Q&A
- Creative writing without clear quality criteria
- When latency is critical (each reflection adds an LLM call)

---

## Golden Rules

1. **Always set a max reflection iterations.** Without a limit, the loop runs forever trying to reach perfect.

2. **Use objective evaluators when possible.** Test pass/fail > LLM critique > no evaluation.

3. **Store the reflection in memory.** The Reflexion framework insight: verbal self-critique stored as context dramatically improves the next attempt.

4. **Make critique specific.** "Improve the response" is bad. "The second paragraph has no supporting evidence — add 2 specific examples" is good.

5. **The exit condition matters as much as the loop.** Define "good enough" before you start. Perfect is the enemy of done.

6. **Don't just retry — reflect first.** Retrying without reflection often produces the same mistake again. The reflection is what drives improvement.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [05 Planning and Reasoning](../05_Planning_and_Reasoning/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [07 Multi-Agent Systems](../07_Multi_Agent_Systems/Theory.md)
