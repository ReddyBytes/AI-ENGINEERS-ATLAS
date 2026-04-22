# Simple Agent — Cheatsheet

## Minimal Working Agent

```python
from claude_agent_sdk import Agent, tool

@tool
def my_tool(param: str) -> str:
    """Description of what this tool does and when Claude should use it."""
    return some_function(param)

agent = Agent(
    model="claude-sonnet-4-6",
    tools=[my_tool],
    system="You are a [role]. [What the agent should do and how.]"
)

result = agent.run("User's goal or question")
print(result)
```

---

## The `@tool` Decorator — What It Does

| Input | Output |
|---|---|
| Function name | `"name": "function_name"` |
| Docstring | `"description": "..."` |
| `param: str` type hint | `{"param": {"type": "string"}}` |
| `param: int = 5` default | `{"required": []}` (optional) |

---

## Tool Function Best Practices

```python
# Good @tool design
@tool
def search_products(
    query: str,
    category: str = "all",
    max_results: int = 10
) -> list[dict]:
    """Search the product catalog by keyword.
    Returns products with name, price, and stock status.
    Category filters to: electronics, clothing, books, or 'all'.
    Use this when the user asks about product availability or pricing."""
    return db.search_products(query, category, max_results)
```

Rules:
1. Docstring explains WHEN to use, what it RETURNS, and CONSTRAINTS
2. Type hints on all parameters
3. Sensible defaults for optional params
4. Return clean structured data (dict/list preferred over raw text)

---

## Agent Creation Options

```python
agent = Agent(
    model="claude-sonnet-4-6",   # model ID
    tools=[tool1, tool2],         # list of @tool functions
    system="...",                 # system prompt
    max_tokens=4096,              # max tokens per response
    max_steps=20,                 # max loop iterations
    temperature=0.0               # 0 = deterministic
)
```

---

## Running an Agent

```python
# Synchronous (blocking)
result = agent.run("Your goal")

# With metadata
result = agent.run(
    "Your goal",
    context={"user_id": "123", "session_id": "abc"}
)

# Inspect what happened
print(result)                    # Final answer text
print(agent.last_run.steps)      # All steps taken
print(agent.last_run.tool_calls) # All tool calls made
```

---

## Debugging a Simple Agent

When something goes wrong:
1. Check the tool docstring — is it clear enough for Claude to know when to use it?
2. Check the tool is in `tools=[...]` — defining `@tool` doesn't auto-register it
3. Check the system prompt — does it tell the agent to use tools when needed?
4. Add `on_step=print` to log every loop iteration
5. Check if the goal is achievable with the tools you provided

---

## Common Patterns

```python
# Pattern: Agent with error handling
try:
    result = agent.run(user_goal)
except AgentMaxStepsError:
    result = "Goal too complex — try breaking it into smaller parts"
except AgentError as e:
    result = f"Agent error: {str(e)}"

# Pattern: Agent with logging
def log_step(step: AgentStep):
    print(f"Step {step.number}: {step.tool_call or 'final answer'}")

agent = Agent(..., on_step=log_step)
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Complete working code |

⬅️ **Prev:** [Why Agent SDK?](../02_Why_Agent_SDK/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Tool Calling in Agents](../04_Tool_Calling_in_Agents/Theory.md)
