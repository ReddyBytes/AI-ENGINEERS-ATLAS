# IDE Integration — Cheatsheet

## Available Extensions

| IDE | Extension | Install |
|-----|-----------|---------|
| VS Code | `anthropic.claude-code` | VS Code Marketplace |
| JetBrains | Claude Code Plugin | Settings → Plugins |

---

## VS Code Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+C` | Open Claude Code panel |
| `Ctrl+Shift+K` | Ask Claude about selected code |
| `Ctrl+Enter` | Send message |
| `Escape` | Cancel current action |
| `Ctrl+Z` | Undo Claude's last edit |

---

## Status Bar Indicators

| Text | Meaning |
|------|---------|
| `Claude: Ready` | Idle, waiting |
| `Claude: Thinking...` | Planning |
| `Claude: Editing` | Writing a file |
| `Claude: Running` | Executing bash |
| `$0.04 \| claude-sonnet-4-6` | Cost + model |

---

## Diff View Actions

When Claude proposes a file edit:

| Button | Action |
|--------|--------|
| Accept | Apply this single change |
| Reject | Skip this change |
| Accept All | Apply all proposed changes |
| Reject All | Discard all proposed changes |

---

## CLI vs IDE — When to Use Each

| Use case | Interface |
|----------|-----------|
| Multi-file refactors | Either (IDE for diff readability) |
| Quick single-function edits | IDE extension |
| CI/CD / automation scripts | Terminal with --print |
| Explaining selected code | IDE extension |
| Complex multi-step tasks | Terminal |

---

## Shared State (CLI ↔ IDE)

Both interfaces share:
- CLAUDE.md config files
- settings.json permissions
- Session memory (--continue works)
- The same tool set

---

## Installation Commands

```bash
# VS Code via CLI
code --install-extension anthropic.claude-code

# Verify
code --list-extensions | grep claude
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept explanation |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |

⬅️ **Prev:** [Agents and Subagents](../10_Agents_and_Subagents/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Permissions and Security](../12_Permissions_and_Security/Theory.md)
