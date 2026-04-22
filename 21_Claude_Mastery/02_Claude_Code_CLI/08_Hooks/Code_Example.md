# Hooks — Code Examples

## Example 1: Auto-format Python after edits

```json
// .claude/settings.json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit",
        "hooks": [
          {
            "type": "command",
            "command": "if [[ \"$CLAUDE_FILE_PATH\" == *.py ]]; then ruff format \"$CLAUDE_FILE_PATH\" && ruff check --fix \"$CLAUDE_FILE_PATH\"; fi"
          }
        ]
      }
    ]
  }
}
```

---

## Example 2: Comprehensive audit log

```json
// .claude/settings.json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/audit.sh"
          }
        ]
      }
    ]
  }
}
```

```bash
#!/bin/bash
# ~/.claude/hooks/audit.sh

LOGFILE="$HOME/.claude/audit.log"
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Write structured log entry
echo "{\"ts\":\"$TIMESTAMP\",\"session\":\"$CLAUDE_SESSION_ID\",\"tool\":\"$CLAUDE_TOOL_NAME\",\"file\":\"$CLAUDE_FILE_PATH\",\"cmd\":\"$CLAUDE_BASH_COMMAND\"}" >> "$LOGFILE"
```

---

## Example 3: Blocking hook — reject dangerous commands

```json
// .claude/settings.json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/safety-check.sh",
            "blocking": true
          }
        ]
      }
    ]
  }
}
```

```bash
#!/bin/bash
# ~/.claude/hooks/safety-check.sh
# Exits 1 (blocking) if command is dangerous

CMD="$CLAUDE_BASH_COMMAND"

# Define dangerous patterns
DANGEROUS_PATTERNS=(
    "rm -rf /"
    "rm -rf \*"
    "DROP TABLE"
    "DELETE FROM .* WHERE 1=1"
    "git push --force"
    "git push -f"
    "chmod -R 777"
    "curl .* | bash"
    "wget .* -O- | bash"
    "> /dev/sda"
)

for PATTERN in "${DANGEROUS_PATTERNS[@]}"; do
    if echo "$CMD" | grep -qiE "$PATTERN"; then
        echo "HOOK BLOCKED: Dangerous pattern detected: '$PATTERN'" >&2
        echo "Command was: $CMD" >&2
        exit 1
    fi
done

exit 0
```

---

## Example 4: Run tests after editing test-related files

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit",
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/test-on-edit.sh"
          }
        ]
      }
    ]
  }
}
```

```bash
#!/bin/bash
# ~/.claude/hooks/test-on-edit.sh
# Run tests if a source or test file was edited

FILE="$CLAUDE_FILE_PATH"
PROJECT="$CLAUDE_PROJECT_DIR"

# Only run for Python files in src/ or tests/
if [[ "$FILE" == */src/*.py ]] || [[ "$FILE" == */tests/*.py ]]; then
    cd "$PROJECT"
    echo "[hook] Running tests after edit to $FILE" >&2
    pytest tests/ -q --tb=short 2>&1 | tail -5 >&2
fi
```

---

## Example 5: Slack notification on task completion

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/notify-slack.sh"
          }
        ]
      }
    ]
  }
}
```

```bash
#!/bin/bash
# ~/.claude/hooks/notify-slack.sh
# Notify Slack when Claude finishes a task

if [ -z "$SLACK_WEBHOOK_URL" ]; then
    exit 0  # Skip if not configured
fi

PROJECT=$(basename "$CLAUDE_PROJECT_DIR")
MSG="Claude Code finished a task in *$PROJECT* (session: $CLAUDE_SESSION_ID)"

curl -s -X POST "$SLACK_WEBHOOK_URL" \
    -H 'Content-type: application/json' \
    -d "{\"text\":\"$MSG\"}" > /dev/null
```

---

## Example 6: Secret detection — block API keys in edits

```bash
#!/bin/bash
# ~/.claude/hooks/check-secrets.sh

if [[ "$CLAUDE_TOOL_NAME" != "Edit" ]] && [[ "$CLAUDE_TOOL_NAME" != "Write" ]]; then
    exit 0  # Only check file edits
fi

# Extract the new content from tool input
if command -v jq &>/dev/null; then
    NEW_CONTENT=$(echo "$CLAUDE_TOOL_INPUT" | jq -r '.new_string // .content // ""' 2>/dev/null)
else
    NEW_CONTENT="$CLAUDE_TOOL_INPUT"
fi

# Check for common secret patterns
if echo "$NEW_CONTENT" | grep -qE "(sk-ant-api[0-9]+-[A-Za-z0-9\-_]{10,}|AKIA[A-Z0-9]{16}|ghp_[A-Za-z0-9]{36,}|xoxb-[0-9]+-[A-Za-z0-9]+)"; then
    echo "HOOK BLOCKED: Potential hardcoded API key or token detected" >&2
    echo "Use environment variables instead: \${MY_API_KEY}" >&2
    exit 1
fi

exit 0
```

---

## Example 7: Full settings.json with all hook types

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{
          "type": "command",
          "command": "bash ~/.claude/hooks/safety-check.sh",
          "blocking": true
        }]
      },
      {
        "matcher": "Edit",
        "hooks": [{
          "type": "command",
          "command": "bash ~/.claude/hooks/check-secrets.sh",
          "blocking": true
        }]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit",
        "hooks": [{
          "type": "command",
          "command": "if [[ \"$CLAUDE_FILE_PATH\" == *.py ]]; then ruff format \"$CLAUDE_FILE_PATH\" 2>/dev/null; fi"
        }]
      },
      {
        "matcher": "*",
        "hooks": [{
          "type": "command",
          "command": "echo \"$(date -u +%Y-%m-%dT%H:%M:%SZ) $CLAUDE_TOOL_NAME $CLAUDE_FILE_PATH\" >> ~/.claude/audit.log"
        }]
      }
    ],
    "Stop": [
      {
        "matcher": "*",
        "hooks": [{
          "type": "command",
          "command": "bash ~/.claude/hooks/notify-slack.sh"
        }]
      }
    ]
  }
}
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |
| [📄 Config_Reference.md](./Config_Reference.md) | Full config reference |

⬅️ **Prev:** [Custom Skills](../07_Custom_Skills/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [MCP Servers](../09_MCP_Servers/Theory.md)
