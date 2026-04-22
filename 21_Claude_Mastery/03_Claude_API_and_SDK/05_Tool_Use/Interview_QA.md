# Tool Use — Interview Q&A

## Beginner Questions

**Q1: What is tool use in the context of the Anthropic API?**

A: Tool use (also called function calling) is a protocol that lets Claude request execution of external functions. You define tools with JSON schemas, Claude decides when to call them and with what arguments, your application executes the actual function, and you return the result to Claude. Claude never executes tools directly — it only generates structured requests to call them.

---

**Q2: What three fields are required in a tool definition?**

A: `name` (the function identifier, snake_case), `description` (when and why to use the tool — this is what Claude reads to decide when to call it), and `input_schema` (a JSON Schema object defining the function's parameters, their types, and which are required).

---

**Q3: What does `stop_reason: "tool_use"` mean, and what must you do when you see it?**

A: It means Claude wants to call a tool. The response is not complete — Claude is waiting for you to execute the tool and return results. You must: (1) extract the `tool_use` block(s) from `response.content`, (2) execute the function(s) in your application, (3) append Claude's response as an assistant message, (4) append the tool results as a user message with `tool_result` content blocks, and (5) send another API call to continue the conversation.

---

**Q4: What is the `tool_use_id` field and why is it important?**

A: It's the unique identifier for each tool call in a response (e.g., `"toolu_01A09q90qw90lq92M9fjBz"`). When you return a `tool_result` content block, you must include the matching `tool_use_id`. Claude uses this to correlate which result belongs to which tool call — especially important when Claude makes multiple parallel tool calls in one response.

---

## Intermediate Questions

**Q5: What happens if Claude makes two tool calls in a single response? How do you handle it?**

A: Claude returns an assistant message with two `tool_use` blocks in the `content` array. You execute both functions (ideally in parallel for efficiency), then return a single user message containing both `tool_result` blocks — one for each `tool_use_id`. Both results go in the same user message. If you returned two separate messages (one per result), you'd violate the alternating role rule and get a 400 error.

---

**Q6: How should you handle a tool execution error? Should you raise an exception or return the error?**

A: Return the error as a string in the `tool_result` content, with `"is_error": True`. Never raise an exception that crashes your application. Claude will read the error message and respond gracefully — often acknowledging the error, suggesting alternatives, or asking the user if they want to retry. Raising exceptions breaks the agent loop and loses conversation context.

---

**Q7: Explain the `tool_choice` parameter and its four options.**

A: `tool_choice` controls whether and how Claude uses tools. `{"type": "auto"}` (default) lets Claude decide whether to use tools or answer directly. `{"type": "any"}` forces Claude to use at least one tool (useful for data extraction). `{"type": "tool", "name": "X"}` forces Claude to call a specific named tool. `{"type": "none"}` prevents tool use even when tools are defined (useful for a "reasoning only" pass in a multi-step pipeline).

---

**Q8: Why is the `description` field the most important part of a tool definition?**

A: Claude reads tool descriptions to decide when, whether, and how to call tools. A vague description like "gets data" gives Claude no signal about when to use the tool, leading to wrong tool selection or tools being ignored. A precise description like "Retrieves current stock price by ticker symbol. Use when the user asks about stock prices, market cap, or share value" tells Claude exactly when to use the tool and what to expect back. The input schema fields' descriptions are equally important — they prevent Claude from passing wrong argument types or formats.

---

## Advanced Questions

**Q9: Design a robust multi-tool agent loop that handles parallel calls, errors, and prevents infinite loops.**

A: 
```python
def agent_loop(user_message, tools, executors, max_iterations=10):
    messages = [{"role": "user", "content": user_message}]
    
    for iteration in range(max_iterations):
        response = client.messages.create(
            model="claude-sonnet-4-6", max_tokens=4096,
            tools=tools, messages=messages
        )
        
        if response.stop_reason == "end_turn":
            return next(b.text for b in response.content if b.type == "text"), iteration
        
        if response.stop_reason != "tool_use":
            raise ValueError(f"Unexpected stop_reason: {response.stop_reason}")
        
        messages.append({"role": "assistant", "content": response.content})
        
        # Execute all tool calls (parallel with asyncio in production)
        results = []
        for block in response.content:
            if block.type != "tool_use": continue
            try:
                result = executors[block.name](**block.input)
                results.append({"type":"tool_result","tool_use_id":block.id,"content":str(result)})
            except Exception as e:
                results.append({"type":"tool_result","tool_use_id":block.id,"content":f"Error: {e}","is_error":True})
        
        messages.append({"role": "user", "content": results})
    
    return f"Max iterations ({max_iterations}) reached", max_iterations
```

---

**Q10: How does streaming interact with tool use? What events do you receive during a streamed tool call?**

A: During streaming, when Claude decides to call a tool, the sequence is: (1) `content_block_start` with `"type": "tool_use"`, the tool name, and an empty input. (2) Multiple `content_block_delta` events with `"type": "input_json_delta"` containing fragments of the JSON arguments (partial JSON that you must concatenate before parsing). (3) `content_block_stop` when the tool arguments are complete. (4) `message_delta` with `"stop_reason": "tool_use"`. You then execute the tool and continue the non-streaming loop from Turn 2, or restart a streaming call with the tool result appended.

---

**Q11: How would you implement a caching strategy for tool definitions in a high-traffic application?**

A: Add `cache_control: {"type": "ephemeral"}` to the last tool in the tools array. Tool definitions are large, static across calls for the same application, and are a good caching target. On the first call, Anthropic caches everything up to and including the marked tool — subsequent calls within 5 minutes read from cache at 0.1x cost. For an application with 10 tools totaling 2,000 tokens and 1,000 daily requests, caching reduces tool definition cost from 2,000,000 tokens/day to ~210,000 tokens/day (first call + 9 cache reads × 0.1x). Combine with caching the system prompt for maximum savings.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept guide |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | Full architecture |
| [📄 Code_Example.md](./Code_Example.md) | Working code |

⬅️ **Prev:** [System Prompts](../04_System_Prompts/Interview_QA.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Streaming](../06_Streaming/Interview_QA.md)
