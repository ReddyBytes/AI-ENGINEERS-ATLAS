# Claude Code as Agent — Interview Q&A

## Beginner Level

**Q1: How is Claude Code itself an example of the agent pattern?**

A: Claude Code implements all four components of an agent: (1) the LLM (Claude Sonnet/Opus) as the reasoning core that decides what to do at each step; (2) built-in tools (Read, Write, Edit, Bash, Glob, Grep, etc.) that allow it to take real actions on your filesystem and shell; (3) a context window that accumulates all file reads, bash outputs, and edit results as working memory; (4) an agent loop that keeps running until the task is complete or you interrupt it. When you ask Claude Code to "add error handling to all database functions," it runs the full loop: Glob to find files, Grep to find functions, Read to understand code, Edit to make changes, Bash to run tests, loop until passing.

---

**Q2: What is the purpose of CLAUDE.md files in Claude Code's architecture?**

A: CLAUDE.md files are the mechanism for persistent, context-specific system prompts. Claude Code loads `~/.claude/CLAUDE.md` (global, loaded in every session) and any `CLAUDE.md` found in the project directory (loaded for that project). Their contents are injected into the agent's system prompt at session start. This allows: project-specific context ("This is an Airflow v3 project on Python 3.11"), behavioral rules ("Never commit without asking"), and team conventions ("All SQL must use the query_builder module"). Without CLAUDE.md, every session starts from zero. With it, the agent has the right context for every task in that project.

---

**Q3: Why does the Edit tool require a unique string match rather than a line number?**

A: Line numbers change when you edit a file — after making one edit, all subsequent line numbers below that edit shift. If Claude Code is making 5 edits to a file in one session, line-number-based edits would fail after the first one because the file changed. Unique string matching (old_string → new_string) is stable: as long as the target code exists and is unique in the file, the edit succeeds regardless of how many other edits have been made. It also prevents a class of error: if the code you're trying to edit was already changed (by you or another process), the unique string match fails loudly rather than editing the wrong line silently. This "fail loud" design is intentional.

---

## Intermediate Level

**Q4: How does Claude Code use the agent loop for a multi-file refactoring task?**

A: Consider "rename the `process_data()` function to `transform_data()` everywhere." Claude Code's loop:

Step 1: `Glob("**/*.py")` — find all Python files.
Step 2: `Grep("process_data", files)` — find which files contain the function.
Step 3: For each matching file: `Read(file)` — verify the context, then `Edit(file, old_string="process_data", new_string="transform_data")` — apply the rename.
Step 4: `Bash("python -m pytest")` — run tests to verify nothing broke.
Step 5: Read test output — check for failures.
Step 6: If failures, read the failing test files, understand why, fix.
Step 7: Return summary to user.

Each step uses the previous result to decide what to do next. This is multi-step reasoning using the built-in tool set. The loop terminates when tests pass and the rename is confirmed complete.

---

**Q5: How does the MEMORY.md pattern implement the external agent memory concept from Topic 06?**

A: MEMORY.md is a file-based implementation of external memory. At session start, Claude Code reads the relevant MEMORY.md file and injects it into the system prompt — loading the stored memories into the active context window. When you say "remember that I prefer metric units," Claude Code appends this to MEMORY.md. At the next session, that fact is loaded again. This implements exactly the external memory loop: save to external store → load at next session → use in context. The file format (plain Markdown) is deliberately simple: it's human-readable and human-editable, so you can review and correct stored memories without specialized tooling. The vector DB approach from Topic 06 scales better for thousands of memories, but for project-scoped or user-specific memory, a Markdown file is often sufficient.

---

**Q6: What design lessons from Claude Code's architecture are most transferable to building your own agents?**

A: Five lessons:

1. **Read before write**: Claude Code always reads a file before editing it. For any agent that modifies state, give it an inspect tool it should call before a modify tool. This prevents acting on stale information.

2. **Fail loud**: the Edit tool raises an error if the target string doesn't exist. Design your tools to raise explicit errors rather than returning empty results or silently doing nothing — silent failures are the hardest bugs to find.

3. **Minimal permission scope**: Claude Code's tools are scoped to the project directory. Every tool you build should operate on the minimum possible scope of the system.

4. **Human-readable memory**: MEMORY.md is a plain text file. Don't over-engineer memory systems — a simple, human-readable format often works better than a database because it's inspectable and correctable.

5. **Transparent actions**: Claude Code shows every tool call in the terminal. Build observability into your agents from the start — users should be able to understand what the agent is doing, and you should be able to audit it later.

---

## Advanced Level

**Q7: Claude Code uses worktrees as a subagent isolation mechanism. Explain the parallel to the subagent pattern from Topic 08.**

A: A Git worktree is an isolated copy of the repository at a separate filesystem path. When Claude Code's Agent tool spawns a subagent to work on a task, it creates a new worktree for that agent. This implements subagent isolation at the filesystem level:

- **Context isolation** (Topic 08 concept): the subagent works in its own directory with its own conversation history — it doesn't see the parent agent's conversation.
- **Tool isolation**: the subagent's file operations are scoped to its worktree. Changes there don't affect the main working tree until explicitly merged.
- **Failure isolation**: if the subagent's changes break things, you delete the worktree — no effect on main. This is the same as the subagent error not crashing the orchestrator.
- **Parallelism**: multiple worktrees can run simultaneously — the filesystem equivalent of parallel subagents.

The worktree is the physical implementation of the logical isolation that the subagent pattern provides. It's elegant: instead of needing a complex sandbox or VM, a Git worktree provides the isolation at the version-control level for free.

---

**Q8: How does Claude Code's permission system (allowedTools, deniedTools, permission modes) relate to the safety principles from Topic 10?**

A: Claude Code's permission system is a direct implementation of the least-privilege principle for tools. The relationship:

- **`allowedTools`** = explicit whitelist: only the specified tools are available. This limits the blast radius of any error or injection — the agent can only do what's on the list.
- **`deniedTools`** = explicit blacklist: all tools except those listed are available. More permissive, but removes specific dangerous capabilities.
- **Permission modes**: read-only mode (only read operations), default mode (reads + writes with confirmation for dangerous bash), trust-all mode (no confirmation). These map to the "risk-proportional controls" principle — use the most restrictive mode appropriate for the task.

For a code review agent that should only read: `allowedTools: ["Read", "Glob", "Grep"]`. For a code generation agent: add `Write` and `Edit`. For a build automation agent: add `Bash` (with confirmation). This is exactly the tool permission scoping discussed in Safety in Agents — Claude Code's configuration just makes it declarative.

---

**Q9: If you were building a production coding agent similar to Claude Code from scratch, what would be your minimal required tool set and what architectural decisions would you make based on Claude Code's design?**

A: Minimal production coding agent tool set:

**Essential (6 tools):**
1. `read_file(path)` — read file contents
2. `write_file(path, content)` — create new files
3. `edit_file(path, old_str, new_str)` — modify existing files (with uniqueness check)
4. `list_files(pattern)` — find files by glob
5. `search_content(pattern, dir)` — grep-style search
6. `run_command(cmd, cwd, timeout)` — execute shell commands

**Architectural decisions from Claude Code's design:**

1. **Edit tool uniqueness enforcement**: implement the old_string uniqueness check from day one — it's the primary mechanism preventing wrong edits.

2. **Read-before-write enforcement**: in the system prompt, require the agent to call `read_file` before any `edit_file` call. Makes this a behavioral rule, not just a suggestion.

3. **Output truncation on all tools**: cap every tool output at a sensible token limit (e.g., file reads at 2000 lines, command output at 10KB). Long outputs are the primary cause of context overflow.

4. **Audit logging on every tool call**: log tool name, inputs, result size, duration. Non-negotiable for any production system.

5. **Permission system**: implement allow/deny lists before launch, not as an afterthought. Default to restrictive; let users expand permissions explicitly.

6. **CLAUDE.md equivalent**: let users drop a `.agent-context.md` file in their project directory. Load it at session start. This dramatically improves quality for repeated use on the same project.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | Full internals |

⬅️ **Prev:** [Safety in Agents](../10_Safety_in_Agents/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Track 4 README](../Readme.md)
