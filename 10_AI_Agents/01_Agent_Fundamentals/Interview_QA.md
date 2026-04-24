# AI Agents — Interview Q&A

## Beginner

**Q1: What is an AI agent and how is it different from a regular chatbot?**

<details>
<summary>💡 Show Answer</summary>

A chatbot takes one input and gives one output. It's a single LLM call.

An AI agent is different because it has a **loop**. It takes a goal, decides what action to take, takes that action (often using a tool), sees the result, and keeps going until the goal is complete. It can make multiple decisions, use multiple tools, and adapt based on what it learns along the way.

The key difference: a chatbot answers, an agent acts.

</details>

---

**Q2: What are the four main components of an AI agent?**

<details>
<summary>💡 Show Answer</summary>

1. **LLM (the brain)** — reasons about the situation and decides what to do next
2. **Tools (the hands)** — functions the agent can call to interact with the world (search, APIs, code execution)
3. **Memory (the notebook)** — tracks what has happened so the agent doesn't start from scratch each loop
4. **The loop (the work cycle)** — the architecture that runs perceive → think → act → observe → repeat until the task is done

</details>

---

**Q3: What is the agent loop? Walk me through each step.**

<details>
<summary>💡 Show Answer</summary>

The agent loop is the core cycle every agent runs:

1. **Perceive** — reads the current situation: the user's goal, previous messages, and any tool results from last iteration
2. **Think** — the LLM reasons about what to do next: what information is needed, which tool to use
3. **Act** — either calls a tool with specific parameters, or produces the final answer if the task is done
4. **Observe** — reads the tool's output and adds it to context
5. **Repeat** — if the goal isn't complete, goes back to thinking with the new information

The loop stops when the agent decides the task is done or when a maximum iteration limit is hit.

</details>

---

## Intermediate

**Q4: How does the agent decide which tool to use?**

<details>
<summary>💡 Show Answer</summary>

The agent reads the **tool schemas** — descriptions of each available tool including its name, what it does, and what parameters it takes.

When the LLM needs to do something, it matches its current need against the tool descriptions. The better and clearer the description, the more likely the agent picks the right tool.

For example: if the agent needs current information, it reads that `search_web` "searches the internet for up-to-date information" and correctly calls that instead of relying on its training data.

This is why writing good tool descriptions is critical. Vague or confusing descriptions lead to wrong tool choices.

</details>

---

**Q5: What is an "observation" in the context of an agent?**

<details>
<summary>💡 Show Answer</summary>

An observation is the **output returned after a tool call**.

When the agent calls `search_web("latest AI news")`, the search results come back — that's the observation. The agent adds this to its context and uses it to decide the next step.

Observations are how the agent learns from its actions. Without observations, the agent would act blindly — it would call tools but never use the results.

The full loop is: **action (tool call) → observation (tool result) → next thought (what this means for the task)**.

</details>

---

**Q6: What's the difference between in-context memory and external (vector) memory in agents?**

<details>
<summary>💡 Show Answer</summary>

**In-context memory** is everything in the current prompt — the conversation history, tool outputs, user messages. It's fast and immediate, but limited by the context window. Once that window is full, older information is dropped.

**External (vector) memory** stores information in a database outside the model. Facts are embedded as vectors and retrieved using semantic search when relevant. It persists across conversations and can hold much more information, but adds latency and retrieval complexity.

In-context is like working memory — what you're actively thinking about. External is like long-term memory — things you've learned that you can look up.

</details>

---

## Advanced

**Q7: How do you prevent an agent from looping forever?**

<details>
<summary>💡 Show Answer</summary>

Several mechanisms:

1. **Max iterations** — hard cap on the number of loop cycles. If hit, either return the best answer so far or raise an error.
2. **Stopping conditions** — explicitly teach the agent what "task complete" looks like. The prompt should include clear criteria.
3. **Timeout** — wall-clock time limit on the entire run.
4. **Detection logic** — check if the agent is repeating the same action. If the last 3 tool calls were identical, intervene.
5. **Structured output for completion** — require the agent to produce a specific "FINAL ANSWER:" token when done, so the orchestrator knows to stop.

In production, always set a max iteration limit. An agent without one is a potential infinite-loop bug waiting to happen.

</details>

---

**Q8: What are the main failure modes of AI agents?**

<details>
<summary>💡 Show Answer</summary>

1. **Hallucinated tool calls** — agent invents a tool that doesn't exist or calls a real tool with wrong parameters
2. **Infinite loops** — agent gets confused about whether the task is done and keeps trying
3. **Wrong tool selection** — picks the wrong tool because descriptions are unclear
4. **Context overflow** — conversation gets so long the model starts forgetting earlier parts
5. **Compounding errors** — a mistake early in the trajectory gets built on, leading the agent further from the correct answer
6. **Over-confidence** — agent produces a confident-sounding final answer before doing enough research

Mitigation: good tool descriptions, max iteration limits, trajectory logging, human-in-the-loop for irreversible actions.

</details>

---

**Q9: How would you design an agent for a high-stakes task like processing financial transactions?**

<details>
<summary>💡 Show Answer</summary>

Key design principles for high-stakes agents:

1. **Human-in-the-loop checkpoints** — before any irreversible action (payment, deletion), pause and require human confirmation
2. **Audit trail** — log every thought, tool call, observation, and decision with timestamps
3. **Sandboxed tools** — separate "read" tools (safe) from "write" tools (risky). Require explicit permission for writes.
4. **Idempotency** — design tools so calling them twice doesn't cause double-payments or duplicate entries
5. **Bounded autonomy** — restrict the agent to a specific, narrow set of allowed actions
6. **Rollback capability** — every action should be reversible if possible
7. **Monitoring and alerts** — track agent behavior in production, alert on anomalies (unusual tool call patterns, repeated failures)

The more consequential the action, the less autonomy you give the agent by default.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Mental_Model.md](./Mental_Model.md) | Agent mental model visual guide |

⬅️ **Prev:** [09 Build a RAG App](../../09_RAG_Systems/09_Build_a_RAG_App/Project_Guide.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [02 ReAct Pattern](../02_ReAct_Pattern/Theory.md)
