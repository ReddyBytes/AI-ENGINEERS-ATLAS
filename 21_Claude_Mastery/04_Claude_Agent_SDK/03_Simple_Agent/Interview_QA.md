# Simple Agent — Interview Q&A

## Beginner Level

**Q1: What are the three minimum requirements to build a working agent with the Claude Agent SDK?**

<details>
<summary>💡 Show Answer</summary>

A: Three things are required:
1. At least one `@tool`-decorated function — this gives the agent an action it can take
2. An `Agent` object configured with the model, tools list, and system prompt
3. A call to `agent.run(goal)` with the user's goal

The `@tool` decorator generates the JSON schema, the `Agent` object wires everything together, and `agent.run()` starts the loop. Without a tool, the agent has no actions and is equivalent to a single API call. Without `agent.run()`, nothing executes.

</details>

---

<br>

**Q2: What role does the docstring play in a `@tool`-decorated function?**

<details>
<summary>💡 Show Answer</summary>

A: The docstring becomes the tool's description — the text Claude reads to decide when to use this tool. Claude cannot see your Python code or variable names beyond the function signature; the docstring is its entire understanding of the tool's purpose, expected inputs, outputs, and constraints. A poor docstring ("does some stuff") means Claude may call the wrong tool, pass wrong parameters, or not call the tool at all. A good docstring ("searches the product catalog by keyword, returns list of dicts with name/price/stock, use when user asks about products") enables reliable tool selection. The docstring is as much a part of your agent's design as the tool logic itself.

</details>

---

<br>

**Q3: What's the difference between defining a `@tool` function and having the agent use it?**

<details>
<summary>💡 Show Answer</summary>

A: Defining `@tool` on a function creates the tool schema — it marks the function as available for agent use. But the function only gets called if: (1) it's included in `tools=[your_function]` when creating the Agent, AND (2) Claude decides to call it during the agent loop. If you define `@tool` but don't pass it to `tools=[]`, Claude never sees the tool and will never call it. If you pass it in `tools=[]` but Claude doesn't need it for the given goal, it still won't be called. Tools are capabilities, not commands.

</details>

---

## Intermediate Level

**Q4: Walk through what happens at the Python level when `agent.run("count the words in 'hello world'")` executes.**

<details>
<summary>💡 Show Answer</summary>

A: Here's the sequence:
1. `agent.run()` constructs the initial message payload: `{model, system_prompt, tools=[schema], messages=[{role: user, content: "count the words..."}]}`
2. The SDK calls `client.messages.create(...)` with this payload
3. Claude responds with a `tool_use` block: `{type: tool_use, name: "count_words", input: {text: "hello world"}}`
4. The SDK detects `stop_reason == "tool_use"`, finds the `count_words` function in the tool registry
5. The SDK calls `count_words(text="hello world")` → returns `2`
6. The SDK appends the tool call and result to messages: `[..., {role: assistant, content: [tool_use]}, {role: user, content: [tool_result: 2]}]`
7. The SDK calls `client.messages.create(...)` again with the updated messages
8. Claude responds with a final text answer: `"'hello world' contains 2 words."`
9. `stop_reason == "end_turn"` → SDK returns this text from `agent.run()`

</details>

---

<br>

**Q5: How does the model "know" what tools are available to it at each loop iteration?**

<details>
<summary>💡 Show Answer</summary>

A: The tool schemas are passed as the `tools` parameter in every API call the SDK makes. Each schema includes the tool name, description, and parameter structure. The model doesn't "remember" tools between calls — it sees the schemas fresh on every iteration because the SDK always includes them in the request. This means: changing the tools list between runs affects all subsequent agent calls immediately. It also means the tool schema consumes tokens on every call — large tool schemas with many tools have a real cost impact. Design compact but clear tool descriptions.

</details>

---

<br>

**Q6: What happens if you give the agent a goal that requires a tool it doesn't have?**

<details>
<summary>💡 Show Answer</summary>

A: Claude attempts to work with what it has. Depending on the model's judgment, it might: answer based on its training data (if the task is answerable without tools), explain that it doesn't have the necessary capability, attempt to approximate the task with available tools, or ask the user for the missing information. The model does not hallucinate tool calls for tools not in its schema — it can only call tools you've explicitly defined. If the goal is genuinely impossible without a specific tool, a well-prompted Claude will say so clearly rather than producing an incorrect answer.

</details>

---

## Advanced Level

**Q7: How would you design a minimal agent that handles multiple, heterogeneous tasks from different users reliably?**

<details>
<summary>💡 Show Answer</summary>

A: Key design decisions for multi-user, multi-task reliability:

**Stateless by default**: create a new `Agent()` instance per request. Don't share agent instances across requests — each needs its own context.

**System prompt parameterization**: inject user-specific context into the system prompt at instantiation time, not at goal time.

**Tool function isolation**: tool functions should be stateless. Side effects (DB writes, API calls) should be idempotent where possible.

**Concurrency**: the SDK is synchronous by default — for concurrent users, run each `agent.run()` in a thread pool or use the async variant.

**Timeout enforcement**: set `max_steps` and add a wall-clock timeout wrapper around `agent.run()` to prevent one slow task from blocking others.

**Error boundaries**: catch `AgentError` per-request; a failure for user A should never affect user B.

```python
from concurrent.futures import ThreadPoolExecutor
import threading

def handle_request(user_id: str, goal: str) -> str:
    agent = Agent(
        model="claude-sonnet-4-6",
        tools=[...],
        system=f"You are assisting user {user_id}. [user context here]",
        max_steps=15
    )
    return agent.run(goal)

with ThreadPoolExecutor(max_workers=10) as pool:
    futures = [pool.submit(handle_request, uid, goal) for uid, goal in requests]
    results = [f.result(timeout=60) for f in futures]
```

</details>

---

<br>

**Q8: How would you test an agent that uses external tools without hitting real APIs in CI?**

<details>
<summary>💡 Show Answer</summary>

A: Replace tools with mock versions that return controlled test data:

```python
@tool
def real_web_search(query: str) -> list[dict]:
    """Searches the web. Returns results."""
    return requests.get(f"https://api.search.com?q={query}").json()

@tool
def mock_web_search(query: str) -> list[dict]:
    """Searches the web. Returns results."""
    # Deterministic fixture for tests
    return [
        {"title": "Test result for: " + query, "url": "https://test.com", "snippet": "Test content"}
    ]

# In tests:
test_agent = Agent(
    model="claude-sonnet-4-6",
    tools=[mock_web_search],  # swap real → mock
    system=agent_system_prompt
)
result = test_agent.run("Find papers on diffusion models")
assert "diffusion" in result.lower()
```

Test strategy: unit test tools in isolation (independent of the agent), integration test the agent with mocks, and end-to-end test with real tools only in staging. The `@tool` decorator means mock and real versions are interchangeable — same schema, different implementation.

</details>

---

<br>

**Q9: What are the token cost implications of running a 10-step agent vs a single API call?**

<details>
<summary>💡 Show Answer</summary>

A: Each loop iteration is a full API call. In a 10-step agent:
- Step 1: prompt (500) + tool schema (200) + goal (50) = ~750 input tokens
- Step 2: prev + tool call (80) + result (500) = ~1,330 input tokens
- Step 3: prev + tool call + result = ~2,200 input tokens
- ...
- Step 10: all previous steps accumulated = potentially 8,000+ input tokens

Input tokens grow with each step because the full history is passed. Output tokens per step are typically 100-500. For a 10-step agent with moderate tool outputs: approximately 30,000-50,000 total tokens — vs ~750 tokens for a single call. This is why: (1) agents should only be used when multi-step is genuinely necessary, (2) tool outputs should be truncated, (3) prompt caching helps (the system prompt and tool schemas repeat on every call), (4) cost monitoring is essential in production.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Complete working code |

⬅️ **Prev:** [Why Agent SDK?](../02_Why_Agent_SDK/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Tool Calling in Agents](../04_Tool_Calling_in_Agents/Theory.md)
