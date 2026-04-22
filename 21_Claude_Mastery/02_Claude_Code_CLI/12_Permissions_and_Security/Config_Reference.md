# Permissions and Security — Config Reference

## Full Permission Config Schema

```json
{
  "permissions": {
    "allow": [
      "<tool-name>",
      "<tool-name>(<pattern>)"
    ],
    "deny": [
      "<tool-name>",
      "<tool-name>(<pattern>)"
    ]
  }
}
```

---

## Tool Names for Permission Rules

| Tool name | What it controls |
|-----------|-----------------|
| `Read` | All file read operations |
| `Write` | All file create/overwrite operations |
| `Edit` | All targeted file edit operations |
| `Bash` | All shell command executions |
| `Glob` | All file pattern searches |
| `Grep` | All content searches |
| `WebFetch` | All HTTP fetch operations |
| `Bash(<pattern>)` | Bash commands matching pattern |
| `Write(<path>)` | Write to specific path pattern |

---

## Pattern Matching Rules

Patterns in `Bash(<pattern>)` use prefix matching:

| Pattern | Matches |
|---------|---------|
| `Bash(git status)` | Exactly `git status` |
| `Bash(git *)` | Any git command |
| `Bash(git log *)` | Any `git log` invocation |
| `Bash(pytest *)` | Any pytest invocation |
| `Bash(pytest tests/ *)` | pytest limited to tests/ directory |
| `Bash(rm *)` | Any rm command |
| `Bash(rm -rf *)` | Only recursive force removes |

---

## Recommended Allow Lists

### Minimal (most restrictive)
```json
"allow": ["Read", "Glob", "Grep"]
```

### Developer (balanced)
```json
"allow": [
  "Read", "Glob", "Grep",
  "Bash(git status)",
  "Bash(git log *)",
  "Bash(git diff *)",
  "Bash(pytest *)",
  "Bash(ruff *)",
  "Bash(python -m mypy *)"
]
```

### Power user (permissive but bounded)
```json
"allow": [
  "Read", "Glob", "Grep",
  "Edit", "Write",
  "Bash(git *)",
  "Bash(pytest *)",
  "Bash(ruff *)",
  "Bash(mypy *)",
  "Bash(python *)",
  "Bash(node *)"
]
```

---

## Recommended Deny Lists

### Minimal deny (just the most dangerous)
```json
"deny": [
  "Bash(rm -rf *)",
  "Bash(git push --force *)",
  "Bash(sudo *)"
]
```

### Standard deny (for most teams)
```json
"deny": [
  "Bash(rm *)",
  "Bash(rm -rf *)",
  "Bash(git push *)",
  "Bash(git push --force *)",
  "Bash(sudo *)",
  "Bash(pip install *)",
  "Bash(npm install *)",
  "Bash(DROP *)",
  "Bash(DELETE *)",
  "Bash(TRUNCATE *)",
  "Bash(chmod 777 *)",
  "Bash(curl * | bash)",
  "Bash(wget * -O- | bash)"
]
```

### High-security (for sensitive environments)
```json
"deny": [
  "Bash(rm *)",
  "Bash(git *)",
  "Bash(sudo *)",
  "Bash(pip *)",
  "Bash(npm *)",
  "Bash(python *)",
  "Bash(node *)",
  "Bash(curl *)",
  "Bash(wget *)",
  "Write(/etc/*)",
  "Write(/usr/*)",
  "Write(~/.ssh/*)",
  "Write(~/.aws/*)"
]
```
(All bash and most writes require explicit approval)

---

## CI/CD Security Pattern

```dockerfile
# Dockerfile.claude-ci
FROM node:20-slim

# Install Claude Code
RUN npm install -g @anthropic-ai/claude-code

# Create non-root user
RUN useradd -m claude-user
USER claude-user

WORKDIR /workspace

# CLAUDE.md with restricted task scope
COPY .claude/ci-CLAUDE.md /workspace/CLAUDE.md

# No production secrets injected here
# ANTHROPIC_API_KEY passed via environment at runtime
```

```bash
# Run in CI:
docker run --rm \
  -v $(pwd):/workspace \
  -e ANTHROPIC_API_KEY=$SECRET \
  my-claude-image \
  claude --dangerously-skip-permissions --print "Run tests and report"
```

---

## Prompt Injection Mitigations

| Mitigation | How to configure |
|------------|-----------------|
| Deny dangerous patterns | `permissions.deny` in settings.json |
| Block based on content | PreToolUse blocking hook |
| Limit readable files | `.claudeignore` |
| Limit file system access | Scope filesystem MCP server |
| Add human checkpoint | Don't use `--dangerously-skip-permissions` |

---

## Security Audit Checklist

```markdown
## Claude Code Security Audit

### Configuration
- [ ] settings.json has deny list with at least: rm*, push --force, sudo
- [ ] No production secrets in CLAUDE.md or settings.json
- [ ] All secrets use ${ENV_VAR} interpolation syntax
- [ ] settings.json is in version control and reviewed via PR

### Usage
- [ ] --dangerously-skip-permissions never used on dev machines
- [ ] --dangerously-skip-permissions CI usage is in sandboxed containers
- [ ] Diffs are reviewed before acceptance (not bulk-approved)

### Hooks
- [ ] PreToolUse hook validates dangerous bash patterns (optional but recommended)
- [ ] Audit log hook is enabled if in a team setting

### MCP
- [ ] All MCP servers are audited (no untrusted community servers)
- [ ] Filesystem MCP server is scoped to specific paths
- [ ] MCP server tokens use ${ENV_VAR} not hardcoded values
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Config_Reference.md** | ← you are here |

⬅️ **Prev:** [IDE Integration](../11_IDE_Integration/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Track 3 — Claude API and SDK](../../03_Claude_API_and_SDK/)
