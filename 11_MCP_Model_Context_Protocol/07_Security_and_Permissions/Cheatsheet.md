# Cheatsheet — Security and Permissions

**MCP security = least privilege + human-in-the-loop + secret management + input validation. The AI is powerful; your security design controls what it can do with that power.**

---

## Key Terms 📋

| Term | Definition |
|---|---|
| **Least privilege** | Give the server only the capabilities it absolutely needs — nothing more |
| **Human-in-the-loop** | Requiring user approval before dangerous tool calls execute |
| **Trust boundary** | The line between what the AI knows and what systems it can actually touch |
| **Capability scoping** | Designing servers to expose a minimal, focused set of capabilities |
| **Secret management** | Storing API keys/passwords in environment variables, never in code |
| **Input validation** | Checking tool arguments in the server before executing them |
| **Audit log** | A record of every tool call: who, what, when, result |
| **Sandboxing** | Running code/operations in an isolated environment with restricted access |

---

## Threat Model for MCP

| Threat | How it Happens | Defense |
|---|---|---|
| AI deletes important files | AI misunderstands a "clean up" instruction | Require confirmation for delete tools |
| API key leaked | Hardcoded in server.py committed to git | Environment variables only |
| Server does too much | One mega-server with all capabilities | Build focused, single-purpose servers |
| Prompt injection attacks an MCP tool | Malicious content in a tool argument | Validate and sanitize all inputs |
| AI makes unexpected API calls | No rate limiting on external API tools | Add rate limiting and budget controls |
| Malicious MCP server from internet | User connects to an untrusted server | Only connect to servers you trust |

---

## Security Layers

```
Layer 1: User decides which servers to connect (trust boundary)
    ↓
Layer 2: Server exposes minimal capabilities (least privilege)
    ↓
Layer 3: Host filters which tools AI sees (capability scoping)
    ↓
Layer 4: Host requires confirmation for dangerous tools (human-in-the-loop)
    ↓
Layer 5: Server validates inputs (input validation)
    ↓
Layer 6: Server runs with minimal OS permissions (sandboxing)
    ↓
Layer 7: Actions are logged (audit trail)
```

---

## Safe Credential Pattern

```python
# WRONG — never do this
api_key = "sk-abc123secretkey"

# CORRECT — always do this
import os
api_key = os.environ.get("MY_API_KEY")
if not api_key:
    return [types.TextContent(type="text", text="Error: MY_API_KEY is not configured")]
```

```json
// Claude Desktop config — pass env vars here (not in code)
{
  "mcpServers": {
    "my-server": {
      "command": "python",
      "args": ["/path/to/server.py"],
      "env": { "MY_API_KEY": "your-key-here" }
    }
  }
}
```

---

## Input Validation Pattern

```python
import os
from pathlib import Path

ALLOWED_BASE_DIR = Path("/home/user/documents")

@app.call_tool()
async def call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
    if name == "read_file":
        path_str = arguments.get("path", "")
        path = Path(path_str).resolve()

        # Validate: path must be within allowed directory
        try:
            path.relative_to(ALLOWED_BASE_DIR)
        except ValueError:
            return [types.TextContent(
                type="text",
                text=f"Error: Access denied. File must be within {ALLOWED_BASE_DIR}"
            )]

        # Validate: file must exist
        if not path.exists():
            return [types.TextContent(type="text", text=f"Error: File not found: {path}")]

        return [types.TextContent(type="text", text=path.read_text())]
```

---

## Dangerous Tool Warning Pattern

```python
# In tool description — warn the AI clearly
types.Tool(
    name="delete_files",
    description=(
        "DESTRUCTIVE: Permanently deletes files matching the given pattern. "
        "This action CANNOT be undone. Always confirm with the user before calling this tool. "
        "Use dry_run=true first to see what would be deleted."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "pattern": {"type": "string", "description": "Glob pattern of files to delete"},
            "dry_run": {
                "type": "boolean",
                "description": "If true, only list files that would be deleted without actually deleting",
                "default": True  # Default to dry_run=true for safety
            }
        },
        "required": ["pattern"]
    }
)
```

---

## When to Use / When NOT to Use Dangerous Tools

**Add confirmation requirements for tools that:**
- Delete files or database records
- Send emails or messages
- Make financial transactions
- Modify production configurations
- Execute arbitrary code

**Confirmation is less critical for tools that:**
- Read files or data (no side effects)
- Search or query (no modification)
- Generate text (no external action)
- Perform local calculations

---

## Golden Rules 🏆

- Never hardcode secrets in server files — use environment variables always
- Mark destructive tools with "DESTRUCTIVE" in the description and default to safe behavior
- Validate all tool inputs before executing — the AI can pass wrong arguments
- Use path restriction to prevent servers from accessing files outside intended directories
- Build focused servers — a smaller capability surface is harder to misuse
- Log every tool call at the server level with enough detail to reproduce and debug
- For code execution tools, always use a sandbox (container, restricted subprocess)
- The user is the last line of defense — design your host to show clear confirmations

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Best_Practices.md](./Best_Practices.md) | Security best practices |

⬅️ **Prev:** [06 Building an MCP Server](../06_Building_an_MCP_Server/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [08 MCP Ecosystem](../08_MCP_Ecosystem/Theory.md)