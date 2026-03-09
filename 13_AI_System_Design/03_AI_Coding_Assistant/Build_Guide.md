# Build Guide
## Design Case 03: AI Coding Assistant

Four phases from a simple chat interface to a full IDE integration with codebase awareness, tool execution, and streaming. Each phase is useful on its own.

---

## Phase 1: Basic Chat Interface with File Context (Week 1-2)

**Goal:** A chat UI (web or CLI) where you can paste code, ask questions about it, and get answers.

**What you build:**
- Simple React frontend (or use the Vercel AI SDK Chat UI)
- Backend API: `POST /chat` accepts messages + optional code snippet
- LLM call with the code snippet injected into the system prompt

**Key implementation:**
```python
# Backend endpoint
@app.post("/chat")
async def chat(request: ChatRequest):
    messages = [
        {
            "role": "system",
            "content": f"""You are an expert coding assistant.

The user is working on this code:
```
{request.code_context}
```

Answer questions about this code, suggest improvements, find bugs, and write new code as requested.
When writing code, always explain what you changed and why."""
        }
    ]
    messages.extend(request.conversation_history)
    messages.append({"role": "user", "content": request.message})

    # Stream the response
    async with client.messages.stream(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2000,
        messages=messages
    ) as stream:
        async for text in stream.text_stream:
            yield text  # Server-Sent Events
```

**Streaming is mandatory from Phase 1.** Code generation responses are long (200-1000 tokens). A user waiting 5 seconds for a blank screen, then seeing code appear all at once, will not trust the tool. Streaming makes the same 5-second response feel responsive.

**Success criteria:** Can correctly answer questions about pasted code, suggest bug fixes, and generate new functions.

---

## Phase 2: Codebase Indexer (Week 3-4)

**Goal:** Index the entire codebase so you can ask "how does the authentication module work?" without pasting files.

**What you build:**
- CLI command: `ai-assistant index /path/to/project`
- Tree-sitter integration to parse code into functions/classes
- SQLite database to store chunks + embeddings
- Query endpoint: `POST /search` that searches the index

**Tree-sitter AST parsing:**
```python
import tree_sitter_python as tspython
from tree_sitter import Language, Parser

PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)

def extract_functions(source_code: str, file_path: str) -> list[CodeChunk]:
    tree = parser.parse(bytes(source_code, "utf8"))
    chunks = []

    def traverse(node):
        if node.type in ("function_definition", "class_definition"):
            start_line = node.start_point[0]
            end_line = node.end_point[0]
            chunk_text = source_code.split("\n")[start_line:end_line+1]
            chunks.append(CodeChunk(
                file_path=file_path,
                start_line=start_line,
                end_line=end_line,
                content="\n".join(chunk_text),
                chunk_type=node.type
            ))
        for child in node.children:
            traverse(child)

    traverse(tree.root_node)
    return chunks
```

**SQLite schema:**
```sql
CREATE TABLE code_chunks (
    id TEXT PRIMARY KEY,
    file_path TEXT NOT NULL,
    start_line INTEGER,
    end_line INTEGER,
    content TEXT NOT NULL,
    chunk_type TEXT,  -- function_definition, class_definition
    embedding BLOB,   -- serialized float32 array
    content_hash TEXT,  -- for incremental updates
    indexed_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_chunks_file_path ON code_chunks(file_path);
CREATE INDEX idx_chunks_content_hash ON code_chunks(content_hash);
```

**Vector search in SQLite (without a vector store):**
SQLite doesn't have native vector search. For a codebase with < 100K chunks (most projects), brute-force cosine similarity in Python is fast enough (< 100ms):
```python
import numpy as np

def search_index(query: str, top_k: int = 5) -> list[CodeChunk]:
    query_embedding = embed(query)
    all_chunks = load_all_chunks_from_sqlite()

    embeddings = np.array([chunk.embedding for chunk in all_chunks])
    similarities = np.dot(embeddings, query_embedding) / (
        np.linalg.norm(embeddings, axis=1) * np.linalg.norm(query_embedding)
    )
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    return [all_chunks[i] for i in top_indices]
```

For larger codebases, swap in a proper vector search library (FAISS, Chroma, or sqlite-vss extension).

**Success criteria:** `ai-assistant ask "how does user authentication work?"` returns the relevant authentication code without you pasting it manually.

---

## Phase 3: IDE Extension with Real-Time Indexing (Week 5-7)

**Goal:** Full IDE integration. The assistant knows what file you're editing, where your cursor is, and has the codebase indexed and kept up to date.

**VS Code Extension architecture:**
```
extension/
├── src/
│   ├── extension.ts          # Entry point, registers commands and events
│   ├── indexer.ts            # File watcher + re-indexing logic
│   ├── contextAssembler.ts   # Build context from editor state + index
│   ├── streamingPanel.ts     # Webview panel that renders streaming response
│   └── backendClient.ts      # HTTP client to your backend API
└── package.json              # VS Code extension manifest
```

**Key VS Code APIs you'll use:**
```typescript
// Capture current editor state
const editor = vscode.window.activeTextEditor;
const document = editor.document;
const cursorLine = editor.selection.active.line;
const fullContent = document.getText();
const languageId = document.languageId;  // "python", "typescript", etc.

// Watch for file changes
const watcher = vscode.workspace.createFileSystemWatcher("**/*.{py,ts,js,go}");
watcher.onDidChange(uri => reindexFile(uri.fsPath));
watcher.onDidCreate(uri => indexNewFile(uri.fsPath));
watcher.onDidDelete(uri => deleteFromIndex(uri.fsPath));
```

**Context assembly (TypeScript):**
```typescript
async function assembleContext(query: string): Promise<string> {
    const editor = vscode.window.activeTextEditor!;
    const fullFile = editor.document.getText();
    const cursorLine = editor.selection.active.line;

    // ±50 lines around cursor
    const startLine = Math.max(0, cursorLine - 50);
    const endLine = Math.min(editor.document.lineCount, cursorLine + 50);
    const cursorContext = fullFile.split("\n").slice(startLine, endLine).join("\n");

    // Semantic search for related code
    const relatedChunks = await searchIndex(query, topK=3);

    return `
Current file: ${editor.document.fileName}
Language: ${editor.document.languageId}

Code around cursor (line ${cursorLine}):
\`\`\`${editor.document.languageId}
${cursorContext}
\`\`\`

Related code from your codebase:
${relatedChunks.map(c => `// ${c.file_path}:${c.start_line}\n${c.content}`).join("\n\n")}
    `;
}
```

**Streaming response in VS Code:**
VS Code extensions can open a WebView panel (a mini-browser inside the IDE). Render the streaming response there using SSE, with Markdown code block highlighting.

**Success criteria:** Open any file, press the keyboard shortcut, type a question, and get a context-aware answer that references code from other files in your project.

---

## Phase 4: Tool Execution (Week 8-10)

**Goal:** The assistant can run tests, read files it hasn't indexed, and search external documentation.

**Tools to implement:**

**run_tests tool:**
```python
import subprocess, tempfile, os

async def run_tests(file_path: str, test_command: str) -> dict:
    # Run in a Docker container for safety
    result = subprocess.run(
        ["docker", "run", "--rm", "-v", f"{project_root}:/code", "python:3.11",
         "bash", "-c", f"cd /code && {test_command}"],
        capture_output=True, text=True, timeout=30
    )
    return {
        "stdout": result.stdout[-3000:],  # Truncate long outputs
        "stderr": result.stderr[-1000:],
        "exit_code": result.returncode,
        "passed": result.returncode == 0
    }
```

**read_file tool:**
```python
async def read_file(file_path: str) -> str:
    abs_path = os.path.join(project_root, file_path)
    # Safety: ensure path is within project root
    if not abs_path.startswith(project_root):
        raise ValueError("Cannot read files outside project directory")
    with open(abs_path, 'r') as f:
        content = f.read()
    return content[:10_000]  # 10K char limit
```

**search_docs tool:**
```python
async def search_documentation(query: str) -> str:
    # Search indexed project docs (README, docs/, CONTRIBUTING.md)
    results = search_index(query, collection="docs", top_k=3)
    return "\n\n".join([f"// {r.file_path}\n{r.content}" for r in results])
```

**Safety considerations for code execution:**
- Never run test commands without Docker isolation — a malicious repository could have code that deletes files
- Timeout all executions (30 seconds max)
- No network access inside the container (unless tests require it)
- Read-only mount of the project directory for safety

**Success criteria:** "Write a function to parse ISO dates, then run the existing date parsing tests to verify nothing broke." The assistant writes the function and automatically runs the test suite.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Architecture_Blueprint.md](./Architecture_Blueprint.md) | System architecture blueprint |
| 📄 **Build_Guide.md** | ← you are here |
| [📄 Component_Breakdown.md](./Component_Breakdown.md) | Component breakdown |
| [📄 Data_Flow_Diagram.md](./Data_Flow_Diagram.md) | Data flow diagram |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Tech_Stack.md](./Tech_Stack.md) | Technology stack choices |

⬅️ **Prev:** [02 RAG Document Search System](../02_RAG_Document_Search_System/Architecture_Blueprint.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 AI Research Assistant](../04_AI_Research_Assistant/Architecture_Blueprint.md)
