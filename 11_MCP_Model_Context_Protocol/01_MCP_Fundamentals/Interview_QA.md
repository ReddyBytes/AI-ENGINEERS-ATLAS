# Interview Q&A — MCP Fundamentals

## Beginner

**Q1: What is MCP and why was it created?**

<details>
<summary>💡 Show Answer</summary>

> MCP stands for Model Context Protocol. It is an open protocol created by Anthropic that standardizes how AI applications connect to external tools and data sources. It was created because every AI application previously needed custom, one-off integrations for each tool — MCP provides a single standard so that any MCP server works with any MCP-compatible client, similar to how USB standardized device connectors.

</details>

<br>

**Q2: What are the three primitives in MCP?**

<details>
<summary>💡 Show Answer</summary>

> The three MCP primitives are:
> - **Tools** — actions the AI can perform (like calling a function — write a file, query a database, send an email)
> - **Resources** — read-only data the AI can access (like a filesystem — file contents, database records, API responses)
> - **Prompts** — reusable, parameterized prompt templates that encode pre-built workflows

</details>

<br>

**Q3: What is the difference between an MCP host and an MCP server?**

<details>
<summary>💡 Show Answer</summary>

> The **host** is the AI application that the user interacts with — for example Claude Desktop, VS Code with Copilot, or a custom app you build. The host contains the AI model and the user interface. The **server** is a separate process that exposes specific capabilities (tools, resources, prompts) — for example a filesystem server, a GitHub server, or a database server. The host consumes what the server provides.

</details>

---

## Intermediate

**Q4: How is MCP different from OpenAI-style function calling?**

<details>
<summary>💡 Show Answer</summary>

> Function calling is a feature baked into a specific AI model's API — you define functions in your API call and that model can choose to call them. MCP is a protocol at the application layer — it is model-agnostic and transport-agnostic. The same MCP server works with Claude, or any other AI that implements an MCP client. MCP also supports stateful sessions, resource reading, and prompt templates — things function calling does not provide. MCP is more like a published API standard whereas function calling is like an in-process callback.

</details>

<br>

**Q5: What message format does MCP use and why?**

<details>
<summary>💡 Show Answer</summary>

> MCP uses **JSON-RPC 2.0** as its message format. JSON-RPC is a lightweight remote procedure call protocol using JSON. It was chosen because it is simple, widely understood, language-agnostic, and works well over both stdio (standard input/output) and HTTP-based transports. Every MCP message is a JSON object with a method name, optional parameters, and an ID for matching responses to requests.

</details>

<br>

**Q6: Can a single MCP server work with multiple different AI models or applications?**

<details>
<summary>💡 Show Answer</summary>

> Yes, that is the entire point of MCP. A single MCP server — say a PostgreSQL database server — can be connected to Claude Desktop, a VS Code extension, a custom Python application, or any other host that implements an MCP client. The server does not know or care which AI model is on the other end. This portability is MCP's core value proposition.

</details>

---

## Advanced

**Q7: How does MCP handle capabilities negotiation and versioning?**

<details>
<summary>💡 Show Answer</summary>

> When a client connects to an MCP server, the first message is an `initialize` request. This message includes the client's protocol version and the capabilities it supports. The server responds with its own protocol version and its capabilities. Both sides then know what features are available and can gracefully handle cases where one side supports something the other does not. This negotiation happens once at the start of every session before any tools or resources are accessed.

</details>

<br>

**Q8: What security model does MCP use for controlling what a server can access?**

<details>
<summary>💡 Show Answer</summary>

> MCP itself is a protocol — it does not enforce security policies. Instead, security is the responsibility of the host and the human user. The host decides which MCP servers to connect to, and the user is expected to only connect to servers they trust. For tool calls that have destructive or irreversible consequences, best practice is for the host to show the user a confirmation dialog before executing. The principle of least privilege should guide server design — each server should only expose the tools it absolutely needs for its purpose.

</details>

<br>

**Q9: How does MCP relate to the broader trend of AI agents? Why does it matter architecturally?**

<details>
<summary>💡 Show Answer</summary>

> MCP is foundational infrastructure for AI agents. An agent is an AI that can take sequences of actions to complete long-horizon tasks — but to take real-world actions, it needs reliable tool access. MCP provides a clean architectural boundary: the agent loop (planning, reasoning, tool selection) lives in the host, while the tool implementations live in MCP servers. This separation means you can upgrade your AI model without touching your tool code, and you can reuse tools across different agents. Multi-agent systems can share MCP servers, and the standardization reduces the "integration tax" that previously made building capable agents so labor-intensive.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 MCP_vs_REST_API.md](./MCP_vs_REST_API.md) | MCP vs REST API comparison |

⬅️ **Prev:** [09 Build an Agent](../../10_AI_Agents/09_Build_an_Agent/Project_Guide.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [02 MCP Architecture](../02_MCP_Architecture/Theory.md)