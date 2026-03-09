# Interview Q&A
## Design Case 03: AI Coding Assistant

Nine questions from beginner to advanced. These come up in interviews for IDE tooling teams, developer tools companies (GitHub Copilot, Cursor, JetBrains AI), and any team building internal developer productivity tools.

---

## Beginner Questions

### Q1: What is the biggest technical challenge in building a coding assistant compared to a standard chatbot?

**Answer:**

Three challenges that don't exist in standard chatbots:

**Codebase context:** A chatbot answers from a knowledge base. A coding assistant needs to understand the code you're currently writing — and how it relates to code across your entire project. You can't just ask "what is X?" You need context from the current file, the cursor position, imported modules, and semantically related functions from other files. This requires a live codebase indexer that stays up to date as you type.

**Latency requirements:** Users tolerate 2-3 seconds for a chatbot response. For autocomplete suggestions, the tolerance is 150-200ms total. This forces architectural tradeoffs that chatbots don't face: you can't do full RAG retrieval for autocomplete, you need a faster/cheaper model, and you need aggressive request cancellation.

**Code staleness:** Unlike a document knowledge base (updated periodically), code changes on every file save. Your index must update incrementally within milliseconds of each save. A stale index means suggestions that reference code that doesn't exist anymore — confusing and trust-destroying.

Compared to a chatbot, you're building a real-time reactive system, not a request-response system.

---

### Q2: Why use Tree-sitter instead of just splitting code files by line count?

**Answer:**

Line count splitting creates semantically meaningless chunks. If you split every 50 lines, you'll frequently cut in the middle of a function — leaving you with chunk A containing the function signature and first half of the body, and chunk B containing the second half and part of the next function.

A chunk that starts mid-function has no standalone meaning. When retrieved for context, it confuses the LLM rather than helping it.

Tree-sitter parses the code into an Abstract Syntax Tree and identifies semantic boundaries: where functions start and end, where classes begin and end, where module-level code lives. You can then create chunks that are always complete, syntactically valid code units.

The practical difference: a codebase with 500 functions produces 500 semantically complete chunks with Tree-sitter, each independently useful. Line-based splitting at 50 lines produces hundreds of fragments that make no sense in isolation.

Tree-sitter also supports 40+ languages with the same parsing interface, making it the standard choice for any polyglot codebase.

---

### Q3: Should the codebase index be stored locally on the developer's machine or on a server?

**Answer:**

For most use cases: locally.

**The case for local:**
- **Privacy:** Your source code contains your business logic, proprietary algorithms, and possibly security-sensitive code. Sending all of it to an external server for indexing is a major enterprise security concern. Most companies have policies prohibiting this.
- **Latency:** Local SQLite queries are sub-millisecond. A network round trip to a remote vector store adds 20-50ms.
- **Offline functionality:** Local index works without an internet connection (except for the LLM inference call).
- **Cost:** No server infrastructure to maintain for indexing.

**The case for server-side:**
- **Multi-developer teams sharing context:** "What has Alice changed in the payment module?" only works if Alice's changes are in a shared index.
- **Very large monorepos:** A repo with 10M+ lines of code produces embeddings that exceed practical local storage/memory.
- **Cross-repository search:** Finding patterns across 50 internal repositories requires a centralized index.

**Architecture recommendation:**
Start with local. If you need shared team context, add an optional server-side sync layer that sends anonymized embeddings (not raw code) to a shared Pinecone index. The raw code stays local.

---

## Intermediate Questions

### Q4: How do you handle a monorepo with 10 million lines of code?

**Answer:**

At 10M LOC, brute-force cosine similarity in SQLite breaks down. 10M lines / 30 lines per function ≈ 300K function chunks. Loading 300K embeddings into memory for numpy dot product = 300K × 1536 dims × 4 bytes = 1.8GB RAM. Retrieval is still fast (~100ms) but memory usage is excessive.

**Strategies:**

**1. Scope the index:** You don't need to index all 10M lines equally. Index the current project module at full granularity. Index other modules at a coarser granularity (class-level, not method-level). Index rarely-changed infrastructure code at file-level only. This reduces the index to ~50K "important" chunks.

**2. Approximate nearest neighbor:** Replace brute-force numpy with FAISS (Facebook AI Similarity Search). FAISS with an IVF (Inverted File Index) structure handles 1M+ vectors in sub-50ms while using quantization to reduce memory. Install: `pip install faiss-cpu`. Drop-in replacement for the numpy similarity search.

**3. Two-tier index:** Hot index (last 30 days of files touched by this developer, ~5K chunks, local SQLite) + cold index (full codebase, Qdrant self-hosted, team-shared). Most queries hit the hot index and find what they need. Cold index is only queried if the hot index returns low-confidence results.

**4. Partitioned indexing:** Partition the codebase by service or module. A developer working on the `payments` service queries only the `payments` index + `shared/utils`. This is a practical scope reduction that mirrors how developers actually think about their work.

---

### Q5: How do you ensure the coding assistant doesn't suggest code that has security vulnerabilities?

**Answer:**

The LLM is trained on the internet, including Stack Overflow answers and GitHub repositories that contain vulnerabilities. Without guardrails, it will sometimes suggest code with SQL injection, insecure deserialization, or missing input validation.

**Defense layers:**

**Static analysis on LLM output:** Before showing the suggestion to the developer, run a fast AST-based security scanner on the generated code. For Python: `bandit` (sub-100ms). For JavaScript: `eslint` with security plugin. Flag: hardcoded secrets, SQL string concatenation, `eval()`, unvalidated user input passed to shell commands.

**Security-aware prompting:** Include security constraints in the system prompt: "When writing code, always use parameterized queries for SQL, validate all user inputs before using them, avoid using `eval()` or `exec()`, and use established cryptography libraries rather than rolling your own."

**Project-specific patterns:** Index your project's existing security utilities and patterns. If the codebase has a `safe_query()` wrapper for database access, make sure it appears in the context so the LLM knows to use it instead of raw SQL.

**Post-generation review requirements:** Make it easy for developers to review suggestions before applying them. The suggestion appears in a panel, not directly inserted. The developer must explicitly apply it. Add a "flag this suggestion" button for security team review.

**No tool can fully prevent insecure code suggestions.** The human developer must remain the security reviewer. These layers reduce the frequency and severity of insecure suggestions, but they don't eliminate the need for code review.

---

### Q6: How do you handle the context window when a developer is working on a file with 3,000 lines?

**Answer:**

A 3,000-line file at ~50 tokens per line = 150,000 tokens. Even Claude's 200K context window can't take the full file plus all the other context you need.

**You never need the full file.** The relevant context for any coding task is the function the developer is in, the functions it calls, and related functions. The context around the cursor is overwhelmingly what matters.

**Strategy: cursor-centric windowing**

```
Always include:
1. The complete function containing the cursor (usually 10-80 lines)
2. ±50 lines of surrounding context (the functions before/after)
3. The file's import statements (10-20 lines)
4. Class definition if inside a class (class header + any class-level attributes)

Conditionally include:
5. Called functions defined in the same file (look up call graph from AST)
6. Related functions from RAG (semantic search results)
```

This gives you 300-500 lines of highly relevant context instead of 3,000 lines of mixed-relevance content.

**For large files, build a file outline:**
```
# File: models/user.py (2,847 lines)
# Structure:
# Line 1-20: Imports
# Line 22-45: class User (inherits BaseModel)
# Line 47-120: class UserRepository
#   - get_by_id (47-67)
#   - create (69-95)
#   - update (97-120)
# Line 122-200: class UserValidator
# ...
```

Include this outline in the context (it's compact, ~20 lines) so the LLM understands the full file structure without seeing all 2,847 lines.

---

## Advanced Questions

### Q7: How would you build the autocomplete feature (inline suggestions as you type) with sub-200ms latency?

**Answer:**

Sub-200ms for a full LLM call with context assembly is aggressive. Here's how to make it work:

**Debounce aggressively:** Don't send a request on every keystroke. Wait for 150ms of inactivity. This means the developer has paused (end of a statement, thinking). Total budget after debounce: 50ms.

**Minimal context only (no RAG):**
- Forget about semantic search over the codebase — that takes 30-50ms
- Context: last 30 lines before cursor + file imports (~500 tokens)
- This context assembly takes < 5ms

**Dedicated fast model:**
- Claude 3.5 Haiku: time to first token ~200ms for short prompts
- GPT-4o-mini: time to first token ~150ms
- Codestral (Mistral): specifically designed for code completion, ~100ms
- For inline autocomplete, 1-3 line suggestions are enough — max_tokens=50
- Time to generate 50 tokens: ~100ms on fast models

**Fill-in-the-middle (FIM) prompting:**
Code completion models support a special prompt format where you provide the code before AND after the cursor, and the model fills in the gap:
```
<PRE> def calculate_tax(amount: float, rate: float) -> float:
    """Calculate tax amount."""
    <SUF>
    return total <MID>
```
This produces better suggestions than "complete from cursor" because the model knows what the code is heading toward.

**Aggressive request cancellation:**
If the developer types another character before the autocomplete response arrives, cancel the in-flight request (HTTP abort). Don't show a stale suggestion. This reduces "wasted" LLM calls and prevents confusing suggestions.

**Completion caching:**
Cache (last 200 tokens → completion) with a 60-second TTL. If the developer writes the same code pattern twice, the second suggestion is instant.

---

### Q8: How do you handle proprietary code that the company doesn't want sent to external LLM APIs?

**Answer:**

This is a real concern for enterprises. Financial models, medical algorithms, defense code — companies want AI assistance without sending their IP to OpenAI or Anthropic.

**Option 1: Self-hosted open-source LLM**

Deploy Code Llama 34B, Codestral, or DeepSeek Coder on your own infrastructure (AWS EC2 with A100 GPUs, or Nebius AI cloud for GPU instances).

- **Quality:** Codestral and DeepSeek Coder 33B are competitive with GPT-4o for code tasks (though behind Claude 3.5 Sonnet for complex reasoning)
- **Cost:** A100 instance on AWS = ~$3.50/hr. For a team of 20 developers at 100 requests/day each = 2,000 requests/day. At 2 seconds/request, peak concurrency ~2 requests at any time → one A100 instance handles this easily.
- **Latency:** Self-hosted LLMs can be faster than API calls (no network round trip) or slower (depends on GPU utilization and model size)

**Option 2: Private deployments of commercial models**

Both Anthropic and OpenAI offer enterprise contracts with data processing agreements that include "no training on your data" clauses. The data transits their servers, but they contractually cannot use it to train models.

For most enterprises, this is sufficient. The risk is network transit and API server storage (temporary caching during processing).

**Option 3: Hybrid approach (recommended)**

Self-host the codebase index (never sends code to external servers). Use external API for LLM inference only — but **sanitize the context before sending**:
- Remove hardcoded secrets (detected via regex / truffleHog patterns)
- Replace internal service names with generic names (`payment-service` → `service-a`)
- Remove comments containing classification labels (`CONFIDENTIAL`, `TOP SECRET`)

The LLM only sees sanitized code. The developer sees the response with original names restored via the sanitization map.

This is a pragmatic middle ground: enterprise-grade IP protection without the cost/complexity of full self-hosting.

---

### Q9: How would you measure whether the coding assistant actually improves developer productivity?

**Answer:**

This is harder than it sounds because "developer productivity" is notoriously difficult to measure.

**Proxy metrics (easy to collect from the IDE extension):**

- **Suggestion acceptance rate:** What percentage of generated suggestions does the developer accept vs reject? Target: > 30% (GitHub Copilot is ~28-35%).
- **Suggestion modification rate:** Of accepted suggestions, what percentage are used verbatim vs modified? High modification rate = suggestions are close but not quite right.
- **Time to first keystroke after suggestion:** If the developer immediately starts editing a suggestion, it was probably wrong. If they accept and move on, it was probably right.
- **Session engagement:** Average messages per session, return usage rate (do developers use it again the next day?), feature adoption (which tools get used?).

**Outcome metrics (harder, require instrumentation):**

- **Time to first commit for a new feature:** Track from the moment a new branch is created to the first working commit. Compare before/after rolling out the assistant.
- **PR size (lines of code per PR):** Larger PRs from the same developers might indicate they're moving faster. Or it might mean they're writing worse code. Correlate with code review time.
- **Test coverage on generated code:** Does code written with AI assistance have the same or better test coverage as manually written code?

**Developer surveys (essential):**
Ask developers directly every two weeks: "On a scale of 1-5, how much time did the assistant save you this week?" "What did it help most with?" "What was frustrating?" Self-reported time savings are subjective but directionally useful.

**A/B testing:**
Roll out to 50% of developers. Compare the two cohorts on commit velocity, bug rate in first-week-post-commit, and survey satisfaction scores. A proper controlled experiment.

**The honest caveat:** There are no standard metrics for developer productivity. Every company measures it differently. Pick 2-3 metrics that matter to your organization (e.g., sprint velocity, P0 bug rate, onboarding time for new developers), measure them before and after the assistant rollout, and make directional judgments.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Architecture_Blueprint.md](./Architecture_Blueprint.md) | System architecture blueprint |
| [📄 Build_Guide.md](./Build_Guide.md) | Step-by-step build guide |
| [📄 Component_Breakdown.md](./Component_Breakdown.md) | Component breakdown |
| [📄 Data_Flow_Diagram.md](./Data_Flow_Diagram.md) | Data flow diagram |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Tech_Stack.md](./Tech_Stack.md) | Technology stack choices |

⬅️ **Prev:** [02 RAG Document Search System](../02_RAG_Document_Search_System/Architecture_Blueprint.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 AI Research Assistant](../04_AI_Research_Assistant/Architecture_Blueprint.md)
