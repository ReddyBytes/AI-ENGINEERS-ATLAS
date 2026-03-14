# Streaming and Checkpointing — Cheatsheet

## Key Terms

| Term | One-line meaning |
|---|---|
| **`.invoke()`** | Run graph synchronously, return final state only |
| **`.stream()`** | Run graph, yield output after each node completes |
| **`.astream_events()`** | Async generator yielding all events including LLM tokens |
| **stream_mode** | Controls what `.stream()` yields — `"updates"`, `"values"`, `"messages"` |
| **Checkpointer** | Storage backend that saves state after every node execution |
| **MemorySaver** | In-memory checkpointer — lost on process restart |
| **SqliteSaver** | File-based checkpointer — persists to SQLite database |
| **thread_id** | Unique key for one workflow run; used to load conversation history |

---

## invoke() vs stream() vs astream_events()

| Method | Output | Use When |
|---|---|---|
| `.invoke()` | Final state (dict) | Background jobs, batch processing |
| `.stream()` | Chunks as nodes complete | Progress UI, debugging |
| `.astream_events()` | All events + LLM tokens (async) | Chat interfaces, real-time apps |

---

## .stream() Patterns

```python
# stream_mode="updates" (default) — node name + what it changed
for chunk in app.stream(state):
    node_name = list(chunk.keys())[0]
    node_output = chunk[node_name]
    print(f"Node '{node_name}' completed: {node_output}")

# stream_mode="values" — full state after each node
for full_state in app.stream(state, stream_mode="values"):
    print(f"Messages so far: {len(full_state['messages'])}")

# stream_mode="messages" — for chat apps
for message_chunk, metadata in app.stream(
    state,
    stream_mode="messages",
    config=config
):
    print(message_chunk.content, end="", flush=True)
```

---

## Token Streaming (async)

```python
from langchain_openai import ChatOpenAI

# LLM MUST have streaming=True for token events
llm = ChatOpenAI(model="gpt-4o-mini", streaming=True)

async def stream_with_tokens(initial_state):
    async for event in app.astream_events(initial_state, version="v2"):
        if event["event"] == "on_chat_model_stream":
            content = event["data"]["chunk"].content
            if content:
                print(content, end="", flush=True)

import asyncio
asyncio.run(stream_with_tokens(initial_state))
```

---

## Checkpointing Setup

```python
# MemorySaver (dev/testing)
from langgraph.checkpoint.memory import MemorySaver
memory = MemorySaver()
app = graph.compile(checkpointer=memory)

# SqliteSaver (simple production)
from langgraph.checkpoint.sqlite import SqliteSaver
with SqliteSaver.from_conn_string("checkpoints.db") as cp:
    app = graph.compile(checkpointer=cp)
    result = app.invoke(state, config={"configurable": {"thread_id": "run-001"}})
```

---

## Conversation Persistence Pattern

```python
from langgraph.graph import MessagesState
from langchain_core.messages import HumanMessage

# Always use the same thread_id for the same conversation
config = {"configurable": {"thread_id": "user-alice-session-1"}}

# Turn 1
app.invoke({"messages": [HumanMessage("My name is Alice")]}, config=config)

# Turn 2 — full history from Turn 1 is automatically loaded
result = app.invoke({"messages": [HumanMessage("What's my name?")]}, config=config)
# AI sees both messages and responds: "Your name is Alice"
```

---

## Inspect Checkpoint State

```python
# Get current state for a thread
state = app.get_state(config)
print(state.values)       # Current state dict
print(state.next)         # Next nodes to run

# Get full history of all checkpoints
for snapshot in app.get_state_history(config):
    print(snapshot.created_at, snapshot.values)
```

---

## When to Use Each

| Scenario | Recommendation |
|---|---|
| Background batch job | `.invoke()` |
| User-facing chat | `.astream_events()` with token streaming |
| Progress UI / agent dashboard | `.stream(stream_mode="updates")` |
| Conversation memory | MemorySaver (dev) or SqliteSaver (prod) with thread_id |
| Human-in-the-loop approval | Checkpointer (any) + interrupt config |
| Multi-user production app | SqliteSaver or PostgresSaver (shared) |

---

## 📂 Navigation

**In this folder:**

| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Working code example |

⬅️ **Prev:** [Multi-Agent with LangGraph](../06_Multi_Agent_with_LangGraph/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Build with LangGraph](../08_Build_with_LangGraph/Project_Guide.md)
