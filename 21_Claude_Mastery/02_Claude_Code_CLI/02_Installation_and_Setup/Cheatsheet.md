# Installation and Setup — Cheatsheet

## Install

```bash
npm install -g @anthropic-ai/claude-code
claude --version    # verify
```

**Prerequisites:** Node.js 18+

---

## Auth Methods

| Method | When to use | Command |
|--------|------------|---------|
| OAuth | Individual developer | `claude` → follow browser prompt |
| API Key | Team / CI/CD | `export ANTHROPIC_API_KEY="sk-ant-..."` |

---

## Key CLI Flags

| Flag | Effect |
|------|--------|
| `--print "task"` | Non-interactive, exits after printing |
| `--continue` | Resume last conversation |
| `--resume <id>` | Resume specific session |
| `--model <id>` | Override default model |
| `--debug` | Verbose debug output |
| `--no-auto-updates` | Disable update checks |
| `--help` | Full help text |

---

## Config File Hierarchy (lowest wins for same key)

```
~/.claude/CLAUDE.md              ← global instructions
~/.claude/settings.json          ← global permissions/hooks
<project>/CLAUDE.md              ← project instructions
<project>/.claude/settings.json  ← project permissions/hooks
<subfolder>/CLAUDE.md            ← folder-level instructions
```

---

## settings.json Structure

```json
{
  "permissions": {
    "allow": ["Read", "Write", "Bash(git *)"],
    "deny": ["Bash(rm -rf *)"]
  },
  "env": {
    "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}"
  },
  "hooks": {},
  "mcpServers": {}
}
```

---

## Key Environment Variables

| Variable | Purpose |
|----------|---------|
| `ANTHROPIC_API_KEY` | Primary credential |
| `ANTHROPIC_BASE_URL` | Custom API endpoint |
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS` | Cap output length |
| `CLAUDE_CODE_DISABLE_TELEMETRY` | Opt out of telemetry |
| `HTTP_PROXY` / `HTTPS_PROXY` | Proxy settings |
| `NO_COLOR` | Disable colored output |

---

## Project Directory Structure

```
myproject/
├── CLAUDE.md                   ← project brief
└── .claude/
    ├── settings.json           ← project permissions
    ├── commands/               ← custom slash commands
    │   └── review.md
    └── memory/
        └── MEMORY.md           ← auto-saved facts
```

---

## Common Install Fixes

| Issue | Fix |
|-------|-----|
| `command not found: claude` | Add npm global bin to PATH |
| Permission denied on install | Use nvm, not system npm |
| Auth loop not completing | Switch to API key auth |
| API key not found | Add `export` to `.zshrc`/`.bashrc` |
| Node version error | `nvm install 20 && nvm use 20` |

---

## Golden Rules

1. Always `cd` to project root before running `claude`
2. Never hardcode API keys in CLAUDE.md
3. Create CLAUDE.md before first run in any project
4. Use `allow` lists for frequently used safe tools
5. Use `deny` lists for commands you never want executed

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept explanation |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Setup walkthrough |

⬅️ **Prev:** [What is Claude Code](../01_What_is_Claude_Code/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Basic Usage and Commands](../03_Basic_Usage_and_Commands/Theory.md)
