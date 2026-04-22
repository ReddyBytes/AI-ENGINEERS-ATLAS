# Tool Use — Code Examples

## Example 1: Single tool — calculator

```python
import anthropic
import math

client = anthropic.Anthropic()

# Define the tool
tools = [
    {
        "name": "calculate",
        "description": "Perform mathematical calculations. Use this for any arithmetic, algebra, or math operations.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "A Python math expression to evaluate (e.g., '15 * 4 + 7', 'math.sqrt(144)')"
                }
            },
            "required": ["expression"]
        }
    }
]

def execute_calculator(expression: str) -> float:
    """Safely evaluate a math expression."""
    return eval(expression, {"__builtins__": {}}, {"math": math})

def ask_with_calculator(question: str) -> str:
    messages = [{"role": "user", "content": question}]
    
    for _ in range(5):  # max 5 tool calls
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            tools=tools,
            messages=messages
        )
        
        if response.stop_reason == "end_turn":
            return response.content[0].text
        
        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = execute_calculator(block.input["expression"])
                    results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result)
                    })
            messages.append({"role": "user", "content": results})
    
    return "Could not complete calculation"

print(ask_with_calculator("What is (15 × 4) + the square root of 144?"))
```

---

## Example 2: Multiple tools — weather + time

```python
import anthropic
from datetime import datetime
import pytz

client = anthropic.Anthropic()

tools = [
    {
        "name": "get_current_time",
        "description": "Returns the current local time for a given timezone. Use when asked about time in a location.",
        "input_schema": {
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": "IANA timezone name (e.g., 'America/New_York', 'Asia/Tokyo')"
                }
            },
            "required": ["timezone"]
        }
    },
    {
        "name": "get_weather",
        "description": "Returns current weather for a city. Use when asked about weather, temperature, or conditions.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name"}
            },
            "required": ["city"]
        }
    }
]

def get_current_time(timezone: str) -> str:
    tz = pytz.timezone(timezone)
    now = datetime.now(tz)
    return now.strftime("%I:%M %p %Z on %A, %B %d, %Y")

def get_weather(city: str) -> str:
    # Mock — replace with real weather API
    weather_db = {
        "Tokyo": "72°F, sunny",
        "London": "58°F, cloudy",
        "New York": "68°F, partly cloudy"
    }
    return weather_db.get(city, "Weather data unavailable")

TOOL_MAP = {"get_current_time": get_current_time, "get_weather": get_weather}

def run(question):
    messages = [{"role": "user", "content": question}]
    for _ in range(8):
        resp = client.messages.create(
            model="claude-sonnet-4-6", max_tokens=1024,
            tools=tools, messages=messages
        )
        if resp.stop_reason == "end_turn":
            return next(b.text for b in resp.content if b.type == "text")
        messages.append({"role": "assistant", "content": resp.content})
        results = []
        for b in resp.content:
            if b.type == "tool_use":
                fn = TOOL_MAP[b.name]
                out = fn(**b.input)
                results.append({"type": "tool_result", "tool_use_id": b.id, "content": out})
        messages.append({"role": "user", "content": results})

print(run("What's the time and weather in Tokyo right now?"))
```

---

## Example 3: Forced tool use with tool_choice

```python
import anthropic
import json

client = anthropic.Anthropic()

# Force structured extraction from any input
tools = [
    {
        "name": "extract_contact",
        "description": "Extract contact information from text.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "email": {"type": "string"},
                "phone": {"type": "string"},
                "company": {"type": "string"}
            },
            "required": []
        }
    }
]

def extract_contact_info(text: str) -> dict:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        tools=tools,
        tool_choice={"type": "tool", "name": "extract_contact"},  # force this tool
        messages=[{"role": "user", "content": f"Extract contact info:\n{text}"}]
    )
    
    tool_block = next(b for b in response.content if b.type == "tool_use")
    return tool_block.input

result = extract_contact_info(
    "Please reach out to Sarah Connor at sarah.c@cyberdyne.com or call 555-0123. She works at Cyberdyne Systems."
)
print(json.dumps(result, indent=2))
# {"name": "Sarah Connor", "email": "sarah.c@cyberdyne.com", "phone": "555-0123", "company": "Cyberdyne Systems"}
```

---

## Example 4: Error handling in tool results

```python
import anthropic
import requests

client = anthropic.Anthropic()

tools = [
    {
        "name": "fetch_url",
        "description": "Fetches content from a URL. Returns the page text.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to fetch"}
            },
            "required": ["url"]
        }
    }
]

def fetch_url(url: str) -> str:
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.text[:2000]  # truncate
    except requests.exceptions.Timeout:
        raise TimeoutError(f"Request to {url} timed out")
    except requests.exceptions.HTTPError as e:
        raise ValueError(f"HTTP {e.response.status_code} from {url}")

def run_with_error_handling(question):
    messages = [{"role": "user", "content": question}]
    for _ in range(5):
        resp = client.messages.create(
            model="claude-sonnet-4-6", max_tokens=1024,
            tools=tools, messages=messages
        )
        if resp.stop_reason == "end_turn":
            return resp.content[0].text
        messages.append({"role": "assistant", "content": resp.content})
        results = []
        for b in resp.content:
            if b.type == "tool_use":
                try:
                    out = fetch_url(**b.input)
                    results.append({"type":"tool_result","tool_use_id":b.id,"content":out})
                except Exception as e:
                    # Return error gracefully — don't crash
                    results.append({
                        "type": "tool_result",
                        "tool_use_id": b.id,
                        "content": f"Error: {str(e)}",
                        "is_error": True
                    })
        messages.append({"role": "user", "content": results})
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept guide |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | Full architecture |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [System Prompts](../04_System_Prompts/Code_Example.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Streaming](../06_Streaming/Code_Example.md)
