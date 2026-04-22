# Multi-Agent Orchestration — Cheatsheet

## Core Pattern

```
Orchestrator Agent
    ├── Worker 1 (specialized system prompt + limited tools)
    ├── Worker 2 (specialized system prompt + limited tools)
    └── Worker 3 (specialized system prompt + limited tools)

Orchestrator receives: high-level goal
Orchestrator outputs: assembled result
Workers receive: focused sub-task
Workers output: clean result
```

---

## Orchestrator Tool Pattern

```python
from claude_agent_sdk import Agent, tool

@tool
def run_specialized_worker(task: str, specialization: str) -> str:
    """Delegate a task to a specialized worker agent.
    Returns the worker's final result. Use for independent sub-tasks."""
    worker = Agent(
        model="claude-sonnet-4-6",
        tools=get_tools_for(specialization),
        system=f"You are a {specialization} specialist. {task_instructions(specialization)}"
    )
    return worker.run(task)

orchestrator = Agent(
    model="claude-sonnet-4-6",
    tools=[run_specialized_worker, merge_results],
    system="You are an orchestrator. Break complex goals into tasks and delegate."
)
```

---

## Sequential vs Parallel

| | Sequential | Parallel |
|---|---|---|
| Task dependency | B needs A's result | A, B, C are independent |
| Speed | Slower (serial) | Faster (concurrent) |
| Implementation | Default agent loop | `asyncio.gather()` |
| Use when | Data flows between tasks | Same input, different analyses |

```python
# Parallel workers
import asyncio

async def run_parallel_workers(tasks: list[str]) -> list[str]:
    agents = [Agent(model=..., tools=...) for _ in tasks]
    results = await asyncio.gather(*[
        a.arun(task) for a, task in zip(agents, tasks)
    ])
    return list(results)
```

---

## When to Use Multi-Agent

**Use multi-agent when:**
- 5+ similar independent sub-tasks (document analysis, data partitions)
- Workers benefit from specialized system prompts
- Context isolation is important (workers shouldn't see each other's work)
- Fault isolation needed (one worker fails, others continue)

**Don't use multi-agent when:**
- 1-3 simple sequential steps (just use one agent)
- Tasks are dependent (worker 2 needs worker 1's full context)
- Spawning overhead > task time
- Simplicity is more important than speed

---

## Rate Limit Awareness

```python
import asyncio

# Don't spawn 50 agents at once — hit rate limits
# Use a semaphore to limit concurrency
sem = asyncio.Semaphore(5)  # max 5 parallel agents

async def bounded_worker(task):
    async with sem:
        agent = Agent(...)
        return await agent.arun(task)

results = await asyncio.gather(*[bounded_worker(t) for t in tasks])
```

---

## Result Aggregation Prompt

```python
aggregator_system = """You receive analysis results from multiple specialized workers.
Your job:
1. Identify common themes across results
2. Note conflicting findings and explain the conflict
3. Prioritize findings by severity/importance
4. Produce a single coherent summary

Do not simply concatenate results — synthesize them."""
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | Patterns in depth |
| [📄 Code_Example.md](./Code_Example.md) | Orchestrator + worker code |

⬅️ **Prev:** [Agent Memory](../06_Agent_Memory/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Subagents](../08_Subagents/Theory.md)
