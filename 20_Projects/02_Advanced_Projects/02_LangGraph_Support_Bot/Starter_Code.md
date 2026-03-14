# Project 2: Starter Code

> Copy this into `support_bot.py`. All `# TODO:` blocks are yours to implement. The graph skeleton runs without errors; fill in each TODO to unlock the next stage.

```python
"""
LangGraph Customer Support Bot
Features: Intent classification, conditional routing, retry loop,
human-in-the-loop escalation, MemorySaver checkpointing.
"""

import os
import json
import re
from typing import TypedDict, Annotated, Optional, Literal
import anthropic
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL = "claude-sonnet-4-6"
CONFIDENCE_THRESHOLD = 0.70
MAX_RETRIES = 2

INTENT_LABELS = ["order_lookup", "refund_request", "general_inquiry", "escalate"]


# ─────────────────────────────────────────────
# State Definition
# ─────────────────────────────────────────────

class SupportState(TypedDict):
    """
    Shared state that flows through every node in the graph.
    The Annotated[list, add_messages] type tells LangGraph to
    append new messages rather than overwrite the list.
    """
    messages: Annotated[list, add_messages]
    intent: Optional[str]
    confidence: float
    retry_count: int
    order_id: Optional[str]
    draft_response: Optional[str]
    approved: bool
    final_response: Optional[str]


def default_state() -> dict:
    """Returns a fresh state dict for a new conversation."""
    return {
        "messages": [],
        "intent": None,
        "confidence": 0.0,
        "retry_count": 0,
        "order_id": None,
        "draft_response": None,
        "approved": False,
        "final_response": None,
    }


# ─────────────────────────────────────────────
# Mock Data Layer
# ─────────────────────────────────────────────

MOCK_ORDERS = {
    "8472": {"status": "Shipped", "eta": "Tomorrow by 8pm", "total": 127.50, "days_ago": 3},
    "5555": {"status": "Processing", "eta": "3-5 business days", "total": 54.99, "days_ago": 1},
    "1234": {"status": "Delivered", "eta": "Delivered 5 days ago", "total": 89.00, "days_ago": 35},
    "9999": {"status": "Cancelled", "eta": "N/A", "total": 210.00, "days_ago": 10},
}


def lookup_order(order_id: str) -> Optional[dict]:
    """Mock order database lookup."""
    return MOCK_ORDERS.get(order_id)


def extract_order_id(text: str) -> Optional[str]:
    """Extract order ID from message text using regex."""
    match = re.search(r'#?(\d{4,})', text)
    return match.group(1) if match else None


# ─────────────────────────────────────────────
# Node: Intent Classifier
# ─────────────────────────────────────────────

def classify_intent(state: SupportState) -> dict:
    """
    Classify the user's latest message into one of four intents.
    Returns updated state with intent, confidence, and order_id.
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # Get the latest user message
    user_messages = [m for m in state["messages"] if isinstance(m, HumanMessage)]
    latest_message = user_messages[-1].content if user_messages else ""

    # TODO: Implement intent classification
    # Steps:
    #   1. Build a system prompt that instructs Claude to classify the message
    #      into one of: order_lookup, refund_request, general_inquiry, escalate
    #   2. Ask for confidence (0.0–1.0) and any extracted order ID
    #   3. Request JSON output format:
    #      {"intent": "...", "confidence": 0.95, "order_id": "8472" or null}
    #   4. Call claude-sonnet-4-6 and parse JSON response
    #   5. Return dict with keys: intent, confidence, order_id
    #
    # Edge cases to handle:
    #   - JSON parse failure: default to general_inquiry, confidence 0.5
    #   - No order ID found: set order_id to None
    #   - Angry/hostile language: should classify as "escalate"

    # Placeholder — replace with your implementation
    print(f"[Classify] Processing: '{latest_message[:50]}...' " if len(latest_message) > 50
          else f"[Classify] Processing: '{latest_message}'")

    # TODO: Replace this placeholder with actual Claude call
    return {
        "intent": "general_inquiry",
        "confidence": 0.5,
        "order_id": extract_order_id(latest_message),
    }
    # END TODO


# ─────────────────────────────────────────────
# Node: Clarification (Retry Path)
# ─────────────────────────────────────────────

def clarification_node(state: SupportState) -> dict:
    """
    When confidence is too low, ask the user to clarify.
    Increments retry_count and adds a clarifying question to messages.
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # TODO: Implement clarification
    # Steps:
    #   1. Build a prompt that explains the classifier wasn't sure
    #      and asks a helpful clarifying question
    #   2. The question should offer options: order status, refund, general help, other
    #   3. Increment retry_count by 1
    #   4. Add the clarifying question as an AIMessage to messages
    #   5. Simulate a user follow-up (for testing, append a HumanMessage with
    #      a clarified version of the original question)
    #   Return: {"retry_count": ..., "messages": [...]}
    #
    # Note: in production, you'd pause and wait for the real user reply.
    # For this project, appending a simulated reply lets you test the loop.

    new_retry_count = state["retry_count"] + 1
    print(f"[Clarify] Attempt {new_retry_count} of {MAX_RETRIES}")

    # TODO: Replace placeholder with Claude-generated clarification
    clarification_msg = AIMessage(
        content="I'd like to help! Could you tell me more — is this about an order status, "
                "a refund, or something else?"
    )
    simulated_user_reply = HumanMessage(
        content="Actually I want to check on my order #8472"  # Simulated for testing
    )

    return {
        "retry_count": new_retry_count,
        "messages": [clarification_msg, simulated_user_reply],
    }


# ─────────────────────────────────────────────
# Node: Order Lookup Specialist
# ─────────────────────────────────────────────

def order_lookup_node(state: SupportState) -> dict:
    """
    Look up order status and return a formatted response.
    """
    # TODO: Implement order lookup
    # Steps:
    #   1. Get order_id from state (or try to extract from latest message)
    #   2. If no order_id found: ask user to provide it
    #   3. Call lookup_order(order_id)
    #   4. If order not found: apologize and offer to escalate
    #   5. If found: format a friendly status message
    #   6. Set final_response and add AIMessage to messages

    order_id = state.get("order_id")

    if not order_id:
        # Try to extract from message history
        for msg in reversed(state["messages"]):
            if isinstance(msg, HumanMessage):
                order_id = extract_order_id(msg.content)
                if order_id:
                    break

    print(f"[OrderLookup] Looking up order #{order_id}")

    # TODO: Replace placeholder with real lookup + Claude-formatted response
    if order_id:
        order = lookup_order(order_id)
        if order:
            response = (
                f"Your order #{order_id} is currently: **{order['status']}**. "
                f"Estimated delivery: {order['eta']}. "
                f"Order total: ${order['total']:.2f}."
            )
        else:
            response = (
                f"I couldn't find order #{order_id} in our system. "
                "Please double-check the order number, or I can connect you with a specialist."
            )
    else:
        response = "I'd be happy to look up your order! Could you provide your order number?"

    return {
        "final_response": response,
        "messages": [AIMessage(content=response)],
    }


# ─────────────────────────────────────────────
# Node: Refund Specialist
# ─────────────────────────────────────────────

def refund_node(state: SupportState) -> dict:
    """
    Process refund request: check eligibility, confirm or decline.
    """
    # TODO: Implement refund processing
    # Steps:
    #   1. Get order_id from state
    #   2. Look up the order
    #   3. Check eligibility: orders placed within 30 days are eligible
    #      (use order["days_ago"] from mock data)
    #   4. If eligible: "process" the refund (mock), return confirmation
    #   5. If not eligible: explain policy (30-day window), offer alternatives
    #   6. If order not found: ask for order number
    #   7. Use Claude to generate a warm, empathetic response — don't just
    #      print a mechanical message. Give Claude the eligibility result
    #      and let it write the customer-facing message.

    order_id = state.get("order_id")
    print(f"[Refund] Processing refund request for order #{order_id}")

    # TODO: Replace placeholder with eligibility check + Claude response
    response = (
        f"I've initiated a refund for order #{order_id}. "
        "You'll receive $XX.XX back to your original payment method within 3-5 business days."
    )

    return {
        "final_response": response,
        "messages": [AIMessage(content=response)],
    }


# ─────────────────────────────────────────────
# Node: General Inquiry
# ─────────────────────────────────────────────

def general_inquiry_node(state: SupportState) -> dict:
    """
    Handle FAQ-style questions using Claude directly.
    """
    # TODO: Implement general inquiry handler
    # Steps:
    #   1. Build a system prompt describing the company's support policies:
    #      - Shipping: standard 5-7 days, express 2 days
    #      - Returns: 30-day window, free for defective items
    #      - Contact: support@example.com, Mon-Fri 9am-6pm
    #   2. Pass the full conversation history (state["messages"]) to Claude
    #   3. Let Claude answer naturally from the policy context
    #   4. Set final_response and add AIMessage

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    system_prompt = """You are a helpful customer support agent for ShopBot.

Company policies:
- Shipping: Standard 5-7 days ($4.99), Express 2 days ($12.99), Free on orders over $50
- Returns: 30-day return window. Free returns for defective items. Customer pays for other returns.
- Refunds: Processed within 3-5 business days after return received
- Contact: support@shopbot.example.com, Mon-Fri 9am-6pm EST
- Hours: Chat support Mon-Sun 8am-10pm

Answer helpfully and concisely. If you don't know something, say so."""

    # TODO: Replace placeholder with actual Claude call using full message history
    response = "Thank you for your question! How can I help you today?"

    return {
        "final_response": response,
        "messages": [AIMessage(content=response)],
    }


# ─────────────────────────────────────────────
# Node: Escalation Draft (Runs before interrupt)
# ─────────────────────────────────────────────

def escalation_draft_node(state: SupportState) -> dict:
    """
    Generate a draft escalation message WITHOUT sending it.
    Execution pauses here for human review (interrupt_before).
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # TODO: Implement escalation draft generation
    # Steps:
    #   1. Build a prompt that instructs Claude to write an empathetic,
    #      de-escalating message acknowledging the customer's frustration
    #   2. Include that a human specialist will follow up within 2 hours
    #   3. Do NOT promise specific outcomes (don't say "we'll definitely fix this")
    #   4. Store the draft in state["draft_response"]
    #
    # This node runs BEFORE the interrupt. The human reviewer sees this draft
    # and decides whether to approve or modify it.

    print("[Escalation] Generating draft for human review...")

    # TODO: Replace with Claude-generated empathetic escalation message
    draft = (
        "I sincerely apologize for the frustrating experience you've had. "
        "I understand this has been unacceptable, and I want to make sure this is "
        "resolved properly. I'm escalating this to our senior support team, and a "
        "specialist will contact you within 2 hours. Thank you for your patience."
    )

    return {"draft_response": draft}


# ─────────────────────────────────────────────
# Node: Escalation Send (Runs after interrupt approval)
# ─────────────────────────────────────────────

def escalation_send_node(state: SupportState) -> dict:
    """
    Send escalation message if approved; generate alternative if not.
    """
    # TODO: Implement approval check
    # Steps:
    #   1. Check state["approved"]
    #   2. If True: use state["draft_response"] as final_response
    #   3. If False: generate an alternative response that buys time without
    #      promising immediate escalation (e.g., "Let me look into this further")
    #   4. Set final_response and add AIMessage

    if state.get("approved", False):
        response = state.get("draft_response", "I'll escalate this for you.")
        print("[Escalation] Draft approved — sending.")
    else:
        # TODO: Generate a non-escalation alternative
        response = "I understand your frustration. Let me look into this further and find the best solution for you."
        print("[Escalation] Draft rejected — sending alternative.")

    return {
        "final_response": response,
        "messages": [AIMessage(content=response)],
    }


# ─────────────────────────────────────────────
# Routing Functions (Conditional Edges)
# ─────────────────────────────────────────────

def route_after_classify(state: SupportState) -> Literal[
    "clarify", "order_lookup", "refund_request", "general_inquiry", "escalate"
]:
    """
    TODO: Implement the routing logic after classification.
    Rules:
      - If confidence < CONFIDENCE_THRESHOLD AND retry_count < MAX_RETRIES → "clarify"
      - If confidence < CONFIDENCE_THRESHOLD AND retry_count >= MAX_RETRIES → "general_inquiry"
        (give up retrying, fall back to general)
      - Otherwise route to the node matching state["intent"]

    The return value must be one of the string keys passed to add_conditional_edges().
    """
    confidence = state.get("confidence", 0.0)
    retry_count = state.get("retry_count", 0)
    intent = state.get("intent", "general_inquiry")

    if confidence < CONFIDENCE_THRESHOLD and retry_count < MAX_RETRIES:
        return "clarify"
    # TODO: add proper routing for all four intents
    return intent  # Placeholder — works if intent matches node name exactly


# ─────────────────────────────────────────────
# Graph Assembly
# ─────────────────────────────────────────────

def build_support_graph(checkpointer=None) -> StateGraph:
    """
    Assemble the full support bot StateGraph.

    TODO: Complete the graph by adding all edges.
    The skeleton adds nodes. You need to wire the edges.
    """
    builder = StateGraph(SupportState)

    # Add all nodes
    builder.add_node("classify", classify_intent)
    builder.add_node("clarify", clarification_node)
    builder.add_node("order_lookup", order_lookup_node)
    builder.add_node("refund_request", refund_node)
    builder.add_node("general_inquiry", general_inquiry_node)
    builder.add_node("escalate", escalation_draft_node)
    builder.add_node("escalation_send", escalation_send_node)

    # Entry point
    builder.set_entry_point("classify")

    # TODO: Add conditional edges from classify → all specialist nodes
    # Use add_conditional_edges("classify", route_after_classify, {...})
    # The dict maps return values of route_after_classify to node names
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

    # TODO: Retry cycle — clarify goes BACK to classify
    builder.add_edge("clarify", "classify")

    # TODO: Terminal edges — all specialist nodes go to END
    # (except escalate which goes to escalation_send)
    builder.add_edge("order_lookup", END)
    builder.add_edge("refund_request", END)
    builder.add_edge("general_inquiry", END)
    builder.add_edge("escalate", "escalation_send")
    builder.add_edge("escalation_send", END)

    # Compile with optional checkpointer and interrupt
    if checkpointer:
        return builder.compile(
            checkpointer=checkpointer,
            interrupt_before=["escalation_send"],  # Pause for human review
        )
    return builder.compile()


# ─────────────────────────────────────────────
# Demo Runner
# ─────────────────────────────────────────────

def run_demo():
    """Run the four demonstration scenarios."""

    checkpointer = MemorySaver()
    graph = build_support_graph(checkpointer=checkpointer)

    print("\n" + "="*60)
    print("SCENARIO 1: Order Lookup")
    print("="*60)
    config = {"configurable": {"thread_id": "thread_order_001"}}
    state = default_state()
    state["messages"] = [HumanMessage("Where is my order #8472?")]
    result = graph.invoke(state, config=config)
    print(f"Final response: {result.get('final_response')}")

    print("\n" + "="*60)
    print("SCENARIO 2: Refund Request")
    print("="*60)
    config = {"configurable": {"thread_id": "thread_refund_001"}}
    state = default_state()
    state["messages"] = [HumanMessage("I want a refund for order #8472 please")]
    result = graph.invoke(state, config=config)
    print(f"Final response: {result.get('final_response')}")

    print("\n" + "="*60)
    print("SCENARIO 3: Low Confidence → Retry Loop")
    print("="*60)
    config = {"configurable": {"thread_id": "thread_retry_001"}}
    state = default_state()
    state["messages"] = [HumanMessage("It's about the thing from before")]
    result = graph.invoke(state, config=config)
    print(f"Final response: {result.get('final_response')}")

    print("\n" + "="*60)
    print("SCENARIO 4: Escalation with Human-in-the-Loop")
    print("="*60)
    config = {"configurable": {"thread_id": "thread_escalate_001"}}
    state = default_state()
    state["messages"] = [HumanMessage(
        "This is absolutely unacceptable! I've been waiting 3 weeks and "
        "nobody has helped me. I want to speak to your manager immediately!"
    )]

    # First invoke — runs until interrupt before escalation_send
    result = graph.invoke(state, config=config)

    if result.get("draft_response"):
        print(f"\nDraft escalation message:\n{result['draft_response']}")
        user_input = input("\nApprove this message? (y/n): ").strip().lower()
        approved = user_input == "y"

        # Update state with approval decision
        graph.update_state(config, {"approved": approved})

        # Resume from checkpoint
        final = graph.invoke(None, config=config)
        print(f"\nFinal response: {final.get('final_response')}")
    else:
        print(f"Final response: {result.get('final_response')}")


def run_multi_turn_demo():
    """
    TODO: Demonstrate multi-turn conversation using checkpointing.

    Steps:
      1. Create a thread_id for a customer session
      2. Send message 1: "Hi, I need help"
      3. Send message 2 (same thread_id): "It's about order #5555"
      4. Send message 3 (same thread_id): "I want a refund for it"
      5. Show that message history accumulates correctly across turns

    Key insight: The same thread_id means the graph resumes from its
    last state rather than starting fresh.
    """
    checkpointer = MemorySaver()
    graph = build_support_graph(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": "customer_multi_turn"}}

    # TODO: Implement multi-turn conversation
    print("\n[Multi-turn demo not yet implemented — complete the TODO above]")


if __name__ == "__main__":
    run_demo()
    # run_multi_turn_demo()  # Uncomment after implementing
```
