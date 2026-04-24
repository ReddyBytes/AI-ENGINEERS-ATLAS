# Tool Calling — Interview Q&A

## Beginner

**Q1: What is tool calling and why do LLMs need it?**

<details>
<summary>💡 Show Answer</summary>

Tool calling (also called function calling) is a mechanism that lets an LLM request that your code executes a specific function during a conversation. The model doesn't run the function itself — it sends a structured request saying "call this function with these inputs," your code runs it, and returns the result.

LLMs need it because they only know what was in their training data, which has a cutoff date and no access to private data. With tool calling, a model can request real-time information (today's weather), query your database (order status), run a calculation accurately, or take an action (send an email). It turns a language model into an orchestrator that can interact with external systems.

</details>

---

**Q2: Walk me through the tool call cycle.**

<details>
<summary>💡 Show Answer</summary>

1. You define tools as JSON schemas with a name, description, and input parameters.
2. You send a user message along with those tool definitions to the model.
3. The model decides whether a tool is needed. If yes, it returns a `tool_use` block (not text) containing the tool name and the inputs it wants to pass.
4. Your code intercepts that response, extracts the tool name and inputs, and runs the actual function.
5. Your code sends a `tool_result` message back to the model containing what the function returned.
6. The model receives the result and generates its final text response to the user.

This cycle can repeat multiple times in one conversation if the model needs to use multiple tools sequentially.

</details>

---

**Q3: What is the difference between the tool "definition" and the tool "call"?**

<details>
<summary>💡 Show Answer</summary>

The tool definition is what you write upfront — it tells the model the tool exists. It has three parts: the name, a description explaining when to use it, and an input schema defining what parameters it accepts.

The tool call is what the model generates at runtime when it decides to use a tool. It contains the tool name and the actual parameter values the model has inferred from context (e.g., `{"city": "Paris", "unit": "celsius"}`).

You write the definition once. The model generates a new call each time it decides to use the tool.

</details>

---

## Intermediate

**Q4: How does the model decide which tool to call?**

<details>
<summary>💡 Show Answer</summary>

The model reads the description field of each tool definition and uses natural language understanding to match the user's request to the most appropriate tool. If a user asks "What's the weather in Tokyo?" and you have a tool with description "Get current weather for a city," the model matches the user's intent to that tool.

This is why the description is more important than the name. A tool named `tw` with description "Retrieves temperature and weather conditions for any city" will be used correctly. A tool named `get_weather` with description "Gets data" will often be misused.

If multiple tools could apply, the model uses context. If no tool applies, it answers from its own knowledge. You can also use `tool_choice` to force the model to use a specific tool.

</details>

---

**Q5: What are parallel tool calls and how do they work?**

<details>
<summary>💡 Show Answer</summary>

Parallel tool calls happen when the model returns multiple `tool_use` blocks in a single response. For example, if a user asks "Compare the weather in Paris and Tokyo," the model can request both `get_weather("Paris")` and `get_weather("Tokyo")` in the same response.

Your code should detect all `tool_use` blocks in the response, execute them (ideally in parallel with threading or async), collect all results, and return them all in a single `tool_result` message list before asking the model to continue.

This is significantly faster than sequential calls — instead of 2 round trips to the model, you do 1. For agents that need 5–10 tool calls, this can reduce latency by 60–80%.

</details>

---

**Q6: How do you handle tool call errors? What if the function fails?**

<details>
<summary>💡 Show Answer</summary>

You should always return a `tool_result` to the model even when the function fails. The pattern is: catch the exception in your code, and return the error message as the tool result with `is_error: true` (in Anthropic's API).

```python
try:
    result = run_my_tool(inputs)
    tool_result_content = str(result)
    is_error = False
except Exception as e:
    tool_result_content = f"Error: {str(e)}"
    is_error = True
```

Then include `is_error=True` in the tool_result message. The model will see the error and can either try a different approach, ask the user for clarification, or gracefully report that it couldn't complete the task. Never silently swallow errors — the model can't recover if it doesn't know something failed.

</details>

---

## Advanced

**Q7: How do you build a multi-step agentic loop with tool calling?**

<details>
<summary>💡 Show Answer</summary>

An agentic loop runs tool calls repeatedly until the model decides it has enough information to give a final answer. The loop looks like this:

```python
messages = [{"role": "user", "content": user_input}]

while True:
    response = client.messages.create(model=..., tools=tools, messages=messages)

    if response.stop_reason == "end_turn":
        break  # Model is done, return final text

    if response.stop_reason == "tool_use":
        # Execute all tool calls, collect results
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = execute_tool(block.name, block.input)
                tool_results.append({"tool_use_id": block.id, "content": result})

        # Add assistant response + tool results to history
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})
```

Key safeguards: set a max iteration limit (e.g., 10 turns) to prevent infinite loops. Log all tool calls for debugging. Validate tool inputs before execution.

</details>

---

**Q8: What are the security risks of tool calling and how do you mitigate them?**

<details>
<summary>💡 Show Answer</summary>

Three main risks:

**Prompt injection via tool results:** Malicious content in tool outputs could hijack the model's behavior. If you're passing web search results back as tool_result content, an attacker could inject "Ignore previous instructions." Mitigation: sanitize tool result content, keep tool results in a separate context from system instructions.

**Excessive permissions:** If your tools can delete records, send emails, or make payments — the model could be tricked into destructive actions. Mitigation: make tools read-only where possible, require confirmation for destructive actions, scope tool permissions to minimum necessary.

**Input hallucination:** The model might pass plausible-sounding but incorrect values to tools (e.g., a wrong order ID). Mitigation: validate all tool inputs, treat them like untrusted user input, return meaningful errors rather than silently failing.

</details>

---

**Q9: What is the difference between tool calling for structured output vs. RAG retrieval?**

<details>
<summary>💡 Show Answer</summary>

Tool calling for structured output: you define a tool like `extract_entities` with an input schema that matches your desired JSON structure. You tell the model "use this tool" and the model's tool_use input becomes your structured data. No function actually runs — you just use the schema enforcement mechanism to get reliable JSON.

RAG retrieval: you define a `search_knowledge_base(query)` tool that actually runs a vector similarity search and returns relevant document chunks. The model calls it to look up information before answering.

The first is a prompting trick to get structured output. The second is actual runtime retrieval. Both use the same tool calling mechanism but for completely different purposes. In production RAG systems, you often combine both: a retrieval tool that returns chunks, plus structured output to format the final answer.

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
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | Tool calling architecture |

⬅️ **Prev:** [01 Prompt Engineering](../01_Prompt_Engineering/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 Structured Outputs](../03_Structured_Outputs/Theory.md)
