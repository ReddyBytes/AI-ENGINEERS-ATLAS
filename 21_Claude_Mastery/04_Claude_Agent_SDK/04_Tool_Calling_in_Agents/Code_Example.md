# Tool Calling in Agents — Code Example

## Basic Tool Call Patterns

```python
"""
Tool calling patterns: schema design, error handling, output formats.
"""
from claude_agent_sdk import Agent, tool
from pathlib import Path
import json


# ── PATTERN 1: Simple typed tools ─────────────────────────────

@tool
def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert a temperature from Celsius to Fahrenheit.
    Returns the converted temperature as a float."""
    return (celsius * 9/5) + 32

@tool
def get_string_info(text: str) -> dict:
    """Analyze a string and return its properties.
    Returns: word_count, char_count, is_palindrome, uppercase_version."""
    words = text.split()
    return {
        "word_count": len(words),
        "char_count": len(text),
        "is_palindrome": text.lower() == text.lower()[::-1],
        "uppercase_version": text.upper()
    }


# ── PATTERN 2: Tool with optional parameters ──────────────────

@tool
def format_list(
    items: list[str],
    separator: str = ", ",
    prefix: str = "",
    suffix: str = ""
) -> str:
    """Format a list of strings into a single formatted string.
    separator: what goes between items (default: ', ')
    prefix: prepend to final result (default: empty)
    suffix: append to final result (default: empty)
    Example: format_list(['a','b','c'], separator=' | ') → 'a | b | c'"""
    result = separator.join(items)
    return f"{prefix}{result}{suffix}"


# ── PATTERN 3: Tool that can fail gracefully ──────────────────

@tool
def safe_divide(numerator: float, denominator: float) -> dict:
    """Divide numerator by denominator.
    Returns: {"result": float, "status": "ok"} on success.
    Returns: {"result": null, "status": "error", "reason": str} on failure.
    Never raises exceptions — all errors returned in response."""
    if denominator == 0:
        return {"result": None, "status": "error", "reason": "Division by zero"}
    return {"result": numerator / denominator, "status": "ok"}


# ── PATTERN 4: Tool with validation ──────────────────────────

ALLOWED_CATEGORIES = ["science", "history", "technology", "arts"]

@tool
def get_facts(topic: str, category: str = "general", count: int = 3) -> list[str]:
    """Get interesting facts about a topic.
    category must be one of: science, history, technology, arts, general.
    count: how many facts to return (1-10).
    Returns list of fact strings."""
    if category not in ALLOWED_CATEGORIES + ["general"]:
        raise ValueError(f"Category must be one of: {ALLOWED_CATEGORIES + ['general']}")
    if not (1 <= count <= 10):
        raise ValueError(f"count must be between 1 and 10, got {count}")
    # In production: call a real facts API
    return [f"Fact {i+1} about {topic} ({category}): ..." for i in range(count)]


# ── PATTERN 5: File tools with scoping ───────────────────────

WORKSPACE_DIR = Path("/tmp/agent_workspace")
WORKSPACE_DIR.mkdir(exist_ok=True)

@tool
def read_workspace_file(filename: str) -> str:
    """Read a file from the agent workspace directory.
    filename: just the filename, not a path (e.g., 'notes.txt', not '/etc/notes.txt').
    Returns file contents as a string.
    Raises FileNotFoundError if file doesn't exist."""
    # Security: prevent path traversal
    safe_path = (WORKSPACE_DIR / filename).resolve()
    if not str(safe_path).startswith(str(WORKSPACE_DIR)):
        raise ValueError(f"Path traversal not allowed: {filename}")
    if not safe_path.exists():
        raise FileNotFoundError(f"File not found: {filename}")
    return safe_path.read_text()

@tool
def write_workspace_file(filename: str, content: str) -> str:
    """Write content to a file in the agent workspace directory.
    filename: just the filename, must end in .txt, .md, or .json.
    Returns confirmation with the file path."""
    safe_path = (WORKSPACE_DIR / filename).resolve()
    if not str(safe_path).startswith(str(WORKSPACE_DIR)):
        raise ValueError(f"Path traversal not allowed: {filename}")
    if safe_path.suffix not in [".txt", ".md", ".json"]:
        raise ValueError(f"Only .txt, .md, .json files allowed, got {safe_path.suffix}")
    safe_path.write_text(content)
    return f"Written to: {safe_path}"


# ── RUN EXAMPLE AGENTS ───────────────────────────────────────

if __name__ == "__main__":
    # Agent 1: using typed tools
    math_agent = Agent(
        model="claude-sonnet-4-6",
        tools=[celsius_to_fahrenheit, safe_divide],
        system="You are a unit conversion assistant."
    )
    result = math_agent.run("What is 37°C in Fahrenheit? Also, what is 100 / 4?")
    print("Math result:", result)
    
    # Agent 2: file workspace agent
    file_agent = Agent(
        model="claude-sonnet-4-6",
        tools=[read_workspace_file, write_workspace_file],
        system="""You are a file management assistant.
        Files live in a workspace directory.
        Always confirm after writing."""
    )
    result = file_agent.run(
        "Write a file called 'shopping.txt' with 3 items: apples, bread, milk. "
        "Then read it back and confirm the contents."
    )
    print("File result:", result)
```

---

## Before-Tool Approval Callback

```python
"""
Human-in-the-loop: require approval before sensitive tool calls.
"""
from claude_agent_sdk import Agent, tool
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Which tools require explicit approval
SENSITIVE_TOOLS = {"send_email", "delete_record", "charge_payment"}

@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email to a recipient.
    to: email address. subject: email subject. body: email content.
    Returns confirmation with message ID."""
    # In production: call email service
    return f"Email sent to {to} (mock). Message ID: msg_001"

@tool
def get_account_info(account_id: str) -> dict:
    """Look up account information by ID.
    Returns: name, email, status, balance."""
    # In production: query database
    return {"name": "Alice", "email": "alice@example.com", "status": "active", "balance": 150.00}

def approval_callback(tool_name: str, tool_input: dict) -> bool:
    """Require human approval for sensitive operations."""
    logger.info(f"Tool call: {tool_name}({tool_input})")
    
    if tool_name in SENSITIVE_TOOLS:
        print(f"\n⚠️  APPROVAL REQUIRED")
        print(f"Tool: {tool_name}")
        print(f"Input: {json.dumps(tool_input, indent=2)}")
        decision = input("Approve? [y/N]: ").strip().lower()
        if decision != "y":
            logger.warning(f"BLOCKED: {tool_name}")
            return False
        logger.info(f"APPROVED: {tool_name}")
    
    return True

agent = Agent(
    model="claude-sonnet-4-6",
    tools=[send_email, get_account_info],
    system="You are a customer support assistant.",
    before_tool=approval_callback
)

if __name__ == "__main__":
    # get_account_info runs automatically; send_email requires approval
    result = agent.run(
        "Look up account acct_001 and send them a welcome email at their email address."
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
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | Tool call internals |

⬅️ **Prev:** [Simple Agent](../03_Simple_Agent/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Multi-Step Reasoning](../05_Multi_Step_Reasoning/Theory.md)
