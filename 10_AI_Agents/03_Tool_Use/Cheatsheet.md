# Tool Use — Cheatsheet

**One-liner:** A tool is a function the agent can call — it has a name, description, and parameters. The agent reads descriptions to decide which tool to use, then the framework executes the actual function.

---

## Key Terms

| Term | What it means |
|---|---|
| **Tool** | A function the agent can call to interact with the world |
| **Tool schema** | The structured definition: name + description + parameters |
| **Function calling** | The native API feature (OpenAI, Anthropic) that lets LLMs request specific function calls with structured parameters |
| **Tool description** | Plain English text explaining what the tool does and when to use it — this guides the agent's decisions |
| **Parameters** | The inputs the function needs, with types and descriptions |
| **Tool result** | The return value of the function, added to context as an Observation |
| **Toolbox** | The full set of tools available to an agent |
| **Built-in tool** | Tools provided by frameworks (search, calculator, Python REPL) |
| **Custom tool** | A tool you write for your specific use case |

---

## Tool Schema Template

```json
{
  "name": "tool_name",
  "description": "What this tool does. When to use it. What it returns.",
  "parameters": {
    "type": "object",
    "properties": {
      "param1": {
        "type": "string",
        "description": "What this parameter is"
      }
    },
    "required": ["param1"]
  }
}
```

---

## LangChain Tool Definition (Python)

```python
from langchain.tools import Tool

my_tool = Tool(
    name="tool_name",
    func=my_function,           # The actual Python function
    description="What it does. When to use it. What it returns."
)
```

---

## When to Use Tools

**Use a search tool when:**
- The agent needs current information (post training cutoff)
- The agent needs facts it might hallucinate

**Use a calculator/code tool when:**
- The agent needs precise math
- The agent needs to process data programmatically

**Use a database tool when:**
- The answer lives in structured data
- You need exact lookups, not approximations

**Use an API tool when:**
- The action requires interacting with an external service
- The agent needs to create, update, or delete real records

---

## Golden Rules

1. **The description is everything.** The LLM picks tools based on descriptions. Vague description = wrong tool choice.

2. **One tool, one job.** Don't build a tool that does five things. Build five tools.

3. **Tell the agent what the tool returns.** "Returns a JSON object with keys: price, currency, last_updated."

4. **Handle errors in the tool.** Return a clear error string rather than raising an exception. The agent should see the error as an Observation and adjust.

5. **Start with 3-5 tools max.** You can always add more. Too many tools confuse the agent.

6. **Test tools independently.** Call each tool function directly before connecting it to an agent. Make sure it works.

7. **Separate read tools from write tools.** Read tools are safe. Write tools (send email, make payment) need guardrails.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |
| [📄 Building_Custom_Tools.md](./Building_Custom_Tools.md) | Guide to building custom tools |

⬅️ **Prev:** [02 ReAct Pattern](../02_ReAct_Pattern/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 Agent Memory](../04_Agent_Memory/Theory.md)
