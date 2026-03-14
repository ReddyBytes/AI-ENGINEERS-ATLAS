# State Management — Cheatsheet

## Key Terms

| Term | One-line meaning |
|---|---|
| **State** | A TypedDict that holds all data flowing through the graph |
| **Reducer** | A function that defines how a field's update is merged into existing state |
| **Partial update** | The dict a node returns — contains only the fields it changes |
| **Overwrite** | Default merge behavior — new value replaces old value |
| **Append** | Reducer behavior using `operator.add` — new list is joined to existing list |
| **MessagesState** | Pre-built LangGraph state for chat with auto-appending messages |
| **add_messages** | LangGraph's smart reducer for message lists (appends + deduplicates) |

---

## State Definition Patterns

```python
from typing import TypedDict, Annotated
import operator
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

# Basic state
class BasicState(TypedDict):
    input: str
    output: str
    score: float

# State with accumulating list (append reducer)
class ResearchState(TypedDict):
    question: str
    results: Annotated[list, operator.add]   # appends on update
    summary: str
    attempts: int

# Chat state (use MessagesState or this pattern)
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# Or just use the built-in:
from langgraph.graph import MessagesState
graph = StateGraph(MessagesState)
```

---

## Reducer Behavior Comparison

```python
# OVERWRITE (default) — field has no Annotated reducer
state = {"count": 5}
node returns: {"count": 10}
result: {"count": 10}    # 5 is gone

# APPEND (operator.add)
state = {"items": ["a", "b"]}
node returns: {"items": ["c"]}
result: {"items": ["a", "b", "c"]}   # appended

# add_messages (smart append)
state = {"messages": [HumanMessage("hi")]}
node returns: {"messages": [AIMessage("hello")]}
result: {"messages": [HumanMessage("hi"), AIMessage("hello")]}
```

---

## Node State Update Rules

```python
# CORRECT: return a dict with only the fields you're updating
def good_node(state: MyState) -> dict:
    return {"summary": "processed text"}

# CORRECT: return empty dict if node has no state changes
def side_effect_node(state: MyState) -> dict:
    send_email(state["result"])  # do work
    return {}                    # no state update needed

# WRONG: mutate state directly
def bad_node(state: MyState) -> dict:
    state["count"] += 1   # Don't do this
    return {}

# WRONG: return None
def also_bad_node(state: MyState):
    do_work()              # forgot return statement
```

---

## Common State Patterns

### Loop counter pattern:
```python
class LoopState(TypedDict):
    data: str
    attempts: int       # increment in each loop
    max_attempts: int   # set at graph start
    satisfied: bool     # termination flag
```

### Agent with tool calls:
```python
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]  # full conversation
    tool_calls: list         # pending tool calls
    tool_results: list       # results from tool execution
```

### Document processing pipeline:
```python
class DocState(TypedDict):
    raw_text: str
    extracted_data: dict
    validation_errors: Annotated[list, operator.add]  # accumulate errors
    is_valid: bool
    retry_count: int
```

---

## MessagesState Quick Reference

```python
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_core.messages import HumanMessage, AIMessage

def chat_node(state: MessagesState) -> dict:
    # Access full history
    history = state["messages"]
    # Call LLM with full history
    response = llm.invoke(history)
    # Return new AI message — add_messages appends it
    return {"messages": [response]}

graph = StateGraph(MessagesState)
graph.add_node("chat", chat_node)
graph.add_edge(START, "chat")
graph.add_edge("chat", END)
app = graph.compile()

# Pass initial message
result = app.invoke({"messages": [HumanMessage("Hello")]})
# result["messages"] = [HumanMessage("Hello"), AIMessage("Hi there!")]
```

---

## State Design Checklist

- [ ] Does every field have a descriptive name and type?
- [ ] Do list fields that accumulate use `Annotated[list, operator.add]`?
- [ ] Are loop counters in state? (`attempts: int`)
- [ ] Are termination flags in state? (`is_done: bool`, `satisfied: bool`)
- [ ] Are all state values serializable? (no open file handles or DB connections)
- [ ] Does the initial `invoke()` call provide all required fields?

---

## 📂 Navigation

**In this folder:**

| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Working code example |

⬅️ **Prev:** [Nodes and Edges](../02_Nodes_and_Edges/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Cycles and Loops](../04_Cycles_and_Loops/Theory.md)
