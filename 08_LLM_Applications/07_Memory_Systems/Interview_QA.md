# Memory Systems — Interview Q&A

## Beginner

**Q1: Why do LLMs not have memory by default? How does their "memory" actually work?**

<details>
<summary>💡 Show Answer</summary>

LLMs are stateless — they have no persistent state between API calls. When you call the API, you send the entire conversation each time. The model processes it fresh. When the API call ends, nothing is saved on the model's side.

The appearance of "memory" in a chat session comes entirely from the messages list you maintain in your code. You're responsible for appending each turn to the list and sending the full history with every new request. The model isn't remembering — it's reading the history you sent.

This has important implications: there's no built-in persistence across sessions. If a user closes the browser and reopens it, the conversation history is gone unless you explicitly saved and reloaded it.

</details>

---

<br>

**Q2: What happens when a conversation gets too long for the context window?**

<details>
<summary>💡 Show Answer</summary>

When the total tokens in your messages array exceeds the model's context limit (e.g., 200K for Claude, 128K for GPT-4o), one of three things happens depending on how you handle it:

(1) API error: the API rejects the request with a context length error. You need to handle this.
(2) Silent truncation: some implementations silently drop the oldest messages. The model loses early context without you knowing.
(3) Graceful handling (what you should do): detect when you're approaching the limit and either summarize old turns or selectively prune them.

The right approach: track token count (use a tokenizer library to count). When you approach ~80% of the limit, summarize the oldest half of the conversation and replace those turns with the summary.

</details>

---

<br>

**Q3: What is the difference between episodic and semantic memory in the context of AI applications?**

<details>
<summary>💡 Show Answer</summary>

These terms come from cognitive science but map well to AI systems.

Episodic memory: memory of specific events and experiences. "On Tuesday, Alex mentioned they're struggling with Python decorators." This is a specific event at a specific time. In AI systems, this is typically stored as embeddings in a vector database — retrieved by semantic similarity when relevant.

Semantic memory: general facts, knowledge, and stable attributes. "Alex is a software developer. They prefer short, direct answers. They're on the Pro plan." This is timeless knowledge about the user or world. In AI systems, this is stored in structured key-value storage or a database — retrieved by lookup.

Both types work together: episodic memory gives context about past interactions; semantic memory gives persistent facts about the user and their preferences.

</details>

---

## Intermediate

**Q4: Describe a production memory architecture for a multi-session AI assistant.**

<details>
<summary>💡 Show Answer</summary>

Three-layer architecture:

**Layer 1: Working memory (in-context)** — the current conversation's last N turns, kept in the messages array. Fast, always available, but limited.

**Layer 2: Episodic memory (vector store)** — past conversations and interactions stored as embeddings. Before each response, retrieve the top-3 most semantically relevant past memories based on the current query. Include them in the system prompt: "Relevant past context: [retrieved memories]".

**Layer 3: Semantic memory (structured DB)** — user profile, preferences, account data, learned facts. Fetched by user ID at the start of each session and kept in the system prompt throughout: "User profile: {name, preferences, history}".

On each turn: (1) retrieve relevant episodic memories, (2) include semantic profile, (3) generate response, (4) decide what's worth saving to episodic store, (5) update semantic profile if new permanent facts were stated.

</details>

---

<br>

**Q5: How does memory summarization work? When should you trigger it?**

<details>
<summary>💡 Show Answer</summary>

Memory summarization compresses old conversation turns into a dense summary, replacing them in the context. This lets you keep the most important information while freeing up context space.

Implementation:

```python
def summarize_old_turns(old_messages: list, llm_client) -> str:
    summary_prompt = f"""Summarize this conversation history into a brief paragraph.
    Focus on: key facts shared, decisions made, user preferences mentioned, and important context.

    Conversation:
    {format_messages(old_messages)}"""

    response = llm_client.messages.create(
        model="claude-opus-4-6",
        max_tokens=300,
        messages=[{"role": "user", "content": summary_prompt}]
    )
    return response.content[0].text
```

When to trigger: when total token count exceeds 70–80% of the context limit. Keep the most recent 4–6 turns as-is (recent context matters most). Summarize everything older.

The summary goes at the top of your system message or as a special message at the start of the conversation history.

</details>

---

<br>

**Q6: What is the MemGPT architecture and how does it differ from simple history management?**

<details>
<summary>💡 Show Answer</summary>

Simple history management: you decide what to remember and forget, with hardcoded rules (keep last N turns, summarize when full). Passive.

MemGPT: the LLM actively manages its own memory using tools. The model has three memory regions: main context (current working area), core memory (always-present facts), and archival storage (long-term vector store). The model can call tools to: read/write/edit core memory, search archival storage, or move content between tiers.

The LLM decides what's important enough to keep, what to archive, and what to retrieve when relevant — mimicking human memory management. Instead of your code deciding "keep the last 10 turns," the model decides "this user's medication allergy is critical and should always be in core memory."

More intelligent but more complex. Better for long-running autonomous agents and personal assistants where the content of past interactions varies wildly in importance.

</details>

---

## Advanced

**Q7: How would you implement a memory system that respects user privacy and right-to-deletion?**

<details>
<summary>💡 Show Answer</summary>

Design principles:

**Separation**: store memories separately from other user data. Memory entries should have explicit user_id tags and timestamps.

**Minimal storage**: only store what's necessary for the application's purpose. Don't log entire conversations unless required.

**Deletion pipeline**: when a user requests data deletion: (1) delete from structured DB by user_id, (2) delete all vector embeddings with user_id metadata filter, (3) delete any conversation logs. The vector DB deletion is the tricky part — most support metadata-filtered deletes.

**Access controls**: each memory retrieval should enforce that user_id A can never retrieve user_id B's memories. This must be enforced at the data layer, not just the application layer.

**Retention policy**: implement automatic expiry. Memories older than N days should be automatically purged unless marked as persistent.

**Audit log**: maintain a log of what data was stored and when, to demonstrate compliance. This log itself should be deletable.

</details>

---

<br>

**Q8: How do you prevent "hallucinated memory" — the model claiming to remember things you never told it?**

<details>
<summary>💡 Show Answer</summary>

Hallucinated memory happens when the model generates plausible-sounding "memories" that aren't in its actual memory store. The model says "I remember you mentioned last week..." but you never said that.

Prevention strategies:

(1) **Ground memory in the prompt explicitly**: only include memories that come from your retrieval system. Add: "You only remember what appears in [Memory] sections below. Do not claim to remember anything else."

(2) **Don't ask open-ended memory questions**: "What did we talk about before?" invites hallucination. Instead: retrieve relevant memories and present them: "Based on your history, here's what I know about you: [retrieved memories]."

(3) **Validate memory claims**: if the model says "You told me X", verify X appears in the stored memories before acting on it.

(4) **Use structured memory for critical facts**: medication, account details, important preferences should be in structured DB, not fuzzy vector retrieval. Exact lookup, not approximate.

</details>

---

<br>

**Q9: Compare the cost implications of in-context memory vs. vector store memory for a high-volume application.**

<details>
<summary>💡 Show Answer</summary>

In-context memory: every turn pays for all prior turns. A conversation of 50 turns with 200 tokens each = 10,000 tokens of history on turn 51. At $3/million tokens (input), that's $0.03 per turn and rising. Over a 1,000,000 message/day application with average 20-turn sessions: significant ongoing cost that grows with conversation length.

Vector store memory: pay once to embed and store. Retrieval costs per query are minimal (typically sub-millisecond, low compute). Token cost per turn is fixed: you only inject the retrieved memories (maybe 500 tokens) regardless of how long the overall history is. At 1M messages/day: flat retrieval cost, fixed context size, predictable cost.

Crossover point: for conversations under ~10 turns, in-context is simpler and cheaper. For sessions with 20+ turns or multi-session use, vector memory is more cost-efficient. Calculate your expected average conversation length and cost per 1M tokens to find your specific break-even point.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Comparison.md](./Comparison.md) | Memory types comparison |

⬅️ **Prev:** [06 Semantic Search](../06_Semantic_Search/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [08 Streaming Responses](../08_Streaming_Responses/Theory.md)
