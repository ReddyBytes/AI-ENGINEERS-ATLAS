# Component Breakdown — MCP

A complete reference table for every component in the MCP architecture — what each one is, what it does, a real-world analogy, and concrete examples.

---

## Component Reference Table

| Component | What It Is | What It Does | Real-World Analogy | Examples |
|---|---|---|---|---|
| **Host** | The AI application | Runs the AI model, manages clients, presents UI | A company that hires contractors | Claude Desktop, VS Code, custom Python app |
| **Client** | Protocol handler inside the host | Manages one session with one server; routes requests and responses | A staffing agency that manages one contractor pool | `StdioClientTransport` in Python MCP SDK |
| **Server** | External process with capabilities | Exposes tools, resources, prompts via MCP protocol | A specialist contractor office | `filesystem-server`, `github-mcp-server` |
| **Tool** | A callable function on the server | Performs an action; takes inputs, returns results | A power tool in a contractor's toolkit | `read_file`, `create_pr`, `run_query` |
| **Resource** | A readable data endpoint | Provides read-only data via URI | A reference manual on a shelf | `file:///home/user/notes.txt`, `db://customers/123` |
| **Prompt** | A reusable prompt template | Fills in a pre-written prompt with arguments | A form template with blanks to fill in | "code_review", "summarize_doc", "write_tests" |
| **Transport** | The communication channel | Carries JSON-RPC messages between client and server | The phone line between the company and contractor | stdio (pipes), SSE (HTTP) |
| **Session** | A stateful connection lifetime | The period from initialize to disconnect | An employment contract | Start when host connects, end when host disconnects |

---

## Host — In Detail

The **Host** is the application the user sees and interacts with. It is responsible for:

- Starting and stopping server processes
- Creating and managing Client instances
- Running the AI model (the language model)
- Injecting available tool descriptions into the model's context
- Routing tool call decisions from the model to the right client
- Presenting results back to the user

The host is the "brain" of the whole system. Without the host, there is no AI model and no conversation.

**What hosts look like in code:**
```python
# A minimal host in Python (pseudocode)
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        tools = await session.list_tools()
        # Now pass tools to the AI model
```

---

## Client — In Detail

The **Client** is embedded inside the host. Each client manages exactly one server connection. It is responsible for:

- Sending the `initialize` request on startup
- Keeping the session alive
- Serializing requests to JSON-RPC format
- Deserializing responses back from JSON-RPC
- Handling connection errors and reconnection

The client is the "translator" — it speaks the MCP protocol so your host application does not have to.

**One-to-one rule:** One client = one server. Always. The host creates as many clients as it has servers.

---

## Server — In Detail

The **Server** is the specialist. It runs as a separate process (or a remote HTTP service) and exposes its capabilities to any client that connects. It is responsible for:

- Declaring its capabilities during `initialize`
- Handling `tools/list` and returning tool schemas
- Handling `tools/call` and actually executing the tool logic
- Handling `resources/list` and `resources/read` if it has resources
- Handling `prompts/list` and `prompts/get` if it has prompts

The server does not know which AI model is on the other end. It just receives MCP requests and sends MCP responses.

**Server startup modes:**
- **stdio**: Host spawns the server as a subprocess; server reads from stdin and writes to stdout
- **SSE**: Server runs as an HTTP service; client connects to it via HTTP

---

## Tool — In Detail

A **Tool** is a function with a defined interface that the AI model can call to take an action.

**Tool definition structure:**
```json
{
  "name": "read_file",
  "description": "Read the contents of a file at the given path",
  "inputSchema": {
    "type": "object",
    "properties": {
      "path": {
        "type": "string",
        "description": "Absolute path to the file to read"
      }
    },
    "required": ["path"]
  }
}
```

**Key facts:**
- The `description` is what the AI reads to understand what the tool does — write it clearly
- The `inputSchema` is a JSON Schema that defines the arguments
- Tools can return text, images, or embedded resources
- Tools should be idempotent where possible (safe to retry)

---

## Resource — In Detail

A **Resource** is a readable data endpoint with a URI. Resources are like files — the AI can list them and read them, but not write to them through the resource interface.

**Resource structure:**
```json
{
  "uri": "file:///home/user/documents/report.pdf",
  "name": "Quarterly Report",
  "mimeType": "application/pdf",
  "description": "Q3 2024 quarterly business report"
}
```

**When to use Resources vs Tools:**
- Use a Resource when the data already exists and you just want to read it
- Use a Tool when you need to perform an action or the data requires parameters to construct

---

## Prompt — In Detail

A **Prompt** is a parameterized prompt template stored on the server. When the host requests a prompt, it fills in the arguments and returns the completed prompt messages.

**Prompt definition:**
```json
{
  "name": "code_review",
  "description": "Generate a thorough code review for a given code snippet",
  "arguments": [
    {
      "name": "code",
      "description": "The code to review",
      "required": true
    },
    {
      "name": "language",
      "description": "Programming language (python, javascript, etc.)",
      "required": false
    }
  ]
}
```

**Use case:** Standardize common AI workflows across your organization. Instead of every developer writing their own "code review" prompt, store the best one as an MCP prompt.

---

## Transport — In Detail

| | stdio | SSE |
|---|---|---|
| **How server starts** | Host spawns subprocess | Server already running |
| **Host sends requests via** | stdin pipe | HTTP POST to `/message` |
| **Server sends responses via** | stdout pipe | Server-Sent Events stream |
| **Best for** | Local tools on same machine | Remote servers, multi-user |
| **Setup complexity** | Simple | Requires HTTP server |
| **Scalability** | One process per client | Many clients per server |

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | MCP architecture deep dive |
| 📄 **Component_Breakdown.md** | ← you are here |

⬅️ **Prev:** [01 MCP Fundamentals](../01_MCP_Fundamentals/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 Hosts Clients Servers](../03_Hosts_Clients_Servers/Theory.md)