# CLAUDE.md and Settings — Cheatsheet

## CLAUDE.md Loading Hierarchy

```
~/.claude/CLAUDE.md              ← global (always loaded)
    ↓ stacks with
<project>/CLAUDE.md              ← project level
    ↓ stacks with
<project>/<subfolder>/CLAUDE.md  ← folder level (wins conflicts)
```

---

## CLAUDE.md Sections — What to Include

| Section | What to write |
|---------|--------------|
| Overview | 1-2 sentences: what the project is |
| Tech stack | Libraries, frameworks, versions |
| Commands | How to run tests, lint, start server |
| File structure | Where things live |
| Conventions | Patterns to follow, naming rules |
| Always | Rules to always follow |
| Never | Things to never do |

---

## Global CLAUDE.md Template

```markdown
# Global CLAUDE.md

## Languages
- Primary: Python 3.11+
- Secondary: TypeScript

## Always
- Type hints on all signatures
- Run tests before marking task complete
- Use logging, not print()

## Never
- Commit to main directly
- Delete files without confirmation
- Use sudo in scripts
```

---

## Project CLAUDE.md Template

```markdown
# [Project Name]

## Overview
[1-2 sentences]

## Tech Stack
- [Framework + version]
- [DB library]
- [Test framework]
- [Linting tool]

## Commands
- Tests: `pytest tests/ -v`
- Lint: `ruff check . && mypy src/`
- Start: `uvicorn app.main:app --reload`

## Structure
- API: `src/routers/`
- Logic: `src/services/`
- DB: `src/repositories/`

## Conventions
- [Rule 1]
- [Rule 2]

## Do Not
- [Prohibition 1]
- [Prohibition 2]
```

---

## settings.json Full Structure

```json
{
  "permissions": {
    "allow": ["Read", "Glob", "Grep", "Bash(git *)"],
    "deny": ["Bash(rm -rf *)", "Bash(sudo *)"]
  },
  "env": {
    "PYTHONPATH": "src",
    "DATABASE_URL": "${DATABASE_URL}"
  },
  "hooks": {},
  "mcpServers": {}
}
```

---

## Permission Pattern Examples

```json
"allow": [
  "Read",                         // always safe
  "Glob",                         // always safe
  "Grep",                         // always safe
  "Bash(git status)",             // exact command
  "Bash(git log *)",              // wildcard match
  "Bash(pytest tests/ *)",        // scoped to test dir
  "Bash(ruff *)"                  // lint tool
]

"deny": [
  "Bash(rm -rf *)",               // no destructive deletes
  "Bash(git push --force *)",     // no force pushes
  "Bash(sudo *)",                 // no sudo
  "Bash(pip install *)"           // require approval for installs
]
```

---

## .claudeignore Template

```
# Build artifacts
dist/
build/
*.pyc
__pycache__/

# Secrets
.env
*.pem
*.key

# Large generated dirs
node_modules/
.venv/
coverage/
*.lock
```

---

## Key Rules

1. Secrets go in `env` with `${VAR}` syntax — never hardcoded in CLAUDE.md
2. Check CLAUDE.md into Git — it's for the whole team
3. Keep CLAUDE.md under 100 lines — long files waste context window
4. Subfolder CLAUDE.md wins over project-level on conflicts
5. settings.json controls permissions; CLAUDE.md controls instructions

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept explanation |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Config_Reference.md](./Config_Reference.md) | Full config reference |

⬅️ **Prev:** [Memory System](../05_Memory_System/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Custom Skills](../07_Custom_Skills/Theory.md)
