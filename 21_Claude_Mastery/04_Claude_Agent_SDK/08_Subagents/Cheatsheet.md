# Subagents — Cheatsheet

## What Makes Something a Subagent

- Spawned by a parent (orchestrator) agent
- Runs its own agent loop (perception → action → observation)
- Has its own context window (isolated from parent)
- Has its own system prompt and tool set
- Returns a result to the parent; parent never sees internals

---

## Spawn Pattern

```python
from claude_agent_sdk import Agent, tool

@tool
def run_subagent(task: str, role: str, available_tools: str) -> str:
    """Spawn a worker agent for a specific task.
    role: what kind of specialist this agent should be.
    Returns the agent's final answer."""
    worker = Agent(
        model="claude-sonnet-4-6",
        tools=resolve_tools(available_tools),
        system=f"You are a {role}. Complete only the task assigned to you.",
        max_steps=10
    )
    return worker.run(task)
```

---

## Context Passing — What to Include

```python
# Too much — defeats isolation
worker.run(f"""
Full conversation history: {full_history}
All user preferences: {all_prefs}
Everything we know about the project: {project_dump}
Your task: summarize document.txt
""")

# Just right — only what's needed
worker.run(f"""
Task: Summarize document.txt focusing on security risks.
Context: This is for an audit report.
Output format: bullet list, max 5 points.
""")
```

---

## Foreground vs Background

```python
# Foreground (blocking) — wait for result
result = worker.run(task)
next_step = use_result(result)

# Background (async) — don't wait, parallelize
import asyncio
results = await asyncio.gather(
    worker1.arun(task1),
    worker2.arun(task2),
    worker3.arun(task3)
)
```

---

## When to Spawn a Subagent

| Spawn when | Don't spawn when |
|---|---|
| Sub-task generates big intermediate context | Sub-task is 1-2 tool calls |
| Sub-task needs specialized tools/prompt | Same tools as parent |
| Sub-task can run in parallel | Must be sequential (data dependency) |
| Failure isolation is valuable | Simplicity matters more |
| Result is a clean deliverable | Result needs to influence every step |

---

## Return Format Best Practices

```python
# Poor — raw unstructured data
return massive_raw_tool_output_string

# Good — structured, actionable
return json.dumps({
    "status": "complete",
    "findings": [
        {"issue": "SQL injection risk", "severity": "high", "line": 42},
        {"issue": "Missing input validation", "severity": "medium", "line": 87}
    ],
    "summary": "2 security issues found in auth module",
    "recommended_action": "Fix SQL parameterization before deployment"
})
```

---

## Isolation Types

| Type | What It Prevents |
|---|---|
| **Context isolation** | Parent history leaking into worker |
| **Tool isolation** | Worker using tools it shouldn't have |
| **Failure isolation** | Worker crash crashing parent |
| **Information isolation** | Workers seeing each other's results |

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Subagent spawn patterns |

⬅️ **Prev:** [Multi-Agent Orchestration](../07_Multi_Agent_Orchestration/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Handoffs](../09_Handoffs/Theory.md)
