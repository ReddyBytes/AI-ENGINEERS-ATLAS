# Multi-Agent Orchestration — Architecture Deep Dive

## Orchestration Topology Patterns

```mermaid
graph TD
    subgraph FAN_OUT["Fan-Out / Fan-In"]
        O1["Orchestrator"] -->|"task 1"| W1A["Worker 1"]
        O1 -->|"task 2"| W1B["Worker 2"]
        O1 -->|"task 3"| W1C["Worker 3"]
        W1A -->|"result 1"| O1
        W1B -->|"result 2"| O1
        W1C -->|"result 3"| O1
        O1 -->|"assembled result"| END1["Output"]
    end

    subgraph HIER["Hierarchical"]
        TOP["Top Orchestrator"] -->|"domain A"| SUB1["Sub-orchestrator A"]
        TOP -->|"domain B"| SUB2["Sub-orchestrator B"]
        SUB1 -->|"batch 1"| W2A["Worker"]
        SUB1 -->|"batch 2"| W2B["Worker"]
        SUB2 -->|"batch 3"| W2C["Worker"]
        SUB2 -->|"batch 4"| W2D["Worker"]
        W2A & W2B --> SUB1
        W2C & W2D --> SUB2
        SUB1 & SUB2 --> TOP
        TOP --> END2["Output"]
    end

    subgraph PIPE["Sequential Pipeline"]
        direction LR
        AGENT_A["Agent A\n(Extract)"] -->|"handoff"| AGENT_B["Agent B\n(Validate)"]
        AGENT_B -->|"handoff"| AGENT_C["Agent C\n(Action)"]
        AGENT_C --> END3["Output"]
    end
```

---

## Orchestrator Decision Algorithm

How the orchestrator decides what workers to spawn:

```mermaid
flowchart TD
    GOAL["Complex Goal Received"]
    GOAL --> DECOMPOSE["Decompose: What are the independent sub-tasks?"]
    DECOMPOSE --> DEPENDENT{"Are tasks\ndependent?"}
    DEPENDENT -->|"Yes"| SEQUENTIAL["Use sequential pipeline\n(handoffs between stages)"]
    DEPENDENT -->|"No"| PARALLEL_CHECK{"How many\nparallel tasks?"}
    PARALLEL_CHECK -->|"1-2"| SINGLE["Single orchestrator\nwith serial tool calls"]
    PARALLEL_CHECK -->|"3-20"| PARALLEL["Spawn parallel workers\nwith asyncio.gather()"]
    PARALLEL_CHECK -->|"20+"| HIER_BATCH["Hierarchical:\nsub-orchestrators\n+ batched workers"]
    SINGLE & PARALLEL & HIER_BATCH --> AGGREGATE["Aggregate results"]
    SEQUENTIAL --> AGGREGATE
    AGGREGATE --> OUTPUT["Final response"]
```

---

## Context Isolation: What Each Layer Sees

```
User's request (500 tokens)
    ↓
Orchestrator context:
┌─────────────────────────────────────────────────────────────┐
│ System prompt (300 tokens)                                   │
│ User request (500 tokens)                                    │
│ Tool call: analyze_document(doc_1) (50 tokens)               │
│ Tool result: {summary: ..., keywords: ...} (200 tokens)      │  ← only the result, not
│ Tool call: analyze_document(doc_2) (50 tokens)               │    the worker's 10 internal steps
│ Tool result: {summary: ..., keywords: ...} (200 tokens)      │
│ Tool call: compile_report(all_results) (300 tokens)          │
│ Tool result: "# Report..." (400 tokens)                      │
│ Final answer (300 tokens)                                    │
└─────────────────────────────────────────────────────────────┘
Total orchestrator context: ~2,300 tokens

Worker 1 context (isolated, discarded after task):
┌─────────────────────────────────────────────────────────────┐
│ Worker system prompt (200 tokens)                            │
│ Task: "Summarize this document..." (600 tokens)              │
│ Tool call: summarize_text(...) (50 tokens)                   │
│ Tool result: ... (300 tokens)                                │
│ Tool call: extract_keywords(...) (50 tokens)                 │
│ Tool result: ... (100 tokens)                                │
│ Final answer (200 tokens)                                    │
└─────────────────────────────────────────────────────────────┘
Worker context: ~1,500 tokens (never seen by orchestrator)
```

The orchestrator's context stays lean even for complex, multi-worker tasks.

---

## Worker Specialization — System Prompt Design

The power of multi-agent is specialization. Each worker gets a focused system prompt:

```python
WORKER_CONFIGS = {
    "security_reviewer": {
        "model": "claude-sonnet-4-6",
        "system": """You are a security code reviewer. Your ONLY focus is security.

        Look for:
        - SQL injection vulnerabilities
        - XSS / CSRF risks  
        - Authentication bypasses
        - Insecure deserialization
        - Hardcoded secrets or credentials
        - Path traversal vulnerabilities

        Return findings as JSON: [{"type": "...", "severity": "critical|high|medium|low", 
        "line": N, "description": "..."}]
        
        If no issues found, return: []""",
        "tools": ["read_file", "search_patterns"]
    },
    
    "style_reviewer": {
        "model": "claude-haiku-4-5",  # cheaper model for simpler task
        "system": """You are a code style reviewer. Your ONLY focus is code quality.

        Check for:
        - PEP 8 compliance (Python)
        - Missing docstrings
        - Complex functions (>20 lines)
        - Magic numbers
        - Variable naming conventions

        Return findings as JSON: [{"type": "...", "severity": "info|warning", 
        "line": N, "description": "..."}]""",
        "tools": ["read_file"]
    },
    
    "correctness_reviewer": {
        "model": "claude-sonnet-4-6",
        "system": """You are a code correctness reviewer. Focus on bugs and logic errors.

        Check for:
        - Off-by-one errors
        - Null pointer risks
        - Resource leaks
        - Incorrect algorithm implementation
        - Edge cases not handled

        Return findings as JSON.""",
        "tools": ["read_file", "run_tests"]
    }
}
```

---

## Failure Handling in Orchestration

```mermaid
flowchart TD
    ORCH["Orchestrator spawns 5 workers"]
    ORCH --> W1["Worker 1 ✅"]
    ORCH --> W2["Worker 2 ✅"]
    ORCH --> W3["Worker 3 ❌ (timeout)"]
    ORCH --> W4["Worker 4 ✅"]
    ORCH --> W5["Worker 5 ❌ (bad output)"]
    
    W1 & W2 & W3 & W4 & W5 --> COLLECT["Orchestrator collects results"]
    COLLECT --> CHECK{"All\nsucceeded?"}
    CHECK -->|"Yes"| AGGREGATE["Aggregate all results"]
    CHECK -->|"No"| PARTIAL{"Partial result\nacceptable?"}
    PARTIAL -->|"Yes"| NOTE["Flag gaps in output\n(e.g., 'Document 3 failed')"]
    PARTIAL -->|"No"| RETRY["Retry failed workers"]
    RETRY -->|"Max retries exceeded"| ESCALATE["Escalate to human\nor return error"]
    NOTE & AGGREGATE & ESCALATE --> OUTPUT["Final output"]
```

---

## Concurrency Architecture

```mermaid
sequenceDiagram
    participant O as Orchestrator
    participant Q as asyncio.Semaphore(3)
    participant W1 as Worker 1
    participant W2 as Worker 2
    participant W3 as Worker 3
    participant W4 as Worker 4 (waiting)
    participant W5 as Worker 5 (waiting)

    O->>Q: acquire (5 tasks, limit=3)
    Q-->>W1: slot available → start
    Q-->>W2: slot available → start
    Q-->>W3: slot available → start
    Note over W4,W5: Waiting for a slot
    W1-->>O: result (slot released)
    Q-->>W4: slot available → start
    W2-->>O: result (slot released)
    Q-->>W5: slot available → start
    W3-->>O: result
    W4-->>O: result
    W5-->>O: result
    Note over O: All 5 results collected
    O->>O: Aggregate and return
```

---

## When Each Pattern Applies

| Topology | Use When | Example |
|---|---|---|
| **Fan-Out/Fan-In** | N independent items, same analysis | Analyze 20 documents in parallel |
| **Hierarchical** | 2-axis decomposition (N items × M analyses) | 10 companies × 5 metrics = 50 workers in 5 groups |
| **Sequential Pipeline** | Dependent stages, data flows forward | Extract → Validate → Enrich → Store |
| **Debate** | Need multiple perspectives on one problem | 3 agents argue for different approaches, 1 judge picks best |
| **Specialist Routing** | Input type determines which expert handles it | Route by topic (billing/technical/account) |

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Architecture_Deep_Dive.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Orchestrator + worker code |

⬅️ **Prev:** [Agent Memory](../06_Agent_Memory/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Subagents](../08_Subagents/Theory.md)
