# Cheatsheet — Building an MCP Server

**Building an MCP server = declare capabilities + implement handlers + set up transport. The Python `mcp` SDK handles the protocol; you write the business logic.**

---

## Key Terms 📋

| Term | Definition |
|---|---|
| **Server object** | `Server("name")` — the core SDK object that registers handlers |
| **Handler** | An async function decorated with `@app.list_tools()`, `@app.call_tool()`, etc. |
| **Decorator** | The `@app.xxx()` syntax that registers a function as an MCP handler |
| **Capabilities** | What the server declares it can do during `initialize` |
| **Tool schema** | JSON Schema that describes a tool's input arguments |
| **Content** | The return type of tool calls — `TextContent`, `ImageContent`, or `EmbeddedResource` |
| **MCP Inspector** | The official dev tool for testing MCP servers interactively |

---

## Minimal Server Template

```python
import asyncio
import mcp.server.stdio
import mcp.types as types
from mcp.server import Server
from mcp.server.models import InitializationOptions

app = Server("my-server")

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="my_tool",
            description="What this tool does",
            inputSchema={
                "type": "object",
                "properties": {
                    "arg1": {"type": "string", "description": "First argument"}
                },
                "required": ["arg1"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "my_tool":
        result = do_the_work(arguments["arg1"])
        return [types.TextContent(type="text", text=result)]
    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with mcp.server.stdio.stdio_server() as (read, write):
        await app.run(read, write, InitializationOptions(
            server_name="my-server",
            server_version="1.0.0",
            capabilities=app.get_capabilities(
                notification_options=None,
                experimental_capabilities={}
            )
        ))

asyncio.run(main())
```

---

## Handler Decorator Reference

| Decorator | Required? | Purpose |
|---|---|---|
| `@app.list_tools()` | YES (if tools) | Returns list of Tool objects |
| `@app.call_tool()` | YES (if tools) | Executes tool by name, returns content |
| `@app.list_resources()` | NO | Returns list of Resource objects |
| `@app.read_resource()` | NO | Returns resource content by URI |
| `@app.list_prompts()` | NO | Returns list of Prompt objects |
| `@app.get_prompt()` | NO | Returns filled-in prompt messages |

---

## Tool Return Types

```python
# Text result
return [types.TextContent(type="text", text="your result here")]

# Multiple content items
return [
    types.TextContent(type="text", text="Result:"),
    types.ImageContent(type="image", data="<base64>", mimeType="image/png")
]

# Error (return as text, don't raise — so AI can read the error)
return [types.TextContent(type="text", text="Error: file not found at /path/to/file")]
```

---

## Environment Variables Pattern

```python
import os

# In your tool handler
api_key = os.environ.get("MY_API_KEY")
if not api_key:
    return [types.TextContent(type="text", text="Error: MY_API_KEY environment variable not set")]
```

```json
// In claude_desktop_config.json
{
  "mcpServers": {
    "my-server": {
      "command": "python",
      "args": ["/path/to/server.py"],
      "env": { "MY_API_KEY": "your-key-here" }
    }
  }
}
```

---

## Testing Commands

```bash
# Test interactively with MCP Inspector
npx @modelcontextprotocol/inspector python server.py

# Test with raw JSON-RPC (stdio)
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | python server.py

# Install in Claude Desktop
# Edit ~/Library/Application Support/Claude/claude_desktop_config.json
# Then restart Claude Desktop
```

---

## Error Handling Pattern

```python
@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    try:
        if name == "read_file":
            path = arguments.get("path")
            if not path:
                return [types.TextContent(type="text", text="Error: 'path' argument is required")]

            content = Path(path).read_text()
            return [types.TextContent(type="text", text=content)]

    except FileNotFoundError:
        return [types.TextContent(type="text", text=f"Error: File not found: {arguments.get('path')}")]
    except PermissionError:
        return [types.TextContent(type="text", text=f"Error: Permission denied: {arguments.get('path')}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]
```

---

## Golden Rules 🏆

- Never write to stdout in a stdio server — use sys.stderr for logs
- Always handle exceptions in tool handlers and return descriptive error text
- Never hardcode credentials — use environment variables
- Use `@app.list_tools()` to declare tools and `@app.call_tool()` to execute them — they work together
- Test every tool with the MCP Inspector before connecting to Claude Desktop
- Design tools to do one thing well — small focused tools are easier to test
- Version your server in the `server_version` field of InitializationOptions

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |
| [📄 Server_Implementation.md](./Server_Implementation.md) | Full server implementation guide |
| [📄 Step_by_Step.md](./Step_by_Step.md) | Step-by-step build guide |

⬅️ **Prev:** [05 Transport Layer](../05_Transport_Layer/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [07 Security and Permissions](../07_Security_and_Permissions/Theory.md)