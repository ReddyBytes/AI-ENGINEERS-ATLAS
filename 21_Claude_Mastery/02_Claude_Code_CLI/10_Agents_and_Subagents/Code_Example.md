# Agents and Subagents — Code Examples

## Example 1: Asking the main agent to parallelize work

```bash
claude

# Give Claude a task that's naturally parallel
> Write Theory.md, Cheatsheet.md, and Interview_QA.md for all 5 topics in
  the 02_Authentication/ folder. Each file should follow the style rules in
  CLAUDE.md. Parallelize across subagents for speed.

# Claude Code will:
# 1. Assess the task: 3 files × 5 topics = 15 files
# 2. Determine parallelism: 5 topics are independent
# 3. Spawn 5 subagents (one per topic)
# 4. Each writes 3 files concurrently
# 5. Main agent collects results and reports
```

---

## Example 2: Explicit parallel file generation

```bash
> I need to write documentation for each of the 8 API endpoints in src/api/routers/.
  For each endpoint, create a separate markdown file in docs/api/ with:
  - Endpoint description
  - Request/response examples
  - Error codes
  
  Use subagents to process all 8 endpoints in parallel.
```

---

## Example 3: Parallel code review

```bash
> Review all 12 modules in src/ for:
  - Type annotation completeness
  - Missing docstrings
  - Error handling gaps
  
  Process all modules in parallel. Return a consolidated report
  with findings ranked by severity.
```

---

## Example 4: Background agent for a long-running task

```bash
> Generate a comprehensive test suite for the entire payments/ module.
  This will take a while. Run it as a background agent so I can
  continue working. Report back when done.

# Main session continues...
> [continuing other work in main session]

# Background agent reports back:
# "Test suite complete: 47 tests written, all passing. 
#  Files created in tests/payments/"
```

---

## Example 5: Worktree-based parallel feature development

```bash
> We need to implement three independent features simultaneously:
  1. Rate limiting middleware (src/middleware/rate_limit.py)
  2. User profile endpoints (src/routers/profiles.py)
  3. Email notification service (src/services/notifications.py)
  
  Use separate worktrees for each feature so the changes are
  completely isolated. Report results when all three are done.

# Claude creates 3 worktrees:
# .claude/worktrees/feature-rate-limit/
# .claude/worktrees/feature-profiles/
# .claude/worktrees/feature-notifications/

# 3 subagents run simultaneously in isolation
# Main agent reviews and merges when done
```

---

## Example 6: Context window-aware task splitting

```bash
# Task that would exceed context window if done sequentially
> Refactor this entire 150-file codebase to use the new error handling
  pattern. The pattern is defined in src/exceptions.py.
  
  Split this across subagents. Each subagent should handle one 
  directory at a time. Use separate worktrees.

# Claude splits by directory:
# Subagent 1: src/api/ (25 files)
# Subagent 2: src/services/ (30 files)  
# Subagent 3: src/repositories/ (20 files)
# etc.
```

---

## Example 7: Instructing Claude to delegate explicitly

```bash
> For each of the following tasks, decide whether to handle it in the
  main session or spawn a subagent. Then execute:
  
  1. Add a docstring to register() in src/auth.py [small, main]
  2. Write Theory.md files for all 10 topics in 03_Advanced/ [large, subagents]
  3. Rename user_id to account_id across the entire codebase [dependent, main]
  4. Generate test data for the 5 main entity types [parallel, subagents]
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | Architecture details |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [MCP Servers](../09_MCP_Servers/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [IDE Integration](../11_IDE_Integration/Theory.md)
