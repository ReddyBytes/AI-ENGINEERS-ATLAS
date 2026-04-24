# Handoffs — Interview Q&A

## Beginner Level

**Q1: What is an agent handoff and how does it differ from spawning a subagent?**

<details>
<summary>💡 Show Answer</summary>

A: A handoff is a sequential transfer of control from one agent to the next. Agent A completes its stage, packages the current state into a structured handoff message, and passes control to Agent B — which continues from where A left off. Agent A is effectively done; B is the active agent going forward.

A subagent spawn is a delegation pattern: the parent agent (orchestrator) sends work to a worker, waits for the result, and continues orchestrating. The parent stays in control throughout.

The practical difference: use handoffs for linear pipelines where each stage hands off to the next (triage → specialist → action); use subagents for parallel work where an orchestrator needs multiple tasks done simultaneously and assembles all the results.

</details>

---

<br>

**Q2: Why is the handoff message structure important?**

<details>
<summary>💡 Show Answer</summary>

A: The handoff message is the only information the next agent receives about everything that came before. If it's missing context, the receiving agent starts over or makes wrong assumptions. If it's too verbose, the receiving agent's context is flooded. A well-structured handoff message has: a human-readable summary (what happened), structured state (the data needed), a list of completed steps (so the receiving agent doesn't redo work), remaining steps (what still needs doing), and metadata for tracing. Think of it as a shift handover in a hospital — the incoming team should know everything they need to know without reading the full case notes from scratch.

</details>

---

<br>

**Q3: When would you use a human-in-the-loop handoff versus an automatic handoff to another agent?**

<details>
<summary>💡 Show Answer</summary>

A: Human-in-the-loop handoffs are appropriate when: the action is irreversible and high-impact (deleting records, sending bulk emails, making financial transactions); the agent's confidence is low (ambiguous data, conflicting signals); the task requires judgment that the model may not have (legal decisions, policy exceptions); or when regulations require human oversight (financial compliance, medical systems). Automatic handoffs (agent to agent) work when the outcome is predictable, reversible, or low-risk. A practical heuristic: if the next step could cause damage that takes more than 15 minutes to undo, require human approval.

</details>

---

## Intermediate Level

**Q4: How do you prevent state loss between handoffs in a multi-stage pipeline?**

<details>
<summary>💡 Show Answer</summary>

A: State loss happens when the handoff message doesn't include everything the next agent needs. Prevention strategies:

1. **Explicit `completed_steps` and `remaining_steps`**: the next agent reads these before acting, skipping what's done.
2. **Structured state object**: don't rely on the context summary — use a typed state dictionary with all relevant fields.
3. **External state store + reference**: for large state (documents, datasets), store it externally and pass the reference ID in the handoff. The next agent loads state from the store.
4. **Handoff validation**: before the handoff message is passed, run a validation step: "Does this message contain all the fields that the next agent requires?" This can be a simple schema check.
5. **Idempotent stages**: design each stage so it can be safely rerun if it receives duplicate input. This makes partial failures recoverable.

</details>

---

<br>

**Q5: How would you implement conditional routing in a handoff system?**

<details>
<summary>💡 Show Answer</summary>

A: Conditional routing means the next agent depends on the result of the current agent. Implementation:

```python
def process_support_ticket(ticket: str) -> str:
    # Stage 1: classify
    classifier = Agent(
        model="claude-haiku-4-5",
        system="Classify this support ticket: billing, technical, account, or other."
    )
    classification = classifier.run(f"Classify: {ticket}")
    
    # Conditional routing based on classification result
    if "billing" in classification.lower():
        specialist = Agent(
            model="claude-sonnet-4-6",
            tools=[lookup_billing, apply_credit, process_refund],
            system="You are a billing specialist."
        )
    elif "technical" in classification.lower():
        specialist = Agent(
            model="claude-sonnet-4-6",
            tools=[lookup_product, search_docs, create_bug_report],
            system="You are a technical support specialist."
        )
    else:
        specialist = Agent(
            model="claude-sonnet-4-6",
            tools=[lookup_account, escalate],
            system="You are a general support agent."
        )
    
    return specialist.run(
        f"Handle this ticket: {ticket}\nClassification: {classification}"
    )
```

The handoff message (in this case, the classification result) determines which agent runs next. This is conditional routing without a central router — the orchestrating code handles the routing decision.

</details>

---

<br>

**Q6: What are the failure modes specific to handoff pipelines and how do you mitigate them?**

<details>
<summary>💡 Show Answer</summary>

A: Four failure modes specific to pipelines:

**State corruption**: Agent A passes malformed or incomplete state. Agent B operates on bad data. Mitigation: validate handoff message schema at each stage before proceeding.

**Infinite loops**: A hands to B hands to A. Mitigation: include `hop_count` in the handoff message; stop and error if it exceeds a limit.

**Silent failures**: Agent B claims success but produces wrong output. Agent C builds on bad foundations. Mitigation: add a validation/verification stage between consequential stages.

**Timeout cascades**: Stage 3 times out; stage 4 never starts; the user sees no output. Mitigation: each stage has an independent timeout; a failed stage returns a partial result with `status: failed` rather than blocking forever; implement circuit breakers that route to a fallback path.

</details>

---

## Advanced Level

**Q7: How would you design a handoff system for a long-running workflow that might span days and survive process restarts?**

<details>
<summary>💡 Show Answer</summary>

A: For multi-day workflows, handoff state cannot live in memory — processes restart, agents time out, servers fail.

Architecture:

**Persistent handoff store**: every handoff message is written to a database before the next stage starts. The handoff store is the source of truth.

```
handoff_store: {
    workflow_id: "wf_001",
    current_stage: "review",
    state: {...},
    history: [
        {stage: "extract", status: "complete", timestamp: "..."},
        {stage: "validate", status: "complete", timestamp: "..."}
    ],
    status: "in_progress"
}
```

**Resumable stages**: each stage reads from the handoff store, not from memory. A stage that crashes can be restarted by reading the last committed handoff.

**Checkpoint commits**: within a long stage, write intermediate state to the store periodically. If the stage restarts, it reads the checkpoint and continues rather than starting over.

**Stage idempotency**: stages check `completed_steps` in the handoff before acting. Rerunning a stage that already ran is a no-op.

**Workflow engine**: use a proper workflow orchestration system (Airflow, Temporal, Prefect) for workflows that span hours or days. These provide durability, retry logic, and visibility built-in.

</details>

---

<br>

**Q8: How does the handoff pattern relate to LangGraph's state machine model?**

<details>
<summary>💡 Show Answer</summary>

A: LangGraph models multi-agent workflows as explicit state machines — nodes are agents or processing steps, edges are transitions (handoffs). The LangGraph `StateGraph` is a formalization of the handoff pattern:

- **Nodes** = agents or tools
- **Edges** = handoffs (including conditional edges = conditional routing)
- **State** = the handoff message (a typed `TypedDict` that flows through the graph)
- **Checkpointing** = the durable handoff store

The handoff pattern described in this topic is what you're implementing informally when you write multi-stage pipelines without LangGraph. LangGraph provides: explicit state schema enforcement, built-in checkpointing (persistent workflows), conditional edge routing, cycle detection (prevents infinite loops), and a visual graph for debugging.

For simple 2-3 stage pipelines: the informal handoff pattern is simpler and sufficient. For complex workflows with branches, cycles, human interrupts, and durability requirements: LangGraph's state machine model provides the structure needed.

</details>

---

<br>

**Q9: What are the performance implications of a 10-stage handoff pipeline vs a single 10-step multi-step agent?**

<details>
<summary>💡 Show Answer</summary>

A: The 10-stage pipeline makes 10 separate agent instantiation + API call sequences; the multi-step agent makes one instantiation with 10 API calls in its loop.

Handoff pipeline advantages:
- Smaller context per call (each stage starts fresh)
- Parallel stages where possible
- Specialized models per stage (use Haiku for simple stages, Sonnet for complex)
- Fault tolerance (a failing stage doesn't affect others)
- Better observability (each stage is a discrete unit to monitor)

Handoff pipeline disadvantages:
- Higher total latency (spawn overhead × 10)
- More infrastructure (routing logic, state persistence)
- Context reconstruction overhead (each stage re-reads state)
- More complex error handling

Multi-step agent advantages:
- Lower total call count
- Full context available at every step
- Simpler code

Rule of thumb: if stages are genuinely independent or benefit from specialization, use a pipeline. If every step needs the full context of all previous steps and specialization adds no value, use a single multi-step agent.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Handoff pipeline in code |

⬅️ **Prev:** [Subagents](../08_Subagents/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Safety in Agents](../10_Safety_in_Agents/Theory.md)
