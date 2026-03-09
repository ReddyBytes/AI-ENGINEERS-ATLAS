# Code Example — Tools, Resources, and Prompts

This example builds a complete MCP server in Python using the official `mcp` SDK. It demonstrates all three primitives: a **Tool** (calculator), a **Resource** (read a notes file), and a **Prompt** (code review template).

---

## Setup

```bash
# Install the MCP Python SDK
pip install mcp

# Create the server file
touch my_demo_server.py
```

---

## Complete Server Code

```python
# my_demo_server.py
# A demo MCP server showing Tools, Resources, and Prompts
# Run with: python my_demo_server.py

import asyncio
import json
from pathlib import Path
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Create the server instance
app = Server("demo-server")

# ─────────────────────────────────────────────
# TOOLS — things the AI can DO
# ─────────────────────────────────────────────

@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """Tell the client what tools this server offers."""
    return [
        types.Tool(
            name="calculate",
            description=(
                "Perform a basic arithmetic calculation. "
                "Supports add, subtract, multiply, divide operations."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["add", "subtract", "multiply", "divide"],
                        "description": "The arithmetic operation to perform"
                    },
                    "a": {
                        "type": "number",
                        "description": "The first number"
                    },
                    "b": {
                        "type": "number",
                        "description": "The second number"
                    }
                },
                "required": ["operation", "a", "b"]
            }
        ),
        types.Tool(
            name="write_note",
            description="Write or append text to the notes.txt file.",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The text to write to the notes file"
                    },
                    "append": {
                        "type": "boolean",
                        "description": "If true, append to existing content. If false, overwrite.",
                        "default": True
                    }
                },
                "required": ["content"]
            }
        )
    ]


@app.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle a tool call from the client."""

    if name == "calculate":
        # Extract and validate arguments
        op = arguments.get("operation")
        a = arguments.get("a")
        b = arguments.get("b")

        # Perform the calculation
        if op == "add":
            result = a + b
        elif op == "subtract":
            result = a - b
        elif op == "multiply":
            result = a * b
        elif op == "divide":
            if b == 0:
                return [types.TextContent(
                    type="text",
                    text="Error: Cannot divide by zero"
                )]
            result = a / b
        else:
            return [types.TextContent(type="text", text=f"Unknown operation: {op}")]

        return [types.TextContent(
            type="text",
            text=f"{a} {op} {b} = {result}"
        )]

    elif name == "write_note":
        content = arguments.get("content", "")
        append = arguments.get("append", True)

        notes_path = Path("notes.txt")
        mode = "a" if append else "w"

        with open(notes_path, mode) as f:
            f.write(content + "\n")

        return [types.TextContent(
            type="text",
            text=f"Successfully {'appended to' if append else 'wrote'} notes.txt"
        )]

    else:
        raise ValueError(f"Unknown tool: {name}")


# ─────────────────────────────────────────────
# RESOURCES — data the AI can READ
# ─────────────────────────────────────────────

@app.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """Tell the client what resources this server provides."""
    notes_path = Path("notes.txt")

    resources = [
        types.Resource(
            uri="file:///notes.txt",
            name="Personal Notes",
            description="A simple text file for storing notes",
            mimeType="text/plain"
        )
    ]
    return resources


@app.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read and return the content of a resource by URI."""

    if uri == "file:///notes.txt":
        notes_path = Path("notes.txt")
        if notes_path.exists():
            return notes_path.read_text()
        else:
            return "Notes file is empty. Use the write_note tool to add content."

    raise ValueError(f"Unknown resource URI: {uri}")


# ─────────────────────────────────────────────
# PROMPTS — reusable prompt templates
# ─────────────────────────────────────────────

@app.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    """Tell the client what prompt templates this server provides."""
    return [
        types.Prompt(
            name="code_review",
            description=(
                "Generate a thorough, structured code review. "
                "Checks for bugs, style issues, performance, and security."
            ),
            arguments=[
                types.PromptArgument(
                    name="code",
                    description="The code snippet to review",
                    required=True
                ),
                types.PromptArgument(
                    name="language",
                    description="The programming language (python, javascript, etc.)",
                    required=False
                ),
                types.PromptArgument(
                    name="focus",
                    description="Optional focus area: 'security', 'performance', or 'style'",
                    required=False
                )
            ]
        )
    ]


@app.get_prompt()
async def handle_get_prompt(
    name: str, arguments: dict[str, str] | None
) -> types.GetPromptResult:
    """Fill in and return a prompt template."""

    if name == "code_review":
        code = arguments.get("code", "")
        language = arguments.get("language", "unknown language")
        focus = arguments.get("focus", "all aspects")

        return types.GetPromptResult(
            description=f"Code review for {language} code",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"""Please review the following {language} code, focusing on {focus}.

For each issue found, please specify:
1. The type of issue (bug, style, performance, security)
2. The line or section where it occurs
3. Why it is a problem
4. How to fix it

Code to review:
```{language}
{code}
```

Provide a summary at the end with an overall quality rating (1-10)."""
                    )
                )
            ]
        )

    raise ValueError(f"Unknown prompt: {name}")


# ─────────────────────────────────────────────
# START THE SERVER
# ─────────────────────────────────────────────

async def main():
    """Run the MCP server using stdio transport."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="demo-server",
                server_version="1.0.0",
                capabilities=app.get_capabilities(
                    notification_options=None,
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
```

---

## How to Test This Server

**Option 1: Use MCP Inspector (recommended for development)**

```bash
# Install the MCP inspector
npx @modelcontextprotocol/inspector python my_demo_server.py
```

This opens a web UI where you can:
- See the tools, resources, and prompts the server exposes
- Call tools with custom arguments
- Read resources
- Request prompts with arguments

**Option 2: Connect to Claude Desktop**

Add this to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "demo": {
      "command": "python",
      "args": ["/absolute/path/to/my_demo_server.py"]
    }
  }
}
```

Restart Claude Desktop. You can now ask Claude to calculate things, write notes, and read your notes file.

---

## What Each Section Demonstrates

| Section | MCP Primitive | Key Pattern |
|---|---|---|
| `@app.list_tools()` | Tool | Returns list of Tool objects with JSON Schema |
| `@app.call_tool()` | Tool | Dispatches by tool name, returns content list |
| `@app.list_resources()` | Resource | Returns list of Resource objects with URIs |
| `@app.read_resource()` | Resource | Returns content string for a given URI |
| `@app.list_prompts()` | Prompt | Returns list of Prompt objects with argument specs |
| `@app.get_prompt()` | Prompt | Fills in template, returns GetPromptResult with messages |

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [03 Hosts Clients Servers](../03_Hosts_Clients_Servers/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 Transport Layer](../05_Transport_Layer/Theory.md)