# Why Agent SDK? — Interview Q&A

## Beginner Level

**Q1: What does the Agent SDK give you that the raw Messages API doesn't?**

<details>
<summary>💡 Show Answer</summary>

A: The Agent SDK provides a complete, pre-built implementation of the agent loop. With the raw API, you must write the `while True` loop yourself, extract tool call blocks from responses, dispatch them to your Python functions, format tool results back into the correct message structure, handle errors, and track context. The SDK handles all of this automatically. You define tools with `@tool` decorators, create an `Agent` object, call `agent.run(goal)`, and the SDK manages every loop iteration. This eliminates a class of bugs (malformed tool result messages, missed stop conditions, context tracking errors) that are common when writing the loop manually.

</details>

---

<br>

**Q2: What is the `@tool` decorator and what does it generate?**

<details>
<summary>💡 Show Answer</summary>

A: The `@tool` decorator transforms a regular Python function into a Claude-compatible tool definition. It reads the function's name, parameter types (from type hints), and description (from the docstring), and generates a JSON schema in the format Claude expects. At runtime, when Claude produces a tool call with that tool's name, the SDK uses this registration to: find the function, validate the input parameters, call it with the correct arguments, and format the return value as a tool result. Without `@tool`, you would manually write the JSON schema and write a dispatch function — both tedious and error-prone.

</details>

---

<br>

**Q3: When should you use the raw API instead of the Agent SDK?**

<details>
<summary>💡 Show Answer</summary>

A: Use the raw API for: (1) single-turn interactions where the model answers without tool use — there's no loop to manage; (2) custom loop logic that doesn't fit the standard agent pattern, such as stateful game engines, multi-player interactions, or systems where the loop is managed by an external framework like LangGraph; (3) tight integration with an existing system that manages its own message history. Use the Agent SDK for any multi-step agent that uses tools, needs subagent support, or benefits from the built-in error recovery and context management.

</details>

---

## Intermediate Level

**Q4: How does the Agent SDK handle tool execution errors?**

<details>
<summary>💡 Show Answer</summary>

A: When a tool function raises an exception, the SDK catches it, formats the exception message as a tool result with an error flag, and injects it into the model's context. The model then sees something like: "Tool execution failed: ZeroDivisionError: division by zero." The model can then decide to retry with different parameters, call a different tool, or explain the error to the user. This is a key advantage over manually writing the loop — in a manual implementation, an unhandled exception would crash the loop entirely. The SDK makes error recovery automatic and gives the model agency in handling failures.

</details>

---

<br>

**Q5: What happens inside `agent.run()` if the model never produces a final answer?**

<details>
<summary>💡 Show Answer</summary>

A: The SDK enforces a `max_steps` limit (configurable, default typically 20). If the model keeps producing tool calls without ever returning a final text response, the loop terminates after `max_steps` iterations and returns a partial result or an error indicating the limit was reached. This prevents runaway agents from looping indefinitely. In practice, the most common cause of hitting max_steps is an ambiguous goal that the model can't determine is "done" — fix this by giving the model explicit success criteria in the system prompt: "When you have found the answer, return it directly without calling any more tools."

</details>

---

<br>

**Q6: Can you mix the Agent SDK and the raw Messages API in the same application?**

<details>
<summary>💡 Show Answer</summary>

A: Yes. A common pattern is: use the Agent SDK for the agent loop, but inside tool functions, use the raw API for specific calls that need custom parameters. For example, a tool might need to call Claude with a very specific token budget, a particular temperature, or prompt caching — all of which you control directly with `messages.create()`. The `@tool` function is just a Python function; anything you can do in Python, you can do inside it. Another pattern: use the raw API for the outer application (authentication, routing, logging) and instantiate Agent SDK agents for specific tasks within that application.

</details>

---

## Advanced Level

**Q7: What are the performance implications of the Agent SDK's context management compared to a hand-rolled loop?**

<details>
<summary>💡 Show Answer</summary>

A: The SDK stores the full message history in memory and passes it with every API call — this is the same behavior as a well-written manual loop. The performance difference is not in context management but in correctness overhead: the SDK validates tool call formats, handles edge cases (empty content blocks, multiple tool calls in one response, tool calls mixed with text), and manages the message structure according to the API specification. A hand-rolled loop that handles all these edge cases correctly produces identical API calls. Where the SDK adds value is in development velocity and correctness, not raw runtime performance. If you identify a specific SDK behavior adding latency (e.g., serialization overhead for large tool outputs), you can override at the tool level.

</details>

---

<br>

**Q8: How would you implement a custom `before_tool` hook to enforce an approval workflow for sensitive operations?**

<details>
<summary>💡 Show Answer</summary>

A: The `before_tool` callback receives the tool name and input before execution and returns a boolean — `True` to allow, `False` to block (the SDK then returns a "rejected" message to the model). For an approval workflow:

```python
SENSITIVE_TOOLS = {"delete_records", "send_email", "execute_payment"}

def require_approval(tool_name: str, tool_input: dict) -> bool:
    if tool_name not in SENSITIVE_TOOLS:
        return True  # allow automatically
    
    # Log the request
    audit_log.record(tool_name, tool_input)
    
    # Request approval (sync in CLI, async in web apps)
    ticket_id = approval_service.create_request(
        tool=tool_name,
        params=tool_input,
        requested_by=session.user_id
    )
    approved = approval_service.wait_for_decision(ticket_id, timeout=300)
    
    if not approved:
        audit_log.record_rejection(ticket_id)
    return approved

agent = Agent(model=..., tools=[...], before_tool=require_approval)
```

The model receives the rejection as a tool result and can adjust its approach — ask for a different method, reduce scope, or explain to the user why it couldn't proceed.

</details>

---

<br>

**Q9: How does the Agent SDK's automatic error recovery differ from implementing retry logic manually, and when is each appropriate?**

<details>
<summary>💡 Show Answer</summary>

A: The SDK's automatic error recovery passes the exception back to the model as context. The model then decides how to respond — this is "intelligent error recovery." Manual retry logic blindly retries the same call with the same parameters, which is appropriate for transient errors (network timeout, rate limit, temporary service unavailability) where the same call should eventually succeed.

The two patterns are complementary:
- Wrap tool functions with manual retry for transient errors (using exponential backoff)
- Let the SDK's automatic recovery handle logical errors (wrong parameters, invalid state, unexpected results)

A combined approach: the tool function retries on `TimeoutError` and `RateLimitError` (transient), but raises `ValueError` immediately on invalid input (logical). The SDK passes `ValueError` to the model so it can fix the parameters, while the model never sees the transient retries.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Comparison.md](./Comparison.md) | Raw API vs SDK full table |

⬅️ **Prev:** [What Are Agents?](../01_What_are_Agents/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Simple Agent](../03_Simple_Agent/Theory.md)
