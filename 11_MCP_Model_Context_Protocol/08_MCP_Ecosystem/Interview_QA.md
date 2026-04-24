# Interview Q&A — MCP Ecosystem

## Beginner

**Q1: What is the MCP ecosystem, and why does it matter for AI development?**

<details>
<summary>💡 Show Answer</summary>

> The MCP ecosystem is the collection of official and community-built MCP servers, client hosts, SDKs, and development tools that have grown around the Model Context Protocol. It matters because it multiplies what any individual developer can build — instead of writing custom code to connect Claude to GitHub, PostgreSQL, Slack, and a web browser, you can use existing, well-maintained MCP servers for each of these. The ecosystem creates a "build once, run anywhere" effect: a server you build can work with Claude Desktop, VS Code, and any future MCP-compatible host. As more people contribute, the ecosystem becomes more valuable for everyone.

</details>

**Q2: Where do you find official MCP servers, and how do you install them?**

<details>
<summary>💡 Show Answer</summary>

> Official MCP servers are maintained by Anthropic at `github.com/modelcontextprotocol/servers`. They are also published as npm packages under the `@modelcontextprotocol` scope on npm. Most can be installed with `npm install -g @modelcontextprotocol/server-NAME` (for Node.js-based servers) or run directly without installation using `npx`. After installing, you add the server to your Claude Desktop config file (`claude_desktop_config.json`) with the command to run it and any required environment variables like API keys.

</details>

**Q3: Name three official MCP servers and explain what each one does.**

<details>
<summary>💡 Show Answer</summary>

> Three commonly used official servers:
> - **filesystem**: Lets Claude read, write, search, and organize files on your local machine within a configured directory. The most commonly used server for personal productivity.
> - **github**: Wraps the GitHub REST API so Claude can browse repositories, view and create pull requests, manage issues, review code, and post comments.
> - **postgres**: Connects to a PostgreSQL database and lets Claude run SQL queries, explore table schemas, and answer questions about your data in natural language.

</details>

---

## Intermediate

**Q4: What criteria would you use to evaluate whether a community MCP server is safe to use?**

<details>
<summary>💡 Show Answer</summary>

> I would evaluate a community server on:
> - **Source code review**: Read the actual code. What tools does it expose? What data does it read? Does it make any outbound network calls to unexpected endpoints?
> - **Credentials handling**: How does it handle API keys and secrets? Are they read from environment variables (good) or hardcoded (bad)?
> - **Tool scope**: Does it expose the minimum capabilities needed? A server that has both read and write access to a system when only read is needed is over-privileged.
> - **Maintenance**: When was the last commit? Are issues being responded to?
> - **Community trust**: How many GitHub stars? Is it from a known developer or organization?
> - **Testing**: Does it have tests? Tests indicate care and reliability.
>
> I would always test with the MCP Inspector first before connecting to Claude Desktop.

</details>

**Q5: What does the MCP Python SDK provide, and how does it relate to the overall ecosystem?**

<details>
<summary>💡 Show Answer</summary>

> The Python SDK (`pip install mcp`) provides:
> - The `Server` class and decorators (`@app.list_tools()`, `@app.call_tool()`, etc.) for building servers
> - The `ClientSession` class for building MCP clients
> - stdio and SSE transport implementations
> - All the MCP types (`Tool`, `Resource`, `Prompt`, `TextContent`, etc.)
> - The protocol implementation so you write business logic, not protocol handling
>
> It is the standard library for Python developers building MCP servers, equivalent to what Express.js is for Node.js web servers. The TypeScript SDK serves the same role for the Node.js ecosystem. Having official SDKs in multiple languages ensures the ecosystem can grow in every programming community, not just Python.

</details>

**Q6: How does the MCP ecosystem handle updates to the protocol itself? What happens if a server was built for an older version of MCP?**

<details>
<summary>💡 Show Answer</summary>

> MCP uses protocol versioning — during the `initialize` handshake, both client and server declare their supported protocol version. If there is a version mismatch, either side can decline to proceed or they negotiate a common supported version. Official servers track the latest protocol versions and are updated when MCP evolves. Community servers may lag behind — this is a real concern when evaluating community servers. If a community server has not been updated in over a year, check the MCP changelog to see if any breaking changes were made that could affect it. In practice, MCP aims to maintain backward compatibility, but feature gaps exist for older servers.

</details>

---

## Advanced

**Q7: If you were a software company releasing an MCP server for your product, what design decisions would you make to maximize adoption in the ecosystem?**

<details>
<summary>💡 Show Answer</summary>

> For maximum adoption:
>
> 1. **Minimal dependencies**: Keep the server lightweight. The more packages required, the harder it is to install. A single file with minimal dependencies is ideal.
>
> 2. **Clear, useful tool descriptions**: Write tool descriptions that help the AI model use them correctly. This directly affects how well users' AI assistants work with your server.
>
> 3. **Both transport options**: Support stdio for local development and SSE for cloud deployment. Let users choose based on their needs.
>
> 4. **Excellent README**: Include: what the server does, what tools it provides, installation steps, required env vars, and example Claude Desktop config.
>
> 5. **Publish to npm AND PyPI**: Different developers use different ecosystems. A TypeScript server published to npm reaches more users than one only on GitHub.
>
> 6. **Semantic versioning**: Use semver so users know when updates are breaking vs additive.
>
> 7. **Test coverage**: Tests demonstrate reliability and make contributing easier.
>
> 8. **Minimal required scopes**: For API-key-based servers, document exactly what API permissions are needed and nothing more.

</details>

**Q8: Describe how the MCP ecosystem could enable a "marketplace of AI capabilities" for enterprise deployments.**

<details>
<summary>💡 Show Answer</summary>

> In an enterprise context, the ecosystem pattern looks like this:
>
> - **IT/Platform team** builds and maintains approved MCP servers for company systems: CRM, ERP, HR systems, internal knowledge bases, code repositories
> - These servers are registered in a private internal server registry (similar to a private npm registry)
> - **Employees** connect their Claude Desktop (or VS Code/custom AI apps) to the company registry and install approved servers
> - The company has a centralized approval process: server code is reviewed by security before it enters the registry
> - **New capabilities** are added by building new servers — not by modifying the AI model or the host application
> - **Access control** is managed at the server level: the HR data server only connects to the HR database with read-only credentials; the code server has access to repos but not production databases
>
> This creates a sustainable "capability marketplace" where AI capabilities are added incrementally, audited, and controlled — just like an enterprise app store for AI tools.

</details>

**Q9: How would you build a "server discovery" feature for a custom MCP host application?**

<details>
<summary>💡 Show Answer</summary>

> A discovery feature would need:
>
> 1. **A registry API**: Query `api.registry.example.com/servers?category=database&language=python` to find available servers
>
> 2. **Metadata standard**: Each server entry includes name, description, required env vars, install command, supported MCP version, category, and trust level (official/verified/community)
>
> 3. **In-app browsing**: A UI in the host app that shows available servers by category, with search and filters
>
> 4. **One-click install**: The host executes the install command, prompts for required env vars, writes the server config, and restarts the MCP connections
>
> 5. **Automatic updates**: Check the registry for server updates and notify users when newer versions are available
>
> This is exactly what package managers like npm and pip do for code libraries — the same patterns apply to MCP server distribution. Anthropic is working on an official MCP registry to enable exactly this kind of discovery.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Integration_Guide.md](./Integration_Guide.md) | Integration guide |
| [📄 Known_Servers.md](./Known_Servers.md) | Known MCP servers directory |

⬅️ **Prev:** [07 Security and Permissions](../07_Security_and_Permissions/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [09 Connect MCP to Agents](../09_Connect_MCP_to_Agents/Theory.md)