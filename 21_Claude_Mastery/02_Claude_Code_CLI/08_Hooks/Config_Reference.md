# Hooks — Config Reference

## Full settings.json Hooks Schema

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "<tool-name | *>",
        "hooks": [
          {
            "type": "command",
            "command": "<shell command string>",
            "blocking": true
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "<tool-name | *>",
        "hooks": [
          {
            "type": "command",
            "command": "<shell command string>",
            "blocking": false
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "<shell command string>"
          }
        ]
      }
    ],
    "Notification": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "<shell command string>"
          }
        ]
      }
    ]
  }
}
```

---

## Hook Object Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `matcher` | string | Yes | — | Tool name or `"*"` for all tools |
| `hooks` | array | Yes | — | List of hook objects |
| `hooks[].type` | string | Yes | — | Currently only `"command"` |
| `hooks[].command` | string | Yes | — | Shell command to execute |
| `hooks[].blocking` | boolean | No | `false` | If true, non-zero exit blocks the tool (PreToolUse only) |

---

## Valid Matcher Values

| Matcher | Matches |
|---------|---------|
| `"Read"` | File read operations |
| `"Write"` | File create/overwrite |
| `"Edit"` | Targeted file edits |
| `"Bash"` | Shell command execution |
| `"Glob"` | File pattern searches |
| `"Grep"` | Content searches |
| `"WebFetch"` | Web page fetches |
| `"*"` | All tools |

---

## Environment Variables Available in Hooks

| Variable | Available in | Value |
|----------|-------------|-------|
| `CLAUDE_TOOL_NAME` | All events | Tool name (e.g., `Edit`) |
| `CLAUDE_TOOL_INPUT` | All events | JSON-encoded tool input |
| `CLAUDE_TOOL_RESULT` | PostToolUse | JSON-encoded tool result |
| `CLAUDE_FILE_PATH` | File tools | Absolute path to file |
| `CLAUDE_BASH_COMMAND` | Bash tool | The command being run |
| `CLAUDE_SESSION_ID` | All events | Current session UUID |
| `CLAUDE_PROJECT_DIR` | All events | Absolute path to project root |

---

## CLAUDE_TOOL_INPUT JSON Shapes

### Edit tool input
```json
{
  "file_path": "/absolute/path/to/file.py",
  "old_string": "text to replace",
  "new_string": "replacement text",
  "replace_all": false
}
```

### Write tool input
```json
{
  "file_path": "/absolute/path/to/file.py",
  "content": "full file content"
}
```

### Bash tool input
```json
{
  "command": "pytest tests/ -v",
  "description": "Run the test suite",
  "timeout": 30000
}
```

### Read tool input
```json
{
  "file_path": "/absolute/path/to/file.py",
  "offset": 0,
  "limit": 100
}
```

---

## CLAUDE_TOOL_RESULT JSON Shapes

### Edit/Write success
```json
{"success": true}
```

### Bash result
```json
{
  "stdout": "output text",
  "stderr": "",
  "exit_code": 0
}
```

### Read result
```json
{
  "content": "1\tline one\n2\tline two\n",
  "line_count": 2
}
```

---

## Hook Script Template

```bash
#!/bin/bash
# Hook script template
# Exit 0 to allow / Exit 1 to block (blocking hooks only)

TOOL="$CLAUDE_TOOL_NAME"
FILE="$CLAUDE_FILE_PATH"
CMD="$CLAUDE_BASH_COMMAND"
SESSION="$CLAUDE_SESSION_ID"
PROJECT="$CLAUDE_PROJECT_DIR"

# Log for debugging
echo "[hook] Tool=$TOOL File=$FILE" >&2

# Your logic here
case "$TOOL" in
    Edit)
        # Handle file edits
        ;;
    Bash)
        # Handle bash execution
        ;;
    *)
        # Handle all others
        ;;
esac

exit 0  # Allow
```

---

## Exit Code Semantics

| Exit code | PreToolUse (blocking=true) | PostToolUse | Stop / Notification |
|-----------|---------------------------|-------------|---------------------|
| 0 | Allow tool | Continue (ignored) | Continue |
| 1+ | BLOCK tool | Continue (ignored) | Continue |

Only PreToolUse with `"blocking": true` uses exit codes for control flow.

---

## Common Hook Patterns

### Pattern: File type guard
```bash
#!/bin/bash
if [[ "$CLAUDE_FILE_PATH" != *.py ]]; then
    exit 0  # Only process Python files
fi
# ... your logic ...
```

### Pattern: Parse JSON input with jq
```bash
#!/bin/bash
if command -v jq &>/dev/null; then
    OLD=$(echo "$CLAUDE_TOOL_INPUT" | jq -r '.old_string // ""')
    NEW=$(echo "$CLAUDE_TOOL_INPUT" | jq -r '.new_string // ""')
fi
```

### Pattern: Fire-and-forget for slow operations
```bash
#!/bin/bash
# Don't block the tool loop — run in background
(expensive-command "$CLAUDE_FILE_PATH" > /dev/null 2>&1) &
exit 0
```

### Pattern: Conditional on environment
```bash
#!/bin/bash
# Only log in CI/CD environments
if [ "$CI" = "true" ]; then
    echo "$CLAUDE_TOOL_NAME" >> /tmp/ci-claude-audit.log
fi
exit 0
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Hook scripts |
| 📄 **Config_Reference.md** | ← you are here |

⬅️ **Prev:** [Custom Skills](../07_Custom_Skills/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [MCP Servers](../09_MCP_Servers/Theory.md)
