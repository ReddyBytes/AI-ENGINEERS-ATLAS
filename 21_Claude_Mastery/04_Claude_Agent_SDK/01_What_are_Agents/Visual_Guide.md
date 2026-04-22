# What Are Agents? — Visual Guide

## The Full Agent Loop, Step by Step

```mermaid
sequenceDiagram
    participant U as User / System
    participant A as Agent Loop
    participant LLM as Claude (LLM)
    participant T as Tool Executor

    U->>A: Goal: "Research top 3 papers on DDPM"
    A->>LLM: [system_prompt + goal + tool_definitions]
    
    Note over LLM: Thinks: I need to search for DDPM papers
    LLM-->>A: tool_call: web_search("DDPM 2020 Ho et al")
    A->>T: Execute: web_search(...)
    T-->>A: Returns: [list of search results]
    A->>LLM: [prev context + tool_result]
    
    Note over LLM: Got results. I need to read the top ones.
    LLM-->>A: tool_call: fetch_page("https://arxiv.org/...")
    A->>T: Execute: fetch_page(...)
    T-->>A: Returns: [paper abstract + citations]
    A->>LLM: [prev context + tool_result]
    
    Note over LLM: I have enough data to synthesize now.
    LLM-->>A: Final answer: "The top 3 DDPM papers are..."
    A->>U: Returns final response
```

---

## Anatomy of One Loop Iteration

```mermaid
flowchart LR
    subgraph ONE_STEP["Single Agent Step"]
        direction TB
        CTX["📋 Current Context\n(system + history + tools)"]
        LLM_BOX["🧠 Claude\nProcess context"]
        DECIDE{"Output\ntype?"}
        TOOL_CALL["🔧 Tool Call\n{ tool, params }"]
        ANSWER["✅ Final Answer\n(text response)"]
        EXEC["⚙️ Execute Tool"]
        RESULT["📊 Tool Result"]
        APPEND["➕ Append to\nContext"]
        
        CTX --> LLM_BOX
        LLM_BOX --> DECIDE
        DECIDE -->|"tool_call"| TOOL_CALL
        DECIDE -->|"answer"| ANSWER
        TOOL_CALL --> EXEC
        EXEC --> RESULT
        RESULT --> APPEND
        APPEND -->|"next iteration"| CTX
    end
```

---

## Context Growth Over a 4-Step Agent Loop

```
Step 0 — Initial context
┌─────────────────────────────────────────────────────────┐
│ System prompt (300 tokens)                               │
│ User goal (50 tokens)                                    │
│ Tool definitions (200 tokens)                            │
└─────────────────────────────────────────────────────────┘
Total: ~550 tokens

Step 1 — After first tool call
┌─────────────────────────────────────────────────────────┐
│ [Previous context: 550 tokens]                           │
│ Tool call: web_search(...) (30 tokens)                   │
│ Tool result: search results (800 tokens)                 │
└─────────────────────────────────────────────────────────┘
Total: ~1,380 tokens

Step 2 — After second tool call
┌─────────────────────────────────────────────────────────┐
│ [Previous context: 1,380 tokens]                         │
│ Tool call: fetch_page(...) (25 tokens)                   │
│ Tool result: paper text (2,000 tokens)                   │
└─────────────────────────────────────────────────────────┘
Total: ~3,405 tokens

Step 3 — After third tool call
┌─────────────────────────────────────────────────────────┐
│ [Previous context: 3,405 tokens]                         │
│ Tool call: fetch_page(...) (25 tokens)                   │
│ Tool result: paper text (2,000 tokens)                   │
└─────────────────────────────────────────────────────────┘
Total: ~5,430 tokens

Step 4 — Final answer generated
┌─────────────────────────────────────────────────────────┐
│ [Previous context: 5,430 tokens]                         │
│ Final response (300 tokens)                              │
└─────────────────────────────────────────────────────────┘
```

Key insight: context grows linearly with steps. Long agents need memory management strategies (see Topic 06).

---

## Agent vs Chain vs Single Call — Visual Comparison

```mermaid
flowchart TD
    subgraph SINGLE["Single Call"]
        direction LR
        Q1["Question"] --> LLM1["LLM"] --> A1["Answer"]
    end

    subgraph CHAIN["Fixed Chain (3 steps)"]
        direction LR
        G2["Goal"] --> S1["Step 1\nPrompt"]
        S1 --> S2["Step 2\nPrompt"]
        S2 --> S3["Step 3\nPrompt"]
        S3 --> R2["Result"]
        note2["Path is predetermined\nby the programmer"]
    end

    subgraph AGENT["Agent (adaptive)"]
        direction TB
        G3["Goal"] --> LOOP["Loop"]
        LOOP --> D3{"Model decides\nnext action"}
        D3 -->|"Tool A"| TA["Execute A\nObserve result"]
        D3 -->|"Tool B"| TB["Execute B\nObserve result"]
        D3 -->|"Done"| R3["Result"]
        TA --> LOOP
        TB --> LOOP
        note3["Path is decided\nby the model"]
    end
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Visual_Guide.md** | ← you are here |

⬅️ **Prev:** [Track 3: Model Reference](../../03_Claude_API_and_SDK/13_Model_Reference/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Why Agent SDK?](../02_Why_Agent_SDK/Theory.md)
