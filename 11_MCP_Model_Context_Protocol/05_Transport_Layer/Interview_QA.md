# Interview Q&A — Transport Layer

## Beginner

**Q1: What are the two MCP transport types and what is the basic difference between them?**

> The two transports are:
> - **stdio** (standard input/output): The host spawns the server as a subprocess. Messages travel through OS pipes — the client writes requests to the server's stdin, the server writes responses to its stdout.
> - **SSE** (Server-Sent Events): The server runs as an HTTP service. The client connects to an SSE endpoint to receive a persistent event stream, and sends requests via HTTP POST to a separate endpoint.
>
> stdio is simpler and best for local tools. SSE is better for remote servers that need to serve multiple clients.

**Q2: Why should you never use print() to write debug messages in a stdio MCP server?**

> In stdio transport, the server communicates with the client through stdout. Every byte written to stdout is treated as part of a JSON-RPC message. If you `print("debug info")`, the client receives "debug info" and tries to parse it as JSON — which fails, causing an error or connection drop. The correct approach is to write debug messages to stderr instead: `print("debug info", file=sys.stderr)`. stderr is separate from stdout and does not interfere with the JSON-RPC channel.

**Q3: Can the same MCP server code work with both stdio and SSE transports?**

> Yes. The server's tool, resource, and prompt logic is completely separate from the transport mechanism. The only part that changes is the startup code — whether you use `stdio_server()` for subprocess mode or set up an HTTP server for SSE mode. You can even write your server once and add both startup modes with a command-line flag to choose between them.

---

## Intermediate

**Q4: Explain why stdio transport cannot be used for a server shared by multiple users.**

> With stdio transport, the host launches the server as a subprocess using OS pipes. Each client connection creates a new subprocess — meaning a dedicated server process per client. If 100 users all need the same database server, you would have 100 separate database server processes running. This is wasteful, does not scale, and makes it impossible to share state (like a connection pool) across clients. For shared, multi-user servers, SSE (HTTP-based) transport is used instead — a single HTTP server handles requests from many clients concurrently.

**Q5: How does SSE (Server-Sent Events) actually work in MCP? Why use SSE rather than regular HTTP request/response?**

> SSE is a web standard that allows a server to push multiple events to a client over a single, long-lived HTTP connection. In MCP's SSE transport:
> - The client opens a connection to `/sse` and keeps it open — this is the "server pushes to client" channel
> - The client sends requests via HTTP POST to `/message` — this is the "client requests" channel
> - The server responds to each POST by sending an SSE event on the open `/sse` stream
>
> Regular HTTP request/response cannot be used alone because the server also needs to send notifications (like progress updates or resource change events) that are not triggered by a client request. SSE provides the persistent connection needed for these server-initiated messages.

**Q6: What happens to a stdio server when the host application closes?**

> When the host application closes, it terminates the subprocess it spawned (the stdio server). The server process is killed by the OS when its parent process (the host) exits. The stdin/stdout pipes are closed, and any in-flight operations are interrupted. This is expected behavior — stdio servers are designed to be ephemeral and tied to the host's lifecycle. For servers that need to persist and maintain state across host sessions, SSE transport is more appropriate.

---

## Advanced

**Q7: How would you implement reconnection logic for an SSE MCP client?**

> SSE connections can drop due to network issues, server restarts, or timeouts. A production SSE client should:
> 1. **Detect disconnection** — catch connection errors or EOF on the SSE stream
> 2. **Implement exponential backoff** — wait 1s, then 2s, then 4s, etc. before retrying (up to a max)
> 3. **Re-initialize on reconnect** — after reconnecting, send `initialize` again since the server session is new
> 4. **Re-register pending requests** — any tool calls that were in-flight should be retried or errored
> 5. **Notify the host** — if reconnection fails after N attempts, the host should remove this server's tools from the AI model's context and notify the user
>
> The MCP SDK handles some of this automatically, but production systems should add monitoring and alerting for repeated reconnection failures.

**Q8: Design a production deployment for an MCP server that needs to serve thousands of concurrent AI sessions. Which transport would you choose and what infrastructure would you need?**

> For thousands of concurrent sessions, I would use **SSE transport** and:
>
> - **HTTP server**: Use a high-performance async Python server (FastAPI + uvicorn or Starlette) or Go/Node.js
> - **Load balancer**: Put multiple server instances behind a load balancer (nginx, AWS ALB)
> - **Session affinity (sticky sessions)**: SSE requires the same server instance to handle both the SSE connection and the corresponding POST messages. Configure the load balancer to route a client to the same instance.
> - **Horizontal scaling**: Run multiple server instances; auto-scale based on connection count
> - **Health checks**: Expose `/health` endpoint; load balancer automatically removes unhealthy instances
> - **Authentication**: API key or JWT in the initial SSE connection headers; verify before allowing a session
> - **Connection limits**: Implement server-side connection limits and timeouts for idle sessions
> - **Observability**: Log every session start/end, every tool call, and error rates

**Q9: Is there any scenario where you would intentionally limit an MCP server to only support one transport type, rather than supporting both?**

> Yes, there are valid reasons:
>
> - **Security**: A server that reads sensitive local files should only support stdio. If it supported SSE, a remote attacker could potentially connect to it and read your files. Restricting to stdio ensures only local processes (the host on your machine) can connect.
>
> - **Simplicity**: A personal tool that will only ever be used by one person on one machine gains nothing from SSE support. Keeping it stdio-only reduces code complexity and attack surface.
>
> - **Enterprise policy**: A shared enterprise server might intentionally only support SSE with authentication, explicitly blocking stdio to prevent unsecured subprocess-based access.
>
> The choice of transport is a security and deployment decision, not just a technical one.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |

⬅️ **Prev:** [04 Tools Resources Prompts](../04_Tools_Resources_Prompts/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [06 Building an MCP Server](../06_Building_an_MCP_Server/Theory.md)