# ReAct Pattern — Code Example

A simple ReAct agent using LangChain with two tools: a calculator and a search tool.

This example shows the full Thought → Action → Observation trace.

---

## Setup

```bash
pip install langchain langchain-openai langchain-community duckduckgo-search
```

```python
import os
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.callbacks import StdOutCallbackHandler

# Use any OpenAI-compatible model
# For Claude, use langchain_anthropic
os.environ["OPENAI_API_KEY"] = "your-key-here"
```

---

## Define the Tools

```python
from langchain.tools import DuckDuckGoSearchRun
import math

# Tool 1: Web Search
search = DuckDuckGoSearchRun()
search_tool = Tool(
    name="search",
    func=search.run,
    description=(
        "Useful for finding current information on the internet. "
        "Input should be a clear search query as a string."
    )
)

# Tool 2: Calculator
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression and return the result."""
    try:
        # Safe evaluation — only allow math operations
        allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith("_")}
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

calculator_tool = Tool(
    name="calculator",
    func=calculate,
    description=(
        "Useful for math calculations. "
        "Input should be a valid Python math expression like '81 ** 2' or 'math.sqrt(144)'. "
        "Always use this instead of computing math in your head."
    )
)

tools = [search_tool, calculator_tool]
```

---

## Create the ReAct Agent

```python
llm = ChatOpenAI(model="gpt-4o", temperature=0)

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,  # This is the ReAct agent type
    verbose=True,       # Shows the full Thought/Action/Observation trace
    max_iterations=5,   # Safety limit — stop after 5 loops
    handle_parsing_errors=True,
)
```

---

## Run the Agent and See the Trace

```python
# Question that requires BOTH search AND calculation
question = """
What year was Python programming language created?
Calculate how many years ago that was (current year is 2024),
then square that number.
"""

result = agent.invoke({"input": question})
print("\n=== FINAL ANSWER ===")
print(result["output"])
```

---

## Example Output (What You'll See)

```
> Entering new AgentExecutor chain...

Thought: I need to find out what year Python was created. I'll search for this.
Action: search
Action Input: Python programming language creation year
Observation: Python was created by Guido van Rossum and first released in 1991.

Thought: Python was created in 1991. Current year is 2024.
So years ago = 2024 - 1991 = 33 years.
Now I need to square 33. I'll use the calculator.
Action: calculator
Action Input: 33 ** 2
Observation: 1089

Thought: Python was created 33 years ago (1991 to 2024). 33 squared is 1089.
I have all the information needed to answer.
Final Answer: Python was created in 1991 by Guido van Rossum.
That was 33 years ago (as of 2024). 33 squared is 1,089.

> Finished chain.

=== FINAL ANSWER ===
Python was created in 1991 by Guido van Rossum.
That was 33 years ago (as of 2024). 33 squared is 1,089.
```

---

## Reading the Trace

The trace shows you exactly how the agent reasoned:

1. **Thought** — agent decides it needs to search
2. **Action** — calls the search tool
3. **Observation** — search returns a result
4. **Thought** — agent reads the result, now knows the year, does mental prep for the calculation
5. **Action** — calls the calculator tool
6. **Observation** — calculator returns the result
7. **Thought** — agent confirms it has everything needed
8. **Final Answer** — complete response

This is the ReAct pattern in action.

---

## Second Example: Pure Calculation (No Search Needed)

```python
math_question = "What is the square root of 2025, then multiply by 7?"

result = agent.invoke({"input": math_question})
```

**Expected trace:**
```
Thought: This is a math problem. I need to calculate sqrt(2025) then multiply by 7.
I'll use the calculator for both steps.
Action: calculator
Action Input: math.sqrt(2025) * 7
Observation: 315.0

Thought: The square root of 2025 is 45, and 45 * 7 = 315. I have the answer.
Final Answer: The square root of 2025 is 45, and 45 multiplied by 7 is 315.
```

The agent recognized it didn't need the search tool and went straight to the calculator.

---

## Third Example: Ambiguous — Watch the Reasoning

```python
ambiguous_question = "Who is the CEO of OpenAI and how long have they been in that role?"

result = agent.invoke({"input": ambiguous_question})
```

**Expected trace:**
```
Thought: I need current information about the OpenAI CEO and their tenure.
This changes over time, so I should search rather than rely on training data.
Action: search
Action Input: OpenAI CEO 2024 how long
Observation: Sam Altman is the CEO of OpenAI. He co-founded OpenAI in 2015 and has
served as CEO since then (except for a brief period in November 2023 when he was
temporarily removed and then reinstated within days).

Thought: Sam Altman has been CEO since OpenAI's founding in 2015.
That's about 9 years (2015 to 2024). I have enough information.
Final Answer: Sam Altman is the CEO of OpenAI. He has held the role since
OpenAI was founded in 2015, approximately 9 years. (Note: he was briefly removed
in November 2023 but reinstated within days.)
```

---

## Key Observations from These Examples

1. **The agent picks the right tool** based on the tool descriptions you provided
2. **It doesn't guess** — for current facts, it searches; for math, it calculates
3. **Each Thought references the Observation** — it's not inventing information
4. **Verbose=True is your friend** — this trace is invaluable for debugging

---

## Common Issues and Fixes

**Agent picks wrong tool:**
- Fix: improve the tool description. Be very specific about when to use each tool.

**Agent tries to calculate in its head:**
- Fix: add "Always use this tool for math — never calculate in your head" to the calculator description.

**Infinite loop:**
- Fix: lower `max_iterations`. Check if the Final Answer format is working.

**Parsing error:**
- Fix: `handle_parsing_errors=True` catches most of these. If persistent, switch to `AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION`.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [01 Agent Fundamentals](../01_Agent_Fundamentals/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 Tool Use](../03_Tool_Use/Theory.md)
