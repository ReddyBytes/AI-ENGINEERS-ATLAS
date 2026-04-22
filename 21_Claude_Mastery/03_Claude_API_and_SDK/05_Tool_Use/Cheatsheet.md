# Tool Use — Cheatsheet

## Tool Definition Schema

```python
tool = {
    "name": "function_name",           # snake_case, no spaces
    "description": "When to use this and what it returns.",
    "input_schema": {
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",      # string | integer | number | boolean | array | object
                "description": "What this param is"
            },
            "param2": {
                "type": "integer",
                "description": "Optional param"
            }
        },
        "required": ["param1"]         # list required params
    }
}
```

---

## Tool Use Flow

```
1. Send:  messages + tools=[ tool defs ]
2. Check: response.stop_reason == "tool_use"
3. Get:   tool_use block → name, input, id
4. Run:   your_function(**block.input)
5. Send:  assistant(tool_use) + user(tool_result)
6. Repeat until stop_reason == "end_turn"
```

---

## Detect Tool Call

```python
if response.stop_reason == "tool_use":
    for block in response.content:
        if block.type == "tool_use":
            name = block.name        # which function to call
            args = block.input       # dict of arguments
            call_id = block.id       # "toolu_01..."
```

---

## Return Tool Result

```python
# Append to messages:
messages.append({"role": "assistant", "content": response.content})
messages.append({
    "role": "user",
    "content": [
        {
            "type": "tool_result",
            "tool_use_id": call_id,     # must match tool_use.id
            "content": str(result)      # result as string
        }
    ]
})
```

---

## Tool Choice Options

```python
tool_choice={"type": "auto"}              # Claude decides (default)
tool_choice={"type": "any"}               # must use some tool
tool_choice={"type": "tool", "name": "X"} # must use tool X
tool_choice={"type": "none"}              # don't use any tools
```

---

## Parallel Tool Results (same user message)

```python
# Claude returns 2 tool_use blocks → execute both → return in same user message
{
  "role": "user",
  "content": [
    {"type": "tool_result", "tool_use_id": "toolu_01", "content": "..."},
    {"type": "tool_result", "tool_use_id": "toolu_02", "content": "..."},
  ]
}
```

---

## Error in Tool Result

```python
{
    "type": "tool_result",
    "tool_use_id": call_id,
    "content": "Error: database timeout after 30s",
    "is_error": True
}
```

---

## Minimal Tool Loop

```python
def tool_loop(user_msg, tools, executor):
    messages = [{"role": "user", "content": user_msg}]
    for _ in range(10):  # max iterations guard
        resp = client.messages.create(
            model="claude-sonnet-4-6", max_tokens=4096,
            tools=tools, messages=messages
        )
        if resp.stop_reason == "end_turn":
            return resp.content[0].text
        messages.append({"role": "assistant", "content": resp.content})
        results = []
        for b in resp.content:
            if b.type == "tool_use":
                out = executor[b.name](**b.input)
                results.append({"type":"tool_result","tool_use_id":b.id,"content":str(out)})
        messages.append({"role": "user", "content": results})
    return "Max iterations reached"
```

---

## Golden Rules

1. Always check `stop_reason == "tool_use"` before assuming text response
2. Preserve the full `response.content` array (including text blocks) when appending to history
3. Return error strings via `tool_result` — never crash your application
4. Match `tool_use_id` exactly in `tool_result`
5. Add max-iteration guard to prevent infinite loops

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept guide |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | Full architecture |
| [📄 Code_Example.md](./Code_Example.md) | Working code |

⬅️ **Prev:** [System Prompts](../04_System_Prompts/Cheatsheet.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Streaming](../06_Streaming/Cheatsheet.md)
