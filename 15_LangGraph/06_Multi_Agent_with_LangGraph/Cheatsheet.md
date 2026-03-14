# Multi-Agent with LangGraph — Cheatsheet

## Key Terms

| Term | One-line meaning |
|---|---|
| **Multi-agent system** | Multiple AI agents coordinating to complete complex tasks |
| **Supervisor** | An orchestrator agent that decides which specialist to call next |
| **Specialist / Sub-agent** | A focused agent with its own tools, prompt, and expertise area |
| **Handoff** | When one agent passes control to another (via state + router) |
| **Subgraph** | A compiled LangGraph used as a node inside another graph |
| **Send API** | LangGraph mechanism for dispatching agents in parallel |

---

## Supervisor Pattern — Template

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class TeamState(TypedDict):
    task: str
    next_agent: str
    research_notes: str
    draft: str
    is_complete: bool
    messages: Annotated[list, add_messages]

# Supervisor decides who works next
def supervisor(state: TeamState) -> dict:
    if not state["research_notes"]:
        return {"next_agent": "researcher"}
    elif not state["draft"]:
        return {"next_agent": "writer"}
    else:
        return {"next_agent": "FINISH", "is_complete": True}

# Router reads supervisor's decision
def supervisor_router(state: TeamState) -> str:
    if state["next_agent"] == "FINISH":
        return END
    return state["next_agent"]  # name of the next agent node

# Specialist nodes
def researcher(state: TeamState) -> dict:
    notes = do_research(state["task"])
    return {"research_notes": notes}

def writer(state: TeamState) -> dict:
    draft = write_draft(state["task"], state["research_notes"])
    return {"draft": draft}

# Build graph
graph = StateGraph(TeamState)
graph.add_node("supervisor", supervisor)
graph.add_node("researcher", researcher)
graph.add_node("writer", writer)

graph.add_edge(START, "supervisor")
graph.add_conditional_edges("supervisor", supervisor_router)
graph.add_edge("researcher", "supervisor")  # always report back
graph.add_edge("writer", "supervisor")      # always report back
```

---

## Subgraph Pattern

```python
# Build specialist as its own graph
specialist_graph = StateGraph(SpecialistState)
specialist_graph.add_node("step1", step1_fn)
specialist_graph.add_edge(START, "step1")
specialist_graph.add_edge("step1", END)
specialist_app = specialist_graph.compile()

# Wrap compiled subgraph as a node in parent graph
def specialist_node(state: ParentState) -> dict:
    result = specialist_app.invoke({"query": state["task"]})
    return {"specialist_output": result["output"]}

parent_graph.add_node("specialist", specialist_node)
```

---

## Parallel Execution with Send

```python
from langgraph.types import Send

def dispatch_parallel(state: TeamState) -> list[Send]:
    return [
        Send("researcher", {"task": state["task"]}),
        Send("analyst", {"task": state["task"]}),
    ]

# Each agent runs simultaneously
# Results merged via reducers when both complete
```

---

## Communication Patterns

| Pattern | State Usage |
|---|---|
| Sequential delegation | `next_agent` field set by supervisor, read by router |
| Results accumulation | `Annotated[list, operator.add]` field for collected outputs |
| Parallel merge | Reducer combines parallel agent outputs |
| Conversation history | `messages: Annotated[list, add_messages]` |

---

## Agent Design Checklist

- [ ] Each agent has a single, focused responsibility
- [ ] Each agent only writes to its own state fields
- [ ] Supervisor has a clear termination condition
- [ ] State TypedDict has fields for each agent's output
- [ ] All agents route back to supervisor (not to END directly)
- [ ] Tested with 2 agents before scaling to more

---

## 📂 Navigation

**In this folder:**

| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | Full architecture diagrams |
| [📄 Code_Example.md](./Code_Example.md) | Working code example |

⬅️ **Prev:** [Human-in-the-Loop](../05_Human_in_the_Loop/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Streaming and Checkpointing](../07_Streaming_and_Checkpointing/Theory.md)
