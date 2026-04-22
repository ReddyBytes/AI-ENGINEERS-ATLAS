# Custom Skills — Cheatsheet

## What Skills Do

Load rich expert context on demand. A skill establishes how Claude thinks and behaves in a domain, rather than executing a specific task.

---

## Skill File Location

```
~/.claude/skills/<name>.md         → /name (global)
<project>/.claude/skills/<name>.md → /name (project, overrides global)
```

---

## Skill File Template

```markdown
---
description: What this skill does (shown in /help)
usage: /skill-name [optional-args]
when_to_use: When to invoke — what problem it solves
allowed_tools:
  - Read
  - Bash
---

## Background
[Context Claude needs for this domain]

## Approach
[How Claude should think through this type of work]

## Step-by-Step Playbook
1. [Step 1 with specifics]
2. [Step 2 with specifics]
3. [Step 3 with specifics]

## Decision Framework
- If [condition]: do [action]
- If [condition]: do [other action]

## Anti-Patterns
- Do not [X] because [reason]

## Files to Read First
- [path to relevant files]

## Related Commands
- /command-name — [what it does]
```

---

## Frontmatter Fields

| Field | Purpose |
|-------|---------|
| `description` | Shown in /help |
| `usage` | Invocation syntax example |
| `when_to_use` | Guidance on when to invoke |
| `allowed_tools` | Restrict tool access for this skill |
| `tags` | Optional categorization |

---

## Skills vs Commands vs CLAUDE.md

| | CLAUDE.md | Slash Command | Skill |
|--|-----------|---------------|-------|
| Loaded | Every session | On demand | On demand |
| Content | Instructions | Task steps | Domain playbook |
| Use for | Project rules | Repeatable actions | Expert context |

---

## Invocation

```
> /debugger
> /learn-topic Python generators
> /deploy staging
> /code-review
```

Everything after the skill name is available as `$ARGUMENTS`.

---

## Characteristics of a Good Skill

- Rich background context (not just a task description)
- Step-by-step approach for the domain
- Decision rules (if X then Y)
- Anti-patterns (what to avoid)
- File references (what to read first)
- Specific to one domain, not general purpose

---

## Example Skill Directory

```
~/.claude/skills/
├── debugger.md        ← system debugging approach
├── learn-topic.md     ← teaching + saving files
├── code-review.md     ← code review framework
└── security-audit.md  ← security review approach

myproject/.claude/skills/
├── deploy.md          ← project-specific deploy process
└── db-debug.md        ← database debugging for this project
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept explanation |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Skill examples |

⬅️ **Prev:** [CLAUDE.md and Settings](../06_CLAUDE_md_and_Settings/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Hooks](../08_Hooks/Theory.md)
