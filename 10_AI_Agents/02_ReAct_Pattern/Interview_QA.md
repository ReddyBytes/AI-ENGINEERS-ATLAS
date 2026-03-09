# ReAct Pattern — Interview Q&A

## Beginner

**Q1: What does ReAct stand for and what problem does it solve?**

ReAct stands for **Reasoning + Acting**. It was introduced in a 2022 paper from Google Brain.

The problem it solves: agents that just generate actions without explicit reasoning often pick the wrong tool, hallucinate facts, or lose track of the goal on multi-step tasks.

ReAct fixes this by requiring the agent to write out a **Thought** — explicit reasoning — before every action. This forces the LLM to be deliberate about what it knows and what it needs, rather than guessing.

---

**Q2: What is the Thought → Action → Observation loop?**

It's the core cycle of the ReAct pattern:

- **Thought**: the agent writes out its reasoning. "I need to find the population of Tokyo. I'll use the search tool."
- **Action**: the agent calls a tool. `search[Tokyo population 2024]`
- **Observation**: the tool returns a result. "Tokyo's population is approximately 13.9 million in the city and 37.4 million in the greater metropolitan area."

Then the agent writes another **Thought** using what it just learned, takes another **Action**, gets another **Observation**, and repeats until it can write a **Final Answer**.

---

**Q3: Why is writing the Thought step important? Can't the agent just act directly?**

Technically yes — an agent can call tools without writing reasoning first. But it's much less reliable.

Writing the Thought does two things:

1. It **grounds the action** — the agent has to articulate what it knows before acting, which reduces hallucination and wrong tool choices.
2. It creates a **readable trace** — you can see exactly why the agent did what it did, which makes debugging possible.

It's like the difference between a student who just writes "42" as their answer vs. one who shows their work. The one who shows work is more likely to be right, and when they're wrong, it's easy to see where the mistake was.

---

## Intermediate

**Q4: How does ReAct differ from Chain-of-Thought (CoT) prompting?**

Both involve getting the LLM to write out reasoning. But they're used differently:

**Chain-of-Thought** is reasoning only — no tool calls. The LLM thinks through a problem step by step purely from its internal knowledge.

**ReAct** interleaves reasoning with actions. Each thought leads to a tool call, and the tool output informs the next thought. The reasoning is grounded in real-world observations, not just the model's training data.

CoT: Think → Think → Think → Answer (no external tools)
ReAct: Think → Act → Observe → Think → Act → Observe → Answer (with tools)

ReAct is like CoT but connected to the real world.

---

**Q5: What happens when a tool call in ReAct returns an error or unexpected result?**

This is where the Thought step becomes especially valuable.

If a tool returns an error, the agent should:
1. Write a Thought acknowledging the error: "The search returned no results. My query may have been too specific."
2. Revise the approach: "I'll try a broader search term."
3. Take a different Action: `search[Tokyo population]` instead of `search[Tokyo population in 2024 official census data]`

A well-implemented ReAct agent is self-correcting. The loop naturally allows for retrying with different approaches. This is why the Observation step is so important — it gives the agent feedback to adjust.

---

**Q6: How is ReAct implemented in frameworks like LangChain?**

In LangChain, when you create an agent with `initialize_agent` using the `ZERO_SHOT_REACT_DESCRIPTION` agent type, it automatically uses a ReAct-style prompt template under the hood.

The prompt template includes:
- The available tools and their descriptions
- Instructions to use the Thought/Action/Observation format
- A list of the previous steps (the scratchpad)

LangChain handles the orchestration loop: after each Action, it calls the actual tool function, gets the result, adds it as an Observation, and passes everything back to the LLM for the next Thought.

You don't have to manually implement the loop — the framework does it. But understanding ReAct means you can debug it when things go wrong.

---

## Advanced

**Q7: What are the limitations of the ReAct pattern for long tasks?**

Several challenges emerge as tasks get longer:

1. **Context window overflow** — every Thought, Action, and Observation gets added to the prompt. Long trajectories exceed the model's context limit. Solution: summarize older steps.

2. **Error compounding** — an incorrect Observation early in the trajectory can lead the agent in the wrong direction for all subsequent steps. The agent builds on bad information.

3. **Verbosity overhead** — each Thought adds tokens, which increases cost and latency. For simple tasks, this overhead isn't worth it.

4. **Reasoning quality degrades** — very long ReAct traces sometimes show the model starting to produce lower-quality Thoughts as the context gets crowded.

Mitigations: truncating the trajectory, summarizing old steps, and breaking very long tasks into sub-tasks.

---

**Q8: How would you evaluate the quality of a ReAct agent's trajectory?**

Evaluation should happen at multiple levels:

1. **Final answer accuracy** — is the answer correct? (Basic benchmark evaluation)
2. **Trajectory efficiency** — how many steps did it take? Fewer steps for the same result is better.
3. **Tool selection quality** — did it pick the right tool each time? (Check Action choices)
4. **Thought coherence** — do the Thoughts logically connect to the Actions? Are they actually reasoning or just restating the question?
5. **Error recovery** — when a tool returned a bad result, did the agent adapt correctly?
6. **Hallucination rate** — did the Final Answer use information from Observations, or did it invent facts not in any Observation?

A good evaluation framework logs the full trajectory and checks each of these dimensions, not just the final answer.

---

**Q9: Compare ReAct with Plan-and-Execute agents. When would you choose one over the other?**

**ReAct** is reactive and interleaved. It decides each step based on what it learned from the previous step. Good for exploratory tasks where you don't know upfront what you'll find.

**Plan-and-Execute** generates a full plan first (a list of steps), then executes each step. Good for structured tasks where the steps are predictable.

| | ReAct | Plan-and-Execute |
|---|---|---|
| Planning | Step by step | Upfront |
| Adaptability | High — adjusts as it goes | Low — follows the plan |
| Predictability | Lower | Higher |
| Good for | Research, exploration | Known workflows |
| Failure mode | Can go off in the wrong direction | Plan may be wrong from the start |

In practice, many production agents combine both: use a planner to create a task list, then use ReAct within each task for tool-grounded execution.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [01 Agent Fundamentals](../01_Agent_Fundamentals/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 Tool Use](../03_Tool_Use/Theory.md)
