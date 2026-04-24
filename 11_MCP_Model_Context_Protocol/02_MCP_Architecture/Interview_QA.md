# Interview Q&A — MCP Architecture

## Beginner

**Q1: What are the three main components of MCP architecture?**

<details>
<summary>💡 Show Answer</summary>

> The three components are:
> - **Host** — the AI application that runs the model and presents the user interface (e.g., Claude Desktop)
> - **Client** — a component that lives inside the host and manages exactly one connection to one MCP server
> - **Server** — a separate external process that exposes tools, resources, or prompts to the AI model
>
> The host contains one or more clients, and each client connects to one server.

</details>

**Q2: What is JSON-RPC 2.0 and why does MCP use it?**

<details>
<summary>💡 Show Answer</summary>

> JSON-RPC 2.0 is a lightweight remote procedure call protocol that uses JSON as its data format. A message includes a method name, optional parameters, and an ID to match responses to requests. MCP uses it because it is simple, language-agnostic, well-understood, and works over any transport channel — the same message format works whether you are using stdio pipes or HTTP-based SSE.

</details>

**Q3: What happens during the MCP session initialization?**

<details>
<summary>💡 Show Answer</summary>

> When a client first connects to a server, it sends an `initialize` request containing the client's protocol version and its supported capabilities. The server responds with its own version and capabilities (the list of tools, resources, and prompts it can provide). The client then sends an `initialized` notification to confirm the handshake is complete. Only after this exchange can tool calls or resource reads happen.

</details>

---

## Intermediate

**Q4: Why does a host have multiple clients instead of one client for all servers?**

<details>
<summary>💡 Show Answer</summary>

> Each client maintains a stateful session with its server — it manages the connection lifecycle, keeps track of session state, and handles reconnection. If one client per server fails or disconnects, the other clients are unaffected. It also keeps the code clean: each client only knows about its own server's capabilities. A single client managing multiple servers would create tight coupling and make failure handling much more complex.

</details>

**Q5: Explain the difference between a Request and a Notification in MCP's JSON-RPC usage.**

<details>
<summary>💡 Show Answer</summary>

> A **Request** has an `id` field and expects a corresponding Response with the same `id`. The caller waits for the response before proceeding. A **Notification** has no `id` field and expects no response — it is fire-and-forget. The `initialized` message sent after the handshake is a notification. Server-side log messages and progress updates are also notifications. Requests are used when you need a result; notifications are used for informational messages.

</details>

**Q6: Can a server initiate communication with the client, or is it always the other way around?**

<details>
<summary>💡 Show Answer</summary>

> In MCP, the client initiates all requests — the client asks for tools, calls tools, reads resources, and so on. However, the server can send **notifications** to the client without being asked. These are one-way messages the server pushes proactively — for example, a progress update while a long tool operation runs, or a log message. The server cannot send a Request (which would require a response) — only Notifications.

</details>

---

## Advanced

**Q7: How does MCP architecture support multi-model or multi-agent scenarios?**

<details>
<summary>💡 Show Answer</summary>

> Because MCP servers are independent processes with a standard interface, multiple hosts (running different AI models or agents) can connect to the same server simultaneously. Each host-client-server connection is an independent session. An orchestrator agent could spawn sub-agents, and all of them could connect to the same filesystem server or database server. The server handles each session independently. This creates a clean, scalable architecture where shared tools are built once and reused across any number of agents.

</details>

**Q8: What are the implications of MCP's stateful session design compared to REST's stateless design?**

<details>
<summary>💡 Show Answer</summary>

> MCP's statefulness means the server can maintain context across multiple calls in the same conversation — for example, caching expensive query results, maintaining a database transaction, or tracking which files have been opened. This is more efficient for conversational AI use cases where many related tool calls happen in sequence. The tradeoff is that stateful servers are harder to scale horizontally (you need session affinity) and require proper cleanup when sessions end. For REST services, each request is independent, which makes horizontal scaling trivial but means no cross-call state is maintained.

</details>

**Q9: If you are building a production MCP server that handles hundreds of simultaneous AI sessions, what architectural considerations matter most?**

<details>
<summary>💡 Show Answer</summary>

> Several considerations matter:
> - **Transport choice**: SSE (HTTP-based) transport scales better than stdio for multi-tenant scenarios since you can put a load balancer in front
> - **Session isolation**: Each session must be isolated — shared mutable state across sessions creates race conditions
> - **Resource cleanup**: Sessions can end abruptly (network drop, client crash) — use server-side timeouts and cleanup handlers
> - **Authentication**: In a multi-tenant setting, you need to authenticate and authorize each session separately, since MCP itself has no built-in auth
> - **Observability**: Log every tool call with session ID, duration, and result for debugging
> - **Idempotency**: Design tools to be safe to retry — the AI may retry a tool call if it does not get a response

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | MCP architecture deep dive |
| [📄 Component_Breakdown.md](./Component_Breakdown.md) | Component breakdown |

⬅️ **Prev:** [01 MCP Fundamentals](../01_MCP_Fundamentals/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 Hosts Clients Servers](../03_Hosts_Clients_Servers/Theory.md)