# Cheatsheet — MCP Fundamentals

**MCP (Model Context Protocol)** is an open protocol by Anthropic that standardizes how AI applications connect to external tools, data sources, and services. Think: USB for AI.

---

## Key Terms 📋

| Term | Definition |
|---|---|
| **MCP** | Model Context Protocol — the open standard for AI-tool connectivity |
| **Host** | The AI application (Claude Desktop, VS Code, your app) that uses MCP |
| **Client** | A component inside the host that manages one connection to one MCP server |
| **Server** | An external process that exposes tools/resources/prompts to the AI |
| **Tool** | An action the AI can perform (create file, query DB, send email) |
| **Resource** | Read-only data the AI can access (file contents, DB records) |
| **Prompt** | A reusable, parameterized prompt template |
| **Transport** | How messages travel — stdio (local subprocess) or SSE (HTTP) |
| **JSON-RPC 2.0** | The message format used by MCP for all communication |

---

## The Three MCP Primitives 🔑

```
Tools      → AI can DO things   (write file, call API, run query)
Resources  → AI can READ things  (file contents, database rows, docs)
Prompts    → AI can USE templates (pre-built workflow instructions)
```

---

## MCP vs. The Old Way

| Old Way | MCP Way |
|---|---|
| Custom code per AI model | One MCP server, any client |
| Tool logic baked into app | Tool logic in reusable server |
| Switching AI = rewrite | Swap client, keep servers |
| N tools = N integrations | N tools = N MCP servers |

---

## Core Message Types

| Message | Direction | Purpose |
|---|---|---|
| `initialize` | Client → Server | Start session, exchange capabilities |
| `tools/list` | Client → Server | Ask what tools are available |
| `tools/call` | Client → Server | Execute a specific tool |
| `resources/list` | Client → Server | Ask what resources are available |
| `resources/read` | Client → Server | Read a specific resource |
| `prompts/list` | Client → Server | Ask what prompt templates exist |
| `prompts/get` | Client → Server | Retrieve a filled prompt template |

---

## When to Use MCP

**Use MCP when:**
- You want the same tool to work with multiple AI clients
- You are building tools others will reuse
- You want a clean separation between AI logic and tool logic
- You are building production AI systems that need maintainable integrations

**Do NOT use MCP when:**
- You need a one-off, app-specific function that will never be reused
- You are prototyping and just need something fast (use function calling directly)
- The tool is purely internal to one model interaction

---

## Golden Rules 🏆

- MCP servers expose capabilities; MCP clients consume them — never the reverse
- Tools DO things; Resources READ things — do not blur this line
- Every MCP interaction starts with an `initialize` handshake
- MCP is transport-agnostic — the same server can run over stdio or SSE
- Think of your MCP server as a published API: version it, document it, test it
- The AI model decides WHEN to call a tool; the server decides HOW to execute it
- One client manages exactly one server connection — hosts can have many clients

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 MCP_vs_REST_API.md](./MCP_vs_REST_API.md) | MCP vs REST API comparison |

⬅️ **Prev:** [09 Build an Agent](../../10_AI_Agents/09_Build_an_Agent/Project_Guide.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [02 MCP Architecture](../02_MCP_Architecture/Theory.md)