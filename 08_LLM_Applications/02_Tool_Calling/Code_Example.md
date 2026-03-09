# Tool Calling — Code Example

Full working example with the Anthropic Claude API. Defines a weather tool, handles the tool loop, and shows parallel tool calls.

```python
import anthropic
import json

client = anthropic.Anthropic()  # uses ANTHROPIC_API_KEY env var

# ─────────────────────────────────────────────
# STEP 1: Define your tools
# Each tool has: name, description, input_schema
# The description is what the model reads to decide when to call this tool
# ─────────────────────────────────────────────

tools = [
    {
        "name": "get_weather",
        "description": (
            "Get the current weather conditions for a specific city. "
            "Use this whenever the user asks about weather, temperature, "
            "forecast, or climate conditions in a location."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City name, e.g. 'Paris' or 'Tokyo'"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "Temperature unit to return"
                }
            },
            "required": ["city"]
        }
    },
    {
        "name": "get_population",
        "description": (
            "Get the current population of a city or country. "
            "Use when the user asks about population size or demographics."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City or country name"
                }
            },
            "required": ["location"]
        }
    }
]


# ─────────────────────────────────────────────
# STEP 2: Implement the actual tool functions
# These are your real functions — the model just requests them
# ─────────────────────────────────────────────

def get_weather(city: str, unit: str = "celsius") -> dict:
    """Simulated weather API — replace with real API call in production."""
    fake_weather = {
        "Paris": {"temp": 18, "condition": "Partly cloudy", "humidity": 65},
        "Tokyo": {"temp": 22, "condition": "Sunny", "humidity": 55},
        "London": {"temp": 12, "condition": "Rainy", "humidity": 80},
        "New York": {"temp": 25, "condition": "Clear", "humidity": 50},
    }
    data = fake_weather.get(city, {"temp": 20, "condition": "Unknown", "humidity": 60})
    temp = data["temp"]
    if unit == "fahrenheit":
        temp = round(temp * 9/5 + 32, 1)
    return {
        "city": city,
        "temperature": temp,
        "unit": unit,
        "condition": data["condition"],
        "humidity": data["humidity"]
    }


def get_population(location: str) -> dict:
    """Simulated population data."""
    populations = {
        "Paris": 2161000,
        "Tokyo": 13960000,
        "London": 8982000,
        "New York": 8336000,
    }
    pop = populations.get(location, 1000000)
    return {"location": location, "population": pop, "source": "2023 estimate"}


def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Route tool calls to the right function."""
    if tool_name == "get_weather":
        result = get_weather(**tool_input)
    elif tool_name == "get_population":
        result = get_population(**tool_input)
    else:
        result = {"error": f"Unknown tool: {tool_name}"}
    return json.dumps(result)


# ─────────────────────────────────────────────
# STEP 3: The tool call loop
# Send message -> detect tool_use -> execute -> send result -> get final answer
# ─────────────────────────────────────────────

def chat_with_tools(user_message: str) -> str:
    """Complete one user turn, handling any tool calls."""
    messages = [{"role": "user", "content": user_message}]

    print(f"\nUser: {user_message}")

    while True:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1024,
            tools=tools,
            messages=messages
        )

        print(f"[Stop reason: {response.stop_reason}]")

        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text

        elif response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"[Tool call: {block.name}({block.input})]")
                    result = execute_tool(block.name, block.input)
                    print(f"[Tool result: {result}]")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })

            messages.append({"role": "user", "content": tool_results})

        else:
            break

    return "Conversation ended unexpectedly."


# ─────────────────────────────────────────────
# TEST CASES
# ─────────────────────────────────────────────

print("TEST 1: Single tool call")
answer = chat_with_tools("What's the weather like in Paris right now?")
print(f"Assistant: {answer}")

print("\nTEST 2: Parallel tool calls")
answer = chat_with_tools("Compare the weather in Tokyo and London.")
print(f"Assistant: {answer}")

print("\nTEST 3: No tool needed")
answer = chat_with_tools("What is the capital of France?")
print(f"Assistant: {answer}")

print("\nTEST 4: Multiple different tools")
answer = chat_with_tools("What's the weather in Tokyo and what is its population?")
print(f"Assistant: {answer}")
```

**Running this:**
```bash
pip install anthropic
export ANTHROPIC_API_KEY="your-key"
python tool_calling_example.py
```

**Key patterns to remember:**
- Check `response.stop_reason == "tool_use"` to detect tool calls
- Always append both the assistant response AND tool results to messages before continuing
- Use `block.id` to link each tool_result back to its tool_use block
- The loop ends when `stop_reason == "end_turn"`


---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | Tool calling architecture |

⬅️ **Prev:** [01 Prompt Engineering](../01_Prompt_Engineering/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 Structured Outputs](../03_Structured_Outputs/Theory.md)
