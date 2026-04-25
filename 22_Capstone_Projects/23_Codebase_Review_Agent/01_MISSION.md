# Project 23 — Codebase Review Agent

## Mission Brief

A new developer joins a team. She is handed a codebase and told to "get familiar with it." She opens the first file. It's 800 lines. She opens the second. There are circular imports. The third has hardcoded passwords. She doesn't know what she doesn't know — and she has no senior engineer to ask.

Now imagine she had a colleague who had already read every file, catalogued every function, flagged every security risk, mapped every module dependency, and synthesized it all into a structured report before her first commit. That colleague doesn't exist at most companies. But you are about to build it.

This project builds a **multi-agent codebase review system**. Four specialized agents work in sequence, each focused on one dimension of code quality. A fifth agent synthesizes their findings into a comprehensive `code_review_report.md`. The result reads like a senior engineer spent a full day reviewing the codebase — because that's the standard we're targeting.

---

## What You Will Build

A multi-agent system that accepts a directory path and produces a complete code review:

**Agent 1 — File Discovery Agent**
Walks the directory tree, finds all `.py` files, reads their contents, builds a structured manifest: filename, size, function list (via Python AST), class list, import list.

**Agent 2 — Code Quality Agent**
Claude reviews each file for: naming conventions, function length, complexity, documentation quality, code duplication, adherence to Pythonic patterns.

**Agent 3 — Security Agent**
Claude scans for OWASP-relevant issues: hardcoded secrets, SQL injection patterns, insecure deserialization, missing input validation, dangerous function use (`eval`, `exec`, `pickle.loads`), exposed debug endpoints.

**Agent 4 — Architecture Agent**
Analyzes the module structure as a whole: circular imports, God classes (single class doing too much), missing abstraction layers, tight coupling, module responsibility violations.

**Agent 5 — Report Agent**
Synthesizes all findings into a structured Markdown report:
- Executive Summary (overall quality score 1-10)
- Critical Issues (must fix — security and bugs)
- Improvement Suggestions (ranked by impact)
- Architecture Observations
- Positive Patterns (what is done well)

---

## Output

`code_review_report.md` — a single structured Markdown file with all findings.

---

## Tech Stack

| Library | Why |
|---|---|
| `anthropic` | Claude API — code review, security scan, architecture analysis, report synthesis |
| `pathlib` | Walk directory tree, filter `.py` files |
| `ast` | Parse Python files to extract functions, classes, imports without executing code |
| `python-dotenv` | Load API key from `.env` |

No external web calls. No vector databases. This runs entirely locally.

---

## Format

**Minimal Hints** — You are given the agent responsibilities, input/output contracts, and the overall architecture. The implementation is up to you. Read the Architecture file carefully before starting.

---

## Difficulty

Advanced (4.5 / 5)

The multi-agent orchestration pattern requires careful state design. Each agent produces a structured artifact that the next agent consumes. The AST-based file analysis requires understanding Python's `ast` module. The biggest challenge is prompt engineering: getting Claude to produce structured, consistent findings across files of wildly different quality levels.

---

## Prerequisites

- Completed the Multi-Tool Research Agent or Multi-Agent Research System project, or equivalent
- Understand Claude's tool_use API (or be prepared to learn it for this project)
- Comfortable with Python's `ast` module basics
- Anthropic API key set in `.env` as `ANTHROPIC_API_KEY`
- Python 3.10+
- No pip installs beyond anthropic and python-dotenv

---

## Expected Output

```
Codebase Review Agent
======================
Target: /path/to/your/codebase

[Agent 1] File Discovery...
          Found 12 Python files (3,847 lines total)
          47 functions, 8 classes, 23 unique imports

[Agent 2] Code Quality Review...
          Reviewing app.py (127 lines)...
          Reviewing models.py (89 lines)...
          ...

[Agent 3] Security Scan...
          app.py: 2 issues found
          db.py: 1 critical issue found
          ...

[Agent 4] Architecture Analysis...
          Module graph analyzed. 1 circular import detected.

[Agent 5] Synthesizing report...
          code_review_report.md written (247 lines)

Review complete.
Overall quality score: 6/10
Critical issues: 3  |  Suggestions: 11  |  Positives: 5
```

---

## Sample Report Structure

```markdown
# Code Review Report
**Codebase:** /path/to/project
**Reviewed:** 2025-09-01
**Overall Quality Score:** 6/10

---

## Executive Summary
...

## Critical Issues
### [SECURITY] Hardcoded API key in config.py line 14
...

## Improvement Suggestions
### [HIGH] God class: UserManager in models.py handles 12 responsibilities
...

## Architecture Observations
...

## Positive Patterns
...
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| 01_MISSION.md | ← you are here |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | Multi-agent system design |
| [03_GUIDE.md](./03_GUIDE.md) | 10-step build guide (minimal hints) |
| [src/starter.py](./src/starter.py) | Skeleton with contracts |
| [src/solution.py](./src/solution.py) | Complete working solution |
| [04_RECAP.md](./04_RECAP.md) | What you built and what's next |

⬅️ **Prev:** [22 — AI Job Application Agent](../22_AI_Job_Application_Agent/01_MISSION.md) &nbsp;&nbsp;&nbsp; ➡️ **Back to Projects README**
