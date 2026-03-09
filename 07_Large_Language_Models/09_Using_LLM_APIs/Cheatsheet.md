# Using LLM APIs — Cheatsheet

**One-liner:** LLM APIs take structured messages (system/user/assistant roles), expose parameters like temperature and max_tokens, support streaming and tool use, and charge per token — manage them carefully.

---

## Key terms

| Term | What it means |
|------|---------------|
| API | Application Programming Interface — send a request, get a response |
| Messages format | Structured conversation with system/user/assistant roles |
| System prompt | Instructions for the model; shapes its behavior for the whole conversation |
| User message | What the human says |
| Assistant message | What the model says (or pre-fill to guide the model) |
| Temperature | Randomness dial: 0 = deterministic, 1.0 = creative |
| max_tokens | Maximum output tokens the model can generate |
| top_p | Nucleus sampling threshold (0.9 = keep tokens summing to 90% probability) |
| stop sequences | Strings that halt generation immediately |
| Streaming | Receive tokens as generated (better UX) vs wait for full response |
| Tool use | Model calls structured functions; you get back JSON (not plain text) |
| Rate limit | Max requests or tokens per minute; exceeded = 429 error |
| Prompt caching | Cache frequently-used prompt prefixes; reduces input token cost by ~90% |
| Batch API | Send multiple requests at once; cheaper but async (not real-time) |
| Context window | Max total tokens (system + messages + response combined) |

---

## Messages format reference

```python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,

    # System prompt — model instructions (optional but recommended)
    system="You are a helpful assistant that answers concisely in 2-3 sentences.",

    # Conversation history — include previous turns for multi-turn chat
    messages=[
        {"role": "user",      "content": "What is the capital of France?"},
        {"role": "assistant", "content": "The capital of France is Paris."},
        {"role": "user",      "content": "What is the population of that city?"}
    ]
)

print(response.content[0].text)
print(f"Input: {response.usage.input_tokens} tokens")
print(f"Output: {response.usage.output_tokens} tokens")
```

---

## Parameter quick reference

| Parameter | Low value effect | High value effect | Good default |
|-----------|-----------------|-------------------|-------------|
| temperature | Focused, deterministic | Creative, varied | 0.7 for chat; 0 for code/JSON |
| max_tokens | Short responses | Long responses | Set to task max |
| top_p | Narrow selection | Broad selection | 0.9 (usually leave alone) |

---

## Common error codes

| Code | Meaning | Action |
|------|---------|--------|
| 400 | Bad request — malformed prompt | Fix the request |
| 401 | Unauthorized — bad API key | Check API key |
| 413 | Payload too large | Shorten the prompt |
| 429 | Rate limit exceeded | Wait and retry with backoff |
| 500/502/503 | Server error | Retry with exponential backoff |

---

## Model size vs cost tradeoffs (Anthropic Claude, approximate 2024)

| Model | Speed | Quality | Input cost | Output cost | Use for |
|-------|-------|---------|-----------|------------|---------|
| claude-3-5-haiku | Fastest | Good | $0.80/M | $4/M | Classification, extraction, simple Q&A |
| claude-3-5-sonnet | Fast | Very good | $3/M | $15/M | Most production tasks |
| claude-3-opus | Slower | Best | $15/M | $75/M | Complex reasoning, frontier tasks |

Note: Prices change frequently. Always check current pricing at console.anthropic.com.

---

## Retry pattern

```python
import time
import anthropic

def call_with_retry(client, **kwargs):
    for attempt in range(3):
        try:
            return client.messages.create(**kwargs)
        except anthropic.RateLimitError:
            time.sleep(2 ** attempt)  # 1, 2, 4 seconds
        except anthropic.APIStatusError as e:
            if e.status_code >= 500 and attempt < 2:
                time.sleep(2 ** attempt)
            else:
                raise
    raise Exception("Max retries exceeded")
```

---

## Streaming pattern

```python
with client.messages.stream(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Tell me a story."}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

---

## Structured output (tool use) pattern

```python
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    tools=[{
        "name": "my_function",
        "description": "What this function does",
        "input_schema": {
            "type": "object",
            "properties": {
                "field1": {"type": "string"},
                "field2": {"type": "integer"}
            },
            "required": ["field1"]
        }
    }],
    messages=[{"role": "user", "content": "Extract..."}]
)

# Check if model used the tool
if response.stop_reason == "tool_use":
    tool_use = next(b for b in response.content if b.type == "tool_use")
    data = tool_use.input  # This is your structured JSON
```

---

## Golden rules

1. Never hardcode API keys. Use environment variables (`ANTHROPIC_API_KEY`).
2. Always set max_tokens. Without it, you might get unexpectedly long (and expensive) responses.
3. Always handle rate limit errors with retry + backoff. Never crash on 429.
4. Use streaming for user-facing apps. It dramatically improves perceived responsiveness.
5. Check token usage in the response. It's your cost tracker.
6. Use the smallest model that does the job well. Haiku is 19x cheaper than Opus.
7. Prompt caching can reduce costs by 90% if you reuse the same system prompt.
8. The model has no memory between API calls. You must send history in messages.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Cookbook.md](./Code_Cookbook.md) | Code cookbook for LLM API calls |
| [📄 Cost_Guide.md](./Cost_Guide.md) | Cost optimization guide |

⬅️ **Prev:** [08 Hallucination and Alignment](../08_Hallucination_and_Alignment/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [01 Prompt Engineering](../../08_LLM_Applications/01_Prompt_Engineering/Theory.md)