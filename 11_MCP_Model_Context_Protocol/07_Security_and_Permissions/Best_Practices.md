# Best Practices — MCP Security

A numbered security checklist for building and deploying MCP servers safely. Use this as a review checklist before shipping any MCP server.

---

## 1. Apply the Principle of Least Privilege

- Only expose tools that your server's purpose actually requires
- Separate read operations from write operations (different tools or different servers)
- Separate safe operations from dangerous operations
- Never add a "bonus" tool "in case someone needs it later" — add it when it is actually needed

**Example:** A documentation search server should have `search_docs` and `get_document`. It should NOT have `delete_document` or `write_document` unless those are explicitly required.

---

## 2. Never Hardcode Credentials

- All API keys, passwords, and tokens must come from environment variables
- Never commit credentials to version control (add `.env` to `.gitignore`)
- Use a secrets manager (AWS Secrets Manager, HashiCorp Vault, 1Password Secrets) for production
- Validate that required env vars are present at startup — fail fast with a helpful message

```python
import os
import sys

# Check at startup — fail immediately if missing
API_KEY = os.environ.get("MY_SERVICE_API_KEY")
if not API_KEY:
    print("ERROR: MY_SERVICE_API_KEY environment variable is required", file=sys.stderr)
    sys.exit(1)
```

---

## 3. Validate All Tool Inputs

- Never execute tool logic without checking the arguments first
- Validate types, ranges, and formats beyond what JSON Schema guarantees
- For file paths: resolve to absolute path and check it is within the allowed base directory
- For SQL: use parameterized queries, never string concatenation
- For shell commands: never pass user-provided strings directly to `subprocess.run(shell=True)`

```python
# Path traversal prevention
from pathlib import Path

ALLOWED_DIR = Path("/home/user/data").resolve()

def safe_file_path(input_path: str) -> Path:
    resolved = Path(input_path).resolve()
    try:
        resolved.relative_to(ALLOWED_DIR)
    except ValueError:
        raise ValueError(f"Path must be within {ALLOWED_DIR}")
    return resolved
```

---

## 4. Mark Dangerous Tools Clearly

- Put "DESTRUCTIVE" or "WARNING" in the description of tools that have irreversible effects
- Include what the tool actually does: "Permanently deletes..." not "Removes..."
- Default to the safest option (e.g., `dry_run=True` as default)
- Consider requiring an explicit `confirm=True` argument for the most dangerous operations

```python
types.Tool(
    name="delete_database_records",
    description=(
        "DESTRUCTIVE: Permanently deletes records matching the filter. "
        "This action cannot be undone. Pass dry_run=true to preview what would be deleted."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "filter": {"type": "string"},
            "dry_run": {"type": "boolean", "default": True}  # Defaults to safe
        },
        "required": ["filter"]
    }
)
```

---

## 5. Handle Errors Without Leaking Sensitive Info

- Catch all exceptions in tool handlers and return TextContent errors
- Do not include full stack traces in error messages returned to the AI (they may contain sensitive paths, connection strings, etc.)
- Log full error details to stderr/log files (not to the AI's response)

```python
try:
    result = execute_query(sql)
    return [types.TextContent(type="text", text=result)]
except DatabaseConnectionError:
    # Don't expose connection string in the error!
    print(f"DB connection error: {e}", file=sys.stderr)
    return [types.TextContent(type="text", text="Error: Database connection failed. Please try again.")]
except Exception as e:
    print(f"Unexpected error in query tool: {e}", file=sys.stderr)
    return [types.TextContent(type="text", text=f"Error: Tool execution failed")]
```

---

## 6. Implement Rate Limiting for External API Calls

- Tools that call external APIs should have rate limiting to prevent runaway costs
- Track call counts per session or per time window
- Return a clear error when limits are exceeded

```python
import time
from collections import defaultdict

call_times = defaultdict(list)
RATE_LIMIT = 10  # calls per minute

def check_rate_limit(tool_name: str) -> bool:
    now = time.time()
    window = 60  # 1 minute
    # Keep only calls within the last window
    call_times[tool_name] = [t for t in call_times[tool_name] if now - t < window]
    if len(call_times[tool_name]) >= RATE_LIMIT:
        return False
    call_times[tool_name].append(now)
    return True
```

---

## 7. Log All Tool Calls for Auditing

- Log every tool call with: timestamp, tool name, argument summary, result status
- Sanitize logs: remove passwords, API keys, or PII from logged argument values
- Keep logs separate from the JSON-RPC channel (use stderr or a log file, never stdout)
- In production, send logs to a centralized logging system (CloudWatch, Datadog, Splunk)

```python
import logging
import json

# Use stderr for logs (stdout is reserved for JSON-RPC in stdio mode)
logging.basicConfig(
    stream=sys.stderr,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger("mcp_server")

# In your call_tool handler:
logger.info(f"Tool called: {name} | Args: {sanitize_args(arguments)}")
```

---

## 8. Scope Server Permissions at the OS Level

- Run the server process as a dedicated low-privilege OS user (not root)
- Only grant the server user access to the directories and databases it needs
- Use read-only filesystem mounts for servers that should only read
- For cloud deployments, use IAM roles with minimal permissions (not admin credentials)

---

## 9. Only Connect to Servers You Trust

This rule applies to users and organizations deploying MCP:

- Audit the source code of any MCP server before connecting to it
- Be cautious about running community-provided MCP servers without review
- For enterprise deployments, maintain an approved server registry
- Treat MCP server installation with the same care as installing software on your machine

---

## 10. Test Security Before Deploying

- Test path traversal: try `../../../etc/passwd` as a file path argument
- Test injection: try `'; DROP TABLE users; --` as a database query argument
- Test resource exhaustion: call the same tool 100 times rapidly and verify rate limiting kicks in
- Review what environment variables and files the server process can access
- Use the principle: "What is the worst thing someone could do with this tool?"

---

## Quick Security Checklist

Before shipping an MCP server, verify:

- [ ] No credentials hardcoded in the code
- [ ] All credentials loaded from environment variables
- [ ] All tool inputs validated before execution
- [ ] File path tools restrict to approved directories
- [ ] Database tools use parameterized queries
- [ ] Dangerous/destructive tools labeled clearly in descriptions
- [ ] All tool handlers wrapped in try/except
- [ ] Errors returned as TextContent, not leaking stack traces to AI
- [ ] Tool calls logged to stderr/file (not stdout)
- [ ] Rate limiting on tools that call external APIs
- [ ] Server runs with minimum necessary OS permissions

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Best_Practices.md** | ← you are here |

⬅️ **Prev:** [06 Building an MCP Server](../06_Building_an_MCP_Server/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [08 MCP Ecosystem](../08_MCP_Ecosystem/Theory.md)