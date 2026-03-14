# Agent Evaluation — Code Example

```python
"""
agent_evaluator.py — Evaluate an agent's task completion and tool use
pip install anthropic
"""
import anthropic
import json
from dataclasses import dataclass, field
from typing import Optional

client = anthropic.Anthropic()


# ──────────────────────────────────────────────
# 1. Mock agent and tools for testing
# ──────────────────────────────────────────────

# Track all tool calls made during execution
TOOL_CALL_LOG = []


def mock_get_weather(city: str) -> dict:
    """Mock weather tool."""
    TOOL_CALL_LOG.append({"tool": "get_weather", "params": {"city": city}})
    weather = {"London": {"temp_c": 15, "condition": "cloudy"},
               "Paris": {"temp_c": 18, "condition": "sunny"},
               "NYC": {"temp_c": 22, "condition": "clear"}}
    return weather.get(city, {"error": f"City {city} not found"})


def mock_convert_temperature(celsius: float) -> dict:
    """Mock temperature conversion tool."""
    TOOL_CALL_LOG.append({"tool": "convert_temperature", "params": {"celsius": celsius}})
    return {"fahrenheit": round(celsius * 9 / 5 + 32, 1)}


def mock_search_flights(origin: str, destination: str, date: str) -> dict:
    """Mock flight search tool."""
    TOOL_CALL_LOG.append({
        "tool": "search_flights",
        "params": {"origin": origin, "destination": destination, "date": date}
    })
    return {
        "flights": [
            {"id": "UA123", "price": 450, "duration": "7h"},
            {"id": "BA456", "price": 380, "duration": "8h"},
        ]
    }


TOOLS = [
    {
        "name": "get_weather",
        "description": "Get current weather for a city",
        "input_schema": {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"]
        }
    },
    {
        "name": "convert_temperature",
        "description": "Convert temperature from Celsius to Fahrenheit",
        "input_schema": {
            "type": "object",
            "properties": {"celsius": {"type": "number"}},
            "required": ["celsius"]
        }
    },
    {
        "name": "search_flights",
        "description": "Search for available flights",
        "input_schema": {
            "type": "object",
            "properties": {
                "origin": {"type": "string"},
                "destination": {"type": "string"},
                "date": {"type": "string", "description": "YYYY-MM-DD"}
            },
            "required": ["origin", "destination", "date"]
        }
    }
]

TOOL_FUNCTIONS = {
    "get_weather": mock_get_weather,
    "convert_temperature": mock_convert_temperature,
    "search_flights": mock_search_flights,
}


def run_agent(task: str, max_steps: int = 10) -> dict:
    """Run agent on a task, return final answer and trajectory."""
    global TOOL_CALL_LOG
    TOOL_CALL_LOG = []  # Reset log

    messages = [{"role": "user", "content": task}]
    steps = 0

    while steps < max_steps:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1024,
            tools=TOOLS,
            messages=messages
        )

        # Check if agent is done
        if response.stop_reason == "end_turn":
            final_answer = response.content[0].text if response.content else ""
            return {
                "task": task,
                "final_answer": final_answer,
                "trajectory": TOOL_CALL_LOG.copy(),
                "steps": steps + 1,
                "completed": True
            }

        # Process tool calls
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                tool_func = TOOL_FUNCTIONS.get(block.name)
                if tool_func:
                    result = tool_func(**block.input)
                else:
                    result = {"error": f"Unknown tool: {block.name}"}
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result)
                })

        # Continue conversation
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})
        steps += 1

    return {
        "task": task,
        "final_answer": "Max steps exceeded",
        "trajectory": TOOL_CALL_LOG.copy(),
        "steps": max_steps,
        "completed": False
    }


# ──────────────────────────────────────────────
# 2. Evaluation framework
# ──────────────────────────────────────────────

@dataclass
class TestCase:
    task: str
    expected_answer_contains: list[str]  # Strings the answer should contain
    golden_trajectory: list[dict]         # Expected tool calls
    max_steps: int = 10
    should_refuse: bool = False           # Safety test case


@dataclass
class EvalResult:
    test_case: TestCase
    agent_output: dict
    answer_score: float = 0.0     # 0 or 1 based on expected strings
    tool_precision: float = 0.0
    tool_recall: float = 0.0
    tool_f1: float = 0.0
    step_efficiency: float = 0.0
    safety_pass: bool = True


def evaluate_answer(actual: str, expected_contains: list[str]) -> float:
    """Check if answer contains all expected strings (case-insensitive)."""
    actual_lower = actual.lower()
    hits = sum(1 for e in expected_contains if e.lower() in actual_lower)
    return hits / len(expected_contains) if expected_contains else 1.0


def evaluate_trajectory(golden: list[dict], actual: list[dict]) -> dict:
    """Compare actual tool calls to golden trajectory."""
    golden_tools = [t["tool"] for t in golden]
    actual_tools = [t["tool"] for t in actual]

    golden_set = set(golden_tools)
    actual_set = set(actual_tools)
    correct_set = golden_set & actual_set

    precision = len(correct_set) / len(actual_set) if actual_set else 0.0
    recall = len(correct_set) / len(golden_set) if golden_set else 0.0
    f1 = 2 * precision * recall / (precision + recall + 1e-9)
    efficiency = len(golden) / len(actual) if actual else 0.0

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "efficiency": efficiency,
        "extra_calls": list(actual_set - golden_set),
        "missed_calls": list(golden_set - actual_set),
    }


def run_evaluation(test_cases: list[TestCase]) -> list[EvalResult]:
    """Run all test cases and return evaluation results."""
    results = []

    for i, tc in enumerate(test_cases):
        print(f"\nTest {i+1}/{len(test_cases)}: {tc.task[:60]}...")
        agent_output = run_agent(tc.task, max_steps=tc.max_steps)

        # Evaluate answer
        answer_score = evaluate_answer(
            agent_output["final_answer"],
            tc.expected_answer_contains
        )

        # Evaluate trajectory
        traj_eval = evaluate_trajectory(
            tc.golden_trajectory,
            agent_output["trajectory"]
        )

        # Safety evaluation
        unsafe_tools = {"delete_file", "send_email", "make_payment"}
        used_tools = {t["tool"] for t in agent_output["trajectory"]}
        safety_pass = len(used_tools & unsafe_tools) == 0

        result = EvalResult(
            test_case=tc,
            agent_output=agent_output,
            answer_score=answer_score,
            tool_precision=traj_eval["precision"],
            tool_recall=traj_eval["recall"],
            tool_f1=traj_eval["f1"],
            step_efficiency=traj_eval["efficiency"],
            safety_pass=safety_pass
        )
        results.append(result)

        status = "PASS" if answer_score >= 0.8 else "FAIL"
        print(f"  Answer: {status} ({answer_score:.2f}) | Tool F1: {traj_eval['f1']:.2f} | Efficiency: {traj_eval['efficiency']:.2f}")
        if traj_eval["extra_calls"]:
            print(f"  Extra calls: {traj_eval['extra_calls']}")
        if traj_eval["missed_calls"]:
            print(f"  Missed calls: {traj_eval['missed_calls']}")

    return results


def print_eval_summary(results: list[EvalResult]):
    """Print aggregate evaluation summary."""
    n = len(results)
    print("\n" + "="*50)
    print(f"Agent Evaluation Summary ({n} test cases)")
    print("="*50)
    print(f"  Task completion rate:  {sum(r.answer_score >= 0.8 for r in results)/n:.2%}")
    print(f"  Avg answer score:      {sum(r.answer_score for r in results)/n:.3f}")
    print(f"  Avg tool precision:    {sum(r.tool_precision for r in results)/n:.3f}")
    print(f"  Avg tool recall:       {sum(r.tool_recall for r in results)/n:.3f}")
    print(f"  Avg tool F1:           {sum(r.tool_f1 for r in results)/n:.3f}")
    print(f"  Avg step efficiency:   {sum(r.step_efficiency for r in results)/n:.3f}")
    print(f"  Safety pass rate:      {sum(r.safety_pass for r in results)/n:.2%}")


# ──────────────────────────────────────────────
# 3. Define test suite and run
# ──────────────────────────────────────────────

TEST_SUITE = [
    TestCase(
        task="What is the current weather in London and what is that in Fahrenheit?",
        expected_answer_contains=["15", "59", "london"],
        golden_trajectory=[
            {"tool": "get_weather", "params": {"city": "London"}},
            {"tool": "convert_temperature", "params": {"celsius": 15}},
        ]
    ),
    TestCase(
        task="Get the weather for Paris.",
        expected_answer_contains=["paris", "18"],
        golden_trajectory=[
            {"tool": "get_weather", "params": {"city": "Paris"}},
        ]
    ),
    TestCase(
        task="Search for flights from NYC to London on 2024-11-12",
        expected_answer_contains=["UA123", "BA456", "london"],
        golden_trajectory=[
            {"tool": "search_flights", "params": {"origin": "NYC", "destination": "London", "date": "2024-11-12"}},
        ]
    ),
]


if __name__ == "__main__":
    print("Running agent evaluation suite...")
    results = run_evaluation(TEST_SUITE)
    print_eval_summary(results)
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

⬅️ **Prev:** [04 — RAG Evaluation](../04_RAG_Evaluation/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [06 — Red Teaming](../06_Red_Teaming/Theory.md)
