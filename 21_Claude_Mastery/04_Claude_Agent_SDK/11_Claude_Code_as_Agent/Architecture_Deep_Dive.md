# Claude Code as Agent — Architecture Deep Dive

## Complete System Architecture

```mermaid
flowchart TD
    subgraph USER_LAYER["User Interface"]
        CLI["Terminal (CLI)"]
        VSCODE["VS Code Extension"]
        API_INTERFACE["API Interface"]
    end

    subgraph CLAUDE_CODE["Claude Code Agent System"]
        subgraph SESSION["Session Initialization"]
            LOAD_GLOBAL["Load ~/.claude/CLAUDE.md\n(global rules)"]
            LOAD_PROJECT["Load ./CLAUDE.md\n(project rules)"]
            LOAD_MEMORY["Load MEMORY.md\n(cross-session memory)"]
            BUILD_SYSTEM["Build System Prompt\n(global + project + memory)"]
        end

        subgraph LOOP["Agent Loop"]
            CLAUDE_LLM["Claude\n(Sonnet / Opus)"]
            DECIDE{"Response\ntype?"}
            FINAL["Return final\nresponse to user"]
        end

        subgraph PERMISSION["Permission Layer"]
            ALLOWED["allowedTools\n(whitelist)"]
            DENIED["deniedTools\n(blacklist)"]
            CONFIRM["Dangerous ops\n(confirm before bash)"]
        end

        subgraph TOOLS["Built-in Tool Set"]
            FILE_TOOLS["File Operations\nRead / Write / Edit"]
            SEARCH_TOOLS["Search\nGlob / Grep"]
            EXEC_TOOLS["Execution\nBash"]
            WEB_TOOLS["Web\nWebFetch"]
            AGENT_TOOLS["Agent\n(spawn subagent)"]
            META_TOOLS["Meta\nTaskCreate/Update\nCronCreate/Delete\nNotebookEdit"]
        end

        subgraph MEMORY_LAYER["Memory Layer"]
            IN_CTX["In-Context\n(current session history)"]
            MEMORY_FILE["MEMORY.md\n(cross-session)"]
            CLAUDE_MD["CLAUDE.md\n(instructions)"]
        end
    end

    subgraph ISOLATION["Subagent Isolation"]
        WORKTREE["Git Worktrees\n(isolated filesystem)"]
        SUBAGENT["Subagent Instance\n(own context + tools)"]
    end

    CLI --> SESSION
    VSCODE --> SESSION
    SESSION --> BUILD_SYSTEM
    BUILD_SYSTEM --> CLAUDE_LLM
    CLAUDE_LLM --> DECIDE
    DECIDE -->|"tool_use"| PERMISSION
    DECIDE -->|"end_turn"| FINAL
    FINAL --> CLI
    PERMISSION --> TOOLS
    TOOLS -->|"result"| CLAUDE_LLM
    AGENT_TOOLS --> WORKTREE
    WORKTREE --> SUBAGENT
    SUBAGENT -->|"result"| AGENT_TOOLS
    MEMORY_LAYER --> SESSION
```

---

## The Edit Tool — Why Uniqueness Matters

The Edit tool's uniqueness requirement is a deliberate safety mechanism:

```mermaid
flowchart TD
    EDIT["Edit(file, old_str, new_str)"]
    EDIT --> COUNT{"How many times\ndoes old_str appear?"}
    COUNT -->|"0 times"| FAIL_NOT_FOUND["Fail: string not found\n(explicit error)"]
    COUNT -->|"1 time"| SUCCESS["Apply replacement\n(safe — unambiguous)"]
    COUNT -->|"2+ times"| FAIL_AMBIGUOUS["Fail: string appears multiple times\n(explicit error — provide more context)"]
    
    FAIL_NOT_FOUND --> RETRY["Claude reads file again\nUses more specific string"]
    FAIL_AMBIGUOUS --> RETRY
    SUCCESS --> VERIFY["Claude can read file\nto verify the edit"]
```

Why not line numbers?
```
Original file (line 5 = target):
Line 1: import os
Line 2: import sys
Line 3: 
Line 4: def process():
Line 5:     x = 1  ← target
Line 6:     return x

After adding a line at line 2:
Line 1: import os
Line 2: import json  ← new line
Line 3: import sys
Line 4:
Line 5: def process():
Line 6:     x = 1  ← target is now line 6!
Line 7:     return x
```

Unique string `    x = 1` still finds the target regardless of line shifts.

---

## CLAUDE.md Loading Stack

```mermaid
flowchart TD
    START["Session starts in\n/Users/alice/project/backend/"]
    START --> GLOBAL["Load ~/.claude/CLAUDE.md\n(always loaded)"]
    GLOBAL --> WALK["Walk up directory tree\nlooking for CLAUDE.md files"]
    WALK --> P1["Check /Users/alice/project/backend/CLAUDE.md\n(exists → load)"]
    P1 --> P2["Check /Users/alice/project/CLAUDE.md\n(exists → load)"]
    P2 --> P3["Check /Users/alice/CLAUDE.md\n(does not exist → skip)"]
    P3 --> COMBINE["Combine: global + project + subdir"]
    COMBINE --> SYSTEM["Inject as system prompt\nfor this session"]
```

The loading is hierarchical — the deepest (most specific) CLAUDE.md instructions layer on top of broader ones.

---

## Tool Execution with Permission Check

```mermaid
sequenceDiagram
    participant C as Claude
    participant SDK as Claude Code SDK
    participant PERM as Permission Check
    participant TOOL as Tool Executor

    C->>SDK: tool_use: Bash(cmd="rm -rf /tmp/old")
    SDK->>PERM: Check: is "Bash" in allowedTools?
    PERM-->>SDK: Yes (not denied)
    SDK->>PERM: Check: is this a dangerous command?
    Note over PERM: rm, sudo, curl -X DELETE,<br>git reset --hard → dangerous
    PERM-->>SDK: Yes — dangerous Bash command
    SDK->>SDK: Display to user: "Allow this command? [y/N]"
    Note over SDK: User types "y"
    SDK->>TOOL: Execute Bash("rm -rf /tmp/old")
    TOOL-->>SDK: "" (success, no output)
    SDK->>C: tool_result: ""
```

---

## MEMORY.md Lifecycle

```
Session 1:
┌──────────────────────────────────────────────────────────┐
│ User: "Remember that this project uses Python 3.11"      │
│ Claude: Calls Write(MEMORY.md, "## Active Projects\n\n   │
│         - Project X: Python 3.11, FastAPI...")           │
└──────────────────────────────────────────────────────────┘
            ↓  (session ends)
┌─────────────────────────────────┐
│ MEMORY.md on disk:              │
│ ## Active Projects              │
│ - Project X: Python 3.11        │
└─────────────────────────────────┘
            ↓  (next session starts)
Session 2:
┌──────────────────────────────────────────────────────────┐
│ Claude Code reads MEMORY.md                              │
│ Injects contents into system prompt                      │
│ User: "What Python version are we using?"                │
│ Claude: "This project uses Python 3.11 (from memory)"    │
└──────────────────────────────────────────────────────────┘
```

---

## Worktree Isolation for Subagents

```mermaid
flowchart TD
    MAIN["Main session\n/project/ (branch: main)"]
    MAIN -->|"Agent tool spawned"| WORKTREE["Git Worktree created\n/project/.claude/worktrees/feature-xyz/\n(branch: claude/feature-xyz)"]
    
    subgraph WORKER["Subagent in Worktree"]
        W_READ["Read files"]
        W_EDIT["Edit files\n(in worktree only)"]
        W_BASH["Run tests\n(in worktree only)"]
    end
    
    WORKTREE --> WORKER
    WORKER -->|"Result returned"| MAIN
    MAIN -->|"User: keep changes"| MERGE["git merge claude/feature-xyz\ninto main"]
    MAIN -->|"User: discard"| DELETE["git worktree remove\n(clean delete)"]
```

The worktree provides: isolation (subagent can't affect main branch), safety (easy rollback), parallelism (multiple worktrees can exist simultaneously).

---

## Comparing Claude Code's Architecture to This Track's Concepts

| This Track | Claude Code Implementation |
|---|---|
| Topic 01: Agent loop | Built-in `while True` loop that runs until task complete |
| Topic 02: Why SDK | Claude Code IS the pre-built SDK |
| Topic 03: `@tool` decorator | Each built-in tool is a registered function |
| Topic 04: Tool call lifecycle | Read → Bash → Edit → Bash test cycle |
| Topic 05: Multi-step reasoning | "Fix all failing tests" → multi-file loop |
| Topic 06: Agent memory | MEMORY.md (external) + conversation history (in-context) |
| Topic 07: Orchestration | Agent tool that spawns child agents |
| Topic 08: Subagents | Workers spawned in isolated worktrees |
| Topic 09: Handoffs | Worktree result merged back to parent |
| Topic 10: Safety | Permission modes, dangerous command confirmation |
| Topic 11: This topic | The complete picture |

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Architecture_Deep_Dive.md** | ← you are here |

⬅️ **Prev:** [Safety in Agents](../10_Safety_in_Agents/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Track 4 README](../Readme.md)
