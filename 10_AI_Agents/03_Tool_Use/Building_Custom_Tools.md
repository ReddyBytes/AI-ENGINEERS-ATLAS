# Building Custom Tools for AI Agents

A step-by-step guide to defining, testing, and adding custom tools to your agent.

---

## The Pattern

Every custom tool follows the same 4-step pattern:

1. **Define the function** — write the Python code that does the actual work
2. **Write the schema/description** — tell the agent what the tool does and when to use it
3. **Test it independently** — call the function directly to make sure it works
4. **Add to agent** — wrap it and add it to your toolbox

---

## Step 1: Define the Function

The function does the real work. Keep it simple and focused.

Rules:
- One function, one purpose
- Always return a **string** (the agent reads text, not Python objects)
- Handle errors inside the function — return an error string, don't raise
- Keep it fast — the agent waits for each tool to return

```python
# Template
def my_tool_function(input: str) -> str:
    """Docstring explaining what this does."""
    try:
        # ... do the work ...
        return "result as a string"
    except Exception as e:
        return f"Error: {str(e)}"
```

---

## Step 2: Write the Description

This is the most important part. The agent decides whether to call your tool based entirely on this description.

**Good description template:**
```
"[What it does]. Use this when [situation]. Input: [what to pass in]. Returns: [what comes back]. [Edge cases if any]."
```

**Bad description:**
```
"gets stuff from the database"
```

**Good description:**
```
"Looks up a customer's order history by email address. Use this when the user asks about past orders, purchase history, or delivery status. Input: customer email address as a string. Returns: JSON string with list of orders, each containing order_id, date, items, and status. Returns 'Customer not found' if the email doesn't exist in our system."
```

---

## Step 3: Test It Independently

Before connecting to an agent, call the function directly. Make sure it works in all cases.

```python
# Test happy path
result = my_tool_function("valid input")
print(result)
assert isinstance(result, str)  # Must return string

# Test error case
result = my_tool_function("invalid input that should fail")
print(result)  # Should return an error string, not raise

# Test edge cases
result = my_tool_function("")
print(result)  # Empty input
```

Only add it to the agent after it passes these tests.

---

## Step 4: Add to Agent

```python
from langchain.tools import Tool

my_tool = Tool(
    name="tool_name",       # No spaces, use underscores
    func=my_tool_function,  # The function from step 1
    description="..."       # The description from step 2
)

# Add to your tools list
tools = [my_tool, other_tool, ...]
```

---

## Example 1: Database Lookup Tool

Use case: agent needs to look up customer information.

```python
import sqlite3
import json

# Simulated database (use your real database connection in production)
def setup_demo_db():
    """Create a demo database for testing."""
    conn = sqlite3.connect(":memory:")
    conn.execute("""
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            email TEXT UNIQUE,
            name TEXT,
            plan TEXT,
            joined_date TEXT
        )
    """)
    conn.executemany("INSERT INTO customers VALUES (?,?,?,?,?)", [
        (1, "alice@example.com", "Alice Smith", "Pro", "2023-01-15"),
        (2, "bob@example.com", "Bob Jones", "Free", "2023-06-20"),
        (3, "carol@example.com", "Carol White", "Enterprise", "2022-11-01"),
    ])
    conn.commit()
    return conn

db_conn = setup_demo_db()

def lookup_customer(email: str) -> str:
    """
    Look up customer information by email address.
    Returns customer details or 'not found' message.
    """
    try:
        email = email.strip().lower()
        cursor = db_conn.execute(
            "SELECT id, name, plan, joined_date FROM customers WHERE email = ?",
            (email,)
        )
        row = cursor.fetchone()

        if row is None:
            return f"Customer with email '{email}' not found in database."

        customer = {
            "id": row[0],
            "name": row[1],
            "plan": row[2],
            "joined_date": row[3],
            "email": email
        }
        return json.dumps(customer)

    except Exception as e:
        return f"Database error: {str(e)}"

# Test it first
print(lookup_customer("alice@example.com"))
# {"id": 1, "name": "Alice Smith", "plan": "Pro", "joined_date": "2023-01-15", "email": "alice@example.com"}

print(lookup_customer("unknown@example.com"))
# Customer with email 'unknown@example.com' not found in database.

# Wrap as a tool
customer_lookup_tool = Tool(
    name="lookup_customer",
    func=lookup_customer,
    description=(
        "Look up a customer's account information by their email address. "
        "Use this when the user asks about a specific customer's plan, join date, or account details. "
        "Input: customer email address as a string. "
        "Returns: JSON with customer id, name, plan, and joined_date. "
        "Returns 'not found' message if the email doesn't match any customer."
    )
)
```

---

## Example 2: File Reader Tool

Use case: agent needs to read documents from the filesystem.

```python
import os

# Define allowed directories for security
ALLOWED_DIRS = ["/tmp/agent_docs", os.path.expanduser("~/documents/agent")]

def read_file(filepath: str) -> str:
    """
    Read the contents of a text file.
    Only reads files in allowed directories for security.
    """
    try:
        # Security: only allow reading from approved directories
        filepath = os.path.abspath(filepath)
        if not any(filepath.startswith(d) for d in ALLOWED_DIRS):
            return f"Error: Cannot read files outside allowed directories. Allowed: {ALLOWED_DIRS}"

        if not os.path.exists(filepath):
            return f"Error: File not found at '{filepath}'"

        if not os.path.isfile(filepath):
            return f"Error: '{filepath}' is a directory, not a file"

        # Limit file size to prevent huge files overwhelming context
        file_size = os.path.getsize(filepath)
        if file_size > 50_000:  # 50KB limit
            return f"Error: File too large ({file_size} bytes). Max allowed: 50,000 bytes."

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        return f"File contents of '{os.path.basename(filepath)}':\n\n{content}"

    except UnicodeDecodeError:
        return f"Error: File appears to be binary, not text. Cannot read."
    except PermissionError:
        return f"Error: Permission denied reading '{filepath}'"
    except Exception as e:
        return f"Error reading file: {str(e)}"


# Test it
import tempfile
with tempfile.NamedTemporaryFile(mode="w", dir="/tmp", suffix=".txt", delete=False) as f:
    f.write("Hello, this is test content.\nLine 2 of the file.")
    test_file = f.name

# Adjust ALLOWED_DIRS for testing
ALLOWED_DIRS.append("/tmp")
print(read_file(test_file))

# Wrap as tool
file_reader_tool = Tool(
    name="read_file",
    func=read_file,
    description=(
        "Read the text contents of a file. "
        "Use this when the user asks you to read, analyze, or summarize a document. "
        "Input: the full file path as a string. "
        "Returns: the file contents as text. "
        "Returns an error message if the file doesn't exist, is binary, or is too large."
    )
)
```

---

## Example 3: API Caller Tool

Use case: agent calls an external REST API to get live data.

```python
import requests
import json

def call_github_api(query: str) -> str:
    """
    Search GitHub repositories.
    query format: "search:<search terms>" or "user:<username>"
    """
    try:
        query = query.strip()

        if query.startswith("user:"):
            username = query[5:].strip()
            url = f"https://api.github.com/users/{username}/repos"
            params = {"sort": "stars", "per_page": 5}
            response = requests.get(url, params=params, timeout=5)

            if response.status_code == 404:
                return f"GitHub user '{username}' not found."

            repos = response.json()
            if not repos:
                return f"User '{username}' has no public repositories."

            result = f"Top repositories for GitHub user '{username}':\n"
            for repo in repos[:5]:
                result += f"- {repo['name']}: {repo.get('description', 'No description')} (⭐ {repo['stargazers_count']})\n"
            return result

        elif query.startswith("search:"):
            search_terms = query[7:].strip()
            url = "https://api.github.com/search/repositories"
            params = {"q": search_terms, "sort": "stars", "per_page": 3}
            response = requests.get(url, params=params, timeout=5)
            data = response.json()

            if not data.get("items"):
                return f"No GitHub repositories found for '{search_terms}'"

            result = f"Top GitHub repositories for '{search_terms}':\n"
            for repo in data["items"][:3]:
                result += f"- {repo['full_name']}: {repo.get('description', 'No description')} (⭐ {repo['stargazers_count']})\n"
            return result

        else:
            return "Invalid format. Use 'search:<terms>' or 'user:<username>'"

    except requests.Timeout:
        return "Error: GitHub API request timed out. Try again."
    except requests.RequestException as e:
        return f"Error calling GitHub API: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


# Test it
print(call_github_api("search:langchain python"))
print(call_github_api("user:torvalds"))

# Wrap as tool
github_tool = Tool(
    name="search_github",
    func=call_github_api,
    description=(
        "Search GitHub repositories or look up a user's repositories. "
        "Use this when the user asks about open source projects, GitHub repos, or code libraries. "
        "Input format: 'search:<terms>' to search repos, or 'user:<username>' to see a user's repos. "
        "Returns: repository names, descriptions, and star counts."
    )
)
```

---

## Common Pitfalls

### Pitfall 1: Returning non-string types

```python
# BAD: returns a dict
def bad_tool(query):
    return {"result": "some data"}  # Agent can't read this directly

# GOOD: return a string
def good_tool(query):
    data = {"result": "some data"}
    return json.dumps(data)  # or: return str(data)
```

### Pitfall 2: Raising exceptions instead of returning error strings

```python
# BAD: agent crashes when this raises
def bad_tool(query):
    if not query:
        raise ValueError("Query cannot be empty")

# GOOD: return error as string so agent can reason about it
def good_tool(query):
    if not query:
        return "Error: Query cannot be empty. Please provide a search term."
```

### Pitfall 3: Vague descriptions leading to wrong tool selection

```python
# BAD: agent won't know when to use this
Tool(name="data", description="gets data")

# GOOD: specific, tells agent exactly when to use it
Tool(
    name="get_sales_data",
    description="Retrieve monthly sales figures by product category. Use this when the user asks about revenue, sales numbers, or financial performance. Input: month as 'YYYY-MM'."
)
```

### Pitfall 4: Tools that are too slow

Agents wait for each tool. If your tool takes 30 seconds, the agent stalls.

```python
# Add timeouts to all network calls
response = requests.get(url, timeout=5)  # 5 second timeout

# For slow operations, consider caching
import functools

@functools.lru_cache(maxsize=100)
def expensive_database_lookup(query: str) -> str:
    # This result is cached — same query won't hit DB twice
    ...
```

### Pitfall 5: No input validation

```python
# BAD: crashes on unexpected input
def bad_tool(city: str) -> str:
    return weather_api.get(city)  # What if city is None? Or has SQL injection?

# GOOD: validate input first
def good_tool(city: str) -> str:
    if not city or not isinstance(city, str):
        return "Error: city must be a non-empty string"
    city = city.strip()[:100]  # Limit length
    if not city.replace(" ", "").isalpha():
        return "Error: city name should only contain letters and spaces"
    return weather_api.get(city)
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |
| 📄 **Building_Custom_Tools.md** | ← you are here |

⬅️ **Prev:** [02 ReAct Pattern](../02_ReAct_Pattern/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 Agent Memory](../04_Agent_Memory/Theory.md)
