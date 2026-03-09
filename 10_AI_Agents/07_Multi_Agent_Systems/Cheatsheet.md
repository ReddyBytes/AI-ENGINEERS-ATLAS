# Multi-Agent Systems — Cheatsheet

**One-liner:** Multi-agent systems use specialized agents coordinated by an orchestrator — each agent has a focused role, the right tools, and communicates results to other agents, enabling parallelism and specialization impossible with a single agent.

---

## Key Terms

| Term | What it means |
|---|---|
| **Multi-agent system** | Multiple AI agents working together, each with distinct roles |
| **Orchestrator** | The coordinating agent — delegates tasks, synthesizes results |
| **Specialist agent** | An agent focused on one role (researcher, writer, coder, critic) |
| **Pipeline (sequential)** | Agents work in a chain — each passes output to the next |
| **Parallel agents** | Multiple agents work simultaneously on different sub-tasks |
| **Crew** | CrewAI's concept: a defined team of agents with roles and tasks |
| **GroupChat** | AutoGen's concept: agents communicate in a structured conversation |
| **Inter-agent communication** | How agents pass information to each other (message passing, shared memory, tool calls) |
| **Agent role** | The defined persona and responsibility of an agent ("You are a Python expert...") |
| **Handoff** | When one agent passes its completed work to the next agent |
| **Aggregator** | An agent that combines results from multiple parallel agents |

---

## The Three Patterns

### Orchestrator Pattern
```
User Goal → Orchestrator → Specialist A
                        → Specialist B
                        → Specialist C
                        ← Results
            Orchestrator → Final Answer
```

### Sequential Pipeline
```
Agent 1 → Agent 2 → Agent 3 → Agent 4 → Output
```

### Parallel Pattern
```
                 → Agent A → Result A ─┐
User Goal → Split → Agent B → Result B ─┼→ Aggregator → Final
                 → Agent C → Result C ─┘
```

---

## Framework Comparison

| | CrewAI | AutoGen | LangGraph |
|---|---|---|---|
| **Core concept** | Crew of role-based agents | Conversable agents | State machine graph |
| **Communication** | Task delegation | Group chat | Graph edges |
| **Best for** | Role-based collaboration | Code generation + execution | Complex conditional workflows |
| **Learning curve** | Low | Medium | High |

---

## When to Use Multi-Agent Systems

**Use multi-agent when:**
- Task requires genuinely different expertise (research + code + writing)
- Task can be parallelized (research 5 companies simultaneously)
- Single agent keeps hitting context window limits
- Different parts of the task need different tools

**Stick to single agent when:**
- The task is naturally sequential and can't be parallelized
- Coordination overhead would exceed the benefit
- The task is simple enough for one agent
- You're still prototyping (single agent is easier to debug)

---

## Golden Rules

1. **Give each agent a clear, narrow role.** "Research agent" not "do stuff agent." Specific role = better output.

2. **Agents should not share tools they don't need.** The writer agent doesn't need the database query tool.

3. **Design handoffs carefully.** What exactly does Agent 1 pass to Agent 2? Be explicit about the format.

4. **Test each agent individually before combining them.** A system of bad agents is a worse bad agent.

5. **The orchestrator should not do the work.** It delegates. If the orchestrator is doing research AND writing, you've missed the point.

6. **Keep communication structured.** Agents should output clearly formatted results, not conversational text, when passing to other agents.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | Multi-agent architecture deep dive |

⬅️ **Prev:** [06 Reflection and Self-Correction](../06_Reflection_and_Self_Correction/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [08 Agent Frameworks](../08_Agent_Frameworks/Theory.md)
