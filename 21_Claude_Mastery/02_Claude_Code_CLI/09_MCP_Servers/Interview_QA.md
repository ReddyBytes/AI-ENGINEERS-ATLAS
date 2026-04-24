# MCP Servers — Interview Q&A

## Beginner 🟢

**Q1: What does MCP add to Claude Code?**

<details>
<summary>💡 Show Answer</summary>

Claude Code's built-in tools are limited to the local file system and shell (Read, Write, Edit, Bash, Grep). MCP (Model Context Protocol) extends this by connecting Claude to external systems — databases, GitHub, web search, Confluence, Slack, and more. Each MCP server exposes tools that Claude can call just like its built-in tools, using natural language with no special syntax.

</details>

---

**Q2: How do you add an MCP server to Claude Code?**

<details>
<summary>💡 Show Answer</summary>

Register it in `settings.json` under the `mcpServers` key with a name, command, args, and optionally environment variables:
```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {"GITHUB_TOKEN": "${GITHUB_TOKEN}"}
    }
  }
}
```
Claude Code starts the server process at session start and makes its tools available automatically.

</details>

---

**Q3: What are the three MCP primitives and what does each do?**

<details>
<summary>💡 Show Answer</summary>

Tools are callable functions Claude invokes with arguments (like `search_github_issues`). Resources are data streams Claude can read (like the content of a database table). Prompts are pre-defined prompt templates the server exposes. In practice, most MCP servers primarily expose tools — resources and prompts are less common but supported by the protocol.

</details>

---

## Intermediate 🟡

**Q4: What is the difference between stdio and SSE transport in MCP?**

<details>
<summary>💡 Show Answer</summary>

stdio transport starts the MCP server as a local process and communicates via stdin/stdout. It's low-latency and best for servers running on your machine. SSE (Server-Sent Events) transport uses HTTP — Claude Code sends requests to a URL and receives streaming responses. Use SSE for remote or hosted MCP servers. Most official servers use stdio; configure SSE with `"transport": "sse"` and `"url"` fields instead of `command`/`args`.

</details>

---

**Q5: Name five official Anthropic MCP servers and what they provide.**

<details>
<summary>💡 Show Answer</summary>

1. `server-filesystem` — read/write files in specified paths (outside the current project)
2. `server-github` — GitHub issues, pull requests, repositories, code search
3. `server-postgres` — run SQL queries on a PostgreSQL database
4. `server-fetch` — HTTP requests with more control than the built-in WebFetch
5. `server-brave-search` — web search via the Brave Search API. Others include `server-sqlite`, `server-git`, `server-memory`, and `server-google-drive`.

</details>

---

**Q6: How would you connect Claude Code to a PostgreSQL database for a development workflow?**

<details>
<summary>💡 Show Answer</summary>

1. Install the server (handled by npx automatically): register in settings.json:
```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "${DATABASE_URL}"]
    }
  }
}
```
2. Set `DATABASE_URL` in your shell environment (pointing to dev database, not production).
3. Now ask Claude directly: "Show me the schema of the users table" or "Query for all orders placed in the last 24 hours." Claude calls the postgres MCP tools automatically.

</details>

---

## Advanced 🔴

**Q7: How does MCP's standardized protocol benefit the AI tooling ecosystem?**

<details>
<summary>💡 Show Answer</summary>

Without MCP, every AI assistant needs custom integration code for every external tool — a Google Drive plugin for Claude, a different plugin for ChatGPT, another for GitHub Copilot. Each integration is one-off, requires maintenance, and doesn't transfer. MCP standardizes the interface so any MCP server works with any MCP client. A server built for Claude Code works in any compliant host. This is analogous to how USB standardized device connections — once you have the standard, the ecosystem builds around it rather than each device needing custom ports.

</details>

---

**Q8: What are the security risks of using community MCP servers?**

<details>
<summary>💡 Show Answer</summary>

Community servers run as processes on your machine with your permissions. Risks: a malicious or compromised server could exfiltrate files, send data to external endpoints, or execute code with your credentials. Mitigations: (1) review the source code before registering any community server; (2) use official Anthropic servers where possible; (3) scope filesystem servers to specific paths; (4) use environment variables for tokens so a malicious server can only access what it's been explicitly given; (5) run unfamiliar servers in a sandboxed environment first. Apply the same caution you would for any third-party npm package.

</details>

---

**Q9: How would you build a custom MCP server that exposes an internal company API?**

<details>
<summary>💡 Show Answer</summary>

Create a Node.js or Python server that implements the MCP protocol. Using the `@modelcontextprotocol/sdk` package: define tools with JSON schemas describing their inputs, write handler functions that call your internal API, register the server with Claude Code via settings.json pointing to your server script. Example (Node.js):
```javascript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
const server = new Server({ name: "company-api", version: "1.0" });
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [{ name: "get_customer", inputSchema: { type: "object", properties: { id: { type: "string" } } } }]
}));
server.setRequestHandler(CallToolRequestSchema, async (req) => {
  const customer = await fetchCustomerFromInternalAPI(req.params.arguments.id);
  return { content: [{ type: "text", text: JSON.stringify(customer) }] };
});
```
This pattern is covered in depth in Section 11 (MCP) of this repo.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | Deep architecture |

⬅️ **Prev:** [Hooks](../08_Hooks/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Agents and Subagents](../10_Agents_and_Subagents/Theory.md)
