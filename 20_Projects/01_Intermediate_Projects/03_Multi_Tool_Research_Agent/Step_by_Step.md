# Project 3 — Multi-Tool Research Agent: Step-by-Step Guide

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

`duckduckgo-search` provides a free, no-key-required web search API:

```python
from duckduckgo_search import DDGS

def web_search(query: str, max_results: int = 5) -> str:
    """
    Search the web using DuckDuckGo. Returns a formatted string of results.
    """
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=max_results))

    if not results:
        return "No results found."

    output = []
    for i, r in enumerate(results, start=1):
        output.append(f"{i}. {r['title']}\n   URL: {r['href']}\n   {r['body']}")
    return "\n\n".join(output)
```

Test this independently before wiring it into the agent:
```python
print(web_search("anthropic claude 3 release date"))
```

**Theory connection:** Read `10_AI_Agents/03_Tool_Use/Theory.md` — specifically the section on tool output formatting. The tool output is injected back into the LLM context, so it needs to be readable text, not a Python dict.

### Step 3: Implement the wikipedia_summary tool

```python
import wikipediaapi

def wikipedia_summary(topic: str) -> str:
    """
    Fetch the Wikipedia summary for a topic. Returns the first two paragraphs.
    """
    wiki = wikipediaapi.Wikipedia(
        language="en",
        user_agent="ResearchAgent/1.0 (educational project)"
    )
    page = wiki.page(topic)

    if not page.exists():
        return f"No Wikipedia article found for '{topic}'."

    # Return summary (first section) truncated to 1000 chars
    summary = page.summary[:1000]
    return f"Wikipedia: {page.title}\n\n{summary}"
```

Test:
```python
print(wikipedia_summary("Transformer (machine learning model)"))
```

### Step 4: Implement the calculator tool (safely)

**Do NOT use `eval()` directly.** Instead, use Python's `ast` module to parse and evaluate only safe mathematical expressions:

```python
import ast
import operator

# Safe operators allowed in expressions
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
}

def safe_eval(node):
    """Recursively evaluate an AST node using only safe operations."""
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Unsafe constant: {node.value}")
    elif isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in SAFE_OPERATORS:
            raise ValueError(f"Unsafe operator: {op_type}")
        left = safe_eval(node.left)
        right = safe_eval(node.right)
        return SAFE_OPERATORS[op_type](left, right)
    elif isinstance(node, ast.UnaryOp):
        if type(node.op) not in SAFE_OPERATORS:
            raise ValueError(f"Unsafe unary operator")
        return SAFE_OPERATORS[type(node.op)](safe_eval(node.operand))
    else:
        raise ValueError(f"Unsupported node type: {type(node)}")


def calculator(expression: str) -> str:
    """
    Safely evaluate a mathematical expression.

    Args:
        expression: A math expression string, e.g. "37.4 / 20.1" or "(100 + 50) * 2"

    Returns:
        The result as a string, or an error message.
    """
    try:
        tree = ast.parse(expression, mode="eval")
        result = safe_eval(tree.body)
        return str(result)
    except (ValueError, ZeroDivisionError, SyntaxError) as e:
        return f"Error: {e}"
```

Test with safe and unsafe inputs:
```python
print(calculator("100 * 1.07 ** 5"))      # compound interest
print(calculator("__import__('os')"))      # should fail safely
print(calculator("10 / 0"))               # division by zero
```

---

## Stage 2 — Tool Schemas (Anthropic Format)

### Step 5: Understand the tool schema structure

Read `10_AI_Agents/03_Tool_Use/Theory.md`. The Anthropic API requires tools to be defined as JSON schemas. Each tool needs:

- `name`: identifier (used in tool_use blocks)
- `description`: tells Claude WHEN to use this tool
- `input_schema`: JSON Schema for the parameters

Good descriptions matter. "Search the web" is weaker than "Search the web for current information, recent news, specific facts, or any topic where up-to-date information is needed." Claude uses the description to decide whether to call the tool.

### Step 6: Write the tool schemas

```python
TOOLS = [
    {
        "name": "web_search",
        "description": (
            "Search the web for current information, recent news, specific facts, "
            "prices, events, or any topic where up-to-date information is needed. "
            "Returns the top 5 search results with titles, URLs, and snippets."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query. Be specific for better results.",
                }
            },
            "required": ["query"],
        },
    },
    {
        "name": "wikipedia_summary",
        "description": (
            "Get a factual summary of a topic from Wikipedia. Best for: background "
            "information, definitions, historical facts, biographical information, "
            "and general overviews of established topics."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "The topic to look up on Wikipedia.",
                }
            },
            "required": ["topic"],
        },
    },
    {
        "name": "calculator",
        "description": (
            "Perform mathematical calculations. Supports +, -, *, /, ** (exponent), "
            "% (modulo). Use this for any arithmetic you need to perform accurately."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "A mathematical expression, e.g. '37.4 / 20.1' or '(100 + 50) * 2'",
                }
            },
            "required": ["expression"],
        },
    },
]
```

---

## Stage 3 — Single Tool Call Round Trip

Before building the full loop, validate that a single tool call works end to end.

### Step 7: Make a request that triggers a tool call

```python
import anthropic
import json

client = anthropic.Anthropic()

messages = [
    {"role": "user", "content": "What is the Wikipedia article about Python programming language?"}
]

response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    tools=TOOLS,
    messages=messages
)

print(f"Stop reason: {response.stop_reason}")
print(f"Content: {response.content}")
```

When `stop_reason == "tool_use"`, the response contains tool call blocks. Inspect them:

```python
for block in response.content:
    print(f"Block type: {block.type}")
    if block.type == "tool_use":
        print(f"Tool: {block.name}")
        print(f"Input: {block.input}")
        print(f"ID: {block.id}")
```

### Step 8: Execute the tool and inject the result

After extracting the tool call, execute the tool, then add both the assistant's response and the tool result to the conversation:

```python
# Add assistant's response (with tool_use block) to history
messages.append({"role": "assistant", "content": response.content})

# Execute the tool
tool_block = next(b for b in response.content if b.type == "tool_use")
result = wikipedia_summary(tool_block.input["topic"])

# Add tool result to history — FORMAT IS CRITICAL
messages.append({
    "role": "user",
    "content": [
        {
            "type": "tool_result",
            "tool_use_id": tool_block.id,  # must match the tool_use block's id
            "content": result,
        }
    ]
})

# Continue the conversation
response2 = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    tools=TOOLS,
    messages=messages
)
print(response2.content[0].text)
```

**Theory connection:** Read `10_AI_Agents/02_ReAct_Pattern/Theory.md` — the tool_result injection is the "Observation" step in the ReAct pattern.

---

## Stage 4 — Full ReAct Loop

### Step 9: Build the agent loop

The key insight: keep calling the API and executing tools until `stop_reason == "end_turn"` (Claude produced a final answer) rather than `"tool_use"` (Claude wants another tool call).

```python
def run_agent_turn(
    user_message: str,
    conversation_history: list,
    max_tool_calls: int = 10,
) -> str:
    """
    Run one user turn through the agent loop.

    Returns the agent's final text response.
    """
    # Add user message to history
    conversation_history.append({
        "role": "user",
        "content": user_message
    })

    tool_call_count = 0

    while tool_call_count < max_tool_calls:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=conversation_history
        )

        # Add assistant response to history
        conversation_history.append({
            "role": "assistant",
            "content": response.content
        })

        if response.stop_reason == "end_turn":
            # Extract the final text response
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return "(no text response)"

        elif response.stop_reason == "tool_use":
            # Execute all tool calls in this response
            tool_results = []

            for block in response.content:
                if block.type == "tool_use":
                    tool_call_count += 1
                    result = execute_tool(block.name, block.input)

                    print(f"  [Tool call] {block.name}({block.input})")
                    print(f"  [Result] {result[:200]}...")

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

            # Inject all tool results as a single user message
            conversation_history.append({
                "role": "user",
                "content": tool_results
            })

        else:
            return f"Unexpected stop reason: {response.stop_reason}"

    return "Maximum tool calls reached. Partial research complete."
```

### Step 10: Implement the tool dispatcher

```python
def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Route a tool call to the correct implementation."""
    if tool_name == "web_search":
        return web_search(tool_input["query"])
    elif tool_name == "wikipedia_summary":
        return wikipedia_summary(tool_input["topic"])
    elif tool_name == "calculator":
        return calculator(tool_input["expression"])
    else:
        return f"Unknown tool: {tool_name}"
```

**Theory connection:** Read `10_AI_Agents/04_Agent_Memory/Theory.md`. The `conversation_history` list is the agent's working memory — it holds everything the agent has seen and done in this session.

---

## Stage 5 — Conversation Memory and CLI

### Step 11: Persist history across user turns

The `conversation_history` list accumulates all messages across the session. On the next user turn, the full history is sent to Claude, so it can answer follow-up questions in context.

Design decision: where does memory end? Options:
- Never truncate (simple, but eventually hits context limit)
- Truncate to last N turns
- Summarize old context with Claude

For this project, implement the "last N turns" approach: if history exceeds a threshold, drop the oldest user/assistant pairs (never drop the system prompt).

### Step 12: Write the main CLI loop

```python
def main():
    print("Research Agent (powered by Claude + Tools)")
    print("Tools: web_search, wikipedia_summary, calculator")
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
        if user_input.lower() in ("quit", "exit"):
            break
        if user_input.lower() == "clear":
            conversation_history = []
            print("Memory cleared.\n")
            continue

        print("\nAgent thinking...")
        response = run_agent_turn(user_input, conversation_history)
        print(f"\nAgent: {response}\n")
```

---

## Stage 6 — Testing and Error Handling

### Step 13: Test multi-tool queries

These questions should trigger multiple tool calls:

1. "What is the GDP of Japan, and how does it compare to the GDP of Germany? What is the ratio?"
   - Should call wikipedia_summary twice (or web_search), then calculator

2. "Who invented the transformer architecture and what institution were they at?"
   - Should call web_search or wikipedia_summary

3. "If compound interest is 5% per year and I invest $1000, how much do I have after 10 years?"
   - Should call calculator with `1000 * (1.05 ** 10)`

### Step 14: Handle tool errors gracefully

Wrap every tool call in a try/except so tool failures do not crash the agent:

```python
try:
    result = execute_tool(block.name, block.input)
except Exception as e:
    result = f"Tool error: {str(e)}"
```

Claude can recover from a tool error — it will see the error message as an observation and may try a different approach.

### Step 15: Add a max_iterations guard

Without a limit, a buggy agent could loop forever. The `max_tool_calls=10` parameter in `run_agent_turn` provides this. Log a warning when the limit is hit.

---

## Extension Challenges

1. **Add a file_reader tool**: Given a file path, read and return the content. Useful for agents that need to analyze local documents.

2. **Tool use logging**: Save every tool call (name, input, output, timestamp) to a JSONL file. This creates an audit trail for what the agent did.

3. **Streaming output**: Use the Anthropic streaming API to display Claude's reasoning in real time rather than waiting for the full response.

4. **Multi-agent**: Create a "researcher" agent and a "writer" agent. The researcher uses tools to gather information, the writer takes that information and formats a polished report.

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
| [Project_Guide.md](./Project_Guide.md) | What you'll build |
| Step_by_Step.md | ← you are here |
| [Starter_Code.md](./Starter_Code.md) | Code with TODOs |
| [Architecture_Blueprint.md](./Architecture_Blueprint.md) | System diagram |

⬅️ **Prev:** [02 — Personal Knowledge Base RAG](../02_Personal_Knowledge_Base_RAG/Project_Guide.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 — Custom LoRA Fine-Tuning](../04_Custom_LoRA_Fine_Tuning/Project_Guide.md)
