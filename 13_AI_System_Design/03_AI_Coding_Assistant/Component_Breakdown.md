# Component Breakdown
## Design Case 03: AI Coding Assistant

The hardest parts of building a coding assistant are not the LLM call — they are the context assembly, the codebase indexer's handling of code change velocity, and the latency requirements for in-IDE use.

---

## 1. AST-Aware Codebase Indexer

**The fundamental problem with text chunking for code:**

Standard NLP chunking (`RecursiveCharacterTextSplitter`) splits at 512 tokens regardless of code structure. Consider this Python module:

```python
# functions.py

def validate_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@"
    # ... 30 lines ...

class UserService:
    def __init__(self, db):
        self.db = db

    def create_user(self, email, name):
        # ... 20 lines ...
```

A token-based splitter at 512 tokens might cut right through `create_user`, producing a chunk that starts in the middle of a method. That chunk has no standalone meaning.

**Tree-sitter solves this by parsing the actual code structure.** It produces an AST (Abstract Syntax Tree) where each function and class is a discrete node with exact start/end positions.

**Tree-sitter chunking strategy by chunk type:**

| AST Node Type | Chunking Rule | Example |
|---|---|---|
| `function_definition` | One chunk per function | `def validate_email(...)` → 1 chunk |
| `class_definition` (small < 100 lines) | Whole class as one chunk | `class Config:` → 1 chunk |
| `class_definition` (large > 100 lines) | Class header + each method separately | `class UserService:` + `def create_user:` |
| `module` (top-level code) | Non-function code as one chunk | Import statements, module docstring |
| `arrow_function` / `function_expression` (JS) | Each named function | Handles JS functional patterns |

**Supported languages via Tree-sitter grammar packages:**
Python, JavaScript, TypeScript, Go, Rust, Java, C, C++, Ruby, PHP, Swift, Kotlin, Scala — all with the same parsing interface.

**Incremental indexing (how changes stay fast):**
```
File save detected
→ Hash new content (md5)
→ Compare with stored hash
→ Same hash: skip (no change)
→ Different hash:
    1. Parse AST with Tree-sitter (10-50ms)
    2. Delete old chunks for this file (SQLite DELETE WHERE file_path = ?)
    3. Extract new chunks from AST
    4. Embed new chunks (batch API call, 20-100ms)
    5. Insert new chunks into SQLite
    6. Update file hash
```

Total incremental update time: ~200ms for a typical file. Debounced to trigger 500ms after last keystroke, so this completes before the user's next query.

---

## 2. Context Assembler

The context assembler builds the final prompt that goes to the LLM. It makes the critical decisions about what to include within the token budget.

**Context sources (in priority order):**

**1. System prompt (always first, ~1,500 tokens):**
Defines the assistant's behavior, lists available tools, and sets constraints:
```
You are an expert software engineer. You help developers understand, debug, and improve their code.

When writing code:
- Match the existing code style in the project
- Write docstrings/comments in the same style as the surrounding code
- Consider edge cases and error handling
- Prefer explicit over implicit

Available tools: run_tests, read_file, search_docs
```

**2. Current file content (always included, up to 3,000 tokens):**
The full content of the file the developer has open. If the file is very large (>3,000 tokens), include: the full function containing the cursor + 50 lines before/after + file-level imports.

**3. Cursor context (always included, ~1,000 tokens):**
The 50 lines before and after the cursor position. This is the most relevant local context — what the developer is actively working on.

**4. Related code from RAG (top 3, ~2,500 tokens):**
Semantic search against the codebase index. The query is a combination of the user's message + the function name at the cursor. The top 3 most relevant chunks from other files.

This is how the assistant can answer "how does the PaymentService use this UserService?" — it retrieves the PaymentService implementation without the developer having to open that file.

**5. Directly imported modules (if small, ~1,000 tokens):**
If the current file imports `from utils import format_currency`, include the `format_currency` function definition. This is extracted from the AST's import graph.

**6. Conversation history (last 5 exchanges, ~1,500 tokens):**
Multi-turn support. The developer asked "what does this function do?" and now asks "can you refactor it?" — the assistant needs to know what "it" refers to.

**Token budget enforcement:**
The assembler calculates the token count of each component before including it. If the total would exceed the budget (10,000 tokens by default), it drops components in reverse priority order, starting with the oldest conversation turns.

---

## 3. Streaming Response Handler

Streaming is not optional for a coding assistant. Code generation takes 2-8 seconds. Without streaming, the developer sees a loading spinner and wonders if the tool crashed.

**How streaming works with Claude:**
```python
async with client.messages.stream(
    model="claude-3-5-sonnet-20241022",
    max_tokens=2000,
    messages=assembled_context
) as stream:
    async for text_chunk in stream.text_stream:
        yield text_chunk  # Sent as SSE event to the IDE extension
```

**In the IDE extension (VS Code):**
The extension opens a WebView panel (an embedded browser). The streaming response is rendered in real-time using Server-Sent Events. Code blocks are syntax-highlighted with a language-aware highlighter as they stream.

**The "write to cursor" feature:**
When the user asks the assistant to write code, the extension can directly insert the streaming response at the cursor position using `editor.edit()`. The developer watches the code appear token-by-token in their editor — this is the signature UX of tools like GitHub Copilot Chat.

---

## 4. Tool Orchestrator

The tool orchestrator handles the multi-turn loop between the LLM's tool requests and execution results.

**The execution loop:**
```python
async def run_with_tools(messages: list, tools: list) -> str:
    while True:
        response = await client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            tools=tools,
            messages=messages
        )

        if response.stop_reason == "tool_use":
            tool_use_block = next(b for b in response.content if b.type == "tool_use")
            tool_name = tool_use_block.name
            tool_input = tool_use_block.input

            # Execute the tool
            result = await execute_tool(tool_name, tool_input)

            # Add results to conversation
            messages.append({"role": "assistant", "content": response.content})
            messages.append({
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": tool_use_block.id,
                    "content": str(result)
                }]
            })
        else:
            # stop_reason == "end_turn" — final response
            return response.content[0].text
```

**Parallel tool execution:**
When the LLM requests multiple independent tools in the same turn (Claude can emit multiple `tool_use` blocks), execute them in parallel:
```python
if response.stop_reason == "tool_use":
    tool_calls = [b for b in response.content if b.type == "tool_use"]
    if len(tool_calls) > 1:
        results = await asyncio.gather(*[execute_tool(t.name, t.input) for t in tool_calls])
    else:
        results = [await execute_tool(tool_calls[0].name, tool_calls[0].input)]
```

**Tool execution safety:**
- `run_tests`: Always in Docker, always with timeout, always read-only bind mount
- `read_file`: Validate path is within project root (prevent `../../etc/passwd`)
- `web_search`: Rate limited (max 3 searches per conversation turn)
- `write_file`: **Never allow this tool** — writing to files should require developer confirmation

---

## 5. Local SQLite Index

**Why local (not server-side)?**

The codebase index stores the full content of your code. Sending all your code to a remote server for indexing:
- Creates privacy/IP concerns (most enterprises prohibit this)
- Adds latency (network roundtrip for every index query)
- Adds dependency (server must be up for basic code search)

SQLite stored on the developer's machine (`~/.ai-assistant/index_{project_hash}.db`) solves all three. The index is private, local, and available offline.

**Vector search in SQLite:**

SQLite doesn't natively support vector search. Options:
- **Brute force cosine similarity (< 50K chunks):** Load all embeddings into numpy arrays, compute similarity matrix. ~50ms for 50K vectors on modern hardware.
- **sqlite-vss extension:** Adds HNSW vector search to SQLite. Works for up to ~1M vectors.
- **FAISS in-process:** Meta's FAISS library for fast approximate nearest neighbor search, loaded alongside SQLite.

For most codebases (< 100K lines of code), brute-force numpy is fast enough. A codebase with 100K LOC has roughly 3,000-5,000 functions, which is 5,000 vectors. Brute-force cosine similarity on 5,000 vectors takes < 5ms.

**When to use a remote vector store:** For monorepos with millions of lines of code (Google/Meta-scale), or for multi-developer shared indexes, a remote vector store (Pinecone, Qdrant) becomes necessary. But for the typical developer's codebase, local SQLite is the right call.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Architecture_Blueprint.md](./Architecture_Blueprint.md) | System architecture blueprint |
| [📄 Build_Guide.md](./Build_Guide.md) | Step-by-step build guide |
| 📄 **Component_Breakdown.md** | ← you are here |
| [📄 Data_Flow_Diagram.md](./Data_Flow_Diagram.md) | Data flow diagram |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Tech_Stack.md](./Tech_Stack.md) | Technology stack choices |

⬅️ **Prev:** [02 RAG Document Search System](../02_RAG_Document_Search_System/Architecture_Blueprint.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 AI Research Assistant](../04_AI_Research_Assistant/Architecture_Blueprint.md)
