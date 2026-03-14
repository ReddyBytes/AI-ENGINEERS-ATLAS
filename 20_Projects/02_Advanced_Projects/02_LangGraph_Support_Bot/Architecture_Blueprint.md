# Project 2: Architecture Blueprint

## Full System Flowchart

```mermaid
flowchart TD
    START([User Message]) --> ENTRY[Entry Point]
    ENTRY --> CLS[Classify Intent Node\nReturns: intent + confidence]

    CLS --> ROUTE{Route by Intent\n& Confidence}

    ROUTE -->|confidence < 0.70\nretry_count < 2| CLR[Clarification Node\nAsk user to clarify]
    CLR -->|cycle back| CLS

    ROUTE -->|confidence < 0.70\nretry_count >= 2| GEN[General Inquiry Node\nFallback handler]
    ROUTE -->|order_lookup| ORD[Order Lookup Node\nMock DB query]
    ROUTE -->|refund_request| REF[Refund Node\nEligibility check]
    ROUTE -->|general_inquiry| GEN
    ROUTE -->|escalate| ESC[Escalation Draft Node\nGenerate draft message]

    ESC -->|INTERRUPT - human reviews| HUMAN{Human Review\nApprove/Reject?}
    HUMAN -->|graph.update_state\napproved=True| SEND[Escalation Send Node\nSend approved draft]
    HUMAN -->|graph.update_state\napproved=False| SEND
    SEND --> END1([END])

    ORD --> END2([END])
    REF --> END3([END])
    GEN --> END4([END])

    CHKPT[(MemorySaver\nCheckpointer)] -.->|persists state\nafter each node| CLS
    CHKPT -.-> ESC

    style START fill:#4A90D9,color:#fff
    style HUMAN fill:#E67E22,color:#fff
    style ESC fill:#E74C3C,color:#fff
    style CLR fill:#F39C12,color:#fff
    style CHKPT fill:#8E44AD,color:#fff
    style CLS fill:#27AE60,color:#fff
```

---

## Node Reference Table

| Node | Function | Reads from State | Writes to State | Routes to |
|---|---|---|---|---|
| `classify` | `classify_intent()` | `messages[-1]` | `intent`, `confidence`, `order_id` | Conditional (see router) |
| `clarify` | `clarification_node()` | `retry_count`, `messages` | `retry_count += 1`, `messages` (append Q + simulated reply) | `classify` (cycle) |
| `order_lookup` | `order_lookup_node()` | `order_id`, `messages` | `final_response`, `messages` | `END` |
| `refund_request` | `refund_node()` | `order_id`, `messages` | `final_response`, `messages` | `END` |
| `general_inquiry` | `general_inquiry_node()` | `messages` (full history) | `final_response`, `messages` | `END` |
| `escalate` | `escalation_draft_node()` | `messages` | `draft_response` | `escalation_send` (interrupted) |
| `escalation_send` | `escalation_send_node()` | `approved`, `draft_response` | `final_response`, `messages` | `END` |

---

## State Schema

```mermaid
classDiagram
    class SupportState {
        +Annotated[list, add_messages] messages
        +Optional[str] intent
        +float confidence
        +int retry_count
        +Optional[str] order_id
        +Optional[str] draft_response
        +bool approved
        +Optional[str] final_response
    }
```

| Field | Type | Description | Modified By |
|---|---|---|---|
| `messages` | `list` (append-only) | Full conversation history | Every node (append) |
| `intent` | `str \| None` | One of the four intent classes | `classify` |
| `confidence` | `float` | 0.0–1.0, classifier confidence | `classify` |
| `retry_count` | `int` | Number of clarification retries | `clarify` |
| `order_id` | `str \| None` | Extracted order ID if present | `classify`, `order_lookup` |
| `draft_response` | `str \| None` | Pending escalation message for review | `escalation_draft` |
| `approved` | `bool` | Human approval for escalation | Set via `graph.update_state()` |
| `final_response` | `str \| None` | The final bot message to the user | All specialist nodes |

---

## Human-in-the-Loop Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant G as LangGraph
    participant H as Human Reviewer
    participant C as Checkpointer

    U->>G: "I want to speak to your manager RIGHT NOW"
    G->>G: classify → escalate
    G->>G: escalation_draft_node (generates draft)
    G->>C: Save state (checkpoint)
    Note over G: INTERRUPT before escalation_send
    G-->>H: Return state with draft_response
    H->>H: Reviews draft message
    H->>G: graph.update_state(config, {approved: True})
    H->>G: graph.invoke(None, config=config)
    G->>C: Load checkpoint
    G->>G: escalation_send_node (sends approved draft)
    G-->>U: Final escalation message sent
```

---

## Retry Loop Trace

```mermaid
stateDiagram-v2
    [*] --> classify: User: "it's about the thing"
    classify --> clarify: confidence=0.42 retry=0
    clarify --> classify: retry=1 + new message
    classify --> clarify: confidence=0.55 retry=1
    clarify --> classify: retry=2 + new message
    classify --> general_inquiry: retry=2 >= MAX_RETRIES
    general_inquiry --> [*]: final_response set
```

---

## Routing Decision Table

| `confidence` | `retry_count` | `intent` | Routes to |
|---|---|---|---|
| >= 0.70 | any | `order_lookup` | `order_lookup` |
| >= 0.70 | any | `refund_request` | `refund_request` |
| >= 0.70 | any | `general_inquiry` | `general_inquiry` |
| >= 0.70 | any | `escalate` | `escalate` |
| < 0.70 | 0 or 1 | any | `clarify` |
| < 0.70 | >= 2 | any | `general_inquiry` (fallback) |

---

## Checkpointing Architecture

```mermaid
flowchart LR
    A[Invoke with thread_id] --> B[Load checkpoint\nif exists]
    B --> C[Run nodes until\ninterrupt or END]
    C --> D[Save state to\nMemorySaver]
    D --> E{Interrupt?}
    E -->|Yes| F[Return to caller\nwait for resume]
    E -->|No| G[Return final state]
    F --> H[Human updates state]
    H --> A
```

| Checkpointer | Storage | Use Case |
|---|---|---|
| `MemorySaver` | In-memory Python dict | Development and testing |
| `SqliteSaver` | SQLite file | Single-node production |
| `PostgresSaver` | PostgreSQL | Multi-node production |

---

## File Structure

```
02_LangGraph_Support_Bot/
├── support_bot.py         # Main graph (from Starter_Code.md)
├── mock_data.py           # Extended mock order/customer database
├── test_scenarios.py      # Automated tests for all four paths
└── requirements.txt
```
