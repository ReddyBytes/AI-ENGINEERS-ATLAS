# Interview Q&A — Hosts, Clients, and Servers

## Beginner

**Q1: In MCP, what is the difference between a Host and a Server?**

> The **Host** is the AI application that the user interacts with — it runs the AI model and manages the user interface. Examples include Claude Desktop or a custom Python app. The **Server** is an external process that provides specific capabilities (tools, resources, prompts) — like a filesystem server or a GitHub server. The host consumes what the server provides. The host is the "brain"; the server is the "hands."

**Q2: What does the MCP Client do, and where does it live?**

> The MCP Client is a component that lives inside the Host application (not as a separate program). Its job is to handle the MCP protocol details: it sends the `initialize` request to the server, serializes requests into JSON-RPC format, deserializes responses, and manages the session lifecycle. Think of it as the protocol adapter layer inside your AI app. Every server connection needs its own dedicated client.

**Q3: Can a Host connect to more than one Server?**

> Yes — that is one of MCP's key strengths. A host creates one client per server, so connecting to five servers means having five clients running simultaneously inside the host. Each client independently manages its server connection. The host aggregates capabilities from all servers and gives the AI model access to all of them at once.

---

## Intermediate

**Q4: Why is the "one client per server" design important? What would go wrong if one client managed multiple servers?**

> The one-client-per-server design keeps things cleanly isolated. Each session has its own state, its own lifecycle, and its own error handling. If you had one client managing multiple servers, a disconnection from one server would potentially disrupt all servers. It would also be harder to route tool calls correctly and harder to restart failed connections. The isolation means you can add, remove, or restart individual server connections without affecting the others.

**Q5: What is the difference between a server running in stdio mode versus being a remote service?**

> In **stdio mode**, the host spawns the server as a subprocess. Communication happens through stdin and stdout pipes — the host writes requests to stdin and reads responses from stdout. The server only exists while the host is running. This is ideal for local tools.
>
> As a **remote service** (SSE transport), the server runs as an HTTP service — either on localhost or on a remote machine. The client connects via HTTP and uses Server-Sent Events to receive responses. This server exists independently of any particular host and can serve multiple clients simultaneously. This is better for shared company services or web-based tools.

**Q6: Who is responsible for deciding which tools the AI model can use — the host, the client, or the server?**

> All three play a role:
> - The **server** defines which tools exist and declares them during initialization
> - The **client** retrieves the tool list and passes it to the host
> - The **host** decides which tools to inject into the AI model's context (it could filter some out based on security policy)
> - The **AI model** decides when to actually call a tool based on the user's request
>
> The server creates tools, but the host controls what the model sees, and the model decides what to call.

---

## Advanced

**Q7: How would you design a system where multiple AI applications share the same MCP server?**

> Use the **SSE transport** for the shared server. Instead of each host spawning its own subprocess, the server runs as a persistent HTTP service. Multiple hosts each create a client that connects to the same HTTP endpoint. Each client gets its own session — the server handles each session independently, maintaining separate state per session.
>
> Key considerations:
> - Session isolation: each client's state must not bleed into another client's session
> - Authentication: each connecting host should authenticate (e.g., using an API key in the HTTP request)
> - Concurrency: the server must be thread-safe or use async handling for simultaneous requests from multiple clients
> - Cleanup: handle disconnected sessions gracefully with timeouts

**Q8: Imagine you are building an AI coding assistant that needs to read files, run code, and search the web. How would you design the host-client-server architecture?**

> I would build three separate single-purpose servers:
> - **Filesystem Server** (stdio): exposes `read_file`, `write_file`, `list_directory`, `search_in_files`
> - **Code Execution Server** (stdio): exposes `run_python`, `run_bash` with a sandbox
> - **Web Search Server** (SSE, since it calls a remote API): exposes `search_web`, `fetch_page`
>
> The host (the coding assistant app) creates three clients, one per server. The AI model has access to all three tool sets simultaneously. Each server is kept simple and focused, making it easy to test and maintain. If the code execution server has a security issue, I can fix it without touching the other servers.

**Q9: What happens if a server crashes mid-session? How should the host/client handle it?**

> When a server crashes, the client's connection breaks — it will receive an EOF on stdio or a connection close on SSE. The client should:
> 1. Detect the disconnection via an error or connection close
> 2. Notify the host that this server is unavailable
> 3. Optionally attempt reconnection with exponential backoff
> 4. Remove the server's tools from the AI model's available tools
>
> Any in-flight tool calls should return an error result to the AI model so it can decide how to proceed (retry, use a different approach, or tell the user there was an error). The host should not crash — the failure of one server should not bring down the entire AI session.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |

⬅️ **Prev:** [02 MCP Architecture](../02_MCP_Architecture/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 Tools Resources Prompts](../04_Tools_Resources_Prompts/Theory.md)