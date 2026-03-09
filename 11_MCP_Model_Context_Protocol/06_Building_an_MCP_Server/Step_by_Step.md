# Step-by-Step — Build Your First MCP Server

This is a hands-on tutorial. By the end, you will have a working MCP server connected to Claude Desktop. The server will expose two tools that Claude can actually use.

**Time estimate:** 20-30 minutes
**Prerequisites:** Python 3.10+, Claude Desktop installed

---

## Step 1: Install the MCP SDK

```bash
# Create a project directory
mkdir my-mcp-server
cd my-mcp-server

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the MCP SDK
pip install mcp httpx
```

Verify the install:
```bash
python -c "import mcp; print('MCP SDK installed successfully')"
```

---

## Step 2: Define Your Tools

Create a file called `server.py`. We will build a simple "utility tools" server with two tools:
- `get_word_count` — counts words in a text
- `reverse_text` — reverses a string

```python
# server.py
import asyncio
import sys
import mcp.server.stdio
import mcp.types as types
from mcp.server import Server
from mcp.server.models import InitializationOptions

# Step 2a: Create the server object
app = Server("utility-server")

# Step 2b: Declare what tools we have
@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="get_word_count",
            description=(
                "Count the number of words, characters, and lines in a given text. "
                "Useful for analyzing text length."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to analyze"
                    }
                },
                "required": ["text"]
            }
        ),
        types.Tool(
            name="reverse_text",
            description="Reverse the characters or words in a given text.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to reverse"
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["characters", "words"],
                        "description": "Whether to reverse individual characters or word order",
                        "default": "characters"
                    }
                },
                "required": ["text"]
            }
        )
    ]
```

---

## Step 3: Implement the Tool Logic

Add the tool execution handler to your `server.py`:

```python
# Step 3: Implement what happens when tools are called
@app.call_tool()
async def call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent]:

    # Always guard against None arguments
    if arguments is None:
        arguments = {}

    if name == "get_word_count":
        text = arguments.get("text", "")
        if not text:
            return [types.TextContent(type="text", text="Error: text argument is required")]

        word_count = len(text.split())
        char_count = len(text)
        char_no_spaces = len(text.replace(" ", ""))
        line_count = text.count("\n") + 1

        result = f"""Text Analysis:
- Words: {word_count}
- Characters (with spaces): {char_count}
- Characters (no spaces): {char_no_spaces}
- Lines: {line_count}"""

        return [types.TextContent(type="text", text=result)]

    elif name == "reverse_text":
        text = arguments.get("text", "")
        mode = arguments.get("mode", "characters")

        if not text:
            return [types.TextContent(type="text", text="Error: text argument is required")]

        if mode == "words":
            reversed_text = " ".join(text.split()[::-1])
        else:
            reversed_text = text[::-1]

        return [types.TextContent(type="text", text=reversed_text)]

    else:
        raise ValueError(f"Unknown tool: {name}")
```

---

## Step 4: Add the Transport Setup

Add the transport and main function to the bottom of `server.py`:

```python
# Step 4: Set up the stdio transport and run
async def main():
    # Use stdio transport (server communicates via stdin/stdout)
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="utility-server",
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

## Step 5: Test Locally with MCP Inspector

Before connecting to Claude Desktop, test your server with the official MCP Inspector:

```bash
# Make sure you are in your project directory with venv active
npx @modelcontextprotocol/inspector python server.py
```

This opens a browser at `http://localhost:5173`. In the Inspector:

1. Click **"Tools"** in the left panel — you should see `get_word_count` and `reverse_text`
2. Click `get_word_count`, fill in `text: "Hello world this is a test"`, click **"Run Tool"**
3. You should see: `Words: 6, Characters: 26, ...`
4. Test `reverse_text` with mode `"words"` — the output should have the words in reverse order

If the Inspector shows your tools and they work correctly, your server is ready.

---

## Step 6: Connect to Claude Desktop

Find your Claude Desktop config file:
- **Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

Add your server to the config (replace the path with your actual absolute path):

```json
{
  "mcpServers": {
    "utility-server": {
      "command": "python",
      "args": ["/absolute/path/to/my-mcp-server/server.py"]
    }
  }
}
```

**Important:** Use the full absolute path, not a relative path. Find it with:
```bash
# Mac/Linux
pwd   # while in your project directory

# Then combine: /Users/yourname/my-mcp-server/server.py
```

**Restart Claude Desktop** completely (quit and reopen). Claude Desktop must restart to pick up config changes.

---

## Step 7: Verify It Works

In Claude Desktop, look for the tools icon (usually a hammer or wrench icon) — this indicates MCP tools are available.

Try these prompts:
- "How many words are in this sentence: The quick brown fox jumps over the lazy dog"
- "Reverse the words in this phrase: Hello World from MCP"
- "Count the characters in this paragraph: [paste some text]"

Claude should use your tools to answer these questions. You will see it call `get_word_count` or `reverse_text` in the conversation.

---

## Troubleshooting

**Server does not appear in Claude Desktop:**
- Make sure you used an absolute path in the config
- Make sure Python is in your PATH (run `which python` to confirm)
- If using a venv, use the full path to the venv's Python: `/path/to/venv/bin/python`
- Check Claude Desktop logs (menu → Help → Show Logs)

**Tools appear but fail:**
- Run `python server.py` directly in your terminal — any startup errors will appear
- Check for missing imports or syntax errors

**"Module not found" error:**
- Make sure you installed `mcp` in the same Python environment Claude Desktop is using
- Use the venv Python path in the config: `/path/to/venv/bin/python`

---

## What You Built

```
my-mcp-server/
├── server.py          ← Your MCP server
└── venv/              ← Python virtual environment

server.py contains:
├── Server object       (Server("utility-server"))
├── list_tools()       (declares 2 tools with schemas)
├── call_tool()        (implements tool logic)
└── main()             (stdio transport setup)
```

From here, you can extend this server with:
- More tools (file operations, calculations, API calls)
- Resources (expose data files)
- Prompts (reusable templates)

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |
| [📄 Server_Implementation.md](./Server_Implementation.md) | Full server implementation guide |
| 📄 **Step_by_Step.md** | ← you are here |

⬅️ **Prev:** [05 Transport Layer](../05_Transport_Layer/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [07 Security and Permissions](../07_Security_and_Permissions/Theory.md)