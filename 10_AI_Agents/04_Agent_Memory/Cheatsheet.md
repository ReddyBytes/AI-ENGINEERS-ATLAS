# Agent Memory — Cheatsheet

**One-liner:** Agent memory is how agents track what has happened — in-context keeps the full conversation, summarization compresses it, entity memory tracks specific facts, and vector memory stores knowledge across sessions.

---

## Key Terms

| Term | What it means |
|---|---|
| **In-context memory** | Stores the full conversation history in the prompt — fast, but limited by context window size |
| **ConversationBufferMemory** | LangChain's simplest memory — keeps all messages in the prompt |
| **Summarization memory** | Condenses older conversation turns into a summary — covers more, loses detail |
| **ConversationSummaryMemory** | LangChain memory that uses an LLM to summarize older turns |
| **Entity memory** | Tracks specific named entities (people, places, things) and facts about them |
| **Vector memory** | Stores information in a vector database — retrieved via semantic search across sessions |
| **Context window** | The maximum amount of text an LLM can process in one call — the hard limit for in-context memory |
| **Memory retrieval** | The process of fetching relevant memories before each agent response |
| **Episodic memory** | Memory of specific past events — implemented via vector store + timestamps |
| **Working memory** | What the agent is actively using right now — essentially what's in context |

---

## Memory Types Quick Comparison

| Type | Storage | Capacity | Retrieval | Persists across sessions? |
|---|---|---|---|---|
| In-context | In the prompt | Context window limit | Instant (already in prompt) | No |
| Summarization | Compressed summary in prompt | Much more than in-context | Instant (already in prompt) | No (unless saved) |
| Entity | Structured facts in prompt | Dozens of entities | Instant (already in prompt) | Yes (if persisted) |
| Vector | External database | Unlimited | Semantic search (slower) | Yes |

---

## LangChain Memory Classes (Quick Reference)

```python
from langchain.memory import ConversationBufferMemory      # Full history
from langchain.memory import ConversationSummaryMemory     # Summarized history
from langchain.memory import ConversationBufferWindowMemory # Last N turns only
from langchain.memory import ConversationEntityMemory      # Track entities
from langchain.memory import VectorStoreRetrieverMemory    # Semantic retrieval
```

---

## When to Use Each Type

**Use ConversationBufferMemory when:**
- Short conversations (under ~20 turns)
- You need the exact wording of previous messages
- Simplicity matters more than scale

**Use ConversationSummaryMemory when:**
- Long conversations (20+ turns)
- Exact wording doesn't matter, just the gist
- Budget/token cost is a concern

**Use Entity Memory when:**
- Conversation tracks specific people, projects, tasks
- You want the agent to "know" persistent facts about named things

**Use Vector Memory when:**
- You need memory across many sessions
- The user base is large (one store per user)
- Relevant context from the past needs to be retrieved selectively

---

## Golden Rules

1. **Start with ConversationBufferMemory.** It's the simplest and works well for most use cases under 20 turns.

2. **Switch to SummaryMemory as conversations grow.** Watch your token usage — a long buffer is expensive.

3. **Entity memory shines for personal assistants.** Any agent that needs to "know" about specific people or projects.

4. **Vector memory is the long game.** Use it when you want the agent to remember across many conversations.

5. **Memory without relevance filtering is noise.** Don't dump 10,000 past messages into context. Retrieve only what's relevant.

6. **Always test memory with long conversations.** Memory bugs often only appear after many turns.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |
| [📄 Comparison.md](./Comparison.md) | Memory types comparison |

⬅️ **Prev:** [03 Tool Use](../03_Tool_Use/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 Planning and Reasoning](../05_Planning_and_Reasoning/Theory.md)
