# MCP vs REST API — When to Use Each

## Overview

Both MCP and REST APIs are ways for software to communicate with external services. But they were designed for very different purposes. Understanding the difference helps you make the right architectural choice.

---

## Side-by-Side Comparison 📊

| Dimension | REST API | MCP |
|---|---|---|
| **Designed for** | General-purpose web communication | AI model tool use |
| **Who calls it** | Any HTTP client (browser, app, script) | AI models via MCP clients |
| **Session state** | Stateless (each request is independent) | Stateful (session maintained throughout conversation) |
| **Protocol** | HTTP request/response | JSON-RPC 2.0 over stdio or SSE |
| **Discovery** | Manual (read docs / OpenAPI spec) | Built-in (`tools/list`, `resources/list`) |
| **Authentication** | API keys, OAuth, JWT in headers | Trust model — host controls which servers connect |
| **Schema** | OpenAPI/Swagger (optional) | JSON Schema in tool definitions (required) |
| **Direction** | Primarily client → server (request/response) | Bidirectional — server can also send notifications |
| **Streaming** | Possible but requires special setup | Native via SSE transport |
| **Purpose** | Expose functionality over the web | Expose capabilities to AI assistants |

---

## When to Use REST API ✅

Use a REST API when:

- You are building a public API that many different types of clients will consume (browsers, mobile apps, other services, scripts)
- Your consumers are human developers who will use your API directly
- You want to leverage the existing web infrastructure (load balancers, API gateways, caching)
- You need fine-grained HTTP-level control (specific status codes, headers, caching)
- You are integrating with existing systems that already speak HTTP
- You want to rate-limit, bill, and authenticate individual API consumers separately

**Example:** A payments API, a weather data service, a user authentication endpoint.

---

## When to Use MCP ✅

Use MCP when:

- You are building tools specifically for AI models to use
- You want the same tool to work with multiple AI applications without rewriting
- You need the AI to be able to discover what tools are available at runtime
- You want tools that are stateful and can maintain context across multiple calls in a conversation
- You are building a library of reusable AI capabilities for your organization
- You want clean separation between your AI application logic and your tool implementations

**Example:** A filesystem browser for AI, a code execution sandbox, a company knowledge base search tool.

---

## The Hybrid Pattern

Many real-world systems use **both**:

```
User → AI App (MCP Host)
              ↓
        MCP Client
              ↓
        MCP Server  →  calls  →  REST API (your existing backend)
```

Your existing REST APIs do not need to change. You write a thin MCP server that wraps your REST API calls and exposes them as MCP tools. The AI gets structured tool access; your existing systems stay unchanged.

**Example:** You have a customer database with a REST API. You write a `customer_lookup` MCP tool that internally calls `GET /api/customers/{id}`. The AI calls the MCP tool, not the REST endpoint directly.

---

## Key Conceptual Differences

**REST is stateless — MCP is stateful**

In REST, every request contains everything needed to process it. The server remembers nothing between requests. In MCP, a session is established at the start of a conversation and maintained throughout. The server can remember context, accumulate results, and maintain ongoing state.

**REST is for humans-writing-code — MCP is for AI-reading-schemas**

REST APIs are documented for human developers who read the docs and write integration code. MCP tool definitions include machine-readable descriptions and JSON Schema so the AI model itself can understand what a tool does and what arguments to pass — without a human in the loop.

**REST is pull-only — MCP supports server-side notifications**

In REST, the client always initiates requests. In MCP, the server can send notifications to the client (for example, "the file you were watching has changed"). This makes MCP better suited for event-driven AI workflows.

---

## Decision Guide 🗺️

```
Are you building for AI models specifically?
    YES → Use MCP
    NO  → Use REST

Do you need the same tool to work with multiple AI systems?
    YES → Use MCP
    NO  → Function calling might be simpler

Do you have an existing REST API you want AI to access?
    YES → Write an MCP wrapper around your REST API
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **MCP_vs_REST_API.md** | ← you are here |

⬅️ **Prev:** [09 Build an Agent](../../10_AI_Agents/09_Build_an_Agent/Project_Guide.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [02 MCP Architecture](../02_MCP_Architecture/Theory.md)