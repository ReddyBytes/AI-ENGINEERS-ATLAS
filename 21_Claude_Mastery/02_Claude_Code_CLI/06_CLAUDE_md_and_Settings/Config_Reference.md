# CLAUDE.md and Settings — Config Reference

## CLAUDE.md Quick Reference

### Global CLAUDE.md (`~/.claude/CLAUDE.md`)

Applies to all projects. Use for personal preferences and universal rules.

```markdown
# Global CLAUDE.md

## About
- Primary language: Python 3.11
- Secondary: TypeScript/Node.js

## Code Style
- Type hints on all function signatures
- Google-style docstrings for public APIs
- No `Any` types without justification

## Workflow
- Run tests before marking any task complete
- Show diffs before applying file changes
- Ask before deleting any file
- Never commit directly to main

## Logging
- Use `logging` module, never `print()` for debugging
- Log at DEBUG level inside functions, INFO at service boundaries

## Never
- Use `sudo` in scripts
- Hardcode API keys, passwords, or secrets
- Use `exec()` or `eval()` on user input
```

---

### Project CLAUDE.md (`<project>/CLAUDE.md`)

Applies to this project. Overrides global on conflicts.

```markdown
# Project Name

## Overview
[What this service does — 1-2 sentences]
[Primary audience / users]

## Tech Stack
- Language: Python 3.11
- Web framework: FastAPI 0.115
- Database: PostgreSQL via asyncpg (NOT SQLAlchemy)
- Cache: Redis via aioredis
- Testing: pytest + httpx (async test client)
- Linting: ruff
- Types: mypy strict mode

## Commands
- Run all tests: `pytest tests/ -v --tb=short`
- Run single test: `pytest tests/path/test_file.py::test_name -v`
- Lint: `ruff check . && python -m mypy src/ --strict`
- Format: `ruff format .`
- Start dev server: `uvicorn app.main:app --reload --port 8000`
- Start with Docker: `docker compose up app`

## File Structure
```
src/
├── main.py          ← FastAPI app factory
├── routers/         ← HTTP endpoint definitions
├── services/        ← Business logic
├── repositories/    ← Database queries (asyncpg)
├── models/          ← Pydantic request/response models
├── schemas/         ← Shared schemas (APIResponse, etc.)
└── exceptions.py    ← AppError base class
```

## Conventions
- All endpoints return `APIResponse` wrapper — see `src/schemas/base.py`
- All exceptions inherit from `AppError` — see `src/exceptions.py`
- DB queries only in `repositories/` — never inline in routers
- Route handlers call service layer only — no direct DB access in routers
- New public endpoints require an integration test in `tests/integration/`

## Always
- Validate request body with Pydantic models
- Use `async def` for all route handlers and DB functions
- Add `created_at` / `updated_at` to all new DB models

## Do Not
- Import from `repositories/` directly in routers
- Use `SELECT *` in SQL queries
- Commit migration files manually — use alembic
```

---

### Subfolder CLAUDE.md (`<project>/<subfolder>/CLAUDE.md`)

Overrides project-level rules for a specific directory.

```markdown
# Legacy Module — Special Rules

This is legacy code from the v1 acquisition. Different rules apply:

- Python 2.7 compatible — no f-strings, no walrus operators, no type hints
- Do NOT refactor or "improve" unless explicitly asked
- Tests: `python -m pytest legacy/tests/ -v` (not the main pytest)
- All new features in this module are frozen — report instead of implementing
```

---

## settings.json Full Reference

### Location

```
~/.claude/settings.json          ← global (all projects)
<project>/.claude/settings.json  ← project (this project only)
```

### Complete Schema

```json
{
  "permissions": {
    "allow": [
      "Read",
      "Glob",
      "Grep",
      "Bash(<pattern>)",
      "Write",
      "Edit"
    ],
    "deny": [
      "Bash(<dangerous-pattern>)"
    ]
  },
  "env": {
    "KEY": "literal_value",
    "SECRET_KEY": "${SHELL_VAR}"
  },
  "hooks": {
    "PreToolUse": [...],
    "PostToolUse": [...],
    "Stop": [...],
    "Notification": [...]
  },
  "mcpServers": {
    "<server-name>": {
      "command": "npx",
      "args": [...],
      "env": {}
    }
  }
}
```

### permissions.allow Patterns

```json
"allow": [
  "Read",                            // all file reads
  "Glob",                            // all glob searches
  "Grep",                            // all grep searches
  "Write",                           // all file writes (use carefully)
  "Edit",                            // all file edits (use carefully)
  "Bash(git status)",                // exact command
  "Bash(git log *)",                 // wildcard on arguments
  "Bash(git diff *)",
  "Bash(git log --oneline *)",
  "Bash(pytest *)",                  // all pytest invocations
  "Bash(pytest tests/ *)",           // pytest in tests/ only
  "Bash(ruff *)",
  "Bash(python -m mypy *)",
  "Bash(python scripts/*.py)",       // scripts in scripts/ dir
  "Bash(make test)",                 // specific make target
  "Bash(docker compose ps)"         // read-only docker
]
```

### permissions.deny Patterns

```json
"deny": [
  "Bash(rm -rf *)",                  // destructive delete
  "Bash(rm *)",                      // any delete
  "Bash(git push --force *)",        // force push
  "Bash(git push *)",                // all pushes (require explicit approval)
  "Bash(sudo *)",                    // no sudo
  "Bash(pip install *)",             // no package installs
  "Bash(npm install *)",
  "Bash(chmod 777 *)",               // no world-writable
  "Bash(DROP *)",                    // no SQL drops
  "Bash(DELETE FROM *)",             // no SQL deletes
  "Bash(curl * | bash)",             // no curl-pipe-bash
  "Bash(wget * -O- | bash)"
]
```

---

## .claudeignore Reference

```
# .claudeignore — files/dirs Claude won't read or search

# Python
__pycache__/
*.pyc
*.pyo
.pytest_cache/
.mypy_cache/
.ruff_cache/
htmlcov/
.coverage
*.egg-info/

# Node
node_modules/
.npm/
dist/
build/
.next/
.nuxt/

# Virtual environments
.venv/
venv/
env/

# Secrets — NEVER read these
.env
.env.*
*.pem
*.key
*.p12
*.pfx
secrets/
credentials/

# Version-controlled but noisy
*.lock
package-lock.json
yarn.lock
Pipfile.lock
poetry.lock

# Large generated files
coverage/
*.min.js
*.min.css
```

---

## Environment Variable Best Practices

```json
// ✅ Correct: interpolate from shell env
{
  "env": {
    "DATABASE_URL": "${DATABASE_URL}",
    "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}",
    "REDIS_URL": "${REDIS_URL}"
  }
}

// ❌ Wrong: hardcoded secrets
{
  "env": {
    "DATABASE_URL": "postgres://user:password@localhost/mydb",
    "ANTHROPIC_API_KEY": "sk-ant-api03-..."
  }
}

// ✅ Correct: non-sensitive literals are fine
{
  "env": {
    "PYTHONPATH": "src",
    "LOG_LEVEL": "debug",
    "ENVIRONMENT": "development"
  }
}
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

⬅️ **Prev:** [Memory System](../05_Memory_System/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Custom Skills](../07_Custom_Skills/Theory.md)
