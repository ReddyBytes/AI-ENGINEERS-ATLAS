# Multi-Step Reasoning — Code Example

## Basic Chained Tool Calls

```python
"""
Multi-step reasoning: task decomposition via chained tool calls.
"""
from claude_agent_sdk import Agent, tool
from datetime import datetime
import json


# ── TOOLS FOR A SALES DATA AGENT ─────────────────────────────

# Simulated sales database
SALES_DATA = {
    "Q1": {"Product_A": 45200, "Product_B": 38100, "Product_C": 29400},
    "Q2": {"Product_A": 51800, "Product_B": 35600, "Product_C": 33200},
    "Q3": {"Product_A": 48900, "Product_B": 41200, "Product_C": 37800},
    "Q4": {"Product_A": 62100, "Product_B": 39400, "Product_C": 44100},
}

@tool
def get_top_products(quarter: str, limit: int = 3) -> list[str]:
    """Get the top N products by sales in a specific quarter.
    quarter: 'Q1', 'Q2', 'Q3', or 'Q4'.
    limit: how many top products to return (default 3).
    Returns a list of product names ordered by descending revenue."""
    if quarter not in SALES_DATA:
        raise ValueError(f"Quarter must be Q1-Q4, got: {quarter}")
    quarter_data = SALES_DATA[quarter]
    sorted_products = sorted(quarter_data.keys(), 
                            key=lambda p: quarter_data[p], reverse=True)
    return sorted_products[:limit]

@tool
def get_sales(product: str, quarters: list[str]) -> dict:
    """Get sales figures for a product across specified quarters.
    product: product name (e.g., 'Product_A').
    quarters: list of quarters, e.g., ['Q3', 'Q4'].
    Returns dict of {quarter: revenue} pairs."""
    result = {}
    for q in quarters:
        if q not in SALES_DATA:
            raise ValueError(f"Invalid quarter: {q}")
        if product not in SALES_DATA[q]:
            raise KeyError(f"Product '{product}' not found in {q}")
        result[q] = SALES_DATA[q][product]
    return result

@tool
def compute_growth(value_before: float, value_after: float) -> dict:
    """Compute the growth/decline between two values.
    Returns: absolute_change, percentage_change (positive = growth).
    Example: compute_growth(100, 120) → {absolute_change: 20, percentage_change: 20.0}"""
    absolute = value_after - value_before
    if value_before == 0:
        return {"absolute_change": absolute, "percentage_change": None}
    percentage = round((absolute / value_before) * 100, 1)
    return {"absolute_change": absolute, "percentage_change": percentage}

@tool  
def format_as_table(headers: list[str], rows: list[list]) -> str:
    """Format data as a Markdown table.
    headers: column header names.
    rows: list of rows, each row is a list of values.
    Returns a formatted Markdown table string."""
    header_row = "| " + " | ".join(str(h) for h in headers) + " |"
    separator = "| " + " | ".join("---" for _ in headers) + " |"
    data_rows = ["| " + " | ".join(str(v) for v in row) + " |" for row in rows]
    return "\n".join([header_row, separator] + data_rows)


# ── MULTI-STEP SALES ANALYSIS AGENT ──────────────────────────

system_prompt = """You are a sales analytics assistant.

When asked to compare quarters:
1. Get the top products for each quarter
2. Get sales figures for each product in both quarters
3. Compute the growth/decline for each product
4. Format the results as a table

Work through these steps systematically using the tools."""

agent = Agent(
    model="claude-sonnet-4-6",
    tools=[get_top_products, get_sales, compute_growth, format_as_table],
    system=system_prompt,
    max_steps=20
)

if __name__ == "__main__":
    result = agent.run(
        "Compare sales for the top 3 products in Q3 vs Q4. "
        "Show the absolute change and percentage change for each."
    )
    print(result)
    # Claude will:
    # 1. get_top_products("Q4", 3) → [Product_A, Product_C, Product_D]
    # 2. get_sales("Product_A", ["Q3", "Q4"]) → {Q3: 48900, Q4: 62100}
    # 3. get_sales("Product_B", ["Q3", "Q4"]) → {Q3: 41200, Q4: 39400}
    # 4. get_sales("Product_C", ["Q3", "Q4"]) → {Q3: 37800, Q4: 44100}
    # 5. compute_growth(48900, 62100) → {+13200, +27.0%}
    # 6. compute_growth(41200, 39400) → {-1800, -4.4%}
    # 7. compute_growth(37800, 44100) → {+6300, +16.7%}
    # 8. format_as_table(headers, rows) → markdown table
    # Final: structured comparison table
```

---

## Planning Before Acting

```python
"""
Explicit planning: force the agent to think before calling tools.
"""
from claude_agent_sdk import Agent, tool

@tool
def list_files_in_dir(directory: str) -> list[str]:
    """List all files in a directory. Returns list of filenames."""
    import os
    try:
        return os.listdir(directory)
    except FileNotFoundError:
        raise FileNotFoundError(f"Directory not found: {directory}")

@tool
def read_file_contents(path: str) -> str:
    """Read the contents of a text file. Returns file contents as string."""
    from pathlib import Path
    return Path(path).read_text()

@tool
def count_word_in_file(file_path: str, word: str) -> dict:
    """Count occurrences of a word in a file (case-insensitive).
    Returns: {word, count, file_path}"""
    from pathlib import Path
    content = Path(file_path).read_text().lower()
    count = content.split().count(word.lower())
    return {"word": word, "count": count, "file_path": file_path}

# System prompt that encourages planning
planning_system = """You are a file analysis assistant.

IMPORTANT: Before calling any tools, always write out your plan:
1. What information do I need?
2. Which tools will I call and in what order?
3. What does each step depend on?

Then execute your plan step by step.
Only move to the next step after seeing the result of the current one."""

planning_agent = Agent(
    model="claude-sonnet-4-6",
    tools=[list_files_in_dir, read_file_contents, count_word_in_file],
    system=planning_system,
    max_steps=15
)

if __name__ == "__main__":
    # The agent will first write out a plan, then execute it
    result = planning_agent.run(
        "In the /tmp/docs directory, find all .txt files "
        "and tell me how many times the word 'error' appears in each one."
    )
    print(result)
    # Expected plan output before tool calls:
    # "Plan: 1) list_files_in_dir('/tmp/docs') to find .txt files
    #        2) For each .txt file: count_word_in_file(path, 'error')
    #        3) Compile results into a summary"
```

---

## Iterative Refinement Loop

```python
"""
Iterative refinement: agent loops until it achieves a quality threshold.
"""
from claude_agent_sdk import Agent, tool

@tool
def evaluate_quality(text: str, criteria: list[str]) -> dict:
    """Evaluate text quality against a list of criteria.
    Returns: {score: 0-10, passed: bool, feedback: list[str]}
    score < 7 means the text needs improvement."""
    # Simplified quality check (in production: LLM-as-judge)
    score = 0
    feedback = []
    
    for criterion in criteria:
        if criterion == "length" and len(text.split()) >= 50:
            score += 3
        elif criterion == "length":
            feedback.append("Text is too short (need 50+ words)")
        
        if criterion == "has_examples" and ("for example" in text.lower() or "e.g." in text.lower()):
            score += 3
        elif criterion == "has_examples":
            feedback.append("Text needs at least one example")
        
        if criterion == "clear_conclusion" and ("in summary" in text.lower() or "therefore" in text.lower()):
            score += 4
        elif criterion == "clear_conclusion":
            feedback.append("Text needs a clear conclusion")
    
    return {"score": min(score, 10), "passed": score >= 7, "feedback": feedback}

@tool
def improve_text(text: str, feedback: list[str]) -> str:
    """Placeholder: in production this would call a writing improvement API.
    For demonstration, adds example improvements based on feedback."""
    improvements = []
    if any("short" in f.lower() for f in feedback):
        text += " [Additional context and explanation added here to meet length requirements.]"
    if any("example" in f.lower() for f in feedback):
        text += " For example, this demonstrates the concept clearly."
    if any("conclusion" in f.lower() for f in feedback):
        text += " In summary, these points illustrate the key ideas."
    return text

iterative_agent = Agent(
    model="claude-sonnet-4-6",
    tools=[evaluate_quality, improve_text],
    system="""You are a writing quality assurance agent.

When given a piece of text:
1. Evaluate it against the criteria
2. If it passes (score >= 7), return it with a pass confirmation
3. If it fails, improve it based on the feedback and evaluate again
4. Repeat until it passes or you've made 3 improvement attempts

Always show the score and what was improved.""",
    max_steps=12
)

if __name__ == "__main__":
    draft = "Agents are AI systems that use tools."
    
    result = iterative_agent.run(
        f"Evaluate and improve this text until it meets all quality criteria: "
        f"'{draft}'\n\n"
        f"Criteria to meet: ['length', 'has_examples', 'clear_conclusion']"
    )
    print(result)
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

⬅️ **Prev:** [Tool Calling in Agents](../04_Tool_Calling_in_Agents/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Agent Memory](../06_Agent_Memory/Theory.md)
