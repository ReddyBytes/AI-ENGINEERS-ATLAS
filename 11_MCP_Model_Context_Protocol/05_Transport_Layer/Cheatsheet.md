# Cheatsheet — Transport Layer

**The MCP transport layer defines HOW messages travel between client and server. Two options: stdio (subprocess pipes) and SSE (HTTP-based).**

---

## Key Terms 📋

| Term | Definition |
|---|---|
| **Transport** | The physical mechanism that carries JSON-RPC messages |
| **stdio** | Standard input/output — server runs as a subprocess, messages via pipes |
| **SSE** | Server-Sent Events — HTTP-based transport with POST requests and event stream |
| **stdin** | Standard input — the pipe the client writes requests to (stdio transport) |
| **stdout** | Standard output — the pipe the server writes responses to (stdio transport) |
| **SSE stream** | A persistent HTTP connection over which the server pushes events |
| **Subprocess** | A child process spawned by the host; used in stdio transport |

---

## stdio vs SSE Comparison

| | stdio | SSE |
|---|---|---|
| **Server startup** | Host spawns subprocess | Server already running |
| **Client sends via** | stdin pipe | HTTP POST to `/message` |
| **Server sends via** | stdout pipe | SSE events stream |
| **Server lifetime** | Lives while host is running | Independent of host |
| **Clients per server** | One (one process per client) | Many (one server, many clients) |
| **Network required** | No | Yes (HTTP) |
| **Setup complexity** | Simple | Requires HTTP server |
| **Best for** | Local tools, development | Remote services, multi-user |
| **Debugging** | Easy (run server directly) | Need HTTP tooling |
| **Production scale** | Small (personal tools) | Large (enterprise, shared) |

---

## stdio Setup Pattern (Python)

```python
# Server side — runs over stdio
import asyncio
import mcp.server.stdio
from mcp.server import Server
from mcp.server.models import InitializationOptions

app = Server("my-server")

# ... define tools, resources, prompts ...

async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, InitializationOptions(...))

asyncio.run(main())
```

```json
// Claude Desktop config (stdio)
{
  "mcpServers": {
    "my-server": {
      "command": "python",
      "args": ["/path/to/server.py"],
      "env": { "SOME_API_KEY": "value" }
    }
  }
}
```

---

## SSE Setup Pattern (Python)

```python
# Server side — runs over SSE using FastAPI
from fastapi import FastAPI
from mcp.server.sse import SseServerTransport
from mcp.server import Server
import uvicorn

app = Server("my-server")
# ... define tools, resources, prompts ...

fastapi_app = FastAPI()
sse = SseServerTransport("/messages")

@fastapi_app.get("/sse")
async def sse_endpoint(request):
    async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
        await app.run(streams[0], streams[1], app.create_initialization_options())

@fastapi_app.post("/messages")
async def handle_messages(request):
    await sse.handle_post_message(request.scope, request.receive, request._send)

uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)
```

```json
// Claude Desktop config (SSE)
{
  "mcpServers": {
    "my-remote-server": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

---

## Critical Debug Rule for stdio

```
NEVER print() to stdout in a stdio server.
stdout is the JSON-RPC channel — any non-JSON output breaks the client.

Instead use:
import sys
print("debug message", file=sys.stderr)
```

---

## When to Use Which

**Use stdio when:**
- The server is a personal tool on your local machine
- You are developing and testing a new server
- The server needs filesystem or OS access on the user's machine
- You want simple deployment (just run a Python script)

**Use SSE when:**
- Multiple users or AI apps need to share the same server
- The server is deployed on a remote machine or cloud
- You need the server to run independently of any particular client
- You need horizontal scaling or load balancing

---

## Golden Rules 🏆

- stdio servers write only JSON-RPC messages to stdout — never plain text
- Use stderr for all logging and debug output in stdio servers
- SSE servers must handle dropped connections gracefully
- One stdio server process = one client connection maximum
- SSE servers can handle unlimited concurrent clients (resource permitting)
- The JSON-RPC message format is IDENTICAL between stdio and SSE — only the transport changes
- Test with stdio locally; deploy with SSE for production shared services

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |

⬅️ **Prev:** [04 Tools Resources Prompts](../04_Tools_Resources_Prompts/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [06 Building an MCP Server](../06_Building_an_MCP_Server/Theory.md)