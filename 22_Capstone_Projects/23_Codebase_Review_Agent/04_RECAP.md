# Project 23 — Codebase Review Agent: Recap

## What You Built

You built a multi-agent system that reviews a Python codebase across four dimensions — code quality, security, architecture, and synthesis — and produces a single structured report. No human reviewer needed.

The system makes roughly `(2 * N_files) + 2` Claude API calls for a codebase with N files: one quality call and one security call per file, one architecture call for the whole module graph, and one synthesis call to write the final report.

---

## What You Practiced

**Multi-agent architecture with sequential handoffs.** Each agent has a single responsibility and a defined output contract. Agent 1's manifest feeds Agents 2, 3, and 4. Their findings feed Agent 5. This is the same pattern used in production AI pipelines for document processing, compliance analysis, and automated due diligence — the domain changes, the architecture does not.

**AST-based static analysis.** You parsed Python source code without executing it. The `ast` module gives you a complete structural view of a file — functions, classes, imports, docstrings — with zero risk of running malicious code. This is how real linters work. Pylint, Flake8, and Bandit all use AST traversal under the hood.

**Prompt scoping for consistency.** Each agent prompt is tightly scoped to one task. The security prompt does not ask Claude to evaluate code quality. The architecture prompt does not receive source code — only the module map. Scoping prevents Claude from conflating responsibilities and producing inconsistent output.

**Structured output with failure fallbacks.** Every Claude call has a fallback default. If Claude returns malformed JSON, the pipeline continues with empty findings rather than crashing. The final report may be incomplete, but the system completes.

**Cycle detection on a graph.** You built DFS-based cycle detection on the import graph. This is a classic computer science problem applied to a real engineering need. Circular imports are one of the most common architectural problems in Python codebases, and they are rarely detected before they cause import failures in production.

---

## Design Decisions Worth Examining

**Why not send source code to the Architecture agent?**
A 10-file codebase might be 5000 lines. Sending all source to one Claude call would hit context limits and cost more. The architecture agent only needs the structural graph — file names, what they import, what classes and functions they contain. That is enough to detect God classes, tight coupling, and missing abstractions without reading every line.

**Why is gap analysis in Agent 22 pure Python, while security analysis here uses Claude?**
Gap analysis is mechanical keyword matching — there is no semantic judgment needed. Security analysis requires language understanding: `API_KEY = "sk-live-..."` looks different from `api_key_param = "test"` to a human, and Claude can make that distinction. Use Claude where judgment is needed; use Python where it is not.

**Why sequential instead of parallel agents?**
Sequential is simpler to implement, debug, and explain. Parallel agents (using `concurrent.futures`) would be a meaningful performance improvement for large codebases: Agents 2, 3, and 4 are all independent reads from the same manifest. That parallelization is left as a stretch goal intentionally — the sequential version is the right starting point.

---

## Where This Could Go Next

**Git diff mode.** Instead of reviewing a full codebase, accept a `git diff` and review only the changed files. This is PR review: run the agent on every pull request and post findings as a GitHub comment.

**Incremental reviews.** Store the previous report's findings hash. On the next run, only review files that changed since the last review. This makes large codebases tractable.

**Severity thresholds as gates.** If critical issues are found, exit with code 1. Wire this into a CI pipeline: `python solution.py ./src --fail-on-critical`. The build fails if the review finds critical security issues.

**Language support beyond Python.** The AST layer is Python-specific, but the Claude agents are not. Swap out the AST parser for a JavaScript or TypeScript parser and the security/quality/architecture agents work without modification.

---

## The Pattern, Generalized

You built a system with this shape:

```
Ingest → Structured Manifest → N independent specialists → Synthesis
```

This shape appears everywhere in production AI:
- Legal contract review (document → clauses → risk agent, compliance agent, pricing agent → summary)
- Medical record analysis (record → structured data → diagnosis agent, medication agent, history agent → clinical summary)
- Financial due diligence (filings → financials → risk agent, growth agent, comparable agent → investment memo)

The codebase review domain is a clear, safe test bed for this pattern. The architecture carries.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [01_MISSION.md](./01_MISSION.md) | What you built |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design |
| [03_GUIDE.md](./03_GUIDE.md) | Build guide |
| [src/starter.py](./src/starter.py) | Starter skeleton |
| [src/solution.py](./src/solution.py) | Complete solution |
| 04_RECAP.md | ← you are here |

⬅️ **Prev:** [22 — AI Job Application Agent](../22_AI_Job_Application_Agent/01_MISSION.md) &nbsp;&nbsp;&nbsp; ➡️ **Back to Projects README**
