# Data Flow Diagram
## Design Case 01: Customer Support Agent

Two flows: the happy path (agent answers successfully) and the escalation path (agent hands off to human). Both are shown in full detail.

---

## Happy Path: Agent Answers the Question

```mermaid
sequenceDiagram
    actor User
    participant GW as API Gateway
    participant CM as Conversation Manager
    participant Redis
    participant Postgres
    participant Embed as Embedding Service
    participant Pinecone
    participant LLM as Claude 3.5 Sonnet
    participant CRM as Account Lookup API

    User->>GW: POST /chat { session_id, message }
    GW->>GW: Validate JWT, check rate limit

    GW->>CM: Forward request with user_id

    CM->>Redis: GET session:{session_id}
    Redis-->>CM: Session JSON (last 8 messages)
    Note over CM: If no session: create new, generate session_id

    par Parallel Operations
        CM->>Embed: Embed user message
        Embed-->>CM: query_vector [1536 floats]
    and
        CM->>Postgres: Load user account flags
        Postgres-->>CM: { tier: "premium", status: "active" }
    end

    CM->>Pinecone: query(vector, top_k=5, filter={})
    Pinecone-->>CM: [chunk1, chunk2, chunk3] with similarity scores
    Note over CM: Filter: keep chunks with score >= 0.72

    CM->>CM: Assemble context window
    Note over CM: System prompt + history + KB chunks + current message

    CM->>LLM: POST /messages { messages, tools, max_tokens: 1000 }

    LLM->>LLM: Decide: tool call needed?
    LLM-->>CM: { tool_use: "get_ticket_history", input: { user_id } }

    CM->>CRM: GET /accounts/{user_id}/tickets
    CRM-->>CM: [ { ticket_id, status, summary } ]

    CM->>LLM: [tool_result appended] Continue generation
    LLM-->>CM: { stop_reason: "end_turn", response: "Your last ticket..." }

    CM->>Redis: SET session:{id} [updated messages] EX 1800
    CM->>Postgres: INSERT message (user + assistant)

    CM-->>GW: { response, session_id, sources_used }
    GW-->>User: Streaming response tokens
```

---

## Escalation Path: Handing Off to Human

```mermaid
sequenceDiagram
    actor User
    participant CM as Conversation Manager
    participant Rules as Escalation Rules Engine
    participant LLM as Claude 3.5 Sonnet
    participant EscSvc as Escalation Service
    participant Zendesk
    participant Queue as Human Agent Queue
    participant Postgres

    User->>CM: "I want to speak to a manager about my $800 refund"

    CM->>Rules: Pre-LLM keyword check
    Rules->>Rules: Detect "speak to manager" + refund > $500
    Rules-->>CM: ESCALATE flag set (reason: "user_requested + high_value")

    CM->>LLM: Generate acknowledgement response
    LLM-->>CM: "I understand you'd like to speak with a specialist..."

    CM->>EscSvc: escalate({ session_id, user_id, reason, priority: "high" })

    EscSvc->>Postgres: Load full conversation transcript
    Postgres-->>EscSvc: All messages in session

    EscSvc->>Zendesk: POST /tickets
    Note over EscSvc,Zendesk: Subject: "Escalation: $800 refund request"\nBody: full transcript\nPriority: urgent\nTag: ai-escalation, high-value

    Zendesk-->>EscSvc: { ticket_id: "TKT-99281" }

    EscSvc->>Queue: Publish { ticket_id, user_id, priority: "high", channel: "chat" }
    Queue-->>EscSvc: Acknowledged

    EscSvc-->>CM: { ticket_id: "TKT-99281", est_wait: "< 5 min" }

    CM-->>User: "I've connected you with a specialist (Ticket #TKT-99281). Expected wait: < 5 minutes."
    CM->>CM: Lock session (no further AI responses until human takes over)
```

---

## Knowledge Base Indexing Flow (Background Process)

This flow runs whenever new documentation is uploaded, not during user conversations.

```mermaid
flowchart LR
    A["Document Upload\nPDF / Word / HTML / Confluence"] --> B["Text Extraction\npymupdf, python-docx\nBeautifulSoup"]
    B --> C["Text Cleaning\nRemove headers/footers\nNormalize whitespace"]
    C --> D["Chunking\nRecursiveCharacterTextSplitter\n512 tokens, 50 overlap"]
    D --> E["Embedding\ntext-embedding-3-small\nBatch: 100 chunks/request"]
    E --> F{"Existing doc\nin Pinecone?"}
    F -- Yes --> G["Delete old vectors\nby document_id"]
    F -- No --> H["Continue"]
    G --> H
    H --> I["Upsert to Pinecone\nID, vector, metadata"]
    I --> J["Update Postgres\ndocuments table:\nchunk_count, indexed_at, status=active"]
    J --> K["Notify: indexing complete\nLog chunk count, total tokens"]
```

---

## Token Flow and Cost Breakdown

For every conversation turn, here is exactly where tokens are consumed:

```mermaid
flowchart TD
    A["User Message\n~50 tokens input"]
    B["System Prompt\n~600 tokens (fixed)"]
    C["Conv History\n~1,600 tokens (last 8 pairs)"]
    D["KB Chunks\n~1,200 tokens (top 3)"]
    E["Tool Results\n~200 tokens (account data)"]
    F["LLM Input\n~3,650 tokens total"]
    G["LLM Output\n~400 tokens response\n+ ~100 tokens tool calls"]
    H["Cost Calculation\nInput: 3,650 × $0.000003 = $0.011\nOutput: 500 × $0.000015 = $0.0075\nTotal: ~$0.018 per turn"]

    A --> F
    B --> F
    C --> F
    D --> F
    E --> F
    F --> G
    G --> H
```

**At 10,000 active users sending 5 messages/day = 50,000 turns/day:**
- Cost per day: 50,000 × $0.018 = **$900/day**
- Cost per month: **$27,000/month**

This is where semantic caching pays off. If 40% of queries are FAQ-type (similar to previously asked questions), caching reduces this to **$540/day**.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Architecture_Blueprint.md](./Architecture_Blueprint.md) | System architecture blueprint |
| [📄 Build_Guide.md](./Build_Guide.md) | Step-by-step build guide |
| [📄 Component_Breakdown.md](./Component_Breakdown.md) | Component breakdown |
| 📄 **Data_Flow_Diagram.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Tech_Stack.md](./Tech_Stack.md) | Technology stack choices |

⬅️ **Prev:** [09 Scaling AI Apps](../../12_Production_AI/09_Scaling_AI_Apps/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [02 RAG Document Search System](../02_RAG_Document_Search_System/Architecture_Blueprint.md)
