# Tool Calling in Agents — Interview Q&A

## Beginner Level

**Q1: What is a tool call in the context of an agent, and how is it different from a function call in regular code?**

A: In regular code, a function call is synchronous and direct — the programmer writes `result = function(args)` and it executes. A tool call in an agent is a request from the model: Claude produces a JSON object describing which function it wants called and with what parameters. The agent loop (not Claude) then executes the function and injects the result back into Claude's context. Claude never directly executes code — it requests execution. This indirection is what allows the SDK to: validate inputs, log the call, enforce permissions, and handle errors before the model sees the result.

---

**Q2: Why does a good tool docstring matter for agent reliability?**

A: The docstring is the model's only source of information about when and how to use the tool. Claude reads the docstring to decide: "Is this tool relevant to my current step?" and "What parameters should I pass?" A vague docstring produces unreliable tool selection — Claude may call the wrong tool, skip a useful tool, or pass wrong parameter types. A specific docstring that says "Use this to look up customer account details by customer ID. Returns: id, name, email, plan, status. Raises ValueError if customer not found" gives Claude everything it needs to use the tool correctly. Think of docstrings as the tool's API contract.

---

**Q3: What happens to a tool call when the function raises an exception?**

A: The SDK catches the exception and formats it as a tool result with an error flag, approximately: `{"type": "tool_result", "tool_use_id": "...", "is_error": true, "content": "ValueError: Customer not found: id=999"}`. This is injected into the model's context like any other tool result. Claude then sees the error and can respond intelligently: try a different customer ID, call a different tool, or inform the user that the customer doesn't exist. The agent loop does not crash — error recovery is automatic.

---

## Intermediate Level

**Q4: Explain the complete message structure for a multi-turn tool call interaction.**

A: After one tool call, the message history looks like:

```
messages = [
  {"role": "user", "content": "How many orders does customer 42 have?"},
  {
    "role": "assistant",
    "content": [
      {"type": "text", "text": "Let me look that up."},
      {"type": "tool_use", "id": "toolu_01", "name": "get_orders",
       "input": {"customer_id": 42}}
    ]
  },
  {
    "role": "user",
    "content": [
      {"type": "tool_result", "tool_use_id": "toolu_01",
       "content": [{"type": "text", "text": "[{...}, {...}, {...}]"}]}
    ]
  }
]
```

The tool result is sent as a `user` role message because it comes from outside the model. The `tool_use_id` links the result to its request. The SDK constructs and manages this structure automatically.

---

**Q5: What is the principle of least privilege in tool design and why does it matter for agents?**

A: Least privilege means giving each tool the minimum permissions necessary for its stated purpose. For tools: a file-reading tool should only access specific directories, not the entire filesystem; an email tool should only send to approved domains, not arbitrary addresses; a database tool should be read-only unless writes are specifically needed. It matters for agents because: (1) agents can call tools many times in a loop — a broad-permission tool called incorrectly 20 times causes 20x the damage; (2) prompt injection attacks that hijack the agent are limited to what the tools allow; (3) accidental errors (wrong parameters, model confusion) are bounded by the tool's scope.

---

**Q6: How does the order of tools in the `tools=[]` list affect agent behavior?**

A: For most agent SDKs and Claude specifically, the order of tools in the list has no effect on tool selection — Claude chooses tools based on their names and descriptions, not their position. However, order can matter for: (1) the token budget (all tool schemas are included in every API call, so more tools = more tokens); (2) schema clarity (similar tool names near each other in the prompt may confuse the model; space them with clear descriptions); (3) documentation and maintenance (consistent ordering helps code reviewers). There is no first-tool bias in the model's selection; selection is determined entirely by the goal and descriptions.

---

## Advanced Level

**Q7: How would you design tools for an agent that needs to work with both read and write database operations safely?**

A: Separate read and write operations into distinct tools with explicit scope:

```python
@tool
def query_database(sql: str) -> list[dict]:
    """Execute a read-only SQL SELECT query. No INSERT/UPDATE/DELETE allowed.
    Raises ValueError if query is not a SELECT statement."""
    sql_clean = sql.strip().upper()
    if not sql_clean.startswith("SELECT"):
        raise ValueError("Only SELECT queries allowed via this tool")
    return db.execute_readonly(sql)

@tool
def update_customer_status(
    customer_id: int, 
    new_status: str,
    reason: str
) -> dict:
    """Update a single customer's status. Allowed statuses: active, suspended, cancelled.
    Reason is required for audit trail. Returns updated record.
    IMPORTANT: This modifies production data. Only use after confirming with the user."""
    if new_status not in ["active", "suspended", "cancelled"]:
        raise ValueError(f"Invalid status: {new_status}")
    audit_log.write(customer_id, new_status, reason)
    return db.update_customer(customer_id, status=new_status)
```

Key design decisions: validate in the tool (not just in the system prompt), write tools explicitly mention they modify data, write tools are narrowly scoped (one record, specific fields), write tools log to an audit trail.

---

**Q8: What are the token cost implications of running many tool calls in a single agent session, and how do you optimize?**

A: Every API call includes the full tool schema list. For an agent with 10 tools, each tool schema averaging 150 tokens: 10 × 150 = 1,500 tokens per call, just for tool definitions. Over 20 agent steps: 30,000 tokens in tool schemas alone. Accumulated history adds more: each tool call + result pair adds ~500-2,000 tokens per step.

Optimization strategies:
1. **Fewer tools**: every unused tool is pure cost. Trim to the minimum set.
2. **Compact docstrings**: be concise without losing clarity. Cut examples from docstrings (test that you don't need them).
3. **Prompt caching**: tool schemas are static — mark them as cacheable. Anthropic's prompt caching reduces cost for repeated identical prefixes.
4. **Tool output truncation**: cap tool return values at a reasonable size (500-1000 tokens). Return summaries, not raw data.
5. **Context compression**: at step N, summarize the first N/2 steps and drop their raw content.

---

**Q9: Describe a scenario where tool execution order is critical and how you would enforce it in agent design.**

A: Consider a pipeline that: (1) reads a file, (2) validates its format, (3) uploads it. Steps must happen in order. If the agent skips validation and uploads a malformed file, the upload succeeds but the file is corrupt.

Enforcing order in agent design:
- **Tool chaining via return values**: validate() returns a validation token. upload() requires the token as a parameter — Claude can't call upload without first calling validate.
- **System prompt sequencing**: "Always validate before uploading. Never call upload_file without first calling validate_file on the same path."
- **Stateful tools**: a session state variable tracks which files are validated. upload() checks this state and raises an error if the file hasn't been validated.
- **Orchestrator-enforced pipeline**: use a fixed pipeline (not a free agent) for strictly ordered tasks — call validate(), then conditionally call upload() based on the result, rather than letting the model choose the order.

The best approach depends on how critical the ordering is: use stateful tools or an orchestrator for hard requirements, system prompt for soft guidance.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Tool patterns in code |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | Tool call internals |

⬅️ **Prev:** [Simple Agent](../03_Simple_Agent/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Multi-Step Reasoning](../05_Multi_Step_Reasoning/Theory.md)
