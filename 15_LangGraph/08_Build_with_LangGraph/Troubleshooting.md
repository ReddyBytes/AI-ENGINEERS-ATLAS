# LangGraph Troubleshooting Guide

## Common Errors and How to Fix Them

---

## Error 1: GraphRecursionError

```
langgraph.errors.GraphRecursionError: Recursion limit of 25 reached without hitting a stop condition.
```

**What it means**: Your graph has run 25 node executions without reaching `END`.

**Causes**:
1. A loop with no exit condition — the router always routes back
2. `recursion_limit` set too low for the number of iterations you need
3. A bug in your router function (e.g., `quality_score` is always low)

**Fix**:
```python
# Option 1: Increase recursion_limit
result = app.invoke(state, config={"recursion_limit": 100})

# Option 2: Add/fix your exit condition
def router(state):
    if state["attempts"] >= 5:
        return END    # Hard limit — this was missing!
    if state["score"] >= 0.8:
        return END
    return "try_again"

# Option 3: Debug by logging what the router sees
def router(state):
    print(f"DEBUG router: attempts={state['attempts']}, score={state['score']}")
    # ... rest of logic
```

**Rule of thumb**: `recursion_limit = (nodes_per_loop × max_loops) × 1.2`

---

## Error 2: KeyError inside a Node

```
KeyError: 'some_field'
```

**What it means**: A node tried to access `state["some_field"]` but that field doesn't exist in the state.

**Causes**:
1. You forgot to include the field in your initial `invoke()` call
2. Typo in the field name
3. Field exists in TypedDict but wasn't initialized

**Fix**:
```python
# Option 1: Always provide all fields in initial state
result = app.invoke({
    "question": "...",
    "search_results": [],    # Don't forget this!
    "attempts": 0,
    "max_attempts": 3,
    # etc.
})

# Option 2: Use .get() with defaults in nodes
def my_node(state):
    results = state.get("search_results", [])  # Safe access
    count = state.get("attempts", 0)
    return {"summary": f"Found {len(results)} results"}
```

---

## Error 3: Node Returned None / NoneType Error

```
TypeError: 'NoneType' object is not iterable
# or
Exception: Node returned None instead of a dict
```

**What it means**: A node function has no `return` statement (or returns nothing on some code path).

**Fix**:
```python
# WRONG — missing return
def my_node(state):
    do_some_work(state)
    # oops — no return statement

# CORRECT — always return a dict
def my_node(state):
    do_some_work(state)
    return {}  # even if no state changes, return empty dict

# WRONG — conditional path with no return
def my_node(state):
    if state["flag"]:
        return {"result": "done"}
    # if flag is False, falls through with no return!

# CORRECT — every path returns
def my_node(state):
    if state["flag"]:
        return {"result": "done"}
    return {"result": "skipped"}  # always return
```

---

## Error 4: Graph Starts But Immediately Ends / Does Nothing

**Symptom**: `app.invoke(state)` returns instantly with the initial state unchanged.

**Cause**: You forgot to add `graph.add_edge(START, "first_node")`.

**Fix**:
```python
# Check your graph construction — this line is required:
graph.add_edge(START, "first_node")

# Without it, the graph has no entry point and immediately terminates.
# You WILL NOT get an error at compile time — only silent failure at runtime.
```

---

## Error 5: Invalid Node Name in Router

```
ValueError: Node 'fetc_order' not found in graph
# or the graph routes to a node that never runs — silent bug
```

**What it means**: Your router function returns a string that doesn't match any node name.

**Cause**: Typo in the node name returned by a router function. Node names are plain strings — there is no autocomplete or type checking.

**Fix**:
```python
# Use constants for node names to avoid typos
RESEARCHER = "researcher"
WRITER = "writer"

graph.add_node(RESEARCHER, researcher_fn)
graph.add_node(WRITER, writer_fn)

def router(state):
    if not state["research"]:
        return RESEARCHER   # Uses the constant — typo-safe
    return WRITER

# Or validate in the router itself
VALID_NODES = {"researcher", "writer", "reviewer"}

def safe_router(state):
    decision = compute_decision(state)
    if decision not in VALID_NODES:
        raise ValueError(f"Router returned invalid node: {decision}")
    return decision
```

---

## Error 6: List Field Being Overwritten Instead of Appended

**Symptom**: After multiple loop iterations, your results list only contains the most recent results, not all accumulated results.

**Cause**: You defined the list field without a reducer. Without `Annotated[list, operator.add]`, every update overwrites the existing list.

**Fix**:
```python
from typing import Annotated
import operator

# WRONG — list will be overwritten on each update
class BadState(TypedDict):
    results: list    # No reducer

# CORRECT — list will be appended on each update
class GoodState(TypedDict):
    results: Annotated[list, operator.add]   # operator.add as reducer

# Then in your node:
def search_node(state: GoodState) -> dict:
    new_results = ["result 1", "result 2"]
    return {"results": new_results}   # These are APPENDED, not overwritten
```

---

## Error 7: Checkpointing with MemorySaver Across Processes

**Symptom**: State is lost between requests in a web server. `app.get_state(config)` returns `None` on the second request.

**Cause**: `MemorySaver` stores state in-process memory. In multi-process web servers (gunicorn, uvicorn with multiple workers), each worker has its own memory — checkpoints don't cross process boundaries.

**Fix**:
```python
# For local/single-process: MemorySaver is fine
from langgraph.checkpoint.memory import MemorySaver

# For production multi-process: use a shared database
from langgraph.checkpoint.sqlite import SqliteSaver

# SqliteSaver — shared file, single process or sequential access
with SqliteSaver.from_conn_string("checkpoints.db") as checkpointer:
    app = graph.compile(checkpointer=checkpointer)

# For true multi-process production: use PostgresSaver
# pip install langgraph-checkpoint-postgres
# from langgraph.checkpoint.postgres import PostgresSaver
```

---

## Error 8: interrupt_before Not Working (Graph Doesn't Pause)

**Symptom**: You configured `interrupt_before=["my_node"]` but the graph runs through `my_node` without pausing.

**Cause**: Most common cause is forgetting to attach a checkpointer. `interrupt_before` requires a checkpointer to save the state when it pauses.

**Fix**:
```python
# WRONG — interrupt without checkpointer
app = graph.compile(interrupt_before=["approval_node"])
# graph will NOT pause — there's nowhere to save the state

# CORRECT — interrupt WITH checkpointer
from langgraph.checkpoint.memory import MemorySaver
memory = MemorySaver()
app = graph.compile(
    checkpointer=memory,            # Required!
    interrupt_before=["approval_node"]
)

# Also: always use the same config/thread_id for the paused run and the resume
config = {"configurable": {"thread_id": "my-workflow"}}
app.invoke(initial_state, config=config)  # pauses
app.invoke(None, config=config)           # resumes (same config!)
```

---

## Error 9: Resume with invoke(None) Starts a New Graph Instead

**Symptom**: Calling `app.invoke(None, config=config)` after an interrupt starts a fresh graph run rather than resuming.

**Cause**: The thread_id in your config doesn't match the one used when the graph paused, OR there is no checkpoint saved for that thread_id.

**Fix**:
```python
# Store and reuse the exact same config
config = {"configurable": {"thread_id": "approval-workflow-001"}}

# Step 1: Run until interrupt (saves checkpoint to thread_id)
app.invoke(initial_state, config=config)

# Step 2: Verify there IS a paused checkpoint
paused_state = app.get_state(config)
print(paused_state.next)  # Should show the interrupted node name

# Step 3: Resume with SAME config
app.invoke(None, config=config)
```

---

## Error 10: State Has Unexpected None Values

**Symptom**: Some state fields are `None` even though you expected them to be set.

**Cause**: TypedDict fields have no default values — if you don't set them in the initial state dict and no node writes to them before they are read, they will be `None` (or raise a `KeyError`).

**Fix**:
```python
# Always initialize ALL state fields in your invoke() call
result = app.invoke({
    "question": "my question",
    "results": [],           # empty list, not missing
    "summary": "",           # empty string, not missing
    "score": 0.0,            # zero, not missing
    "attempts": 0,
    "max_attempts": 5,
    "is_done": False,        # False, not missing
})

# Or use Optional with None explicitly
from typing import Optional
class State(TypedDict):
    results: list
    summary: Optional[str]   # Explicitly nullable
```

---

## Debugging Tips

### Print State at Every Node
```python
def debug_wrapper(node_fn, node_name):
    """Wraps any node function to log its input/output state."""
    def wrapped(state):
        print(f"\n>>> Entering {node_name}")
        print(f"    State keys: {list(state.keys())}")
        result = node_fn(state)
        print(f"    Node returned: {result}")
        return result
    return wrapped

# Wrap your nodes:
graph.add_node("my_node", debug_wrapper(my_node_fn, "my_node"))
```

### Inspect Graph Structure Before Running
```python
# Check your graph before compiling
print(graph.nodes)   # All registered nodes
print(graph.edges)   # All edges

# After compiling, draw the graph (requires graphviz)
app = graph.compile()
app.get_graph().print_ascii()
```

### Use Stream to Debug Loop Iterations
```python
# Watch every iteration of a loop
for i, chunk in enumerate(app.stream(state)):
    print(f"\nStep {i + 1}: {list(chunk.keys())}")
    for node_name, output in chunk.items():
        for field, value in output.items():
            print(f"  {node_name}.{field} = {str(value)[:50]}")
```

---

## 📂 Navigation

**In this folder:**

| File | |
|---|---|
| [📄 Project_Guide.md](./Project_Guide.md) | Project overview and spec |
| [📄 Architecture_Blueprint.md](./Architecture_Blueprint.md) | Detailed architecture |
| [📄 Step_by_Step.md](./Step_by_Step.md) | Implementation guide |
| 📄 **Troubleshooting.md** | ← you are here |

⬅️ **Prev:** [Streaming and Checkpointing](../07_Streaming_and_Checkpointing/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [LangGraph vs LangChain](../LangGraph_vs_LangChain.md)
