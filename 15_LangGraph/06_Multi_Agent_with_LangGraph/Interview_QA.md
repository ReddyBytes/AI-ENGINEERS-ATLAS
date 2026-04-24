# Multi-Agent with LangGraph — Interview Q&A

## Beginner Level

**Q1: What is a multi-agent system and why is it better than a single large agent?**

<details>
<summary>💡 Show Answer</summary>

**A:** A multi-agent system is a collection of specialized AI agents that work together. Instead of one agent trying to do everything (research, write, review, execute), each agent has one focused job. This is better because: (1) context windows stay focused — each agent only sees information relevant to its task, improving quality; (2) system prompts can be specialized — the researcher can be instructed to "be thorough and cite sources" while the editor is instructed to "be concise and direct", with no conflict; (3) tools are scoped — a web search tool goes only to the researcher, a code execution tool goes only to the coder; (4) it is easier to debug and improve — when the research is poor, you fix the research agent, not the whole system.

</details>

---

<br>

**Q2: What is a supervisor agent in LangGraph?**

<details>
<summary>💡 Show Answer</summary>

**A:** A supervisor agent is an orchestrator that decides which specialist agent to call next. It does not do the actual work — it manages the overall workflow. In LangGraph, the supervisor is a node that reads the current state (what has been done so far) and returns an update to a field like `next_agent` indicating which specialist should work next. A conditional edge reads this field and routes to the appropriate specialist node. After the specialist runs, it routes back to the supervisor, which reassesses and either delegates to another specialist or terminates the workflow.

</details>

---

<br>

**Q3: How do agents in a LangGraph multi-agent system communicate with each other?**

<details>
<summary>💡 Show Answer</summary>

**A:** Agents communicate through the shared state TypedDict — they do not call each other directly or share variables. Each agent node reads from state, does its work, and writes its output to specific state fields. The supervisor reads those output fields to make routing decisions. For example, the researcher writes to `research_notes`, the writer reads `research_notes` and writes to `draft`, the reviewer reads `draft` and writes to `review_feedback`. State is the single communication channel — everything passes through it.

</details>

---

## Intermediate Level

**Q4: What is the subgraph pattern in LangGraph multi-agent systems?**

<details>
<summary>💡 Show Answer</summary>

**A:** In the subgraph pattern, each specialist agent is itself a complete, compiled LangGraph graph. Instead of a single Python function, the specialist is built as a `StateGraph` with its own nodes, edges, and potentially its own internal cycles. You then wrap the compiled specialist graph in a regular Python function that calls `specialist_app.invoke(...)` and returns the relevant results. This function becomes a node in the parent (supervisor) graph. The benefit is that specialists can have complex internal logic — an inner retry loop, tool calls, reflection steps — without exposing that complexity to the supervisor.

</details>

---

<br>

**Q5: What is the Send API in LangGraph and when would you use it?**

<details>
<summary>💡 Show Answer</summary>

**A:** The `Send` API allows you to dispatch multiple agent nodes in parallel. Instead of a router function returning a single node name string, it returns a list of `Send` objects, each specifying a target node and the state to send to it. Both target nodes run concurrently. Their results are merged back into the main state using reducers. You use it when two or more agents can work independently on the same task simultaneously — for example, a researcher gathering background info at the same time as an analyst running data queries. Parallel execution reduces total wall-clock time when tasks don't depend on each other.

</details>

---

<br>

**Q6: How do you terminate a supervisor loop?**

<details>
<summary>💡 Show Answer</summary>

**A:** The supervisor must have an explicit termination condition. Common patterns: (1) A state flag — `is_complete: bool` set by the supervisor when all tasks are done, with the router returning `END` when this flag is `True`; (2) A sentinel value in `next_agent` — the supervisor returns `next_agent: "FINISH"` and the router returns `END` when it sees this value; (3) A completed tasks set — the supervisor checks whether all required tasks appear in a `completed_tasks` list in state. Without one of these conditions, the supervisor will either keep delegating (infinite loop) or eventually hit `recursion_limit` and raise a `GraphRecursionError`.

</details>

---

## Advanced Level

**Q7: How would you design a multi-agent content creation pipeline that can produce different content types (blog posts, social media posts, video scripts) using the same supervisor but different specialist combinations?**

<details>
<summary>💡 Show Answer</summary>

**A:** The design would use: (1) A `content_type` field in state set by the initial input; (2) A supervisor that reads `content_type` and builds a task plan — the plan for a blog post might be [researcher, outliner, writer, editor] while a social post plan might be [researcher, copywriter]; (3) A `task_queue: Annotated[list, ???]` in state that the supervisor populates on first run and pops from on subsequent runs; (4) Specialist nodes that are always available but only called when the task queue includes their name; (5) An `iteration_count` for safety. This architecture is data-driven: adding a new content type means adding a new task plan mapping, not modifying the supervisor's core logic. Each specialist node is stateless with respect to content type — it just processes what it receives in state.

</details>

---

<br>

**Q8: What are the tradeoffs between the supervisor pattern and a fixed-pipeline multi-agent graph?**

<details>
<summary>💡 Show Answer</summary>

**A:** A **fixed pipeline** (researcher → writer → reviewer, always in that order) is simpler, faster, and easier to debug. Use it when the sequence is always the same. A **supervisor pattern** (dynamic routing) is more flexible — the supervisor can skip steps, repeat steps, add new agents based on what it finds, or handle unexpected cases. Use it when the workflow is genuinely dynamic and depends on what the previous agent produced. The tradeoffs: supervisor pattern adds latency (each agent completes before the supervisor decides the next step), adds LLM calls (the supervisor itself is usually an LLM), and is harder to debug (the routing logic is opaque — an LLM decision). Start with a fixed pipeline whenever possible; upgrade to a supervisor only when you need dynamic routing.

</details>

---

## 📂 Navigation

**In this folder:**

| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | Full architecture diagrams |
| [📄 Code_Example.md](./Code_Example.md) | Working code example |

⬅️ **Prev:** [Human-in-the-Loop](../05_Human_in_the_Loop/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Streaming and Checkpointing](../07_Streaming_and_Checkpointing/Theory.md)
