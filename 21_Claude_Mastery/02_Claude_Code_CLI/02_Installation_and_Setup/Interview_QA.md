# Installation and Setup — Interview Q&A

## Beginner 🟢

**Q1: How do you install Claude Code?**

Claude Code is installed via npm as a global package:
```bash
npm install -g @anthropic-ai/claude-code
```
This requires Node.js 18 or higher. After installation, the `claude` binary is available from any directory in your terminal.

---

**Q2: What are the two ways to authenticate Claude Code?**

OAuth (recommended for individuals): run `claude` on first launch, which opens a browser to `console.anthropic.com` for account-based authentication. API Key (for teams/CI/CD): set the `ANTHROPIC_API_KEY` environment variable before running `claude`. The OAuth method auto-refreshes; the API key method requires manual rotation.

---

**Q3: What is CLAUDE.md and why should you create one before first use?**

`CLAUDE.md` is a Markdown file Claude Code reads automatically when it starts in a directory. It contains project instructions, coding conventions, and context that Claude uses throughout the session. Without it, Claude has no project-specific knowledge and you'll spend time re-explaining context every session. Creating even a brief CLAUDE.md before first run gives Claude a foundation to work from.

---

## Intermediate 🟡

**Q4: What is the configuration hierarchy in Claude Code and how does precedence work?**

Claude Code loads config from four levels: global `~/.claude/CLAUDE.md`, global `~/.claude/settings.json`, project `<project>/CLAUDE.md`, and project `<project>/.claude/settings.json`. If the same setting exists at multiple levels, the more specific (lower) level wins. This means project settings override global settings, and subfolder `CLAUDE.md` files override project-level ones. This allows you to have sensible defaults globally and project-specific overrides where needed.

---

**Q5: What is `settings.json` used for and what are its key fields?**

`settings.json` controls runtime behavior for Claude Code. Key sections: `permissions.allow` lists tools that auto-execute without a confirmation prompt; `permissions.deny` lists tools that are always blocked; `env` passes environment variables to Claude; `hooks` registers shell script hooks for tool events; `mcpServers` registers MCP tool extensions. It can exist at both global (`~/.claude/settings.json`) and project (`.claude/settings.json`) levels.

---

**Q6: How would you set up Claude Code for a CI/CD pipeline where there's no interactive browser?**

For CI/CD, use API key authentication instead of OAuth: set `ANTHROPIC_API_KEY` as an environment variable or secret in your pipeline. Run Claude Code with the `--print` flag for non-interactive mode (outputs result and exits with a status code). Pre-approve all needed tools in `settings.json` so there are no interactive permission prompts. Example:
```bash
ANTHROPIC_API_KEY=$SECRET claude --print "Run tests and report failures"
```

---

## Advanced 🔴

**Q7: How would you configure Claude Code for a multi-developer team so every developer gets consistent behavior?**

Check `CLAUDE.md` and `.claude/settings.json` into the project's Git repository. This gives every developer the same project instructions and permission rules automatically. Keep sensitive values (API keys) out of these files — use environment variables. Use a global `~/.claude/CLAUDE.md` for individual preferences (editor style, personal conventions) and the project's `CLAUDE.md` for shared conventions. The merge happens automatically at runtime.

---

**Q8: What security considerations apply when configuring `settings.json`?**

Never store API keys directly in `settings.json` — use `"${ANTHROPIC_API_KEY}"` interpolation syntax instead. Be conservative with `permissions.allow` — only pre-approve tools that are safe and routine (e.g., `Read`, `Bash(git status)`). Use `permissions.deny` to block dangerous patterns (e.g., `Bash(rm -rf *)`). Check `settings.json` into version control so the team can review permission changes via PR. Avoid using `--dangerously-skip-permissions` outside of sandboxed dev environments.

---

**Q9: What happens during `npm install -g @anthropic-ai/claude-code` behind the scenes?**

npm downloads the package from the registry, installs its Node.js dependencies, and creates a `claude` binary symlink in the global npm bin directory (e.g., `/usr/local/bin/claude` or `~/.nvm/versions/node/vX/bin/claude`). The first run triggers an auth check — if no credentials are found, it starts the OAuth or API key flow. Claude Code also checks for updates on startup and can self-update via npm. The binary communicates with the Anthropic API over HTTPS using the stored credentials.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Setup walkthrough |

⬅️ **Prev:** [What is Claude Code](../01_What_is_Claude_Code/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Basic Usage and Commands](../03_Basic_Usage_and_Commands/Theory.md)
