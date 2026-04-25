"""
LangGraph Customer Support Bot — Project 12
==============================================
Features: Intent classification, conditional routing, retry loop,
human-in-the-loop escalation, MemorySaver checkpointing.

Usage:
    python starter.py

Setup:
    pip install langgraph langchain-anthropic langchain-core anthropic
    Set ANTHROPIC_API_KEY in environment or .env file.
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

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL = "claude-sonnet-4-6"
CONFIDENCE_THRESHOLD = 0.70   # below this, ask for clarification  # ←
MAX_RETRIES = 2               # max clarification attempts before falling back to general  # ←

INTENT_LABELS = ["order_lookup", "refund_request", "general_inquiry", "escalate"]


# ---------------------------------------------------------------------------
# State Definition
# ---------------------------------------------------------------------------

class SupportState(TypedDict):
    """
    Shared state flowing through every node.
    Annotated[list, add_messages] appends new messages rather than overwriting.
    """
    messages: Annotated[list, add_messages]  # ← add_messages is the key reducer
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


# ---------------------------------------------------------------------------
# Mock Data Layer
# ---------------------------------------------------------------------------

MOCK_ORDERS = {
    "8472": {"status": "Shipped",    "eta": "Tomorrow by 8pm",       "total": 127.50, "days_ago": 3},
    "5555": {"status": "Processing", "eta": "3-5 business days",      "total": 54.99,  "days_ago": 1},
    "1234": {"status": "Delivered",  "eta": "Delivered 5 days ago",   "total": 89.00,  "days_ago": 35},
    "9999": {"status": "Cancelled",  "eta": "N/A",                   "total": 210.00, "days_ago": 10},
}


def lookup_order(order_id: str) -> Optional[dict]:
    """Mock order database lookup."""
    return MOCK_ORDERS.get(order_id)


def extract_order_id(text: str) -> Optional[str]:
    """Extract order ID (4+ digit number) from message text."""
    match = re.search(r'#?(\d{4,})', text)
    return match.group(1) if match else None


# ---------------------------------------------------------------------------
# Node: Intent Classifier
# ---------------------------------------------------------------------------

def classify_intent(state: SupportState) -> dict:
    """
    Classify the user's latest message into one of four intents.
    Returns: intent, confidence, order_id
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    user_messages = [m for m in state["messages"] if isinstance(m, HumanMessage)]
    latest_message = user_messages[-1].content if user_messages else ""

    print(f"[Classify] Processing: '{latest_message[:60]}'")

    # TODO: Implement intent classification.
    #   1. Build a system prompt that instructs Claude to classify the message
    #      into one of: order_lookup, refund_request, general_inquiry, escalate
    #   2. Ask for confidence (0.0–1.0) and any extracted order ID
    #   3. Request JSON output: {"intent": "...", "confidence": 0.95, "order_id": "8472" or null}
    #   4. Call claude-sonnet-4-6 with max_tokens=100 (short JSON response)
    #   5. json.loads() the response
    #   6. Handle JSONDecodeError: default to general_inquiry, confidence=0.5
    #   7. Angry/hostile language -> "escalate"
    #
    # Placeholder — replace with actual Claude call:
    return {
        "intent": "general_inquiry",
        "confidence": 0.5,
        "order_id": extract_order_id(latest_message),
    }  # ← replace with real implementation


# ---------------------------------------------------------------------------
# Node: Clarification (Retry Path)
# ---------------------------------------------------------------------------

def clarification_node(state: SupportState) -> dict:
    """
    When confidence is too low, ask the user to clarify.
    Increments retry_count and appends a clarifying question + simulated reply.
    """
    new_retry_count = state["retry_count"] + 1
    print(f"[Clarify] Attempt {new_retry_count} of {MAX_RETRIES}")

    # TODO: Use Claude to generate a natural clarifying question.
    #   The question should offer options: order status / refund / general help / other.
    #   After generating, append it as AIMessage.
    #   Also append a simulated HumanMessage with a clarified version (for testing).
    #
    # Note: returning "messages": [msg1, msg2] here APPENDS to state["messages"]
    # because of the add_messages reducer — it does NOT replace the list.

    clarification_msg = AIMessage(
        content="I'd like to help! Could you tell me more — is this about an order status, "
                "a refund, or something else entirely?"
    )
    simulated_user_reply = HumanMessage(
        content="Actually I want to check on my order #8472"  # simulated for testing
    )

    return {
        "retry_count": new_retry_count,
        "messages": [clarification_msg, simulated_user_reply],
    }


# ---------------------------------------------------------------------------
# Node: Order Lookup Specialist
# ---------------------------------------------------------------------------

def order_lookup_node(state: SupportState) -> dict:
    """Look up order status and return a formatted response."""
    order_id = state.get("order_id")

    if not order_id:
        for msg in reversed(state["messages"]):
            if isinstance(msg, HumanMessage):
                order_id = extract_order_id(msg.content)
                if order_id:
                    break

    print(f"[OrderLookup] Looking up order #{order_id}")

    # TODO: Implement order lookup.
    #   1. Call lookup_order(order_id) to get order dict from MOCK_ORDERS
    #   2. If order not found: apologize and offer to escalate
    #   3. If found: format a clear status message with status, eta, total
    #   4. Optionally: use Claude to write the customer-facing response
    #      (give it the order data as context for a warmer, more natural reply)
    #   5. Set final_response and append AIMessage to messages

    if order_id:
        order = lookup_order(order_id)
        if order:
            response = (
                f"Your order #{order_id} is currently: {order['status']}. "
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


# ---------------------------------------------------------------------------
# Node: Refund Specialist
# ---------------------------------------------------------------------------

def refund_node(state: SupportState) -> dict:
    """Process refund request: check eligibility, confirm or decline."""
    order_id = state.get("order_id")
    print(f"[Refund] Processing refund request for order #{order_id}")

    # TODO: Implement refund processing.
    #   1. Look up the order using lookup_order(order_id)
    #   2. Eligibility rule: order["days_ago"] <= 30
    #   3. If eligible: "process" the refund (mock), write confirmation
    #   4. If not eligible: explain the 30-day window policy, suggest alternatives
    #   5. If order not found: ask for order number
    #   6. Use Claude to generate the customer-facing message — pass eligibility
    #      result and order data as context for a warm, empathetic response

    # Placeholder:
    response = (
        f"I've initiated a refund for order #{order_id}. "
        "You'll receive the refund to your original payment method within 3-5 business days."
    )

    return {
        "final_response": response,
        "messages": [AIMessage(content=response)],
    }  # ← replace placeholder with real eligibility check


# ---------------------------------------------------------------------------
# Node: General Inquiry
# ---------------------------------------------------------------------------

def general_inquiry_node(state: SupportState) -> dict:
    """Handle FAQ-style questions using Claude with company policy context."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    system_prompt = """You are a helpful customer support agent for ShopBot.

Company policies:
- Shipping: Standard 5-7 days ($4.99), Express 2 days ($12.99), Free on orders over $50
- Returns: 30-day return window. Free returns for defective items. Customer pays for other returns.
- Refunds: Processed within 3-5 business days after return received
- Contact: support@shopbot.example.com, Mon-Fri 9am-6pm EST
- Hours: Chat support Mon-Sun 8am-10pm

Answer helpfully and concisely. If you don't know something, say so."""

    # TODO: Replace placeholder with a real Claude call.
    #   Pass state["messages"] as the conversation history.
    #   Use langchain_core message types (HumanMessage, AIMessage).
    #   Set final_response and append AIMessage.

    response = "Thank you for your question! How can I help you today?"  # ← placeholder

    return {
        "final_response": response,
        "messages": [AIMessage(content=response)],
    }


# ---------------------------------------------------------------------------
# Node: Escalation Draft (Runs before interrupt)
# ---------------------------------------------------------------------------

def escalation_draft_node(state: SupportState) -> dict:
    """
    Generate a draft escalation message WITHOUT sending it.
    Execution pauses here for human review (interrupt_before=["escalation_send"]).
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    print("[Escalation] Generating draft for human review...")

    # TODO: Use Claude to generate an empathetic, de-escalating draft message.
    #   Instructions:
    #   - Acknowledge the customer's frustration sincerely
    #   - Say a human specialist will follow up within 2 hours
    #   - Do NOT promise specific outcomes
    #   - Tone: warm, professional, not defensive
    #   Store result in draft_response (do NOT add to messages — that happens in escalation_send).

    draft = (
        "I sincerely apologize for the frustrating experience you've had. "
        "I understand this has been unacceptable, and I want to make sure this is resolved properly. "
        "I'm escalating this to our senior support team, and a specialist will contact you within 2 hours. "
        "Thank you for your patience."
    )  # ← replace placeholder with Claude-generated draft

    return {"draft_response": draft}


# ---------------------------------------------------------------------------
# Node: Escalation Send (Runs after interrupt approval)
# ---------------------------------------------------------------------------

def escalation_send_node(state: SupportState) -> dict:
    """Send escalation message if approved; generate alternative if not."""
    if state.get("approved", False):
        response = state.get("draft_response", "I'll escalate this for you.")
        print("[Escalation] Draft approved — sending.")
    else:
        # TODO: Generate a non-escalation alternative when the human rejects the draft.
        #   Something like: "Let me look into this further to find the best solution."
        response = "I understand your frustration. Let me look into this further and find the best solution for you."
        print("[Escalation] Draft rejected — sending alternative.")

    return {
        "final_response": response,
        "messages": [AIMessage(content=response)],
    }


# ---------------------------------------------------------------------------
# Routing Function
# ---------------------------------------------------------------------------

def route_after_classify(state: SupportState) -> Literal[
    "clarify", "order_lookup", "refund_request", "general_inquiry", "escalate"
]:
    """
    Routing rules:
    - confidence < threshold AND retry_count < MAX_RETRIES -> "clarify"
    - confidence < threshold AND retry_count >= MAX_RETRIES -> "general_inquiry" (fallback)
    - Otherwise: route to the node matching state["intent"]
    """
    confidence = state.get("confidence", 0.0)
    retry_count = state.get("retry_count", 0)
    intent = state.get("intent", "general_inquiry")

    if confidence < CONFIDENCE_THRESHOLD and retry_count < MAX_RETRIES:
        return "clarify"
    if confidence < CONFIDENCE_THRESHOLD:
        return "general_inquiry"

    # TODO: Add validation — if intent is not a valid label, default to general_inquiry
    return intent  # ← works as-is if classify_intent always returns valid intents


# ---------------------------------------------------------------------------
# Graph Assembly
# ---------------------------------------------------------------------------

def build_support_graph(checkpointer=None):
    """Assemble the full support bot StateGraph."""
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

    # Conditional routing from classify
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

    # Retry cycle — clarify goes BACK to classify  # ← this is the cycle
    builder.add_edge("clarify", "classify")

    # Terminal edges
    builder.add_edge("order_lookup", END)
    builder.add_edge("refund_request", END)
    builder.add_edge("general_inquiry", END)
    builder.add_edge("escalate", "escalation_send")
    builder.add_edge("escalation_send", END)

    if checkpointer:
        return builder.compile(
            checkpointer=checkpointer,
            interrupt_before=["escalation_send"],  # pause for human review  # ←
        )
    return builder.compile()


# ---------------------------------------------------------------------------
# Demo Runner
# ---------------------------------------------------------------------------

def run_demo():
    """Run all four demonstration scenarios."""
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
    print("SCENARIO 3: Low Confidence -> Retry Loop")
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
        "This is absolutely unacceptable! I've been waiting 3 weeks and nobody has helped me. "
        "I want to speak to your manager immediately!"
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

    Key: same thread_id means the graph resumes from its last state.
    """
    checkpointer = MemorySaver()
    graph = build_support_graph(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": "customer_multi_turn"}}

    # TODO: Implement multi-turn conversation  # ←
    print("\n[Multi-turn demo not yet implemented — complete the TODO above]")


if __name__ == "__main__":
    run_demo()
    # run_multi_turn_demo()  # Uncomment after implementing
