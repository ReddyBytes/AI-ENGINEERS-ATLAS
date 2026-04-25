# Project 12 — LangGraph Support Bot: Build Guide

## Build Phases

| Phase | What you build | Time estimate |
|---|---|---|
| 0 | Environment setup + LangGraph mental model | 15 min |
| 1 | State definition + classifier node | 45 min |
| 2 | Routing logic + basic graph | 30 min |
| 3 | Retry loop | 30 min |
| 4 | Human-in-the-loop escalation | 45 min |
| 5 | Checkpointing + specialist nodes | 45 min |

Total: approximately 3–4 hours

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

### Step 3: Draw the graph before writing code

Before writing any code, draw this on paper:
- A box for each node (Classify, OrderLookup, Refund, General, Escalate, EscalationSend, Clarify)
- Arrows for each edge
- Mark which edges are conditional (diamond shape)
- Mark where the retry loop goes back

Theory checkpoint: `15_LangGraph/01_LangGraph_Fundamentals/Theory.md` — specifically the section on why graphs beat chains for stateful agents.

---

## Phase 1 — State Definition and Classifier Node

### Step 4: Define the TypedDict state

Your state is the single object that flows through every node.

```python
from typing import TypedDict, Annotated, Optional
from langgraph.graph.message import add_messages

class SupportState(TypedDict):
    messages: Annotated[list, add_messages]  # add_messages appends rather than overwrites
    intent: Optional[str]
    confidence: float
    retry_count: int
    order_id: Optional[str]
    draft_response: Optional[str]
    approved: bool
    final_response: Optional[str]
```

Note: `Annotated[list, add_messages]` tells LangGraph to use the append reducer — new messages are added to the list, not replacing it.

### Step 5: Build the intent classifier node

The classifier must return `intent` (one of four strings) and `confidence` (0.0–1.0).

<details><summary>💡 Hint</summary>

Prompt structure:
```
Classify this customer support message into one of:
order_lookup, refund_request, general_inquiry, escalate

Return JSON: {"intent": "...", "confidence": 0.95, "order_id": "8472" or null}

Message: {latest_message}
```

Use `json.loads()` to parse. Handle JSONDecodeError by defaulting to `general_inquiry` with confidence 0.5.

Angry or hostile language → "escalate". Order number extraction → put in "order_id" field.

</details>

<details><summary>✅ Answer</summary>

```python
def classify_intent(state: SupportState) -> dict:
    client = anthropic.Anthropic()
    user_messages = [m for m in state["messages"] if isinstance(m, HumanMessage)]
    latest = user_messages[-1].content if user_messages else ""

    system = """Classify this customer support message into exactly one of:
order_lookup, refund_request, general_inquiry, escalate

Rules:
- order_lookup: asking about order status, tracking, shipping
- refund_request: requesting a refund, return, or money back
- escalate: angry, demanding a manager, using hostile language
- general_inquiry: everything else

Return JSON only: {"intent": "...", "confidence": 0.0-1.0, "order_id": "NNNN" or null}"""

    response = client.messages.create(
        model=MODEL,
        max_tokens=100,
        system=system,
        messages=[{"role": "user", "content": latest}],
    )
    try:
        data = json.loads(response.content[0].text)
        return {
            "intent": data.get("intent", "general_inquiry"),
            "confidence": float(data.get("confidence", 0.5)),
            "order_id": data.get("order_id"),
        }
    except (json.JSONDecodeError, KeyError):
        return {"intent": "general_inquiry", "confidence": 0.5, "order_id": None}
```

</details>

### Step 6: Test the classifier in isolation

Before wiring it into a graph, call the function directly:

```python
from langchain_core.messages import HumanMessage

test_state = {"messages": [HumanMessage("Where is my order #8472?")]}
result = classify_intent(test_state)
print(result)  # {"intent": "order_lookup", "confidence": 0.94, "order_id": "8472"}
```

---

## Phase 2 — Routing Logic and Basic Graph

### Step 7: Write the routing function

```python
def route_after_classify(state: SupportState) -> str:
    """Returns node name to route to."""
    confidence = state.get("confidence", 0.0)
    retry_count = state.get("retry_count", 0)
    intent = state.get("intent", "general_inquiry")

    if confidence < CONFIDENCE_THRESHOLD and retry_count < MAX_RETRIES:
        return "clarify"
    if confidence < CONFIDENCE_THRESHOLD:
        return "general_inquiry"  # fallback after max retries
    return intent  # routes to one of the four specialist nodes
```

### Step 8: Build the minimal StateGraph

```python
from langgraph.graph import StateGraph, END

builder = StateGraph(SupportState)
builder.add_node("classify", classify_intent)
builder.add_node("clarify", clarification_node)
builder.add_node("order_lookup", order_lookup_node)
builder.add_node("refund_request", refund_node)
builder.add_node("general_inquiry", general_inquiry_node)
builder.add_node("escalate", escalation_draft_node)
builder.add_node("escalation_send", escalation_send_node)

builder.set_entry_point("classify")
builder.add_conditional_edges(
    "classify",
    route_after_classify,
    {
        "clarify": "clarify",
        "order_lookup": "order_lookup",
        "refund_request": "refund_request",
        "general_inquiry": "general_inquiry",
        "escalate": "escalate",
    }
)
```

### Step 9: Test the graph without checkpointing

```python
graph = builder.compile()
result = graph.invoke({"messages": [HumanMessage("Where is order #123?")],
                       "retry_count": 0, "confidence": 0.0, "approved": False})
print(result["final_response"])
```

---

## Phase 3 — Retry Loop

### Step 10: Build the clarification node

The clarification node increments `retry_count`, generates a clarifying question, and appends a simulated user reply (for testing).

<details><summary>💡 Hint</summary>

```python
def clarification_node(state: SupportState) -> dict:
    new_retry = state["retry_count"] + 1
    # Generate clarifying question with Claude...
    clarification = AIMessage(content="Could you tell me more — is this about an order, a refund, or something else?")
    simulated_reply = HumanMessage(content="Actually I want to check on my order #8472")
    return {
        "retry_count": new_retry,
        "messages": [clarification, simulated_reply],  # add_messages reducer appends these
    }
```

The `messages` key uses the `add_messages` reducer — returning a list here appends to the existing messages rather than replacing them.

</details>

### Step 11: Wire the retry cycle

```python
builder.add_edge("clarify", "classify")   # cycle: clarify always goes back to classify
```

LangGraph handles cycles correctly as long as you have a termination condition (the `retry_count < MAX_RETRIES` check).

Theory checkpoint: `15_LangGraph/04_Cycles_and_Loops/Theory.md`.

---

## Phase 4 — Human-in-the-Loop Escalation

### Step 12: Build the escalation draft node

This node generates a draft response but does NOT send it. Execution stops here for human review.

```python
def escalation_draft_node(state: SupportState) -> dict:
    # Generate empathetic escalation message with Claude
    # Store in draft_response — do NOT add to messages yet
    draft = "I sincerely apologize for the frustrating experience..."
    return {"draft_response": draft}
```

### Step 13: Compile with `interrupt_before`

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
graph = builder.compile(
    checkpointer=checkpointer,
    interrupt_before=["escalation_send"],  # pause BEFORE sending
)
```

### Step 14: Test the interrupt-resume cycle

```python
config = {"configurable": {"thread_id": "thread_001"}}

# First invoke — runs until interrupt
result = graph.invoke(
    {"messages": [HumanMessage("I want to speak to your manager RIGHT NOW")],
     "retry_count": 0, "confidence": 0.0, "approved": False},
    config=config,
)
print("Draft:", result["draft_response"])

# Human reviews and approves
approved = input("Approve? (y/n): ").strip() == "y"
graph.update_state(config, {"approved": approved})

# Resume — runs from interrupt point to END
final = graph.invoke(None, config=config)
print("Sent:", final["final_response"])
```

<details><summary>💡 Hint</summary>

`graph.invoke(None, config=config)` resumes from the last checkpoint. Passing `None` as the input means "use the saved state, don't add new input." The `update_state` call before this modifies the saved state with the human's approval decision.

</details>

Theory checkpoint: `15_LangGraph/05_Human_in_the_Loop/Theory.md`.

---

## Phase 5 — Checkpointing and Specialist Nodes

### Step 15: Implement order_lookup_node

1. Get `order_id` from state (or extract from message history with regex)
2. Call `lookup_order(order_id)` — mock function returning order dict
3. Format a friendly status message using the order data
4. Set `final_response` and append AIMessage to messages

### Step 16: Implement refund_node

1. Look up the order
2. Check eligibility: `order["days_ago"] <= 30` for refund eligibility
3. If eligible: format confirmation response
4. If not eligible: explain 30-day policy and suggest alternatives
5. Use Claude to write the customer-facing message — give it the eligibility result as context

### Step 17: Demonstrate conversation persistence

```python
config = {"configurable": {"thread_id": "customer_789"}}

# Turn 1
graph.invoke({"messages": [HumanMessage("Hi, I need help with my order")],
              "retry_count": 0, "confidence": 0.0, "approved": False}, config=config)

# Turn 2 (same thread_id — previous messages still in state)
graph.invoke({"messages": [HumanMessage("The order number is #5555")]}, config=config)
```

MemorySaver stores state in-memory. For production, swap to `SqliteSaver` (single-node) or `PostgresSaver` (multi-node).

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

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [01_MISSION.md](./01_MISSION.md) | Project context and motivation |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design and node reference |
| 03_GUIDE.md | you are here |
| [src/starter.py](./src/starter.py) | Runnable Python skeleton |
| [04_RECAP.md](./04_RECAP.md) | What you learned, extensions, job mapping |

⬅️ **Prev:** [11 — Advanced RAG with Reranking](../11_Advanced_RAG_with_Reranking/01_MISSION.md)
➡️ **Next:** [13 — Automated Eval Pipeline](../13_Automated_Eval_Pipeline/01_MISSION.md)
