# Slash Commands — Interview Q&A

## Beginner 🟢

**Q1: What is a slash command in Claude Code?**

<details>
<summary>💡 Show Answer</summary>

A slash command is a shortcut that triggers a pre-written instruction set when typed as `/command-name` in the Claude Code REPL. Built-in commands (like `/help`, `/clear`, `/cost`) manage session state. Custom commands (stored as `.md` files in `.claude/commands/`) allow you to codify any repeatable workflow — code review, documentation, deployment checks — into a single invocation.

</details>

---

**Q2: What do the built-in slash commands do?**

<details>
<summary>💡 Show Answer</summary>

`/help` lists all available commands. `/clear` wipes the current conversation so you start fresh. `/compact` summarizes older conversation history to save context window space. `/cost` shows token usage and estimated API cost for the current session. `/status` shows the active model, session ID, and memory file locations.

</details>

---

**Q3: Where do you put custom slash command files?**

<details>
<summary>💡 Show Answer</summary>

Custom commands go in `.claude/commands/` within your project, as Markdown files. The filename (without `.md`) becomes the command name. A file at `.claude/commands/review.md` is invoked as `/review`. Global commands that apply to all projects go in `~/.claude/commands/`.

</details>

---

## Intermediate 🟡

**Q4: How do you pass arguments to a custom slash command?**

<details>
<summary>💡 Show Answer</summary>

Use the `$ARGUMENTS` placeholder in your command file body. When the command is invoked as `/docgen src/utils.py`, everything after `/docgen` (`src/utils.py`) replaces `$ARGUMENTS`. Add an `argument_hint` field in the YAML frontmatter to show users what argument format to use (it appears in `/help`).

</details>

---

**Q5: What is the YAML frontmatter in a command file and what can you configure?**

<details>
<summary>💡 Show Answer</summary>

The frontmatter is a YAML block at the top of the command file delimited by `---`. Key fields: `description` (text shown in `/help`), `allowed_tools` (list of tools this command may use — useful for security scoping), and `argument_hint` (prompt shown to users about what argument to pass). The frontmatter is optional but recommended for discoverability and security.

</details>

---

**Q6: When would you use a project command vs a global command?**

<details>
<summary>💡 Show Answer</summary>

Use project commands (`.claude/commands/`) for workflows specific to this codebase: running the project's test suite, checking against project-specific style rules, running database migrations. Use global commands (`~/.claude/commands/`) for general-purpose workflows you use in any project: code review, PR summary generation, documentation. Project commands take precedence over global commands with the same name.

</details>

---

## Advanced 🔴

**Q7: How would you design a slash command for a deployment pre-flight check?**

<details>
<summary>💡 Show Answer</summary>

```markdown

</details>

---
description: Run pre-flight checks before deploying to production
allowed_tools:
  - Bash
  - Read
  - Grep
---
Run the following checks and report PASS/FAIL for each:

1. `pytest tests/ -q` — all tests pass
2. `ruff check .` — no linting errors
3. `python -m mypy src/ --strict` — no type errors
4. Check that no `print()` debugging statements exist in src/
5. Verify .env.production exists and has all required keys from .env.example
6. Run `git status` — no uncommitted changes

If any check fails, list the failures and STOP. Do not proceed.
If all pass, output: "✅ All checks passed. Ready to deploy."
```

---

**Q8: What's the difference between a slash command and a CLAUDE.md instruction?**

<details>
<summary>💡 Show Answer</summary>

CLAUDE.md contains persistent project context and behavior rules that apply to every session — conventions, tech stack, what to avoid. These are always-on background instructions. Slash commands are on-demand workflows you explicitly invoke. Think of CLAUDE.md as "how Claude should always behave in this project" and slash commands as "specific workflows I want to trigger on demand." They complement each other: CLAUDE.md sets the context, commands define repeatable actions within that context.

</details>

---

**Q9: How do you share custom commands across a team and ensure everyone has the same version?**

<details>
<summary>💡 Show Answer</summary>

Check the `.claude/commands/` directory into the project's Git repository. Since each command is a plain Markdown file, it goes through normal code review like any other file change. Team members who clone or pull the repo automatically get the latest commands. Changes to commands can be reviewed in PRs, rolled back via git, and maintained alongside the code they operate on. This is one of the key advantages of the file-based command system over platform-specific integrations.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Command examples |

⬅️ **Prev:** [Basic Usage and Commands](../03_Basic_Usage_and_Commands/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Memory System](../05_Memory_System/Theory.md)
