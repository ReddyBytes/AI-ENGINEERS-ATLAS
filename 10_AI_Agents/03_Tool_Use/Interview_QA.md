# Tool Use — Interview Q&A

## Beginner

**Q1: What is a tool in the context of AI agents?**

<details>
<summary>💡 Show Answer</summary>

A tool is a **function the agent can call** to interact with the world outside the LLM.

Without tools, an agent can only use information from its training data — it can't search the web, run code, query a database, or take actions.

With tools, it can do all of those things. Tools are what let agents affect reality.

Every tool has three parts:
- **Name**: how the agent refers to it
- **Description**: what it does (the agent reads this to decide when to use it)
- **Parameters**: what inputs it needs

Examples: a web search tool, a calculator, a database lookup function, a file reader.

</details>

---

**Q2: How does the agent decide which tool to use?**

<details>
<summary>💡 Show Answer</summary>

The agent reads the **descriptions** of all available tools and matches its current need to the most appropriate one.

If the agent needs current information → it reads "search_web: searches the internet for up-to-date information" and picks that.

If the agent needs to calculate → it reads "calculator: evaluates math expressions" and picks that.

This is why descriptions are so important. The LLM doesn't execute tools — it just reads descriptions and decides which one to request. The better and clearer the description, the better the tool selection.

</details>

---

**Q3: What is "function calling" and how does it relate to tools?**

<details>
<summary>💡 Show Answer</summary>

Function calling is a **native API feature** in modern LLMs (OpenAI, Anthropic's Claude, Google Gemini) that allows the model to output a structured request to call a function with specific parameters.

Instead of asking the LLM to output text like `Action: search[Python history]`, function calling lets you define tools as structured schemas. The LLM then outputs something like:

```json
{
  "function": "search_web",
  "arguments": {"query": "Python programming language history"}
}
```

Your code reads this, calls the actual Python function, gets the result, and passes it back.

Function calling is more reliable than text parsing because the output is structured and predictable.

</details>

---

## Intermediate

**Q4: What makes a good tool description vs a bad one?**

<details>
<summary>💡 Show Answer</summary>

A bad description is vague and doesn't guide the agent:
```
name: "data_tool"
description: "gets data"
```

A good description tells the agent exactly when to use the tool, what it returns, and any important caveats:
```
name: "get_product_price"
description: "Retrieves the current price of a product from our inventory system.
              Use this when the user asks about product pricing or cost.
              Input: product_name (string).
              Returns: price in USD as a float. Returns 'Product not found' if the
              product doesn't exist in inventory."
```

Key elements of a good description:
1. What the tool does
2. When to use it ("use this when...")
3. What it returns
4. What it does NOT do or any limitations
5. Edge case behavior (errors, not found, etc.)

</details>

---

**Q5: How do you handle tool errors gracefully in an agent?**

<details>
<summary>💡 Show Answer</summary>

The tool function should **catch exceptions and return a clear error string** rather than raising an exception. This way, the error becomes an Observation the agent can reason about.

Example:
```python
def get_stock_price(symbol: str) -> str:
    try:
        price = fetch_from_api(symbol)
        return f"${price:.2f}"
    except SymbolNotFoundError:
        return f"Stock symbol '{symbol}' not found. Check the symbol and try again."
    except APIError as e:
        return f"API error: {str(e)}. Try again in a moment."
```

When the agent sees "Stock symbol 'AAPL123' not found", it can reason: "I may have the wrong symbol. Let me search for the correct ticker."

If you raise an exception instead, the agent might crash or get stuck.

</details>

---

**Q6: What is the difference between built-in tools and custom tools?**

<details>
<summary>💡 Show Answer</summary>

**Built-in tools** come with frameworks or are ready-made integrations:
- DuckDuckGo/Tavily search
- Wikipedia lookup
- Python REPL (code execution)
- Calculator
- File system access

You configure them and add them to your agent.

**Custom tools** are functions you write for your specific domain:
- `query_our_crm(customer_id)` — looks up a specific customer
- `post_to_slack(channel, message)` — sends a Slack message
- `get_shipping_status(order_id)` — checks your logistics system

The pattern is the same for both: define the function, write a clear description, wrap it as a tool, add to the agent. The difference is just whether someone already wrote the function for you.

</details>

---

## Advanced

**Q7: How do you secure tools that can take destructive actions (delete, send, pay)?**

<details>
<summary>💡 Show Answer</summary>

Several layers of protection:

1. **Separate read and write tools** — never let the agent call a delete function with the same ease as a read function

2. **Require confirmation for irreversible actions** — add a `confirm: bool` parameter that must be explicitly set to `True` for writes

3. **Rate limiting** — limit how many times a write tool can be called per session

4. **Audit logging** — every tool call is logged with timestamp, parameters, and caller identity

5. **Human-in-the-loop** — for high-stakes tools (payments, emails), pause the agent and require human approval before execution

6. **Scope restrictions** — a customer service agent should only be able to query *that customer's* data, not all customers'

7. **Dry run mode** — implement a `dry_run=True` option that shows what would happen without doing it

</details>

---

**Q8: How does tool use work differently across LLM providers (OpenAI vs Anthropic vs Google)?**

<details>
<summary>💡 Show Answer</summary>

All three support structured tool use but with slightly different syntax:

**OpenAI** uses `tools` in the API request with `type: "function"`. The model outputs `tool_calls` with structured arguments.

**Anthropic (Claude)** uses `tools` in the API request similarly. Claude outputs `tool_use` blocks in its response with `input` parameters.

**Google (Gemini)** uses `tools` with `function_declarations`. The model outputs `functionCall` with `args`.

The underlying concept is identical across all three. Frameworks like LangChain abstract these differences so your tool definitions work with any provider.

In practice, if you're using a framework, you define tools once and the framework handles the provider-specific formatting.

</details>

---

**Q9: How would you design a tool registry for a production agent system?**

<details>
<summary>💡 Show Answer</summary>

A tool registry is a central system that manages tool definitions, permissions, and versioning:

```python
class ToolRegistry:
    def __init__(self):
        self._tools = {}
        self._permissions = {}  # tool_name -> required_permission_level

    def register(self, tool, permission_level="read"):
        self._tools[tool.name] = tool
        self._permissions[tool.name] = permission_level

    def get_tools_for_agent(self, agent_permission_level):
        """Return only tools the agent is allowed to use."""
        return [
            tool for name, tool in self._tools.items()
            if self._permissions[name] <= agent_permission_level
        ]
```

Key features of a production tool registry:
- **Permission levels** — different agents get different tool sets
- **Versioning** — tools can be updated without breaking existing agents
- **Documentation** — auto-generate tool docs from schemas
- **Monitoring** — track which tools are called, how often, and what fails
- **Feature flags** — enable/disable tools without redeployment
- **Testing harness** — run tool tests in isolation before deploying

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |
| [📄 Building_Custom_Tools.md](./Building_Custom_Tools.md) | Guide to building custom tools |

⬅️ **Prev:** [02 ReAct Pattern](../02_ReAct_Pattern/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 Agent Memory](../04_Agent_Memory/Theory.md)
