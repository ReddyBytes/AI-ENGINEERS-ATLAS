# Extended Thinking — Code Examples

Complete examples for using extended thinking with the Anthropic Python SDK.

---

## Setup

```python
import anthropic
client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
```

---

## 1 — Basic extended thinking

```python
def think_and_answer(question: str, budget: int = 5000) -> dict:
    """Generate a response with extended thinking."""
    response = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=budget + 2000,  # thinking + response
        thinking={
            "type": "enabled",
            "budget_tokens": budget
        },
        messages=[{"role": "user", "content": question}]
    )
    
    result = {"thinking": None, "answer": None, "stop_reason": response.stop_reason}
    
    for block in response.content:
        if block.type == "thinking":
            result["thinking"] = block.thinking
        elif block.type == "text":
            result["answer"] = block.text
    
    return result


# Example: Hard math problem
result = think_and_answer(
    "What is the sum of all positive integers n ≤ 100 such that n² + n + 41 is prime?",
    budget=8000
)
print(f"Thinking length: {len(result['thinking'])} chars")
print(f"Answer: {result['answer']}")
```

---

## 2 — Compare with and without thinking

```python
def compare_thinking_modes(question: str):
    """Run the same question with and without extended thinking and compare."""
    
    # Without thinking
    standard = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=2048,
        messages=[{"role": "user", "content": question}]
    )
    
    # With extended thinking
    with_thinking = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=12000,
        thinking={"type": "enabled", "budget_tokens": 10000},
        messages=[{"role": "user", "content": question}]
    )
    
    # Extract answers
    standard_answer = standard.content[0].text
    thinking_text, thinking_answer = None, None
    for block in with_thinking.content:
        if block.type == "thinking":
            thinking_text = block.thinking
        elif block.type == "text":
            thinking_answer = block.text
    
    print(f"=== WITHOUT THINKING ===")
    print(standard_answer)
    print(f"\nTokens used: {standard.usage.output_tokens}")
    
    print(f"\n=== WITH THINKING ===")
    print(f"Thinking tokens: {len(thinking_text.split()) * 1.3:.0f} (approx)")
    print(thinking_answer)
    print(f"\nTotal output tokens: {with_thinking.usage.output_tokens}")


compare_thinking_modes(
    "A company's revenue grows at 15% annually. If it was $1M in 2020, "
    "in which year will it first exceed $3M? Show your reasoning."
)
```

---

## 3 — Streaming extended thinking

```python
def stream_with_thinking(question: str, budget: int = 8000):
    """Stream a response, showing thinking and answer separately."""
    
    print("--- THINKING (internal reasoning) ---")
    thinking_buffer = []
    answer_buffer = []
    current_block_type = None
    
    with client.messages.stream(
        model="claude-3-7-sonnet-20250219",
        max_tokens=budget + 3000,
        thinking={"type": "enabled", "budget_tokens": budget},
        messages=[{"role": "user", "content": question}]
    ) as stream:
        for event in stream:
            event_type = getattr(event, 'type', None)
            
            if event_type == 'content_block_start':
                block = event.content_block
                current_block_type = block.type
                if block.type == 'text':
                    print("\n--- FINAL ANSWER ---")
                    
            elif event_type == 'content_block_delta':
                delta = event.delta
                if current_block_type == 'thinking':
                    chunk = getattr(delta, 'thinking', '')
                    if chunk:
                        thinking_buffer.append(chunk)
                        print(chunk, end='', flush=True)
                elif current_block_type == 'text':
                    chunk = getattr(delta, 'text', '')
                    if chunk:
                        answer_buffer.append(chunk)
                        print(chunk, end='', flush=True)
    
    print("\n")
    return ''.join(thinking_buffer), ''.join(answer_buffer)


stream_with_thinking(
    "Design a data structure that supports O(1) insert, delete, and getRandom. "
    "Explain the approach and implement it in Python."
)
```

---

## 4 — Thinking for multi-step math

```python
def solve_math_problem(problem: str, budget: int = 15000) -> dict:
    """Use extended thinking to solve complex math problems."""
    
    response = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=budget + 4000,
        system=(
            "You are an expert mathematician. Show your complete reasoning. "
            "At the end of your response, state the final numerical answer clearly "
            "in the format: ANSWER: [value]"
        ),
        thinking={"type": "enabled", "budget_tokens": budget},
        messages=[{"role": "user", "content": problem}]
    )
    
    thinking_text = None
    answer_text = None
    for block in response.content:
        if block.type == "thinking":
            thinking_text = block.thinking
        elif block.type == "text":
            answer_text = block.text
    
    # Extract final answer
    import re
    match = re.search(r'ANSWER:\s*(.+)', answer_text or '', re.IGNORECASE)
    final_answer = match.group(1).strip() if match else "Not found"
    
    return {
        "problem": problem,
        "thinking_tokens_approx": int(len((thinking_text or "").split()) * 1.3),
        "final_answer": final_answer,
        "full_solution": answer_text,
        "thinking_trace": thinking_text
    }


result = solve_math_problem(
    "Find all pairs of positive integers (m, n) such that m² - n² = 2024."
)
print(f"Final answer: {result['final_answer']}")
print(f"Thinking used: ~{result['thinking_tokens_approx']} tokens")
```

---

## 5 — Thinking for code design

```python
def design_with_thinking(design_problem: str, budget: int = 20000) -> str:
    """Use extended thinking for complex code architecture decisions."""
    
    response = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=budget + 8000,
        system=(
            "You are a senior software architect. Think through design tradeoffs "
            "carefully before recommending an approach. Consider multiple options, "
            "their pros and cons, and justify your final recommendation."
        ),
        thinking={"type": "enabled", "budget_tokens": budget},
        messages=[{"role": "user", "content": design_problem}]
    )
    
    for block in response.content:
        if block.type == "text":
            return block.text
    return ""


design = design_with_thinking(
    "Design a distributed rate limiter that can handle 1M requests/second "
    "across 100 servers. It must be accurate within 1% and add less than 5ms latency. "
    "What approach do you recommend and why?"
)
print(design)
```

---

## 6 — Token usage tracking for cost management

```python
def track_thinking_cost(question: str, budget: int = 10000):
    """Track token usage and estimate cost for thinking calls."""
    
    SONNET_INPUT_RATE = 3.00 / 1_000_000   # $ per token
    SONNET_OUTPUT_RATE = 15.00 / 1_000_000  # $ per token
    
    response = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=budget + 4000,
        thinking={"type": "enabled", "budget_tokens": budget},
        messages=[{"role": "user", "content": question}]
    )
    
    usage = response.usage
    input_cost = usage.input_tokens * SONNET_INPUT_RATE
    output_cost = usage.output_tokens * SONNET_OUTPUT_RATE  # includes thinking
    total_cost = input_cost + output_cost
    
    print(f"Token usage:")
    print(f"  Input:  {usage.input_tokens:,} tokens (${input_cost:.4f})")
    print(f"  Output: {usage.output_tokens:,} tokens (${output_cost:.4f})")
    print(f"  Total cost: ${total_cost:.4f}")
    
    # Extract answer
    for block in response.content:
        if block.type == "text":
            return block.text
    return ""


answer = track_thinking_cost(
    "What is the probability that a randomly chosen 6-digit number "
    "contains at least one repeated digit?"
)
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

⬅️ **Prev:** [07 Constitutional AI](../07_Constitutional_AI/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [09 Claude Model Families](../09_Claude_Model_Families/Theory.md)
