# Reflection and Self-Correction — Theory

You've written a 5-paragraph essay. You read it back: "This paragraph doesn't support my thesis." Rewrite. Read again: "The introduction is weak." Fix it. You didn't just write and submit — you wrote, critiqued your own work, then improved it. That self-correction loop is what separates a good essay from a great one.

AI agents can do the same thing: generate output, evaluate it, find problems, and fix them automatically.

👉 This is why we need **Reflection and Self-Correction** — it lets agents improve their own outputs through iterative critique, just like a thoughtful human would.

---

## What Is Reflection?

Reflection is a second LLM call (or second pass) that acts as a **critic** — reads the output, identifies problems, and then the agent fixes them.

The loop:
1. **Generate** — produce an initial output
2. **Critique** — evaluate the output for errors, gaps, or quality issues
3. **Revise** — fix the identified problems
4. **Repeat** — until the output meets a quality bar or max iteration limit

---

## Self-Critique Prompting

The simplest form — ask the same model to critique its own output:

```
[Original output]

Now review your response above. Identify:
1. Any factual errors
2. Any logical gaps
3. Any parts that could be improved

Then rewrite an improved version.
```

The model often catches its own mistakes when explicitly asked to look for them.

---

## The Reflexion Framework

Reflexion (from a 2023 paper) formalizes this into three components:

1. **Actor** — the agent that produces actions and outputs
2. **Evaluator** — judges the quality of the actor's output (another LLM, a function, or a test runner)
3. **Self-Reflection** — based on the evaluator's feedback, the actor generates a verbal self-critique stored in memory

The key insight: the self-reflection is stored and used in the next attempt. The agent tries again with its own analysis of what went wrong.

```mermaid
flowchart TD
    Task["Task"] --> Actor["Actor\nGenerates output"]
    Actor --> Eval["Evaluator\nChecks quality/correctness"]
    Eval --> Good{"Acceptable?"}
    Good -->|"Yes"| Done["Final Output"]
    Good -->|"No"| Reflect["Self-Reflection\n'What went wrong? What should I do differently?'"]
    Reflect --> Memory["Store reflection\nin memory"]
    Memory --> Actor2["Actor (attempt N+1)\nTries again using the reflection"]
    Actor2 --> Eval
```

---

## Why Iterative Refinement Improves Quality

Generating output and evaluating output are different skills. Even for humans, writing and editing are separate modes of thinking. By explicitly separating these phases — generate, then critique — you get both modes working on the problem.

The evaluator can be:
- **The same LLM** asked to critique (zero-shot reflection)
- **A different LLM** with a specific critic persona
- **A code test runner** — run the code and use test failures as the evaluation signal
- **A human** — human-in-the-loop for high-stakes outputs

---

## The "Check Your Work" Loop for Code

Code generation is where reflection really shines — the evaluator is objective: do the tests pass?

```mermaid
sequenceDiagram
    participant Agent
    participant Executor as Code Executor
    participant Tests

    Agent->>Executor: Write and run code
    Executor->>Tests: Execute test suite
    Tests-->>Agent: Tests fail: NullPointerError line 12
    Agent->>Agent: Reflect: "I forgot to handle the None case"
    Agent->>Executor: Rewrite with None guard
    Executor->>Tests: Execute test suite
    Tests-->>Agent: All tests pass
    Agent->>Agent: Done — return final code
```

---

## When Self-Correction Helps Most

| Task Type | Benefit of Reflection | Why |
|---|---|---|
| Code generation | Very high | Tests provide exact, objective feedback |
| Factual writing | High | Catches hallucinations and unsupported claims |
| Structured output (JSON, SQL) | High | Validates format, fixes syntax errors |
| Creative writing | Medium | Subjective — quality depends on criteria |
| Simple Q&A | Low | Not worth the extra cost for simple tasks |

---

✅ **What you just learned:** Reflection lets agents critique and improve their own outputs — generate → critique → revise → repeat — making outputs more accurate, better structured, and less error-prone.

🔨 **Build this now:** Write a paragraph explaining a technical topic you know. Then write 3 specific critique questions about it. Answer those critiques and write an improved paragraph. That's the reflection loop — you just ran it manually.

➡️ **Next step:** Multi-Agent Systems → `/Users/1065696/Github/AI/10_AI_Agents/07_Multi_Agent_Systems/Theory.md`

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| 📄 **Theory.md** | ← you are here |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [05 Planning and Reasoning](../05_Planning_and_Reasoning/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [07 Multi-Agent Systems](../07_Multi_Agent_Systems/Theory.md)
