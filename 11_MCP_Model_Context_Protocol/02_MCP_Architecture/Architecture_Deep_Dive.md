# Architecture Deep Dive — MCP

This document provides a detailed technical look at MCP's architecture — the full message flow, session lifecycle, capabilities negotiation, and transport options.

---

## Full System Architecture Diagram

```mermaid
graph TB
    subgraph HOST["🖥️ HOST PROCESS (e.g. Claude Desktop)"]
        UI["User Interface"]
        MODEL["AI Model (Claude)"]
        AGENT["Agent Loop\n(tool selection, response)"]
        C1["MCP Client 1"]
        C2["MCP Client 2"]
        C3["MCP Client 3"]
        UI --> MODEL
        MODEL --> AGENT
        AGENT --> C1
        AGENT --> C2
        AGENT --> C3
    end

    subgraph S1["🗂️ SERVER PROCESS 1"]
        SH1["Server Handler"]
        FS["Filesystem\nOperations"]
        SH1 --> FS
    end

    subgraph S2["🐙 SERVER PROCESS 2"]
        SH2["Server Handler"]
        GH["GitHub API\nCalls"]
        SH2 --> GH
    end

    subgraph S3["🌐 REMOTE SERVER 3"]
        SH3["HTTP Server"]
        DB["Database\nQueries"]
        SH3 --> DB
    end

    C1 <-->|"JSON-RPC\nover stdio"| SH1
    C2 <-->|"JSON-RPC\nover stdio"| SH2
    C3 <-->|"JSON-RPC\nover SSE/HTTP"| SH3
```

---

## Session Lifecycle — Full Detail

```mermaid
sequenceDiagram
    participant Host
    participant Client
    participant Server

    Note over Host,Server: Phase 1 — Connection Setup
    Host->>Server: Start subprocess (or HTTP connect)
    Client->>Server: {"jsonrpc":"2.0","id":1,"method":"initialize",<br/>"params":{"protocolVersion":"2024-11-05","capabilities":{...}}}
    Server-->>Client: {"jsonrpc":"2.0","id":1,"result":{<br/>"serverInfo":{"name":"filesystem","version":"1.0"},<br/>"capabilities":{"tools":{},"resources":{}}}}
    Client->>Server: {"jsonrpc":"2.0","method":"initialized"} (notification, no id)

    Note over Host,Server: Phase 2 — Discovery
    Client->>Server: {"jsonrpc":"2.0","id":2,"method":"tools/list"}
    Server-->>Client: {"result":{"tools":[{"name":"read_file","description":"...","inputSchema":{...}}]}}
    Client->>Server: {"jsonrpc":"2.0","id":3,"method":"resources/list"}
    Server-->>Client: {"result":{"resources":[{"uri":"file:///home/","name":"Home Directory"}]}}

    Note over Host,Server: Phase 3 — Normal Operation
    Host->>Client: Call tool: read_file with path="/notes.txt"
    Client->>Server: {"jsonrpc":"2.0","id":4,"method":"tools/call",<br/>"params":{"name":"read_file","arguments":{"path":"/notes.txt"}}}
    Server-->>Client: {"result":{"content":[{"type":"text","text":"note contents..."}]}}
    Client-->>Host: Tool result: "note contents..."

    Note over Host,Server: Phase 4 — Session End
    Host->>Client: Disconnect
    Client->>Server: Connection closes
    Server->>Server: Cleanup session state
```

---

## Capabilities Negotiation

During `initialize`, both sides declare what they support. This allows gradual protocol evolution.

**Client capabilities (what the host supports):**
```json
{
  "capabilities": {
    "sampling": {},
    "roots": { "listChanged": true }
  }
}
```

**Server capabilities (what the server offers):**
```json
{
  "capabilities": {
    "tools": { "listChanged": false },
    "resources": { "listChanged": true, "subscribe": true },
    "prompts": { "listChanged": false },
    "logging": {}
  }
}
```

**Capability meaning:**
| Capability | Meaning |
|---|---|
| `tools` | Server exposes callable tools |
| `tools.listChanged` | Server will notify if tool list changes |
| `resources` | Server exposes readable resources |
| `resources.subscribe` | Client can subscribe to resource change events |
| `prompts` | Server exposes prompt templates |
| `logging` | Server can send log notifications |
| `sampling` | Client supports being asked to run AI completions |
| `roots` | Client exposes filesystem roots (for servers that browse local files) |

---

## Transport Comparison

### stdio Transport

```
Host Process
│
├── spawns: python filesystem_server.py
│                    │
│   stdin  ─────────►│  (JSON-RPC requests from client)
│   stdout ◄─────────│  (JSON-RPC responses from server)
```

- Server runs as a subprocess
- Communication via OS pipes (stdin/stdout)
- One client = one subprocess
- Best for: local tools, CLI tools, development

### SSE Transport (Server-Sent Events)

```
Host Process                        Remote/Local HTTP Server
│                                   │
├── MCP Client  ──HTTP POST──────►  │  /message endpoint (client sends)
│               ◄──SSE stream────   │  /sse endpoint (server sends events)
```

- Server runs as an HTTP server
- Client sends requests via HTTP POST
- Server sends responses + notifications via SSE stream
- Best for: remote servers, multi-tenant servers, web services

---

## Tool Call Flow — Detailed

```mermaid
sequenceDiagram
    participant LLM as AI Model
    participant Host
    participant Client
    participant Server

    LLM->>Host: I want to call: read_file({"path": "/config.json"})
    Host->>Host: Validate: is "read_file" in known tools?
    Host->>Client: Route to Client 1 (owns filesystem server)
    Client->>Server: tools/call {name:"read_file", arguments:{"path":"/config.json"}}
    Server->>Server: Execute: open /config.json, read contents
    Server-->>Client: {content:[{type:"text", text:"{\"version\":\"1.0\"...}"}]}
    Client-->>Host: Tool result received
    Host-->>LLM: Tool result: {"version": "1.0", ...}
    LLM->>Host: Generate final response using tool result
```

---

## Error Handling in Architecture

MCP defines standard JSON-RPC error codes plus MCP-specific ones:

| Code | Meaning |
|---|---|
| `-32700` | Parse error — invalid JSON |
| `-32600` | Invalid Request — malformed JSON-RPC |
| `-32601` | Method not found |
| `-32602` | Invalid params |
| `-32603` | Internal error |
| `-32001` | MCP: Resource not found |
| `-32002` | MCP: Tool execution error |

Errors return as:
```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "error": {
    "code": -32002,
    "message": "Tool execution failed: file not found"
  }
}
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Architecture_Deep_Dive.md** | ← you are here |
| [📄 Component_Breakdown.md](./Component_Breakdown.md) | Component breakdown |

⬅️ **Prev:** [01 MCP Fundamentals](../01_MCP_Fundamentals/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 Hosts Clients Servers](../03_Hosts_Clients_Servers/Theory.md)