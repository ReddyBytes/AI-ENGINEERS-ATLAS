# Raw API vs Agent SDK — Full Comparison

## Side-by-Side Feature Comparison

| Feature | Raw Messages API | Agent SDK |
|---|---|---|
| **Agent loop** | Write yourself (while True) | Built-in |
| **Tool dispatch** | Write dispatcher (match tool name → function) | Automatic via `@tool` |
| **Tool schema generation** | Write JSON schema manually | Automatic from type hints + docstring |
| **Context management** | Manage messages list yourself | Automatic |
| **Tool result formatting** | Format `tool_result` blocks manually | Automatic |
| **Error recovery** | Catch exceptions, format error results | Automatic — errors returned to model |
| **Stop condition handling** | Check `stop_reason` manually | Automatic |
| **Streaming** | Wire up SSE stream manually | `agent.stream()` or `on_step` callback |
| **Subagent spawning** | Instantiate Agent SDK inside raw code | `Agent` class with parent context |
| **Max steps enforcement** | Write your own counter | `max_steps=N` parameter |
| **Human-in-the-loop** | Add check at each tool dispatch point | `before_tool` callback |
| **Step logging** | Instrument each loop iteration | `on_step` callback |

---

## Code Volume Comparison

Same agent (web research with one tool):

```python
# ====== RAW API — ~50 lines ======
import anthropic
import json

client = anthropic.Anthropic()

def web_search(query: str) -> list[dict]:
    # ... your search implementation

tool_schema = {
    "name": "web_search",
    "description": "Search the web for information.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"}
        },
        "required": ["query"]
    }
}

def run_agent(goal: str) -> str:
    messages = [{"role": "user", "content": goal}]
    step = 0
    
    while step < 20:
        step += 1
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            tools=[tool_schema],
            messages=messages
        )
        
        if response.stop_reason == "end_turn":
            text_blocks = [b for b in response.content if b.type == "text"]
            return text_blocks[0].text if text_blocks else ""
        
        tool_calls = [b for b in response.content if b.type == "tool_use"]
        if not tool_calls:
            text_blocks = [b for b in response.content if b.type == "text"]
            return text_blocks[0].text if text_blocks else ""
        
        messages.append({"role": "assistant", "content": response.content})
        
        tool_results = []
        for tc in tool_calls:
            try:
                if tc.name == "web_search":
                    result = web_search(**tc.input)
                else:
                    result = f"Unknown tool: {tc.name}"
                content = json.dumps(result)
            except Exception as e:
                content = f"Error: {str(e)}"
            
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tc.id,
                "content": content
            })
        
        messages.append({"role": "user", "content": tool_results})
    
    return "Max steps reached"

# ====== AGENT SDK — ~15 lines ======
from claude_agent_sdk import Agent, tool

@tool
def web_search(query: str) -> list[dict]:
    """Search the web for information. Returns title, url, snippet."""
    # ... your search implementation

agent = Agent(
    model="claude-sonnet-4-6",
    tools=[web_search],
    system="You are a research assistant.",
    max_steps=20
)

result = agent.run(goal)
```

---

## When Each is Right

### Use Raw API When...

**Single message/response (most common case)**
```python
# No loop needed — this is 90% of LLM use cases
response = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Translate this to Spanish: Hello world"}]
)
```

**Custom loop logic**
```python
# You have a game loop, stateful simulation, or non-standard flow
while game.running:
    state = game.get_state()
    action = client.messages.create(...)  # one call per game step
    game.apply(action)
```

**Framework integration**
```python
# LangGraph, LangChain, or another framework manages the loop
# They call the raw API internally
workflow = StateGraph(...)
workflow.add_node("think", call_claude)  # raw API call inside the node
```

**Ultra-fine control**
```python
# Specific token budgets, custom stop sequences, unusual content structures
response = client.messages.create(
    max_tokens=50,
    stop_sequences=["<DONE>"],
    messages=[...],
    metadata={"user_id": "..."}
)
```

### Use Agent SDK When...

**Any multi-step agent with tools** — this is the entire purpose of the SDK.

**Subagent spawning** — built-in support for spawning and coordinating child agents.

**Rapid prototyping** — go from idea to running agent in minutes, not hours.

**Teams** — standardizes the agent pattern across your codebase.

---

## Performance Characteristics

| Metric | Raw API | Agent SDK |
|---|---|---|
| **Overhead per call** | Zero | Minimal (~1-5ms for dispatch/format) |
| **Token usage** | Identical (same API) | Identical |
| **Latency** | Network RTT only | Network RTT + dispatch overhead (negligible) |
| **Memory** | Your list | SDK-managed list (same content) |
| **Concurrency** | You manage | `asyncio.gather()` with `arun()` |

The performance difference is negligible. Choose based on code quality, not performance.

---

## Migration Path

If you've already written a manual loop and want to migrate to the SDK:

1. Keep your tool functions as-is, add `@tool` decorator
2. Replace your tool schema dict with the type hints + docstring approach
3. Delete your `while True` loop, dispatch function, message management
4. Replace with `Agent(model=..., tools=[...], system=...).run(goal)`
5. Keep your `before_tool` logic in the SDK's `before_tool` callback

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Comparison.md** | ← you are here |

⬅️ **Prev:** [What Are Agents?](../01_What_are_Agents/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Simple Agent](../03_Simple_Agent/Theory.md)
