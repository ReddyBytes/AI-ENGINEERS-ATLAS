# Code Example — Weather MCP Server

A complete, working MCP server that provides weather information using the Open-Meteo free API (no API key required). This server demonstrates a real-world pattern: wrapping an external REST API as MCP tools.

---

## Setup

```bash
pip install mcp httpx
```

---

## Full Weather Server Code

```python
# weather_server.py
# A weather lookup MCP server using the Open-Meteo free API
# No API key required!
# Run with: python weather_server.py
# Test with: npx @modelcontextprotocol/inspector python weather_server.py

import asyncio
import httpx
import sys
import mcp.server.stdio
import mcp.types as types
from mcp.server import Server
from mcp.server.models import InitializationOptions

# ─────────────────────────────────────────────
# SERVER SETUP
# ─────────────────────────────────────────────

app = Server("weather-server")

# Open-Meteo base URL (free, no API key)
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────

async def get_coordinates(city: str) -> tuple[float, float, str] | None:
    """Look up latitude/longitude for a city name."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                GEOCODING_URL,
                params={"name": city, "count": 1, "language": "en"},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            if not data.get("results"):
                return None

            result = data["results"][0]
            return (
                result["latitude"],
                result["longitude"],
                result.get("name", city)
            )
        except Exception as e:
            print(f"Geocoding error: {e}", file=sys.stderr)
            return None


async def get_weather_data(lat: float, lon: float, forecast_days: int = 1) -> dict | None:
    """Fetch weather data for given coordinates."""
    async with httpx.AsyncClient() as client:
        try:
            params = {
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,windspeed_10m,precipitation,weathercode",
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode",
                "forecast_days": forecast_days,
                "timezone": "auto"
            }
            response = await client.get(WEATHER_URL, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Weather API error: {e}", file=sys.stderr)
            return None


def weather_code_to_description(code: int) -> str:
    """Convert WMO weather code to human-readable description."""
    codes = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Foggy", 48: "Icy fog",
        51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
        61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
        80: "Slight showers", 81: "Moderate showers", 82: "Violent showers",
        95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Thunderstorm with heavy hail"
    }
    return codes.get(code, f"Unknown (code {code})")


# ─────────────────────────────────────────────
# TOOLS
# ─────────────────────────────────────────────

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    """Declare the tools this server provides."""
    return [
        types.Tool(
            name="get_current_weather",
            description=(
                "Get the current weather conditions for a city. "
                "Returns temperature, wind speed, precipitation, and weather description."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city name to look up weather for (e.g., 'London', 'New York', 'Tokyo')"
                    }
                },
                "required": ["city"]
            }
        ),
        types.Tool(
            name="get_weather_forecast",
            description=(
                "Get a multi-day weather forecast for a city. "
                "Returns daily high/low temperatures, precipitation, and weather description."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city name to look up the forecast for"
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days to forecast (1-7)",
                        "minimum": 1,
                        "maximum": 7,
                        "default": 3
                    }
                },
                "required": ["city"]
            }
        ),
        types.Tool(
            name="compare_weather",
            description=(
                "Compare current weather between two cities. "
                "Useful for deciding where to travel or understanding regional differences."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "city1": {
                        "type": "string",
                        "description": "First city to compare"
                    },
                    "city2": {
                        "type": "string",
                        "description": "Second city to compare"
                    }
                },
                "required": ["city1", "city2"]
            }
        )
    ]


@app.call_tool()
async def call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent]:
    """Handle tool execution."""

    # ── Tool: get_current_weather ──────────────────────────
    if name == "get_current_weather":
        city = arguments.get("city", "")
        if not city:
            return [types.TextContent(type="text", text="Error: city argument is required")]

        # Get coordinates
        coords = await get_coordinates(city)
        if not coords:
            return [types.TextContent(
                type="text",
                text=f"Error: Could not find location for '{city}'. Try a more specific city name."
            )]

        lat, lon, resolved_name = coords

        # Get weather data
        data = await get_weather_data(lat, lon, forecast_days=1)
        if not data:
            return [types.TextContent(type="text", text="Error: Could not fetch weather data. Please try again.")]

        current = data.get("current", {})
        temp = current.get("temperature_2m", "N/A")
        wind = current.get("windspeed_10m", "N/A")
        precip = current.get("precipitation", "N/A")
        code = current.get("weathercode", 0)
        units = data.get("current_units", {})

        result = f"""Current weather in {resolved_name}:
- Conditions: {weather_code_to_description(code)}
- Temperature: {temp}{units.get('temperature_2m', '°C')}
- Wind speed: {wind}{units.get('windspeed_10m', ' km/h')}
- Precipitation: {precip}{units.get('precipitation', ' mm')}
"""
        return [types.TextContent(type="text", text=result)]

    # ── Tool: get_weather_forecast ─────────────────────────
    elif name == "get_weather_forecast":
        city = arguments.get("city", "")
        days = arguments.get("days", 3)

        if not city:
            return [types.TextContent(type="text", text="Error: city argument is required")]

        coords = await get_coordinates(city)
        if not coords:
            return [types.TextContent(
                type="text",
                text=f"Error: Could not find location for '{city}'"
            )]

        lat, lon, resolved_name = coords
        data = await get_weather_data(lat, lon, forecast_days=days)
        if not data:
            return [types.TextContent(type="text", text="Error: Could not fetch forecast data")]

        daily = data.get("daily", {})
        dates = daily.get("time", [])
        max_temps = daily.get("temperature_2m_max", [])
        min_temps = daily.get("temperature_2m_min", [])
        precip = daily.get("precipitation_sum", [])
        codes = daily.get("weathercode", [])

        lines = [f"{days}-day forecast for {resolved_name}:\n"]
        for i in range(min(days, len(dates))):
            lines.append(
                f"{dates[i]}: {weather_code_to_description(codes[i])} | "
                f"High: {max_temps[i]}°C, Low: {min_temps[i]}°C | "
                f"Precipitation: {precip[i]}mm"
            )

        return [types.TextContent(type="text", text="\n".join(lines))]

    # ── Tool: compare_weather ──────────────────────────────
    elif name == "compare_weather":
        city1 = arguments.get("city1", "")
        city2 = arguments.get("city2", "")

        if not city1 or not city2:
            return [types.TextContent(type="text", text="Error: both city1 and city2 are required")]

        # Fetch both cities concurrently
        coords1, coords2 = await asyncio.gather(
            get_coordinates(city1),
            get_coordinates(city2)
        )

        if not coords1:
            return [types.TextContent(type="text", text=f"Error: Could not find location for '{city1}'")]
        if not coords2:
            return [types.TextContent(type="text", text=f"Error: Could not find location for '{city2}'")]

        data1, data2 = await asyncio.gather(
            get_weather_data(coords1[0], coords1[1]),
            get_weather_data(coords2[0], coords2[1])
        )

        def format_city(name, data):
            c = data.get("current", {})
            return (
                f"{name}:\n"
                f"  {weather_code_to_description(c.get('weathercode', 0))}\n"
                f"  Temperature: {c.get('temperature_2m', 'N/A')}°C\n"
                f"  Wind: {c.get('windspeed_10m', 'N/A')} km/h"
            )

        result = f"Weather Comparison:\n\n{format_city(coords1[2], data1)}\n\n{format_city(coords2[2], data2)}"
        return [types.TextContent(type="text", text=result)]

    else:
        raise ValueError(f"Unknown tool: {name}")


# ─────────────────────────────────────────────
# MAIN — START THE SERVER
# ─────────────────────────────────────────────

async def main():
    """Run the weather MCP server over stdio transport."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="weather-server",
                server_version="1.0.0",
                capabilities=app.get_capabilities(
                    notification_options=None,
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Testing

```bash
# Option 1: MCP Inspector (interactive web UI)
npx @modelcontextprotocol/inspector python weather_server.py

# Option 2: Direct JSON-RPC test (stdio)
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | python weather_server.py
```

---

## Claude Desktop Config

```json
{
  "mcpServers": {
    "weather": {
      "command": "python",
      "args": ["/absolute/path/to/weather_server.py"]
    }
  }
}
```

After restarting Claude Desktop, try asking:
- "What's the weather in Tokyo right now?"
- "Give me a 5-day forecast for London"
- "Compare the weather in Paris and New York"

---

## Key Patterns Demonstrated

| Pattern | Location in Code |
|---|---|
| Multiple tools in one server | `list_tools()` returns 3 Tool objects |
| Async HTTP calls with httpx | `get_coordinates()`, `get_weather_data()` |
| Concurrent tool operations | `asyncio.gather()` in `compare_weather` |
| Input validation | Checking for empty `city` before API calls |
| Graceful error returns | `return [types.TextContent(type="text", text="Error: ...")]` |
| Environment-independent | No API key needed (uses free Open-Meteo API) |
| Logging to stderr | `print(..., file=sys.stderr)` in helpers |

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |
| [📄 Server_Implementation.md](./Server_Implementation.md) | Full server implementation guide |
| [📄 Step_by_Step.md](./Step_by_Step.md) | Step-by-step build guide |

⬅️ **Prev:** [05 Transport Layer](../05_Transport_Layer/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [07 Security and Permissions](../07_Security_and_Permissions/Theory.md)