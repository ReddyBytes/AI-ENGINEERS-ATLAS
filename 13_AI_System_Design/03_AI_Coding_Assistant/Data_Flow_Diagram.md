# Data Flow Diagram
## Design Case 03: AI Coding Assistant

Three flows: the main query flow (developer asks a question), the background indexing flow (codebase stays current), and the tool execution flow (tests run, files read).

---

## Flow 1: Developer Sends a Query

From keystroke to streaming response — the complete path.

```mermaid
sequenceDiagram
    actor Dev as Developer
    participant Ext as VS Code Extension
    participant Assembler as Context Assembler
    participant SQLite as Local SQLite Index
    participant Backend as Backend API
    participant LLM as Claude 3.5 Sonnet
    participant Stream as Streaming Panel

    Dev->>Ext: Presses keyboard shortcut\nTypes: "How does this function handle errors?"

    Ext->>Ext: Capture editor state:\n- Active file content\n- Cursor line (line 42)\n- Language (Python)

    par Parallel Context Assembly
        Ext->>SQLite: Semantic search: embed query → cosine similarity
        SQLite-->>Ext: [auth_handler.py:85, middleware.py:23, exceptions.py:10]
    and
        Ext->>Ext: Extract cursor context (±50 lines around line 42)
        Ext->>Ext: Extract imports from current file AST
    end

    Ext->>Assembler: Build prompt with all context
    Assembler->>Assembler: Calculate token counts\nApply budget (10K tokens max)\nDrop oldest history if needed

    Assembler->>Backend: POST /chat\n{ messages: [...], stream: true }
    Backend->>LLM: POST /messages\n{ model, messages, tools, stream: true }

    LLM-->>Backend: Token stream begins...
    Backend-->>Ext: SSE: "This function uses..."
    Ext-->>Stream: Render token in panel
    LLM-->>Backend: SSE: "...a try/except block"
    Ext-->>Stream: Render token in panel
    Note over LLM,Stream: Continues until stop_reason = "end_turn"

    LLM-->>Backend: SSE: [DONE] (stream complete)
    Backend->>Backend: Save exchange to session history
    Backend-->>Ext: Stream closed
```

---

## Flow 2: Background Codebase Indexing

This flow runs silently in the background. The developer never sees it, but it's what makes the assistant context-aware.

```mermaid
sequenceDiagram
    actor Dev as Developer
    participant FS as File System
    participant Watcher as File Watcher (chokidar)
    participant Debounce as Debounce Timer (500ms)
    participant Parser as Tree-sitter AST Parser
    participant SQLite as Local SQLite
    participant Embedder as Embedding Service

    Dev->>FS: Saves file: src/auth/user_service.py

    FS->>Watcher: inotify: MODIFY event on user_service.py
    Watcher->>Debounce: Start 500ms timer (or reset if already running)

    Note over Debounce: Waits for 500ms of inactivity (absorbs rapid saves)

    Debounce->>Debounce: Timer expires
    Debounce->>SQLite: SELECT content_hash WHERE file_path = 'user_service.py'
    SQLite-->>Debounce: Stored hash: "abc123"
    Debounce->>Debounce: Compute new hash: "def456" (file changed)

    Debounce->>Parser: Parse AST of user_service.py
    Parser-->>Debounce: [FunctionDef:login (L5-L30), FunctionDef:logout (L32-L45), ClassDef:UserService (L1-L100)]

    Debounce->>SQLite: DELETE WHERE file_path = 'user_service.py'
    Note over SQLite: Remove all stale chunks for this file

    loop For each extracted chunk
        Debounce->>Embedder: POST /embeddings { input: chunk_content }
        Embedder-->>Debounce: [1536 floats]
        Debounce->>SQLite: INSERT chunk (file_path, lines, content, embedding, hash)
    end

    Note over Dev: Total time: ~200ms. Developer didn't notice.
```

---

## Flow 3: Tool Execution (Running Tests)

When the developer asks the assistant to write code and verify it passes tests.

```mermaid
sequenceDiagram
    actor Dev as Developer
    participant Ext as VS Code Extension
    participant Backend as Backend API
    participant LLM as Claude 3.5 Sonnet
    participant Docker as Docker Container
    participant Postgres as Test DB (in container)

    Dev->>Ext: "Write a function to validate email addresses, then run the validation tests"

    Ext->>Backend: POST /chat { message: "...", tools_enabled: true }
    Backend->>LLM: Messages + tool definitions (run_tests, read_file)

    LLM-->>Backend: { tool_use: "read_file", input: { path: "tests/test_validators.py" } }
    Backend->>Backend: Read file: tests/test_validators.py
    Backend-->>LLM: [tool_result: full test file content]

    LLM-->>Backend: { content: "Here is the implementation:\n```python\ndef validate_email(email: str) -> bool:\n    import re\n    pattern = r'...'\n    return bool(re.match(pattern, email))\n```" }
    Backend-->>Ext: Stream this code to developer
    Ext-->>Dev: Shows generated code in panel

    LLM-->>Backend: { tool_use: "run_tests", input: { command: "pytest tests/test_validators.py -v" } }
    Backend->>Docker: docker run --rm -v project:/code python:3.11 pytest tests/...
    Note over Docker: Isolated execution, 30s timeout, no network

    Docker->>Docker: Run test suite...
    Docker-->>Backend: { stdout: "...3 passed, 0 failed...", exit_code: 0 }

    Backend-->>LLM: [tool_result: test output]
    LLM-->>Backend: "All 3 tests pass. The implementation correctly handles standard emails, rejects malformed inputs, and handles edge cases."
    Backend-->>Ext: Stream final response
    Ext-->>Dev: "All 3 tests pass..."
```

---

## Autocomplete vs Chat: The Latency Difference

This assistant supports two interaction modes with very different latency requirements:

```mermaid
flowchart LR
    subgraph Chat["Chat Mode (P99 < 3s)"]
        A1["Developer asks question\n(explicit action)"] --> B1["Full context assembly\n~200ms"]
        B1 --> C1["LLM with full context\n~800ms to first token"]
        C1 --> D1["Streaming response\nvisible immediately"]
    end

    subgraph Autocomplete["Autocomplete Mode (P99 < 200ms)"]
        A2["Keystroke detected\n(implicit action)"] --> B2["Debounce 150ms"]
        B2 --> C2["Minimal context only\ncurrent function + 10 lines"]
        C2 --> D2["Fast LLM call\nHaiku / GPT-4o-mini"]
        D2 --> E2["3-5 token suggestion\nappears inline"]
    end
```

**Autocomplete mode design constraints:**
- Latency target: < 200ms total (150ms debounce + 30ms embedding + 20ms context + 100ms LLM first token)
- Use a faster, cheaper model (Claude 3.5 Haiku, GPT-4o-mini)
- Never use RAG retrieval in autocomplete — the vector search adds 30-50ms
- Cache common completions (exact cache on the last 200 tokens of context)
- Cancel the request if the developer types another character before the response arrives

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Architecture_Blueprint.md](./Architecture_Blueprint.md) | System architecture blueprint |
| [📄 Build_Guide.md](./Build_Guide.md) | Step-by-step build guide |
| [📄 Component_Breakdown.md](./Component_Breakdown.md) | Component breakdown |
| 📄 **Data_Flow_Diagram.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Tech_Stack.md](./Tech_Stack.md) | Technology stack choices |

⬅️ **Prev:** [02 RAG Document Search System](../02_RAG_Document_Search_System/Architecture_Blueprint.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 AI Research Assistant](../04_AI_Research_Assistant/Architecture_Blueprint.md)
