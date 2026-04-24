# Multi-Agent Systems — Interview Q&A

## Beginner

**Q1: What is a multi-agent system and why is it better than a single agent for complex tasks?**

<details>
<summary>💡 Show Answer</summary>

A multi-agent system is multiple AI agents working together, each with a distinct role, coordinated to complete a larger goal.

It's better than a single agent for complex tasks for three reasons:

1. **Specialization** — an agent told "you are a Python expert, only write code" performs better at coding than an agent trying to research, plan, write, AND debug simultaneously.

2. **Parallelism** — multiple agents can work at the same time. Research 5 companies simultaneously with 5 agents instead of one agent doing them one after another.

3. **Context management** — each agent has its own context window focused on its specific task, rather than one agent's context being crowded with every step of a massive workflow.

Think of it like a company vs. a solo freelancer. Both can do the work — but the company (multi-agent) scales and specializes in ways the freelancer (single agent) can't.

</details>

---

**Q2: What is the orchestrator pattern in multi-agent systems?**

<details>
<summary>💡 Show Answer</summary>

The orchestrator pattern has one agent — the orchestrator — that acts as a coordinator or manager.

The orchestrator:
- Takes the high-level goal from the user
- Breaks it into sub-tasks
- Decides which specialist agent to call for each sub-task
- Passes results between agents
- Combines everything into the final output

The orchestrator does NOT do the actual work. It delegates.

Example for "write a product comparison article":
- Orchestrator → calls Research Agent: "find specs for products A and B"
- Orchestrator → calls Analysis Agent: "compare these specs"
- Orchestrator → calls Writer Agent: "write the article based on this comparison"
- Orchestrator → returns the final article

</details>

---

**Q3: What is the difference between sequential (pipeline) and parallel multi-agent patterns?**

<details>
<summary>💡 Show Answer</summary>

**Sequential / Pipeline:** Agents work in a chain. Agent 1 finishes → Agent 2 starts → Agent 3 starts.

```
Research → Analysis → Writing → Editing → Final
```

Each stage depends on the previous stage's output. Clean, ordered, easy to debug.

**Parallel:** Multiple agents work simultaneously on independent sub-tasks.

```
Research Company A ──────────┐
Research Company B ──────────┼──► Aggregator → Final report
Research Company C ──────────┘
```

Parallel is much faster when tasks are independent. 5 research tasks done in the time it takes to do 1.

Most real systems use both — some stages must be sequential (you can't write before you research), some can be parallel (you can research 5 companies simultaneously).

</details>

---

## Intermediate

**Q4: How does inter-agent communication work in frameworks like CrewAI and AutoGen?**

<details>
<summary>💡 Show Answer</summary>

**CrewAI** uses task delegation with result passing:
- You define agents (roles + tools) and tasks (description + which agent does it)
- Tasks can pass their output to the next task's context (`context` parameter)
- The crew runs tasks in the defined order, building up a shared context

**AutoGen** uses conversational message passing:
- Agents are `ConversableAgent` objects that can send and receive messages
- A `GroupChat` manages which agent speaks next
- Agents "talk" to each other in a structured conversation loop
- One agent's output becomes another agent's input through the conversation

Both approaches end up at the same place — agent A's result flows to agent B's context — but the mechanism is different. CrewAI is more structured/declarative. AutoGen is more conversational.

</details>

---

**Q5: What are the main failure modes specific to multi-agent systems?**

<details>
<summary>💡 Show Answer</summary>

1. **Cascading errors** — if Agent 1 produces bad output and Agent 2 builds on it without validation, the error compounds through the whole pipeline.

2. **Communication mismatch** — Agent 1 outputs format X, Agent 2 expects format Y. The handoff fails silently.

3. **Orchestrator confusion** — if the orchestrator's task delegation logic breaks, all specialist agents receive the wrong task.

4. **Conflicting outputs** — two parallel agents produce contradictory information. The aggregator has no way to resolve it without additional logic.

5. **Exponential cost** — one agent making one mistake leads to retries × multiple agents. Costs can spike fast.

6. **Lost context** — a specialist agent doesn't have the full context the orchestrator has, so it makes decisions that make sense locally but not globally.

Mitigation: validate outputs at each handoff, structured output formats, explicit context injection from orchestrator to specialists.

</details>

---

**Q6: When would you NOT use a multi-agent system?**

<details>
<summary>💡 Show Answer</summary>

Multi-agent systems are powerful but add complexity. Avoid them when:

- **The task is simple or short** — a single ReAct agent handles it fine. Adding orchestration overhead isn't worth it.
- **You're still prototyping** — single agents are much easier to debug. Build with one agent first, only split into multi-agent when you hit actual limitations.
- **The sub-tasks are tightly coupled** — if every step depends on the exact state of every other step, coordinating multiple agents becomes more complex than just keeping everything in one agent's context.
- **Cost is a primary concern** — each agent adds LLM calls. An orchestrator deciding who to call is extra calls on top of the actual work.
- **Real-time latency matters** — sequential multi-agent pipelines are slower than a single agent. Each handoff adds latency.

The rule: start simple, add multi-agent complexity only when a single agent demonstrably fails to handle the task.

</details>

---

## Advanced

**Q7: How do you design the interfaces between agents to minimize integration failures?**

<details>
<summary>💡 Show Answer</summary>

Treat agent interfaces like API contracts:

1. **Structured output** — require each agent to produce a specific, parseable format (Pydantic model, JSON schema):
```python
class ResearchResult(BaseModel):
    topic: str
    key_findings: list[str]
    sources: list[str]
    confidence: float  # 0-1
```

2. **Validation at each handoff** — before passing to the next agent, validate the output matches the expected schema. If it doesn't, retry or raise.

3. **Explicit contracts** — document exactly what each agent receives as input and produces as output.

4. **Defensive prompting** — the receiving agent's prompt should handle the case where the input is incomplete or malformed.

5. **Versioning** — if you update one agent's output format, update all downstream agents that consume it.

This is essentially API design applied to agents.

</details>

---

**Q8: How would you implement error recovery in a multi-agent pipeline?**

<details>
<summary>💡 Show Answer</summary>

Error recovery strategies at different levels:

**At the task level:**
```python
def run_with_retry(agent, task, max_retries=3):
    for attempt in range(max_retries):
        result = agent.run(task)
        if validate(result):
            return result
        task = refine_task(task, result)  # Add error context to retry
    raise Exception(f"Task failed after {max_retries} attempts")
```

**At the handoff level:**
- Validate output before passing downstream
- If validation fails: retry the producing agent with more explicit requirements
- If retry fails: fall back to a simpler approach or skip the step

**At the orchestrator level:**
- Track which tasks succeeded/failed
- If a specialist fails, the orchestrator can try a different specialist or a different approach
- Always have a "graceful degradation" path — partial results with transparency about what failed

**At the pipeline level:**
- Checkpoint state between agents — if the pipeline fails midway, don't start over from scratch
- Store intermediate results so you can resume from the last successful checkpoint

</details>

---

**Q9: How does AutoGen's GroupChat differ from CrewAI's crew model, and when would you choose each?**

<details>
<summary>💡 Show Answer</summary>

**AutoGen GroupChat:**
- Agents participate in a group conversation
- A GroupChatManager decides which agent speaks next (round-robin or LLM-selected)
- Agents "talk" to each other naturally, building on each other's messages
- Built-in code execution: agents can write code and another agent runs it
- Best for: iterative workflows, code generation + debugging, open-ended back-and-forth

**CrewAI Crew:**
- Declarative: you define roles, tasks, and a process (sequential or hierarchical)
- Stronger role enforcement — each agent has a defined persona that shapes all its outputs
- Tasks have explicit descriptions, outputs, and context chains
- Better at structured workflows with defined stages
- Best for: content production pipelines, role-based workflows, report generation

**Choose AutoGen when:**
- You need code execution built into the loop
- The workflow is conversational and iterative
- Agents need to critique and revise each other's work dynamically

**Choose CrewAI when:**
- You have a well-defined pipeline with clear stages
- Role-playing and specialist personas matter to output quality
- You want a simpler, more readable configuration
- You're building content or research workflows

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
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | Multi-agent architecture deep dive |

⬅️ **Prev:** [06 Reflection and Self-Correction](../06_Reflection_and_Self_Correction/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [08 Agent Frameworks](../08_Agent_Frameworks/Theory.md)
