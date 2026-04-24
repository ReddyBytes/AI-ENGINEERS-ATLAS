# IDE Integration — Interview Q&A

## Beginner 🟢

**Q1: What IDEs have official Claude Code integration?**

<details>
<summary>💡 Show Answer</summary>

Anthropic provides official extensions for VS Code (available in the VS Code marketplace as `anthropic.claude-code`) and JetBrains IDEs (IntelliJ IDEA, PyCharm, WebStorm, and others — available in the JetBrains Plugin Marketplace). Both extensions bring the full Claude Code agentic experience into the editor UI.

</details>

---

**Q2: What does the VS Code Claude Code extension add that the terminal doesn't have?**

<details>
<summary>💡 Show Answer</summary>

The VS Code extension adds: a dockable side panel for the Claude conversation (no alt-tab required), inline diff view for file edits using VS Code's native diff viewer with syntax highlighting and Accept/Reject buttons, status bar indicators showing Claude's current state and session cost, keyboard shortcuts for common actions, and right-click context menu options for selected code. The underlying agent capabilities are identical to the CLI — it's the interaction layer that changes.

</details>

---

**Q3: What does the status bar indicator show during a Claude Code session in VS Code?**

<details>
<summary>💡 Show Answer</summary>

The status bar shows Claude's current state: `Claude: Ready` (idle), `Claude: Thinking...` (planning next action), `Claude: Editing` (writing a file), `Claude: Running` (executing a bash command). It also shows the session cost and active model name (e.g., `$0.04 | claude-sonnet-4-6`). This lets you monitor progress and cost without watching the output panel.

</details>

---

## Intermediate 🟡

**Q4: When would you use the terminal over the IDE extension, and vice versa?**

<details>
<summary>💡 Show Answer</summary>

Use the terminal for: CI/CD integration and automation scripts (with `--print` flag), complex multi-step tasks where you want full terminal output visibility, sessions where you're doing many rapid interactions. Use the IDE extension for: single-function edits where you want inline diff view, explaining or refactoring selected code without leaving the editor, quick questions about the currently open file. Both interfaces share the same config, permissions, and session state — the choice is about interaction ergonomics, not capability.

</details>

---

**Q5: How do the CLI and IDE extension share state?**

<details>
<summary>💡 Show Answer</summary>

They both read the same configuration files (global `~/.claude/CLAUDE.md`, project `CLAUDE.md`, `settings.json`). They both use the same session persistence — you can start a task in the terminal, close it, and resume with `--continue` in either the terminal or IDE extension. The memory system (MEMORY.md) is file-based, so it's shared. The only thing not directly shared is the in-memory conversation history of an active session — but session IDs allow resuming that in either interface.

</details>

---

**Q6: How does the inline diff view work in the IDE extension when Claude makes a file edit?**

<details>
<summary>💡 Show Answer</summary>

When Claude proposes a file change, instead of showing a terminal-formatted diff, the extension opens VS Code's built-in diff viewer with the original file on the left and the proposed change on the right — with full syntax highlighting, line numbers, and change indicators. You have Accept/Reject buttons for individual hunks (sections of the diff) or Accept All/Reject All for the whole file. Accepted changes are immediately applied to the working file. Rejected changes are discarded. This is the same diff viewer used for git diffs in VS Code.

</details>

---

## Advanced 🔴

**Q7: How would you set up Claude Code IDE integration for a team where developers use a mix of VS Code and JetBrains?**

<details>
<summary>💡 Show Answer</summary>

The config is already portable: CLAUDE.md and `.claude/settings.json` are in the project directory and read by both extensions identically. Ensure both extensions are listed in team documentation. Add `.claude/` to `.gitignore` if you don't want to version-control settings, or check it in if you want consistent behavior across the team. Custom slash commands in `.claude/commands/` work in both IDEs. The main difference is keyboard shortcuts — document both IDE's shortcuts in your onboarding guide.

</details>

---

**Q8: What are the performance implications of using the IDE extension vs the terminal?**

<details>
<summary>💡 Show Answer</summary>

Performance of the Claude agent loop is identical — both interfaces call the same underlying `claude` process. The IDE extension adds a UI rendering layer (VSCode webview or JetBrains tool window), which is negligible. For very rapid repeated interactions (running many quick commands in a row), the terminal REPL may feel slightly faster because it has less UI overhead. For file review and diff approval, the IDE extension is significantly faster because you don't need to read terminal diff formatting — the visual diff viewer is more efficient for reviewing large changes.

</details>

---

**Q9: What's the security model when using Claude Code through an IDE extension?**

<details>
<summary>💡 Show Answer</summary>

Identical to the CLI. The extension runs the same Claude Code binary with the same permissions system. All file edits require approval in the diff view (equivalent to the terminal's y/n prompt). The same `settings.json` allow/deny rules apply. The IDE extension doesn't add or remove any permissions — it's purely a UI wrapper. This means all the same security best practices apply: review diffs before accepting, use deny rules for dangerous operations, don't bypass permissions with `--dangerously-skip-permissions` in team settings.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |

⬅️ **Prev:** [Agents and Subagents](../10_Agents_and_Subagents/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Permissions and Security](../12_Permissions_and_Security/Theory.md)
