# State Management — Interview Q&A

## Beginner Level

**Q1: What is state in LangGraph and why is it needed?**

<details>
<summary>💡 Show Answer</summary>

**A:** State is a Python `TypedDict` that holds all data flowing through the graph. Every node receives the full state, does its work, and returns a partial dict of updates. State is needed because nodes cannot call each other directly — the only way one node can pass information to another is by writing to state. Think of it as the shared whiteboard in a team — everyone reads from it and writes to it, but no one passes notes directly between individuals.

</details>

---

**Q2: What is the difference between a full state and a partial update?**

<details>
<summary>💡 Show Answer</summary>

**A:** The full state contains all the fields defined in your TypedDict — it is the complete picture of the workflow at a given moment. A partial update is what a node *returns*: a dict containing only the fields that node changed. LangGraph merges the partial update into the full state before passing it to the next node. This means if your state has 10 fields but a node only needs to update 1, it returns a dict with just that 1 field — the other 9 pass through unchanged.

</details>

---

**Q3: What is a TypedDict and why does LangGraph use it for state?**

<details>
<summary>💡 Show Answer</summary>

**A:** `TypedDict` is a Python type from the `typing` module that creates a dictionary with declared, typed keys. Unlike a regular dict, a TypedDict tells type checkers (and developers) exactly what keys are allowed and what types they should hold. LangGraph uses TypedDict for state because: (1) it provides clear documentation of what data the graph needs, (2) it enables IDE autocompletion inside nodes, and (3) it allows type validation with mypy or pyright to catch field name typos before running.

</details>

---

## Intermediate Level

**Q4: What is a reducer in LangGraph and when do you need one?**

<details>
<summary>💡 Show Answer</summary>

**A:** A reducer is a function that defines how a field's update gets merged into the existing state. Without a reducer, updates **overwrite**: if the current state has `results: ["a", "b"]` and a node returns `results: ["c"]`, the new state is `results: ["c"]` — the original items are lost. With the `operator.add` reducer (declared via `Annotated[list, operator.add]`), the result is `results: ["a", "b", "c"]` — the new list is appended. You need reducers whenever you want to *accumulate* data across multiple node executions rather than replace it. Common cases: message histories, collected search results, accumulated errors.

</details>

---

**Q5: What is MessagesState and how is it different from a custom TypedDict?**

<details>
<summary>💡 Show Answer</summary>

**A:** `MessagesState` is a pre-built state class provided by LangGraph specifically for chat applications. It has a single field `messages: Annotated[list[BaseMessage], add_messages]`. The `add_messages` reducer is smarter than `operator.add`: it appends new messages to the list AND handles deduplication by message ID (so if you re-inject a tool result, it replaces rather than duplicates). Using `MessagesState` saves you from writing the boilerplate and ensures correct message handling. You extend it for custom fields: `class MyState(MessagesState): extra_field: str`.

</details>

---

**Q6: Why is it wrong to mutate state directly inside a node function?**

<details>
<summary>💡 Show Answer</summary>

**A:** Mutating state directly inside a node (`state["count"] += 1`) is wrong for three reasons: (1) LangGraph's merge mechanism expects a return value — if you mutate and return `{}`, the merged state will reflect your mutation *and* have inconsistent behavior, depending on whether LangGraph copied the state before passing it; (2) in parallel or async execution, direct mutation causes race conditions where multiple nodes fight over the same object; (3) checkpointing captures the pre-node state and the node's return value separately — direct mutations break this model. Always return a new dict: `return {"count": state["count"] + 1}`.

</details>

---

**Q7: What types of values should NOT be stored in state?**

<details>
<summary>💡 Show Answer</summary>

**A:** State gets serialized by checkpointers (MemorySaver, SqliteSaver) so it can be saved and resumed. Values that cannot be serialized will break checkpointing. Avoid storing: open file handles, database connection objects, threading locks, Python generator objects, PIL/OpenCV images (store image paths or base64 strings instead), and lambda functions. Stick to serializable Python types: strings, numbers, booleans, lists, dicts, and dataclasses with `__dict__`.

</details>

---

## Advanced Level

**Q8: How would you design state for a multi-step document processing pipeline that validates each field and can retry individual failed steps?**

<details>
<summary>💡 Show Answer</summary>

**A:** The state would need: (1) `raw_document: str` — the original input; (2) `extracted_fields: dict` — output of the extraction node; (3) `validation_errors: Annotated[list[str], operator.add]` — accumulated errors using a reducer so multiple validation runs append rather than overwrite; (4) `validated_fields: dict` — fields that passed validation; (5) `retry_counts: dict[str, int]` — per-field retry counters; (6) `max_retries: int` — configured at graph start; (7) `is_complete: bool` — termination flag. The router function checks `is_complete` or `max(retry_counts.values()) >= max_retries` to decide whether to loop back or terminate. This design keeps each concern in a named, typed field and makes the router logic trivially readable.

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

⬅️ **Prev:** [Nodes and Edges](../02_Nodes_and_Edges/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Cycles and Loops](../04_Cycles_and_Loops/Theory.md)
