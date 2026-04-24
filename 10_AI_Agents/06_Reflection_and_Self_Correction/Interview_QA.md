# Reflection and Self-Correction — Interview Q&A

## Beginner

**Q1: What is reflection in the context of AI agents?**

<details>
<summary>💡 Show Answer</summary>

Reflection is when an agent reviews and critiques its own output, then improves it.

Instead of generating one response and stopping, the agent:
1. Generates an initial output
2. Reviews it: "Is this correct? Is it complete? Is it the best I can do?"
3. Identifies specific problems
4. Revises the output based on those problems
5. Optionally repeats until the output meets a quality bar

It mirrors how humans edit their own work. A first draft is rarely the best version. The edit pass is what elevates quality.

</details>

---

<br>

**Q2: What is the Reflexion framework?**

<details>
<summary>💡 Show Answer</summary>

Reflexion (2023 paper) formalizes agent self-correction into three roles:

1. **Actor** — generates outputs and actions
2. **Evaluator** — judges the quality of the actor's output (could be an LLM, test runner, or function)
3. **Self-Reflection** — based on evaluator feedback, the actor writes a verbal analysis of what went wrong

The crucial insight: the self-reflection is stored in memory. The next attempt starts with "last time I tried this, here's what I did wrong and what I should do differently."

This is much more powerful than just "try again" — the agent learns from each failure within the task, not across training runs.

</details>

---

<br>

**Q3: Why is code generation a great use case for self-correction?**

<details>
<summary>💡 Show Answer</summary>

Code generation benefits from self-correction more than almost any other task because the **evaluator is objective**.

You don't need an LLM to judge if the code is good. You just run it:
- Tests pass → output is correct
- Tests fail → here's exactly what went wrong

The error message itself is the critique. "AttributeError: 'NoneType' object has no attribute 'strip'" tells the agent exactly what to fix.

This creates a tight, reliable feedback loop:
```
Write code → Run tests → Tests fail with error message →
Agent reads error → Agent fixes the specific issue →
Run tests again → Repeat until passing
```

No human judgment needed. The tests do the evaluating automatically.

</details>

---

## Intermediate

**Q4: How do you implement a self-critique loop in practice?**

<details>
<summary>💡 Show Answer</summary>

The core pattern:

```python
def reflection_loop(task, max_iterations=3):
    output = generate(task)

    for i in range(max_iterations):
        # Step 1: Generate critique
        critique = llm.invoke(f"""
            Review this output:
            {output}

            Identify: factual errors, logical gaps, missing content, quality issues.
            Be specific. If no issues, say ACCEPTABLE.
        """)

        # Step 2: Check if acceptable
        if "ACCEPTABLE" in critique:
            return output

        # Step 3: Revise based on critique
        output = llm.invoke(f"""
            Original task: {task}
            Previous output: {output}
            Critique: {critique}

            Write an improved version that addresses all the issues in the critique.
        """)

    return output  # Best attempt after max iterations
```

The loop is: generate → critique → revise → repeat.

</details>

---

<br>

**Q5: What are the different types of evaluators and when do you choose each?**

<details>
<summary>💡 Show Answer</summary>

| Evaluator Type | When to use | Example |
|---|---|---|
| Same LLM (self-critique) | Writing, reasoning, open-ended tasks | "Review your essay for logical gaps" |
| Separate critic LLM | When self-critique is too lenient or biased | Different prompt persona: "You are a harsh critic..." |
| Test runner | Code generation | pytest results |
| Format validator | Structured output (JSON, SQL, YAML) | JSON schema validation |
| Semantic similarity | When output must match a reference | Embedding-based distance from expected |
| Human evaluator | High-stakes outputs | Review queue before publishing |

For code: use test runner (objective, fast, precise).
For writing: use LLM critic (flexible, but may be too lenient on its own work).
For structured data: use schema validation (instant, deterministic).

</details>

---

<br>

**Q6: What's the difference between reflection and fine-tuning?**

<details>
<summary>💡 Show Answer</summary>

**Reflection** happens at inference time — during a single task run. The agent critiques and improves its output right now, for this specific task. It doesn't update the model weights. The improvement only applies to this one run.

**Fine-tuning** happens at training time. You use examples of good/bad outputs to update the model's weights permanently. Every future inference benefits from what was learned.

They're complementary:
- Reflection is immediate, cheap, and task-specific
- Fine-tuning is permanent, expensive, and general

A practical workflow: use reflection to generate high-quality outputs → collect those examples → use them to fine-tune the model → the fine-tuned model needs less reflection on similar future tasks.

</details>

---

## Advanced

**Q7: How does the Reflexion framework store and use reflections across attempts?**

<details>
<summary>💡 Show Answer</summary>

In Reflexion, the self-reflection is stored as a text string and injected into the next attempt's context.

```python
reflections = []

for attempt in range(max_attempts):
    # Build context with previous reflections
    if reflections:
        reflection_context = "Previous attempts and what went wrong:\n" + "\n".join(reflections)
    else:
        reflection_context = ""

    # Generate output with reflection context
    output = actor.generate(task, context=reflection_context)

    # Evaluate
    score = evaluator.evaluate(output, task)

    if score >= threshold:
        return output  # Success

    # Generate reflection on the failure
    reflection = actor.reflect(
        task=task,
        output=output,
        score=score,
        feedback=evaluator.get_feedback()
    )
    reflections.append(f"Attempt {attempt+1}: {reflection}")

return output  # Best attempt
```

The reflections accumulate. By attempt 3, the agent has a record of two failed attempts and their specific failure modes. This guides the third attempt away from those same mistakes.

</details>

---

<br>

**Q8: What are the failure modes of self-correction and how do you mitigate them?**

<details>
<summary>💡 Show Answer</summary>

1. **Sycophantic critique** — the model is too lenient on its own work. "This is great! Maybe slightly improve X." Mitigation: use a separate critic model with a harsh persona, or use objective evaluators (tests).

2. **Infinite loop** — the model keeps finding new things to "fix" without converging. Mitigation: hard max iteration limit; define "acceptable" criteria upfront.

3. **Over-correction** — the model changes something that was correct based on a false critique. Mitigation: preserve parts the critique says are fine; only modify what the critique flags.

4. **Degradation** — after several revisions, the output gets worse. Sometimes revision iteration makes things overly complex or loses clarity. Mitigation: keep all versions, evaluate each, return the best one (not just the last).

5. **Reflection without change** — agent identifies the issue but makes the same mistake in the revision. Mitigation: require the agent to explicitly state what it will change before generating the revision.

</details>

---

<br>

**Q9: How would you design a self-correcting code generation agent for production?**

<details>
<summary>💡 Show Answer</summary>

Architecture:

```
User request
     ↓
Code Generator (LLM)
     ↓
[Code output]
     ↓
Sandbox Executor (runs code in isolated environment)
     ↓
Test Results:
  - PASS → Return code
  - FAIL (syntax error) → Fix syntax, re-run (no LLM needed)
  - FAIL (test failures) → Self-reflection → Revise code → Re-run
  - FAIL (security violation) → Reject, regenerate with stricter constraints
     ↓
[Max 5 attempts] → Return best attempt with test report
```

Key production considerations:
1. **Sandbox everything** — never run agent-generated code outside an isolated environment
2. **Resource limits** — timeout (30s), memory cap, no network access from sandbox
3. **Test quality matters** — the agent can only fix what the tests can detect
4. **Log everything** — every attempt, every error, every reflection for debugging
5. **Rate limiting** — max N corrections per user per hour to prevent abuse
6. **Graceful degradation** — if all attempts fail, return the best partial solution with an explanation of what doesn't work yet

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [05 Planning and Reasoning](../05_Planning_and_Reasoning/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [07 Multi-Agent Systems](../07_Multi_Agent_Systems/Theory.md)
