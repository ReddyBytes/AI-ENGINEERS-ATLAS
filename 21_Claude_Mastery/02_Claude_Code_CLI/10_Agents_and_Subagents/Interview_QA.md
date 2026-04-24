# Agents and Subagents — Interview Q&A

## Beginner 🟢

**Q1: What is a subagent in Claude Code?**

<details>
<summary>💡 Show Answer</summary>

A subagent is a new Claude Code instance spawned by the main agent to handle a specific delegated task. It has its own context window, tool access, and working environment. Subagents are used to parallelize large tasks — multiple subagents work simultaneously on independent subtasks, then report results back to the main agent. The mechanism is the Agent tool, which the main Claude uses to create and manage child instances.

</details>

---

<br>

**Q2: Why would you use subagents instead of having one agent do everything?**

<details>
<summary>💡 Show Answer</summary>

Two main reasons: speed and context. Speed: independent tasks can run in parallel — writing 12 files with 4 subagents takes ~1/4 the time of doing them sequentially. Context: a single agent working on a large task will eventually fill its context window with old messages and lose track of early decisions. Each subagent starts fresh with a clean context focused on its specific scope.

</details>

---

<br>

**Q3: What is a worktree and why is it useful with subagents?**

<details>
<summary>💡 Show Answer</summary>

A worktree is an isolated Git working directory that shares the repository but has its own independent file state. When two subagents need to modify files in parallel, giving each a separate worktree prevents conflicts — agent A's in-progress changes to `src/auth/` don't interfere with agent B's changes to `src/payments/`. After both finish, you can merge or review the worktrees separately.

</details>

---

## Intermediate 🟡

**Q4: What information must you give a subagent for it to work independently?**

<details>
<summary>💡 Show Answer</summary>

Everything it needs — subagents don't share context with the parent. Include: the specific task description, relevant project context (tech stack, conventions), exact file paths to create or modify, where to find CLAUDE.md and MEMORY.md for project rules, any constraints (scope limitations, naming conventions), and what to report back when done. A well-briefed subagent is self-sufficient; a poorly briefed subagent asks questions, reducing the efficiency benefit.

</details>

---

<br>

**Q5: What are background agents and when would you use them?**

<details>
<summary>💡 Show Answer</summary>

Background agents are subagents that run without blocking the main session. You dispatch a task to a background agent and immediately continue working on other things. The background agent runs to completion independently and reports back when done. Use them for: long-running tasks (large refactors, test suite generation), tasks where you don't need to supervise execution, or when you want to parallelize work without waiting for each subagent to finish before starting the next.

</details>

---

<br>

**Q6: How do you decide whether to parallelize a task across subagents or handle it in the main agent?**

<details>
<summary>💡 Show Answer</summary>

Key decision criteria: (1) Are the subtasks independent? — parallel file writes are independent, but step 2 depends on step 1's output is not. (2) Is the total scope large? — more than 10 files or 30 tool calls is a good trigger to consider subagents. (3) Are there parallel file modifications needed? — if yes, use subagents with worktrees. If all three criteria suggest parallelization, spawn subagents. If the task has dependencies or is small and fast, handle it in the main agent to avoid subagent orchestration overhead.

</details>

---

## Advanced 🔴

**Q7: How does context window management interact with the subagent architecture?**

<details>
<summary>💡 Show Answer</summary>

Every Claude model has a fixed context window (e.g., 200K tokens for Claude Sonnet). In a long session, earlier messages get truncated when the window fills. For a 50-file refactor, a single agent reaching the context limit late in the task would start making inconsistent decisions because it can no longer "see" early choices. Subagents solve this by giving each one a scoped task that fits comfortably in a fresh context window. The main agent's context stays clean because it only sees subagent summaries, not the full execution details.

</details>

---

<br>

**Q8: What are the rate limit and cost implications of running many parallel subagents?**

<details>
<summary>💡 Show Answer</summary>

Each subagent makes its own API calls, consuming tokens and hitting rate limits independently. Running 10 parallel subagents is effectively 10 simultaneous API users. Anthropic's rate limits apply per API key — too many parallel agents will hit token-per-minute (TPM) or request-per-minute (RPM) limits, causing some agents to slow or fail. Practical sweet spot: 3-5 parallel agents. Also note cost: parallel agents don't reduce token usage — they consume the same tokens as sequential but faster. Budget accordingly for large parallelized tasks.

</details>

---

<br>

**Q9: How does the subagent pattern in Claude Code relate to multi-agent architectures in AI systems?**

<details>
<summary>💡 Show Answer</summary>

Claude Code's subagent system is an implementation of the orchestrator-worker multi-agent pattern: the main agent is the orchestrator that decomposes tasks and delegates; subagents are workers that execute specific scopes. This mirrors patterns like LangGraph's supervisor architecture and AutoGen's team-based approaches. The key difference: Claude Code's agents share the same underlying model and tool set by default, whereas general multi-agent systems often specialize agents with different models or tools. The worktree isolation in Claude Code adds a file-system-level separation that most agent frameworks don't have natively.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | Architecture details |
| [📄 Code_Example.md](./Code_Example.md) | Practical examples |

⬅️ **Prev:** [MCP Servers](../09_MCP_Servers/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [IDE Integration](../11_IDE_Integration/Theory.md)
