# Agent Memory — Comparison Table

A detailed side-by-side comparison of all memory types for AI agents.

---

## Full Comparison Table

| | **In-Context (Buffer)** | **Summarization** | **Entity** | **Vector (Long-Term)** |
|---|---|---|---|---|
| **How it works** | Stores full conversation history in the prompt | Uses an LLM to compress old turns into a rolling summary | Tracks named entities (people, places, things) and facts about them | Embeds memories as vectors, retrieves via semantic search |
| **Storage location** | Inside the prompt | Inside the prompt (as summary text) | Inside the prompt (as a structured fact list) | External vector database (Chroma, Pinecone, FAISS, etc.) |
| **Capacity** | Limited by context window (~4K–128K tokens) | Much more — older turns are compressed | Dozens of entities before prompt gets large | Unlimited — stored outside the model |
| **Retrieval method** | Instant — already in the prompt | Instant — already in the prompt | Instant — already in the prompt | Semantic similarity search — adds latency |
| **Precision** | Exact — every word preserved | Lossy — summarization loses detail | Exact for tracked entities | Approximate — finds semantically similar memories |
| **Persists across sessions?** | No (unless you save and reload) | No (unless you save and reload) | Yes (if stored in a database) | Yes — designed for cross-session use |
| **Scalability** | Low — breaks on long conversations | Medium — handles longer convos | Medium — works while entities are focused | High — scales to millions of memories |
| **Cost** | Cheap per turn, expensive as history grows | Moderate — summarization LLM calls cost tokens | Moderate — entity extraction can add calls | Higher — embedding + retrieval infrastructure |
| **Complexity** | Very low — plug and play | Low — one extra LLM call for summary | Medium — needs entity extraction logic | High — needs vector DB, embedding model, retrieval pipeline |
| **Best use case** | Short focused conversations | Long support conversations | Personal assistants, project trackers | Multi-session memory, knowledge bases |
| **LangChain class** | `ConversationBufferMemory` | `ConversationSummaryMemory` | `ConversationEntityMemory` | `VectorStoreRetrieverMemory` |
| **Example framework** | LangChain, LlamaIndex | LangChain, LlamaIndex | LangChain | LangChain + Chroma/Pinecone |

---

## Decision Guide: Which Memory to Use?

```
Start here:
↓
Is this a single short conversation (under 20 turns)?
→ YES: ConversationBufferMemory (simple, fast, exact)
→ NO: Continue ↓

Does the conversation need to track specific named things
(people, projects, tasks)?
→ YES: ConversationEntityMemory (or combine with buffer)
→ NO: Continue ↓

Is the conversation potentially very long (50+ turns)?
→ YES: ConversationSummaryMemory (or SummaryBufferMemory)
→ NO: Continue ↓

Does the agent need memory across multiple sessions?
→ YES: VectorStoreRetrieverMemory (long-term, semantic)
→ NO: ConversationBufferMemory is probably fine
```

---

## Real-World Use Case Examples

| Use Case | Memory Strategy | Why |
|---|---|---|
| Customer support chatbot (one ticket) | Buffer memory | Single conversation, need exact history |
| Customer support (returning customer) | Buffer + Vector memory | Current ticket in buffer, past tickets in vector |
| Personal assistant (calendar/tasks) | Entity + Buffer | Track tasks, people, and dates explicitly |
| Research agent (multi-step, long) | Summary + Vector | Long conversation gets summarized, past research stored |
| Coding assistant (single session) | Buffer memory | Need exact code context from earlier in conversation |
| Coding assistant (across projects) | Vector memory | Retrieve relevant code context from past work |
| Language learning tutor | Summary + Entity | Track student's level, mistakes, vocabulary — entity memory |
| Medical Q&A bot | Vector memory | Retrieve relevant medical literature, patient history |

---

## How Memory Types Work Together

Production agents often combine multiple memory types:

```
                    ┌─────────────────────┐
                    │     Current Query   │
                    └──────────┬──────────┘
                               │
           ┌───────────────────┼───────────────────┐
           ▼                   ▼                   ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │ Buffer/      │  │   Entity     │  │   Vector     │
    │ Summary      │  │   Memory     │  │   Memory     │
    │ (this convo) │  │ (key facts)  │  │ (past convos)│
    └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
           └──────────────────┴──────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Combined Context  │
                    │   → LLM Response    │
                    └─────────────────────┘
```

Each memory source contributes different information. The LLM sees all of it and produces a response that draws on all three.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |
| 📄 **Comparison.md** | ← you are here |

⬅️ **Prev:** [03 Tool Use](../03_Tool_Use/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 Planning and Reasoning](../05_Planning_and_Reasoning/Theory.md)
