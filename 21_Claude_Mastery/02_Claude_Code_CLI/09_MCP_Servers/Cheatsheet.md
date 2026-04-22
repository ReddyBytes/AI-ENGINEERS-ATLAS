# MCP Servers — Cheatsheet

## What MCP Adds to Claude Code

Standard tools: Read, Write, Edit, Bash, Grep, Glob, WebFetch — local file system and shell only.
MCP adds: databases, GitHub, web search, Confluence, Slack, cloud APIs — any external system.

---

## Adding a Server (settings.json)

```json
{
  "mcpServers": {
    "<name>": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-<name>", "<arg1>"],
      "env": {
        "API_TOKEN": "${ENV_VAR}"
      }
    }
  }
}
```

---

## Transport Options

| Transport | Config | Best for |
|-----------|--------|---------|
| stdio (default) | `command` + `args` | Local servers |
| SSE | `transport: "sse"`, `url` | Remote/hosted servers |

---

## Official Servers (npm packages)

| Tool | Package | What it does |
|------|---------|-------------|
| filesystem | `server-filesystem` | Extended file system access |
| fetch | `server-fetch` | HTTP fetch with more control |
| git | `server-git` | Git history and operations |
| github | `server-github` | Issues, PRs, repos |
| postgres | `server-postgres` | SQL queries on PostgreSQL |
| sqlite | `server-sqlite` | SQLite queries |
| brave-search | `server-brave-search` | Web search |
| google-drive | `server-gdrive` | Google Drive files |

---

## MCP Primitives

| Primitive | Description |
|-----------|-------------|
| Tools | Callable functions Claude invokes |
| Resources | Data streams Claude reads |
| Prompts | Pre-defined prompt templates |

---

## Example Configurations

### GitHub integration
```json
"github": {
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-github"],
  "env": {"GITHUB_TOKEN": "${GITHUB_TOKEN}"}
}
```

### PostgreSQL
```json
"postgres": {
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-postgres", "${DATABASE_URL}"]
}
```

### Remote SSE server
```json
"my-api": {
  "transport": "sse",
  "url": "https://api.example.com/mcp"
}
```

### Filesystem (scoped)
```json
"filesystem": {
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp", "/home/user/docs"]
}
```

---

## Security Rules

1. Never hardcode tokens — use `"${ENV_VAR}"`
2. Scope filesystem servers to specific paths
3. Audit community servers before use
4. Use SSE only for trusted remote servers
5. Remember: MCP servers inherit your machine's permissions

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept explanation |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | Deep architecture |

⬅️ **Prev:** [Hooks](../08_Hooks/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Agents and Subagents](../10_Agents_and_Subagents/Theory.md)
