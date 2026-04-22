# Agents and Subagents — Cheatsheet

## Key Concepts

| Term | Meaning |
|------|---------|
| Main agent | Your primary Claude Code session |
| Subagent | A spawned child Claude instance with its own context |
| Agent tool | The tool used to create subagents |
| Background agent | Subagent that runs without blocking the main session |
| Worktree | Isolated Git working directory for safe parallel file edits |

---

## When to Use Subagents

| Condition | Use subagents? |
|-----------|---------------|
| Tasks are independent of each other | Yes |
| Task spans >10 files and >30 tool calls | Consider splitting |
| Parallel file modifications needed | Yes + worktrees |
| Tasks have sequential dependencies | No |
| Quick single-file task | No |

---

## Subagent Best Practices

1. Tasks must be independent — no data dependencies between parallel agents
2. Include full context in task description — subagents don't share parent memory
3. Use worktrees for parallel file modifications
4. Limit to 3-5 parallel agents — more hits rate limits
5. Have main agent reconcile and verify after all subagents complete

---

## Worktrees Quick Reference

```bash
# Claude Code creates worktrees automatically when using Agent tool with isolation
# Manual worktree operations:

# Create a worktree
git worktree add .claude/worktrees/feature-a feature-a-branch

# List worktrees
git worktree list

# Remove worktree
git worktree remove .claude/worktrees/feature-a

# View Claude Code worktrees
ls .claude/worktrees/
```

---

## Context Window Management

```
Rule of thumb:
- < 10 files, < 30 tool calls → main agent
- 10-50 files, complex task  → 3-5 subagents
- 50+ files                  → many subagents with worktrees
```

---

## Subagent Task Description Template

```
Task: [Specific, bounded description]

Context:
- Project: [what the project is]
- Tech stack: [relevant details]
- File to create/modify: [exact path]
- Style rules: follow [CLAUDE.md location]
- Project facts: read [MEMORY.md location]

Constraints:
- Only modify files in [scope]
- Follow [specific convention]

Output: Report [what to report back]
```

---

## Parallel vs Sequential Decision

```
Independent tasks → PARALLEL subagents
    ↓
Need file isolation? → Use WORKTREES
    ↓
Long-running tasks? → Use BACKGROUND agents

Sequential dependencies → MAIN AGENT handles directly
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept explanation |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | Architecture details |
| [📄 Code_Example.md](./Code_Example.md) | Practical examples |

⬅️ **Prev:** [MCP Servers](../09_MCP_Servers/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [IDE Integration](../11_IDE_Integration/Theory.md)
