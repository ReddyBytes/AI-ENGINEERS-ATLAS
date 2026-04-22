# Agent Memory — Cheatsheet

## Memory Types at a Glance

| Type | Location | Scope | Speed | Limit |
|---|---|---|---|---|
| **In-context** | Context window | Session only | Instant | ~200K tokens |
| **External (vector DB)** | Database | Persistent | Retrieval latency | Storage |
| **Session state** | KV store / file | Session or persistent | Fast lookup | Storage |
| **Episodic log** | Append-only store | Persistent | Query latency | Storage |

---

## In-Context Memory Pattern

```python
# It's just the conversation history
messages = [
    {"role": "user", "content": "My name is Alice"},
    {"role": "assistant", "content": "Hi Alice!"},
    # Everything above is "in-context memory"
    {"role": "user", "content": "What's my name?"}
    # Claude can answer: "Your name is Alice"
]
```

Limit: fills up over long sessions. Must compress or offload.

---

## External Memory Tools

```python
@tool
def save_to_memory(content: str, tags: list[str] = None) -> str:
    """Save important information to long-term memory for future sessions.
    Use for: user preferences, decisions made, facts to remember.
    Tags help with retrieval. Returns confirmation."""
    vector_db.upsert(embed(content), content, tags=tags or [])
    return "Saved to memory."

@tool
def recall_from_memory(query: str, limit: int = 5) -> list[str]:
    """Search long-term memory for information relevant to the query.
    Use at session start or when you need to remember something.
    Returns most semantically similar stored memories."""
    results = vector_db.search(embed(query), top_k=limit)
    return [r.text for r in results]
```

---

## Session State Pattern

```python
# Load at session start
state = load_state(user_id)  # {"preferences": {...}, "history": [...]}

# Pass to agent via system prompt
agent = Agent(
    system=f"""You are assisting {state['name']}.
    Their preferences: {json.dumps(state['preferences'])}
    Last session summary: {state.get('last_summary', 'No previous sessions')}"""
)

# Save at session end
state['last_summary'] = agent.last_run.final_answer
save_state(user_id, state)
```

---

## Context Compression Pattern

```python
# When context is growing large, compress
@tool
def compress_and_save(step_summaries: list[str]) -> str:
    """Compress intermediate findings and save them externally.
    Call this after every 5 steps to prevent context overflow."""
    summary = "\n".join(step_summaries)
    external_store.write(session_id, summary)
    return "Compressed. Use recall_step_data() to retrieve if needed."
```

---

## Memory Decision Tree

```
Does the agent need to remember this?
├── Within this session only → In-context (do nothing)
├── Across sessions, semantic search needed → Vector DB
├── Across sessions, exact lookup needed → KV store / session state
├── For audit trail only → Append log
└── Too big for context but needed this session → External store + reference
```

---

## System Prompt for Memory Use

```python
system = """At the start of each conversation:
1. Call recall_from_memory("user preferences and history") 
2. Use the results to personalize your responses

During the conversation:
- Save important decisions or facts with save_to_memory()
- Don't save trivial information

At task completion:
- Save a brief summary of what was accomplished"""
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |

⬅️ **Prev:** [Multi-Step Reasoning](../05_Multi_Step_Reasoning/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Multi-Agent Orchestration](../07_Multi_Agent_Orchestration/Theory.md)
