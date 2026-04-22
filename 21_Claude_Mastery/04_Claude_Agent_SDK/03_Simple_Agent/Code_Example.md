# Simple Agent — Code Example

## Complete Minimal Working Agent

```python
"""
Minimal working Claude agent with one tool.
Shows the complete @tool + Agent.run() pattern.
"""
from claude_agent_sdk import Agent, tool


# ── DEFINE TOOLS ──────────────────────────────────────────────

@tool
def count_words(text: str) -> int:
    """Count the number of words in a text string.
    Returns an integer word count. Splits on whitespace."""
    return len(text.split())


@tool
def reverse_text(text: str) -> str:
    """Reverse a text string character by character.
    Returns the reversed string. Works on any UTF-8 text."""
    return text[::-1]


@tool
def to_uppercase(text: str) -> str:
    """Convert text to uppercase.
    Returns the same text with all letters capitalized."""
    return text.upper()


# ── CREATE AGENT ──────────────────────────────────────────────

agent = Agent(
    model="claude-sonnet-4-6",
    tools=[count_words, reverse_text, to_uppercase],
    system="""You are a text analysis assistant.
    Use the available tools to answer questions about text.
    Always use a tool to compute the answer — don't guess.""",
    max_steps=10
)


# ── RUN THE AGENT ─────────────────────────────────────────────

if __name__ == "__main__":
    # Example 1: single tool call
    result = agent.run("How many words are in 'The quick brown fox'?")
    print(result)
    # → "The sentence 'The quick brown fox' contains 4 words."

    # Example 2: multi-step (two tool calls)
    result = agent.run(
        "Take the phrase 'hello world', reverse it, "
        "then tell me how many characters the result has."
    )
    print(result)
    # → Claude calls reverse_text("hello world") → "dlrow olleh"
    # → Claude calls count_words or counts manually
    # → Returns: "'dlrow olleh' has 11 characters (5 + space + 5)"

    # Example 3: task with no tool needed
    result = agent.run("What is 2 + 2?")
    print(result)
    # → Claude answers directly: "4" (no tool call needed)
```

---

## Adding Step-by-Step Logging

```python
from claude_agent_sdk import Agent, tool, AgentStep

@tool
def add(a: float, b: float) -> float:
    """Add two numbers together. Returns the sum."""
    return a + b

@tool
def multiply(a: float, b: float) -> float:
    """Multiply two numbers together. Returns the product."""
    return a * b

# Callback called after each loop iteration
def log_step(step: AgentStep):
    step_num = step.number
    if step.tool_call:
        print(f"  Step {step_num}: Called {step.tool_call.name}({step.tool_call.input})")
        print(f"           Result: {step.tool_call.result}")
    else:
        print(f"  Step {step_num}: Final answer produced")

agent = Agent(
    model="claude-sonnet-4-6",
    tools=[add, multiply],
    system="You are a math assistant. Use tools to compute answers.",
    on_step=log_step
)

print("Running: (4 + 7) × 3")
result = agent.run("What is (4 + 7) times 3?")
print(f"\nAnswer: {result}")

# Output:
#   Step 1: Called add({"a": 4, "b": 7})
#            Result: 11
#   Step 2: Called multiply({"a": 11, "b": 3})
#            Result: 33
#   Step 3: Final answer produced
#
# Answer: (4 + 7) × 3 = 11 × 3 = 33
```

---

## Error Handling

```python
from claude_agent_sdk import Agent, tool, AgentError, AgentMaxStepsError

@tool
def divide(a: float, b: float) -> float:
    """Divide a by b. Raises ZeroDivisionError if b is 0."""
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return a / b

agent = Agent(
    model="claude-sonnet-4-6",
    tools=[divide],
    system="You are a math assistant.",
    max_steps=5
)

# The agent handles tool errors automatically:
result = agent.run("What is 10 divided by 0?")
print(result)
# Claude sees: "Tool error: ZeroDivisionError: Cannot divide by zero"
# Claude responds: "I can't divide 10 by 0 — division by zero is undefined in mathematics."

# Catching SDK-level errors:
try:
    result = agent.run(
        "Keep adding 1 to 0 until you reach 1000 (show all steps)"
    )
except AgentMaxStepsError:
    print("Agent hit max steps — goal was too large for the step limit")
except AgentError as e:
    print(f"Agent failed: {e}")
```

---

## Agent with External Data Source

```python
import json
from claude_agent_sdk import Agent, tool

# Simulated product database
PRODUCTS = {
    "prod_001": {"name": "Widget A", "price": 9.99, "stock": 150},
    "prod_002": {"name": "Widget B", "price": 24.99, "stock": 0},
    "prod_003": {"name": "Gadget X", "price": 49.99, "stock": 23},
}

@tool
def search_products(query: str) -> list[dict]:
    """Search products by name. Returns list of matching products with id, name, price, stock.
    Returns empty list if no matches. Case-insensitive search."""
    results = []
    query_lower = query.lower()
    for pid, product in PRODUCTS.items():
        if query_lower in product["name"].lower():
            results.append({"id": pid, **product})
    return results

@tool
def get_product_details(product_id: str) -> dict:
    """Get full details for a product by its ID.
    Returns product dict with name, price, stock.
    Raises KeyError if product_id not found."""
    if product_id not in PRODUCTS:
        raise KeyError(f"Product {product_id} not found")
    return {"id": product_id, **PRODUCTS[product_id]}

@tool
def check_availability(product_id: str) -> dict:
    """Check if a product is in stock. Returns status and quantity.
    Status is 'available' or 'out_of_stock'."""
    if product_id not in PRODUCTS:
        raise KeyError(f"Product {product_id} not found")
    stock = PRODUCTS[product_id]["stock"]
    return {
        "product_id": product_id,
        "status": "available" if stock > 0 else "out_of_stock",
        "quantity": stock
    }

agent = Agent(
    model="claude-sonnet-4-6",
    tools=[search_products, get_product_details, check_availability],
    system="""You are a product catalog assistant.
    Help customers find products and check availability.
    Always verify stock before confirming availability."""
)

# Multi-step: search → check availability → answer
result = agent.run("Is Widget B currently in stock? How much does it cost?")
print(result)
# → Claude calls search_products("Widget B") → [{"id": "prod_002", ...}]
# → Claude calls check_availability("prod_002") → {"status": "out_of_stock", "quantity": 0}
# → "Widget B costs $24.99 but is currently out of stock."
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [Why Agent SDK?](../02_Why_Agent_SDK/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Tool Calling in Agents](../04_Tool_Calling_in_Agents/Theory.md)
