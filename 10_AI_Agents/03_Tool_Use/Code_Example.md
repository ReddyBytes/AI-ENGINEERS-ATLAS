# Tool Use — Code Example

Three custom tools connected to a LangChain agent. The agent uses the right tool for different questions.

---

## Setup

```bash
pip install langchain langchain-openai requests
```

```python
import os
import math
import json
import requests
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI

os.environ["OPENAI_API_KEY"] = "your-key-here"
```

---

## Tool 1: Get Current Weather

```python
def get_current_weather(query: str) -> str:
    """
    Get current weather for a city.
    query should be the city name, e.g. "London" or "New York"
    Uses the free Open-Meteo API (no key required).
    """
    try:
        # Step 1: Get coordinates for the city
        geocode_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo_response = requests.get(geocode_url, params={
            "name": query,
            "count": 1,
            "language": "en",
            "format": "json"
        }, timeout=5)

        geo_data = geo_response.json()
        if not geo_data.get("results"):
            return f"Could not find city: {query}"

        location = geo_data["results"][0]
        lat = location["latitude"]
        lon = location["longitude"]
        city_name = location["name"]
        country = location.get("country", "")

        # Step 2: Get current weather
        weather_url = "https://api.open-meteo.com/v1/forecast"
        weather_response = requests.get(weather_url, params={
            "latitude": lat,
            "longitude": lon,
            "current_weather": True,
            "temperature_unit": "celsius"
        }, timeout=5)

        weather_data = weather_response.json()
        current = weather_data["current_weather"]
        temp = current["temperature"]
        wind = current["windspeed"]

        return (
            f"Current weather in {city_name}, {country}: "
            f"{temp}°C, wind speed {wind} km/h"
        )
    except Exception as e:
        return f"Weather lookup failed: {str(e)}"


weather_tool = Tool(
    name="get_current_weather",
    func=get_current_weather,
    description=(
        "Get the current weather for a city. "
        "Use this when the user asks about weather, temperature, or climate in a location. "
        "Input: city name as a string (e.g. 'London' or 'Tokyo'). "
        "Returns: current temperature in Celsius and wind speed."
    )
)
```

---

## Tool 2: Calculator

```python
def calculate(expression: str) -> str:
    """
    Evaluate a mathematical expression.
    Input: a Python math expression as a string.
    Returns: the numeric result.
    """
    try:
        # Safe math evaluation — expose only math module functions
        safe_globals = {
            "math": math,
            "abs": abs, "round": round, "min": min, "max": max,
            "sum": sum, "pow": pow
        }
        result = eval(expression, {"__builtins__": {}}, safe_globals)
        return str(result)
    except ZeroDivisionError:
        return "Error: Division by zero"
    except SyntaxError:
        return f"Error: Invalid expression '{expression}'"
    except Exception as e:
        return f"Error: {str(e)}"


calculator_tool = Tool(
    name="calculate",
    func=calculate,
    description=(
        "Evaluate a mathematical expression precisely. "
        "Use this for ALL math calculations — never try to calculate in your head. "
        "Supports: +, -, *, /, **, math.sqrt(), math.log(), math.pi, etc. "
        "Input: a valid Python math expression as a string, e.g. '2 ** 10' or 'math.sqrt(144)'. "
        "Returns: the numeric result as a string."
    )
)
```

---

## Tool 3: Web Search (Simulated for Demo)

```python
# In production, replace this with Tavily or DuckDuckGo
# pip install duckduckgo-search
# from langchain_community.tools import DuckDuckGoSearchRun
# search_run = DuckDuckGoSearchRun()

# For this demo, we simulate search responses
def search_web(query: str) -> str:
    """
    Simulated search — in production, replace with real search API.
    """
    # Simulated knowledge base for demo
    knowledge = {
        "python": "Python is a high-level programming language created by Guido van Rossum. First released in 1991. Known for simple, readable syntax.",
        "langchain": "LangChain is a framework for building LLM-powered applications. Supports agents, chains, memory, and tool use. Founded by Harrison Chase in 2022.",
        "openai": "OpenAI is an AI research company founded in 2015. Known for GPT models and ChatGPT. Sam Altman is the CEO.",
        "react pattern": "ReAct (Reasoning + Acting) is a prompting technique for LLM agents. Interleaves Thought-Action-Observation steps. Published by Google Brain in 2022.",
    }

    query_lower = query.lower()
    for key, info in knowledge.items():
        if key in query_lower:
            return info

    return f"Search results for '{query}': Found general information but no specific matches in demo database. In production, this would return real web results."


search_tool = Tool(
    name="search_web",
    func=search_web,
    description=(
        "Search the internet for current information. "
        "Use this when you need facts about people, companies, events, or concepts. "
        "Use this instead of relying on your training data for recent or specific facts. "
        "Input: a clear search query as a string. "
        "Returns: relevant information found online."
    )
)
```

---

## Connect to Agent

```python
llm = ChatOpenAI(model="gpt-4o", temperature=0)

tools = [weather_tool, calculator_tool, search_tool]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    max_iterations=5,
    handle_parsing_errors=True,
)
```

---

## Test: Different Questions, Different Tools

### Test 1: Weather question → uses get_current_weather

```python
result = agent.invoke({"input": "What is the current weather in Tokyo?"})
print(result["output"])
```

**Expected trace:**
```
Thought: The user wants current weather in Tokyo. I'll use get_current_weather.
Action: get_current_weather
Action Input: Tokyo
Observation: Current weather in Tokyo, Japan: 22°C, wind speed 15 km/h

Thought: I have the weather data. I can answer now.
Final Answer: The current weather in Tokyo, Japan is 22°C with a wind speed of 15 km/h.
```

---

### Test 2: Math question → uses calculator

```python
result = agent.invoke({"input": "What is 2 to the power of 16, then divide by 1024?"})
print(result["output"])
```

**Expected trace:**
```
Thought: This is a math problem. I'll use the calculator.
Action: calculate
Action Input: 2 ** 16 / 1024
Observation: 64.0

Thought: 2^16 is 65536, divided by 1024 is 64. I have the answer.
Final Answer: 2 to the power of 16 is 65,536. Divided by 1,024, the result is 64.
```

---

### Test 3: Factual question → uses search_web

```python
result = agent.invoke({"input": "What is LangChain and who created it?"})
print(result["output"])
```

**Expected trace:**
```
Thought: The user wants to know about LangChain. I should search for this information.
Action: search_web
Action Input: LangChain framework creator
Observation: LangChain is a framework for building LLM-powered applications...
             Founded by Harrison Chase in 2022.

Thought: I found the relevant information about LangChain.
Final Answer: LangChain is a framework for building LLM-powered applications...
```

---

### Test 4: Multi-tool question → uses search THEN calculator

```python
result = agent.invoke({
    "input": "In what year was Python created? Calculate how many years ago that was (current year: 2024) and multiply by 100."
})
print(result["output"])
```

**Expected trace:**
```
Thought: I need to find when Python was created. I'll search for this.
Action: search_web
Action Input: Python programming language creation year
Observation: Python is a high-level programming language created by Guido van Rossum.
             First released in 1991.

Thought: Python was created in 1991. Years ago = 2024 - 1991 = 33. Now I need 33 * 100.
Action: calculate
Action Input: (2024 - 1991) * 100
Observation: 3300

Thought: Python was created 33 years ago. 33 * 100 = 3300.
Final Answer: Python was first released in 1991, which was 33 years ago (as of 2024).
33 multiplied by 100 is 3,300.
```

---

## Key Observations

1. The agent **picked the right tool each time** based on the descriptions
2. **Multi-step questions** used multiple tools in sequence
3. The agent **never tried to calculate in its head** — it used the calculator tool
4. The agent **never tried to guess facts** — it used the search tool

This is the power of clear tool descriptions. The agent matched its need to the right tool automatically.

---

## Replacing the Simulated Search with Real Search

```python
# Option 1: DuckDuckGo (free, no API key)
from langchain_community.tools import DuckDuckGoSearchRun
real_search = DuckDuckGoSearchRun()

search_tool = Tool(
    name="search_web",
    func=real_search.run,
    description="Search the internet for current information. Input: search query."
)

# Option 2: Tavily (better for agents, has an API key free tier)
# pip install tavily-python
from langchain_community.tools.tavily_search import TavilySearchResults
tavily_tool = TavilySearchResults(max_results=3)
# Then add to tools list directly: tools = [weather_tool, calculator_tool, tavily_tool]
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |
| [📄 Building_Custom_Tools.md](./Building_Custom_Tools.md) | Guide to building custom tools |

⬅️ **Prev:** [02 ReAct Pattern](../02_ReAct_Pattern/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 Agent Memory](../04_Agent_Memory/Theory.md)
