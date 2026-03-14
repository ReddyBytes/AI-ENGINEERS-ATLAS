# Human-in-the-Loop — Cheatsheet

## Key Terms

| Term | One-line meaning |
|---|---|
| **HITL** | Human-in-the-Loop — AI pauses for human review at critical steps |
| **Checkpointer** | Storage backend that saves graph state after every node execution |
| **MemorySaver** | In-process checkpointer — state lost on restart; use for dev/testing |
| **SqliteSaver** | File-based checkpointer — state persists to SQLite database |
| **thread_id** | Unique key identifying one workflow run; used to load/resume its state |
| **interrupt_before** | Pause execution BEFORE the named node runs |
| **interrupt_after** | Pause execution AFTER the named node runs |
| **get_state(config)** | Retrieve the current (paused) state for a thread |
| **update_state(config, values)** | Modify state values before resuming |

---

## The HITL Pattern — 5 Steps

```python
from langgraph.checkpoint.memory import MemorySaver

# Step 1: Compile with checkpointer AND interrupt
memory = MemorySaver()
app = graph.compile(
    checkpointer=memory,
    interrupt_before=["approval_node"]  # pause BEFORE this node runs
)

# Step 2: Run until interrupt (graph pauses here)
config = {"configurable": {"thread_id": "run-001"}}
app.invoke({"task": "Do something risky"}, config=config)

# Step 3: Inspect paused state
state = app.get_state(config)
print(state.values)

# Step 4: (Optional) Modify state before resuming
app.update_state(config, {"approved": True, "note": "Looks good"})

# Step 5: Resume execution
final = app.invoke(None, config=config)  # None = resume, don't restart
```

---

## interrupt_before vs interrupt_after

| | `interrupt_before` | `interrupt_after` |
|---|---|---|
| Pause timing | BEFORE node runs | AFTER node runs |
| Node's output in state? | No (node hasn't run) | Yes |
| Use case | Approve before action | Review output before next step |
| Example | Before `send_email` | After `analyze_content` |

---

## Checkpointer Comparison

| Checkpointer | Persistence | Multi-process | Use When |
|---|---|---|---|
| `MemorySaver` | In-memory only | No | Development, testing |
| `SqliteSaver` | SQLite file | No (single process) | Simple production |
| `PostgresSaver` | PostgreSQL | Yes | Multi-process production |

```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver

# MemorySaver
memory = MemorySaver()
app = graph.compile(checkpointer=memory)

# SqliteSaver
with SqliteSaver.from_conn_string("./checkpoints.db") as checkpointer:
    app = graph.compile(checkpointer=checkpointer)
```

---

## Getting and Modifying State

```python
# Get current state
state = app.get_state(config)
state.values         # dict of current state values
state.next           # tuple of nodes that will run next
state.config         # the config (thread_id lives here)

# Get state history (all checkpoints for this thread)
for snapshot in app.get_state_history(config):
    print(snapshot.values, snapshot.created_at)

# Update state (modify before resuming)
app.update_state(
    config,
    {"field_to_change": "new_value"}
)

# Resume
final = app.invoke(None, config=config)
```

---

## Thread ID Pattern

```python
# Each independent workflow run needs a unique thread_id
import uuid

def start_approval_workflow(task_data):
    thread_id = f"approval-{uuid.uuid4()}"
    config = {"configurable": {"thread_id": thread_id}}
    app.invoke(task_data, config=config)
    return thread_id  # Return to caller so they can resume later

def approve_workflow(thread_id, approval_note):
    config = {"configurable": {"thread_id": thread_id}}
    app.update_state(config, {"approval_note": approval_note, "approved": True})
    return app.invoke(None, config=config)
```

---

## Quick Debugging Checklist

- [ ] `checkpointer` passed to `.compile()`?
- [ ] `interrupt_before` or `interrupt_after` configured in `.compile()`?
- [ ] Same `thread_id` used for invoke, get_state, update_state, and resume?
- [ ] Resume uses `app.invoke(None, config)` — not `app.invoke(initial_state, config)`?
- [ ] Using `SqliteSaver` or better for production (not `MemorySaver`)?

---

## 📂 Navigation

**In this folder:**

| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Working code example |

⬅️ **Prev:** [Cycles and Loops](../04_Cycles_and_Loops/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Multi-Agent with LangGraph](../06_Multi_Agent_with_LangGraph/Theory.md)
