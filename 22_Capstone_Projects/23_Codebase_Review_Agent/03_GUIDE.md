# Project 23 — Codebase Review Agent: Build Guide

## Before You Start

Install dependencies:

```bash
pip install anthropic python-dotenv
```

The `ast` and `pathlib` modules are in the Python standard library. No extra installs needed.

Create a `.env` file:

```
ANTHROPIC_API_KEY=your_key_here
```

Pick a target codebase to review. A good choice for testing: a small open-source Python project on GitHub (clone it locally), or a previous project from this course (`08_Multi_Tool_Research_Agent`, for example). Aim for 5-15 Python files for your first run.

---

## Step 1 — Understand what you are building

Read `02_ARCHITECTURE.md` fully before writing any code. Understand the five agent contracts. Know what each agent receives and what it returns. Sketch the data structures on paper if it helps.

The key insight: this is not one big prompt. It is five small, focused prompts, each with a well-defined input and output contract.

---

## Step 2 — File discovery with AST

Your first agent calls no external APIs. Use `pathlib` and `ast` only.

Walk the directory tree:

```python
from pathlib import Path

def find_python_files(codebase_path: str) -> list[Path]:
    root = Path(codebase_path)
    return sorted(root.rglob("*.py"))
```

For each file, parse with `ast.parse()` and extract: function names, class names, import names, and whether docstrings exist.

Skip files that fail to parse (syntax errors). Log a warning and continue.

Build and return the `FileManifest` as described in the Architecture file.

Checkpoint: Print the manifest for a small codebase. Verify function/class counts look right.

---

## Step 3 — Code quality agent

For each file in the manifest, call Claude with the quality review prompt from the Architecture file.

Return accumulated `QualityFindings`.

Do not send files larger than 6000 characters to Claude — truncate with a note. Very large files get a partial review.

Checkpoint: Review one file manually. Does Claude's feedback match what you see in the code?

---

## Step 4 — Security agent

Same pattern as Step 3, different prompt. Scan each file for the OWASP checklist from the Architecture file.

Key: the security prompt must ask for `line_hint` (approximate line number) for each finding. This makes the report actionable.

Checkpoint: Test on a file that deliberately has a hardcoded secret: `API_KEY = "sk-test-abc123"`. Verify Claude flags it as critical.

---

## Step 5 — Architecture agent

Do not send full source code. Send only the module map: file paths + their imports + class names + function names. This keeps the prompt compact and focuses Claude on structural patterns, not line-level details.

Build a compact module map dict from `FileManifest`:

```python
module_map = [
    {
        "file": f["relative_path"],
        "imports": f["imports"],
        "classes": f["classes"],
        "functions": f["functions"],
    }
    for f in manifest
]
```

Detect circular imports in Python before calling Claude. Add the result to the prompt as confirmed findings. Claude then analyzes God classes and missing abstractions, which require language understanding.

Checkpoint: Create two files that import each other. Verify your cycle detector catches it.

---

## Step 6 — Circular import detection

Implement `find_cycles(graph: dict) -> list` as described in the Architecture file.

Build the graph from the manifest: key = relative file path, value = list of imported module names that are also in the manifest (local imports only, not stdlib or third-party).

To match import names to file paths, strip `.py` and replace path separators with dots.

---

## Step 7 — Report synthesis agent

Collect all findings into a single dict. Call Claude with the report synthesis prompt.

The synthesis prompt receives JSON for all three finding types plus file stats. Claude writes the full Markdown report.

Write the output to `code_review_report.md` in the codebase directory (or `./` by default).

Checkpoint: Open the report. Does the Executive Summary match your own read of the codebase quality? If not, improve the synthesis prompt.

---

## Step 8 — Wire the pipeline together

Write a `main()` function that calls each agent in sequence and prints progress markers.

After Agent 5, print a summary line:

```
Review complete.
Overall quality score: X/10
Critical issues: N  |  Suggestions: N  |  Positives: N
```

Parse the quality score and counts from the report text using simple string search.

---

## Step 9 — CLI interface

Accept the codebase path as a command-line argument:

```bash
python codebase_review.py /path/to/project
python codebase_review.py /path/to/project --output ./reports/my_review.md
python codebase_review.py /path/to/project --skip-security
```

Flags to support:
- `--output` — path for the output report (default: `code_review_report.md`)
- `--skip-security` — run quality and architecture only
- `--model` — allow specifying the model (default: `claude-opus-4-5`)

---

## Step 10 — Test and iterate on prompts

Run the agent against a codebase you know well. Read the report critically.

Questions to ask:
- Are critical issues actually critical, or is Claude over-flagging?
- Are the suggestions ranked by impact, or are trivial style issues listed first?
- Does the quality score feel calibrated to the actual code quality?
- Are positive patterns identified, or is the report purely negative?

Iterate on the prompts. Prompt quality is the primary determinant of report quality.

---

## Stretch Goals

- Parallelize Agents 2, 3, and 4 using `concurrent.futures.ThreadPoolExecutor`
- Add a `--diff` flag: pass a git diff instead of a full codebase for PR-style review
- Generate an HTML report with syntax-highlighted code snippets for each issue
- Add a severity threshold flag: `--min-severity high` only reports high/critical issues
- Track reviews over time: append to `review_history.json` and report trends

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [01_MISSION.md](./01_MISSION.md) | What you'll build |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design and data flow |
| 03_GUIDE.md | ← you are here |
| [src/starter.py](./src/starter.py) | Skeleton with contracts |
| [src/solution.py](./src/solution.py) | Complete working solution |
| [04_RECAP.md](./04_RECAP.md) | What you built and what's next |

⬅️ **Prev:** [22 — AI Job Application Agent](../22_AI_Job_Application_Agent/01_MISSION.md) &nbsp;&nbsp;&nbsp; ➡️ **Back to Projects README**
