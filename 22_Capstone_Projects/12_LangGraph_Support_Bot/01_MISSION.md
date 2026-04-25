# Project 12 — LangGraph Support Bot

## The Real-World Story

Imagine you're on-call at an e-commerce company. It's Black Friday. 50,000 support tickets pour in over 6 hours. Your team of 12 agents handles 400 tickets. The remaining 49,600 go unanswered. Customer satisfaction craters. Returns spike.

The company deploys an AI support bot the following year. But this bot is a simple chain: classify intent, look up answer, respond. It handles 70% of tickets correctly. The other 30%? It confidently gives wrong answers about refund policies, invents order statuses that don't exist, and sometimes forwards customers to agents who don't have permission to help.

The problem wasn't the model — it was the architecture. A chain has no memory of what it already tried. It can't loop back when it's unsure. It can't pause and ask a human before sending a sensitive escalation.

LangGraph solves all of this. This project builds a production-grade support bot with proper state, conditional routing, retry loops, human approval gates, and conversation checkpointing.

---

## What You Build

A customer support agent using LangGraph's `StateGraph` that handles four intent classes and includes safety mechanisms for edge cases.

Intent classes:
- `order_lookup` — Customer wants status on an order
- `refund_request` — Customer wants a refund processed
- `general_inquiry` — FAQ-style questions
- `escalate` — Sensitive issues requiring human review

Key behaviors:
1. Intent classification with confidence score
2. If confidence < 0.7, retry classification with a clarification prompt
3. Specialist nodes for each intent with access to mock tool calls
4. Human-in-the-loop interrupt before sending any escalation message
5. MemorySaver checkpointing so conversations resume after timeout
6. Graceful handling of failed tool calls

Deliverable: A runnable Python script demonstrating all four intent paths, a retry loop, and the human interrupt flow.

---

## What Success Looks Like

```
=== Scenario 1: Order Lookup ===
User: "Where is my order #8472?"

[Classify] Intent: order_lookup | Confidence: 0.94
[Route]    -> order_lookup node
[OrderLookup] Order #8472: Shipped — arriving Tomorrow by 8pm

Bot: Your order #8472 is currently Shipped. Estimated arrival: Tomorrow by 8pm.

=== Scenario 4: Escalation with Human-in-the-Loop ===
User: "This is unacceptable! I've been waiting 3 weeks. Get me your manager!"

[Classify] Intent: escalate | Confidence: 0.95
[Route]    -> escalation_draft node
[INTERRUPT] Human approval required before sending escalation message.
            Draft: "I sincerely apologize for the frustrating experience..."
            Approve? (y/n): y
[Resume]   Escalation message sent.

=== Scenario 3: Low Confidence Retry ===
User: "It's about the thing from before"

[Classify] Confidence: 0.45 — below threshold (0.70)
[Clarify]  Attempt 1 of 2
Bot: Could you tell me more — is this about an order status, a refund, or something else?
[Classify] Intent: order_lookup | Confidence: 0.92 (after clarification)
```

---

## Concepts Covered

| Concept | What You Learn |
|---|---|
| StateGraph | Typed state that flows through every node, state reducers |
| Conditional Edges | Routing functions that return node names based on state |
| Retry Loop | Cycle edges (clarify -> classify) with termination condition |
| Human-in-the-Loop | `interrupt_before` to pause execution for human approval |
| MemorySaver | Conversation checkpointing and resume by thread_id |
| Specialist Nodes | Independent handlers per intent with own tool access |

---

## Prerequisites

- Completed Intermediate Path or equivalent
- Python comfortable with type hints and dataclasses
- Basic understanding of what a state machine is
- Anthropic SDK experience (at least Intermediate Project 2 or equivalent)

---

## Learning Format

**Difficulty:** Medium-Hard (4 / 5)

Individual LangGraph concepts are well-documented. The difficulty is composing all six concepts (routing, loops, interrupts, checkpointing) into a single coherent system and debugging graph execution.

**Theory files to read first:**
- `15_LangGraph/01_LangGraph_Fundamentals/Theory.md`
- `15_LangGraph/02_Nodes_and_Edges/Theory.md`
- `15_LangGraph/03_State_Management/Theory.md`
- `15_LangGraph/04_Cycles_and_Loops/Theory.md`
- `15_LangGraph/05_Human_in_the_Loop/Theory.md`

**Tools and libraries:**
| Tool | Purpose |
|---|---|
| `langgraph` | StateGraph, nodes, edges, checkpointing |
| `langchain-anthropic` | Claude integration for LangGraph |
| `anthropic` | Direct SDK access for custom calls |
| `langchain-core` | Message types (HumanMessage, AIMessage) |

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| 01_MISSION.md | you are here |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design and node reference |
| [03_GUIDE.md](./03_GUIDE.md) | Progressive build steps |
| [src/starter.py](./src/starter.py) | Runnable Python skeleton |
| [04_RECAP.md](./04_RECAP.md) | What you learned, extensions, job mapping |

⬅️ **Prev:** [11 — Advanced RAG with Reranking](../11_Advanced_RAG_with_Reranking/01_MISSION.md)
➡️ **Next:** [13 — Automated Eval Pipeline](../13_Automated_Eval_Pipeline/01_MISSION.md)
