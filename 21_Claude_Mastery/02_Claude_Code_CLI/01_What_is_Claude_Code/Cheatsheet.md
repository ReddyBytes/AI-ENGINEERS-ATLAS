# Claude Code — Cheatsheet

## What is it?

**Claude Code** is Anthropic's CLI agent for autonomous coding tasks. It runs Claude in your terminal with direct file system access, shell execution, and an agentic perceive→plan→act→observe loop.

---

## The Agentic Loop (at a glance)

```
User task → Read context → Plan → Execute tool → Observe result → Repeat → Report
```

---

## Core Tools Claude Code Uses

| Tool | Action |
|------|--------|
| `Read` | Read file contents |
| `Write` | Create/overwrite file |
| `Edit` | Targeted string replacement in file |
| `Bash` | Execute shell command |
| `Glob` | Find files by pattern |
| `Grep` | Search file contents (regex) |
| `WebFetch` | Fetch URL and extract content |

---

## Claude Code vs Chat — Quick Comparison

| Dimension | Chat | Claude Code |
|-----------|------|-------------|
| Interface | Browser | Terminal |
| File access | Paste code | Direct FS |
| Task scope | Single turn | Multi-step |
| Context | Manual | Auto-reads project |
| Configuration | Prompt only | CLAUDE.md + settings.json |

---

## Key Configuration Files

| File | Purpose |
|------|---------|
| `~/.claude/CLAUDE.md` | Global rules — applies to all projects |
| `<project>/CLAUDE.md` | Project-specific instructions |
| `<project>/.claude/settings.json` | Tool permissions, hooks, MCP servers |
| `<project>/.claude/memory/MEMORY.md` | Auto-saved cross-session facts |

---

## What Claude Code CAN Do

- Read any file in your project
- Edit files with surgical precision
- Run bash commands (tests, git, package managers)
- Search codebases with glob/grep
- Fetch web pages for documentation
- Spawn background subagents
- Use MCP servers (databases, GitHub, etc.)
- Follow CLAUDE.md conventions automatically

---

## What Claude Code CANNOT Do (by default)

- Write files without permission prompt
- Run destructive commands without approval
- Access the internet without WebFetch tool
- Persist memory between sessions (without MEMORY.md)
- Modify files outside project scope (sandboxed)

---

## Common Use Patterns

```bash
# Ask a question about your codebase
claude "What does the auth module do?"

# Fix a failing test
claude "The test_login test is failing. Find and fix it."

# Refactor across files
claude "Rename UserService to AccountService everywhere"

# Write documentation
claude "Add docstrings to all public methods in src/"

# Code review
claude "Review the last git commit for bugs and style issues"
```

---

## Golden Rules

1. Write a `CLAUDE.md` for every project — it's the contractor's briefing
2. Review all diffs before accepting — the agent acts on your behalf
3. Use `--print` flag for non-interactive / CI/CD mode
4. Start tasks with clear scope — vague inputs produce vague outputs
5. Use `MEMORY.md` to persist important project-specific facts

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept explanation |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |

⬅️ **Prev:** [Track 2 Overview](../../02_Claude_Code_CLI/) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Installation and Setup](../02_Installation_and_Setup/Theory.md)
