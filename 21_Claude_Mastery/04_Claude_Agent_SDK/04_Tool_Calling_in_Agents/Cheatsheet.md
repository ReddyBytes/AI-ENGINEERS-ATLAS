# Tool Calling in Agents — Cheatsheet

## Tool Call Lifecycle (Quick Reference)

```
1. Claude produces tool_use block → { name, id, input }
2. SDK dispatches → find function by name in tool registry
3. SDK executes → function(input) → result or exception
4. SDK formats → tool_result { tool_use_id, content }
5. SDK injects → appends to message context
6. Claude continues → sees result, decides next action
```

---

## Tool Schema Anatomy

```python
@tool
def tool_name(
    required_param: str,          # required (no default)
    optional_param: int = 10,     # optional (has default)
    another: list[str] = None     # optional list
) -> dict:                        # return type hint
    """One-line summary of what this does.
    
    When to use: describe the use case.
    Returns: describe the return value structure.
    Constraints: limits, error conditions, side effects."""
    ...
```

Generated schema:
```json
{
  "name": "tool_name",
  "description": "...",
  "input_schema": {
    "type": "object",
    "properties": {
      "required_param": {"type": "string"},
      "optional_param": {"type": "integer"},
      "another": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["required_param"]
  }
}
```

---

## Automatic vs Manual Execution

```python
# Automatic (default) — SDK executes immediately
agent = Agent(model=..., tools=[...])

# Manual — approve before execution
def before_tool(name: str, input: dict) -> bool:
    if name in DANGEROUS_TOOLS:
        return ask_human(f"Allow {name}({input})?")
    return True

agent = Agent(model=..., tools=[...], before_tool=before_tool)
```

---

## Error Recovery Flow

```
Tool raises Exception
    → SDK catches it
    → Formats as tool_result with error field
    → Claude sees: "Tool failed: <error message>"
    → Claude can: retry / use different tool / report to user
```

---

## Tool Output Best Practices

| Return | Use When |
|---|---|
| `str` | Messages, status text, prose |
| `dict` | Single structured record |
| `list[dict]` | Multiple records |
| `int / float` | Numeric results |
| `bool` | Pass/fail signals |

Avoid: raw HTML, binary data, deeply nested objects, untruncated large files.

Cap output size — a tool returning 50KB floods the context.

---

## Retry Pattern for Transient Errors

```python
import time
from functools import wraps

def with_retry(attempts=3):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            for i in range(attempts):
                try:
                    return fn(*args, **kwargs)
                except (TimeoutError, ConnectionError) as e:
                    if i == attempts - 1:
                        raise
                    time.sleep(2 ** i)
        return wrapper
    return decorator

@tool
@with_retry(attempts=3)
def fetch_data(url: str) -> dict:
    """Fetch JSON from a URL. Retries on network errors."""
    return requests.get(url, timeout=10).json()
```

---

## Bad vs Good Docstrings

```python
# BAD — vague, no guidance
@tool
def search(q: str) -> list:
    """Search for stuff."""

# GOOD — specific, actionable, constrained
@tool
def search_knowledge_base(
    query: str,
    max_results: int = 5
) -> list[dict]:
    """Search the internal knowledge base for relevant articles.
    Returns articles with fields: title, summary, url, relevance_score.
    Use when the user asks about company policies, procedures, or products.
    Returns empty list if no articles match. Max 20 results per call."""
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Tool patterns in code |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | Tool call internals |

⬅️ **Prev:** [Simple Agent](../03_Simple_Agent/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Multi-Step Reasoning](../05_Multi_Step_Reasoning/Theory.md)
