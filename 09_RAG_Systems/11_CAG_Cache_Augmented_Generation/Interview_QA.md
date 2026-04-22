# CAG — Cache-Augmented Generation Interview Q&A

---

## Beginner

**Q1: What is CAG and what problem does it solve?**

CAG (Cache-Augmented Generation) is an approach where an entire document or knowledge source is loaded into the model's context window once, the model's internal computation for that document is cached, and subsequent queries reuse that cached state instead of reprocessing the document each time. The problem it solves: in standard RAG, every query triggers a retrieval step — chunking, embedding, vector search, re-ranking — which adds latency, infrastructure complexity, and potential for retrieval failures (wrong chunks, missed information). CAG eliminates retrieval entirely for knowledge sources that fit in the context window. The model sees the complete document, not a handful of retrieved fragments, which means questions that require understanding across multiple sections are answered correctly without any retrieval engineering.

---

**Q2: What is a KV cache and why does it make CAG cost-effective?**

When a transformer model processes a sequence of tokens, each attention layer computes Key (K) and Value (V) matrices for every token. These KV pairs are what the attention mechanism uses to relate tokens to each other. The insight: if you process the same document prefix on multiple queries, the K and V matrices for the document tokens are identical each time — recomputing them is wasteful. A KV cache stores these computed matrices from the first processing and reuses them on subsequent calls. Anthropic's prompt caching API charges 90% less for cached tokens ($0.30/MTok vs $3.00/MTok). After just two queries on the same document, caching is cheaper than re-processing. For a session with 20 questions about a long document, the savings on document tokens are ~90%.

---

**Q3: When should you use CAG instead of RAG?**

Use CAG when: the document fits in the context window (a 400-page contract is ~280K tokens — fits in Claude's 200K window if trimmed, or in Gemini's 1M window); you have many queries against the same document; accuracy is critical and retrieval failures are unacceptable; you want minimal infrastructure (no vector database, no embedding pipeline). Stick with RAG when: the knowledge base is too large for any context window (e.g., a 100,000-page documentation corpus); documents change frequently (cache invalidates on every update); you need to query across many different documents based on semantic relevance; cost per query must be minimized regardless of document size. In practice, CAG and RAG complement each other — use CAG for focused, static documents and RAG for large, diverse corpora.

---

## Intermediate

**Q4: How does Anthropic's prompt caching work in practice?**

You mark a `cache_control: {"type": "ephemeral"}` block in your message content at the cache breakpoint. Everything before that breakpoint is cached after the first request. On subsequent requests that use the identical prefix (same system prompt + same document text up to the cache_control marker), Anthropic serves the cached KV state instead of recomputing from scratch. The response includes three token counts: `cache_creation_input_tokens` (paid once at 125% of normal price on the first call), `cache_read_input_tokens` (paid at 10% of normal price on cache hits), and `input_tokens` (the uncached portion — the question, always paid at full price). The cache expires after 5 minutes of inactivity, so long-running sessions should handle cache misses gracefully — a cache miss simply means the document is reprocessed at full cost for that call, after which the cache is refreshed.

---

**Q5: What are the limitations of CAG?**

Three main limitations: (1) **Context window size**: even at 1 million tokens, some corpora are too large — a 100,000-page knowledge base cannot fit in any current context window. CAG simply cannot replace RAG for arbitrarily large knowledge bases. (2) **Cache invalidation**: if the document changes, the cache is invalidated. For knowledge bases that update frequently, you constantly pay the cache write cost. RAG with live re-indexing handles this more gracefully. (3) **Cache expiration**: Anthropic's ephemeral cache expires after 5 minutes of inactivity. For long user sessions with gaps between questions, the cache may expire and the next query triggers a full recomputation. Applications must handle this gracefully (detect cache miss from the `cache_creation_input_tokens` field, absorb the cost, and continue). OpenAI's cache is longer-lived but not explicitly controlled.

---

**Q6: How would you compare the cost of CAG vs standard RAG for a high-query workload?**

Consider a 100-page document (~70,000 tokens) queried 1,000 times per day. **Standard RAG cost**: each query retrieves ~5 chunks (~2,000 tokens) = 2,000 × 1,000 = 2M tokens/day input + generation costs. Plus embedding model costs for each query. **CAG cost**: first query of each cache cycle pays cache write (70,000 × 1.25x). All subsequent queries within the 5-minute window pay only 70,000 × 0.10 + question tokens (~100). For 1,000 queries/day: ~cache writes for ~200 cache sessions (5-min windows) + 800 cache reads + question tokens. The CAG scenario pays significantly less on document tokens but more if the cache expires frequently. The optimal strategy: for a session-heavy product (users asking many questions per session), CAG wins clearly. For sparse, infrequent queries against a large corpus, RAG may be cheaper because you only process the relevant chunks per query.

---

## Advanced

**Q7: How does CAG relate to the "lost in the middle" problem, and how does this affect its use?**

The "lost in the middle" phenomenon (documented in research by Liu et al., 2023) shows that LLMs perform significantly worse at retrieving information from the middle of a very long context compared to the beginning or end. When you load a 200K-token document into CAG, information in the middle pages may be less reliably retrieved than information at the start or end. This is a genuine limitation of CAG for very long documents: a user asking about a specific clause in the middle of a 400-page contract may get a worse answer than if that clause had been the retrieved top-k chunk in a RAG system. Mitigation strategies: (1) put the most important sections at the beginning of the document; (2) use CAG for moderate-length documents (10K–50K tokens) where the middle-problem is less severe; (3) for very long documents, a hybrid approach works — use CAG for the relevant chapter or section, identified by a lightweight retrieval step.

---

**Q8: How would you build a production CAG system that handles cache expiration and multiple concurrent users?**

A robust production CAG system needs: (1) **Cache warmup tracking** — maintain a dictionary mapping `(document_id, model)` → `last_cache_active_time`. If the last query was >4 minutes ago, assume the cache expired and accept the next call will pay cache write cost; (2) **Concurrent user handling** — for N users querying the same document simultaneously, all N queries can share the same cache since the document prefix is identical. This is a significant advantage over RAG (which has independent vector searches per user); (3) **Session management** — group user queries within a session and keep the cache warm by sending periodic "keep-alive" queries (or accepting expiry gracefully); (4) **Multi-document routing** — if you have multiple document types (different contracts, different manuals), route each document to its own cached context. Don't concatenate unrelated documents — unnecessary tokens slow generation and confuse the model; (5) **Fallback to RAG** — for documents that exceed the context window, automatically fall back to RAG with a clear separation in your routing logic.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concept |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |

⬅️ **Prev:** [GraphRAG](../10_GraphRAG/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [AI Agents — Fundamentals](../../10_AI_Agents/01_Agent_Fundamentals/Theory.md)
