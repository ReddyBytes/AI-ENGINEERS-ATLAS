# Project 2: Step-by-Step Build Guide

## Overview

Build the LangGraph support bot in five phases. Each phase produces a runnable graph you can test before moving on.

---

## Phase 0 — Environment Setup

### Step 1: Install dependencies

```bash
pip install langgraph langchain-anthropic langchain-core anthropic
```

### Step 2: Verify LangGraph version

```bash
python -c "import langgraph; print(langgraph.__version__)"
# Should be 0.2.x or higher for interrupt_before support
```

### Step 3: Set your API key

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Step 4: Confirm LangGraph mental model

Before writing any code, draw this on paper:
- A box for each node (ClassifyIntent, OrderLookup, Refund, General, Escalate, Clarify)
- Arrows for each edge
- Mark which edges are conditional (diamond shape)
- Mark where the retry loop goes back

**Theory checkpoint:** Read `15_LangGraph/01_LangGraph_Fundamentals/Mental_Model.md` — specifically the section on why graphs beat chains for stateful agents.

---

## Phase 1 — Define State and Build the Classifier Node

### Step 5: Define the TypedDict state

Your state is the single object that flows through every node. Think carefully about what every node needs to read and write:

```python
from typing import TypedDict, Annotated, Optional
from langgraph.graph.message import add_messages

class SupportState(TypedDict):
    messages: Annotated[list, add_messages]  # Conversation history
    intent: Optional[str]                    # Classified intent
    confidence: float                        # Classification confidence
    retry_count: int                         # How many times we've retried
    order_id: Optional[str]                  # Extracted order ID if present
    draft_response: Optional[str]            # Pending message for human review
    approved: bool                           # Human approved the escalation
    final_response: Optional[str]            # The message sent to user
```

Note the `Annotated[list, add_messages]` on `messages` — this uses LangGraph's built-in message reducer that appends rather than overwrites.

### Step 6: Build the intent classifier node

The classifier must return:
- `intent`: one of `["order_lookup", "refund_request", "general_inquiry", "escalate"]`
- `confidence`: 0.0–1.0

Write a prompt that asks Claude to classify the latest user message and return JSON:
```json
{"intent": "refund_request", "confidence": 0.92, "order_id": "8472"}
```

Use `json.loads()` to parse the response.

### Step 7: Test the classifier in isolation

Before wiring it into a graph, call the classifier function directly with several inputs:
- "I want to return my order"
- "Where is my package?"
- "I hate your company"
- "Can I change my shipping address?"

Confirm it returns sensible intents and reasonable confidence scores.

**Theory checkpoint:** Read `15_LangGraph/02_Nodes_and_Edges/Theory.md`.

---

## Phase 2 — Build the Routing Logic and Basic Graph

### Step 8: Write the routing function

```python
def route_by_intent(state: SupportState) -> str:
    if state["confidence"] < 0.7 and state["retry_count"] < 2:
        return "clarify"
    if state["intent"] == "order_lookup":
        return "order_lookup"
    # TODO: add other routes
```

This function is passed to `add_conditional_edges()`. It takes state and returns a string matching a node name.

### Step 9: Build the minimal StateGraph

```python
from langgraph.graph import StateGraph, END

builder = StateGraph(SupportState)
builder.add_node("classify", classify_intent)
builder.add_node("clarify", clarification_node)
builder.add_node("order_lookup", order_lookup_node)
# Add other nodes...

builder.set_entry_point("classify")
builder.add_conditional_edges("classify", route_by_intent, {
    "clarify": "clarify",
    "order_lookup": "order_lookup",
    # ...
})
```

### Step 10: Test the graph without checkpointing

```python
graph = builder.compile()
result = graph.invoke({"messages": [HumanMessage("Where is order #123?")]})
print(result["final_response"])
```

Confirm routing works for each intent.

**Theory checkpoint:** Read `15_LangGraph/02_Nodes_and_Edges/Code_Example.md`.

---

## Phase 3 — Implement the Retry Loop

### Step 11: Build the clarification node

The clarification node should:
1. Increment `retry_count` in state
2. Generate a clarifying question using Claude ("Could you tell me more about your issue?")
3. Route back to user — in a real system, this waits for a user reply

For this project, simulate a follow-up message by appending both the bot clarification and a "simulated user reply" to `messages`.

### Step 12: Wire the retry cycle

The key insight: after clarification, the graph routes **back to `classify`**, not forward. This is a cycle.

```python
builder.add_edge("clarify", "classify")
```

LangGraph handles cycles correctly as long as you have a termination condition (the `retry_count < 2` check in your router).

### Step 13: Test the retry path

```python
result = graph.invoke({
    "messages": [HumanMessage("It's about the thing")],
    "retry_count": 0,
})
```

Watch the graph cycle: classify → clarify → classify → (second classification attempt).

**Theory checkpoint:** Read `15_LangGraph/04_Cycles_and_Loops/Theory.md`. This explains how LangGraph tracks visited nodes and prevents infinite loops.

---

## Phase 4 — Add Human-in-the-Loop for Escalation

### Step 14: Build the escalation draft node

This node does NOT send the message — it only prepares it:
1. Generate a draft escalation response using Claude
2. Store it in `state["draft_response"]`
3. Return updated state

```python
def escalation_draft_node(state: SupportState) -> dict:
    # Generate empathetic escalation message
    draft = generate_escalation_draft(state["messages"])
    return {"draft_response": draft}
```

### Step 15: Compile with `interrupt_before`

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
graph = builder.compile(
    checkpointer=checkpointer,
    interrupt_before=["escalation_send"],  # Pause BEFORE sending
)
```

### Step 16: Test the interrupt-resume cycle

```python
config = {"configurable": {"thread_id": "thread_001"}}

# First invoke — runs until interrupt
result = graph.invoke(
    {"messages": [HumanMessage("I want to speak to your manager RIGHT NOW")]},
    config=config,
)
print("Draft:", result["draft_response"])

# Simulate human approval
approved = input("Approve? (y/n): ").strip() == "y"

# Update state with approval decision
graph.update_state(config, {"approved": approved})

# Resume — runs from interrupt point to END
final = graph.invoke(None, config=config)
print("Sent:", final["final_response"])
```

### Step 17: Build the escalation_send node

This node checks `state["approved"]`:
- If True: set `final_response = draft_response`, route to END
- If False: generate an alternative response explaining escalation is being reviewed

**Theory checkpoint:** Read `15_LangGraph/05_Human_in_the_Loop/Theory.md` and `Code_Example.md`.

---

## Phase 5 — Checkpointing and Multi-Turn Conversations

### Step 18: Demonstrate conversation persistence

Show that conversations survive "timeouts" (program restart):

```python
# Conversation 1
config = {"configurable": {"thread_id": "customer_789"}}
graph.invoke({"messages": [HumanMessage("Hi, I need help with my order")]}, config=config)

# ... program "restarts" (in reality, just a new invoke call)

# Conversation resumes — previous messages still in state
graph.invoke({"messages": [HumanMessage("The order number is #5555")]}, config=config)
```

MemorySaver stores state in-memory. For production, swap to `SqliteSaver` or a database-backed checkpointer.

### Step 19: Add the order_lookup specialist node

This node should:
1. Extract the order ID from `state["order_id"]` or parse it from messages
2. Call a mock `lookup_order(order_id)` function (returns fake JSON data)
3. Format a response: "Your order #8472 is currently: Shipped — arriving tomorrow"
4. Set `state["final_response"]` and route to END

### Step 20: Add the refund specialist node

Similar to order_lookup, but:
1. Check eligibility (mock: orders < 30 days are eligible)
2. If eligible: process refund (mock), set confirmation response
3. If ineligible: explain policy, suggest alternatives

**Theory checkpoint:** Read `15_LangGraph/06_Multi_Agent_with_LangGraph/Theory.md` — the escalation node is a minimal "handoff to human agent" pattern.

---

## Testing Checklist

- [ ] Graph compiles without errors
- [ ] All four intents route to correct specialist nodes
- [ ] Low-confidence inputs trigger clarification loop
- [ ] Retry count prevents infinite loops (max 2 retries)
- [ ] Escalation path pauses at interrupt and waits for approval
- [ ] Approval=True sends the draft; Approval=False generates alternative
- [ ] Multiple turns with same `thread_id` accumulate message history
- [ ] Order lookup returns data from mock function
- [ ] Refund node checks eligibility before processing
