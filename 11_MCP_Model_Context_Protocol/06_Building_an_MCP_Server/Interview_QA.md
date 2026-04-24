# Interview Q&A — Building an MCP Server

## Beginner

**Q1: What is the minimum code needed to create a working MCP server with one tool?**

<details>
<summary>💡 Show Answer</summary>

> You need five things:
> 1. Import the `mcp` SDK (`pip install mcp`)
> 2. Create a `Server` object: `app = Server("my-server")`
> 3. Implement `@app.list_tools()` — returns a list of `Tool` objects with name, description, and inputSchema
> 4. Implement `@app.call_tool()` — handles tool execution by name and returns `TextContent` results
> 5. Set up stdio transport in an async `main()` function and run with `asyncio.run(main())`
>
> The SDK handles all the JSON-RPC protocol details. You focus on the tool logic.

</details>

<br>

**Q2: How do you pass secrets (like API keys) to an MCP server?**

<details>
<summary>💡 Show Answer</summary>

> Use **environment variables** — never hardcode secrets in server files. In your server code, read them with `os.environ.get("MY_API_KEY")`. When configuring the server in Claude Desktop (or any host), set the env variables in the server's config section under `"env"`. This way the key is in the config file (which you can keep private), not in the server source code that might be shared or version-controlled.

</details>

<br>

**Q3: How do you test an MCP server during development?**

<details>
<summary>💡 Show Answer</summary>

> The best way is to use the **MCP Inspector** — an official development tool provided by Anthropic. Install it with `npx @modelcontextprotocol/inspector python your_server.py` and it opens a web UI where you can browse the server's tools, call them with custom arguments, read resources, and request prompts. This lets you test the full MCP interface without needing Claude Desktop. You can also write unit tests for individual tool handler functions directly, treating them as regular Python async functions.

</details>

---

## Intermediate

**Q4: Explain the relationship between `@app.list_tools()` and `@app.call_tool()`. Why are they separate?**

<details>
<summary>💡 Show Answer</summary>

> `@app.list_tools()` answers "what can you do?" — it returns the schema (name, description, inputSchema) for every tool the server offers. It is called once at session start (or when the client asks for the tool list).
>
> `@app.call_tool()` answers "do this specific thing" — it receives a tool name and arguments, executes the corresponding logic, and returns the result.
>
> They are separate because discovery and execution are different operations. A client needs to know what tools exist before it can call any of them. Separating declaration from implementation also keeps the code organized: the schema definitions are in one place and the business logic is in another.

</details>

<br>

**Q5: What should you return when a tool encounters an error?**

<details>
<summary>💡 Show Answer</summary>

> You should return a `TextContent` object with an error message — do not raise an unhandled exception. For example: `return [types.TextContent(type="text", text="Error: File not found: /path/to/file")]`. Returning the error as text content allows the AI model to read the error message and make a decision (retry with a different path, tell the user, try an alternative). An unhandled exception propagates as a generic JSON-RPC error that the AI cannot read or understand.

</details>

<br>

**Q6: How do you structure a server that needs to call an external REST API in its tool handlers?**

<details>
<summary>💡 Show Answer</summary>

> Best practices:
> 1. **Use async HTTP** — use `httpx` or `aiohttp` with `async/await` since your handlers are already async
> 2. **Read API key from env** — `api_key = os.environ.get("API_KEY")`
> 3. **Handle HTTP errors** — catch `httpx.HTTPStatusError` and return informative error messages
> 4. **Set timeouts** — external APIs can hang; set a reasonable timeout on HTTP calls
> 5. **Cache when appropriate** — if the API data does not change frequently, cache responses to avoid hitting rate limits
>
> Example pattern:
> ```python
> import httpx
> async with httpx.AsyncClient() as client:
>     response = await client.get(url, headers={"Authorization": f"Bearer {api_key}"}, timeout=10)
>     response.raise_for_status()
>     return [types.TextContent(type="text", text=response.text)]
> ```

</details>

---

## Advanced

**Q7: How would you design an MCP server for a use case that requires maintaining state across multiple tool calls in the same session?**

<details>
<summary>💡 Show Answer</summary>

> MCP sessions are stateful, so you can maintain per-session state in the server. The recommended pattern:
> 1. Create a session state dictionary or object at the module level or using a context variable
> 2. On `initialize`, create a new state object for the session
> 3. In tool handlers, read from and write to the session state
> 4. On session end (connection close), clean up the session state
>
> Example: a "shopping cart" MCP server that lets the AI add items and then checkout:
> ```python
> session_carts = {}  # session_id -> list of items
>
> @app.call_tool()
> async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
>     session_id = get_current_session_id()  # from context
>     if name == "add_item":
>         session_carts.setdefault(session_id, []).append(arguments["item"])
>         return [types.TextContent(type="text", text="Added")]
>     elif name == "checkout":
>         cart = session_carts.pop(session_id, [])
>         # process checkout...
> ```

</details>

<br>

**Q8: What is the difference between returning an error as `TextContent` versus using JSON-RPC error responses?**

<details>
<summary>💡 Show Answer</summary>

> **TextContent errors** (returning `[types.TextContent(type="text", text="Error: ...")]`) are tool-level errors. The tool call succeeded at the protocol level, but the tool's work failed for a domain reason (file not found, invalid argument value, API rate limited). The AI model receives this error message as the tool's result and can reason about it, retry with different arguments, or tell the user what went wrong.
>
> **JSON-RPC errors** (raised by the SDK as exceptions like `McpError`) are protocol-level errors. They indicate something went wrong at the MCP level — invalid method, internal server error, malformed request. The AI typically cannot reason about these; the host shows a generic failure. These should be rare in production.
>
> Rule of thumb: if the tool executed and produced an outcome (even a bad one), return TextContent. If something went wrong before the tool even started executing, let the SDK handle it as a protocol error.

</details>

<br>

**Q9: How would you implement a tool that returns streaming results — for example, a tool that runs a long query and streams rows as they arrive?**

<details>
<summary>💡 Show Answer</summary>

> MCP itself does not have a built-in streaming result type for tool calls — a `tools/call` response is expected to return a complete result. For streaming-style workflows, you have a few options:
>
> 1. **Progress notifications**: Use `server.request_context.session.send_log_message()` to send progress notifications during execution. The client/host can display these to the user while waiting.
>
> 2. **Pagination**: Design the tool to return N results at a time with a `cursor` argument. The AI calls the tool multiple times, each time passing the cursor from the previous call, until all results are retrieved.
>
> 3. **Background execution + polling**: Return a `job_id` immediately, then have a separate `get_job_result(job_id)` tool the AI can poll. This works well for very long-running operations.
>
> Genuine streaming (line by line) is better suited for a direct streaming API rather than MCP tools.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |
| [📄 Server_Implementation.md](./Server_Implementation.md) | Full server implementation guide |
| [📄 Step_by_Step.md](./Step_by_Step.md) | Step-by-step build guide |

⬅️ **Prev:** [05 Transport Layer](../05_Transport_Layer/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [07 Security and Permissions](../07_Security_and_Permissions/Theory.md)