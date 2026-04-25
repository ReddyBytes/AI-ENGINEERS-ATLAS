# Project 08 — Multi-Tool Research Agent: Build Guide

## Overview

| Stage | What you build | Time estimate |
|---|---|---|
| 1 | Environment + tool implementations | 45 min |
| 2 | Tool schemas (Anthropic format) | 30 min |
| 3 | Single tool call round trip | 45 min |
| 4 | Full ReAct loop (multi-turn tool use) | 60 min |
| 5 | Conversation memory + CLI | 30 min |
| 6 | Testing and error handling | 30 min |

Total: approximately 4 hours

Read `01_MISSION.md` and `02_ARCHITECTURE.md` before starting.

---

## Stage 1 — Environment and Tool Implementations

### Step 1: Install dependencies

```bash
pip install anthropic duckduckgo-search wikipedia-api python-dotenv
```

`.env` file:
```
ANTHROPIC_API_KEY=sk-ant-...
```

### Step 2: Implement the web_search tool

`duckduckgo-search` provides a free, no-key-required web search API.

<details><summary>💡 Hint</summary>

Use `DDGS` as a context manager: `with DDGS() as ddgs: results = list(ddgs.text(query, max_results=max_results))`. Each result has keys `title`, `href`, and `body`. Format as a numbered list of strings and join them. Return "No results found." if empty.

</details>

<details><summary>✅ Answer</summary>

```python
from duckduckgo_search import DDGS

def web_search(query: str, max_results: int = 5) -> str:
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
    except Exception as e:
        return f"Search failed: {e}"

    if not results:
        return f"No results found for: '{query}'"

    lines = []
    for i, r in enumerate(results, start=1):
        lines.append(f"{i}. {r.get('title', 'No title')}")
        lines.append(f"   URL: {r.get('href', '')}")
        lines.append(f"   {r.get('body', '')}")
        lines.append("")
    return "\n".join(lines)
```

</details>

Test independently before wiring into the agent: `print(web_search("anthropic claude release date"))`.

**Theory connection:** Read `10_AI_Agents/03_Tool_Use/Theory.md` — specifically the section on tool output formatting. The tool output is injected back into the LLM context, so it needs to be readable text, not a Python dict.

### Step 3: Implement the wikipedia_summary tool

<details><summary>💡 Hint</summary>

Use `wikipediaapi.Wikipedia(language="en", user_agent="ResearchAgent/1.0 (...)")`. Call `wiki.page(topic)`. Check `page.exists()` before accessing content. Return `page.summary[:1500]` with a header line showing the article title.

</details>

<details><summary>✅ Answer</summary>

```python
import wikipediaapi

def wikipedia_summary(topic: str) -> str:
    wiki = wikipediaapi.Wikipedia(
        language="en",
        user_agent="ResearchAgent/1.0 (intermediate-ai-project)"
    )
    page = wiki.page(topic)
    if not page.exists():
        return f"No Wikipedia article found for '{topic}'."
    return f"Wikipedia — {page.title}\n\n{page.summary[:1500].strip()}"
```

</details>

### Step 4: Implement the calculator tool (safely)

**Do NOT use `eval()` directly.** Use Python's `ast` module to parse and evaluate only safe mathematical expressions.

<details><summary>💡 Hint</summary>

Parse the expression with `ast.parse(expression, mode="eval")` to get a tree. Then write a `_safe_eval_node(node)` function that handles only `ast.Constant` (return the number), `ast.BinOp` (recurse and apply the operator), and `ast.UnaryOp` (negate). For any other node type, raise `ValueError`. Keep a dict mapping AST operator types to Python `operator` functions.

</details>

<details><summary>✅ Answer</summary>

```python
import ast
import operator

_SAFE_OPERATORS = {
    ast.Add: operator.add, ast.Sub: operator.sub,
    ast.Mult: operator.mul, ast.Div: operator.truediv,
    ast.Pow: operator.pow, ast.Mod: operator.mod,
    ast.USub: operator.neg,
}

def _safe_eval_node(node) -> float:
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return float(node.value)
        raise ValueError(f"Non-numeric constant: {node.value!r}")
    elif isinstance(node, ast.BinOp):
        op = type(node.op)
        if op not in _SAFE_OPERATORS:
            raise ValueError(f"Operator not allowed: {op.__name__}")
        return _SAFE_OPERATORS[op](_safe_eval_node(node.left), _safe_eval_node(node.right))
    elif isinstance(node, ast.UnaryOp):
        if type(node.op) not in _SAFE_OPERATORS:
            raise ValueError(f"Unary operator not allowed")
        return _SAFE_OPERATORS[type(node.op)](_safe_eval_node(node.operand))
    else:
        raise ValueError(f"Expression type not allowed: {type(node).__name__}")

def calculator(expression: str) -> str:
    try:
        tree = ast.parse(expression.strip(), mode="eval")
        result = _safe_eval_node(tree.body)
        return str(result)
    except (ValueError, ZeroDivisionError, SyntaxError) as e:
        return f"Error: {e}"
```

</details>

Test with safe and unsafe inputs:
```python
print(calculator("100 * 1.07 ** 5"))       # compound interest
print(calculator("__import__('os')"))       # should fail safely
print(calculator("10 / 0"))                # division by zero
```

---

## Stage 2 — Tool Schemas (Anthropic Format)

### Step 5: Understand the tool schema structure

The Anthropic API requires tools to be defined as JSON schemas. Each tool needs:
- `name`: identifier (used in tool_use blocks)
- `description`: tells Claude WHEN to use this tool
- `input_schema`: JSON Schema for the parameters

Good descriptions matter. "Search the web" is weaker than "Search the web for current information, recent news, specific facts, or any topic where up-to-date information is needed."

### Step 6: Write the tool schemas

<details><summary>💡 Hint</summary>

Each tool schema is a dict with `name`, `description`, and `input_schema`. The `input_schema` follows JSON Schema — `type: object`, `properties: {param_name: {type: string, description: ...}}`, `required: [param_name]`.

</details>

<details><summary>✅ Answer</summary>

```python
TOOLS = [
    {
        "name": "web_search",
        "description": (
            "Search the web for current information, recent news, specific facts, "
            "company data, prices, events, or any topic where up-to-date or "
            "real-world information is needed. Returns top 5 results."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query. Be specific and include key terms.",
                }
            },
            "required": ["query"],
        },
    },
    {
        "name": "wikipedia_summary",
        "description": (
            "Get a factual summary from Wikipedia. Best for: background context, "
            "definitions, historical facts, biographical information, scientific "
            "concepts, and general overviews of well-established topics."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "The topic to look up."}
            },
            "required": ["topic"],
        },
    },
    {
        "name": "calculator",
        "description": (
            "Perform mathematical calculations accurately. Supports +, -, *, /, "
            "** (exponent), % (modulo). Use for any arithmetic to avoid approximation."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Math expression, e.g. '37.4 / 20.1'",
                }
            },
            "required": ["expression"],
        },
    },
]
```

</details>

---

## Stage 3 — Single Tool Call Round Trip

Before building the full loop, validate that a single tool call works end to end.

### Step 7: Make a request that triggers a tool call

```python
messages = [{"role": "user", "content": "What is the Wikipedia article about Python?"}]

response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    tools=TOOLS,
    messages=messages
)

print(f"Stop reason: {response.stop_reason}")
for block in response.content:
    print(f"Block type: {block.type}")
    if block.type == "tool_use":
        print(f"Tool: {block.name}, Input: {block.input}, ID: {block.id}")
```

When `stop_reason == "tool_use"`, the response contains tool call blocks.

### Step 8: Execute the tool and inject the result

<details><summary>💡 Hint</summary>

After getting a tool_use response:
1. Append `{"role": "assistant", "content": response.content}` to history — store the content list, not a string.
2. Execute the tool using `block.name` and `block.input`.
3. Append `{"role": "user", "content": [{"type": "tool_result", "tool_use_id": block.id, "content": result}]}` to history.
4. Make another API call with the updated history.

</details>

<details><summary>✅ Answer</summary>

```python
# Add assistant response (with tool_use block) to history
messages.append({"role": "assistant", "content": response.content})

# Execute the tool
tool_block = next(b for b in response.content if b.type == "tool_use")
result = wikipedia_summary(tool_block.input["topic"])

# Inject tool result — format is critical
messages.append({
    "role": "user",
    "content": [{"type": "tool_result", "tool_use_id": tool_block.id, "content": result}]
})

# Continue
response2 = client.messages.create(model="claude-opus-4-6", max_tokens=1024, tools=TOOLS, messages=messages)
print(response2.content[0].text)
```

</details>

**Theory connection:** Read `10_AI_Agents/02_ReAct_Pattern/Theory.md` — the tool_result injection is the "Observation" step in the ReAct pattern.

---

## Stage 4 — Full ReAct Loop

### Step 9: Build the agent loop

The key insight: keep calling the API and executing tools until `stop_reason == "end_turn"` (Claude produced a final answer) rather than `"tool_use"` (Claude wants another tool call).

<details><summary>💡 Hint</summary>

Write a `while tool_call_count < MAX_TOOL_CALLS_PER_TURN:` loop. Inside: call the API, append the assistant response to history. If `stop_reason == "end_turn"`, extract and return the text. If `stop_reason == "tool_use"`, loop over all tool_use blocks, execute each, collect tool_results, append them as a single user message, then continue the loop.

</details>

<details><summary>✅ Answer</summary>

```python
def run_agent_turn(user_message: str, conversation_history: list, verbose: bool = True) -> str:
    conversation_history.append({"role": "user", "content": user_message})
    tool_call_count = 0

    while tool_call_count < MAX_TOOL_CALLS_PER_TURN:
        response = client.messages.create(
            model=MODEL, max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT, tools=TOOLS,
            messages=conversation_history
        )
        conversation_history.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return "(no text response)"

        elif response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_call_count += 1
                    result = execute_tool(block.name, block.input)
                    if verbose:
                        print(f"  [Tool] {block.name}({block.input})")
                        print(f"  [Result] {result[:200]}...")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })
            conversation_history.append({"role": "user", "content": tool_results})
        else:
            return f"Unexpected stop_reason: {response.stop_reason}"

    return f"Research incomplete: reached maximum of {MAX_TOOL_CALLS_PER_TURN} tool calls."
```

</details>

### Step 10: Implement the tool dispatcher

<details><summary>💡 Hint</summary>

Route by `tool_name` string. Wrap the entire function in `try/except Exception as e: return str(e)` so tool failures never crash the agent.

</details>

<details><summary>✅ Answer</summary>

```python
def execute_tool(tool_name: str, tool_input: dict) -> str:
    try:
        if tool_name == "web_search":
            return web_search(tool_input["query"])
        elif tool_name == "wikipedia_summary":
            return wikipedia_summary(tool_input["topic"])
        elif tool_name == "calculator":
            return calculator(tool_input["expression"])
        else:
            return f"Unknown tool: {tool_name}"
    except Exception as e:
        return f"Tool error: {e}"
```

</details>

**Theory connection:** Read `10_AI_Agents/04_Agent_Memory/Theory.md`. The `conversation_history` list is the agent's working memory.

---

## Stage 5 — Conversation Memory and CLI

### Step 11: Persist history across user turns

The `conversation_history` list accumulates all messages across the session. On the next user turn, the full history is sent to Claude, so it can answer follow-up questions in context.

Implement the "last N turns" approach: if history exceeds a threshold, drop the oldest user/assistant pairs.

```python
def trim_history(conversation_history: list, max_turns: int = 20) -> None:
    while len(conversation_history) > max_turns * 4:
        conversation_history.pop(0)
        conversation_history.pop(0)
```

### Step 12: Write the main CLI loop

```python
def main():
    print("Research Agent — Tools: web_search | wikipedia_summary | calculator")
    print("Type 'quit' to exit, 'clear' to reset memory.\n")
    conversation_history = []

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye.")
            break
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            break
        if user_input.lower() == "clear":
            conversation_history = []
            print("Memory cleared.\n")
            continue

        trim_history(conversation_history)
        print("\nAgent thinking...\n")
        try:
            response = run_agent_turn(user_input, conversation_history)
            print(f"Agent: {response}\n")
        except Exception as e:
            print(f"Error: {e}\n")
```

---

## Stage 6 — Testing and Error Handling

### Step 13: Test multi-tool queries

These questions should trigger multiple tool calls:

1. "What is the GDP of Japan, and how does it compare to the GDP of Germany? What is the ratio?" — should call wikipedia_summary twice then calculator
2. "Who invented the transformer architecture and what institution were they at?" — should call web_search or wikipedia_summary
3. "If compound interest is 5% per year and I invest $1000, how much do I have after 10 years?" — should call calculator with `1000 * (1.05 ** 10)`

### Step 14: Handle tool errors gracefully

Wrap every tool call in a try/except so tool failures do not crash the agent. Claude can recover from a tool error — it will see the error message as an observation and may try a different approach.

### Step 15: Add a max_iterations guard

The `max_tool_calls=10` parameter in `run_agent_turn` provides this. Log a warning when the limit is hit.

---

## Checklist Before Moving On

- [ ] All three tools work independently before being wired into the agent
- [ ] Calculator rejects unsafe inputs (test with `__import__('os')`)
- [ ] Agent calls multiple tools in sequence for complex questions
- [ ] Tool results are correctly injected with matching `tool_use_id`
- [ ] Conversation history persists across user turns
- [ ] `clear` command resets memory
- [ ] Agent does not crash when a tool returns an error
- [ ] max_tool_calls guard prevents infinite loops

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [01_MISSION.md](./01_MISSION.md) | Context and goals |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design and diagrams |
| 03_GUIDE.md | you are here |
| [src/starter.py](./src/starter.py) | Runnable starter code |
| [04_RECAP.md](./04_RECAP.md) | What you built + next steps |

⬅️ **Prev:** [07 — Personal Knowledge Base RAG](../07_Personal_Knowledge_Base_RAG/01_MISSION.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [09 — Custom LoRA Fine-Tuning](../09_Custom_LoRA_Fine_Tuning/01_MISSION.md)
