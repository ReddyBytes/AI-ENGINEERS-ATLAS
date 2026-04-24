# Streaming and Checkpointing — Interview Q&A

## Beginner Level

**Q1: What is the difference between invoke() and stream() in LangGraph?**

<details>
<summary>💡 Show Answer</summary>

**A:** `.invoke()` runs the entire graph synchronously and returns only the final state when execution is complete. You see nothing until the graph finishes. `.stream()` runs the graph but yields an output after each node completes — you get chunks of progress as the work happens. Both produce the same final state; the difference is when you receive the information. Use `.invoke()` for background jobs where no user is waiting. Use `.stream()` for user-facing applications where showing progress is important.

</details>

---

<br>

**Q2: What is a checkpointer in LangGraph and what does it store?**

<details>
<summary>💡 Show Answer</summary>

**A:** A checkpointer is a storage backend attached at compile time that automatically saves the complete graph state after every node execution. It stores the full state TypedDict as a "checkpoint" keyed by the `thread_id`. This enables: (1) human-in-the-loop workflows that pause and resume; (2) conversation persistence across multiple turns; (3) crash recovery from the last checkpoint; (4) state history for auditing. Without a checkpointer, state only exists in memory during a single `.invoke()` call and is lost when the call returns.

</details>

---

<br>

**Q3: What is a thread_id and how does it enable conversation memory?**

<details>
<summary>💡 Show Answer</summary>

**A:** A `thread_id` is a string you provide in the config (`{"configurable": {"thread_id": "..."}}`) that identifies one specific conversation or workflow run. When a checkpointer is attached, LangGraph saves the state after each node under the thread_id key. On the next `.invoke()` call with the same thread_id and a MessagesState graph, LangGraph loads the saved state (including full message history), adds the new message, and runs the graph — giving the LLM access to everything said in previous turns. Each unique thread_id gets its own isolated state, so different users' conversations don't interfere.

</details>

---

## Intermediate Level

**Q4: What are the different stream_mode options in LangGraph's .stream() method?**

<details>
<summary>💡 Show Answer</summary>

**A:** LangGraph's `.stream()` supports several modes: (1) `"updates"` (default) — yields `{node_name: {partial_state_update}}` after each node; best for tracking which node ran and what it changed; (2) `"values"` — yields the complete current state after each node; best for watching how state evolves step by step; (3) `"debug"` — yields detailed internal execution information; best for development debugging; (4) `"messages"` — yields individual message chunks; best for streaming LLM output in chat applications without using the async events API. Choose based on what your application needs to display.

</details>

---

<br>

**Q5: What is astream_events() and when should you use it instead of stream()?**

<details>
<summary>💡 Show Answer</summary>

**A:** `.astream_events()` is an async generator that yields all execution events including individual LLM token events. When an LLM is generating a response inside a node, `astream_events()` yields each token as it is produced — allowing you to display the text appearing word by word, like ChatGPT. You use it when you need token-level streaming (most chat UI applications). It requires: (1) the LLM to have `streaming=True` set; (2) async execution (`async for`); (3) `version="v2"` parameter for stability. `.stream()` with `stream_mode="updates"` shows node-by-node progress; `astream_events` shows token-by-token progress within each node.

</details>

---

<br>

**Q6: What is the difference between MemorySaver and SqliteSaver, and when should you use each?**

<details>
<summary>💡 Show Answer</summary>

**A:** `MemorySaver` stores all checkpoints in an in-process Python dictionary. It requires zero setup, is fast, and is appropriate for development and automated testing. The critical limitation: all data is lost when the process restarts, and it does not work across multiple processes or servers. `SqliteSaver` stores checkpoints in a SQLite database file on disk. It requires specifying a file path (`from_conn_string("checkpoints.db")`), persists across restarts, and works for single-process production deployments. It does not work across multiple concurrent processes (SQLite has write-lock limitations). For multi-process production environments (containerized apps, multiple workers), use a shared database like PostgreSQL with `PostgresSaver`.

</details>

---

## Advanced Level

**Q7: How would you implement a real-time research agent dashboard that shows each agent's progress as it happens and stores conversation history?**

<details>
<summary>💡 Show Answer</summary>

**A:** The implementation would use: (1) `SqliteSaver` attached at compile time for conversation persistence; (2) a consistent thread_id per user session stored in the application database; (3) `.stream(stream_mode="updates")` to yield `{node_name: updates}` chunks; (4) a WebSocket connection from the backend to the frontend; on each yielded chunk, send a WebSocket message like `{"node": "researcher", "status": "complete", "output": "..."}` which the frontend displays as a progress update; (5) for LLM token streaming within nodes, use `astream_events` instead and filter for `on_chat_model_stream` events, forwarding each token via WebSocket; (6) at the end of each `.stream()` iteration, call `app.get_state(config)` to retrieve the full final state for display.

</details>

---

<br>

**Q8: How does checkpointing interact with graph cycles/loops? Does it checkpoint every iteration of a loop?**

<details>
<summary>💡 Show Answer</summary>

**A:** Yes — checkpointing is not loop-aware, it fires after every single node execution regardless of whether that node is in a loop. If your graph has a loop with 2 nodes and it runs 10 iterations, the checkpointer saves 20 checkpoints (2 per iteration × 10 iterations). You can see all these snapshots via `app.get_state_history(config)`. This has two implications: (1) storage: in loops with many iterations, checkpoint storage grows quickly — plan accordingly for long-running loops; (2) recovery: if a long-running loop crashes after iteration 7, you can resume from the checkpoint at the end of iteration 7, not from the beginning — this is very valuable for expensive operations like LLM calls or external API calls that you don't want to repeat unnecessarily.

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

⬅️ **Prev:** [Multi-Agent with LangGraph](../06_Multi_Agent_with_LangGraph/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Build with LangGraph](../08_Build_with_LangGraph/Project_Guide.md)
