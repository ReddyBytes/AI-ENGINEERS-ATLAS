# Memory System — Interview Q&A

## Beginner 🟢

**Q1: What problem does the Claude Code memory system solve?**

Without memory, every Claude Code session starts cold — Claude only knows what's in CLAUDE.md and what you tell it in the current session. Anything discovered in previous sessions (architecture patterns, undocumented behaviors, your preferences) is lost. The memory system solves this by persisting useful facts between sessions as Markdown files, so Claude accumulates knowledge about your project over time.

---

**Q2: What is MEMORY.md and what does it contain?**

`MEMORY.md` is the memory index file — it's the entry point Claude reads when starting a session to recall what it knows about the project. It contains structured notes organized by category: architecture facts, key patterns, test setup, user preferences, and known quirks. It's plain Markdown, fully readable and editable. It links to more detailed memory files for longer entries.

---

**Q3: How do you explicitly ask Claude to save something to memory?**

Use natural language: "Remember that X", "Save to memory: Y", "Make a note that Z." Claude writes the fact to the appropriate section of MEMORY.md. You can also ask Claude to read back its memory: "What do you know about the database setup?" or "Show me everything you've saved for this project."

---

## Intermediate 🟡

**Q4: What are the four memory types in Claude Code and when does each apply?**

Project memory (codebase-specific facts in `.claude/memory/MEMORY.md`), global memory (cross-project preferences in `~/.claude/projects/<hash>/memory/`), user/feedback memory (corrections and stated preferences, stored alongside project memory), and reference memory (architecture documents and design decisions linked from the index). Most everyday memory is project-scoped. Global memory is for personal preferences and cross-cutting facts.

---

**Q5: What does Claude auto-save to memory vs what does it skip?**

Claude auto-saves when it discovers architecture patterns not obvious from reading the code, undocumented behaviors, test setup quirks, or when you state a preference or make a correction. It skips temporary task state ("we're halfway through refactoring X"), things that are immediately obvious from reading the codebase, volatile facts, and anything personal. The heuristic is: "would this fact be useful to know at the start of a future session?"

---

**Q6: How is MEMORY.md different from CLAUDE.md?**

CLAUDE.md is static — you write it, it contains instructions (rules, conventions, commands to run). It's the project brief. MEMORY.md is dynamic — Claude writes it during sessions based on discoveries and stated preferences. It contains facts (what is true) rather than instructions (what to do). Both are Markdown files that Claude reads at session start, but they serve different purposes and are written by different parties.

---

## Advanced 🔴

**Q7: How would you design a memory strategy for a large microservices repo where different engineers work on different services?**

Create a top-level MEMORY.md in `.claude/memory/` as an index, then create service-specific detail files: `auth-service.md`, `payments-service.md`, `user-service.md`. The index points to each detail file. Each detail file covers that service's architecture, test setup, deployment notes, and quirks. Check all memory files into Git so every engineer benefits. Engineer A working on auth updates `auth-service.md`; engineer B working on payments updates `payments-service.md`. This keeps memory modular and prevents the index from becoming bloated.

---

**Q8: What are the risks of poorly managed memory and how do you mitigate them?**

Risks: stale facts (architecture changed but memory wasn't updated), bloated memory (too much noise makes real facts harder to find), inconsistency (memory contradicts CLAUDE.md or current code). Mitigations: date entries that may become stale, periodically review and prune memory files (quarterly or after major refactors), keep entries short and scannable, link to code for facts that can be verified, and treat memory files like code — subject to review and version control.

---

**Q9: How do subagents and background agents interact with the memory system?**

When Claude Code spawns a subagent for a task, the subagent can read the project's MEMORY.md to bootstrap context without a lengthy briefing from the parent agent. This is especially valuable for parallel agents working on different parts of the same codebase — they all start from the same shared knowledge base. Subagents can also write new facts to memory after completing their task, so discoveries flow back into the shared pool. This creates an emergent knowledge accumulation pattern as more agents work in the repo.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |

⬅️ **Prev:** [Slash Commands](../04_Slash_Commands/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [CLAUDE.md and Settings](../06_CLAUDE_md_and_Settings/Theory.md)
