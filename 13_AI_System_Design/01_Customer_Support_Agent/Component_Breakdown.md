# Component Breakdown
## Design Case 01: Customer Support Agent

Deep dive into each component — what it does, why it's designed the way it is, and what goes wrong when it's poorly implemented.

---

## 1. Conversation Manager

**This is the most important component.** Everything else is a utility. The Conversation Manager orchestrates the entire interaction.

**Responsibilities:**
- Load the current session from Redis (or create a new one)
- Assemble the context window (system prompt + history + KB chunks + current message)
- Invoke the LLM with the assembled context
- Detect and execute tool calls from the LLM response
- Apply escalation rules
- Save the updated session back to Redis
- Write the final message to PostgreSQL for audit

**Context window management in detail:**

The Conversation Manager enforces a strict token budget. It knows that the LLM's context window is finite and that filling it with irrelevant content degrades response quality (the "lost in the middle" problem — LLMs attend less to content in the middle of a long context).

```
Priority order for context assembly:
1. System prompt (non-negotiable, always included)
2. Current user message (always included)
3. Most recent 4 message pairs (highest signal, always included)
4. Retrieved KB chunks (reranked top 3)
5. Older message pairs (dropped first if budget exceeded)
```

**Session state structure (stored in Redis as JSON):**
```json
{
  "session_id": "ses_abc123",
  "user_id": "usr_456",
  "created_at": "2025-03-09T10:00:00Z",
  "last_active": "2025-03-09T10:15:00Z",
  "messages": [
    {"role": "user", "content": "...", "timestamp": "..."},
    {"role": "assistant", "content": "...", "timestamp": "...", "tokens": 312}
  ],
  "escalation_flags": [],
  "retry_count": 0,
  "account_data_cached": {"plan": "premium", "account_status": "active"}
}
```

**Why Redis for sessions?**
- Sub-millisecond read/write (5ms vs 50ms for Postgres under load)
- TTL-based expiry handles session cleanup automatically
- Session data is ephemeral — we only need it for the duration of the conversation
- If Redis goes down, we fall back to Postgres (slightly higher latency but no data loss)

---

## 2. RAG Retrieval (Knowledge Base Search)

**Purpose:** Find the 3-5 documentation chunks most relevant to the user's current question.

**Indexing pipeline (runs offline, triggered on doc upload):**
1. Parse document (PDF → text, HTML → text, Confluence page → markdown)
2. Split into chunks using `RecursiveCharacterTextSplitter`: 512 tokens, 50-token overlap
3. Embed each chunk with `text-embedding-3-small` (1536 dimensions, $0.02/1M tokens)
4. Upsert into Pinecone with metadata: `{doc_id, chunk_index, source_url, doc_title, last_updated}`

**Query pipeline (runs on every user message):**
1. Embed the current user message (same model as indexing — this is critical)
2. Query Pinecone: `index.query(vector=query_embedding, top_k=5, include_metadata=True)`
3. Filter results: keep only chunks with `similarity_score >= 0.72`
4. If no chunks pass threshold: flag as KB miss → escalation candidate
5. Format retrieved chunks into a context block with source citations

**Why 512 tokens with 50-token overlap?**
- 256 tokens: too small, loses context around the answer, requires retrieving more chunks to get a complete picture
- 1024 tokens: chunks are so large they contain multiple topics, retrieval becomes less precise
- 50-token overlap: ensures that sentences split at chunk boundaries still appear in at least one chunk

**The embedding model consistency rule:**
You must use the same embedding model for both indexing and querying. If you switch models, you need to re-embed the entire knowledge base. This is a painful operational concern — document this clearly and pin the model version.

**Handling knowledge base freshness:**
Support docs change (new product features, updated pricing, policy changes). Each document in PostgreSQL has a `last_modified` timestamp. A background job checks for changes every 15 minutes and re-indexes modified documents. Individual chunk vectors can be updated in Pinecone by ID.

---

## 3. Tool Orchestration

**The LLM decides which tools to call based on tool definitions in the system prompt.** Tool orchestration is the layer that executes those calls and feeds results back.

**Tool definitions passed to Claude:**
```python
tools = [
    {
        "name": "search_knowledge_base",
        "description": "Search support documentation for answers. Use when the user asks a product or policy question.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_ticket_history",
        "description": "Retrieve the user's recent support tickets. Use when the user references a previous issue.",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string"},
                "limit": {"type": "integer", "default": 5}
            },
            "required": ["user_id"]
        }
    },
    {
        "name": "escalate_to_human",
        "description": "Transfer this conversation to a human agent. Use when you cannot resolve the issue or the user requests it.",
        "input_schema": {
            "type": "object",
            "properties": {
                "reason": {"type": "string", "description": "Why escalation is needed"},
                "priority": {"type": "string", "enum": ["low", "medium", "high"]}
            },
            "required": ["reason", "priority"]
        }
    }
]
```

**Execution loop:**
```
while True:
    response = llm.call(messages=context, tools=tools)

    if response.stop_reason == "tool_use":
        tool_call = response.content[0]
        result = execute_tool(tool_call.name, tool_call.input)

        # Append tool call + result to messages
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": [{"type": "tool_result", "tool_use_id": tool_call.id, "content": str(result)}]})

        # Loop back to LLM with tool result
        continue
    else:
        # Final response (stop_reason == "end_turn")
        return response.content[0].text
```

**Tool call limits:** Cap at 5 tool calls per turn to prevent infinite loops. If exceeded, return the response as-is and log a warning.

---

## 4. Escalation Service

**Escalation is not just about routing — it's about context transfer.** A human agent who inherits a conversation needs to know everything the AI already discussed. A bad escalation (context lost, user has to repeat themselves) is worse than no escalation.

**What the escalation service does:**
1. Creates a Zendesk ticket with full conversation transcript in the ticket notes
2. Tags the ticket with escalation reason and detected flags (e.g., `ai-escalation`, `billing-dispute`)
3. Sets ticket priority based on account tier (VIP customers get `urgent`)
4. Sends a PubSub message to the human agent routing system
5. Returns a confirmation to the user with ticket number and expected response time

**Escalation vs Handoff:**
- **Escalation**: AI transfers mid-conversation to a human. Human sees full transcript, continues in the same channel.
- **Ticket creation**: AI creates a ticket for async follow-up (email response within 24h). Used for less urgent issues.

**Preventing premature escalation:**
- Add a "soft escalation warning" state — ask the user "Would you like me to connect you with a specialist?" before hard escalating
- Only hard-escalate on critical keywords or repeated failures
- Track escalation rate in your metrics. If it goes above 30%, your KB coverage is insufficient.

---

## 5. Storage Layer

**PostgreSQL** is the source of truth. Redis is the hot cache. Pinecone is the search index.

**PostgreSQL schema (simplified):**
```sql
-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    account_tier TEXT DEFAULT 'standard',  -- standard, premium, enterprise
    account_status TEXT DEFAULT 'active',  -- active, suspended, vip, flagged
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Conversations (session archive)
CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    session_id TEXT UNIQUE,  -- matches Redis key
    started_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ,
    escalated BOOLEAN DEFAULT FALSE,
    escalation_reason TEXT,
    message_count INTEGER,
    total_tokens INTEGER
);

-- Messages (full audit trail)
CREATE TABLE messages (
    id UUID PRIMARY KEY,
    conversation_id UUID REFERENCES conversations(id),
    role TEXT NOT NULL,  -- user, assistant, tool
    content TEXT NOT NULL,
    tokens INTEGER,
    tool_name TEXT,  -- populated if role = tool
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tickets
CREATE TABLE tickets (
    id UUID PRIMARY KEY,
    conversation_id UUID REFERENCES conversations(id),
    user_id UUID REFERENCES users(id),
    zendesk_ticket_id TEXT,
    status TEXT DEFAULT 'open',
    priority TEXT DEFAULT 'normal',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Indexes that matter:**
```sql
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_conversations_session_id ON conversations(session_id);
```

---

## 6. Observability Stack

**LangSmith / Langfuse (LLM-specific observability):**
Every LLM call is traced with:
- Full input prompt (system + history + KB context)
- Full output (including tool calls)
- Token counts (input/output/total)
- Model used, temperature, latency
- Session ID (so you can trace an entire conversation)

This is invaluable for debugging. When a user reports a bad response, you can pull up the exact trace — see what was in the context window, what the model returned, which tools were called.

**Datadog (infrastructure observability):**
- Service latency histograms (P50/P95/P99 per endpoint)
- Error rate by component (Pinecone errors, LLM API errors, tool call failures)
- Redis hit rate
- Active session count
- Cost per hour (computed from token usage × price)

**Alerting:**
- LLM error rate > 1%: page on-call
- P99 latency > 5s: alert
- Escalation rate > 30% (15-min window): alert (KB coverage problem)
- Redis memory > 80%: alert

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Architecture_Blueprint.md](./Architecture_Blueprint.md) | System architecture blueprint |
| [📄 Build_Guide.md](./Build_Guide.md) | Step-by-step build guide |
| 📄 **Component_Breakdown.md** | ← you are here |
| [📄 Data_Flow_Diagram.md](./Data_Flow_Diagram.md) | Data flow diagram |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Tech_Stack.md](./Tech_Stack.md) | Technology stack choices |

⬅️ **Prev:** [09 Scaling AI Apps](../../12_Production_AI/09_Scaling_AI_Apps/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [02 RAG Document Search System](../02_RAG_Document_Search_System/Architecture_Blueprint.md)
