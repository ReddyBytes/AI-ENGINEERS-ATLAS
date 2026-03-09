# Cheatsheet — MCP Ecosystem

**The MCP Ecosystem is the growing collection of official and community MCP servers, clients, SDKs, and tools. Start with what exists before building from scratch.**

---

## Key Terms 📋

| Term | Definition |
|---|---|
| **Official servers** | MCP servers built and maintained by Anthropic |
| **Community servers** | MCP servers built by third-party developers and companies |
| **MCP Registry** | A directory of available MCP servers (GitHub, npm, PyPI) |
| **MCP Inspector** | Official dev tool for testing servers interactively |
| **Client hosts** | Applications that support MCP (Claude Desktop, VS Code, etc.) |
| **SDK** | Software Development Kit for building MCP servers/clients (Python, TypeScript, Go, Rust) |

---

## Official MCP Servers (by Anthropic)

| Server | What It Does | Install |
|---|---|---|
| `filesystem` | Read/write local files and directories | `npx @modelcontextprotocol/server-filesystem <allowed-dir>` |
| `github` | GitHub repos, PRs, issues, code | `npm install -g @modelcontextprotocol/server-github` |
| `gitlab` | GitLab repos, MRs, issues | `npm install -g @modelcontextprotocol/server-gitlab` |
| `google-drive` | Read Google Drive files | `npm install -g @modelcontextprotocol/server-gdrive` |
| `slack` | Read/post Slack messages | `npm install -g @modelcontextprotocol/server-slack` |
| `postgres` | Query PostgreSQL databases | `npm install -g @modelcontextprotocol/server-postgres` |
| `sqlite` | Query SQLite databases | `npm install -g @modelcontextprotocol/server-sqlite` |
| `brave-search` | Web search via Brave API | `npm install -g @modelcontextprotocol/server-brave-search` |
| `puppeteer` | Control a headless browser | `npm install -g @modelcontextprotocol/server-puppeteer` |
| `fetch` | Fetch and read web pages | `npm install -g @modelcontextprotocol/server-fetch` |
| `memory` | Persistent memory across sessions | `npm install -g @modelcontextprotocol/server-memory` |
| `sequential-thinking` | Structured step-by-step reasoning | `npm install -g @modelcontextprotocol/server-sequential-thinking` |

---

## MCP Client Hosts

| Host | Type | How to Configure |
|---|---|---|
| Claude Desktop | Desktop app | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| VS Code | IDE extension | `.vscode/mcp.json` or settings |
| Cursor | AI IDE | Similar to VS Code config |
| Custom Python app | Your code | Use `mcp` Python SDK with ClientSession |
| Zed editor | IDE | Built-in MCP support |

---

## SDKs Available

| Language | Package | Install |
|---|---|---|
| Python | `mcp` | `pip install mcp` |
| TypeScript/Node | `@modelcontextprotocol/sdk` | `npm install @modelcontextprotocol/sdk` |
| Go | `github.com/mark3labs/mcp-go` | `go get github.com/mark3labs/mcp-go` |
| Rust | `mcp-rs` | `cargo add mcp-rs` |

---

## Where to Find Servers

```
Official: github.com/modelcontextprotocol/servers
npm:      npmjs.com/search?q=%40modelcontextprotocol
PyPI:     pypi.org/search/?q=mcp-server
GitHub:   github.com/search?q=mcp+server+topic%3Amcp
```

---

## Evaluating a Community Server (Safety Checklist)

Before connecting a community server:
- [ ] Review the source code on GitHub
- [ ] Check: what tools does it expose? What permissions does it need?
- [ ] Check: does it require an API key? Is it safe to pass one?
- [ ] Check: last commit date — is it maintained?
- [ ] Check: does it have a clear README explaining what it does?
- [ ] Check: how many stars/forks? Is there community trust?
- [ ] Check: run it with MCP Inspector before connecting to Claude Desktop

---

## Golden Rules 🏆

- Search before building — someone may have already made what you need
- Review community server code before connecting to them (treat like installing software)
- Official Anthropic servers are the gold standard for design patterns — read their source code
- Contribute back — if you build something useful, open source it
- Keep servers updated — the MCP protocol evolves; old servers may need updates
- Star and follow the main `modelcontextprotocol/servers` repo to stay current with the ecosystem

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Integration_Guide.md](./Integration_Guide.md) | Integration guide |
| [📄 Known_Servers.md](./Known_Servers.md) | Known MCP servers directory |

⬅️ **Prev:** [07 Security and Permissions](../07_Security_and_Permissions/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [09 Connect MCP to Agents](../09_Connect_MCP_to_Agents/Theory.md)