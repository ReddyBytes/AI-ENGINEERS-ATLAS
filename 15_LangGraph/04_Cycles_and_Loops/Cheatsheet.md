# Cycles and Loops — Cheatsheet

## Key Concepts

| Concept | One-line meaning |
|---|---|
| **Cycle** | An edge that points backward — from a later node to an earlier one |
| **Loop termination** | The router function returning `END` or a terminal node name |
| **recursion_limit** | Max total node executions before `GraphRecursionError` is raised |
| **GraphRecursionError** | Error raised when recursion_limit is exceeded |
| **Attempt counter** | A state field (`attempts: int`) that increments each loop iteration |
| **ReAct loop** | LLM → tool call → LLM (continues until LLM gives a final answer) |

---

## Minimal Loop Pattern

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

class LoopState(TypedDict):
    value: int
    attempts: int
    max_attempts: int

def work_node(state: LoopState) -> dict:
    new_value = do_work(state["value"])
    return {
        "value": new_value,
        "attempts": state["attempts"] + 1   # Always increment counter
    }

def router(state: LoopState) -> str:
    # Check hard limit first
    if state["attempts"] >= state["max_attempts"]:
        return END
    # Check success condition
    if is_good_enough(state["value"]):
        return END
    # Otherwise loop
    return "work_node"

graph = StateGraph(LoopState)
graph.add_node("work_node", work_node)
graph.add_edge(START, "work_node")
graph.add_conditional_edges("work_node", router)
app = graph.compile()
```

---

## ReAct Agent Loop Pattern

```python
def call_llm(state) -> dict:
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

def run_tools(state) -> dict:
    results = execute_tool_calls(state["messages"][-1].tool_calls)
    return {"messages": results}

def should_continue(state) -> str:
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "run_tools"   # LLM wants more tool calls
    return END               # LLM gave final answer

graph.add_edge(START, "call_llm")
graph.add_conditional_edges("call_llm", should_continue)
graph.add_edge("run_tools", "call_llm")  # Loop back after tool execution
```

---

## recursion_limit Usage

```python
# Setting the limit
result = app.invoke(state, config={"recursion_limit": 50})

# Catching the error
from langgraph.errors import GraphRecursionError
try:
    result = app.invoke(state, config={"recursion_limit": 10})
except GraphRecursionError as e:
    print(f"Loop exceeded limit: {e}")

# Calculating the right limit:
# recursion_limit = nodes_per_loop * expected_max_loops * 1.2
# Example: 2 nodes per loop, max 10 loops → limit = 24
```

---

## Loop Termination Checklist

Every loop MUST have:
- [ ] A counter in state that increments each iteration (`attempts += 1`)
- [ ] A max iterations check in the router (`if attempts >= max: return END`)
- [ ] A success condition in the router (`if score >= threshold: return END`)
- [ ] A default route that loops back (`return "work_node"`)
- [ ] An appropriate `recursion_limit` as a backstop

---

## Common Loop Termination Patterns

```python
# Pattern 1: Quality threshold with max iterations
def router(state):
    if state["attempts"] >= 5: return END
    if state["score"] >= 0.9: return "finalize"
    return "improve"

# Pattern 2: Boolean flag
def router(state):
    if state["is_done"]: return END
    return "continue"

# Pattern 3: Stalled progress detection
def router(state):
    if state["attempts"] >= 3: return END
    scores = state["recent_scores"]
    if len(scores) >= 3 and max(scores) - min(scores) < 0.01:
        return END   # No improvement — give up
    return "iterate"

# Pattern 4: LLM decides (ReAct)
def router(state):
    last = state["messages"][-1]
    if last.tool_calls: return "tools"
    return END   # LLM finished
```

---

## 📂 Navigation

**In this folder:**

| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Working code example |

⬅️ **Prev:** [State Management](../03_State_Management/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Human-in-the-Loop](../05_Human_in_the_Loop/Theory.md)
