# System Prompts — Cheatsheet

## Basic Usage

```python
client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    system="You are a helpful assistant.",   # ← system prompt here
    messages=[{"role": "user", "content": "Hello!"}]
)
```

---

## System vs User: When to Use Each

| What you want | Where to put it |
|---|---|
| Persona / role | `system` |
| Output format rules | `system` |
| Domain restrictions | `system` |
| Tone / language style | `system` |
| Actual user question | `messages[role=user]` |
| Conversation context | `messages` array |

---

## Common System Prompt Patterns

### Persona
```python
system = "You are Maya, a friendly support agent for AcmeCo. Be concise and helpful."
```

### Output format
```python
system = "Respond only with valid JSON. No prose, no markdown. Schema: {answer: str, confidence: float}"
```

### Domain restriction
```python
system = "You only answer questions about Python programming. Redirect all other topics."
```

### Tone + length
```python
system = "Use plain language (8th grade reading level). Keep responses under 150 words."
```

### Role in a pipeline
```python
system = "You are a data extraction engine. Extract fields as JSON. Return null for missing fields."
```

---

## XML Structure for Long Prompts

```python
system = """
<role>
You are a customer service agent for TechBank.
</role>

<rules>
- Never share account balances
- Always verify customer identity before account topics
- Escalate fraud to supervisor immediately
</rules>

<tone>
Professional, calm, empathetic
</tone>
"""
```

---

## System + Prompt Caching

```python
# Cache the system prompt (saves 90% on repeat calls)
client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    system=[
        {
            "type": "text",
            "text": long_system_prompt,
            "cache_control": {"type": "ephemeral"}
        }
    ],
    messages=[{"role": "user", "content": user_input}]
)
```

---

## Key Rules

- `system` is a top-level parameter — NOT inside `messages`
- No `role` field needed — it's automatically treated as system
- Applies to every turn in the conversation
- Higher priority than user messages
- Can be a string or an array of content blocks (for caching)

---

## Common Mistakes

| Mistake | Fix |
|---|---|
| Putting system in messages | Use `system=` parameter, not `messages[role=system]` |
| Vague instructions | Be specific: "respond in 3 bullet points" not "be concise" |
| Contradictory rules | Resolve conflicts — one rule wins, state which |
| Trusting system prompt as hard constraint | Add output validation for safety-critical rules |

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept guide |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Working code |

⬅️ **Prev:** [First API Call](../03_First_API_Call/Cheatsheet.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Tool Use](../05_Tool_Use/Cheatsheet.md)
