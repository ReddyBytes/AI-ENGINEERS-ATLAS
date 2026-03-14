# Project 2: LangGraph Support Bot

## Why This Project Matters

Imagine you're on-call at an e-commerce company. It's Black Friday. 50,000 support tickets pour in over 6 hours. Your team of 12 agents handles 400 tickets. The remaining 49,600 go unanswered. Customer satisfaction craters. Returns spike.

The company deploys an AI support bot the following year. But this bot is a simple chain: classify intent, look up answer, respond. It handles 70% of tickets correctly. The other 30%? It confidently gives wrong answers about refund policies, invents order statuses that don't exist, and sometimes forwards customers to agents who don't have permission to help.

The problem wasn't the model — it was the architecture. A chain has no memory of what it already tried. It can't loop back when it's unsure. It can't pause and ask a human before sending a sensitive escalation.

LangGraph solves all of this. This project builds a production-grade support bot with proper state, conditional routing, retry loops, human approval gates, and conversation checkpointing.

---

## What You'll Build

A customer support agent using LangGraph's `StateGraph` that handles four intent classes and includes safety mechanisms for edge cases.

**Intent Classes:**
- `order_lookup` — Customer wants status on an order
- `refund_request` — Customer wants a refund processed
- `general_inquiry` — FAQ-style questions
- `escalate` — Sensitive issues requiring human review

**Key Behaviors:**
1. Intent classification with confidence score
2. If confidence < 0.7, retry classification with a clarification prompt
3. Specialist nodes for each intent with access to (mock) tool calls
4. Human-in-the-loop interrupt before sending any escalation message
5. MemorySaver checkpointing so conversations resume after timeout
6. Graceful handling of failed tool calls

**Deliverable:** A runnable Python script demonstrating all four intent paths, a retry loop, and the human interrupt flow.

---

## Learning Objectives

By completing this project, you will:

- Build a `StateGraph` with typed state (`TypedDict`)
- Define conditional edges using routing functions
- Implement a retry loop using cycle edges back to a prior node
- Use `interrupt_before` to pause execution for human approval
- Persist conversation state with `MemorySaver`
- Resume a graph from a saved checkpoint
- Understand when LangGraph outperforms plain LangChain chains

---

## Topics Covered

| Advanced Path Topic | What You Apply Here |
|---|---|
| Topic 10 — LangGraph Fundamentals | StateGraph, compile, invoke |
| Topic 11 — Nodes & Edges | Node functions, conditional edges, routing |
| Topic 12 — State Management | TypedDict state, state reducers |
| Topic 13 — Cycles & Loops | Retry loop when confidence is low |
| Topic 14 — Human-in-the-Loop | `interrupt_before`, resume from checkpoint |
| Topic 15 — Multi-Agent with LangGraph | Specialist subgraph nodes |

---

## Prerequisites

- Completed Intermediate Path or equivalent
- Python comfortable with type hints and dataclasses
- Basic understanding of what a state machine is
- Anthropic SDK experience (at least Intermediate Project 2 or equivalent)

---

## Difficulty

**4 / 5 — Medium-Hard**

Individual LangGraph concepts are well-documented. The difficulty is composing all six concepts (routing, loops, interrupts, checkpointing) into a single coherent system and debugging graph execution.

---

## Tools & Libraries

| Tool | Purpose |
|---|---|
| `langgraph` | StateGraph, nodes, edges, checkpointing |
| `langchain-anthropic` | Claude integration for LangChain/LangGraph |
| `anthropic` | Direct SDK access for custom calls |
| `langchain-core` | Message types, tool definitions |

---

## Expected Output

```
=== New conversation: thread_001 ===
User: "I want a refund for order #8472"

[Classify] Intent: refund_request | Confidence: 0.92
[Route]    → refund_node
[Refund]   Looking up order #8472...
[Refund]   Order found: $127.50, purchased 3 days ago. Eligible for refund.
[Refund]   Processing refund... ✓

Bot: Your refund of $127.50 for order #8472 has been initiated.
     It will appear on your card within 3-5 business days.

=== Escalation path ===
User: "This is unacceptable, I've been waiting 3 weeks and your manager is incompetent"

[Classify] Intent: escalate | Confidence: 0.95
[Route]    → escalation_node
[INTERRUPT] Human approval required before sending escalation message.
            Draft: "I'm so sorry to hear this. Let me connect you with..."
            Approve? (y/n): y
[Resume]   Escalation message sent.

=== Low confidence retry ===
User: "It's about the thing"

[Classify] Confidence: 0.45 — below threshold
[Retry]    → clarification_node
Bot: I'd like to help! Could you tell me more — is this about an order,
     a refund, or something else?
```

---

## Extension Challenges

1. Add a fifth intent: `account_issue` with its own specialist node
2. Implement conversation memory so the bot remembers previous turns
3. Add tool calling to look up real (mock) order data from a JSON file
4. Build a Streamlit UI that shows the graph state in real time
5. Add a max-retry limit that escalates automatically after 3 failed classifications

---

## Theory Files to Read First

Before coding, read:
- `15_LangGraph/01_LangGraph_Fundamentals/Theory.md`
- `15_LangGraph/01_LangGraph_Fundamentals/Mental_Model.md`
- `15_LangGraph/02_Nodes_and_Edges/Theory.md`
- `15_LangGraph/03_State_Management/Theory.md`
- `15_LangGraph/04_Cycles_and_Loops/Theory.md`
- `15_LangGraph/05_Human_in_the_Loop/Theory.md`
