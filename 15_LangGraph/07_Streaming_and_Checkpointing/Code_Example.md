# Streaming and Checkpointing — Code Example

## Streaming Graph Output + Persistent Checkpointing

This example demonstrates:
1. Node-level streaming with `.stream()` — see progress as each node completes
2. Conversation persistence with `MemorySaver` — agent remembers previous messages
3. State history inspection — see all saved checkpoints for a thread

```python
# streaming_checkpointing_example.py
# Run: pip install langgraph
# Then: python streaming_checkpointing_example.py

import asyncio
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage


# ─── 1. Build a Simple Conversational Graph ──────────────────────────────────
# We use MessagesState (built-in) which has:
# messages: Annotated[list[BaseMessage], add_messages]
# This automatically appends new messages rather than overwriting.

def think(state: MessagesState) -> dict:
    """
    Node 1: Analyze what the user said.
    In production: could involve intent detection, context retrieval, etc.
    """
    last_message = state["messages"][-1]
    analysis = f"Processing user message: '{last_message.content[:50]}'"
    print(f"  [think] {analysis}")

    # Return a new AI message — add_messages appends it to history
    return {"messages": [AIMessage(content=f"[Thinking: {analysis}]")]}


def respond(state: MessagesState) -> dict:
    """
    Node 2: Generate the final response.
    In production: call an LLM with the full message history.
    Here we simulate a contextual response by checking message history.
    """
    messages = state["messages"]
    human_messages = [m for m in messages if isinstance(m, HumanMessage)]

    # Count total turns for context demonstration
    turn_count = len(human_messages)

    # Simulate contextual responses based on history
    last_human = human_messages[-1].content.lower()

    if "name" in last_human and turn_count > 1:
        # Check if name was mentioned in a previous message
        first_msg = human_messages[0].content if human_messages else ""
        if "alice" in first_msg.lower():
            response_text = "Your name is Alice! I remember from our earlier conversation."
        else:
            response_text = "I don't recall a name being mentioned. Could you tell me your name?"
    elif "hello" in last_human or "hi" in last_human:
        response_text = f"Hello! This is turn {turn_count} of our conversation."
    elif "remember" in last_human:
        all_human_msgs = [m.content for m in human_messages[:-1]]
        if all_human_msgs:
            response_text = f"I remember our conversation! You said: '{all_human_msgs[0][:50]}...'"
        else:
            response_text = "This is our first message — nothing to remember yet!"
    else:
        response_text = f"Got it. That's message #{turn_count} in our conversation."

    print(f"  [respond] Response: '{response_text[:60]}'")
    return {"messages": [AIMessage(content=response_text)]}


# ─── 2. Build and Compile with Checkpointer ──────────────────────────────────

graph = StateGraph(MessagesState)
graph.add_node("think", think)
graph.add_node("respond", respond)
graph.add_edge(START, "think")
graph.add_edge("think", "respond")
graph.add_edge("respond", END)

# MemorySaver stores checkpoints in memory (use SqliteSaver for production)
memory = MemorySaver()
app = graph.compile(checkpointer=memory)


# ─── 3. Demo 1: Node-Level Streaming ─────────────────────────────────────────
print("=" * 60)
print("DEMO 1: NODE-LEVEL STREAMING with .stream()")
print("=" * 60)

config_streaming = {"configurable": {"thread_id": "streaming-demo"}}

print("\nRunning graph with .stream() — watching each node complete:\n")
for chunk in app.stream(
    {"messages": [HumanMessage("Hello, can you see this message?")]},
    config=config_streaming,
    stream_mode="updates"   # yields {node_name: state_updates}
):
    # Each chunk shows which node just completed and what it returned
    for node_name, node_output in chunk.items():
        print(f"  ✓ Node '{node_name}' completed:")
        if "messages" in node_output:
            last_msg = node_output["messages"][-1] if node_output["messages"] else None
            if last_msg:
                print(f"    → Message: '{last_msg.content[:70]}'")
        print()

print("Streaming complete!")


# ─── 4. Demo 2: Multi-Turn Conversation with Persistence ─────────────────────
print("\n" + "=" * 60)
print("DEMO 2: CONVERSATION PERSISTENCE with MemorySaver")
print("=" * 60)

# Use a unique thread_id for this conversation
config_chat = {"configurable": {"thread_id": "alice-conversation-001"}}


def chat_turn(user_message: str, turn_num: int):
    """Send one message and show the response."""
    print(f"\n--- Turn {turn_num} ---")
    print(f"User: {user_message}")

    result = app.invoke(
        {"messages": [HumanMessage(user_message)]},
        config=config_chat
    )

    # The last message in history is the AI's response
    ai_response = result["messages"][-1].content
    print(f"AI:   {ai_response}")
    print(f"(Total messages in history: {len(result['messages'])})")


# Three turns — the agent remembers across all of them
chat_turn("My name is Alice and I love LangGraph", turn_num=1)
chat_turn("Hello again!", turn_num=2)
chat_turn("Do you remember what my name is?", turn_num=3)


# ─── 5. Demo 3: Inspect Checkpoint History ───────────────────────────────────
print("\n" + "=" * 60)
print("DEMO 3: CHECKPOINT HISTORY INSPECTION")
print("=" * 60)

print(f"\nAll checkpoints saved for thread 'alice-conversation-001':")
print("(Latest first)\n")

for i, snapshot in enumerate(app.get_state_history(config_chat)):
    message_count = len(snapshot.values.get("messages", []))
    next_nodes = snapshot.next if snapshot.next else ("END",)
    print(f"  Checkpoint {i+1}:")
    print(f"    Messages in state: {message_count}")
    print(f"    Next nodes: {next_nodes}")
    if i >= 5:  # Show first 6 checkpoints
        print(f"  ... (and more)")
        break


# ─── 6. Demo 4: stream_mode="values" ─────────────────────────────────────────
print("\n" + "=" * 60)
print("DEMO 4: stream_mode='values' — Watch State Grow")
print("=" * 60)

config_values = {"configurable": {"thread_id": "values-demo"}}

print("\nWatching full state evolve after each node:\n")
for i, full_state in enumerate(app.stream(
    {"messages": [HumanMessage("Testing stream_mode values")]},
    config=config_values,
    stream_mode="values"   # yields full state after each node
)):
    message_count = len(full_state.get("messages", []))
    print(f"  State snapshot {i+1}: {message_count} messages in history")
```

---

## Expected Output

```
============================================================
DEMO 1: NODE-LEVEL STREAMING with .stream()
============================================================

Running graph with .stream() — watching each node complete:

  ✓ Node 'think' completed:
    → Message: '[Thinking: Processing user message: 'Hello, can you see this messa]'

  ✓ Node 'respond' completed:
    → Message: 'Hello! This is turn 1 of our conversation.'

Streaming complete!

============================================================
DEMO 2: CONVERSATION PERSISTENCE with MemorySaver
============================================================

--- Turn 1 ---
User: My name is Alice and I love LangGraph
  [think] Processing user message: 'My name is Alice and I love LangGraph'
  [respond] Response: 'Got it. That's message #1 in our conversatio'
AI:   Got it. That's message #1 in our conversation.
(Total messages in history: 3)

--- Turn 2 ---
User: Hello again!
  [think] Processing user message: 'Hello again!'
  [respond] Response: 'Hello! This is turn 2 of our conversation.'
AI:   Hello! This is turn 2 of our conversation.
(Total messages in history: 6)

--- Turn 3 ---
User: Do you remember what my name is?
  [think] Processing user message: 'Do you remember what my name is?'
  [respond] Response: 'Your name is Alice! I remember from our earlie'
AI:   Your name is Alice! I remember from our earlier conversation.
(Total messages in history: 9)

============================================================
DEMO 3: CHECKPOINT HISTORY INSPECTION
============================================================

All checkpoints saved for thread 'alice-conversation-001':
(Latest first)

  Checkpoint 1:
    Messages in state: 9
    Next nodes: ('END',)
  Checkpoint 2:
    Messages in state: 8
    Next nodes: ('respond',)
  ...
```

---

## Key Concepts Demonstrated

| Concept | Where in code |
|---|---|
| Node-level streaming | `app.stream(state, stream_mode="updates")` |
| Chunk structure | `{node_name: {state_updates}}` |
| MemorySaver checkpointer | `MemorySaver()` passed to `.compile()` |
| Conversation persistence | Same `thread_id` across 3 turns |
| History grows with turns | `len(result["messages"])` increases each turn |
| Checkpoint history | `app.get_state_history(config)` |
| Full state streaming | `stream_mode="values"` |
| MessagesState auto-append | `add_messages` reducer in built-in MessagesState |

---

## Upgrading to Token Streaming with a Real LLM

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", streaming=True)  # streaming=True required

async def stream_tokens():
    """Stream individual LLM tokens as they are generated."""
    print("\nStreaming tokens: ", end="", flush=True)

    async for event in app.astream_events(
        {"messages": [HumanMessage("Tell me about LangGraph in 3 sentences.")]},
        config={"configurable": {"thread_id": "token-demo"}},
        version="v2"
    ):
        if event["event"] == "on_chat_model_stream":
            token = event["data"]["chunk"].content
            if token:
                print(token, end="", flush=True)
        elif event["event"] == "on_chain_start":
            if event["name"] not in ("LangGraph", "Channel"):  # filter noise
                print(f"\n[Node: {event['name']}]", flush=True)

    print()  # newline after streaming

asyncio.run(stream_tokens())
```

---

## 📂 Navigation

**In this folder:**

| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [Multi-Agent with LangGraph](../06_Multi_Agent_with_LangGraph/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Build with LangGraph](../08_Build_with_LangGraph/Project_Guide.md)
