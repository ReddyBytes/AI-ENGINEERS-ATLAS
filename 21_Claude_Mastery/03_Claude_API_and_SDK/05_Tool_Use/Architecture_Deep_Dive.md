# Tool Use — Architecture Deep Dive

## The Full Tool Use Protocol

Tool use in the Anthropic API follows a precise multi-turn protocol. Understanding the exact message structure at each step is essential for building reliable agent loops.

---

## Step-by-Step Request/Response Architecture

```mermaid
sequenceDiagram
    participant User
    participant App as Application
    participant Claude

    Note over App,Claude: TURN 1 — User question + tool definitions
    App->>Claude: POST /v1/messages\n{messages:[user], tools:[...]}
    Claude->>App: {content:[text?, tool_use+], stop_reason:"tool_use"}

    Note over App: Execute tool(s)

    Note over App,Claude: TURN 2 — Tool results
    App->>Claude: POST /v1/messages\n{messages:[user, assistant(tool_use), user(tool_result)]}
    Claude->>App: {content:[text], stop_reason:"end_turn"}

    App->>User: Final answer
```

---

## Exact Message Structure at Each Turn

### Turn 1 — Initial Request

```json
{
  "model": "claude-sonnet-4-6",
  "max_tokens": 4096,
  "tools": [
    {
      "name": "search_database",
      "description": "Search the product database by keyword. Returns matching products with IDs and prices.",
      "input_schema": {
        "type": "object",
        "properties": {
          "query": {
            "type": "string",
            "description": "Search keyword"
          },
          "limit": {
            "type": "integer",
            "description": "Max results to return (default 10)"
          }
        },
        "required": ["query"]
      }
    }
  ],
  "messages": [
    {"role": "user", "content": "Find me laptops under $1000"}
  ]
}
```

### Turn 1 — Claude's Response (tool call)

```json
{
  "id": "msg_01...",
  "type": "message",
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "I'll search the database for laptops under $1000."
    },
    {
      "type": "tool_use",
      "id": "toolu_01A09q90qw90lq92M9fjBz",
      "name": "search_database",
      "input": {
        "query": "laptop under 1000",
        "limit": 5
      }
    }
  ],
  "stop_reason": "tool_use"
}
```

Note: Claude may include a `text` block before `tool_use`. You must preserve the entire `content` array.

### Turn 2 — Request with Tool Result

```json
{
  "model": "claude-sonnet-4-6",
  "max_tokens": 4096,
  "tools": [...],
  "messages": [
    {"role": "user", "content": "Find me laptops under $1000"},
    {
      "role": "assistant",
      "content": [
        {"type": "text", "text": "I'll search the database for laptops under $1000."},
        {
          "type": "tool_use",
          "id": "toolu_01A09q90qw90lq92M9fjBz",
          "name": "search_database",
          "input": {"query": "laptop under 1000", "limit": 5}
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "tool_result",
          "tool_use_id": "toolu_01A09q90qw90lq92M9fjBz",
          "content": "[{\"id\":\"LAP001\",\"name\":\"ThinkPad E15\",\"price\":899},{\"id\":\"LAP002\",\"name\":\"Dell Inspiron 15\",\"price\":749}]"
        }
      ]
    }
  ]
}
```

---

## Parallel Tool Call Architecture

When Claude calls multiple tools at once, all `tool_use` blocks appear in the same assistant message, and all `tool_result` blocks appear in the same user message:

```mermaid
graph TD
    A["User: Compare weather in Tokyo and Paris"] --> B["Claude response"]
    B --> C["tool_use: get_weather(Tokyo)\nid: toolu_01"]
    B --> D["tool_use: get_weather(Paris)\nid: toolu_02"]
    C --> E["Execute in parallel"]
    D --> E
    E --> F["tool_result: 72°F\ntool_use_id: toolu_01"]
    E --> G["tool_result: 65°F\ntool_use_id: toolu_02"]
    F --> H["Single user message\nwith both results"]
    G --> H
    H --> I["Claude final answer"]
```

```json
{
  "role": "user",
  "content": [
    {
      "type": "tool_result",
      "tool_use_id": "toolu_01",
      "content": "Tokyo: 72°F, sunny"
    },
    {
      "type": "tool_result",
      "tool_use_id": "toolu_02",
      "content": "Paris: 65°F, cloudy"
    }
  ]
}
```

Both results go in the same user message. Each `tool_use_id` matches the corresponding `tool_use` block's `id`.

---

## Tool Choice Architecture

```mermaid
graph TD
    A["tool_choice parameter"] --> B{"type?"}
    B -->|auto| C["Claude decides:\nmay or may not use tools"]
    B -->|any| D["Claude MUST use at\nleast one tool"]
    B -->|tool| E["Claude MUST use\nthe specified tool"]
    B -->|none| F["Claude MUST NOT\nuse any tools"]
```

| Value | Use case |
|---|---|
| `{"type": "auto"}` | General assistant — let Claude decide |
| `{"type": "any"}` | Force tool usage (data extraction) |
| `{"type": "tool", "name": "X"}` | Force a specific pipeline step |
| `{"type": "none"}` | Run a pass where tools were defined but shouldn't fire |

---

## Error Handling Architecture

```mermaid
flowchart TD
    A["Execute tool"] --> B{success?}
    B -->|yes| C["tool_result: content=result"]
    B -->|timeout| D["tool_result: content='Error: timeout'\nis_error: true"]
    B -->|exception| E["tool_result: content='Error: msg'\nis_error: true"]
    C --> F["Append to messages\nContinue loop"]
    D --> F
    E --> F
    F --> G["Claude reads error\nand responds gracefully"]
```

```json
{
  "type": "tool_result",
  "tool_use_id": "toolu_01...",
  "content": "Error: Database unavailable. Please try again in a moment.",
  "is_error": true
}
```

Claude will acknowledge the error and either retry, use a fallback, or inform the user gracefully.

---

## Multi-Step Agent Loop Architecture

```mermaid
flowchart LR
    subgraph "Agent Loop"
        A["Initial\nuser message"] --> B["messages.create\nwith tools"]
        B --> C{stop_reason}
        C -->|tool_use| D["Extract tool_use\nblocks"]
        D --> E["Execute tools\n(parallel if possible)"]
        E --> F["Append assistant\n+ tool_result msgs"]
        F --> B
        C -->|end_turn| G["Return final\nresponse text"]
    end
    
    subgraph "Safety"
        H["Max iterations\ncounter"] -.-> C
        H -->|exceeded| I["Return partial\n+ warning"]
    end
```

Always implement a `max_iterations` guard (typically 10) to prevent infinite loops.

---

## Tool Definition Best Practices

```mermaid
graph TD
    A["Tool Definition Quality"] --> B["name: snake_case,\nverb_noun pattern"]
    A --> C["description: when to use,\nwhat it returns,\nlimitations"]
    A --> D["input_schema: exact types,\nclear descriptions per field,\nrequired vs optional"]
    
    B --> E["Good: get_weather\nBad: weather"]
    C --> F["Good: 'Returns current temperature and conditions for a city. Use when user asks about weather.'\nBad: 'Gets weather'"]
    D --> G["Good: field descriptions\nthat explain units and format\nBad: no descriptions on fields"]
```

---

## Token Cost of Tool Use

Tool definitions consume input tokens on every call. A typical tool definition with one input field costs ~50-100 tokens. A complex tool with many fields costs 200+ tokens.

Optimization strategies:
1. Cache tool definitions using prompt caching (mark tools with `cache_control`)
2. Only include relevant tools per request — don't pass all 20 tools to a simple question
3. Use `tool_choice: {"type": "none"}` when you want Claude to reason without acting

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Concept guide |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Architecture_Deep_Dive.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Working code |

⬅️ **Prev:** [System Prompts](../04_System_Prompts/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Streaming](../06_Streaming/Theory.md)
