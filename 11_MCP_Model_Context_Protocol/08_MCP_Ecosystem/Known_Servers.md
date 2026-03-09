# Known MCP Servers Directory

A curated directory of well-known MCP servers — both official (maintained by Anthropic) and community-built. Use this as a starting point when looking for a server that fits your needs.

---

## Official Servers (by Anthropic)

These servers are maintained in the `modelcontextprotocol/servers` GitHub repository and are the most reliable, up-to-date implementations.

| Server Name | Category | What It Does | Install Command | Required Config |
|---|---|---|---|---|
| **filesystem** | Files | Read, write, search, and manage local files in configured directories | `npx @modelcontextprotocol/server-filesystem /path/to/dir` | Allowed directory as arg |
| **github** | Dev Tools | Manage GitHub repos, PRs, issues, branches, code | `npm install -g @modelcontextprotocol/server-github` | `GITHUB_PERSONAL_ACCESS_TOKEN` |
| **gitlab** | Dev Tools | Manage GitLab projects, merge requests, issues | `npm install -g @modelcontextprotocol/server-gitlab` | `GITLAB_PERSONAL_ACCESS_TOKEN`, `GITLAB_API_URL` |
| **google-drive** | Files | Read and search Google Drive files and documents | `npm install -g @modelcontextprotocol/server-gdrive` | OAuth2 credentials file |
| **google-maps** | Location | Geocoding, directions, place search | `npm install -g @modelcontextprotocol/server-google-maps` | `GOOGLE_MAPS_API_KEY` |
| **slack** | Messaging | Read channels, post messages, manage Slack workspace | `npm install -g @modelcontextprotocol/server-slack` | `SLACK_BOT_TOKEN`, `SLACK_TEAM_ID` |
| **postgres** | Database | Query and explore PostgreSQL databases | `npm install -g @modelcontextprotocol/server-postgres` | `POSTGRES_CONNECTION_STRING` |
| **sqlite** | Database | Query and explore SQLite database files | `npm install -g @modelcontextprotocol/server-sqlite` | `DB_PATH` |
| **brave-search** | Search | Web and local search via Brave Search API | `npm install -g @modelcontextprotocol/server-brave-search` | `BRAVE_API_KEY` |
| **puppeteer** | Browser | Control a headless Chrome browser — screenshot, navigate, fill forms | `npm install -g @modelcontextprotocol/server-puppeteer` | None |
| **fetch** | Web | Fetch and convert web pages to Markdown | `npm install -g @modelcontextprotocol/server-fetch` | None |
| **memory** | State | Persistent key-value memory that survives across Claude sessions | `npm install -g @modelcontextprotocol/server-memory` | None |
| **sequential-thinking** | Reasoning | Structured multi-step problem-solving framework | `npm install -g @modelcontextprotocol/server-sequential-thinking` | None |
| **aws-kb-retrieval** | Cloud | Retrieve documents from AWS Knowledge Bases (Bedrock) | `npm install -g @modelcontextprotocol/server-aws-kb-retrieval` | AWS credentials |
| **everart** | Media | AI image generation | `npm install -g @modelcontextprotocol/server-everart` | `EVERART_API_KEY` |

---

## Claude Desktop Config Examples

### Filesystem Server

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/yourname/Documents",
        "/Users/yourname/Desktop"
      ]
    }
  }
}
```

### GitHub Server

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_your_token_here"
      }
    }
  }
}
```

### PostgreSQL Server

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-postgres",
        "postgresql://username:password@localhost/dbname"
      ]
    }
  }
}
```

### Multiple Servers Together

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/me/projects"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_..." }
    },
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": { "BRAVE_API_KEY": "BSA..." }
    }
  }
}
```

---

## Notable Community Servers

Community servers are built by third-party developers. Always review the source code before using.

| Server | Category | What It Does | Source |
|---|---|---|---|
| **mcp-server-kubernetes** | DevOps | Manage Kubernetes clusters | GitHub: `Flux159/mcp-server-kubernetes` |
| **mcp-server-docker** | DevOps | Manage Docker containers and images | GitHub: various |
| **mcp-obsidian** | Notes | Read and write Obsidian vault notes | GitHub: `MarkusPfundstein/mcp-obsidian` |
| **mcp-notion** | Productivity | Read and write Notion pages/databases | GitHub: various |
| **mcp-jira** | Project Mgmt | Manage Jira tickets and boards | GitHub: various |
| **mcp-linear** | Project Mgmt | Manage Linear issues and projects | GitHub: various |
| **mcp-qdrant** | Vector DB | Query Qdrant vector database | GitHub: `qdrant/mcp-server-qdrant` |
| **mcp-redis** | Cache/DB | Read and write Redis data | GitHub: various |
| **mcp-mongodb** | Database | Query MongoDB collections | GitHub: various |
| **mcp-openapi** | API | Automatically generate MCP tools from an OpenAPI spec | GitHub: various |

---

## Tools for Working with MCP Servers

| Tool | Purpose | Install |
|---|---|---|
| **MCP Inspector** | Interactive testing tool for any MCP server | `npx @modelcontextprotocol/inspector` |
| **mcp-cli** | Command-line client to interact with MCP servers | `pip install mcp-cli` |
| **MCP Proxy** | Run multiple MCP servers behind a single SSE endpoint | GitHub: `sparfenyuk/mcp-proxy` |

---

## Where to Find More Servers

- **Official GitHub repo**: `github.com/modelcontextprotocol/servers` — the canonical list
- **npm search**: `npmjs.com/search?q=%40modelcontextprotocol`
- **GitHub topic**: `github.com/topics/mcp-server`
- **Awesome MCP**: `github.com/punkpeye/awesome-mcp-servers` — community-curated list

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Integration_Guide.md](./Integration_Guide.md) | Integration guide |
| 📄 **Known_Servers.md** | ← you are here |

⬅️ **Prev:** [07 Security and Permissions](../07_Security_and_Permissions/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [09 Connect MCP to Agents](../09_Connect_MCP_to_Agents/Theory.md)