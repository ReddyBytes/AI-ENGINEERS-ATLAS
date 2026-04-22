# Hooks — Cheatsheet

## Hook Events

| Event | When it fires | Blocking? |
|-------|--------------|-----------|
| `PreToolUse` | Before tool executes | Yes (non-zero exit blocks tool) |
| `PostToolUse` | After tool executes | No (exit code ignored) |
| `Stop` | When Claude finishes task | No |
| `Notification` | When Claude sends a notification | No |

---

## settings.json Hook Structure

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit",
        "hooks": [
          {
            "type": "command",
            "command": "your-shell-command-here",
            "blocking": false
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/check.sh",
            "blocking": true
          }
        ]
      }
    ]
  }
}
```

---

## Hook Environment Variables

| Variable | Value |
|----------|-------|
| `CLAUDE_TOOL_NAME` | Tool name (Edit, Bash, Read, etc.) |
| `CLAUDE_TOOL_INPUT` | JSON-encoded input to the tool |
| `CLAUDE_TOOL_RESULT` | JSON-encoded result (PostToolUse only) |
| `CLAUDE_FILE_PATH` | File path for file tools |
| `CLAUDE_BASH_COMMAND` | Bash command being run |
| `CLAUDE_SESSION_ID` | Current session ID |
| `CLAUDE_PROJECT_DIR` | Project root |

---

## Blocking vs Non-Blocking

| Blocking | Exit 0 → proceed | Exit non-zero → block tool |
|----------|------------------|---------------------------|
| Non-blocking | Exit 0 → continue | Exit non-zero → also continue |

Use `"blocking": true` only for policy enforcement (PreToolUse).

---

## Common Patterns

### Auto-format Python after edit
```json
{
  "matcher": "Edit",
  "hooks": [{
    "type": "command",
    "command": "if [[ $CLAUDE_FILE_PATH == *.py ]]; then ruff format \"$CLAUDE_FILE_PATH\"; fi"
  }]
}
```

### Audit log all tools
```json
{
  "matcher": "*",
  "hooks": [{
    "type": "command",
    "command": "echo \"$(date -u +%Y-%m-%dT%H:%M:%SZ) $CLAUDE_TOOL_NAME $CLAUDE_FILE_PATH\" >> ~/.claude/audit.log"
  }]
}
```

### Block dangerous bash commands
```bash
# ~/.claude/hooks/check.sh
#!/bin/bash
if echo "$CLAUDE_BASH_COMMAND" | grep -qE "rm -rf|DROP TABLE|--force"; then
    echo "BLOCKED: $CLAUDE_BASH_COMMAND" >&2
    exit 1
fi
exit 0
```

---

## Matcher Patterns

| Matcher | Matches |
|---------|---------|
| `"Edit"` | Only Edit tool |
| `"Bash"` | Only Bash tool |
| `"Read"` | Only Read tool |
| `"Write"` | Only Write tool |
| `"*"` | All tools |

---

## Golden Rules

1. Non-blocking for logging/formatting — blocking only for policy
2. Keep hooks fast (sub-100ms) — avoid expensive operations
3. Log to stderr on failure so you can debug
4. Use `$CLAUDE_PROJECT_DIR` not hardcoded paths
5. Test hooks directly in shell before relying on them

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept explanation |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Hook scripts |
| [📄 Config_Reference.md](./Config_Reference.md) | Full config reference |

⬅️ **Prev:** [Custom Skills](../07_Custom_Skills/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [MCP Servers](../09_MCP_Servers/Theory.md)
