# Memory Systems — Comparison

Choosing the right memory approach for your application.

---

## Side-by-Side Comparison

| Property | In-Context Memory | Vector-Based Memory | Structured Memory |
|----------|------------------|---------------------|-------------------|
| **What it stores** | Full conversation turns | Embeddings of past conversations/events | Explicit facts, user profile |
| **Storage location** | Messages array in code | Vector database (Chroma, Pinecone, etc.) | SQL/NoSQL database |
| **Capacity** | Limited by context window | Virtually unlimited | Virtually unlimited |
| **Retrieval** | Always available (full history) | Semantic similarity search (top-K) | Exact key lookup |
| **Retrieval quality** | Exact — everything is there | Good — retrieves most relevant (~90–95% recall) | Perfect — exact data |
| **Cost per turn** | Grows linearly with conversation length | Fixed (embedding cost once, retrieval cheap) | Very low (DB query) |
| **Setup complexity** | None (just maintain a list) | Medium (needs vector DB + embedding model) | Low to medium |
| **Persistence** | Not persistent across sessions | Persistent with vector DB | Persistent with DB |
| **Best for** | Single sessions, short conversations | Recalling past conversations and events | User preferences, facts, profile |
| **Fails when** | Conversation exceeds context limit | Memory is very precise/exact data | Data is unstructured or event-based |

---

## When to Use Each

### In-Context Only
```
Simple chatbot or assistant for single sessions
The entire conversation fits within budget and context limits
No need to remember across separate sessions
Quick prototype or demo
```

### In-Context + Vector Memory
```
Multi-session personal assistant
Customer support agent that remembers past tickets
AI coach that builds on previous lessons
Any app where "remember what we discussed last Tuesday" matters
```

### In-Context + Structured Memory
```
User has a profile with preferences and settings
Account data needs to be referenced (plan type, permissions)
Specific facts about the user are important (name, role, location)
```

### All Three Combined (Production Assistant)
```
System message: [structured profile — user name, prefs, account]
Retrieved context: [top-3 most relevant past memories from vector store]
Recent history: [last 5 turns of current conversation]
Current turn: [new user message]
```

---

## Cost Comparison at Scale

Assume: 1,000,000 messages per day. Average 20-turn conversation. 150 tokens per turn.

| Memory Type | Token overhead per message | Daily input tokens | Daily cost (at $3/M tokens) |
|-------------|---------------------------|--------------------|-----------------------------|
| In-context (all 20 turns) | 3,000 tokens avg | 3B tokens | ~$9,000 |
| Summarization (last 5 + summary) | 1,000 tokens avg | 1B tokens | ~$3,000 |
| Vector memory (retrieved chunks) | 500 tokens avg | 500M tokens | ~$1,500 |
| Structured only (profile) | 200 tokens avg | 200M tokens | ~$600 |

These are rough estimates. Real costs depend on model, token counts, and retrieval overhead. The principle holds: as conversations grow longer, vector and structured memory become dramatically more cost-efficient.

---

## Decision Flowchart

```
Does your app need to remember across sessions?
├── No → In-context only (keep the messages list)
└── Yes → What kind of memory?
    ├── Past conversations and events → Vector store memory
    ├── User preferences and facts → Structured DB memory
    └── Both → Combine all three layers
```

---

## Common Patterns

**Pattern 1: Simple Session Memory**
```python
messages = []  # Start fresh each session
# Append turns, send full list each time
# Clear when done
```

**Pattern 2: Summarizing Memory**
```python
if token_count(messages) > 80_000:
    summary = summarize(messages[:-6])  # Summarize all but last 6
    messages = [{"role": "system", "content": f"Previous summary: {summary}"}] + messages[-6:]
```

**Pattern 3: Vector Memory**
```python
# Before each response:
relevant_past = vector_db.query(current_message, top_k=3)
system = f"Relevant past context:\n{format(relevant_past)}\n\nUser profile: {user_profile}"

# After each response:
vector_db.add(current_turn, metadata={"user_id": user_id, "timestamp": now()})
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Comparison.md** | ← you are here |

⬅️ **Prev:** [06 Semantic Search](../06_Semantic_Search/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [08 Streaming Responses](../08_Streaming_Responses/Theory.md)
