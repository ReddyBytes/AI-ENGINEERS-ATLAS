# Cheatsheet — MCP Architecture

**MCP Architecture** is the three-layer pattern of Host → Client → Server that enables AI applications to connect to external tools using a standardized protocol.

---

## Key Terms 📋

| Term | Definition |
|---|---|
| **Host** | The AI application (Claude Desktop, VS Code, custom app) that runs the model and UI |
| **Client** | Component inside the host; manages one connection to one MCP server |
| **Server** | Separate process that exposes tools, resources, and prompts via MCP |
| **JSON-RPC 2.0** | The message format for all MCP communication (method + params + id) |
| **Capabilities** | What a server can do — declared during the `initialize` handshake |
| **Session** | A stateful connection from client connect to client disconnect |
| **Transport** | The channel used — stdio (subprocess pipes) or SSE (HTTP) |

---

## Architecture Layout

```
Host
├── AI Model (Claude)
├── MCP Client 1  ──stdio──►  MCP Server 1 (Filesystem)
├── MCP Client 2  ──stdio──►  MCP Server 2 (GitHub)
└── MCP Client 3  ──SSE───►  MCP Server 3 (Database API)
```

---

## Session Lifecycle

```
1. Host starts server process (or connects via HTTP)
2. Client sends:  initialize {protocolVersion, capabilities}
3. Server replies: {serverInfo, capabilities}
4. Client sends:  initialized (notification — no response needed)
5. Normal operation: tools/list, tools/call, resources/read, etc.
6. Session ends: connection closes, server may shut down
```

---

## JSON-RPC 2.0 Message Structure

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "read_file",
    "arguments": { "path": "/home/user/notes.txt" }
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [{ "type": "text", "text": "file contents here..." }]
  }
}
```

**Error:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": { "code": -32600, "message": "File not found" }
}
```

---

## Core MCP Methods

| Method | Caller | Purpose |
|---|---|---|
| `initialize` | Client | Start session, exchange versions + capabilities |
| `initialized` | Client | Notify server initialization is complete |
| `tools/list` | Client | Get list of available tools |
| `tools/call` | Client | Execute a specific tool |
| `resources/list` | Client | Get list of available resources |
| `resources/read` | Client | Read a specific resource |
| `prompts/list` | Client | Get list of available prompts |
| `prompts/get` | Client | Retrieve a prompt with arguments filled in |
| `notifications/message` | Server | Server sends a log/progress notification |

---

## When to Use / When NOT to Use

**One client per server** — always. A client manages exactly one server relationship.

**Multiple servers** — encouraged. Build focused single-purpose servers and connect many to one host.

**Do NOT** make the host talk directly to a server without a client. The client is not optional.

---

## Golden Rules 🏆

- Host = the AI app; Client = protocol handler inside the host; Server = tool provider (external process)
- One client manages exactly one server; a host can have unlimited clients
- All communication is JSON-RPC 2.0 — request/response or notification
- The initialize handshake MUST complete before any tool calls
- Server capabilities are declared once at init time and do not change during a session
- The server never calls the host — communication is always client-initiated (except notifications)
- Design servers to be stateless-friendly even though the session is stateful

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | MCP architecture deep dive |
| [📄 Component_Breakdown.md](./Component_Breakdown.md) | Component breakdown |

⬅️ **Prev:** [01 MCP Fundamentals](../01_MCP_Fundamentals/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 Hosts Clients Servers](../03_Hosts_Clients_Servers/Theory.md)