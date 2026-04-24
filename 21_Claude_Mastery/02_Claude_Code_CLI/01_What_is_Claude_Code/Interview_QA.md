# Claude Code — Interview Q&A

## Beginner 🟢

**Q1: What is Claude Code and how does it differ from the Claude chat interface?**

<details>
<summary>💡 Show Answer</summary>

Claude Code is Anthropic's official CLI agent that runs Claude directly in your terminal with access to your file system and shell. Unlike the chat interface where you manually paste code and describe problems, Claude Code can read files autonomously, execute commands, and complete multi-step tasks without you acting as an intermediary. It runs an agentic loop (perceive → plan → act → observe) rather than responding to a single message.

</details>

---

<br>

**Q2: What does "agentic loop" mean in the context of Claude Code?**

<details>
<summary>💡 Show Answer</summary>

The agentic loop is the continuous cycle Claude Code runs: it perceives context (reads files, runs commands), plans what to do, executes a tool action, observes the result, and then loops — repeating until the task is complete or it needs human input. This is fundamentally different from a single request-response exchange. The model doesn't just output text — it acts, reads feedback, and adjusts.

</details>

---

<br>

**Q3: What tools does Claude Code have access to?**

<details>
<summary>💡 Show Answer</summary>

Core tools include: `Read` (read file contents), `Write` (create/overwrite files), `Edit` (targeted replacements), `Bash` (execute shell commands), `Glob` (find files by pattern), `Grep` (search file contents), and `WebFetch` (retrieve web pages). Additional tools can be added via MCP servers.

</details>

---

## Intermediate 🟡

**Q4: How does CLAUDE.md give Claude Code project context?**

<details>
<summary>💡 Show Answer</summary>

`CLAUDE.md` files are automatically loaded when Claude Code starts. There's a hierarchy: `~/.claude/CLAUDE.md` (global, always loaded), `<project>/CLAUDE.md` (project-level), and subfolder `CLAUDE.md` files. These files contain instructions, conventions, tech stack info, and behavioral rules. Claude reads them at session start, so you never have to re-explain your project structure.

</details>

<br>

**Q5: What is the permission system and why does it exist?**

<details>
<summary>💡 Show Answer</summary>

The permission system ensures Claude Code asks before taking potentially destructive actions. By default it prompts before writing files, running bash commands, or deleting anything. This allows you to review and approve each action. You can pre-approve specific tools via `settings.json`, or bypass all permissions (with explicit opt-in using `--dangerously-skip-permissions` — only for sandboxed environments).

</details>

<br>

**Q6: How does Claude Code handle multi-step tasks that require iterating on failures?**

<details>
<summary>💡 Show Answer</summary>

Claude Code reads the output of every tool invocation. If a bash command returns an error or a test fails, Claude reads that error output and uses it as feedback to plan the next action. This is the "observe" phase of the loop — the model doesn't just execute blindly, it reads results and adapts. This is what allows it to fix its own mistakes across multiple iterations.

</details>

---

## Advanced 🔴

**Q7: How does Claude Code compare architecturally to a traditional script or a chat-based code assistant?**

<details>
<summary>💡 Show Answer</summary>

A traditional script is deterministic — it executes a fixed sequence of operations. A chat-based assistant is reactive — it responds to each prompt independently without tool execution. Claude Code combines a reasoning model with a tool-use loop: it has the flexibility to reason about what to do next, the ability to execute actions on your machine, and the feedback loop to observe results and iterate. It's closer to an autonomous agent than either alternative.

</details>

<br>

**Q8: What are the key advantages of using CLAUDE.md versus just giving instructions at the start of each session?**

<details>
<summary>💡 Show Answer</summary>

CLAUDE.md is persistent, structured, and version-controlled. Instructions given at session start are ephemeral and require repetition every time. CLAUDE.md files are loaded automatically at the right scope (global, project, subfolder), meaning different projects can have different behaviors without any manual setup. They can also be checked into Git so the whole team benefits from the same Claude behavior.

</details>

<br>

**Q9: When would you NOT use Claude Code, and use the API or chat instead?**

<details>
<summary>💡 Show Answer</summary>

Use chat for exploration, learning, and one-off questions. Use the API when you're building a product that programmatically calls Claude. Use Claude Code when you need to: operate on actual files in a repo, run tests and build tools, execute multi-step engineering tasks autonomously, or maintain persistent project context across sessions. Claude Code is not ideal when the task is purely conversational, when you need sub-100ms latency, or when you need to embed Claude in your own application's logic.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |

⬅️ **Prev:** [Track 2 Overview](../../02_Claude_Code_CLI/) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Installation and Setup](../02_Installation_and_Setup/Theory.md)
