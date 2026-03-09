# Code Example — MCP-Powered Agent

This example builds a complete agentic loop in Python that connects to an MCP server and uses Claude to autonomously accomplish goals using real tools.

The agent connects to the weather server from section 06 and can answer questions that require multiple tool calls.

---

## Setup

```bash
pip install mcp anthropic httpx
```

You need the weather server from section 06 (`weather_server.py`) in the same directory.

---

## Part 1: Simple MCP Client (No Agent Loop)

First, the basic pattern — connect to a server, list tools, call one:

```python
# simple_mcp_client.py
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    # Configure the MCP server to connect to
    server_params = StdioServerParameters(
        command="python",
        args=["weather_server.py"]
    )

    # Connect to the server
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            # 1. Initialize the session
            await session.initialize()
            print("Connected to weather server!")

            # 2. Discover available tools
            tools = await session.list_tools()
            print("\nAvailable tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description[:60]}...")

            # 3. Call a tool directly
            print("\nCalling get_current_weather for London...")
            result = await session.call_tool(
                "get_current_weather",
                arguments={"city": "London"}
            )

            print("Result:", result.content[0].text)

asyncio.run(main())
```

---

## Part 2: Full Agentic Loop with MCP Tools

This is the real agent — Claude autonomously decides when and how to use the weather tools:

```python
# mcp_agent.py
# A Claude agent that uses MCP tools to answer weather questions
# The agent decides when to call tools and chains multiple calls if needed

import asyncio
import anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# ─────────────────────────────────────────────
# MCP CONNECTION + TOOL DISCOVERY
# ─────────────────────────────────────────────

async def get_mcp_tools(session: ClientSession) -> tuple[list, dict]:
    """
    Connect to MCP server, get tools, and convert to Anthropic format.
    Returns: (anthropic_tools, tool_name_to_description_map)
    """
    mcp_tools_response = await session.list_tools()
    mcp_tools = mcp_tools_response.tools

    # Convert MCP tool format → Anthropic function calling format
    # The inputSchema is JSON Schema — exactly what Anthropic expects
    anthropic_tools = [
        {
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        }
        for tool in mcp_tools
    ]

    return anthropic_tools, {t.name: t for t in mcp_tools}


# ─────────────────────────────────────────────
# AGENT LOOP
# ─────────────────────────────────────────────

async def run_agent(
    session: ClientSession,
    user_goal: str,
    max_steps: int = 10
) -> str:
    """
    Run the agentic loop:
    - Give Claude the user's goal + available tools
    - If Claude calls a tool, execute it via MCP and add result
    - Repeat until Claude signals it's done (end_turn)
    - Return Claude's final response
    """

    # Get tools in Anthropic format
    anthropic_tools, tool_map = await get_mcp_tools(session)

    print(f"\n{'='*50}")
    print(f"Agent Goal: {user_goal}")
    print(f"Available tools: {[t['name'] for t in anthropic_tools]}")
    print(f"{'='*50}\n")

    # Initialize conversation
    messages = [
        {"role": "user", "content": user_goal}
    ]

    client = anthropic.Anthropic()

    # ── Agent loop ─────────────────────────────
    for step in range(max_steps):
        print(f"--- Step {step + 1} ---")

        # Ask Claude what to do next
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=2048,
            tools=anthropic_tools,
            messages=messages,
            system=(
                "You are a helpful assistant with access to weather tools. "
                "Use the tools to get real weather data when needed. "
                "Be concise in your final answer."
            )
        )

        print(f"Stop reason: {response.stop_reason}")

        # ── Done: Claude has finished ──────────
        if response.stop_reason == "end_turn":
            # Extract the text from the response
            for block in response.content:
                if hasattr(block, "text"):
                    print(f"\nFinal answer: {block.text}")
                    return block.text
            return "Agent completed without text response"

        # ── Tool use: Claude wants to call tools ──
        if response.stop_reason == "tool_use":
            # Add Claude's response (including tool call requests) to conversation
            messages.append({"role": "assistant", "content": response.content})

            # Execute each tool call
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_args = block.input

                    print(f"Calling tool: {tool_name}")
                    print(f"Arguments: {tool_args}")

                    # Execute via MCP
                    try:
                        mcp_result = await session.call_tool(
                            tool_name,
                            arguments=tool_args
                        )

                        # Extract the text result
                        result_text = ""
                        for content_block in mcp_result.content:
                            if hasattr(content_block, "text"):
                                result_text += content_block.text

                        print(f"Result: {result_text[:100]}...")
                        is_error = False

                    except Exception as e:
                        result_text = f"Tool call failed: {str(e)}"
                        is_error = True
                        print(f"Error: {result_text}")

                    # Add tool result to message list
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result_text
                    })

            # Add all tool results to conversation
            messages.append({
                "role": "user",
                "content": tool_results
            })

        else:
            # Unexpected stop reason
            print(f"Unexpected stop reason: {response.stop_reason}")
            break

    return "Agent reached maximum steps without completing"


# ─────────────────────────────────────────────
# MAIN — RUN THE AGENT
# ─────────────────────────────────────────────

async def main():
    # Connect to the weather MCP server
    server_params = StdioServerParameters(
        command="python",
        args=["weather_server.py"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Test 1: Simple question requiring one tool call
            answer = await run_agent(
                session,
                "What's the weather like in Tokyo right now?",
                max_steps=5
            )

            print("\n" + "="*50)

            # Test 2: Question requiring multiple tool calls (comparison)
            answer = await run_agent(
                session,
                "I'm deciding between traveling to Paris or London next week. "
                "Compare the weather in both cities and recommend which is better "
                "for sightseeing based on the current conditions.",
                max_steps=10
            )

            print("\n" + "="*50)

            # Test 3: Planning question using forecast tool
            answer = await run_agent(
                session,
                "I have outdoor events planned in New York for the next 3 days. "
                "Looking at the forecast, which day is best for being outside?",
                max_steps=5
            )

asyncio.run(main())
```

---

## Part 3: Multi-Server Agent (Connect to Multiple Servers)

This shows how to connect one agent to multiple MCP servers simultaneously:

```python
# multi_server_agent.py
import asyncio
import anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from contextlib import AsyncExitStack

async def run_multi_server_agent(user_goal: str):
    """
    An agent connected to multiple MCP servers.
    Aggregates tools from all servers and routes calls correctly.
    """

    # Configuration: list of servers to connect to
    server_configs = [
        {
            "name": "weather",
            "params": StdioServerParameters(
                command="python",
                args=["weather_server.py"]
            )
        },
        # You could add more servers here:
        # {
        #     "name": "filesystem",
        #     "params": StdioServerParameters(
        #         command="npx",
        #         args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
        #     )
        # }
    ]

    # Use AsyncExitStack to manage multiple async context managers
    async with AsyncExitStack() as stack:
        # Connect to all servers
        all_tools = []       # Combined tool list for Anthropic
        tool_sessions = {}   # Map: tool_name → ClientSession for routing

        for config in server_configs:
            # Open connection
            read, write = await stack.enter_async_context(
                stdio_client(config["params"])
            )
            session = await stack.enter_async_context(
                ClientSession(read, write)
            )
            await session.initialize()

            # Get tools from this server
            tools_response = await session.list_tools()
            for tool in tools_response.tools:
                # Convert to Anthropic format
                all_tools.append({
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                })
                # Remember which session handles this tool
                tool_sessions[tool.name] = session

        print(f"Connected to {len(server_configs)} servers")
        print(f"Total tools available: {len(all_tools)}")
        print(f"Tool names: {list(tool_sessions.keys())}")

        # Run the agent with all aggregated tools
        client = anthropic.Anthropic()
        messages = [{"role": "user", "content": user_goal}]

        for step in range(15):
            response = client.messages.create(
                model="claude-opus-4-6",
                max_tokens=2048,
                tools=all_tools,
                messages=messages
            )

            if response.stop_reason == "end_turn":
                for block in response.content:
                    if hasattr(block, "text"):
                        return block.text
                return "Done"

            if response.stop_reason == "tool_use":
                messages.append({"role": "assistant", "content": response.content})
                tool_results = []

                for block in response.content:
                    if block.type == "tool_use":
                        # Route to the correct server's session
                        session = tool_sessions.get(block.name)
                        if not session:
                            result_text = f"Error: No server found for tool '{block.name}'"
                        else:
                            try:
                                mcp_result = await session.call_tool(block.name, block.input)
                                result_text = mcp_result.content[0].text
                            except Exception as e:
                                result_text = f"Tool error: {str(e)}"

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result_text
                        })

                messages.append({"role": "user", "content": tool_results})

    return "Agent completed"


asyncio.run(run_multi_server_agent(
    "Compare the weather in 3 major European capitals and tell me "
    "which one has the best conditions for a weekend trip."
))
```

---

## Expected Output

```
==================================================
Agent Goal: What's the weather like in Tokyo right now?
Available tools: ['get_current_weather', 'get_weather_forecast', 'compare_weather']
==================================================

--- Step 1 ---
Stop reason: tool_use
Calling tool: get_current_weather
Arguments: {'city': 'Tokyo'}
Result: Current weather in Tokyo:
- Conditions: Partly cloudy...

--- Step 2 ---
Stop reason: end_turn

Final answer: The current weather in Tokyo is partly cloudy with a temperature
of 18°C. Wind speed is 12 km/h with no significant precipitation.
It's a mild day, suitable for outdoor activities with a light jacket.
```

---

## Key Patterns Summary

| Pattern | Where It Appears |
|---|---|
| Connect to MCP server | `stdio_client(server_params)` + `ClientSession` |
| Initialize session | `await session.initialize()` |
| Get MCP tools | `await session.list_tools()` |
| Convert to Anthropic format | `{"name": ..., "description": ..., "input_schema": ...}` |
| Agent loop | `while stop_reason != "end_turn"` |
| Execute tool via MCP | `await session.call_tool(name, arguments)` |
| Return error as result | Text result with error message (not exception) |
| Multi-server routing | `tool_sessions[tool_name] = session` dictionary |

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [08 MCP Ecosystem](../08_MCP_Ecosystem/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [01 Model Serving](../../12_Production_AI/01_Model_Serving/Theory.md)