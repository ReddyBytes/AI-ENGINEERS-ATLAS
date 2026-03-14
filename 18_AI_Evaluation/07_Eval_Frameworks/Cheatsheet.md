# Eval Frameworks — Cheatsheet

## Framework Selection at a Glance

| Need | Best Tool |
|------|-----------|
| Config-driven CI evals, fast setup | **Promptfoo** |
| Observability + tracing + evals in one | **LangSmith** |
| OpenAI-native, community datasets | **OpenAI Evals** |
| Custom pipeline, full control | **Roll your own** |
| Enterprise compliance, audit trail | **LangSmith** |

---

## Promptfoo — Minimal Setup

### Install
```bash
npm install -g promptfoo
# or
pip install promptfoo
```

### `promptfooconfig.yaml`
```yaml
prompts:
  - "Answer this customer question helpfully: {{question}}"

providers:
  - openai:gpt-4o
  - anthropic:claude-opus-4-6

tests:
  - vars:
      question: "What is your return policy?"
    assert:
      - type: contains
        value: "30 days"
      - type: llm-rubric
        value: "Response is polite and helpful"
      - type: cost
        threshold: 0.01  # max $0.01 per call
```

### Run
```bash
promptfoo eval
promptfoo view  # opens browser UI
```

---

## Promptfoo Assertion Types

| Type | What It Checks | Example |
|------|---------------|---------|
| `contains` | Substring present | `value: "refund"` |
| `not-contains` | Substring absent | `value: "I cannot"` |
| `regex` | Pattern match | `value: "\\d{3}-\\d{4}"` |
| `json` | Valid JSON output | _(no value needed)_ |
| `javascript` | Custom JS function | `value: "output.length < 500"` |
| `python` | Custom Python fn | `value: "len(output) < 500"` |
| `llm-rubric` | AI judge scoring | `value: "factually accurate"` |
| `similar` | Semantic similarity | `value: "expected answer"` |
| `cost` | Token cost limit | `threshold: 0.05` |
| `latency` | Response time limit | `threshold: 3000` (ms) |

---

## LangSmith — Key Concepts

```
Project → Runs → Traces → Spans
                    ↓
               Feedback (human or automated)
                    ↓
              Datasets & Experiments
```

### Minimal Python Setup
```python
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "ls__your_key"
os.environ["LANGCHAIN_PROJECT"] = "my-project"

# Now all LangChain/LangGraph calls are auto-traced
from langchain_anthropic import ChatAnthropic
llm = ChatAnthropic(model="claude-opus-4-6")
response = llm.invoke("What is 2+2?")  # auto-logged to LangSmith
```

### Run an Evaluation
```python
from langsmith.evaluation import evaluate

results = evaluate(
    lambda inputs: {"answer": run_my_chain(inputs["question"])},
    data="my-dataset-name",
    evaluators=[accuracy_evaluator, helpfulness_evaluator],
    experiment_prefix="gpt4o-vs-claude",
)
```

### Log Human Feedback
```python
from langsmith import Client
client = Client()
client.create_feedback(
    run_id=run.id,
    key="correctness",
    score=1,  # 0 or 1
    comment="Perfect answer"
)
```

---

## OpenAI Evals — Key Patterns

### Install
```bash
pip install evals
git clone https://github.com/openai/evals
```

### Minimal YAML Eval
```yaml
# my_eval.yaml
my_qa_eval:
  id: my_qa_eval
  metrics: [accuracy]

my_qa_eval/defaults:
  class: evals.eval:ModelGradedEval
  args:
    samples_jsonl: data/samples.jsonl
    eval_type: cot_classify
    modelgraded_spec: fact
```

### Sample Format
```json
{"input": [{"role": "user", "content": "Capital of France?"}],
 "ideal": "Paris"}
```

---

## Build-Your-Own Pattern

```python
# Minimal custom eval loop
import json
from anthropic import Anthropic

client = Anthropic()

def run_eval(test_cases: list[dict]) -> dict:
    results = []
    for case in test_cases:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1024,
            messages=[{"role": "user", "content": case["input"]}]
        )
        output = response.content[0].text
        passed = case["expected"].lower() in output.lower()
        results.append({"case": case, "output": output, "passed": passed})

    pass_rate = sum(r["passed"] for r in results) / len(results)
    return {"pass_rate": pass_rate, "results": results}
```

---

## CI/CD Integration

### GitHub Actions (Promptfoo)
```yaml
name: Eval on PR
on: [pull_request]
jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: npm install -g promptfoo
      - run: promptfoo eval --ci --output results.json
      - name: Comment results on PR
        uses: promptfoo/promptfoo-action@v1
        with:
          results: results.json
          github-token: ${{ secrets.GITHUB_TOKEN }}
```

### Pass/Fail Threshold
```bash
# Fail CI if pass rate < 80%
promptfoo eval --pass-rate-threshold 0.8
```

---

## When to Use What

```
Small team, fast iteration?
  → Promptfoo (config YAML, no code needed)

LangChain/LangGraph stack?
  → LangSmith (built-in integration)

OpenAI models + community benchmarks?
  → OpenAI Evals

Need custom metrics + full data ownership?
  → Build your own

Enterprise + SOC2 + audit trail?
  → LangSmith Enterprise
```

---

## Key Metrics to Track in Any Framework

| Metric | Target | Alert If |
|--------|--------|----------|
| Pass rate | > 85% | < 75% |
| Regression rate | 0% | > 5% |
| P95 latency | < 3s | > 5s |
| Cost per eval | < $0.05 | > $0.20 |
| Judge agreement (κ) | > 0.7 | < 0.5 |

---

## 📂 Navigation

- Parent: [18_AI_Evaluation](../)
- Theory: [Theory.md](Theory.md)
- Interview Q&A: [Interview_QA.md](Interview_QA.md)
- Code Example: [Code_Example.md](Code_Example.md)
- Framework Comparison: [Comparison.md](Comparison.md)
- Next section: [08_Build_an_Eval_Pipeline](../08_Build_an_Eval_Pipeline/)
