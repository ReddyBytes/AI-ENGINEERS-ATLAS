# Slash Commands — Code Examples

## Example 1: Basic built-in commands

```bash
# In Claude Code REPL

# See all available commands (built-in + custom)
> /help

# Check session cost so far
> /cost
# Session cost: $0.04 | Input: 12,400 tokens | Output: 3,200 tokens

# Clear conversation to start fresh task
> /clear

# Compact history when approaching context limits
> /compact

# Check current status
> /status
# Model: claude-sonnet-4-6
# Session ID: sess_abc123
# Memory: ~/.claude/projects/myproject/MEMORY.md
```

---

## Example 2: A minimal custom command

```
# File: .claude/commands/review.md
---
description: Review current changes for bugs and style issues
allowed_tools:
  - Bash
  - Read
  - Grep
---

Run `git diff HEAD` to see current unstaged changes.
Run `git diff --cached HEAD` for staged changes.

Review all changes for:
1. Logic errors or obvious bugs
2. Missing error handling (uncaught exceptions)
3. Security issues (hardcoded secrets, SQL injection patterns)
4. Style issues (unused imports, missing type hints, overly long functions)
5. Missing tests for new functions

Format your findings as:
- **Critical** (must fix): ...
- **Warning** (should fix): ...
- **Suggestion** (optional): ...

Keep it concise — maximum 3 items per category.
```

Invocation:
```
> /review
```

---

## Example 3: Command with arguments

```
# File: .claude/commands/docgen.md
---
description: Generate docstrings for a Python file
argument_hint: <filepath>
allowed_tools:
  - Read
  - Edit
---

Read the Python file at $ARGUMENTS.
For every public function and class that doesn't already have a docstring, add
a Google-style docstring.

Rules:
- Preserve all existing code exactly
- Add Args, Returns, and Raises sections where applicable
- Use the function signature and body to infer what each argument does
- Do not add docstrings to private functions (prefixed with _)

Show me the diff before applying any changes.
```

Invocations:
```
> /docgen src/auth/jwt_handler.py
> /docgen src/api/users.py
> /docgen src/utils/string_helpers.py
```

---

## Example 4: A deployment pre-flight command

```
# File: .claude/commands/preflight.md
---
description: Run all pre-deployment checks
allowed_tools:
  - Bash
  - Read
  - Grep
---

Run these checks in order and report PASS or FAIL for each:

**Code quality:**
1. `ruff check .` — linting clean
2. `python -m mypy src/ --strict` — type checking passes
3. No `print()` debugging in src/ (grep for bare print statements)

**Tests:**
4. `pytest tests/ -q --tb=short` — all tests pass

**Config:**
5. `.env.example` exists and lists all required variables
6. All variables in `.env.example` are set in the running environment

**Git:**
7. `git status --short` — no uncommitted changes
8. Current branch is not `main` (we should be on a feature branch)

If any check fails, STOP and list all failures clearly.
If all checks pass, output: "All checks passed. Ready to deploy."
```

---

## Example 5: A global command for PR summaries

```
# File: ~/.claude/commands/pr-summary.md
---
description: Generate a GitHub PR description from current branch changes
allowed_tools:
  - Bash
---

Run:
- `git log main...HEAD --oneline` to see all commits
- `git diff main...HEAD --stat` to see files changed
- `git diff main...HEAD` for the full diff

Write a pull request description in GitHub Markdown format:

## Summary
[1-3 bullet points: what changed and why]

## Changes
[Files affected and what changed in each]

## Testing
[How to test this change — commands to run or manual steps]

## Breaking Changes
[List any breaking changes, or "None"]

Keep it concise and technical. Write for a code reviewer who knows the codebase.
```

---

## Example 6: Full project command directory

```
myproject/
└── .claude/
    └── commands/
        ├── review.md          → /review
        ├── docgen.md          → /docgen <filepath>
        ├── preflight.md       → /preflight
        ├── test-single.md     → /test-single <test_name>
        ├── db-migrate.md      → /db-migrate
        └── changelog.md       → /changelog
```

All of these are committed to Git and available to every developer on the team.

---

## Example 7: /test-single command

```
# File: .claude/commands/test-single.md
---
description: Run a specific test and diagnose failures
argument_hint: <test_name_or_path>
allowed_tools:
  - Bash
  - Read
---

Run: `pytest $ARGUMENTS -v --tb=long`

If the test passes: report "Test passed."
If it fails:
1. Read the failing test file
2. Read the source file being tested
3. Diagnose why the test is failing
4. Suggest a fix (but don't apply it yet — show the proposed change first)
```

Invocation:
```
> /test-single tests/test_auth.py::test_login_invalid_password
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [Basic Usage and Commands](../03_Basic_Usage_and_Commands/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Memory System](../05_Memory_System/Theory.md)
