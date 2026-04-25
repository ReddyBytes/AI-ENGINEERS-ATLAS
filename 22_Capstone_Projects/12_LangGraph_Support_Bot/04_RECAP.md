# Project 12 — LangGraph Support Bot: Recap

## What You Built

A stateful customer support agent using LangGraph's `StateGraph` that handles four intent classes with conditional routing, a confidence-based retry loop, and a human-in-the-loop approval gate for sensitive escalations. All conversation state is checkpointed with `MemorySaver`, allowing sessions to survive restarts and resume exactly where they left off.

---

## Concepts Applied

| Concept | How You Applied It |
|---|---|
| StateGraph | Defined `SupportState` as a `TypedDict` with all fields needed by every node; compiled it into a runnable graph |
| `add_messages` reducer | Used `Annotated[list, add_messages]` on the messages field so nodes append to conversation history rather than replacing it |
| Conditional Edges | Wrote `route_after_classify()` that inspects confidence and retry_count to decide which node runs next |
| Retry Cycle | Added `builder.add_edge("clarify", "classify")` — a back-edge that creates a loop; controlled by the `retry_count < MAX_RETRIES` guard in the router |
| `interrupt_before` | Compiled the graph with `interrupt_before=["escalation_send"]` so execution pauses before sending sensitive messages |
| `graph.update_state()` | Injected the human's approval decision into the saved checkpoint before resuming |
| MemorySaver | Each node's output is saved after execution; the same `thread_id` picks up the right conversation on the next invoke |

---

## Extension Ideas

**1. Fifth intent — `account_issue`**
Add a specialist node for account-related issues (password reset, billing address, duplicate charges). Extend the classifier prompt to recognize this intent. Add routing, a new node, and a mock account database. This tests whether the routing table and state flow correctly scale to additional intents.

**2. Real multi-turn conversation memory**
Replace the simulated user reply in `clarification_node` with an actual pause and resume loop. After the bot asks for clarification, wait for a real human reply (from stdin or an HTTP endpoint), append it as a `HumanMessage`, and continue. This is the production pattern — the graph literally pauses mid-execution and waits.

**3. Max-retry auto-escalation**
Currently, after `MAX_RETRIES` the system falls back to `general_inquiry`. Add a stricter rule: if the classifier has failed `MAX_RETRIES` times, route to `escalate` automatically rather than giving a generic answer. Track this as a separate `auto_escalated` flag in state so human reviewers know why the escalation was triggered.

---

## Job Mapping

| Role | How this project applies |
|---|---|
| ML Engineer | Builds stateful AI agents; understands the difference between chains and graphs for production deployments |
| Backend Engineer | Integrates LangGraph's interrupt/resume pattern with API endpoints and persistent storage (SqliteSaver, PostgresSaver) |
| AI Product Engineer | Designs human-in-the-loop workflows; builds approval gates for sensitive AI outputs before they reach customers |
| Conversational AI Engineer | Implements intent classification, confidence thresholds, and retry logic for production support bots |
| Platform Engineer | Manages checkpointer backends (MemorySaver -> SqliteSaver -> PostgresSaver) and the tradeoffs between in-memory and durable state |

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [01_MISSION.md](./01_MISSION.md) | Project context and motivation |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design and node reference |
| [03_GUIDE.md](./03_GUIDE.md) | Progressive build steps |
| [src/starter.py](./src/starter.py) | Runnable Python skeleton |
| 04_RECAP.md | you are here |

⬅️ **Prev:** [11 — Advanced RAG with Reranking](../11_Advanced_RAG_with_Reranking/01_MISSION.md)
➡️ **Next:** [13 — Automated Eval Pipeline](../13_Automated_Eval_Pipeline/01_MISSION.md)
