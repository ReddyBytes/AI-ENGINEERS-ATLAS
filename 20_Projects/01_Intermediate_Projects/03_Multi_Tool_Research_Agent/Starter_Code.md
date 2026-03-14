# Project 3 — Multi-Tool Research Agent: Starter Code

## How to Use This File

Copy the code into `research_agent.py`. Implement every `# TODO:` block. The overall structure and tool implementations are mostly provided — your work is the ReAct loop mechanics and the glue code that connects everything.

---

## Setup

```bash
pip install anthropic duckduckgo-search wikipedia-api python-dotenv
```

`.env`:
```
ANTHROPIC_API_KEY=sk-ant-...
```

---

## `research_agent.py`

```python
"""
Multi-Tool Research Agent
=========================
A ReAct agent with web search, Wikipedia, and calculator tools.

Usage:
    python research_agent.py

Requirements:
    pip install anthropic duckduckgo-search wikipedia-api python-dotenv
"""

import ast
import operator
import os
from dotenv import load_dotenv
from anthropic import Anthropic
from duckduckgo_search import DDGS
import wikipediaapi

load_dotenv()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MODEL = "claude-opus-4-6"
MAX_TOKENS = 2048
MAX_TOOL_CALLS_PER_TURN = 10   # safety limit to prevent infinite loops
MAX_HISTORY_TURNS = 20          # max user/assistant pairs to keep in memory

SYSTEM_PROMPT = """You are a research assistant with access to three tools:
- web_search: for current information, news, and specific facts
- wikipedia_summary: for background knowledge and factual overviews
- calculator: for arithmetic and mathematical calculations

When answering, use tools to gather accurate information rather than relying
on your training data alone. Think step by step, gather the facts you need,
then provide a comprehensive, accurate answer.

Always cite where information came from (e.g., "According to Wikipedia..." or
"Web search results indicate...")."""

# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

def web_search(query: str, max_results: int = 5) -> str:
    """
    Search the web using DuckDuckGo. No API key required.

    Returns a formatted string of top results.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
    except Exception as e:
        return f"Search failed: {e}"

    if not results:
        return f"No results found for query: '{query}'"

    lines = []
    for i, r in enumerate(results, start=1):
        lines.append(f"{i}. {r.get('title', 'No title')}")
        lines.append(f"   URL: {r.get('href', 'No URL')}")
        lines.append(f"   {r.get('body', 'No snippet')}")
        lines.append("")
    return "\n".join(lines)


def wikipedia_summary(topic: str) -> str:
    """
    Fetch a Wikipedia summary for a topic.

    Returns the summary text (first ~1000 characters) or a not-found message.
    """
    wiki = wikipediaapi.Wikipedia(
        language="en",
        user_agent="ResearchAgent/1.0 (intermediate-ai-project)"
    )
    page = wiki.page(topic)

    if not page.exists():
        return f"No Wikipedia article found for '{topic}'. Try a different search term."

    summary = page.summary[:1500].strip()
    return f"Wikipedia — {page.title}\n\n{summary}"


# ---------------------------------------------------------------------------
# Safe calculator
# ---------------------------------------------------------------------------

_SAFE_OPERATORS = {
    ast.Add:  operator.add,
    ast.Sub:  operator.sub,
    ast.Mult: operator.mul,
    ast.Div:  operator.truediv,
    ast.Pow:  operator.pow,
    ast.Mod:  operator.mod,
    ast.USub: operator.neg,
}


def _safe_eval_node(node) -> float:
    """Recursively evaluate an AST node. Only allows numeric operations."""
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return float(node.value)
        raise ValueError(f"Non-numeric constant not allowed: {node.value!r}")
    elif isinstance(node, ast.BinOp):
        op_class = type(node.op)
        if op_class not in _SAFE_OPERATORS:
            raise ValueError(f"Operator not allowed: {op_class.__name__}")
        left = _safe_eval_node(node.left)
        right = _safe_eval_node(node.right)
        return _SAFE_OPERATORS[op_class](left, right)
    elif isinstance(node, ast.UnaryOp):
        if type(node.op) not in _SAFE_OPERATORS:
            raise ValueError(f"Unary operator not allowed: {type(node.op).__name__}")
        return _SAFE_OPERATORS[type(node.op)](_safe_eval_node(node.operand))
    else:
        raise ValueError(f"Expression type not allowed: {type(node).__name__}")


def calculator(expression: str) -> str:
    """
    Safely evaluate a mathematical expression.

    Allowed: +, -, *, /, ** (exponent), % (modulo), parentheses, numbers.
    NOT allowed: function calls, variables, string operations, imports.

    Returns the result as a string, or a descriptive error.
    """
    # TODO: Implement safe expression evaluation.
    #
    # Steps:
    #   1. Strip whitespace from expression.
    #   2. Call ast.parse(expression, mode="eval") to get the AST.
    #      Wrap in try/except SyntaxError to catch unparseable expressions.
    #   3. Call _safe_eval_node(tree.body) to evaluate.
    #      Wrap in try/except (ValueError, ZeroDivisionError) for runtime errors.
    #   4. Return str(result) on success, or f"Error: {e}" on failure.
    #
    # Test cases (implement these assertions after your function works):
    #   assert calculator("2 + 2") == "4.0"
    #   assert calculator("10 / 4") == "2.5"
    #   assert "Error" in calculator("__import__('os')")
    #   assert "Error" in calculator("10 / 0")
    pass


# ---------------------------------------------------------------------------
# Tool registry
# ---------------------------------------------------------------------------

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
                "topic": {
                    "type": "string",
                    "description": "The topic name to look up on Wikipedia.",
                }
            },
            "required": ["topic"],
        },
    },
    {
        "name": "calculator",
        "description": (
            "Perform mathematical calculations accurately. Supports: +, -, *, /, "
            "** (exponent), % (modulo), and parentheses. Use for any arithmetic "
            "to avoid rounding errors or approximation mistakes."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Math expression, e.g. '1000 * 1.05 ** 10' or '(150 + 200) / 2'",
                }
            },
            "required": ["expression"],
        },
    },
]


def execute_tool(tool_name: str, tool_input: dict) -> str:
    """
    Dispatch a tool call to the correct implementation.

    Args:
        tool_name: One of "web_search", "wikipedia_summary", "calculator".
        tool_input: Dict of arguments matching the tool's input_schema.

    Returns:
        String result from the tool.
    """
    # TODO: Route to the correct function based on tool_name.
    #       For web_search: call web_search(tool_input["query"])
    #       For wikipedia_summary: call wikipedia_summary(tool_input["topic"])
    #       For calculator: call calculator(tool_input["expression"])
    #       For unknown tools: return f"Unknown tool: {tool_name}"
    #       Wrap the entire function in try/except — return the error string,
    #       never let an exception propagate (the agent must continue running).
    pass


# ---------------------------------------------------------------------------
# Agent loop
# ---------------------------------------------------------------------------

client = Anthropic()


def run_agent_turn(
    user_message: str,
    conversation_history: list,
    verbose: bool = True,
) -> str:
    """
    Process one user turn through the full ReAct loop.

    The loop continues until Claude produces a final text response
    (stop_reason == "end_turn") or until max_tool_calls is reached.

    Args:
        user_message: The user's question or instruction.
        conversation_history: Running list of all messages. MODIFIED IN PLACE.
        verbose: If True, print tool calls and observations.

    Returns:
        Claude's final text response.
    """
    # Add user message to history
    conversation_history.append({
        "role": "user",
        "content": user_message,
    })

    tool_call_count = 0

    while tool_call_count < MAX_TOOL_CALLS_PER_TURN:
        # TODO: Call client.messages.create() with:
        #         model=MODEL
        #         max_tokens=MAX_TOKENS
        #         system=SYSTEM_PROMPT
        #         tools=TOOLS
        #         messages=conversation_history
        response = None  # replace with your API call

        # TODO: Add the assistant's response to conversation_history.
        #       IMPORTANT: response.content is a list of blocks (TextBlock, ToolUseBlock).
        #       You must store it as-is: {"role": "assistant", "content": response.content}
        #       Not as a string — as the actual content list.

        # Check stop reason
        if response.stop_reason == "end_turn":
            # TODO: Extract and return the text from the final response.
            #       Iterate over response.content blocks.
            #       Find the block where hasattr(block, "text") is True.
            #       Return block.text.
            #       If no text block found, return "(Agent produced no text response)"
            pass

        elif response.stop_reason == "tool_use":
            # TODO: Process all tool_use blocks in response.content.
            #
            # For EACH tool_use block (block.type == "tool_use"):
            #   1. Increment tool_call_count.
            #   2. Call execute_tool(block.name, block.input) to get the result.
            #   3. If verbose, print the tool name, input, and first 200 chars of result.
            #   4. Append to tool_results list:
            #      {
            #          "type": "tool_result",
            #          "tool_use_id": block.id,   # must match the tool_use block id
            #          "content": result,
            #      }
            #
            # After processing ALL tool calls in this response:
            #   Append a single user message to conversation_history:
            #   {"role": "user", "content": tool_results}
            #
            # The while loop then continues — Claude sees the results and decides
            # whether to call more tools or produce a final answer.

            tool_results = []

            for block in response.content:
                if block.type == "tool_use":
                    pass  # TODO: implement the logic described above

            # TODO: Append tool_results to conversation_history as a user message.
            pass

        else:
            return f"Unexpected stop_reason: {response.stop_reason}"

    # Reached max tool calls without end_turn
    return (
        f"Research incomplete: reached maximum of {MAX_TOOL_CALLS_PER_TURN} tool calls. "
        "The agent may have been in a loop. Try rephrasing your question."
    )


# ---------------------------------------------------------------------------
# Memory management
# ---------------------------------------------------------------------------

def trim_history(conversation_history: list, max_turns: int = MAX_HISTORY_TURNS) -> None:
    """
    Remove oldest user/assistant turn pairs if history exceeds max_turns.

    Modifies conversation_history in place.
    """
    # TODO: Count user+assistant pairs (each "turn" = 1 user message + 1 assistant message).
    #       If the number of turns exceeds max_turns, remove the oldest pairs from the front.
    #
    # Simple approach: count messages of role "user" that contain a string (not tool results).
    # For this project, a simpler heuristic is fine:
    #   while len(conversation_history) > max_turns * 4:  # rough estimate
    #       conversation_history.pop(0)
    #       conversation_history.pop(0)
    pass


# ---------------------------------------------------------------------------
# Main CLI
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("  Research Agent")
    print("  Tools: web_search | wikipedia_summary | calculator")
    print("=" * 60)
    print("Commands: 'quit' to exit, 'clear' to reset memory.\n")

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
            print("Goodbye.")
            break

        if user_input.lower() == "clear":
            conversation_history = []
            print("Memory cleared. Starting fresh.\n")
            continue

        # Trim history if needed
        trim_history(conversation_history)

        print("\nAgent thinking...\n")

        try:
            # TODO: Call run_agent_turn(user_input, conversation_history, verbose=True).
            #       Print the result with a "Agent: " prefix.
            #       Wrap in try/except to handle API errors gracefully.
            response_text = None  # replace with your call
            print(f"Agent: {response_text}\n")
        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    main()
```

---

## Testing Your Implementation

After completing all TODOs, run these manual tests:

### Test 1: Calculator safety
```python
assert "Error" in calculator("__import__('os').system('ls')")
assert "Error" in calculator("open('/etc/passwd').read()")
assert "Error" in calculator("1/0")
assert calculator("10 * 5") == "50.0"
print("Calculator safety tests passed.")
```

### Test 2: Single tool call
Ask the agent: "What is 237 times 456?"
Expected: agent calls `calculator("237 * 456")` once, returns 108072.

### Test 3: Multi-tool chaining
Ask: "What is the population of Tokyo divided by the population of Paris?"
Expected: agent calls wikipedia_summary (or web_search) for each city, then calculator.

### Test 4: Memory across turns
Ask: "Who invented the Transformer architecture?"
Then ask: "What university were they from?"
Expected: second answer uses context from first without re-searching.

### Test 5: Memory clear
After a multi-turn conversation, type `clear`.
Then ask a follow-up to the previous question.
Expected: agent no longer has previous context, may need to look it up again.

---

## Common Mistakes

**Storing response.content as a string**: You MUST store `response.content` (a list of blocks) directly, not `str(response.content)`. The API validates the message format and rejects strings where a content list is expected.

**tool_use_id mismatch**: The `tool_result` block's `tool_use_id` must exactly match the `id` field of the corresponding `tool_use` block. Copy it directly from `block.id` — do not reconstruct it.

**Forgetting to append tool_results**: After executing all tools, you must append a `{"role": "user", "content": tool_results}` message before the next API call. Without this, Claude never sees the tool outputs.

**Using eval() in calculator**: Always use the AST-based safe evaluator. `eval("__import__('os').system('rm -rf /')")` would execute that command on your machine.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [Project_Guide.md](./Project_Guide.md) | What you'll build |
| [Step_by_Step.md](./Step_by_Step.md) | Build instructions |
| Starter_Code.md | ← you are here |
| [Architecture_Blueprint.md](./Architecture_Blueprint.md) | System diagram |

⬅️ **Prev:** [02 — Personal Knowledge Base RAG](../02_Personal_Knowledge_Base_RAG/Project_Guide.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 — Custom LoRA Fine-Tuning](../04_Custom_LoRA_Fine_Tuning/Project_Guide.md)
