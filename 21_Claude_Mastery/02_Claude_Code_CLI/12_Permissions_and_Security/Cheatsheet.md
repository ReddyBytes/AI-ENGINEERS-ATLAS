# Permissions and Security — Cheatsheet

## Permission Modes

| Mode | How to set | Effect |
|------|-----------|--------|
| Default | (nothing) | Prompts before writes + bash |
| acceptEdits | `"allow": ["Write", "Edit"]` | Writes auto-approved |
| Custom | `allow` + `deny` lists | Fine-grained control |
| Bypass | `--dangerously-skip-permissions` | No prompts (CI/CD only) |

---

## Permission Decision Flow

```
Claude wants to run tool X
    ↓
Is X in allow list?  → Yes → Execute silently
    ↓ No
Is X in deny list?   → Yes → Block, tell Claude
    ↓ No
Prompt user → Approve → Execute
              Reject  → Skip
```

---

## settings.json Permission Config

```json
{
  "permissions": {
    "allow": [
      "Read",
      "Glob",
      "Grep",
      "Bash(git status)",
      "Bash(git log *)",
      "Bash(git diff *)",
      "Bash(pytest *)",
      "Bash(ruff *)",
      "Bash(python -m mypy *)"
    ],
    "deny": [
      "Bash(rm *)",
      "Bash(rm -rf *)",
      "Bash(git push *)",
      "Bash(git push --force *)",
      "Bash(sudo *)",
      "Bash(pip install *)",
      "Bash(DROP *)",
      "Bash(DELETE FROM *)"
    ]
  }
}
```

---

## Risky Patterns to Always Deny

| Pattern | Risk |
|---------|------|
| `rm -rf *` | Mass deletion |
| `git push --force *` | Overwrites remote history |
| `DROP TABLE *` | Irreversible data loss |
| `sudo *` | Privilege escalation |
| `curl * \| bash` | Arbitrary code execution |
| Write to `/etc/*` | System file modification |

---

## --dangerously-skip-permissions

```bash
# Only in sandboxed environments:
claude --dangerously-skip-permissions --print "task"
```

Use only when:
- Inside Docker / VM / restricted container
- No production credentials present
- In CI/CD automation

Never use on:
- Your development machine
- With production credentials
- On shared systems

---

## Defense in Depth

```
Layer 1: Anthropic safety training
Layer 2: Claude Code permission prompts
Layer 3: settings.json allow/deny lists
Layer 4: PreToolUse blocking hooks
Layer 5: OS-level sandboxing
```

---

## Prompt Injection Defense

| Defense | How it helps |
|---------|-------------|
| Permission prompts | Bash still requires approval |
| Deny lists | Block dangerous patterns regardless |
| .claudeignore | Prevent reading untrusted files |
| Hooks | Additional blocking layer |
| Context awareness | Claude distinguishes content vs instructions |

---

## Security Checklist

- [ ] Deny list has `rm -rf *`, `git push --force *`, `sudo *`
- [ ] No production secrets in Claude Code environment
- [ ] `settings.json` is reviewed and in version control
- [ ] `--dangerously-skip-permissions` is not used on dev machines
- [ ] Diffs are read before approval, not auto-approved

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept explanation |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Config_Reference.md](./Config_Reference.md) | Full config reference |

⬅️ **Prev:** [IDE Integration](../11_IDE_Integration/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Track 3 — Claude API and SDK](../../03_Claude_API_and_SDK/)
