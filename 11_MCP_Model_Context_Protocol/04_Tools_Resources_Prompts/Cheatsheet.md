# Cheatsheet — Tools, Resources, and Prompts

**The three MCP primitives: Tools DO things, Resources READ things, Prompts GUIDE things.**

---

## Key Terms 📋

| Term | Definition |
|---|---|
| **Tool** | A callable function with side effects; the AI calls it to take action |
| **Resource** | Read-only data identified by URI; the AI reads it for context |
| **Prompt** | Parameterized prompt template; fills in and returns messages for the AI |
| **inputSchema** | JSON Schema defining what arguments a Tool accepts |
| **URI** | Uniform Resource Identifier — the address of a Resource (e.g., `file:///notes.txt`) |
| **MIME type** | The type of resource content (e.g., `text/plain`, `application/json`) |
| **Content** | What a tool or resource returns — can be text, image, or embedded resource |

---

## Three Primitives at a Glance

| | Tool | Resource | Prompt |
|---|---|---|---|
| **Purpose** | Perform an action | Provide data to read | Provide a prompt template |
| **Side effects?** | YES | NO | NO |
| **Takes arguments?** | YES (JSON Schema) | NO (URI only) | YES (named parameters) |
| **Returns** | Action result | Data content | Messages list |
| **Who requests it** | AI model | AI model or host | User or host |
| **MCP method** | `tools/call` | `resources/read` | `prompts/get` |

---

## Tool Definition Structure

```json
{
  "name": "create_file",
  "description": "Create a new file with the given name and content",
  "inputSchema": {
    "type": "object",
    "properties": {
      "path": {
        "type": "string",
        "description": "Absolute path where the file should be created"
      },
      "content": {
        "type": "string",
        "description": "Text content to write into the file"
      }
    },
    "required": ["path", "content"]
  }
}
```

---

## Resource Definition Structure

```json
{
  "uri": "file:///home/user/notes.txt",
  "name": "Personal Notes",
  "mimeType": "text/plain",
  "description": "User's personal notes file"
}
```

---

## Prompt Definition Structure

```json
{
  "name": "code_review",
  "description": "Generate a thorough code review",
  "arguments": [
    { "name": "code", "description": "The code to review", "required": true },
    { "name": "language", "description": "Programming language", "required": false }
  ]
}
```

---

## Tool Return Content Types

```json
// Text content
{ "type": "text", "text": "file contents here" }

// Image content
{ "type": "image", "data": "<base64>", "mimeType": "image/png" }

// Embedded resource
{ "type": "resource", "resource": { "uri": "...", "text": "..." } }
```

---

## When to Use Each

**Use a Tool when:**
- The operation changes state (creates, updates, deletes)
- You need to call an external API
- The operation requires arguments to know what to do

**Use a Resource when:**
- The data already exists and just needs to be read
- The data is addressable by a stable URI
- No arguments are needed beyond the URI

**Use a Prompt when:**
- You want to standardize a workflow or persona across the team
- You have a complex multi-step prompt that should be reusable
- Users should be able to select and run it without writing prompt text

---

## Golden Rules 🏆

- Tools change the world; Resources do not — respect this boundary
- Write tool `description` fields as if explaining to an AI: be specific and complete
- Always validate tool inputs — the AI can pass wrong argument types
- Return helpful error messages from tools so the AI can understand what went wrong
- Resources use URIs — design your URI scheme to be readable and consistent
- Prompts return messages (role + content), not plain text
- Fewer, well-designed tools beat many vague tools — the AI picks better when descriptions are clear

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [03 Hosts Clients Servers](../03_Hosts_Clients_Servers/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 Transport Layer](../05_Transport_Layer/Theory.md)