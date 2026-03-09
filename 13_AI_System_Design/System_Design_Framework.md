# System Design Framework for AI Systems

A structured approach to answering AI system design questions in interviews and designing systems in practice. This framework adapts the classic system design approach to account for the unique properties of LLM-based systems.

---

## The 5-Step Framework

### Step 1: Clarify Requirements (5 minutes)

Never start designing without asking clarifying questions. In an AI system, the answers change the architecture significantly.

**Functional requirements to clarify:**
- What is the input? (text, documents, code, voice?)
- What is the expected output? (generated text, structured data, actions?)
- Does it need to maintain conversation history (multi-turn)?
- Does it need to call external tools or APIs?
- Does it need to cite sources or explain reasoning?
- Is this real-time (streaming response) or batch (async job)?

**Non-functional requirements to clarify:**
- What is the expected QPS (queries per second)?
- What is the acceptable latency? (P50, P99)
- What is the data retention requirement?
- What are the data privacy/compliance requirements? (PII handling, GDPR, SOC2)
- Is this internal tooling or customer-facing?
- What is the cost budget per query?

**Scale questions:**
- How many concurrent users?
- How large is the knowledge base / document corpus?
- How much conversation history needs to be maintained?

> In an interview, explicitly state your assumptions. "I'll assume 1,000 concurrent users, P99 latency target of 3 seconds, and documents up to 50 pages each."

---

### Step 2: Estimate Scale (3 minutes)

Back-of-envelope math to size your system. This drives infrastructure decisions.

**Token estimation:**
- Average user query: ~50 tokens
- Context window used per call: ~4,000 tokens (retrieved docs + history + system prompt)
- LLM output: ~300 tokens
- At 1,000 QPS: 4,300,000 input tokens/second + 300,000 output tokens/second

**Storage estimation:**
- 1 million documents, avg 10 pages, avg 500 tokens/page = 5 billion tokens raw text
- At 1,536 dimensions (text-embedding-3-small), float32 = ~6 bytes/dimension
- 1M documents, 10 chunks each = 10M vectors × 6KB = 60GB vector storage

**Latency budget breakdown (target: 2 seconds end-to-end):**
- API Gateway + routing: 10ms
- Session lookup (Redis): 5ms
- Query embedding: 50ms
- Vector search: 100ms
- Reranking (if used): 200ms
- LLM inference (streaming): 800ms to first token, 2s full response
- Response post-processing: 20ms

**Cost estimation:**
- GPT-4o: $2.50/1M input, $10/1M output
- At 1,000 QPS with 4K input tokens: $2.50 × 4,000/1M = $0.01 per query
- 1M queries/day = $10,000/day — forces you to think about caching and cheaper models

---

### Step 3: Design the Data Model (5 minutes)

What data does your system store and how?

**Core entities in most AI systems:**

```
Users
  id, email, created_at, plan_tier

Sessions / Conversations
  id, user_id, created_at, last_active_at, metadata (JSON)

Messages
  id, session_id, role (user|assistant|system), content, tokens_used, created_at

Documents (for RAG systems)
  id, name, source_url, uploaded_by, created_at, chunk_count, status

Chunks (for RAG systems)
  id, document_id, content, token_count, embedding_id, metadata (page, section)

ToolCalls (for agent systems)
  id, message_id, tool_name, input (JSON), output (JSON), latency_ms, status
```

**Vector storage schema (Pinecone example):**
```
Vector ID: chunk_{document_id}_{chunk_index}
Embedding: [1536 floats]
Metadata: {
  document_id, chunk_index, content_preview,
  document_name, user_id, access_group
}
```

**Key design decisions:**
- Store full message content in PostgreSQL, not in the vector store
- Keep embeddings separate from metadata — vector store holds pointers, relational DB holds truth
- Use soft deletes (`deleted_at`) for documents so you can audit what was indexed

---

### Step 4: Design the Components (15 minutes)

Walk through each major component, explain what it does, and justify the choice.

**Standard components in AI systems:**

| Component | What It Does | Key Design Decision |
|---|---|---|
| API Gateway | Rate limiting, auth, routing | Kong / AWS API Gateway / nginx |
| Session Manager | Load/save conversation context | Redis for hot sessions, Postgres for cold |
| Context Assembler | Builds the prompt from history + retrieved docs | Most critical component — determines quality |
| Embedding Model | Converts text to vectors | text-embedding-3-small vs ada-002 vs Cohere |
| Vector Store | Similarity search over embeddings | Pinecone (managed) vs Weaviate (self-hosted) |
| LLM | Generates the response | Claude Sonnet (cost/quality) vs GPT-4o |
| Tool Orchestrator | Decides which tools to call and sequences them | LangChain / LangGraph / custom |
| Observability | Logs LLM inputs/outputs, traces | LangSmith / Langfuse / Datadog |

**For each component, explain:**
1. What is it doing?
2. What are the inputs and outputs?
3. What happens when it fails?
4. How does it scale?

---

### Step 5: Discuss Tradeoffs (5 minutes)

This is where senior engineers shine. Every design decision has a cost.

**Common tradeoffs in AI systems:**

**Chunk size (RAG):**
- Smaller chunks (256 tokens) = better precision, more chunks to retrieve, loses context
- Larger chunks (1024 tokens) = more context per chunk, noisier retrieval, fills context window faster
- **Decision:** 512 tokens with 50-token overlap is a good starting default

**Model selection:**
- GPT-4o: highest quality, highest cost ($10/1M output), 4s avg latency
- Claude 3.5 Sonnet: comparable quality, lower cost ($3/1M output), similar latency
- GPT-4o-mini / Claude 3.5 Haiku: 10x cheaper, good for classification/routing tasks
- **Decision:** Use a tiered model strategy — cheap model for intent classification, expensive model for generation

**Caching:**
- Semantic caching (cache by embedding similarity) saves 30-60% of LLM calls for FAQ-type systems
- Exact cache (Redis, TTL 1 hour) works when queries are repetitive
- No cache: always fresh, always expensive
- **Decision:** Layer both — exact cache first, semantic cache second, LLM third

**Memory strategy:**
- Full history: unlimited context accumulation → hits context window, expensive
- Sliding window (last N messages): simple, loses early context
- Summarization: compress old messages, preserves semantic content
- **Decision:** Sliding window (last 10 messages) + periodic summarization for long sessions

---

## AI-Specific Design Considerations

These are the areas that trip up engineers who approach AI design like traditional service design.

### Context Window Management

Every LLM has a context window limit (Claude: 200K tokens, GPT-4o: 128K tokens). You cannot assume unlimited context.

**Budget your context window explicitly:**
```
System prompt:           500 tokens  (fixed)
Conversation history:  2,000 tokens  (last 8 messages)
Retrieved documents:   4,000 tokens  (top-k chunks)
User query:              200 tokens  (current message)
Response buffer:       2,000 tokens  (expected output)
─────────────────────────────────────
Total:                 8,700 tokens  (well within 128K, but budget it anyway)
```

If your retrieved docs can be large (e.g., 10 chunks × 1,024 tokens = 10K tokens), you need reranking to reduce to the top 3-4 chunks that actually fit.

### Latency Budget

An LLM call takes 1–5 seconds for the first token. Users tolerate this if they see a streaming response (tokens appearing as they're generated). If they see a blank screen for 3 seconds and then text appears all at once, they will think the system is broken.

**Always stream LLM responses.** Use Server-Sent Events (SSE) or WebSockets. Start sending the response token-by-token as the LLM generates it.

**Parallelize where possible:**
- Run query embedding and session lookup in parallel
- Run multiple tool calls in parallel (if they're independent)
- Pre-fetch likely follow-up context while streaming the response

### Cost Model

LLM costs are per-token, not per-request. A system that works fine at 100 users/day can cost $50,000/month at 100,000 users/day if you didn't model costs.

**Cost optimization levers:**
- **Prompt compression:** Remove redundant context, shorten system prompts
- **Model tiering:** Use cheap models (GPT-4o-mini at $0.15/1M input) for classification/routing, expensive models only for generation
- **Semantic caching:** Cache embeddings + responses for frequently asked questions (30-60% hit rate on FAQ systems)
- **Batch processing:** For non-real-time tasks (document ingestion, report generation), use batch APIs at 50% discount
- **Streaming interruption:** Let users stop generation early — you're billed for tokens generated, not tokens read

### Evaluation Strategy

Without evaluation, you don't know if your AI system is working. This is the most underinvested area in AI systems.

**Four layers of evaluation:**

| Layer | Method | Frequency |
|---|---|---|
| Retrieval quality | Recall@k, MRR, NDCG on golden question set | On every RAG change |
| Generation quality | LLM-as-judge (correctness, grounding, helpfulness) | Daily on sampled traffic |
| End-to-end quality | Human eval on 50-100 queries/week | Weekly |
| Regression testing | Automated tests on known-good question/answer pairs | Every deployment |

**Build an evaluation dataset early.** Collect 50-100 real user queries with expected outputs. Use this as your test suite every time you change chunking strategy, embedding model, or prompts.

### Failure Modes Unique to AI Systems

| Failure Mode | What Happens | Mitigation |
|---|---|---|
| Hallucination | LLM generates confident but wrong answer | Require citation, use RAG, set temperature low |
| Prompt injection | User input hijacks system prompt | Input sanitization, output validation, system prompt hardening |
| Context poisoning | Bad retrieved document leads LLM astray | Reranking, source credibility scoring |
| Rate limiting | LLM API returns 429 | Exponential backoff, fallback models, request queuing |
| Context window overflow | Too many tokens in the prompt | Truncation strategy, summarization, strict budget |
| Stale knowledge base | Indexed documents are outdated | Incremental sync, document versioning, freshness metadata |

---

## Interview Answer Template

When answering an AI system design question in an interview, use this structure:

```
1. "Before I start, let me clarify a few things..." (2 min clarifying questions)
2. "Let me estimate the scale..." (1 min math)
3. "Here's the high-level architecture..." (draw diagram, 3 min)
4. "Let me walk through the data flow for the happy path..." (3 min)
5. "Now let me dig into the hardest components..." (5 min on 2-3 interesting components)
6. "Here are the key tradeoffs I made and alternatives I considered..." (3 min)
7. "For failure modes, the main risks are..." (2 min)
```

Total: ~20 minutes, which is the typical time for a system design question.

