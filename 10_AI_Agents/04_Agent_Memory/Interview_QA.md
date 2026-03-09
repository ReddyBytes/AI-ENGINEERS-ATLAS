# Agent Memory — Interview Q&A

## Beginner

**Q1: Why does an AI agent need memory?**

Without memory, every response is completely disconnected from everything that came before.

Ask an agent "I'm planning a trip to Japan" — then ask "What should I pack?" — without memory, it has no idea what you're packing for.

Memory lets agents maintain context within a conversation and across conversations. It's what transforms a stateless question-answerer into something that feels like a persistent, helpful assistant.

---

**Q2: What is in-context memory and what are its limitations?**

In-context memory is the simplest approach: the full conversation history is included directly in the prompt on every API call.

```
[System prompt]
User: My name is Sarah
Assistant: Nice to meet you, Sarah!
User: I'm working on a Django project
Assistant: Great! What do you need help with?
User: [current message]  ← Agent can see all previous turns
```

Limitations:
1. **Context window limit** — LLMs can only process a certain amount of text at once (e.g., 128K tokens for GPT-4). Long conversations hit this limit.
2. **Cost** — every message re-sends all previous messages. A 100-turn conversation means turn 100 sends 100 messages worth of tokens.
3. **Relevance** — older, less relevant messages dilute the context. The agent might focus on something from 50 turns ago that no longer matters.

---

**Q3: What is the difference between ConversationBufferMemory and ConversationSummaryMemory?**

**ConversationBufferMemory** keeps every message verbatim. Turn 1, turn 2, turn 3... all stored and included in every new prompt.

**ConversationSummaryMemory** uses an LLM to periodically summarize older parts of the conversation. Instead of keeping 50 raw messages, it keeps one compressed paragraph: "User is planning a trip to Japan in June, budget is $3000, interested in Tokyo and Kyoto."

Buffer: exact but expensive over time.
Summary: approximate but handles long conversations much better.

Use buffer for short conversations. Use summary when conversations run long.

---

## Intermediate

**Q4: How does vector-based long-term memory work?**

Vector memory stores information as **numerical embeddings** in a database outside the LLM.

Here's the process:

1. **Storage**: When a conversation ends, key information is embedded (converted to a vector of numbers) and saved in the database with metadata.

2. **Retrieval**: At the start of a new conversation, the agent's current context is embedded and compared to stored memories using cosine similarity.

3. **Injection**: The most similar (relevant) memories are retrieved and added to the prompt.

This allows the agent to have memories that persist forever across any number of sessions. The key advantage over buffer memory: you don't need to fit all memories into the context window. You only retrieve the relevant ones.

---

**Q5: What is entity memory and when is it useful?**

Entity memory tracks specific named things (people, places, organizations, objects) and facts about them.

As the conversation progresses, the system extracts and updates facts:

```
Tracked entities:
- Sarah: senior developer, works on Django, deadline March 15, prefers dark mode
- Project "Phoenix": web app, uses React frontend, has auth bug on login page
- Bug #142: authentication error, affects 10% of users, high priority
```

This is especially useful for:
- Personal assistants that track tasks and people
- Customer service bots that need to know account details
- Coding assistants that track project-specific context

When Sarah says "how's the deadline looking?", entity memory tells the agent she means March 15 for Project Phoenix.

---

**Q6: How do you handle memory when the conversation gets very long?**

Several strategies:

1. **Sliding window** — only keep the last N turns. Drop older messages.
   ```python
   ConversationBufferWindowMemory(k=10)  # Keep last 10 turns
   ```

2. **Summarization** — summarize older turns, keep recent ones verbatim.
   ```python
   ConversationSummaryBufferMemory(max_token_limit=1000)
   ```

3. **Selective retrieval** — store old turns in a vector database, retrieve only the relevant ones.

4. **Hierarchical compression** — summarize in stages: recent messages verbatim → last hour as summary → last day as brief recap.

In production, most systems use a combination: a short buffer for recent context, a summary for the session, and a vector store for long-term facts.

---

## Advanced

**Q7: How would you design a memory system for a personal assistant that serves 100,000 users?**

Key design requirements:

1. **Isolation**: each user needs their own memory store. Memories can't leak between users.

2. **Scalability**: 100K users with potentially thousands of memories each = vector database with proper indexing.

3. **Privacy/retention**: users can request deletion of their memories (GDPR, etc.)

Architecture:
- Vector database (Pinecone, Qdrant) with user_id as a metadata filter
- Each memory tagged with: user_id, timestamp, conversation_id, topic
- On every new conversation: retrieve top-5 most relevant past memories for that user
- Periodic memory consolidation: compress old memories, remove duplicates

```python
def get_user_memories(user_id: str, query: str) -> list:
    # Retrieve only this user's memories
    results = vector_store.similarity_search(
        query=query,
        filter={"user_id": user_id},
        k=5  # Top 5 most relevant
    )
    return results
```

---

**Q8: What are the tradeoffs between storing raw conversations vs. summarized memories in a vector store?**

**Raw conversations:**
- Pros: exact wording preserved, can search by specific phrases, no information loss
- Cons: much larger storage, retrieval returns long chunks, costs more to embed and store

**Summarized memories:**
- Pros: compact, each memory chunk is focused and meaningful, retrieval is more precise
- Cons: summarization can lose important details, requires an extra LLM call to create summaries

**Best practice**: a hybrid approach.
- Store the raw conversation for audit/compliance purposes
- Embed summarized versions for retrieval
- Index by multiple dimensions: semantic similarity, timestamp, user, topic

The summary becomes the retrieval unit; the raw text is the source of truth if you need exact details.

---

**Q9: What is the "lost in the middle" problem and how does memory design address it?**

Research has shown that LLMs have a recency and primacy bias — they pay more attention to information at the very beginning and very end of the context window, and less attention to information in the middle.

This means if you have a 20,000 token conversation history and a critical fact is in the middle, the agent may effectively ignore it.

Memory design solutions:
1. **Summarization** — instead of a long raw history, have a short sharp summary that keeps key facts near the top of context
2. **Selective retrieval** — only inject the most relevant memories, keeping context short and focused
3. **Structured context** — put the most important facts in a structured block at the top of the prompt, separate from conversation history
4. **Memory highlighting** — explicitly flag critical facts: "IMPORTANT: user's deadline is March 15"

Good memory design isn't just about storing information — it's about placing it where the LLM will actually pay attention to it.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |
| [📄 Comparison.md](./Comparison.md) | Memory types comparison |

⬅️ **Prev:** [03 Tool Use](../03_Tool_Use/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 Planning and Reasoning](../05_Planning_and_Reasoning/Theory.md)
