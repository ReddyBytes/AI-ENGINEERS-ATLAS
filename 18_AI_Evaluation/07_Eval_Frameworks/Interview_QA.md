# Eval Frameworks — Interview Q&A

## Beginner Questions

**Q1: What is Promptfoo and why would you use it?**

<details>
<summary>💡 Show Answer</summary>

Promptfoo is a config-driven evaluation framework for LLMs. You write a YAML file that specifies your prompts, the models to test, test inputs, and assertions. Then you run `promptfoo eval` and get a pass/fail report — no code required.

You'd use it when you want to:
- Quickly compare two models (e.g., GPT-4o vs Claude)
- Catch regressions when you tweak a prompt
- Run evals in CI/CD without writing custom evaluation code

</details>

---

**Q2: What is LangSmith used for?**

<details>
<summary>💡 Show Answer</summary>

LangSmith is an observability and evaluation platform from LangChain. It does two main things:

1. **Tracing** — it automatically captures every LLM call, tool invocation, and chain step in a searchable UI
2. **Evaluation** — you can create datasets, run experiments, log human feedback, and compare runs

It's especially useful if you're already using LangChain or LangGraph because integration is nearly automatic (just set env vars).

</details>

---

**Q3: What's the difference between an assertion and an evaluator?**

<details>
<summary>💡 Show Answer</summary>

- An **assertion** is a deterministic check: does the output contain this string? Is it valid JSON? Does it match this regex? Fast and cheap — no LLM call required.
- An **evaluator** is a function (often an LLM call) that makes a judgment call: is this response helpful? Is it factually correct? Slower and more expensive.

Best practice: use assertions wherever possible; fall back to evaluators for nuanced quality checks.

</details>

---

**Q4: What does a test dataset for an eval framework typically look like?**

<details>
<summary>💡 Show Answer</summary>

Usually a list of input/expected pairs:
```json
[
  {"input": "What's 2+2?", "expected": "4"},
  {"input": "Capital of France?", "expected": "Paris"},
  {"input": "Summarize: [long article]", "expected": "Key points are..."}
]
```

For more complex cases (RAG, agents), you add context fields, tool call expectations, and reference answers.

</details>

---

## Intermediate Questions

**Q5: How would you integrate evals into a CI/CD pipeline?**

<details>
<summary>💡 Show Answer</summary>

Three approaches:

1. **Promptfoo CI mode**: Run `promptfoo eval --ci` as a GitHub Actions step. It exits with a non-zero code if pass rate drops below threshold, blocking the PR merge.

2. **Custom eval script**: Write a Python script that runs your test suite and calls `sys.exit(1)` if pass rate < threshold. Add it to `.github/workflows/`.

3. **LangSmith Experiments**: Trigger eval runs on PR via the LangSmith API, then post results as a PR comment.

The key principle: treat eval failures like test failures — they block deployment.

</details>

---

**Q6: When would you build a custom eval framework instead of using Promptfoo or LangSmith?**

<details>
<summary>💡 Show Answer</summary>

Build custom when:
- Your evaluation logic is domain-specific (e.g., validating medical coding accuracy against ICD-10 database)
- You need to integrate with proprietary internal systems
- You require full data ownership with no third-party services
- Your eval involves complex multi-step workflows (e.g., running a simulation to check agent behavior)

Use off-the-shelf when:
- Standard assertions cover your needs
- You want a quick setup
- You want the UI, dashboards, and collaboration features

</details>

---

**Q7: What is an "experiment" in LangSmith and how does it help?**

<details>
<summary>💡 Show Answer</summary>

An experiment in LangSmith is a named run of your eval suite against a specific dataset. Each experiment captures: which model was used, which prompt version, the timestamp, all inputs/outputs, and evaluator scores.

This lets you answer: "Did my prompt change improve quality?" by comparing Experiment A vs Experiment B side-by-side. It's version control for your LLM system's behavior.

</details>

---

**Q8: What are the main assertion types in Promptfoo and when do you use each?**

<details>
<summary>💡 Show Answer</summary>

| Assertion | Use Case |
|-----------|----------|
| `contains` | Check that a required phrase appears (e.g., "refund policy") |
| `not-contains` | Check that disallowed phrases are absent (e.g., "I cannot help") |
| `regex` | Validate format (phone numbers, dates, IDs) |
| `json` | Ensure output is parseable JSON (for structured output prompts) |
| `javascript` | Custom logic not expressible in other types |
| `llm-rubric` | Subjective quality checks ("Is this polite?", "Is this accurate?") |
| `similar` | Semantic similarity to a reference answer |
| `cost` | Prevent expensive runaway prompts |
| `latency` | Enforce SLA requirements |

</details>

---

## Advanced Questions

**Q9: How do you handle evaluation at scale — when you have thousands of test cases and can't afford to run all of them on every deploy?**

<details>
<summary>💡 Show Answer</summary>

Strategies:

1. **Tiered test suites** — run a fast "smoke test" subset (50–100 cases) on every PR, and the full suite nightly or on release branches only

2. **Prioritized sampling** — weight test cases by severity: edge cases and safety-critical scenarios always run; routine cases sample at 20%

3. **Caching** — cache LLM judge responses for unchanged test cases; only re-run cases where the prompt or model changed

4. **Async pipelines** — run evals in parallel background jobs; post results to Slack/GitHub when done rather than blocking the PR

5. **Regression focus** — on PRs, only run the test cases related to the changed functionality (similar to unit test scoping)

</details>

---

**Q10: Design a production eval system for a customer support chatbot.**

<details>
<summary>💡 Show Answer</summary>

Requirements: catch regressions, measure quality, scale to 10k test cases, run in CI.

Architecture:

```
PR Opened
    ↓
Smoke Tests (100 critical cases) — blocks merge if < 85%
    ↓ (merged)
Nightly Full Eval (10k cases)
    ↓
Results Dashboard (LangSmith)
    ↓
Alert if regression > 3% (Slack notification)
```

Eval mix:
- 40% format/correctness assertions (fast, deterministic)
- 30% LLM-as-judge quality scoring (helpfulness, tone, accuracy)
- 20% safety assertions (no PII leak, no harmful content)
- 10% latency/cost assertions (P95 < 3s, < $0.02/request)

Dataset management:
- Golden set: 500 manually verified cases, never auto-added
- Failure set: auto-add any production case that received a thumbs-down
- Edge cases: manually curated adversarial inputs

Human review loop:
- Weekly: review 50 randomly sampled production conversations
- Monthly: update golden set with new patterns discovered

</details>

---

**Q11: What is "eval drift" and how do you detect it?**

<details>
<summary>💡 Show Answer</summary>

Eval drift happens when your evaluation setup becomes stale and stops reflecting real-world quality:

1. **Prompt drift** — your eval prompts haven't been updated to reflect new product requirements
2. **Dataset drift** — your test cases no longer represent the distribution of real user queries
3. **Judge drift** — the LLM you use as a judge has been updated and now scores differently
4. **Saturation** — your model scores 98%+ on all test cases, so the benchmark can't detect further improvements or subtle regressions

Detection:
- Track score distributions over time — sudden jumps may indicate judge model updates
- Regularly sample production conversations and check if they're represented in your test set
- Periodically introduce "known bad" test cases to verify the judge still catches failures
- Compare LLM-judge scores against human scores monthly; recalibrate if they diverge

</details>

---

## 📂 Navigation

- Parent: [18_AI_Evaluation](../)
- Theory: [Theory.md](Theory.md)
- Cheatsheet: [Cheatsheet.md](Cheatsheet.md)
- Code Example: [Code_Example.md](Code_Example.md)
- Framework Comparison: [Comparison.md](Comparison.md)
- Next section: [08_Build_an_Eval_Pipeline](../08_Build_an_Eval_Pipeline/)
