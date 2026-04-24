# Hooks — Interview Q&A

## Beginner 🟢

**Q1: What are hooks in Claude Code?**

<details>
<summary>💡 Show Answer</summary>

Hooks are shell commands that fire automatically at specific points in the tool-execution loop. You configure them in `settings.json`. When Claude uses a tool (like Edit or Bash), your hook script runs — before (PreToolUse) or after (PostToolUse) the tool executes. Common uses: auto-formatting files after edits, logging tool activity, blocking dangerous commands, sending notifications.

</details>

---

<br>

**Q2: What are the four hook events and when does each fire?**

<details>
<summary>💡 Show Answer</summary>

`PreToolUse` fires before a tool executes and can block it (non-zero exit prevents the tool from running). `PostToolUse` fires after a tool executes — the result is available but you can't stop it now. `Stop` fires when Claude completes a task. `Notification` fires when Claude sends a notification to the user. Most hooks use PostToolUse for side effects and PreToolUse for enforcement.

</details>

---

<br>

**Q3: How do you configure a hook that auto-formats Python files after Claude edits them?**

<details>
<summary>💡 Show Answer</summary>

In `.claude/settings.json`:
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit",
        "hooks": [
          {
            "type": "command",
            "command": "if [[ $CLAUDE_FILE_PATH == *.py ]]; then ruff format \"$CLAUDE_FILE_PATH\"; fi"
          }
        ]
      }
    ]
  }
}
```
The hook fires after every Edit tool use, checks if the file is Python, and runs ruff format on it.

</details>

---

## Intermediate 🟡

**Q4: What is the difference between blocking and non-blocking hooks?**

<details>
<summary>💡 Show Answer</summary>

A blocking hook (`"blocking": true`) runs PreToolUse and can prevent the tool from executing by returning a non-zero exit code. Claude sees the block and adjusts its plan. A non-blocking hook runs PostToolUse and its exit code is ignored — the tool already ran. Use blocking hooks for policy enforcement (e.g., preventing dangerous bash commands). Use non-blocking hooks for side effects (logging, formatting, notifications).

</details>

---

<br>

**Q5: What environment variables are available to hook scripts?**

<details>
<summary>💡 Show Answer</summary>

Key variables: `CLAUDE_TOOL_NAME` (which tool is being used), `CLAUDE_TOOL_INPUT` (JSON-encoded input), `CLAUDE_TOOL_RESULT` (JSON result, PostToolUse only), `CLAUDE_FILE_PATH` (file path for file tools), `CLAUDE_BASH_COMMAND` (the command being run for Bash tool), `CLAUDE_SESSION_ID` (current session), `CLAUDE_PROJECT_DIR` (project root). Parse JSON values with `jq`.

</details>

---

<br>

**Q6: How would you use hooks to create a complete audit trail of Claude's actions?**

<details>
<summary>💡 Show Answer</summary>

Use a PostToolUse hook with `matcher: "*"` (all tools):
```json
{
  "matcher": "*",
  "hooks": [{
    "type": "command",
    "command": "echo \"$(date -u +%Y-%m-%dT%H:%M:%SZ) session=$CLAUDE_SESSION_ID tool=$CLAUDE_TOOL_NAME file=$CLAUDE_FILE_PATH cmd=$CLAUDE_BASH_COMMAND\" >> ~/.claude/audit.log"
  }]
}
```
This logs every tool invocation with timestamp, session ID, tool name, and relevant identifiers. Add the full `CLAUDE_TOOL_INPUT` JSON for even more detail.

</details>

---

## Advanced 🔴

**Q7: How would you use a PreToolUse blocking hook to enforce a company policy that no API keys are ever committed?**

<details>
<summary>💡 Show Answer</summary>

```bash
#!/bin/bash
# ~/.claude/hooks/check-secrets.sh
INPUT="$CLAUDE_TOOL_INPUT"

# For Edit and Write tools, check the new content for API key patterns
if [[ "$CLAUDE_TOOL_NAME" == "Edit" ]] || [[ "$CLAUDE_TOOL_NAME" == "Write" ]]; then
    NEW_CONTENT=$(echo "$INPUT" | jq -r '.new_string // .content // ""')
    if echo "$NEW_CONTENT" | grep -qE "(sk-ant-|sk-[A-Za-z0-9]{40,}|AKIA[A-Z0-9]{16}|ghp_[A-Za-z0-9]{36})"; then
        echo "BLOCKED: Potential API key detected in file edit" >&2
        exit 1
    fi
fi

# For Bash git commit/push, check staged files
if [[ "$CLAUDE_TOOL_NAME" == "Bash" ]]; then
    if echo "$CLAUDE_BASH_COMMAND" | grep -q "git commit\|git push"; then
        if git diff --cached | grep -qE "(sk-ant-|AKIA[A-Z0-9]{16})"; then
            echo "BLOCKED: API key pattern found in staged changes" >&2
            exit 1
        fi
    fi
fi

exit 0
```

</details>

---

<br>

**Q8: What are the performance implications of hooks and how do you design them responsibly?**

<details>
<summary>💡 Show Answer</summary>

Every hook adds synchronous latency to the tool loop. A hook that takes 500ms means every file edit takes 500ms longer. Best practices: keep hooks under 100ms; use async patterns for heavy operations (fire-and-forget with `&`); avoid shell commands with startup overhead (prefer simple grep/echo over Python scripts); skip hooks for cheap tools (don't run tests on every Read); use event type appropriately (Stop event for expensive operations like test runs, not PostToolUse on every Edit). Profile your hooks by timing them standalone before registering.

</details>

---

<br>

**Q9: How do hooks differ from CLAUDE.md instructions and why would you choose one over the other?**

<details>
<summary>💡 Show Answer</summary>

CLAUDE.md instructions depend on Claude's in-context reasoning — Claude might not follow them precisely if it misinterprets them, if the instruction was written ambiguously, or if context is long and the instruction is far away. Hooks are guaranteed — they fire at the system level regardless of what Claude thinks or decides. Choose CLAUDE.md for: preferences, guidelines, conventions that benefit from Claude's judgment. Choose hooks for: policies that must be enforced without exception — audit logging, dangerous command blocking, mandatory formatting, security checks. The rule: if "Claude should try to do X" is enough, use CLAUDE.md. If "X must always happen no matter what," use a hook.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Hook scripts |
| [📄 Config_Reference.md](./Config_Reference.md) | Full config reference |

⬅️ **Prev:** [Custom Skills](../07_Custom_Skills/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [MCP Servers](../09_MCP_Servers/Theory.md)
