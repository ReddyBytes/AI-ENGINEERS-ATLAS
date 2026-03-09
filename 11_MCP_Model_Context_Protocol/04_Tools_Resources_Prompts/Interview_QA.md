# Interview Q&A — Tools, Resources, and Prompts

## Beginner

**Q1: What are the three MCP primitives and what is the main difference between them?**

> The three MCP primitives are:
> - **Tools** — callable functions that the AI uses to take action and change state (write a file, query a database, send an email). They have side effects.
> - **Resources** — read-only data the AI can access by URI (file contents, database records, documentation). No side effects.
> - **Prompts** — parameterized prompt templates that fill in and return structured messages for the AI to use. No side effects, but they guide AI behavior.
>
> The main difference: Tools DO, Resources READ, Prompts GUIDE.

**Q2: How does the AI model know what arguments to pass when calling a Tool?**

> Each tool has an `inputSchema` field that is a JSON Schema object. JSON Schema defines the argument names, types, required fields, and descriptions. The AI model reads this schema along with the tool's `description` field to understand what the tool needs. For example, if a tool's schema says it needs a `path` (string, required) and `encoding` (string, optional), the AI model will construct a valid argument object before calling the tool.

**Q3: Give an example of when you would use a Resource instead of a Tool.**

> If you have a project README file that the AI should be able to read, you should expose it as a Resource at a URI like `file:///project/README.md`. The AI reads it using `resources/read`. You would use a Tool instead if the data requires parameters to retrieve (like `get_user_record(user_id=123)`) or if the operation has side effects. The rule of thumb: if the data lives at a stable address and reading it does not change anything, use a Resource.

---

## Intermediate

**Q4: A developer wants to expose a database to an AI model. What tools and resources would you design?**

> I would design:
>
> **Tools** (because they execute queries and can change state):
> - `run_read_query(sql: string)` — for SELECT queries
> - `run_write_query(sql: string)` — for INSERT/UPDATE/DELETE (with confirmation)
> - `list_tables()` — returns all table names
> - `describe_table(table_name: string)` — returns schema for one table
>
> **Resources** (for read-only, stable data):
> - `db://schema/tables` — the full database schema as a resource
> - `db://tables/{table_name}` — individual table schemas as resources
>
> Separating read queries into tools (not resources) makes sense because they take parameters. The schema is a resource because it is stable and has a natural URI.

**Q5: What is the difference between a Prompt and a System Prompt you would write directly in your application?**

> A system prompt in your app is hardcoded — it is written once in your code and applies to every conversation. An MCP **Prompt** is a named, parameterized template stored on a server. Users or the host can request it by name with arguments, and the server fills it in and returns the messages. This makes prompts:
> - **Reusable** — multiple apps can use the same server's prompts
> - **Parameterized** — different arguments give different results from the same template
> - **Managed** — the prompt lives in one place on the server; update it once and all clients get the update
> - **Discoverable** — clients can list what prompts are available without reading source code

**Q6: Can a Tool return more than just text? What content types are supported?**

> Yes. Tool results (and resource contents) can be:
> - **Text** — plain text or code, returned as `{"type": "text", "text": "..."}`
> - **Image** — base64-encoded image data with a MIME type, returned as `{"type": "image", "data": "...", "mimeType": "image/png"}`
> - **Embedded Resource** — a reference to a resource URI with content, returned as `{"type": "resource", "resource": {...}}`
>
> A single tool call can return multiple content items — for example, both a text explanation and an image chart.

---

## Advanced

**Q7: How would you design tools for a potentially dangerous operation like deleting files?**

> For dangerous operations I would:
> 1. **Name it clearly** — call it `delete_file` not `remove_item` so there is no ambiguity
> 2. **Document the danger** — in the description write "DESTRUCTIVE: permanently deletes the file at the given path. Cannot be undone."
> 3. **Return confirmation details** — have the tool return what it deleted so the AI can report back to the user
> 4. **Consider a `dry_run` parameter** — a boolean that, when true, only reports what would be deleted without actually deleting anything
> 5. **At the host layer** — implement a confirmation dialog so users see what the AI is about to delete and can approve or deny it
>
> The tool itself executes the deletion, but the host is responsible for showing the user what is about to happen before the tool is called.

**Q8: How does JSON Schema in tool definitions help the AI model make better calls?**

> JSON Schema gives the AI model precise, machine-readable information about what each tool argument must be. Instead of vague instructions, the schema provides:
> - **Types**: `"type": "string"` tells the AI not to pass a number
> - **Required fields**: The `"required"` array tells the AI which arguments it cannot omit
> - **Descriptions**: `"description"` on each property explains what the argument means
> - **Enums**: `"enum": ["read", "write"]` restricts the AI to valid choices
> - **Constraints**: `"minLength"`, `"pattern"`, `"minimum"` etc. give additional guidance
>
> AI models are trained to follow JSON Schema when calling tools, so well-defined schemas result in fewer invalid tool calls and less error handling.

**Q9: Describe a scenario where you would use all three MCP primitives (Tools, Resources, and Prompts) together in one server.**

> Consider a **documentation assistant** MCP server for a software project:
>
> **Resources**: The server exposes every documentation file as a resource:
> - `docs://api/authentication` → authentication documentation
> - `docs://guides/quickstart` → quickstart guide
>
> **Tools**: The server exposes search and write tools:
> - `search_docs(query: string)` — full-text search across documentation
> - `create_doc(title, content, section)` — create a new documentation file
> - `update_doc(path, content)` — update an existing documentation file
>
> **Prompts**: The server stores standard documentation workflows:
> - `write_api_doc` — a prompt template for documenting a new API endpoint (with parameters for method, path, parameters, response schema)
> - `review_docs` — a prompt that guides the AI to check documentation for accuracy and completeness
>
> The AI can read existing docs (Resources), update them (Tools), and follow standard documentation workflows (Prompts) — all through one focused server.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [03 Hosts Clients Servers](../03_Hosts_Clients_Servers/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 Transport Layer](../05_Transport_Layer/Theory.md)