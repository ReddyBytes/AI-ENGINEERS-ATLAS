# Cycles and Loops — Interview Q&A

## Beginner Level

**Q1: What is a cycle in LangGraph and how is it different from a LangChain chain?**

<details>
<summary>💡 Show Answer</summary>

**A:** A cycle in LangGraph is an edge that points backward in the graph — for example, from a node that checks quality back to a node that generates content. This creates a loop where the graph can run the same nodes multiple times. LangChain LCEL chains are directed acyclic graphs (DAGs): data flows in one direction from start to finish with no way to loop back. LangGraph supports cycles, which is the core reason it exists — agents need to retry, iterate, and keep going until a condition is satisfied.

</details>

---

**Q2: How do you create a cycle in LangGraph?**

<details>
<summary>💡 Show Answer</summary>

**A:** A cycle is just a regular edge that happens to point backward: `graph.add_edge("evaluate", "generate")`. If `evaluate` comes after `generate` in your intended flow, this creates a loop. There is nothing special about the syntax — it is the same `add_edge` call you use for any other connection. The graph becomes cyclic the moment you create a path that leads back to a previously-visited node.

</details>

---

**Q3: What is recursion_limit and why does it exist?**

<details>
<summary>💡 Show Answer</summary>

**A:** `recursion_limit` is a configuration parameter that caps the total number of node executions in a single graph run. It exists as a safety net against infinite loops. If your loop termination condition has a bug (or the LLM keeps calling tools indefinitely), the `recursion_limit` will stop execution and raise a `GraphRecursionError` instead of running forever or crashing your server. The default is 25. You set it when calling invoke: `app.invoke(state, config={"recursion_limit": 50})`. Note that it counts *node executions*, not loop iterations.

</details>

---

## Intermediate Level

**Q4: What is the ReAct loop pattern in LangGraph?**

<details>
<summary>💡 Show Answer</summary>

**A:** ReAct (Reason + Act) is a pattern where an LLM alternates between reasoning and acting. In LangGraph, the loop has two nodes: `call_llm` and `run_tools`. The LLM either calls tools (loop continues) or provides a final answer (loop exits). The router checks whether the LLM's last message contains tool calls — if yes, route to `run_tools`, then back to `call_llm`; if no, route to `END`. The key insight is that the LLM itself decides when to stop, making termination emergent rather than hardcoded. This is the standard pattern for tool-using agents.

</details>

---

**Q5: What are the two types of loop termination conditions and why do you need both?**

<details>
<summary>💡 Show Answer</summary>

**A:** The two types are: (1) **quality-based termination** — the loop exits when the output meets a threshold (e.g., `score >= 0.9`, `tests_pass == True`); and (2) **limit-based termination** — the loop exits after a maximum number of iterations (e.g., `attempts >= 10`). You need both because quality-based termination alone can create infinite loops if the quality condition is never met. Limit-based termination alone gives you an answer but not necessarily a good one. Together they create a loop that: tries to achieve quality, but gives up gracefully and returns the best result so far if it cannot.

</details>

---

**Q6: If a graph has 3 nodes per loop iteration and recursion_limit is set to 25, how many full loop iterations can it run?**

<details>
<summary>💡 Show Answer</summary>

**A:** Eight full iterations. Each loop iteration uses 3 node executions (3 × 8 = 24), which is under the limit of 25. The 25th execution would start a 9th iteration but be cut off mid-loop. This is why you should calculate your `recursion_limit` as: `nodes_per_loop × expected_max_iterations × 1.2` (20% buffer). For 3 nodes and 10 max iterations: `3 × 10 × 1.2 = 36`. So set `recursion_limit=36`.

</details>

---

## Advanced Level

**Q7: How would you implement a loop that detects stalled progress and exits early to avoid wasting compute?**

<details>
<summary>💡 Show Answer</summary>

**A:** Store a history of scores in state using an accumulating list reducer. In the router function, check the last N scores: if the variance is below a threshold, the loop has stalled and should exit. Example: `recent_scores = state["score_history"][-3:]`. If `len(recent_scores) >= 3 and max(recent_scores) - min(recent_scores) < 0.01`, return `END`. This pattern is useful in optimization loops where the improvement curve flattens — continuing to iterate wastes compute without improving the result. You can also log a warning when stall exit is triggered so you can later tune your prompts or scoring function.

</details>

---

**Q8: What is the difference between using recursion_limit as the primary loop termination vs as a safety net, and why does it matter?**

<details>
<summary>💡 Show Answer</summary>

**A:** Using `recursion_limit` as the *primary* termination mechanism (i.e., you don't write termination logic in your router, you just rely on the error) is bad practice for several reasons: (1) `GraphRecursionError` is an exception — catching and handling it adds complexity and the final state may be in an undefined intermediate state; (2) you cannot distinguish "we successfully completed N iterations and the result is X" from "we were cut off mid-loop unexpectedly"; (3) there is no way to capture the best result found so far before the error is raised. The right model: your router has proper `if attempts >= max: return END` logic, and `recursion_limit` is a backstop that fires only if there is a bug in your termination logic. Treat `GraphRecursionError` as a programming error signal, not normal control flow.

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

⬅️ **Prev:** [State Management](../03_State_Management/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Human-in-the-Loop](../05_Human_in_the_Loop/Theory.md)
