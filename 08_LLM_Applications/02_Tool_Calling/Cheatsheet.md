# Tool Calling — Cheatsheet

**One-liner:** Tool calling lets you define functions the LLM can request to use — your code runs them and returns results so the model can complete tasks that require real-world data or actions.

---

## Key Terms

| Term | Definition |
|------|-----------|
| **Tool / Function** | A capability you define that the model can request (e.g., `get_weather`, `search_db`) |
| **Tool definition** | JSON schema describing the tool's name, description, and input parameters |
| **tool_use block** | The model's response when it decides to call a tool — contains name + inputs |
| **tool_result** | The message you send back after running the tool — contains the output |
| **Input schema** | JSON Schema that defines what parameters the tool accepts |
| **Parallel tool calls** | Model requests multiple tools in one response turn |
| **Tool loop** | The cycle: model → tool request → your code runs → result returned → model continues |
| **Agentic loop** | Multi-turn tool loop where the model calls many tools to complete a long task |

---

## The Tool Call Loop (step by step)

```
1. You define tools (name + description + input schema)
2. User sends a message
3. Model responds with tool_use (or text if no tool needed)
4. Your code detects tool_use, executes the function
5. Your code sends tool_result back to the model
6. Model generates its final text response
7. Repeat from step 2 for multi-turn conversations
```

---

## Tool Definition Template

```python
{
    "name": "function_name",
    "description": "When to use this — be specific. This is what the model reads.",
    "input_schema": {
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",
                "description": "What this parameter means"
            },
            "param2": {
                "type": "number",
                "description": "What this parameter means"
            }
        },
        "required": ["param1"]
    }
}
```

---

## When to Use / Not Use

| Use tool calling when... | Don't use tool calling when... |
|--------------------------|-------------------------------|
| You need real-time data (weather, prices) | The data is already in the prompt |
| You need to query a database | The task is purely text generation |
| You need guaranteed structured output | Simple extraction (use output format prompting instead) |
| The model needs to take an action | You just want the model to reason through something |
| You need precise calculations | The math is simple enough for the model |

---

## Golden Rules

1. **Tool descriptions drive behavior** — write clear, specific descriptions. The model uses them to decide when to call.
2. **You run the tool, not the model** — the model just requests; your code executes.
3. **Always validate inputs** — treat tool inputs like untrusted user input (the model could hallucinate parameter values).
4. **Handle the case where no tool is called** — the model might answer directly without using a tool.
5. **Parallel calls are efficient** — design tools to be independent so they can run in parallel.
6. **Keep tool count manageable** — more than 10–15 tools and the model starts making poor choices. Group related tools or use tool routing.
7. **The description IS your instruction** — if the model is calling the wrong tool, fix the description first.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | Tool calling architecture |

⬅️ **Prev:** [01 Prompt Engineering](../01_Prompt_Engineering/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 Structured Outputs](../03_Structured_Outputs/Theory.md)
