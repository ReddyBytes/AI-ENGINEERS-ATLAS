# CLAUDE.md and Settings — Interview Q&A

## Beginner 🟢

**Q1: What is CLAUDE.md and why is it important?**

<details>
<summary>💡 Show Answer</summary>

CLAUDE.md is a Markdown file that Claude Code reads automatically at session start. It contains project instructions, conventions, tech stack information, and behavioral rules — the "briefing document" for your AI assistant. Without it, Claude has no project context and you spend time re-explaining the setup every session. With it, Claude is pre-briefed and ready to work correctly from the first command.

</details>

---

<br>

**Q2: What is the hierarchy of CLAUDE.md files and how does precedence work?**

<details>
<summary>💡 Show Answer</summary>

Three levels exist: global (`~/.claude/CLAUDE.md` — applies everywhere), project (`<project>/CLAUDE.md`), and subfolder (`<project>/subfolder/CLAUDE.md`). All levels are loaded and merged. When instructions conflict, the more specific level wins: subfolder beats project, project beats global. This allows you to have global defaults, project-specific overrides, and even folder-level exceptions for legacy code.

</details>

---

<br>

**Q3: What is settings.json and how does it differ from CLAUDE.md?**

<details>
<summary>💡 Show Answer</summary>

`settings.json` controls runtime behavior: which tools auto-execute without prompts (`permissions.allow`), which are permanently blocked (`permissions.deny`), environment variables to inject, hooks to run, and MCP servers to load. `CLAUDE.md` controls instructional content: what the project is, how to run it, conventions to follow. CLAUDE.md answers "what should Claude do and how," while settings.json answers "what is Claude allowed to do."

</details>

---

## Intermediate 🟡

**Q4: How do you allow some bash commands but not others in settings.json?**

<details>
<summary>💡 Show Answer</summary>

Use pattern matching in `permissions.allow`. You can specify exact commands (`"Bash(git status)"`) or use wildcards (`"Bash(git log *)"`, `"Bash(pytest *)"`). The `*` matches any arguments. Use `permissions.deny` with the same pattern syntax to permanently block dangerous operations like `"Bash(rm -rf *)"` or `"Bash(git push --force *)"`. Anything not in either list requires an interactive approval prompt.

</details>

---

<br>

**Q5: What is .claudeignore and when would you use it?**

<details>
<summary>💡 Show Answer</summary>

`.claudeignore` works like `.gitignore` — it lists files and directories Claude Code should skip when searching or reading the project. Use it for: build artifacts (dist/, __pycache__/), generated files (node_modules/, .venv/), secrets files (.env, *.pem, *.key), and large lock files. This prevents Claude from reading irrelevant or sensitive content and speeds up codebase searches.

</details>

---

<br>

**Q6: How do you inject environment variables through settings.json without hardcoding secrets?**

<details>
<summary>💡 Show Answer</summary>

Use the `env` section with `${VAR}` interpolation syntax:
```json
{
  "env": {
    "DATABASE_URL": "${DATABASE_URL}",
    "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}"
  }
}
```
The `${VAR}` syntax reads from your shell environment at runtime. The actual secret value is never written to settings.json — only the reference. This means settings.json is safe to commit to Git.

</details>

---

## Advanced 🔴

**Q7: How would you use subfolder CLAUDE.md to manage a monorepo where each service has different conventions?**

<details>
<summary>💡 Show Answer</summary>

Structure it like this: root `CLAUDE.md` defines shared conventions (Git workflow, commit message format, shared tools). Each service directory (`services/auth/CLAUDE.md`, `services/payments/CLAUDE.md`) defines service-specific conventions (language, test commands, API contracts). When working in `services/auth/`, Claude loads: global → root project → `services/auth/` — giving it the shared baseline plus auth-specific rules. Engineers never have to re-explain each service's conventions.

</details>

---

<br>

**Q8: A new engineer joins the team and complains Claude is giving them different suggestions than other team members. What's likely wrong and how do you fix it?**

<details>
<summary>💡 Show Answer</summary>

Likely causes: (1) the project CLAUDE.md isn't checked into Git, so new engineers don't have it; (2) the engineer has conflicting rules in their personal `~/.claude/CLAUDE.md` that override the project rules; (3) different Claude Code versions with different defaults. Fix: check the project CLAUDE.md and `.claude/settings.json` into Git, document in the project README that engineers should avoid global CLAUDE.md rules that contradict project conventions, and pin Claude Code version in a `.tool-versions` or `package.json` engines field.

</details>

---

<br>

**Q9: What's the optimal length and structure for a project CLAUDE.md?**

<details>
<summary>💡 Show Answer</summary>

Aim for 50-150 lines. Structure: brief project overview (3-5 lines), tech stack (one line each), commands to run tests/lint/start (3-5 lines), file structure map (key directories, one line each), conventions (bulleted list, 5-10 items), always/never sections (5 items each). Long CLAUDE.md files have two problems: they consume context window on every session (reducing available tokens for actual work), and important rules get buried. Prioritize actionable rules over documentation — detailed docs belong in the repo's actual README.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Config_Reference.md](./Config_Reference.md) | Full config reference |

⬅️ **Prev:** [Memory System](../05_Memory_System/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Custom Skills](../07_Custom_Skills/Theory.md)
