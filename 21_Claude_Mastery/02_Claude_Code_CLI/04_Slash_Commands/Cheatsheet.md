# Slash Commands — Cheatsheet

## Built-in Commands

| Command | What it does |
|---------|-------------|
| `/help` | List all commands (built-in + custom) |
| `/clear` | Clear conversation history |
| `/compact` | Compress history to save context window |
| `/cost` | Show token usage + estimated cost |
| `/status` | Show model, session ID, memory info |

---

## Custom Command Location

```
# Project-scoped (preferred)
<project>/.claude/commands/<name>.md  →  /name

# Global (all projects)
~/.claude/commands/<name>.md          →  /name
```

Project commands override global commands with the same name.

---

## Command File Template

```markdown
---
description: Short description shown in /help
allowed_tools:
  - Bash
  - Read
  - Grep
argument_hint: <optional arg description>
---

Your instruction to Claude goes here.
Use $ARGUMENTS to reference anything typed after the command name.

Examples:
> /mycommand some-file.py
$ARGUMENTS = "some-file.py"
```

---

## Frontmatter Fields

| Field | Required | Purpose |
|-------|----------|---------|
| `description` | Recommended | Shown in /help |
| `allowed_tools` | Optional | Restrict tool access |
| `argument_hint` | Optional | Hint for users |

---

## Argument Passing

```markdown
# In command file:
Read $ARGUMENTS and generate documentation.

# Invocation:
> /docgen src/utils.py

# $ARGUMENTS expands to: src/utils.py
```

---

## Example Commands

### /review (code review)
```markdown
---
description: Review current git diff for bugs and style issues
---
Run `git diff HEAD` and review for:
- Logic errors or obvious bugs
- Missing error handling
- Security issues (hardcoded secrets, injection)
Format: **Critical** / **Warning** / **Suggestion**
```

### /pr-summary (PR description)
```markdown
---
description: Generate a PR summary from current branch
---
Run `git diff main...HEAD` and `git log main...HEAD --oneline`.
Write a concise PR description: What / Why / Testing / Breaking changes.
```

### /docgen (generate docstrings)
```markdown
---
description: Add docstrings to a file
argument_hint: <filepath>
---
Read $ARGUMENTS. Add Google-style docstrings to every public function
that lacks one. Show diff before applying.
```

---

## Command Resolution Order

```
1. Project .claude/commands/<name>.md
2. Global ~/.claude/commands/<name>.md
3. Built-in commands
4. Error: command not found
```

---

## Golden Rules

1. Keep command files short — one task, not five
2. Use `$ARGUMENTS` for file-specific commands
3. Check commands into version control for team consistency
4. Use `allowed_tools` to prevent accidental destructive actions
5. Name commands as verbs: `/review`, `/docgen`, `/deploy-check`

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept explanation |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Command examples |

⬅️ **Prev:** [Basic Usage and Commands](../03_Basic_Usage_and_Commands/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Memory System](../05_Memory_System/Theory.md)
