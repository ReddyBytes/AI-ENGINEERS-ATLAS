# Interview Q&A — Connecting MCP to Agents

## Beginner

**Q1: What is an AI agent and how does MCP help it work?**

<details>
<summary>💡 Show Answer</summary>

> An AI agent is an AI model that can take sequences of actions to complete longer-horizon goals — not just answer questions, but actually do things. Instead of just saying "you should query the database," an agent queries the database itself.
>
> MCP helps agents work by providing a standardized way to give agents access to real-world tools. Without MCP, connecting an agent to a database, a GitHub repo, and a web search tool would require three separate custom integrations. With MCP, each of those is a separate MCP server — the agent connects to all three via MCP clients and gets their tools in a unified format. MCP turns the agent from a thinker into a doer.

</details>

<br>

**Q2: What is the agent loop, and what role does MCP play in it?**

<details>
<summary>💡 Show Answer</summary>

> The agent loop is the think-act-observe cycle that agents use to accomplish goals:
> 1. The agent receives a goal
> 2. The AI model thinks about what to do next
> 3. The model calls a tool (via MCP) to take an action
> 4. The tool result is observed by the model
> 5. The model decides what to do next (another tool call, or the goal is done)
> 6. Repeat until done
>
> MCP plays the role of the "act" step — it is the mechanism by which the agent's decision to "call a tool" becomes an actual action in the real world. The agent's thoughts happen in the AI model; the actual actions happen through MCP tool calls.

</details>

<br>

**Q3: What does it mean for an agent to have "multi-server" tool access?**

<details>
<summary>💡 Show Answer</summary>

> A multi-server agent connects to multiple MCP servers simultaneously and gets access to all their tools at once. For example, an agent might connect to three servers: a filesystem server (read/write files), a GitHub server (manage repos), and a database server (run queries). The agent sees all the tools from all three servers and can use any of them in any order to accomplish its goal. This is more powerful than connecting to a single server because the agent can take actions across multiple systems in one autonomous workflow.

</details>

---

## Intermediate

**Q4: How do you convert MCP tool definitions to the format required by the Anthropic Claude API?**

<details>
<summary>💡 Show Answer</summary>

> The conversion is straightforward because both use JSON Schema for argument definitions:
>
> ```python
> mcp_tools = await session.list_tools()
>
> anthropic_tools = [
>     {
>         "name": tool.name,
>         "description": tool.description,
>         "input_schema": tool.inputSchema  # JSON Schema, directly compatible
>     }
>     for tool in mcp_tools.tools
> ]
> ```
>
> The `inputSchema` from MCP is already a JSON Schema object — the same format Claude's API expects for function calling. So you just rename the field from `inputSchema` to `input_schema` and wrap it in the right dictionary structure.

</details>

<br>

**Q5: An agent calls a tool and gets an error. How should the agent loop handle this?**

<details>
<summary>💡 Show Answer</summary>

> The error should be returned as a tool result (not as an exception that crashes the loop). In the Anthropic API format:
>
> ```python
> tool_results.append({
>     "type": "tool_result",
>     "tool_use_id": block.id,
>     "content": f"Error: {str(e)}",
>     "is_error": True
> })
> ```
>
> When the model receives this error result, it can reason about it — it might retry with different arguments, try a different tool to accomplish the same goal, or tell the user that the operation failed and explain why. Returning the error as a readable result is always better than crashing the loop, because the AI can respond to error information intelligently.

</details>

<br>

**Q6: What is the purpose of a maximum step limit in an agent loop, and what is a reasonable default?**

<details>
<summary>💡 Show Answer</summary>

> A maximum step limit prevents the agent from getting stuck in an infinite loop — for example, repeatedly trying to fix a bug by calling the same tool with slightly different arguments without making progress. Without a limit, the agent could run indefinitely, consuming API tokens and potentially taking many unintended actions.
>
> A reasonable default is 10-20 tool calls for focused tasks. For complex multi-step workflows (like "refactor this entire codebase"), you might go up to 50. For very simple tasks (like "fetch this webpage and summarize it"), 5 is often enough. The limit should be tuned to the complexity of your specific task — start conservative and increase if legitimate tasks are being cut off.

</details>

---

## Advanced

**Q7: Design an agent architecture for an automated code review pipeline that connects to multiple MCP servers.**

<details>
<summary>💡 Show Answer</summary>

> Architecture:
>
> **MCP Servers:**
> - **GitHub server** — `list_pull_request_files`, `get_file_content`, `post_pr_comment`, `request_changes`, `approve_pr`
> - **Code analysis server** (custom) — `lint_code(code, language)`, `check_security(code)`, `analyze_complexity(code)`
> - **Filesystem server** — `read_file` for accessing local test files and configs
>
> **Agent workflow:**
> 1. Trigger: A new PR is opened (webhook or polling)
> 2. Agent calls `list_pull_request_files` to get the changed files
> 3. For each changed file, agent calls `get_file_content` to read the diff
> 4. Agent calls `lint_code` and `check_security` on each file
> 5. Agent aggregates findings across all files
> 6. If critical issues: agent calls `request_changes` with a detailed comment listing all issues
> 7. If only minor issues: agent calls `post_pr_comment` with suggestions
> 8. If no issues: agent calls `approve_pr`
>
> **Safety considerations:**
> - The `approve_pr` and `request_changes` tools should require a human review flag for PRs above a size threshold
> - Log all tool calls and their outcomes
> - The agent should not have merge permissions — only review/comment/approve

</details>

<br>

**Q8: How do you handle tool call routing when an agent is connected to multiple MCP servers that might have tools with the same name?**

<details>
<summary>💡 Show Answer</summary>

> Tool name conflicts are a real concern in multi-server setups. Best practices:
>
> 1. **Namespace tools by server**: When aggregating tools, prefix the tool name with the server name: `filesystem__read_file`, `s3__read_file`. This eliminates conflicts and makes it clear which server each tool belongs to.
>
> 2. **Build a routing table**: Keep a dictionary that maps tool name → session object. During discovery, populate this table: `tool_registry[tool.name] = session`. When the model calls a tool, look up the session from the registry.
>
> 3. **Design servers to avoid conflicts**: Single-purpose servers naturally avoid conflicts since each server covers a distinct domain. A filesystem server and a GitHub server will not have tools with the same name.
>
> 4. **Explicit selection in tool descriptions**: If two servers genuinely provide similar capabilities, make their descriptions clearly distinguish them: "Read a LOCAL file from the filesystem" vs "Read a file from GITHUB repository."

</details>

<br>

**Q9: How does connecting agents to MCP differ from using function calling directly in the Claude API? When would you choose one over the other?**

<details>
<summary>💡 Show Answer</summary>

> **Function calling directly:**
> - Tools are defined in your application code
> - Tools only work with this specific application
> - No session state or lifecycle management
> - Lower setup overhead for simple, app-specific tools
> - Works for one-off integrations that will never be reused
>
> **MCP-connected agents:**
> - Tools are defined in separate MCP server processes
> - Same tools work with any MCP-compatible host (Claude Desktop, VS Code, your app)
> - Stateful sessions with proper lifecycle management
> - Higher initial setup; much lower maintenance for shared or reused tools
> - Works for production systems where tools need to be maintained long-term
>
> **Choose direct function calling when:**
> - You are prototyping or building a quick demo
> - The tools are highly app-specific and will never be reused elsewhere
> - You want to minimize infrastructure
>
> **Choose MCP when:**
> - You want tools to be reusable across different AI applications
> - You are building tools that will be maintained and evolved over time
> - Multiple teams or applications need the same tools
> - You want portability — ability to switch AI models without rewriting tool code

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [08 MCP Ecosystem](../08_MCP_Ecosystem/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [01 Model Serving](../../12_Production_AI/01_Model_Serving/Theory.md)