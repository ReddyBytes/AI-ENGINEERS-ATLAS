# Cheatsheet — Connecting MCP to Agents

**MCP gives AI agents access to real-world tools. The agent loop: think → pick tool → execute via MCP → observe result → repeat until done.**

---

## Key Terms 📋

| Term | Definition |
|---|---|
| **Agent** | An AI that takes sequences of actions to complete a longer-horizon goal |
| **Agent loop** | The think-act-observe cycle: model decides → tool called → result observed → repeat |
| **Tool selection** | The AI model's decision about which tool to call and with what arguments |
| **Agentic architecture** | A system where the AI autonomously decides sequences of tool calls |
| **Max steps** | A limit on how many tool calls an agent can make before stopping |
| **Stop reason** | Why the model stopped: `end_turn` (done), `tool_use` (needs to call a tool) |
| **Multi-server agent** | An agent connected to multiple MCP servers simultaneously |

---

## The Agent Loop Pattern

```python
messages = [{"role": "user", "content": user_goal}]
max_steps = 20

for step in range(max_steps):
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        tools=mcp_tools_in_anthropic_format,
        messages=messages
    )

    if response.stop_reason == "end_turn":
        # Agent is done
        print(response.content[0].text)
        break

    if response.stop_reason == "tool_use":
        # Agent wants to call tools
        messages.append({"role": "assistant", "content": response.content})
        tool_results = []

        for block in response.content:
            if block.type == "tool_use":
                # Call the tool via MCP
                result = await mcp_session.call_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result.content[0].text
                })

        messages.append({"role": "user", "content": tool_results})
```

---

## MCP Tool → Anthropic Format Conversion

```python
# MCP Tool definition → Anthropic function calling format
mcp_tools = await session.list_tools()

anthropic_tools = [
    {
        "name": tool.name,
        "description": tool.description,
        "input_schema": tool.inputSchema  # JSON Schema — same format!
    }
    for tool in mcp_tools.tools
]
```

---

## Multi-Server Agent Pattern

```python
async def connect_multiple_servers(server_configs: list[dict]):
    """Connect to multiple MCP servers and aggregate their tools."""
    all_tools = []
    sessions = {}

    for config in server_configs:
        server_params = StdioServerParameters(
            command=config["command"],
            args=config["args"],
            env=config.get("env", {})
        )
        # Create client connection (store for later tool routing)
        client_context = stdio_client(server_params)
        read, write = await client_context.__aenter__()
        session = ClientSession(read, write)
        await session.initialize()

        # Collect tools, remembering which session owns them
        tools = await session.list_tools()
        for tool in tools.tools:
            all_tools.append(tool)
            sessions[tool.name] = session  # Route by tool name

    return all_tools, sessions

# When calling a tool, route to the right session:
async def call_mcp_tool(tool_name, arguments, sessions):
    session = sessions[tool_name]
    return await session.call_tool(tool_name, arguments)
```

---

## Agent Design Principles

| Principle | Why It Matters |
|---|---|
| Set max_steps limit | Prevents infinite loops |
| Handle tool errors | External services fail; agent should recover |
| Log every tool call | Essential for debugging autonomous actions |
| Confirm destructive tools | Agent should ask before irreversible actions |
| Start with fewer tools | Fewer tools = fewer mistakes; add as needed |
| Include context in goal | Agent performs better with rich initial context |

---

## Error Handling in Agent Loops

```python
for block in response.content:
    if block.type == "tool_use":
        try:
            result = await session.call_tool(block.name, block.input)
            content = result.content[0].text
        except Exception as e:
            # Return error as tool result — agent can reason about it
            content = f"Tool call failed: {str(e)}"

        tool_results.append({
            "type": "tool_result",
            "tool_use_id": block.id,
            "content": content,
            "is_error": isinstance(result, Exception)  # Optional: mark as error
        })
```

---

## When to Use MCP Agents vs Simple Chat

| Use MCP Agents when: | Use Simple Chat when: |
|---|---|
| The task requires multiple real-world actions | You just need an answer or explanation |
| The task needs access to real data (files, DB) | Knowledge already in the model is sufficient |
| The task is repeatable and automatable | It is a one-time question |
| Speed of execution matters | Human guidance throughout is preferred |
| The task has a clear completion state | The conversation is exploratory |

---

## Golden Rules 🏆

- Always set a maximum step limit — agents can get stuck in loops
- Return tool errors as text results, not exceptions — the agent can reason about errors
- Log every tool call in production: tool name, arguments, result, duration
- Require human confirmation for any destructive or irreversible tool in an autonomous agent
- Start with the minimal set of tools for the task — more tools means more chances to go wrong
- Make the initial goal message rich with context — the agent performs better with clear instructions
- Test agents with the MCP Inspector and simple test cases before running on real data

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [08 MCP Ecosystem](../08_MCP_Ecosystem/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [01 Model Serving](../../12_Production_AI/01_Model_Serving/Theory.md)