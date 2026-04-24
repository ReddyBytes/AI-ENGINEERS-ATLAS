# Multi-Agent Orchestration — Interview Q&A

## Beginner Level

**Q1: What is the orchestrator-worker pattern in multi-agent systems?**

<details>
<summary>💡 Show Answer</summary>

A: The orchestrator-worker pattern has one orchestrator agent that receives a high-level goal and breaks it down into sub-tasks, and multiple worker agents (subagents) each responsible for one sub-task. The orchestrator delegates work to workers, collects their results, and assembles the final output. Workers are isolated — they only know about their specific sub-task, not the full goal or what other workers are doing. The orchestrator never needs to be an expert in each domain; it just needs to know how to delegate and synthesize. This separation allows each worker to be specialized, focused, and independently testable.

</details>

---

<br>

**Q2: What are the two main reasons to use multi-agent instead of a single agent?**

<details>
<summary>💡 Show Answer</summary>

A: Parallelism and specialization. Parallelism: a single agent runs tool calls sequentially. If you have 10 independent tasks, a single agent takes 10× longer than 10 parallel workers. Multi-agent breaks the sequential constraint and can run all 10 simultaneously. Specialization: a worker with a focused system prompt ("You are a security code reviewer focused only on injection vulnerabilities") outperforms a generalist agent on specific tasks. The focused context prevents scope creep and produces more precise results. Both benefits require independence between sub-tasks — if tasks are dependent, multi-agent adds overhead without the parallelism benefit.

</details>

---

<br>

**Q3: How does context isolation benefit a multi-agent system?**

<details>
<summary>💡 Show Answer</summary>

A: Each worker agent starts with a clean, empty context. This means: (1) The orchestrator's full conversation history (potentially thousands of tokens) doesn't pollute the worker's context — the worker only sees its assigned task. (2) Workers processing sensitive data don't inadvertently share it with other workers. (3) The orchestrator only receives the worker's final result, not its hundreds of intermediate tool calls and thoughts — keeping the orchestrator's context lean. (4) Worker failures don't corrupt the orchestrator's state. Context isolation is what makes multi-agent systems scalable — each component stays focused and bounded.

</details>

---

## Intermediate Level

**Q4: How would you implement a fan-out / fan-in pattern for processing a list of 20 documents?**

<details>
<summary>💡 Show Answer</summary>

A: Fan-out spawns 20 workers (one per document) simultaneously; fan-in collects all results and aggregates.

```python
import asyncio
from claude_agent_sdk import Agent, tool

async def analyze_document(doc_path: str) -> dict:
    """Worker: analyze one document."""
    worker = Agent(
        model="claude-haiku-4-5",  # cheaper model for workers
        tools=[read_file, extract_entities],
        system="Extract key entities and a 2-sentence summary from the document."
    )
    return await worker.arun(f"Analyze: {doc_path}")

async def orchestrate(documents: list[str]) -> str:
    # Fan-out: spawn all workers simultaneously (with concurrency limit)
    sem = asyncio.Semaphore(5)
    async def bounded(path):
        async with sem:
            return await analyze_document(path)
    
    results = await asyncio.gather(*[bounded(d) for d in documents])
    
    # Fan-in: orchestrator aggregates
    orchestrator = Agent(
        model="claude-sonnet-4-6",
        system="Synthesize document analysis results into a consolidated report."
    )
    return await orchestrator.arun(
        f"Synthesize these {len(results)} document analyses:\n{results}"
    )
```

The concurrency semaphore prevents rate limit errors by capping simultaneous API calls.

</details>

---

<br>

**Q5: When is multi-agent orchestration NOT the right approach?**

<details>
<summary>💡 Show Answer</summary>

A: Multi-agent is wrong when:
1. **Tasks are dependent**: if worker 2 needs worker 1's output as input, they must run sequentially — no parallelism benefit, just added spawn overhead.
2. **Tasks are trivial**: spawning an agent that makes 1-2 tool calls adds more overhead than it saves.
3. **Shared context is required**: if all workers need to see each other's work to avoid duplication, the isolation that makes multi-agent efficient becomes a liability.
4. **Simplicity matters more than speed**: a single-agent solution is easier to debug, test, and maintain. Multi-agent introduces coordination complexity, rate limit management, and failure recovery complexity.
5. **Cost matters more than latency**: parallel workers run simultaneously but all incur their full cost. A single agent doing tasks sequentially costs the same total tokens — multi-agent just runs faster.

</details>

---

<br>

**Q6: How does an orchestrator handle a worker failure (timeout, error, or bad output)?**

<details>
<summary>💡 Show Answer</summary>

A: Three strategies:

**Retry with different parameters**: the orchestrator retries the failed sub-task with modified instructions (e.g., more specific guidance if the worker returned an ambiguous result).

**Fallback to a different approach**: if the primary worker fails, the orchestrator calls a simpler tool or a different worker variant.

**Partial completion**: if some workers succeed and one fails, the orchestrator produces a result noting the gap: "Analysis complete for 9 of 10 documents; document 5 failed due to [reason]."

Implementation: workers should return structured results including a `status` field. The orchestrator checks status and routes accordingly. Don't let exceptions from workers crash the orchestrator — wrap each `worker.run()` in try/except.

</details>

---

## Advanced Level

**Q7: How would you design an orchestration system that dynamically decides how many workers to spawn based on the task?**

<details>
<summary>💡 Show Answer</summary>

A: A dynamic worker count system:

```python
async def orchestrate_dynamically(goal: str, input_data: list) -> str:
    # Step 1: Orchestrator analyzes the task
    planner = Agent(
        model="claude-haiku-4-5",
        system="""Given a goal and input data size, decide:
        - How many workers are optimal (1-20)?
        - What specialization does each worker need?
        Return JSON: {"worker_count": N, "worker_roles": [...], "batch_size": M}"""
    )
    plan = json.loads(planner.run(
        f"Goal: {goal}\nInput items: {len(input_data)}"
    ))
    
    # Step 2: Batch input according to plan
    batch_size = plan["batch_size"]
    batches = [input_data[i:i+batch_size] for i in range(0, len(input_data), batch_size)]
    
    # Step 3: Spawn workers per plan
    async def run_worker(batch, role):
        worker = Agent(
            model="claude-sonnet-4-6",
            system=f"You are a {role} specialist.",
            tools=get_tools_for_role(role)
        )
        return await worker.arun(f"Process: {batch}")
    
    results = await asyncio.gather(*[
        run_worker(batch, role) 
        for batch, role in zip(batches, plan["worker_roles"])
    ])
    
    # Step 4: Aggregate
    return aggregate(results)
```

The planner agent reads the task and data size, returns an optimal configuration. This balances parallelism benefit against API cost and rate limits.

</details>

---

<br>

**Q8: Describe a hierarchical multi-agent architecture and when you would use three levels of agents.**

<details>
<summary>💡 Show Answer</summary>

A: Hierarchical architecture: top-level orchestrator → mid-level sub-orchestrators → leaf workers.

Example: competitive analysis of 50 companies across 5 domains (product, pricing, technology, market position, customer sentiment).

```
Top orchestrator (1)
├── Domain sub-orchestrator: Product (1)
│   ├── Product worker for company 1-10
│   ├── Product worker for company 11-20
│   └── ... 5 batches of workers
├── Domain sub-orchestrator: Pricing (1)
│   └── ... 5 batches
└── ... 5 domain sub-orchestrators
```

Why three levels: the top orchestrator can't delegate 250 individual company+domain pairs — that's too much coordination. Sub-orchestrators handle domain-specific aggregation before the top orchestrator synthesizes across domains. Each level has a clear scope: top level synthesizes domains, mid level processes batches within domain, leaf level analyzes one company.

Use three levels when: the problem has two natural decomposition axes (in this case: company × domain), and both axes benefit from parallel processing.

</details>

---

<br>

**Q9: How would you implement observability and debugging for a complex multi-agent orchestration system in production?**

<details>
<summary>💡 Show Answer</summary>

A: Multi-agent systems are hard to debug because failures can happen at any level and trace through multiple agents.

**Distributed tracing**: assign a root `trace_id` to every request. Each spawned worker inherits this ID. Log every agent step with `{trace_id, agent_id, step, tool, input, output, duration}`. Use a structured logging system (Datadog, Jaeger) to reconstruct the full execution tree for any request.

**Worker result schema**: standardize what workers return: `{status, result, errors, steps_taken, tokens_used}`. The orchestrator logs these alongside the trace.

**Step-level hooks**: use `on_step` callbacks in each agent to emit metrics: tokens per step, tool call frequency, errors per agent.

**Replay capability**: log all inputs to each worker. When debugging, you can replay a single worker with its exact input to reproduce the failure without re-running the full orchestration.

**Cost monitoring**: each spawned agent reports its token usage back to the orchestrator. Track total cost per orchestration run and alert on outliers.

A simple start: add a `trace_id` parameter to every worker system prompt and log all agent runs to a database. Aggregating by `trace_id` gives you the full execution tree for any request.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | Patterns in depth |
| [📄 Code_Example.md](./Code_Example.md) | Orchestrator + worker code |

⬅️ **Prev:** [Agent Memory](../06_Agent_Memory/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Subagents](../08_Subagents/Theory.md)
