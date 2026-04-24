# Subagents — Interview Q&A

## Beginner Level

**Q1: What is a subagent and how is it different from the orchestrator?**

<details>
<summary>💡 Show Answer</summary>

A: A subagent is an agent instance spawned by another agent (the orchestrator) to handle a specific sub-task. The orchestrator receives the high-level goal and decides the overall strategy; subagents execute focused pieces of the work. The key differences: the orchestrator has broad context and coordinates multiple tasks; subagents have narrow context and focus on one task. The orchestrator sees the final results of subagents but never sees their internal reasoning or intermediate tool calls. Subagents don't know they're subagents — they just receive a goal and execute it. From the orchestrator's perspective, a subagent call looks exactly like any other tool call.

</details>

---

<br>

**Q2: Why do subagents have their own isolated context window?**

<details>
<summary>💡 Show Answer</summary>

A: Isolation is the primary benefit of subagents. When a worker agent processes a large document, it accumulates thousands of tokens of intermediate reasoning. If this ran inside the orchestrator's context, it would crowd out the orchestrator's own reasoning and other sub-tasks. By running in an isolated context, only the final result is returned to the orchestrator — the orchestrator's context grows by one result, not by all the intermediate steps. This also prevents information from one sub-task from accidentally influencing another, keeps sensitive data scoped to the agent that needs it, and makes debugging easier since each agent's behavior is independent.

</details>

---

<br>

**Q3: What is the difference between spawning a subagent in "foreground" vs "background" mode?**

<details>
<summary>💡 Show Answer</summary>

A: Foreground (blocking): the orchestrator calls `worker.run(task)` and waits for the result before proceeding. The orchestrator's loop is paused until the worker finishes. Use when the next orchestrator step needs the worker's result.

Background (async): the orchestrator launches multiple workers with `asyncio.gather()` and waits for all of them simultaneously. All workers run in parallel; the orchestrator proceeds only after all complete. Use when workers are independent — each gets a different slice of the problem, and the orchestrator needs all results before assembling the final answer. Background spawning is the mechanism that provides the parallelism benefit of multi-agent systems.

</details>

---

## Intermediate Level

**Q4: What should you pass to a subagent as context, and what should you leave out?**

<details>
<summary>💡 Show Answer</summary>

A: Pass only what the subagent needs to complete its specific task. Give the subagent: the task description, the specific input data it needs (e.g., one document path, not all 20), any constraints or output format requirements, and any critical context that affects its reasoning.

Leave out: the full conversation history, other workers' tasks, background context unrelated to the sub-task, the full system state, and anything confidential that this specific worker doesn't need. Excessive context wastes tokens and can confuse the worker. Insufficient context causes the worker to make wrong assumptions. The right level: the worker should have exactly enough context to complete the task without needing to ask questions.

</details>

---

<br>

**Q5: How does failure isolation work in a subagent system and how should the orchestrator handle worker failures?**

<details>
<summary>💡 Show Answer</summary>

A: A subagent failure (exception, timeout, or bad output) should not crash the orchestrator. The spawning tool catches exceptions and returns an error result to the orchestrator. The orchestrator then sees something like `{"status": "failed", "error": "Worker timed out after 60s"}` and decides how to proceed. Common strategies: retry with different parameters or a simpler scope; use a fallback approach (skip this sub-task and note the gap in the output); escalate to the user for human input; produce a partial result clearly noting what's missing. The orchestrator should always check the `status` field of worker results and have an explicit strategy for each failure mode.

</details>

---

<br>

**Q6: When is the overhead of spawning a subagent not worth it?**

<details>
<summary>💡 Show Answer</summary>

A: The overhead includes: the spawn call itself, a separate API call (latency + cost), isolated context setup, and result formatting. This overhead is roughly equivalent to 1-3 additional tool calls in the parent agent. If the sub-task only requires 1-2 tool calls to complete, the overhead exceeds the benefit — just do it directly in the parent agent. Subagents pay off when: the sub-task involves 3+ tool calls, generates significant context, benefits from specialization, or runs in parallel with other sub-tasks. Rule of thumb: if the sub-task would take under 30 seconds as part of the parent loop, don't spawn a subagent.

</details>

---

## Advanced Level

**Q7: How would you implement a subagent pool to avoid spawning overhead on repeated similar tasks?**

<details>
<summary>💡 Show Answer</summary>

A: Agent instance reuse isn't directly supported in most SDKs (each run starts fresh), but you can approximate pooling:

```python
import asyncio
from queue import Queue

class WorkerPool:
    def __init__(self, size: int, system: str, tools: list):
        self.queue = asyncio.Queue(maxsize=size)
        for _ in range(size):
            self.queue.put_nowait(Agent(
                model="claude-sonnet-4-6",
                system=system,
                tools=tools
            ))
    
    async def run(self, task: str) -> str:
        worker = await self.queue.get()
        try:
            return await worker.arun(task)
        finally:
            # Reset and return worker (context cleared between tasks)
            worker.reset()
            self.queue.put_nowait(worker)

# Usage: pool of 5 workers for high-volume tasks
pool = WorkerPool(size=5, system="You are a document analyzer.", tools=[...])
results = await asyncio.gather(*[pool.run(task) for task in 50_tasks])
```

The pool limits concurrency to 5 simultaneous workers (rate limit protection) and reuses agent objects. The `worker.reset()` clears conversation history between tasks.

</details>

---

<br>

**Q8: How do subagents handle partial work completion — what happens if a subagent is interrupted mid-task?**

<details>
<summary>💡 Show Answer</summary>

A: By default, a subagent that is interrupted (timeout, cancellation, exception) returns nothing or an error. This is an all-or-nothing model. For tasks where partial completion is valuable, design explicit checkpointing:

1. **Progress reporting tool**: the worker calls `checkpoint(progress_summary)` every N steps. The orchestrator receives checkpoint updates even if the worker doesn't complete.

2. **Resumable sub-tasks**: structure the sub-task as multiple smaller sub-tasks. Instead of "analyze 50 pages," spawn 5 workers for 10 pages each. If one fails, you have 4/5 results rather than 0/1.

3. **External state**: the worker writes partial results to an external store (database, file) as it goes. If interrupted, the orchestrator reads the partial results directly.

4. **Idempotent design**: design sub-tasks so they can be rerun from the start without side effects. Then a timeout just means retry, not lost work.

</details>

---

<br>

**Q9: Compare the security boundaries between a subagent and a tool in the context of an orchestrator agent.**

<details>
<summary>💡 Show Answer</summary>

A: A tool is a Python function the orchestrator calls directly — it runs in the same process, with the orchestrator's full permissions. A subagent is a separate agent instance with its own process context, system prompt, and tool set.

Security implications:
- **Tool**: has access to everything the orchestrator's process has access to. A tool that writes files can write anywhere the process has permission. The orchestrator's prompt injection defense is the only barrier.
- **Subagent**: has only the tools you explicitly give it. A subagent that handles user-provided content can only take actions via its own tools. If prompt injection occurs in the subagent, it's limited to the subagent's tool set — not the orchestrator's.

This means subagents are more secure for handling untrusted content: the blast radius of a prompt injection is bounded by the subagent's tools. An orchestrator tool handling untrusted input with full orchestrator permissions is more dangerous. Design rule: if a task involves processing untrusted content (web scraping, user-uploaded files, external APIs), run it in a subagent with minimal tool permissions.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Subagent spawn patterns |

⬅️ **Prev:** [Multi-Agent Orchestration](../07_Multi_Agent_Orchestration/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Handoffs](../09_Handoffs/Theory.md)
