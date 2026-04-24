# Nodes and Edges — Interview Q&A

## Beginner Level

**Q1: What is a node in LangGraph?**

<details>
<summary>💡 Show Answer</summary>

**A:** A node is a plain Python function with the signature `def node_name(state: StateType) -> dict`. It receives the current state of the graph, does some work (calls an LLM, runs logic, queries a database), and returns a dict containing only the state fields it wants to update. Nodes are the workers in the graph — they do not control flow directly, they just do their job and return results.

</details>

---

**Q2: What is an edge in LangGraph?**

<details>
<summary>💡 Show Answer</summary>

**A:** An edge is a connection between two nodes that tells LangGraph which node to execute after the current one finishes. Unconditional edges always go from node A to node B: `graph.add_edge("a", "b")`. Conditional edges use a router function to decide at runtime: `graph.add_conditional_edges("a", router_fn)`. Without edges, nodes are isolated — edges define the flow of execution.

</details>

---

**Q3: What are START and END?**

<details>
<summary>💡 Show Answer</summary>

**A:** `START` and `END` are special sentinel values imported from `langgraph.graph`. They are not Python functions. `START` marks where the graph begins — you must add `graph.add_edge(START, "first_node")` for the graph to know where to start. `END` marks a terminal point — any node with an edge to `END` can terminate the graph. A graph can have multiple paths to `END` (e.g., different branches that all eventually finish).

</details>

---

**Q4: What must a node always return?**

<details>
<summary>💡 Show Answer</summary>

**A:** A node must always return a Python dict. The dict should contain only the keys it wants to update in the state. Returning `{}` (empty dict) is valid — it means the node ran but changed nothing. Returning `None` (no return statement) will cause an error when LangGraph tries to merge the update into the state.

</details>

---

## Intermediate Level

**Q5: What is a router function and how do you write one?**

<details>
<summary>💡 Show Answer</summary>

**A:** A router function is a Python function that takes the current state as its only argument and returns a string — the name of the next node to execute, or the `END` constant to terminate. You attach it to a conditional edge: `graph.add_conditional_edges("my_node", my_router)`. The router runs after `my_node` completes and its return value determines which node runs next. The most important rule: every code path in the router must return a value — returning `None` causes a runtime error.

</details>

---

**Q6: Can a graph have multiple nodes pointing to END?**

<details>
<summary>💡 Show Answer</summary>

**A:** Yes, and this is a common and correct pattern. In a branching graph, multiple branches can each terminate independently. For example, in a customer service graph: `handle_order → END`, `handle_refund → END`, and `escalate → END` are all valid and can coexist. LangGraph considers the graph done when *any* node routes to `END` and that node's execution completes. The final state at that point is returned to the caller.

</details>

---

**Q7: What is the difference between an unconditional edge and a conditional edge?**

<details>
<summary>💡 Show Answer</summary>

**A:** An unconditional edge is hardcoded: `add_edge("a", "b")` always routes from a to b, regardless of what state contains. A conditional edge uses a router function that runs after the source node and dynamically returns the next destination: `add_conditional_edges("a", router)`. Use unconditional edges when flow is always the same (e.g., "after fetching data, always format it"). Use conditional edges when the next step depends on the result of the current step (e.g., "if quality passes, ship; if it fails, fix and retry").

</details>

---

**Q8: What happens if a router function returns a node name that does not exist in the graph?**

<details>
<summary>💡 Show Answer</summary>

**A:** LangGraph raises a runtime error when the graph tries to route to the unknown node. This error is not caught at compile time — the `.compile()` step does not validate that all strings returned by router functions are valid node names (since routers are runtime functions). This is one of the most common bugs in LangGraph: a typo in a node name returned by a router will only surface when that code path is actually executed. Always test all branches of your routers.

</details>

---

## Advanced Level

**Q9: How would you implement a fan-out pattern in LangGraph, where one node triggers parallel work across multiple nodes?**

<details>
<summary>💡 Show Answer</summary>

**A:** LangGraph supports parallel node execution through the `Send` API. Instead of a single string, the router function can return a list of `Send` objects, each specifying a node and the state to send to it. This triggers those nodes to run in parallel. The results are then merged back into the main state. For simpler cases without true parallelism, you can simulate fan-out by having a coordinator node that updates state with all needed inputs, followed by a sequential chain of worker nodes. True parallel execution via `Send` is more complex but achieves genuine concurrency and is used in advanced multi-agent patterns.

</details>

---

## 📂 Navigation

**In this folder:**

| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Working code example |

⬅️ **Prev:** [LangGraph Fundamentals](../01_LangGraph_Fundamentals/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [State Management](../03_State_Management/Theory.md)
