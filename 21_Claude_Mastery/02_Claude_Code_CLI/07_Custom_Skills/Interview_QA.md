# Custom Skills — Interview Q&A

## Beginner 🟢

**Q1: What is a custom skill in Claude Code?**

<details>
<summary>💡 Show Answer</summary>

A custom skill is a Markdown file stored in a `skills/` folder that loads rich expert context when invoked. Unlike slash commands (which execute a specific task), a skill establishes how Claude thinks and behaves within a domain — it's a playbook. After invoking a skill, Claude has all the background, approach, and decision frameworks it needs to work effectively in that area without further briefing.

</details>

---

**Q2: Where do skill files live and how do you invoke them?**

<details>
<summary>💡 Show Answer</summary>

Skill files are Markdown files (`.md`) stored in `~/.claude/skills/` for global skills or `<project>/.claude/skills/` for project-scoped skills. The filename without `.md` becomes the command name. A file at `~/.claude/skills/debugger.md` is invoked as `/debugger`. Project skills override global skills with the same name.

</details>

---

**Q3: What should a skill file contain?**

<details>
<summary>💡 Show Answer</summary>

A skill file has a YAML frontmatter block (with `description`, `usage`, `when_to_use`) and a Markdown body. The body should contain: background context about the domain, a step-by-step approach, a decision framework for common choices, anti-patterns to avoid, relevant files to read first, and related slash commands. The richer the context, the more consistently Claude will behave in that domain.

</details>

---

## Intermediate 🟡

**Q4: How is a custom skill different from a slash command?**

<details>
<summary>💡 Show Answer</summary>

Slash commands execute tasks — they contain task instructions Claude follows when invoked. Skills load mental models — they contain domain context, approaches, and frameworks that shape how Claude thinks about subsequent work in that area. A `/review` command reviews the current diff. A `/code-quality` skill loads the full context for what "quality" means in this project, how to evaluate it, common issues, and decision frameworks — after which Claude applies this consistently across multiple review sessions.

</details>

---

**Q5: How would you write a skill that adapts to different environments (dev, staging, production)?**

<details>
<summary>💡 Show Answer</summary>

Use the `$ARGUMENTS` placeholder: a user invokes `/deploy staging` and `$ARGUMENTS` = "staging". In the skill body, instruct Claude to adapt based on the environment argument:
```markdown
The target environment is $ARGUMENTS.
- If dev: use `docker compose up`; no approval needed
- If staging: use the staging Kubernetes cluster; require test verification first
- If production: require checklist completion and explicit confirmation before any action
```
This makes a single skill file handle multiple environments with appropriate risk controls.

</details>

---

**Q6: When would you use a project-scoped skill vs a global skill?**

<details>
<summary>💡 Show Answer</summary>

Global skills (`~/.claude/skills/`) are for domain expertise that applies across all your projects: debugging approaches, code review frameworks, teaching patterns, security audit processes. Project skills (`<project>/.claude/skills/`) are for knowledge tightly coupled to a specific codebase: the deployment pipeline for this project, the database debugging approach for this schema, the integration testing workflow. Project skills can reference specific file paths, commands, and patterns that only make sense in that context.

</details>

---

## Advanced 🔴

**Q7: How would you design a skill system for a team of 10 engineers working on a complex platform?**

<details>
<summary>💡 Show Answer</summary>

Create a shared skills repository checked into a shared dotfiles or tooling repo. Establish categories: `platform/` (architecture, deployment), `domain/` (per-service expertise), `process/` (review, incident response). Each skill is owned by the engineer with the most expertise in that area. New engineers are onboarded by invoking the relevant skills. Skills are versioned in Git — changes require PR review. The most complex skills link to more detailed documentation files outside the skill itself. This creates a living, reviewable knowledge base that compounds over time.

</details>

---

**Q8: What are the limitations of the skill system and how do you work around them?**

<details>
<summary>💡 Show Answer</summary>

Skills are loaded into context at invocation, so very long skills consume context window. Mitigation: keep skill files focused and concise; use file references rather than inline content ("read `docs/architecture.md` for full context"). Skills can't automatically update — if the system they describe changes, the skill becomes stale. Mitigation: date skills and review them quarterly; add a "last verified" date to frontmatter. Skills can't run code themselves — they're context, not execution. Mitigation: pair skills with slash commands for the execution layer.

</details>

---

**Q9: How do skills interact with CLAUDE.md and MEMORY.md at session start?**

<details>
<summary>💡 Show Answer</summary>

When a skill is invoked, Claude reads: (1) CLAUDE.md at all hierarchy levels (global → project → subfolder) — always loaded, (2) MEMORY.md — loaded at start, (3) the skill file — loaded on invocation. The skill has access to all prior context. A well-designed skill can explicitly reference both: "Read MEMORY.md for project-specific context before starting" and "Follow conventions defined in CLAUDE.md." This layering means skills don't need to duplicate what's already in CLAUDE.md or MEMORY.md — they can reference and build on that foundation.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Skill examples |

⬅️ **Prev:** [CLAUDE.md and Settings](../06_CLAUDE_md_and_Settings/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Hooks](../08_Hooks/Theory.md)
