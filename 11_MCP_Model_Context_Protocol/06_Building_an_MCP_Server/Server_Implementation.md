# Server Implementation Reference

A complete reference guide for implementing MCP servers in Python using the `mcp` SDK. Use this as a lookup document when building servers.

---

## SDK Installation

```bash
pip install mcp

# For SSE transport (HTTP server)
pip install mcp fastapi uvicorn

# For making HTTP calls in tools
pip install httpx

# For async database access
pip install asyncpg  # PostgreSQL
# or
pip install aiosqlite  # SQLite
```

---

## Server Capabilities Declaration

During `initialize`, your server declares which primitives it supports. The SDK generates this automatically from the handlers you register:

```python
capabilities=app.get_capabilities(
    notification_options=None,      # Set to NotificationOptions() if you send notifications
    experimental_capabilities={}   # For experimental features
)
```

If you register `@app.list_tools()` + `@app.call_tool()`, the capabilities object automatically includes `tools`.
If you register `@app.list_resources()` + `@app.read_resource()`, capabilities includes `resources`.
If you register `@app.list_prompts()` + `@app.get_prompt()`, capabilities includes `prompts`.

---

## Tool Handler Patterns

### Basic tool handler

```python
@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="tool_name",
            description="Clear description of what this tool does and when to use it",
            inputSchema={
                "type": "object",
                "properties": {
                    "param1": {
                        "type": "string",
                        "description": "What this parameter is for"
                    },
                    "param2": {
                        "type": "integer",
                        "description": "A numeric parameter",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 10
                    },
                    "param3": {
                        "type": "string",
                        "enum": ["option_a", "option_b", "option_c"],
                        "description": "Must be one of these values"
                    }
                },
                "required": ["param1"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
    if arguments is None:
        arguments = {}

    if name == "tool_name":
        param1 = arguments.get("param1")
        if not param1:
            return [types.TextContent(type="text", text="Error: param1 is required")]

        # Your tool logic here
        result = do_something(param1)
        return [types.TextContent(type="text", text=str(result))]

    raise ValueError(f"Unknown tool: {name}")
```

### Tool returning JSON data

```python
import json

return [types.TextContent(
    type="text",
    text=json.dumps({"key": "value", "count": 42}, indent=2)
)]
```

### Tool returning multiple content items

```python
return [
    types.TextContent(type="text", text="Here is the chart:"),
    types.ImageContent(
        type="image",
        data=base64_encoded_image_bytes,
        mimeType="image/png"
    )
]
```

---

## Resource Handler Patterns

```python
@app.list_resources()
async def list_resources() -> list[types.Resource]:
    return [
        types.Resource(
            uri="custom://data/report",
            name="Monthly Report",
            description="The latest monthly business report",
            mimeType="text/plain"
        ),
        types.Resource(
            uri="file:///etc/config.json",
            name="Config File",
            mimeType="application/json"
        )
    ]

@app.read_resource()
async def read_resource(uri: str) -> str:
    if uri == "custom://data/report":
        return fetch_report_from_database()
    elif uri == "file:///etc/config.json":
        return Path("/etc/config.json").read_text()
    else:
        raise ValueError(f"Unknown resource: {uri}")
```

---

## Prompt Handler Patterns

```python
@app.list_prompts()
async def list_prompts() -> list[types.Prompt]:
    return [
        types.Prompt(
            name="analyze_data",
            description="Analyze a dataset and provide insights",
            arguments=[
                types.PromptArgument(
                    name="data",
                    description="The data to analyze (CSV or JSON format)",
                    required=True
                ),
                types.PromptArgument(
                    name="focus",
                    description="What aspect to focus on (trends, outliers, summary)",
                    required=False
                )
            ]
        )
    ]

@app.get_prompt()
async def get_prompt(
    name: str, arguments: dict[str, str] | None
) -> types.GetPromptResult:
    if name == "analyze_data":
        data = (arguments or {}).get("data", "")
        focus = (arguments or {}).get("focus", "all aspects")

        return types.GetPromptResult(
            description="Data analysis prompt",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Analyze the following data, focusing on {focus}:\n\n{data}"
                    )
                )
            ]
        )
    raise ValueError(f"Unknown prompt: {name}")
```

---

## Error Types and Codes

| Situation | Recommended Handling |
|---|---|
| Required argument missing | Return TextContent with error message |
| File not found | Return TextContent: "Error: File not found: {path}" |
| External API failure | Return TextContent: "Error: API call failed: {detail}" |
| Permission denied | Return TextContent: "Error: Permission denied: {detail}" |
| Invalid argument value | Return TextContent: "Error: Invalid {arg}: {reason}" |
| Unknown tool name | Raise `ValueError(f"Unknown tool: {name}")` |
| Unknown resource URI | Raise `ValueError(f"Unknown resource: {uri}")` |
| Internal/unexpected error | Return TextContent: "Error: Internal error: {str(e)}" |

---

## Sending Notifications (Progress Updates)

During a long-running tool operation, you can send progress notifications:

```python
@app.call_tool()
async def call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
    if name == "long_running_task":
        # Send a progress notification
        await app.request_context.session.send_log_message(
            level="info",
            data="Step 1 of 3: Fetching data..."
        )

        data = await fetch_large_dataset()

        await app.request_context.session.send_log_message(
            level="info",
            data="Step 2 of 3: Processing data..."
        )

        result = process(data)
        return [types.TextContent(type="text", text=result)]
```

---

## Transport Configurations

### stdio (default, local)

```python
async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="my-server",
                server_version="1.0.0",
                capabilities=app.get_capabilities(
                    notification_options=None,
                    experimental_capabilities={}
                )
            )
        )

asyncio.run(main())
```

### SSE (HTTP, for remote/shared servers)

```python
from fastapi import FastAPI, Request
from mcp.server.sse import SseServerTransport
import uvicorn

fastapi_app = FastAPI()
sse = SseServerTransport("/messages/")

@fastapi_app.get("/sse")
async def sse_endpoint(request: Request):
    async with sse.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        await app.run(
            streams[0], streams[1],
            app.create_initialization_options()
        )

@fastapi_app.post("/messages/")
async def handle_messages(request: Request):
    await sse.handle_post_message(
        request.scope, request.receive, request._send
    )

if __name__ == "__main__":
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)
```

---

## Testing with MCP Inspector

```bash
# Launch inspector (automatically opens browser)
npx @modelcontextprotocol/inspector python your_server.py

# Inspector lets you:
# - Browse available tools, resources, prompts
# - Call tools with custom JSON arguments
# - Read resources by URI
# - Request prompts with arguments
# - See raw JSON-RPC messages
```

---

## Common inputSchema Patterns

```json
// String with validation
{"type": "string", "minLength": 1, "maxLength": 1000}

// Integer in range
{"type": "integer", "minimum": 0, "maximum": 100, "default": 10}

// Enum (fixed choices)
{"type": "string", "enum": ["small", "medium", "large"]}

// Boolean flag
{"type": "boolean", "default": false}

// Array of strings
{"type": "array", "items": {"type": "string"}, "minItems": 1}

// Optional object
{"type": "object", "properties": {"key": {"type": "string"}}}

// File path
{"type": "string", "description": "Absolute path to the file"}
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |
| 📄 **Server_Implementation.md** | ← you are here |
| [📄 Step_by_Step.md](./Step_by_Step.md) | Step-by-step build guide |

⬅️ **Prev:** [05 Transport Layer](../05_Transport_Layer/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [07 Security and Permissions](../07_Security_and_Permissions/Theory.md)