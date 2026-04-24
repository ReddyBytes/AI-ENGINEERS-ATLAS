# LangGraph Fundamentals — Interview Q&A

## Beginner Level

**Q1: What is LangGraph and what problem does it solve?**

<details>
<summary>💡 Show Answer</summary>

**A:** LangGraph is a framework for building stateful, graph-based AI agent workflows. It solves the problem that LangChain chains are linear — they go A→B→C with no ability to loop, branch, or pause. LangGraph lets you model workflows as a directed graph with nodes (Python functions), edges (connections), and a shared State object. This is essential for real agents that need to retry, branch based on conditions, or coordinate multiple sub-agents.

</details>

---

**Q2: What is the difference between a node and an edge in LangGraph?**

<details>
<summary>💡 Show Answer</summary>

**A:** A **node** is a Python function that does work. It receives the current state, performs some action (calls an LLM, queries a database, makes a decision), and returns a dict with the fields it wants to update. An **edge** is a connection between two nodes — it tells LangGraph which node to execute after the current one finishes. Edges can be unconditional (always go to node B) or conditional (a router function decides which node to go to next).

</details>

---

**Q3: What is the State in LangGraph?**

<details>
<summary>💡 Show Answer</summary>

**A:** State is a Python `TypedDict` that holds all the data flowing through the graph. Every node receives a copy of the current state and returns a partial update. LangGraph automatically merges those updates into the state before passing it to the next node. Think of state as the shared whiteboard that all nodes read from and write to.

</details>

---

**Q4: What does `.compile()` do?**

<details>
<summary>💡 Show Answer</summary>

**A:** `.compile()` validates your graph (checks for disconnected nodes, missing edges, etc.) and returns a `CompiledGraph` object. This compiled object is a standard LangChain runnable — it has `.invoke()`, `.stream()`, and `.batch()` methods. You cannot run a graph without compiling it first.

</details>

---

## Intermediate Level

**Q5: What are conditional edges and how do you define them?**

<details>
<summary>💡 Show Answer</summary>

**A:** Conditional edges let you route to different nodes based on the current state. Instead of a fixed destination, you provide a **router function** that takes the state and returns a string — the name of the next node (or `END`). You define them with `graph.add_conditional_edges("source_node", router_function)`. The router function examines the state and returns the appropriate next node name. This is how you build branching logic in LangGraph.

</details>

---

**Q6: When should you use LangGraph instead of LangChain?**

<details>
<summary>💡 Show Answer</summary>

**A:** Use LangGraph when your workflow needs: (1) cycles or loops — the agent retries or iterates until a condition is met; (2) branching logic — different paths based on the state; (3) human-in-the-loop — pausing execution and resuming after human input; (4) multi-agent coordination — multiple specialized agents that hand off work to each other; (5) persistent state — saving progress and resuming later. Use plain LangChain for linear pipelines like RAG (retrieve → generate → respond) where no loops or branching are needed.

</details>

---

**Q7: How does state get updated between nodes?**

<details>
<summary>💡 Show Answer</summary>

**A:** Nodes return a Python dict containing only the fields they want to change — not the entire state. LangGraph merges this partial update into the full state using a **reducer** function. By default, the reducer simply overwrites the field with the new value. For lists (like a message history), you can use the `Annotated` type with `operator.add` as the reducer to *append* instead of *overwrite*. This merge behavior is what makes it safe to have nodes that only care about some fields in the state.

</details>

---

**Q8: What are START and END in LangGraph?**

<details>
<summary>💡 Show Answer</summary>

**A:** `START` and `END` are special sentinel nodes imported from `langgraph.graph`. They are not Python functions — they are markers. `START` represents the entry point of the graph; you always add an edge from `START` to your first real node with `graph.add_edge(START, "first_node")`. `END` represents a terminal state; any node with an edge to `END` can terminate the graph. A graph can have multiple paths to `END`.

</details>

---

## Advanced Level

**Q9: How does LangGraph enable human-in-the-loop workflows, and what is a checkpointer?**

<details>
<summary>💡 Show Answer</summary>

**A:** LangGraph supports human-in-the-loop via two mechanisms. First, you can configure `interrupt_before=["node_name"]` or `interrupt_after=["node_name"]` when compiling the graph. When the graph reaches that node, it pauses and raises an interrupt. Second, a **checkpointer** (like `MemorySaver` or `SqliteSaver`) is attached at compile time and automatically saves the entire graph state after every node execution to a persistent store. When the workflow is interrupted (for human review), the state is safely stored. When the human approves and the workflow resumes, it loads from the checkpoint and continues exactly where it left off. This combination allows safe, auditable human approval steps in production AI workflows.

</details>

---

## 📂 Navigation

**In this folder:**

| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Mental_Model.md](./Mental_Model.md) | Visual mental model |

⬅️ **Prev:** Section intro &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Nodes and Edges](../02_Nodes_and_Edges/Theory.md)
