# Basic Usage and Commands — Cheatsheet

## Core Interaction Model

```
Interactive REPL: claude
Non-interactive:  claude --print "task description"
```

---

## CLI Flags Reference

| Flag | Use case |
|------|----------|
| `--print "task"` | Non-interactive, exit after output |
| `--continue` | Resume last conversation |
| `--resume <id>` | Resume specific session |
| `--model <id>` | Override default model |
| `--debug` | Verbose tool logging |
| `--no-auto-updates` | Skip update checks |

---

## Permission System — Three States

| State | How set | Behavior |
|-------|---------|----------|
| Auto-approved | `permissions.allow` in settings.json | Executes silently |
| Blocked | `permissions.deny` in settings.json | Always rejected |
| Prompted | Everything else | Asks user before executing |

---

## Diff Prompt Options

When Claude wants to edit a file, you see:

```
Allow this edit? [y/n/a/d]
```

| Key | Action |
|-----|--------|
| `y` | Approve this edit |
| `n` | Reject this edit |
| `a` | Auto-approve all edits this session |
| `d` | View full diff before deciding |

---

## Tool Permission Examples (settings.json)

```json
{
  "permissions": {
    "allow": [
      "Read",
      "Glob",
      "Grep",
      "Bash(git status)",
      "Bash(git log --oneline *)",
      "Bash(pytest *)",
      "Bash(python -m mypy *)"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Bash(git push --force *)",
      "Bash(sudo *)"
    ]
  }
}
```

---

## Common Task Patterns

```bash
# Exploration (no permission needed)
> What does the database module do?
> List all API endpoints
> Explain the error handling strategy

# File edit (diff + approval)
> Add input validation to register()
> Rename user_id to account_id in models.py
> Add type hints to all functions in utils.py

# Shell execution (command + approval)
> Run the test suite
> Check git status
> Install the missing dependency

# Multi-step with verification
> Refactor the auth module, then run tests to confirm nothing broke
```

---

## --print Flag Patterns

```bash
# Query
claude --print "What is config.py used for?"

# Capture output
claude --print "List all TODO comments" > todos.txt

# In CI/CD pipeline
STATUS=$(claude --print "Run tests, return PASS or FAIL")

# Scripted review
claude --print "Review the last git commit for potential bugs"
```

---

## Interaction Tips

- Be specific: "Add error handling to `payments.charge_card()`" beats "fix the payments module"
- Scope it: tell Claude which file and which function when possible
- Verify after edits: always ask Claude to run tests after making changes
- Explore before acting: ask Claude to read first, then act — prevents scope creep

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept explanation |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Practical examples |

⬅️ **Prev:** [Installation and Setup](../02_Installation_and_Setup/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Slash Commands](../04_Slash_Commands/Theory.md)
