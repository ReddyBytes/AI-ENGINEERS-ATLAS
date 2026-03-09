# ReAct Pattern — Cheatsheet

**One-liner:** ReAct = Reasoning + Acting — the agent writes a Thought before every Action, then reads the Observation to reason again. This loop makes agents more reliable and transparent.

---

## Key Terms

| Term | What it means |
|---|---|
| **ReAct** | Reasoning + Acting — a prompting pattern from the 2022 Google Brain paper |
| **Thought** | The agent's written reasoning before taking an action — "what do I know, what do I need?" |
| **Action** | The tool call the agent makes after reasoning — `search[query]` or `calculator[expr]` |
| **Observation** | The result the tool returns — automatically added to context |
| **Trajectory** | The full sequence of Thought → Action → Observation → ... for one task |
| **Final Answer** | The special output that ends the ReAct loop |
| **Grounding** | Basing answers on actual tool results rather than the LLM's memory |
| **Scratchpad** | The intermediate thoughts and observations — used internally, not shown to the user |

---

## The ReAct Format (Quick Reference)

```
Thought: [reasoning about what to do]
Action: tool_name[input]
Observation: [tool output]
Thought: [reasoning about the observation]
Action: tool_name[input]
Observation: [tool output]
...
Final Answer: [answer to original question]
```

Repeat Thought → Action → Observation until you can write Final Answer.

---

## When to Use ReAct

**Use ReAct when:**
- The task needs multiple steps
- You need current information (use a search tool)
- You need precise calculation (use a calculator tool)
- You want the agent's reasoning to be inspectable
- You need to debug why an agent answered a certain way

**Don't use ReAct when:**
- Simple one-step questions that don't need tools
- Latency is critical (each thought adds tokens/time)
- You want a very specific, structured output format

---

## Golden Rules

1. **Always require a Thought before every Action.** This is what makes ReAct work. Skip it and you lose the grounding benefit.

2. **Observations must feed back into context.** The agent should see tool output before the next Thought.

3. **Set a Final Answer stopping condition.** The agent should only use "Final Answer:" when it has enough information to answer the question.

4. **Short, specific Actions are better.** `search[Who is the CEO of Apple 2024]` is better than `search[Apple]`.

5. **Keep Thoughts concise.** One or two sentences. Enough to explain the reasoning, not an essay.

6. **The Thought can catch mistakes.** If the Observation shows an error, the agent should Thought-reason about what went wrong and try differently.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [01 Agent Fundamentals](../01_Agent_Fundamentals/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 Tool Use](../03_Tool_Use/Theory.md)
