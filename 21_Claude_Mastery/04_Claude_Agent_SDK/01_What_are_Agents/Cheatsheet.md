# What Are Agents? — Cheatsheet

## Core Definition

An **agent** = LLM + Tools + Loop + Context

The loop: **Perceive → Reason → Act → Observe → Repeat**

---

## Agent vs Single Call vs Chain

| | Single API Call | Chain | Agent |
|---|---|---|---|
| Path | Fixed | Fixed | Adaptive |
| Steps | 1 | N (predetermined) | N (decided at runtime) |
| Tools | No | Maybe | Yes |
| State | None | Limited | Full history |
| Can retry on failure | No | No | Yes |
| Human needed per step | Yes | No | No |

---

## The Agent Loop (Pseudocode)

```python
context = [system_prompt, user_goal, tool_definitions]

while True:
    response = llm.call(context)
    
    if response.is_final_answer:
        return response.text          # Done
    
    if steps > MAX_STEPS:
        return "Max steps reached"    # Safety stop
    
    result = execute_tool(response.tool_call)
    context.append(response.tool_call)
    context.append(result)
    steps += 1
```

---

## Four Components Every Agent Has

| Component | What It Does |
|---|---|
| **LLM (Claude)** | Core reasoning — decides what to do next |
| **Tools** | Actions — web search, code exec, file I/O, APIs |
| **Context** | Memory — conversation + tool history |
| **Loop** | Infrastructure — keeps running until done |

---

## What Counts as a "Tool"?

- Web search
- Code execution (Python sandbox)
- File read / write
- Database query
- HTTP API call
- Calculator
- Another agent (subagent call)

---

## When to Use an Agent (vs Single Call)

**Use an agent when:**
- Task requires 3+ sequential steps
- Steps depend on results of previous steps
- You don't know the path upfront
- Failures should be retried or worked around
- Tools need to be invoked

**Stick to a single call when:**
- Task is "answer this question"
- Steps are known and fixed
- Latency matters and tools aren't needed
- Simple transformation or classification

---

## Agent Termination Conditions

Always set at least one:
- Model returns a final answer (no tool call)
- Max steps limit reached (e.g., 20)
- Token budget exhausted
- Human interrupt triggered
- Error threshold exceeded

---

## Key Vocab

| Term | Meaning |
|---|---|
| **Agent loop** | The while-loop that keeps running perception→action cycles |
| **ReAct** | "Reason + Act" — the original agent loop formulation |
| **Tool call** | Structured request to execute a function |
| **Observation** | Tool result injected back into context |
| **Orchestrator** | Agent that delegates to other agents |
| **Subagent** | Agent spawned by an orchestrator |
| **Stop condition** | The rule that ends the loop |

---

## Golden Rules

1. Every agent needs a max-steps limit — never run an unbounded loop
2. Tools make the agent real — without them, it's just a chain of thoughts
3. Context is memory — the longer the loop, the more context grows
4. Adaptive = the model decides the path, not you
5. Agents add overhead — don't use them for simple tasks

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Visual_Guide.md](./Visual_Guide.md) | Step-by-step diagrams |

⬅️ **Prev:** [Track 3: Model Reference](../../03_Claude_API_and_SDK/13_Model_Reference/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Why Agent SDK?](../02_Why_Agent_SDK/Theory.md)
