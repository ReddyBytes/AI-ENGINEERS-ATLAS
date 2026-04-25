"""
LangGraph Customer Support Bot — Project 12 SOLUTION
======================================================
Features: Intent classification, conditional routing, retry loop,
human-in-the-loop escalation, MemorySaver checkpointing.

Usage:
    python solution.py

Setup:
    pip install langgraph langchain-anthropic langchain-core anthropic
    Set ANTHROPIC_API_KEY in environment.
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

    Claude returns JSON with intent, confidence score, and any extracted order ID.
    Hostile/angry language maps to "escalate". JSON parse errors default to
    general_inquiry with 0.5 confidence so the conversation can still proceed.
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    user_messages = [m for m in state["messages"] if isinstance(m, HumanMessage)]
    latest_message = user_messages[-1].content if user_messages else ""

    print(f"[Classify] Processing: '{latest_message[:60]}'")

    system = """Classify this customer support message into exactly one intent.

Intents:
- order_lookup: asking about order status, tracking, shipping, where is my order
- refund_request: requesting a refund, return, money back, cancel and refund
- escalate: angry, hostile, demanding a manager or supervisor, threatening
- general_inquiry: everything else (FAQ, policies, hours, products)

Rules:
- If the message contains a 4+ digit order number, extract it as order_id
- Angry or hostile language -> escalate, even if asking about an order
- Vague messages with no clear intent -> general_inquiry with low confidence

Return ONLY valid JSON, no other text:
{"intent": "<one of the four intents>", "confidence": <0.0-1.0>, "order_id": "<digits>" or null}"""

    response = client.messages.create(
        model=MODEL,
        max_tokens=100,        # ← short JSON response; no need for more tokens
        system=system,
        messages=[{"role": "user", "content": latest_message}],
    )

    try:
        # Strip any markdown fences Claude might add (```json ... ```)
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = re.sub(r"```[a-z]*\n?", "", raw).strip()
        data = json.loads(raw)
        intent = data.get("intent", "general_inquiry")
        # Validate intent is one we recognize
        if intent not in INTENT_LABELS:
            intent = "general_inquiry"
        return {
            "intent": intent,
            "confidence": float(data.get("confidence", 0.5)),
            "order_id": data.get("order_id") or extract_order_id(latest_message),  # ← fallback regex
        }
    except (json.JSONDecodeError, KeyError, TypeError):
        # On any parse failure, fall back gracefully
        return {
            "intent": "general_inquiry",
            "confidence": 0.5,
            "order_id": extract_order_id(latest_message),
        }


# ---------------------------------------------------------------------------
# Node: Clarification (Retry Path)
# ---------------------------------------------------------------------------

def clarification_node(state: SupportState) -> dict:
    """
    When confidence is too low, ask the user to clarify.
    Increments retry_count and appends clarifying question + simulated reply.

    Returning "messages": [msg1, msg2] APPENDS to state["messages"] because of
    the add_messages reducer — it does NOT replace the existing list.
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    new_retry_count = state["retry_count"] + 1
    print(f"[Clarify] Attempt {new_retry_count} of {MAX_RETRIES}")

    # Generate a natural clarifying question with Claude
    user_messages = [m for m in state["messages"] if isinstance(m, HumanMessage)]
    latest = user_messages[-1].content if user_messages else ""

    clarify_prompt = (
        f"A customer sent this message: '{latest}'\n"
        "It's unclear what they need. Write a short, friendly clarifying question "
        "offering options: order status check, refund request, general help, or other. "
        "Keep it under 30 words. Be warm and helpful."
    )
    response = client.messages.create(
        model=MODEL,
        max_tokens=80,
        messages=[{"role": "user", "content": clarify_prompt}],
    )
    clarifying_question = response.content[0].text.strip()

    clarification_msg = AIMessage(content=clarifying_question)
    simulated_user_reply = HumanMessage(
        content="Actually I want to check on my order #8472"  # ← simulated for testing the retry loop
    )

    return {
        "retry_count": new_retry_count,
        "messages": [clarification_msg, simulated_user_reply],  # ← add_messages appends both
    }


# ---------------------------------------------------------------------------
# Node: Order Lookup Specialist
# ---------------------------------------------------------------------------

def order_lookup_node(state: SupportState) -> dict:
    """
    Look up order status and return a warm, formatted customer response.
    Tries order_id from state first, then scans message history with regex.
    Uses Claude to write the customer-facing message for a natural tone.
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    order_id = state.get("order_id")

    # Scan message history if order_id not in state
    if not order_id:
        for msg in reversed(state["messages"]):
            if isinstance(msg, HumanMessage):
                order_id = extract_order_id(msg.content)
                if order_id:
                    break

    print(f"[OrderLookup] Looking up order #{order_id}")

    if order_id:
        order = lookup_order(order_id)
        if order:
            # Use Claude to write a warm, natural customer-facing message
            context = (
                f"Order #{order_id}: Status={order['status']}, "
                f"ETA={order['eta']}, Total=${order['total']:.2f}"
            )
            write_prompt = (
                f"Write a friendly, concise customer support message confirming order status. "
                f"Order data: {context}. Keep it under 50 words. Be warm and reassuring."
            )
            resp = client.messages.create(
                model=MODEL, max_tokens=120,
                messages=[{"role": "user", "content": write_prompt}],
            )
            response = resp.content[0].text.strip()
        else:
            response = (
                f"I couldn't find order #{order_id} in our system. "
                "Please double-check the order number, or I can connect you with a specialist."
            )
    else:
        response = "I'd be happy to look up your order! Could you please provide your order number?"

    return {
        "final_response": response,
        "messages": [AIMessage(content=response)],
    }


# ---------------------------------------------------------------------------
# Node: Refund Specialist
# ---------------------------------------------------------------------------

def refund_node(state: SupportState) -> dict:
    """
    Process refund request with eligibility check.
    Policy: refunds within 30 days of order. Uses Claude for empathetic messaging.
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    order_id = state.get("order_id")

    # Try to find order_id from messages if not in state
    if not order_id:
        for msg in reversed(state["messages"]):
            if isinstance(msg, HumanMessage):
                order_id = extract_order_id(msg.content)
                if order_id:
                    break

    print(f"[Refund] Processing refund request for order #{order_id}")

    if not order_id:
        response = (
            "I'd be glad to help with a refund. Could you please provide your order number "
            "so I can look into this for you?"
        )
    else:
        order = lookup_order(order_id)
        if not order:
            response = (
                f"I couldn't find order #{order_id} in our system. "
                "Please verify the order number, or I can connect you with a specialist."
            )
        else:
            eligible = order["days_ago"] <= 30  # ← 30-day refund policy

            if eligible:
                context = (
                    f"Order #{order_id} total ${order['total']:.2f} is eligible for refund "
                    f"(ordered {order['days_ago']} days ago, within 30-day window). "
                    f"Refund has been initiated."
                )
                tone = "Confirm refund initiated, 3-5 business days to original payment method. Be warm and reassuring."
            else:
                context = (
                    f"Order #{order_id} was ordered {order['days_ago']} days ago "
                    f"(over the 30-day return window). Total: ${order['total']:.2f}."
                )
                tone = (
                    "Explain the 30-day return policy has passed. Be empathetic. "
                    "Suggest alternatives: store credit, exchange, or escalation to supervisor."
                )

            write_prompt = (
                f"Write a customer support response for a refund request. {tone} "
                f"Context: {context}. Keep it under 60 words."
            )
            resp = client.messages.create(
                model=MODEL, max_tokens=150,
                messages=[{"role": "user", "content": write_prompt}],
            )
            response = resp.content[0].text.strip()

    return {
        "final_response": response,
        "messages": [AIMessage(content=response)],
    }


# ---------------------------------------------------------------------------
# Node: General Inquiry
# ---------------------------------------------------------------------------

def general_inquiry_node(state: SupportState) -> dict:
    """Handle FAQ-style questions using Claude with ShopBot company policy context."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    system_prompt = """You are a helpful customer support agent for ShopBot.

Company policies:
- Shipping: Standard 5-7 days ($4.99), Express 2 days ($12.99), Free on orders over $50
- Returns: 30-day return window. Free returns for defective items. Customer pays for other returns.
- Refunds: Processed within 3-5 business days after return received
- Contact: support@shopbot.example.com, Mon-Fri 9am-6pm EST
- Hours: Chat support Mon-Sun 8am-10pm

Answer helpfully and concisely. Keep responses under 100 words. If you don't know something, say so."""

    # Extract the conversation history as formatted messages for context
    conversation = []
    for msg in state["messages"]:
        if isinstance(msg, HumanMessage):
            conversation.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            conversation.append({"role": "assistant", "content": msg.content})

    # Ensure conversation ends with a user message
    if not conversation or conversation[-1]["role"] != "user":
        conversation.append({"role": "user", "content": "Hello, I need help."})

    resp = client.messages.create(
        model=MODEL,
        max_tokens=200,
        system=system_prompt,
        messages=conversation,
    )
    response = resp.content[0].text.strip()

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
    Execution pauses AFTER this node for human review
    (interrupt_before=["escalation_send"] in the compiled graph).
    Draft is stored in state; the send node reads it after approval.
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    print("[Escalation] Generating draft for human review...")

    # Get the customer's original message for context
    user_messages = [m for m in state["messages"] if isinstance(m, HumanMessage)]
    customer_message = user_messages[0].content if user_messages else "frustrating experience"

    draft_prompt = (
        f"A customer sent this angry message: '{customer_message[:200]}'\n\n"
        "Write a de-escalating response that:\n"
        "- Sincerely acknowledges their frustration without being defensive\n"
        "- Says a senior specialist will follow up within 2 hours\n"
        "- Does NOT promise specific outcomes (refunds, replacements, etc.)\n"
        "- Tone: warm, professional, empathetic\n"
        "Keep it under 60 words."
    )

    resp = client.messages.create(
        model=MODEL,
        max_tokens=150,
        messages=[{"role": "user", "content": draft_prompt}],
    )
    draft = resp.content[0].text.strip()

    # Store as draft_response — NOT added to messages yet (that happens in escalation_send)
    return {"draft_response": draft}


# ---------------------------------------------------------------------------
# Node: Escalation Send (Runs after interrupt approval)
# ---------------------------------------------------------------------------

def escalation_send_node(state: SupportState) -> dict:
    """
    Send escalation message if approved; generate an alternative if not.
    Reads the approved flag set by the human reviewer via graph.update_state().
    """
    if state.get("approved", False):
        # Human approved the draft — send it as-is
        response = state.get("draft_response", "I'll escalate this for you right away.")
        print("[Escalation] Draft approved — sending.")
    else:
        # Human rejected the draft — generate a non-escalation alternative
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        alt_prompt = (
            "Write a brief, empathetic message telling a customer you're looking further "
            "into their issue to find the best solution. Do not escalate or make promises. "
            "Keep it under 30 words."
        )
        resp = client.messages.create(
            model=MODEL, max_tokens=80,
            messages=[{"role": "user", "content": alt_prompt}],
        )
        response = resp.content[0].text.strip()
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
    - Low confidence + retries remaining  -> ask for clarification
    - Low confidence + retries exhausted  -> fall back to general_inquiry
    - Otherwise                           -> route to intent-matched specialist node
    """
    confidence = state.get("confidence", 0.0)
    retry_count = state.get("retry_count", 0)
    intent = state.get("intent", "general_inquiry")

    if confidence < CONFIDENCE_THRESHOLD and retry_count < MAX_RETRIES:
        print(f"[Route] Low confidence ({confidence:.2f}), retry {retry_count+1}/{MAX_RETRIES}")
        return "clarify"

    if confidence < CONFIDENCE_THRESHOLD:
        print(f"[Route] Max retries reached — falling back to general_inquiry")
        return "general_inquiry"

    # Validate intent is a recognized label
    if intent not in ["order_lookup", "refund_request", "general_inquiry", "escalate"]:
        intent = "general_inquiry"

    print(f"[Route] Intent='{intent}', confidence={confidence:.2f} -> routing to {intent}")
    return intent


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

    # Conditional routing from classify node
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

    # Retry cycle — clarify loops BACK to classify until confidence improves or retries exhausted
    builder.add_edge("clarify", "classify")  # ← this is the cycle

    # Terminal edges for specialist nodes
    builder.add_edge("order_lookup", END)
    builder.add_edge("refund_request", END)
    builder.add_edge("general_inquiry", END)
    builder.add_edge("escalate", "escalation_send")  # ← draft -> (interrupt) -> send
    builder.add_edge("escalation_send", END)

    if checkpointer:
        return builder.compile(
            checkpointer=checkpointer,
            interrupt_before=["escalation_send"],  # ← pause AFTER draft, BEFORE send
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
    print("SCENARIO 2: Refund Request (eligible order)")
    print("="*60)
    config = {"configurable": {"thread_id": "thread_refund_001"}}
    state = default_state()
    state["messages"] = [HumanMessage("I want a refund for order #8472 please")]
    result = graph.invoke(state, config=config)
    print(f"Final response: {result.get('final_response')}")

    print("\n" + "="*60)
    print("SCENARIO 2b: Refund Request (ineligible — beyond 30 days)")
    print("="*60)
    config = {"configurable": {"thread_id": "thread_refund_002"}}
    state = default_state()
    state["messages"] = [HumanMessage("I want a refund for order #1234")]  # 35 days ago
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
    print("SCENARIO 4: Escalation with Human-in-the-Loop (auto-approving)")
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

        # Auto-approve for non-interactive demo; in production: approved = input("y/n") == "y"
        approved = True
        print(f"\nAuto-approving for demo: approved={approved}")

        graph.update_state(config, {"approved": approved})  # ← inject human decision into saved state
        final = graph.invoke(None, config=config)            # ← resume from checkpoint with None input
        print(f"\nFinal response: {final.get('final_response')}")
    else:
        print(f"Final response: {result.get('final_response')}")


def run_multi_turn_demo():
    """
    Demonstrate multi-turn conversation using checkpointing.
    The same thread_id means the graph resumes from its last state across invocations.
    Message history accumulates: each new message is appended by the add_messages reducer.
    """
    checkpointer = MemorySaver()
    graph = build_support_graph(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": "customer_multi_turn"}}

    print("\n" + "="*60)
    print("MULTI-TURN DEMO")
    print("="*60)

    # Turn 1: vague message
    print("\n[Turn 1] Customer: Hi, I need help")
    state = default_state()
    state["messages"] = [HumanMessage("Hi, I need help")]
    result = graph.invoke(state, config=config)
    print(f"Bot: {result.get('final_response')}")

    # Turn 2: follow-up on same thread — history is preserved in MemorySaver
    print("\n[Turn 2] Customer: It's about order #5555")
    result = graph.invoke(
        {"messages": [HumanMessage("It's about order #5555")]},  # ← only new message needed
        config=config,  # ← same thread_id resumes accumulated state
    )
    print(f"Bot: {result.get('final_response')}")

    # Turn 3: another follow-up
    print("\n[Turn 3] Customer: I'd like to return it")
    result = graph.invoke(
        {"messages": [HumanMessage("I'd like to return it")]},
        config=config,
    )
    print(f"Bot: {result.get('final_response')}")

    # Show message history accumulated across all turns
    total_msgs = len(result.get("messages", []))
    print(f"\n[Multi-turn] Total messages in thread: {total_msgs}")
    print("[Multi-turn] History accumulates correctly across turns via MemorySaver.")


if __name__ == "__main__":
    run_demo()
    run_multi_turn_demo()
