# Memory Systems — Cheatsheet

**One-liner:** Memory systems give LLM applications the ability to persist information across conversation turns and sessions — overcoming the model's stateless, context-limited nature.

---

## Key Terms

| Term | Definition |
|------|-----------|
| **Context window** | Max tokens the model can process at once — the "working memory" limit |
| **In-context memory** | Keeping the full conversation history in the messages array |
| **Memory summarization** | Compressing old turns into a summary when history gets too long |
| **External memory** | A separate store (vector DB, database) outside the LLM context |
| **Episodic memory** | Memory of specific past events/conversations |
| **Semantic memory** | Memory of facts, preferences, and structured user profile data |
| **Working memory** | What's currently in the context window (LLM's immediate awareness) |
| **MemGPT** | An architecture where the LLM itself manages what to remember and forget |
| **Memory retrieval** | Fetching relevant past memories to include in the current prompt |

---

## Memory Type Comparison

| Type | Storage | Capacity | Retrieval | Cost per Turn |
|------|---------|----------|-----------|---------------|
| In-context | Messages array | Limited by context window | All of it, always | High (grows with turns) |
| Summarization | Compressed text | Medium (summary + recent) | Full summary | Medium |
| Vector store | External DB | Unlimited | Top-K relevant | Low (retrieval cost) |
| Structured/key-value | Database | Unlimited | Exact lookup | Very low |

---

## When to Use Each

| Memory Type | Use When... |
|-------------|-------------|
| In-context only | Single session, < 20 turns, context fits |
| + Summarization | Long single sessions (document work, debugging) |
| + Vector store | Multi-session app, remembering past conversations |
| + Structured DB | User preferences, account info, settings |
| MemGPT-style | Autonomous agents, long-running tasks |

---

## Golden Rules

1. **Most apps only need in-context memory** — don't over-engineer. Add complexity only when the context window is a real problem.
2. **Summarize, don't truncate** — cutting old messages loses information. Summarize them first.
3. **Store what matters** — not every word of every conversation. Extract key facts and decisions.
4. **Retrieve before generating** — pull relevant memories into context before the LLM responds.
5. **Privacy matters** — memory systems that persist user data need careful access controls and deletion capabilities.
6. **Test for hallucinated memory** — the model might "remember" things you never told it. Validate against your memory store.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Comparison.md](./Comparison.md) | Memory types comparison |

⬅️ **Prev:** [06 Semantic Search](../06_Semantic_Search/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [08 Streaming Responses](../08_Streaming_Responses/Theory.md)
