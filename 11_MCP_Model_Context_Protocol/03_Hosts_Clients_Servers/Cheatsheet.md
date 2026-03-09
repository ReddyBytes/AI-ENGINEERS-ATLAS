# Cheatsheet — Hosts, Clients, and Servers

**In MCP, every entity plays one of three roles: Host (runs the AI), Client (speaks the protocol), or Server (provides capabilities).**

---

## Key Terms 📋

| Term | Definition |
|---|---|
| **Host** | The AI application — owns the model, UI, and user conversation |
| **Client** | Protocol handler inside the host; manages one server connection |
| **Server** | External process or service that exposes tools/resources/prompts |
| **Subprocess** | How stdio-transport servers run — spawned as a child process by the host |
| **Session** | A stateful connection from one client to one server |
| **Capabilities** | What a server can offer — declared during `initialize` |

---

## Responsibilities by Role

| Responsibility | Host | Client | Server |
|---|---|---|---|
| Run the AI model | YES | NO | NO |
| Manage user interface | YES | NO | NO |
| Read MCP config | YES | NO | NO |
| Create/manage clients | YES | NO | NO |
| Send `initialize` | NO | YES | NO |
| Serialize JSON-RPC | NO | YES | NO |
| Handle session state | NO | YES | NO |
| Declare capabilities | NO | NO | YES |
| Execute tool logic | NO | NO | YES |
| Read/write filesystem | NO | NO | YES |
| Call external APIs | NO | NO | YES |

---

## The 1:N:1 Relationship

```
1 Host
  has N Clients  (one per server it connects to)
    each Client manages 1 Server
```

---

## Host Examples

| Host | Type | How It Connects |
|---|---|---|
| Claude Desktop | Desktop app | Reads claude_desktop_config.json |
| VS Code Copilot | IDE extension | Reads .vscode/mcp.json |
| Custom Python app | Your code | You create ClientSession objects |
| Jupyter notebook | Interactive | You create clients programmatically |

---

## Server Examples

| Server | What It Provides | Transport |
|---|---|---|
| Filesystem server | read/write/list files | stdio |
| GitHub MCP server | repos, PRs, issues | stdio |
| PostgreSQL server | SQL query execution | stdio |
| Web search server | internet search results | stdio or SSE |
| Custom API server | your company's internal API | SSE |

---

## What Happens When Host Starts

```
1. Host reads config (e.g., claude_desktop_config.json)
2. For each server entry → create a Client
3. Client starts server subprocess (stdio) or connects (SSE)
4. Client sends initialize → server returns capabilities
5. Host aggregates all capabilities into AI model context
6. User interaction begins
```

---

## Golden Rules 🏆

- The host is the application users interact with — it owns the model and conversation
- A client is NOT a separate program — it is code inside the host process
- Every client manages EXACTLY ONE server connection
- A host can have as many clients as it needs (connect to 10 servers = 10 clients)
- Servers are ideally single-purpose — one domain, one server
- The server never contacts the host first — it only responds to client requests (except notifications)
- Servers should not know or care which AI model is on the other side

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |

⬅️ **Prev:** [02 MCP Architecture](../02_MCP_Architecture/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 Tools Resources Prompts](../04_Tools_Resources_Prompts/Theory.md)