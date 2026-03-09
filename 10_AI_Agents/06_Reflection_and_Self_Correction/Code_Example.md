# Reflection and Self-Correction — Code Example

An agent that generates code, runs it, reads the error, and automatically fixes it — a self-correction loop.

---

## Setup

```bash
pip install langchain langchain-openai
```

```python
import os
import subprocess
import tempfile
import textwrap
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

os.environ["OPENAI_API_KEY"] = "your-key-here"

llm = ChatOpenAI(model="gpt-4o", temperature=0)
```

---

## The Code Executor (Sandboxed)

```python
def run_code_safely(code: str, timeout: int = 10) -> dict:
    """
    Execute Python code in a subprocess (isolated from this process).
    Returns: {"success": bool, "output": str, "error": str}
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        temp_file = f.name

    try:
        result = subprocess.run(
            ["python", temp_file],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        if result.returncode == 0:
            return {
                "success": True,
                "output": result.stdout,
                "error": ""
            }
        else:
            return {
                "success": False,
                "output": result.stdout,
                "error": result.stderr
            }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": "",
            "error": f"Code execution timed out after {timeout} seconds"
        }
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": str(e)
        }
    finally:
        import os as _os
        try:
            _os.unlink(temp_file)
        except Exception:
            pass
```

---

## The Code Generator

```python
def generate_code(task: str, previous_attempt: str = "", error: str = "") -> str:
    """
    Generate Python code for a task.
    If there's a previous failed attempt, include it and the error for self-correction.
    """
    if previous_attempt and error:
        # Self-correction prompt
        prompt = f"""You are writing Python code. A previous attempt failed.

Task: {task}

Previous code that failed:
```python
{previous_attempt}
```

Error message:
```
{error}
```

Analyze the error carefully. Write corrected Python code that fixes this specific issue.
Return ONLY the Python code. No explanation, no markdown, no backticks."""

    else:
        # First attempt
        prompt = f"""Write Python code to complete this task:

{task}

Requirements:
- Complete, runnable Python code
- Include a print statement to show the result
- Handle edge cases

Return ONLY the Python code. No explanation, no markdown, no backticks."""

    messages = [
        SystemMessage(content="You are an expert Python programmer. Write clean, correct code."),
        HumanMessage(content=prompt)
    ]

    response = llm.invoke(messages)
    return response.content.strip()
```

---

## The Self-Correction Loop

```python
def self_correcting_code_agent(task: str, max_attempts: int = 4) -> dict:
    """
    Generate code, run it, and if it fails, self-correct automatically.
    Returns the final result with attempt history.
    """
    history = []
    current_code = ""
    current_error = ""

    for attempt in range(1, max_attempts + 1):
        print(f"\n{'='*50}")
        print(f"ATTEMPT {attempt}/{max_attempts}")
        print('='*50)

        # Generate code (first attempt or self-correction)
        current_code = generate_code(task, current_code, current_error)
        print(f"\nGenerated code:\n{current_code}")

        # Run the code
        result = run_code_safely(current_code)
        print(f"\nExecution result: {'SUCCESS' if result['success'] else 'FAILED'}")

        if result['success']:
            print(f"Output: {result['output']}")
            history.append({
                "attempt": attempt,
                "code": current_code,
                "success": True,
                "output": result['output'],
                "error": ""
            })
            return {
                "success": True,
                "final_code": current_code,
                "output": result['output'],
                "attempts": attempt,
                "history": history
            }
        else:
            print(f"Error:\n{result['error']}")
            current_error = result['error']
            history.append({
                "attempt": attempt,
                "code": current_code,
                "success": False,
                "output": result['output'],
                "error": current_error
            })

    # All attempts exhausted
    return {
        "success": False,
        "final_code": current_code,
        "output": "",
        "attempts": max_attempts,
        "history": history,
        "last_error": current_error
    }
```

---

## Test 1: Simple Task (Should Pass First Try)

```python
result = self_correcting_code_agent(
    task="Write a function that takes a list of numbers and returns the mean, median, and mode. Test it with [1, 2, 2, 3, 4, 5, 5, 5].",
    max_attempts=4
)

print(f"\n{'='*50}")
print("FINAL RESULT")
print('='*50)
print(f"Success: {result['success']}")
print(f"Attempts needed: {result['attempts']}")
print(f"Output: {result['output']}")
```

---

## Test 2: Intentionally Buggy Task (Tests Self-Correction)

Here we give the agent a slightly tricky task where the first attempt often fails:

```python
tricky_task = """
Write a Python function that:
1. Takes a URL string (e.g. "https://example.com/page?id=123&name=test")
2. Parses out all query parameters as a dictionary
3. Returns the dictionary sorted by key alphabetically
4. Test it with "https://api.example.com/search?q=python&sort=desc&page=2&limit=10"
5. Print the result in JSON format with indentation
"""

result = self_correcting_code_agent(task=tricky_task, max_attempts=4)

print(f"\n{'='*50}")
print("FINAL RESULT")
print('='*50)
print(f"Success: {result['success']}")
print(f"Attempts needed: {result['attempts']}")
if result['success']:
    print(f"Final output:\n{result['output']}")
```

**What you'll see when self-correction kicks in:**

```
==================================================
ATTEMPT 1/4
==================================================
Generated code:
from urllib.parse import urlparse, parse_qs
import json
...

Execution result: FAILED
Error:
  File "tmp.py", line 8
    params = {k: v[0] if len(v) == 1 else v for k, v in params.items()
                                                                         ^
SyntaxError: invalid syntax

==================================================
ATTEMPT 2/4
==================================================
[Agent reads error, sees syntax issue, regenerates with fix]

Generated code:
from urllib.parse import urlparse, parse_qs
import json

def parse_url_params(url):
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    # Flatten single-item lists and sort
    result = {k: (v[0] if len(v) == 1 else v) for k, v in params.items()}
    return dict(sorted(result.items()))
...

Execution result: SUCCESS
Output:
{
  "limit": "10",
  "page": "2",
  "q": "python",
  "sort": "desc"
}
```

---

## Test 3: View the Full History

```python
# See exactly what happened on each attempt
for entry in result['history']:
    print(f"\n--- Attempt {entry['attempt']} ---")
    print(f"Status: {'SUCCESS' if entry['success'] else 'FAILED'}")
    if entry['error']:
        print(f"Error: {entry['error'][:200]}")
    if entry['success']:
        print(f"Output: {entry['output']}")
```

---

## The Pattern in Plain English

What just happened:

1. **First try** — agent generates code based on the task description
2. **Execution** — code runs in an isolated subprocess
3. **Failure detected** — the exact error message is captured
4. **Self-correction** — agent sees: original task + failed code + exact error → generates a targeted fix
5. **Repeat** — loop runs until success or max attempts

The error message acts as the evaluator — no LLM judgment needed to know if the code works.

---

## Extending This: With Tests

For even more reliable self-correction, provide explicit test cases:

```python
task_with_tests = """
Write a function `fibonacci(n)` that returns the nth Fibonacci number.
It must pass these tests:
- fibonacci(0) == 0
- fibonacci(1) == 1
- fibonacci(10) == 55
- fibonacci(20) == 6765

Include the tests in the code using assert statements.
Print "All tests passed!" if successful.
"""

result = self_correcting_code_agent(task=task_with_tests, max_attempts=4)
```

Now the agent isn't just fixing syntax errors — it's self-correcting logical bugs as well, because the assertion failures tell it exactly what the expected vs actual values are.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [05 Planning and Reasoning](../05_Planning_and_Reasoning/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [07 Multi-Agent Systems](../07_Multi_Agent_Systems/Theory.md)
