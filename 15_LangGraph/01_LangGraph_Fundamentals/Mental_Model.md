# LangGraph Fundamentals — Mental Model

## The Core Mental Model: Chain vs Graph

The biggest conceptual shift from LangChain to LangGraph is moving from a **linear pipeline** to a **directed graph with cycles**. Here is what that looks like visually.

---

## Linear Chain (LangChain)

A chain is like an assembly line. Work flows in one direction. Each station passes its output to the next. There is no going back, no branching, no skipping.

```
Input
  │
  ▼
┌─────────────┐
│  Step 1:    │
│  Retrieve   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Step 2:    │
│  Augment    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Step 3:    │
│  Generate   │
└──────┬──────┘
       │
       ▼
    Output
```

**Characteristics:**
- Always executes in the same order
- No branching based on content
- No loops or retries
- No shared mutable state
- Perfect for: RAG, text transformation, simple Q&A

---

## Directed Graph with Branches and Loops (LangGraph)

A graph is like a flowchart or decision tree. Work can branch based on conditions. Work can loop back. Multiple paths can lead to the same endpoint. The graph "knows where it is" at all times via the State object.

```
                   ┌──────────┐
      ┌────────────│  START   │
      │            └──────────┘
      ▼
┌─────────────┐
│  Classify   │◄──────────────────────┐
│  Intent     │                       │
└──────┬──────┘                       │
       │                              │
    [Router]                          │
   /    |    \                        │
  ▼     ▼     ▼                       │
┌───┐ ┌───┐ ┌────────┐               │
│ A │ │ B │ │  C     │               │
│ Order│ │Refund│ │Escalate│          │
└─┬─┘ └─┬─┘ └───┬────┘               │
  │     │       │                    │
  ▼     │       │                    │
┌─────┐ │       │                    │
│Check│ │       │                    │
│Sat? │─┘       │                    │
└──┬──┘         │                    │
   │            │                    │
 [No?]──────────────────────────────►┘
   │
 [Yes]
   │
   ▼
┌──────────┐
│   END    │◄─────────────────────────┘
└──────────┘       (from B and C)
```

**Characteristics:**
- Branches based on state content
- Can loop back to earlier nodes
- All nodes share the same State object
- Router functions decide the next node
- Perfect for: agents, multi-step decisions, approval workflows

---

## The State Object — The Baton in the Relay Race

Every node in a LangGraph graph receives the **same State object**. It is the single source of truth for the entire workflow.

```
State: {
  user_message: "Where is my order?"  ← set at start
  intent: ""                          ← set by "classify" node
  order_data: {}                      ← set by "fetch_order" node
  response: ""                        ← set by "respond" node
  satisfied: False                    ← set by "evaluate" node
}

Node 1 (classify):     reads user_message → writes intent
Node 2 (fetch_order):  reads intent       → writes order_data
Node 3 (respond):      reads order_data   → writes response
Node 4 (evaluate):     reads response     → writes satisfied
```

Each node only touches the fields it cares about. The rest of the state passes through unchanged.

---

## The Two Types of Edges — Fixed vs Conditional

```
UNCONDITIONAL EDGE:
  node_a ──────────────────────► node_b
  (always goes to node_b)

CONDITIONAL EDGE:
  node_a ──► [router function] ──► node_b  (if condition X)
                               └──► node_c  (if condition Y)
                               └──► END     (if condition Z)
  (router reads state and returns the target node name)
```

The router function is just a Python function that takes state as input and returns a string (the name of the next node).

---

## The Lifecycle of a LangGraph Run

```
1. .invoke(initial_state) called
        │
        ▼
2. Graph routes to first node (via START edge)
        │
        ▼
3. Node function executes
   - Receives full state
   - Does work (LLM call, DB query, etc.)
   - Returns partial state update (dict)
        │
        ▼
4. LangGraph merges partial update into full state
        │
        ▼
5. Next node determined (unconditional or conditional edge)
        │
        ├─ If next node exists → go to step 3
        │
        └─ If END → return final state to caller
```

---

## Summary Table

| Concept | Mental Model | In Code |
|---|---|---|
| StateGraph | The whole flowchart | `StateGraph(StateType)` |
| State | The shared whiteboard | `class MyState(TypedDict)` |
| Node | A worker at a station | `def my_node(state) -> dict` |
| Unconditional edge | A one-way conveyor belt | `add_edge("a", "b")` |
| Conditional edge | A railroad switch | `add_conditional_edges("a", router)` |
| Compile | Print the flowchart, check it | `app = graph.compile()` |
| Invoke | Run the flowchart | `app.invoke(initial_state)` |

---

## 📂 Navigation

**In this folder:**

| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Mental_Model.md** | ← you are here |

⬅️ **Prev:** Section intro &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Nodes and Edges](../02_Nodes_and_Edges/Theory.md)
