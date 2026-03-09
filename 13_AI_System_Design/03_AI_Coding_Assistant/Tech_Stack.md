# Tech Stack
## Design Case 03: AI Coding Assistant

Technology choices for the IDE extension, the codebase indexer, and the backend service.

---

## Full Stack Table

| Component | Technology Choice | Why This Choice | Alternatives | When to Switch |
|---|---|---|---|---|
| **IDE Extension** | VS Code Extension API (TypeScript) | VS Code is the most popular IDE (71% market share), excellent extension API, TypeScript gives type safety, large ecosystem. | JetBrains Platform (Kotlin/Java), Neovim Lua | Build JetBrains extension for enterprises using IntelliJ/Rider. Build Neovim plugin for power users. VS Code should be first. |
| **AST Parser** | Tree-sitter | Universal: supports 40+ languages with the same API. Fast (C library with language bindings). Produces parse trees, not just tokens. Used by Neovim, GitHub, and Sourcegraph. | Language-specific parsers (javalang, ast.py), ANTLR | Use Python's built-in `ast` module if you only support Python (no dependency). Use ANTLR if you need custom grammar parsing. |
| **Local Vector Store** | SQLite + numpy (< 100K chunks) | Zero additional dependencies, stored locally on disk, queries ~5-50ms at typical codebase sizes. | FAISS (>100K chunks), Chroma, sqlite-vss extension | Switch to FAISS for large codebases (> 100K functions). Switch to Qdrant self-hosted for team shared indexes. |
| **Embedding Model** | text-embedding-3-small (OpenAI) | Best general-purpose code embedding. Note: code-specific models (CodeBERT, UniXcoder) exist but have lower MTEB scores. | CodeBERT, StarEncoder, Cohere embed-v3 | For full offline/privacy, use `microsoft/codebert-base` self-hosted. For best code retrieval quality, experiment with `Salesforce/SFR-Embedding-Code-400M_R`. |
| **LLM (chat/Q&A)** | Claude 3.5 Sonnet | Best code understanding + generation quality, 200K context handles large files, strong instruction following. | GPT-4o, Codestral (Mistral), DeepSeek Coder V2 | GPT-4o is comparable quality. Codestral for faster/cheaper code-specific tasks. DeepSeek Coder V2 for self-hosted enterprise deployment. |
| **LLM (autocomplete)** | Claude 3.5 Haiku or GPT-4o-mini | 10x faster and cheaper than Sonnet/GPT-4o. Sub-200ms time to first token. Sufficient quality for 1-3 line completions. | Codestral (fill-in-middle native), Starcoder2 | Codestral for fill-in-middle format (native FIM support, optimized for inline suggestions). Starcoder2 for self-hosted. |
| **Backend API** | FastAPI (Python) | Async streaming support, Python ecosystem for LLM libraries, auto-generated OpenAPI docs. | Node.js (Express + OpenAI streaming), Go | Node.js for TypeScript consistency with the extension. Go for high-throughput backend at scale. |
| **Code Execution Sandbox** | Docker (rootless) | Industry-standard isolation. Rootless mode reduces attack surface. Resource limits (CPU, memory, network). Supports any language runtime. | Firecracker (AWS Lambda), nsjail, gVisor | Firecracker for sub-100ms container startup (critical for interactive use). gVisor for stronger isolation. |
| **File Watcher** | chokidar (Node.js) in extension | Cross-platform (macOS FSEvents, Linux inotify, Windows ReadDirectoryChanges), battle-tested, handles symlinks and large directory trees. | Watchman (Facebook), native OS API | Watchman for very large repos (> 100K files) — more efficient than chokidar at scale. |
| **Session Management** | In-memory (extension) + optional Redis | Conversation history stored in-process in the extension for simplicity. Optional Redis sync for cross-device continuity. | PostgreSQL, SQLite | Add PostgreSQL only if you need persistent conversation history across IDE restarts and devices. |
| **Authentication** | API Key (developer) + JWT (enterprise SSO) | API key is simplest for individual developers. JWT + Okta/Auth0 for enterprise with group-based access controls. | OAuth2, mTLS | mTLS for enterprise with strict security requirements and no public internet exposure. |
| **Streaming Protocol** | Server-Sent Events (SSE) | Simple, HTTP-based, native browser support, works through firewalls. One-directional (server → client), which is all we need. | WebSockets, gRPC streaming | WebSockets if you need bidirectional streaming (e.g., live collaboration). gRPC for internal service-to-service streaming. |

---

## Privacy-First Architecture Variant

For enterprises where code cannot leave the corporate network:

```
IDE Extension (same)
    ↓
Local Context Assembler (no network)
    ↓
Local Embedding Model (CodeBERT or SFR-Embedding-Code, runs on CPU)
    ↓
Local SQLite Index (on developer's machine)
    ↓
Corporate VPN
    ↓
Self-Hosted LLM API (DeepSeek Coder V2 33B or Code Llama 70B on internal GPU cluster)
    ↓
Response streams back via VPN
```

**What leaves the corporate network:** Nothing. The LLM inference runs on corporate GPU infrastructure. The index is local. The only external dependency is the developer's IDE, which is already there.

**Cost estimate for a 100-developer enterprise:**
- 2x NVIDIA A100 80GB instances (handles 20 concurrent requests at 2s each): ~$7/hr = $5,000/month
- DeepSeek Coder V2 33B: fits on one A100, good quality
- Total: $5,000/month for unlimited usage by 100 developers vs $2,000-10,000/month for external API costs with data risk

---

## LLM Model Comparison for Code Tasks

| Model | Code Quality | Context | Latency | Cost (output) | Best For |
|---|---|---|---|---|---|
| Claude 3.5 Sonnet | Excellent | 200K | 1.5s first token | $15/1M | Complex refactoring, architecture questions |
| Claude 3.5 Haiku | Good | 200K | 0.3s first token | $1.25/1M | Autocomplete, simple completions |
| GPT-4o | Excellent | 128K | 1.5s first token | $10/1M | Complex coding tasks |
| GPT-4o-mini | Good | 128K | 0.2s first token | $0.60/1M | Autocomplete |
| Codestral (Mistral) | Very Good | 32K | 0.5s first token | API varies | Fill-in-middle, code-specific tasks |
| DeepSeek Coder V2 | Excellent | 128K | Self-hosted | $0 (self-hosted) | Enterprise self-hosted |
| Code Llama 70B | Good | 100K | Self-hosted | $0 (self-hosted) | Open-source self-hosted option |

**Rule:** For the chat interface (interactive Q&A), use the best model you can afford (Sonnet / GPT-4o). For autocomplete, use the fastest model available (Haiku / GPT-4o-mini / Codestral). The quality difference for 3-token completions is negligible.

---

## Build vs Buy Decision

| Capability | Build | Buy |
|---|---|---|
| IDE Extension | Build (unavoidable, must be tailored to your UX) | N/A |
| AST Parsing | Use Tree-sitter (open source library, not truly "building") | N/A |
| Local vector search | Build (30 lines of numpy code is sufficient) | Chroma (if you want a library) |
| LLM Inference | Buy (use Anthropic/OpenAI API) | Self-host only for privacy requirements |
| Reranking (if added) | Use Cohere API | Self-host BGE-Reranker (for data privacy) |
| Code sandbox | Build (Docker wrapper, 50 lines) | Buy (Fly.io Machines API for managed sandboxes) |
| Auth | Buy (Auth0 / Okta) | Build only if you have specific requirements |

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Architecture_Blueprint.md](./Architecture_Blueprint.md) | System architecture blueprint |
| [📄 Build_Guide.md](./Build_Guide.md) | Step-by-step build guide |
| [📄 Component_Breakdown.md](./Component_Breakdown.md) | Component breakdown |
| [📄 Data_Flow_Diagram.md](./Data_Flow_Diagram.md) | Data flow diagram |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Tech_Stack.md** | ← you are here |

⬅️ **Prev:** [02 RAG Document Search System](../02_RAG_Document_Search_System/Architecture_Blueprint.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 AI Research Assistant](../04_AI_Research_Assistant/Architecture_Blueprint.md)
