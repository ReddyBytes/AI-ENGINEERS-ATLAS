# LangGraph Fundamentals — Cheatsheet

## Key Terms

| Term | One-line meaning |
|---|---|
| **StateGraph** | The container object you add nodes and edges to |
| **State** | A TypedDict that holds all data flowing through the graph |
| **Node** | A Python function that reads state and returns a partial update |
| **Edge** | A connection between two nodes (unconditional) |
| **Conditional Edge** | A connection where a router function decides the next node |
| **START** | The special node representing the entry point of the graph |
| **END** | The special node representing a terminal state |
| **Compile** | Validates the graph and returns a runnable `CompiledGraph` |
| **Checkpointer** | A storage backend that saves state after every node execution |
| **Reducer** | A function that defines how a state field gets merged on update |

---

## LangGraph vs LangChain — Quick Comparison

| Feature | LangChain | LangGraph |
|---|---|---|
| Workflow shape | Linear chain | Directed graph (with cycles) |
| Branching | Limited (`RunnableBranch`) | First-class conditional edges |
| Loops | Not supported natively | Core feature |
| State | Passed explicitly or via memory | Typed, shared, auto-managed |
| Human-in-the-loop | Not supported | Built-in interrupt/resume |
| Streaming | Yes | Yes (per node) |
| Best for | RAG, simple chains | Agents, multi-step loops |
| Complexity | Low | Medium |

---

## Minimal Graph Pattern

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

class State(TypedDict):
    value: str

def my_node(state: State) -> dict:
    return {"value": state["value"] + " processed"}

graph = StateGraph(State)
graph.add_node("my_node", my_node)
graph.add_edge(START, "my_node")
graph.add_edge("my_node", END)
app = graph.compile()
result = app.invoke({"value": "hello"})
```

---

## Conditional Edge Pattern

```python
def router(state: State) -> str:
    if state["value"] == "a":
        return "node_a"
    return "node_b"

graph.add_conditional_edges("decision_node", router)
# router returns the NAME of the next node as a string
```

---

## When to Use LangGraph vs Other Options

| Use LangGraph when... | Use LangChain when... | Use plain API when... |
|---|---|---|
| You need loops or retries | You have a linear pipeline | No orchestration needed |
| You need branching logic | Building a RAG pipeline | Simple one-shot calls |
| You need human approval steps | Chaining prompts together | Prototyping quickly |
| Multiple agents coordinate | Tool use without loops | Cost-sensitive applications |
| You need to save and resume state | LCEL is sufficient | |

---

## Core API Reference

```python
# Build
graph = StateGraph(StateType)
graph.add_node("name", function)
graph.add_edge("from", "to")
graph.add_edge(START, "first_node")
graph.add_edge("last_node", END)
graph.add_conditional_edges("node", router_fn)

# Compile
app = graph.compile()
app = graph.compile(checkpointer=MemorySaver())  # with persistence

# Run
result = app.invoke(initial_state)
for chunk in app.stream(initial_state):
    print(chunk)
```

---

## 📂 Navigation

**In this folder:**

| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Mental_Model.md](./Mental_Model.md) | Visual mental model |

⬅️ **Prev:** Section intro &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Nodes and Edges](../02_Nodes_and_Edges/Theory.md)
