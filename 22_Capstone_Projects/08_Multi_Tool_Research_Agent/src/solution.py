"""
Multi-Tool Research Agent — SOLUTION
======================================
A ReAct agent powered by Claude with web search, Wikipedia, and calculator tools.

Usage:
    python solution.py

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
MAX_TOOL_CALLS_PER_TURN = 10   # ← safety limit to prevent infinite loops
MAX_HISTORY_TURNS = 20          # ← max user/assistant pairs to keep in memory

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
        with DDGS() as ddgs:  # ← context manager handles session lifecycle
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

    Returns the summary text (first ~1500 characters) or a not-found message.
    """
    wiki = wikipediaapi.Wikipedia(
        language="en",
        user_agent="ResearchAgent/1.0 (intermediate-ai-project)"  # ← Wikipedia requires a user-agent
    )
    page = wiki.page(topic)

    if not page.exists():
        return f"No Wikipedia article found for '{topic}'. Try a different search term."

    summary = page.summary[:1500].strip()  # ← limit to 1500 chars to keep context manageable
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
        return _SAFE_OPERATORS[op_class](
            _safe_eval_node(node.left), _safe_eval_node(node.right)
        )
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
    """
    try:
        expression = expression.strip()
        tree = ast.parse(expression, mode="eval")  # ← parse into AST, mode="eval" for single expression
        result = _safe_eval_node(tree.body)         # ← recursively evaluate only safe node types
        return str(result)
    except SyntaxError as e:
        return f"Error: syntax error — {e}"
    except (ValueError, ZeroDivisionError) as e:
        return f"Error: {e}"


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

    Returns a string result. Never raises — exceptions are returned as error strings.
    """
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
        return f"Tool error ({tool_name}): {e}"  # ← never crash the agent loop


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
        # Call the API with current conversation state
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=conversation_history,
        )

        # CRITICAL: store response.content as-is (a list of content blocks)
        # The API validates message format and expects the original content structure
        conversation_history.append({
            "role": "assistant",
            "content": response.content,  # ← keep as list of blocks, NOT as string
        })

        if response.stop_reason == "end_turn":
            # Claude finished — find and return the text block
            for block in response.content:
                if hasattr(block, "text"):  # ← TextBlock has .text; ToolUseBlock does not
                    return block.text
            return "(no text response)"  # ← defensive fallback if no text block found

        elif response.stop_reason == "tool_use":
            tool_results = []

            for block in response.content:
                if block.type == "tool_use":
                    tool_call_count += 1

                    # Execute the tool
                    result = execute_tool(block.name, block.input)

                    if verbose:
                        print(f"  [Tool] {block.name}({block.input})")
                        print(f"  [Result] {result[:200]}...")  # ← truncate long results in console

                    # Collect tool results to send back as a single user message
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,  # ← MUST match block.id exactly (not block.name)
                        "content": result,
                    })

            # Inject all tool results as a single user message
            # This is the "Observation" step in the ReAct pattern
            conversation_history.append({"role": "user", "content": tool_results})

        else:
            return f"Unexpected stop_reason: {response.stop_reason}"

    return (
        f"Research incomplete: reached maximum of {MAX_TOOL_CALLS_PER_TURN} tool calls. "
        "Try rephrasing your question."
    )


# ---------------------------------------------------------------------------
# Memory management
# ---------------------------------------------------------------------------

def trim_history(conversation_history: list, max_turns: int = MAX_HISTORY_TURNS) -> None:
    """
    Remove oldest user/assistant turn pairs if history exceeds max_turns.

    Modifies conversation_history in place.
    """
    # Each "turn" generates multiple messages (user + assistant + tool_results + assistant...)
    # Using a conservative factor of 4 messages per logical turn
    while len(conversation_history) > max_turns * 4:
        conversation_history.pop(0)  # ← remove oldest user message
        conversation_history.pop(0)  # ← remove its paired assistant message


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

        trim_history(conversation_history)
        print("\nAgent thinking...\n")

        try:
            response_text = run_agent_turn(user_input, conversation_history, verbose=True)
            print(f"Agent: {response_text}\n")
        except Exception as e:
            print(f"Error: {e}\n")


# ---------------------------------------------------------------------------
# Demo / __main__ block
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Demonstrate all three tools work independently before running the agent
    print("=== Tool Smoke Tests ===\n")

    # Test calculator (no API needed)
    result = calculator("1000 * 1.05 ** 10")
    print(f"Calculator: 1000 * 1.05 ** 10 = {result}")

    unsafe = calculator("__import__('os').system('ls')")
    print(f"Calculator (unsafe): {unsafe}")  # ← should return Error:

    zero_div = calculator("10 / 0")
    print(f"Calculator (div zero): {zero_div}\n")   # ← should return Error:

    print("=== Starting Research Agent ===\n")
    main()


# ---------------------------------------------------------------------------
# Tests (run after implementing all TODOs)
# ---------------------------------------------------------------------------

def test_calculator_safety():
    assert "Error" in calculator("__import__('os').system('ls')")
    assert "Error" in calculator("1/0")
    result = calculator("10 * 5")
    assert "50" in result, f"Expected 50 in result, got: {result}"
    print("Calculator safety tests passed.")


def test_single_tool():
    # Ask the agent a simple math question
    history = []
    result = run_agent_turn("What is 237 times 456?", history, verbose=True)
    assert "108072" in result, f"Expected 108072 in: {result}"
    print("Single tool test passed.")
