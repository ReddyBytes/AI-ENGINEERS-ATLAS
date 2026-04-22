# Why Agent SDK? — Cheatsheet

## What the SDK Does For You

| Raw API (You Write) | Agent SDK (Pre-Built) |
|---|---|
| Message history management | ✅ Automatic |
| `while True` loop | ✅ Automatic |
| Extract `tool_use` blocks | ✅ Automatic |
| Dispatch to Python function | ✅ `@tool` decorator |
| Format `tool_result` messages | ✅ Automatic |
| Error recovery | ✅ Errors returned to model |
| Max steps / limits | ✅ Configurable |
| Streaming | ✅ Built-in |

---

## Minimal SDK Pattern

```python
from claude_agent_sdk import Agent, tool

@tool
def my_tool(param: str) -> str:
    """What this tool does and when to use it."""
    return do_the_thing(param)

agent = Agent(
    model="claude-sonnet-4-6",
    tools=[my_tool],
    system="You are a [role]. Use tools to [purpose]."
)

result = agent.run("User's goal here")
```

---

## When to Use What

| Scenario | Use |
|---|---|
| Single question, no tools | `client.messages.create()` |
| Single question + one tool call | `client.messages.create()` |
| Multi-step agent with tools | `Agent SDK` |
| Custom loop logic (game, stateful) | Raw API, write your own loop |
| Subagents needed | `Agent SDK` |
| LangGraph integration | LangGraph (wraps raw API) |

---

## SDK vs Raw API — Code Comparison

```python
# Raw API — 30+ lines for the same agent
client = anthropic.Anthropic()
messages = []
while True:
    response = client.messages.create(model=..., tools=..., messages=messages)
    if response.stop_reason == "end_turn": break
    tool_calls = [b for b in response.content if b.type == "tool_use"]
    if not tool_calls: break
    messages.append({"role": "assistant", "content": response.content})
    results = [{"type": "tool_result", "tool_use_id": tc.id,
                "content": str(run_tool(tc.name, tc.input))} for tc in tool_calls]
    messages.append({"role": "user", "content": results})

# Agent SDK — 10 lines
agent = Agent(model="claude-sonnet-4-6", tools=[...], system="...")
result = agent.run(goal)
```

---

## Key Agent Config Options

| Option | Purpose | Default |
|---|---|---|
| `model` | Which Claude to use | Required |
| `tools` | List of `@tool` functions | `[]` |
| `system` | Agent system prompt | `""` |
| `max_steps` | Max loop iterations | 20 |
| `before_tool` | Approval callback | None |
| `on_step` | Logging/streaming callback | None |

---

## Golden Rules

1. SDK for agents, raw API for single calls
2. The SDK handles the loop — you handle the tools
3. Docstrings on `@tool` functions are part of your design
4. You can always drop to raw API inside a tool function
5. SDK doesn't replace prompt engineering — you still write system prompts

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Comparison.md](./Comparison.md) | Raw API vs SDK full table |

⬅️ **Prev:** [What Are Agents?](../01_What_are_Agents/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Simple Agent](../03_Simple_Agent/Theory.md)
