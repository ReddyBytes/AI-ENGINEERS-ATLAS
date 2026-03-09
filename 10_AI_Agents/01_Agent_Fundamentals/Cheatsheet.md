# AI Agents — Cheatsheet

**One-liner:** An AI agent is an LLM + tools + memory + a loop that keeps acting until a goal is complete.

---

## Key Terms

| Term | What it means |
|---|---|
| **Agent** | An LLM system that takes a goal, uses tools, and loops until the task is done |
| **LLM** | The reasoning engine — reads context, decides what to do next |
| **Tool** | A function the agent can call (search, calculator, API, database) |
| **Tool schema** | The description of a tool: name, what it does, what parameters it takes |
| **Memory** | How the agent tracks what's happened (in-context or vector store) |
| **Agent loop** | The cycle: Perceive → Think → Act → Observe → Repeat |
| **Observation** | The result returned after the agent calls a tool |
| **Trajectory** | The full sequence of thoughts and actions an agent took to reach the answer |
| **System prompt** | The instructions that tell the agent its role, tools, and behavior |
| **Final answer** | When the agent decides the goal is complete and returns the result |
| **Orchestrator** | The code that runs the loop, passes tool outputs back to the LLM |
| **Autonomy** | How much the agent decides for itself vs follows fixed rules |

---

## The Agent Loop (Quick Reference)

```
1. PERCEIVE  — Read the goal + current state + previous observations
2. THINK     — LLM decides: what should I do next?
3. ACT       — Call a tool OR produce the final answer
4. OBSERVE   — Read the tool's output
5. REPEAT    — Go back to step 1 if goal isn't done
```

---

## When to Use an Agent

**Use an agent when:**
- The task needs multiple steps
- You can't predict all the steps upfront
- The LLM needs to use external tools
- The task involves decisions based on live data

**Don't use an agent when:**
- The workflow is fixed and predictable → use a Chain
- You just need Q&A over your documents → use RAG
- You need speed and low cost → use a simpler pattern
- Mistakes are very costly → agents can make unexpected choices

---

## Golden Rules

1. **Give the LLM clear tool descriptions.** The agent decides what to use based on the description. Vague descriptions = wrong tool choices.

2. **Always set a max iteration limit.** Without it, a confused agent will loop forever.

3. **Log the trajectory.** The sequence of thoughts and actions is your best debugging tool.

4. **Start simple.** Add tools one at a time. Test each one. Don't give the agent 20 tools at once.

5. **The loop is the agent.** Everything else (memory, tools) just supports the loop.

6. **Trust but verify.** Agents make mistakes. Add validation before they take irreversible actions (sending emails, making payments).

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Mental_Model.md](./Mental_Model.md) | Agent mental model visual guide |

⬅️ **Prev:** [09 Build a RAG App](../../09_RAG_Systems/09_Build_a_RAG_App/Project_Guide.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [02 ReAct Pattern](../02_ReAct_Pattern/Theory.md)
