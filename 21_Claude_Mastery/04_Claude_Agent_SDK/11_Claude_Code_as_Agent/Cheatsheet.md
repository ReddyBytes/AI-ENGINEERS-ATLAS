# Claude Code as Agent — Cheatsheet

## Claude Code's Agent Architecture

| Component | Claude Code Implementation |
|---|---|
| LLM (reasoning core) | Claude Sonnet / Opus |
| Tools | Read, Write, Edit, Bash, Glob, Grep, WebFetch, Agent, etc. |
| Agent loop | Built-in — runs until task complete or user interrupts |
| System prompt | CLAUDE.md files (global + project) |
| External memory | MEMORY.md files (per project) |
| Subagents | Agent tool (spawns isolated worktree agents) |
| Context isolation | Git worktrees |
| Permission system | allowedTools, deniedTools, permission modes |
| Audit trail | Tool call display in terminal |

---

## The Edit Tool's Safety Design

```
1. Read file first (always — Claude Code enforces this)
2. Provide exact old_string (unique in the file)
3. Edit fails loudly if:
   - old_string not found
   - old_string appears multiple times
   - File doesn't exist

Why: "fail loud" prevents silent wrong edits
      Forces read-before-write discipline
```

---

## CLAUDE.md as System Prompt

```
Loading order:
~/.claude/CLAUDE.md (global rules, always loaded)
└── ~/project/CLAUDE.md (project rules, loaded in project)
    └── Combined into session system prompt

Use for:
- Agent personas ("You are a [role]")
- Constraints ("Never commit without asking")
- Context ("This is an Airflow v3 project, Python 3.11")
- Skill invocations
```

---

## MEMORY.md Pattern (External Memory)

```python
# Equivalent Python for what Claude Code does

# At session start:
memory = read_file("~/.claude/projects/.../MEMORY.md")
system_prompt += f"\n\nSession memory:\n{memory}"

# When user says "remember X":
append_to_file("MEMORY.md", f"\n- {fact_to_remember}")

# Between sessions: memory persists in the file
```

---

## Five Design Lessons from Claude Code

| Lesson | Implementation | Apply It |
|---|---|---|
| Read before write | Always Read before Edit | Give agents inspect-before-modify tools |
| Fail loud | Edit fails if string not found | Make tools raise errors, not return None |
| Minimal footprint | Tools scoped to project directory | Scope all agent tools to minimum permissions |
| Readable memory | Plain Markdown for MEMORY.md | Human-readable memory beats complex schemas |
| Transparent actions | Shows every tool call in terminal | Log all tool calls; make agent behavior visible |

---

## Claude Code Tool Map

```
File operations:     Read, Write, Edit
Search:              Glob, Grep
Execution:           Bash
Web:                 WebFetch
Agents:              Agent (spawn subagent)
Task management:     TaskCreate, TaskUpdate, TaskList, TaskGet
Scheduling:          CronCreate, CronDelete, CronList
Notebooks:           NotebookEdit
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | Full internals |

⬅️ **Prev:** [Safety in Agents](../10_Safety_in_Agents/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Track 4 README](../Readme.md)
