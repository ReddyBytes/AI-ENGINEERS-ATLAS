# Integration Guide — Adding MCP Servers to Your Setup

This guide shows you exactly how to add MCP servers to Claude Desktop, VS Code, and custom Python applications.

---

## Claude Desktop Integration

### Finding the Config File

| Platform | Config File Location |
|---|---|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| Linux | `~/.config/claude/claude_desktop_config.json` |

### Config File Structure

```json
{
  "mcpServers": {
    "server-alias": {
      "command": "command-to-run",
      "args": ["arg1", "arg2"],
      "env": {
        "ENV_VAR_NAME": "value"
      }
    }
  }
}
```

- `"server-alias"` — a name you choose; appears in Claude Desktop UI
- `"command"` — the executable to run (python, node, npx, etc.)
- `"args"` — command-line arguments passed to the server
- `"env"` — environment variables passed to the server process

### Step-by-Step: Add a Server to Claude Desktop

1. **Find or install the server** (example: GitHub server)
```bash
# npm-based servers can be run with npx (no install needed)
# or install globally:
npm install -g @modelcontextprotocol/server-github
```

2. **Edit the config file**
```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_your_token_here"
      }
    }
  }
}
```

3. **Restart Claude Desktop** — completely quit (not just close window) and reopen

4. **Verify** — Look for the tools icon in the bottom of the chat input. Click it to see available tools.

### Adding Your Own Python Server to Claude Desktop

```json
{
  "mcpServers": {
    "my-custom-server": {
      "command": "/path/to/venv/bin/python",
      "args": ["/absolute/path/to/my_server.py"],
      "env": {
        "MY_API_KEY": "your-key-here"
      }
    }
  }
}
```

**Important tips:**
- Always use absolute paths, not relative paths
- If using a Python virtual environment, use the venv's Python binary path
- Test the server independently before adding to Claude Desktop: `python my_server.py` should not crash

---

## VS Code Integration

VS Code supports MCP through extensions (primarily GitHub Copilot and third-party AI extensions).

### For GitHub Copilot (VS Code)

Create or edit `.vscode/mcp.json` in your project:

```json
{
  "servers": {
    "filesystem": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "${workspaceFolder}"]
    },
    "github": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${env:GITHUB_TOKEN}"
      }
    }
  }
}
```

Note: VS Code uses `${workspaceFolder}` and `${env:VAR}` template variables.

### For SSE-Based Servers in VS Code

```json
{
  "servers": {
    "remote-database": {
      "type": "sse",
      "url": "http://localhost:8000/sse"
    }
  }
}
```

---

## Custom Python Application Integration

Use the `mcp` SDK to connect to any MCP server from your own Python code.

### Connecting to a stdio Server

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    # Configure which server to connect to
    server_params = StdioServerParameters(
        command="python",
        args=["/path/to/server.py"],
        env={"MY_API_KEY": "your-key"}
    )

    # Connect to the server
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()

            # List available tools
            tools = await session.list_tools()
            print("Available tools:", [t.name for t in tools.tools])

            # Call a tool
            result = await session.call_tool(
                "my_tool",
                arguments={"param1": "value1"}
            )
            print("Result:", result.content[0].text)

asyncio.run(main())
```

### Connecting to an SSE Server

```python
import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

async def main():
    async with sse_client("http://localhost:8000/sse") as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("Available tools:", [t.name for t in tools.tools])

            result = await session.call_tool("get_current_weather", {"city": "London"})
            print(result.content[0].text)

asyncio.run(main())
```

### Using MCP with the Anthropic Python SDK

```python
import anthropic
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run_agent_with_mcp():
    # Connect to MCP server and get tools
    server_params = StdioServerParameters(
        command="python",
        args=["weather_server.py"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Get MCP tools and convert to Anthropic format
            mcp_tools = await session.list_tools()
            anthropic_tools = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                }
                for tool in mcp_tools.tools
            ]

            # Run the Anthropic API with MCP tools
            client = anthropic.Anthropic()

            messages = [{"role": "user", "content": "What's the weather in Tokyo?"}]

            # Agentic loop
            while True:
                response = client.messages.create(
                    model="claude-opus-4-6",
                    max_tokens=1024,
                    tools=anthropic_tools,
                    messages=messages
                )

                if response.stop_reason == "end_turn":
                    print(response.content[0].text)
                    break

                # Handle tool calls
                if response.stop_reason == "tool_use":
                    messages.append({"role": "assistant", "content": response.content})

                    tool_results = []
                    for block in response.content:
                        if block.type == "tool_use":
                            # Execute the tool via MCP
                            result = await session.call_tool(
                                block.name,
                                arguments=block.input
                            )
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": result.content[0].text
                            })

                    messages.append({"role": "user", "content": tool_results})

asyncio.run(run_agent_with_mcp())
```

---

## Troubleshooting Common Integration Issues

| Problem | Likely Cause | Solution |
|---|---|---|
| Server not appearing in Claude Desktop | Wrong path or command | Check config uses absolute paths; test command in terminal |
| "Module not found" error | Wrong Python binary | Use full path to venv Python: `/path/to/venv/bin/python` |
| Server connects but tools not visible | Config not reloaded | Completely quit and restart Claude Desktop (not just close) |
| Tool calls fail silently | Server crashing on startup | Run `python server.py` in terminal to see error output |
| "Permission denied" | File/directory permissions | Check server has read/write access to configured paths |
| API key errors | Env var not passed | Verify env section in config; check var name spelling |

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Integration_Guide.md** | ← you are here |
| [📄 Known_Servers.md](./Known_Servers.md) | Known MCP servers directory |

⬅️ **Prev:** [07 Security and Permissions](../07_Security_and_Permissions/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [09 Connect MCP to Agents](../09_Connect_MCP_to_Agents/Theory.md)