# Build Guide
## Design Case 01: Customer Support Agent

A phased approach that lets you ship something working at each stage. Each phase adds capability on top of the previous one. Don't skip to phase 4 — the earlier phases teach you where the real problems are.

---

## Phase 1: Basic Q&A with RAG (Week 1-2)

**Goal:** A chatbot that answers questions from your documentation. No memory, no tools, no escalation.

**What you build:**
- Script to ingest support docs (PDFs, Confluence, HTML) into a vector store
- Simple API endpoint: `POST /chat` accepts a message, returns an answer
- RAG pipeline: embed query → search Pinecone → stuff chunks into prompt → call LLM → return response

**Stack for this phase:**
- LangChain for RAG pipeline
- OpenAI `text-embedding-3-small` for embeddings (cheap, good quality)
- Pinecone Starter tier (free)
- Claude 3.5 Haiku for generation (fast, cheap for prototyping)

**Key implementation decisions:**
- **Chunk size:** 512 tokens with 50-token overlap. Use `RecursiveCharacterTextSplitter` from LangChain.
- **Top-k:** Retrieve 5 chunks, include all 5 in prompt. Reranking comes in phase 3.
- **System prompt:** Keep it simple — "You are a helpful support agent. Answer using only the provided context. If you don't know, say so."

**What you'll learn:** You'll quickly find that chunk quality matters more than anything else. Some docs will chunk badly (tables get broken up, numbered lists lose context). Fix the chunking before moving on.

**Success criteria:** Can correctly answer 80% of your top-20 most common support questions from documentation.

---

## Phase 2: Tool Calling for Ticket and Account Lookup (Week 3-4)

**Goal:** The agent can look up real user data — account status, order history, existing tickets.

**New components:**
- Two tool definitions: `lookup_account(user_id)` and `get_ticket_history(user_id)`
- Tool execution layer: when LLM requests a tool, your code executes it and returns the result
- Authentication: pass user identity from your auth layer into the conversation manager

**How tool calling works with Claude:**

The LLM receives tool definitions in the system prompt (or via the `tools` API parameter). When it decides to call a tool, it returns a structured JSON response instead of plain text. Your code intercepts this, executes the tool, and calls the LLM again with the tool result appended to the conversation.

```
Turn 1: User: "What's the status of my last order?"
LLM response: { "tool": "lookup_account", "args": { "user_id": "usr_12345" } }
Your code: calls internal CRM API → gets order data
Turn 2: [tool result appended to context]
LLM response: "Your last order #78432 was shipped on March 5th and is expected to arrive March 9th."
```

**What to watch for:**
- Tool call latency adds to total response time. If account lookup takes 500ms, your P99 response time jumps.
- The LLM may try to call tools that don't exist or with wrong argument formats. Add validation and return informative error messages back to the LLM.
- Log every tool call (input + output + latency) from day one. You need this for debugging.

**Success criteria:** Agent correctly identifies returning users, references their account data in responses, and doesn't hallucinate account details.

---

## Phase 3: Escalation Logic (Week 5)

**Goal:** The agent knows when it can't help and hands off gracefully to a human.

**Escalation is two parts:** detection (know when to escalate) and execution (actually do the handoff).

**Detection rules (evaluate in this order):**
1. **Keyword detection (pre-LLM):** Check for "speak to manager", "legal", "lawsuit", "refund over $X" before calling the LLM. These are hard escalates.
2. **KB miss (post-retrieval):** If max similarity score from Pinecone is < 0.72, the knowledge base doesn't have an answer. Flag this.
3. **Retry loop detection:** If the user has sent 3+ messages that are semantically similar (embed + cosine similarity > 0.85), they're not getting what they need.
4. **LLM self-assessment (post-generation):** Add a structured output field: `{ "response": "...", "confidence": "low|medium|high", "should_escalate": true|false }`. Let the LLM flag its own uncertainty.

**Escalation execution:**
- Create a ticket in Zendesk via API with full conversation transcript
- Return a message to the user: "I'm connecting you with a specialist who can better assist. Ticket #12345 has been created."
- Notify the human agent queue (Slack webhook / PubSub message)
- Lock the session — no more LLM calls for this conversation until human takes over

**What to watch for:** The LLM will over-escalate at first (it's conservative). Add a confidence threshold and tune it on real conversations. Track escalation rate as a metric — target is typically 10-20% depending on complexity of your support domain.

---

## Phase 4: Multi-Turn Memory (Week 6-7)

**Goal:** The agent remembers context across the entire conversation, not just the last message.

**Session management with Redis:**
- On first message: create a session ID (UUID), store in Redis with `SET session:{id} {json} EX 1800` (30 min TTL)
- On each message: load session from Redis, append new message, trim to last 10 messages if over limit, save back
- On session expiry: move to PostgreSQL for long-term storage

**Context assembly logic (the most important function in your system):**

```python
def assemble_context(session: Session, current_message: str) -> list[Message]:
    messages = []

    # 1. System prompt (always first)
    messages.append({"role": "system", "content": SYSTEM_PROMPT})

    # 2. Conversation history (last 8 pairs = 16 messages)
    messages.extend(session.recent_messages[-16:])

    # 3. Retrieved KB context (injected as a system message before user's message)
    kb_chunks = retrieve_from_kb(current_message, top_k=3)
    if kb_chunks:
        context_block = format_kb_context(kb_chunks)
        messages.append({"role": "system", "content": f"Relevant documentation:\n{context_block}"})

    # 4. Current user message (always last)
    messages.append({"role": "user", "content": current_message})

    return messages
```

**Summarization for long sessions:**
When a session exceeds 20 messages, summarize the oldest 10 messages into a single "Conversation summary" system message. This keeps context window usage bounded while preserving the key facts from earlier in the conversation.

**Success criteria:** Agent correctly references earlier context ("As I mentioned when you first contacted us about the billing issue...") and doesn't ask the user to repeat themselves.

---

## Phase 5: Evaluation Pipeline (Week 8-9)

**Goal:** Know whether your system is actually working, and catch regressions automatically.

**Build a golden dataset:**
- Collect 100 real user queries with their ideal responses
- Include edge cases: out-of-scope questions, ambiguous queries, escalation triggers
- Store as `{query, context, expected_response, expected_escalation: bool}`

**Retrieval evaluation:**
- For each query in your golden set, run the RAG retrieval and check if the relevant chunk appears in top-k results
- Metric: Recall@3 (did the right chunk appear in the top 3 results?)
- Target: Recall@3 > 0.85

**Generation evaluation with LLM-as-judge:**
```python
judge_prompt = """
Rate this support response on three criteria (1-5 each):
1. Factual correctness (does it align with the provided documentation?)
2. Completeness (does it fully address the user's question?)
3. Tone (is it appropriate for customer support?)

User question: {question}
Documentation provided: {context}
Agent response: {response}

Return JSON: {"correctness": N, "completeness": N, "tone": N, "explanation": "..."}
"""
```

Run this on 10% of live traffic daily. Alert if average correctness drops below 4.0.

**Regression tests:**
- Run your golden dataset on every deployment
- Block deployment if Recall@3 drops more than 5% or if judge scores drop more than 0.3 points
- This catches problems before users do

**Dashboard metrics to track:**
- Sessions per day, messages per session
- Escalation rate (target: 10-20%)
- KB hit rate (queries with similarity > 0.75)
- LLM latency (P50/P99 per endpoint)
- Cost per conversation (tokens × price)
- User satisfaction (if you have a thumbs up/down widget)

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Architecture_Blueprint.md](./Architecture_Blueprint.md) | System architecture blueprint |
| 📄 **Build_Guide.md** | ← you are here |
| [📄 Component_Breakdown.md](./Component_Breakdown.md) | Component breakdown |
| [📄 Data_Flow_Diagram.md](./Data_Flow_Diagram.md) | Data flow diagram |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Tech_Stack.md](./Tech_Stack.md) | Technology stack choices |

⬅️ **Prev:** [09 Scaling AI Apps](../../12_Production_AI/09_Scaling_AI_Apps/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [02 RAG Document Search System](../02_RAG_Document_Search_System/Architecture_Blueprint.md)
