# Nodes and Edges — Cheatsheet

## Key Terms

| Term | One-line meaning |
|---|---|
| **Node** | A Python function: `def fn(state) -> dict` |
| **Edge** | A fixed connection between two nodes |
| **Conditional Edge** | A connection where a router function picks the next node |
| **Router function** | A Python function that takes state and returns a node name string |
| **START** | Sentinel import marking the graph entry point |
| **END** | Sentinel import marking a terminal state |

---

## Node Pattern

```python
def my_node(state: MyState) -> dict:
    # Read from state
    value = state["some_field"]
    # Do work
    result = process(value)
    # Return ONLY the fields you're updating
    return {"output_field": result}

# Register with graph
graph.add_node("my_node", my_node)
```

---

## Edge Patterns

```python
# Unconditional edge — always goes A → B
graph.add_edge("node_a", "node_b")

# START and END edges
graph.add_edge(START, "first_node")   # required — sets entry point
graph.add_edge("last_node", END)      # terminates graph

# Conditional edge — router decides destination
def router(state: MyState) -> str:
    if state["condition"]:
        return "node_x"
    return "node_y"

graph.add_conditional_edges("decision_node", router)
```

---

## Router Function Rules

| Rule | Detail |
|---|---|
| Input | Full state object |
| Output | String (node name) or `END` constant |
| Must not return `None` | Every code path must return a value |
| Node names must exist | Typos cause runtime errors — add nodes first |
| Can return `END` | Terminates the graph cleanly |

```python
from langgraph.graph import END

def safe_router(state: MyState) -> str:
    if state["attempts"] > 3:
        return END            # terminate after max retries
    if state["done"]:
        return "finalize"
    return "try_again"
```

---

## Build Order (Always Follow This Sequence)

```
1. Define StateGraph with state type
   graph = StateGraph(MyState)

2. Add all nodes first
   graph.add_node("a", fn_a)
   graph.add_node("b", fn_b)

3. Add edges (nodes must exist first)
   graph.add_edge(START, "a")
   graph.add_edge("a", "b")
   graph.add_edge("b", END)

4. Compile
   app = graph.compile()

5. Run
   result = app.invoke(initial_state)
```

---

## Common Edge Patterns

| Pattern | Code |
|---|---|
| Linear: A → B → END | `add_edge("a","b")`, `add_edge("b", END)` |
| Branch: A → B or C | `add_conditional_edges("a", router)` |
| Loop: A → B → A | `add_edge("b", "a")` (creates cycle) |
| Loop with exit: A → B → A or END | `add_conditional_edges("b", router)` |
| Parallel join (via state) | Both nodes write to state; merge node reads combined result |

---

## Quick Debugging Checklist

- [ ] Did you `add_node()` before `add_edge()`?
- [ ] Did you `add_edge(START, "first_node")`?
- [ ] Does every terminal path have `add_edge("x", END)`?
- [ ] Does your router function return a value on every code path?
- [ ] Are all node names in router functions spelled correctly?
- [ ] Does every node return a dict (not `None`)?

---

## 📂 Navigation

**In this folder:**

| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Working code example |

⬅️ **Prev:** [LangGraph Fundamentals](../01_LangGraph_Fundamentals/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [State Management](../03_State_Management/Theory.md)
