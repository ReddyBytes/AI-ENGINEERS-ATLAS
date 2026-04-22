# First API Call — Interview Q&A

## Beginner Questions

**Q1: What command do you run to install the Anthropic Python SDK?**

A: `pip install anthropic`. For JavaScript: `npm install @anthropic-ai/sdk`.

---

**Q2: How does the Python SDK know which API key to use?**

A: By default, `anthropic.Anthropic()` reads the `ANTHROPIC_API_KEY` environment variable. You can also pass the key explicitly with `anthropic.Anthropic(api_key="sk-ant-...")`, but storing secrets in environment variables is strongly preferred. The environment variable must be set before creating the client.

---

**Q3: Why is `message.content[0].text` used instead of just `message.content`?**

A: The `content` field is a list of content blocks, not a string. Claude can return multiple blocks (e.g., a text block plus a tool_use block). To get the text, you must index into the list at position 0 and access the `.text` attribute of that block. Accessing `message.content` directly gives you a list object, which is not useful for printing.

---

**Q4: What are the two required parameters in every `messages.create()` call?**

A: `model` (which Claude model to use, e.g., `"claude-sonnet-4-6"`) and `max_tokens` (maximum output token count). The `messages` array is also required. Without all three, the SDK raises a validation error.

---

## Intermediate Questions

**Q5: What is the main structural difference between the Python and JavaScript SDKs?**

A: The Python SDK calls are synchronous by default — `client.messages.create(...)` blocks until the response arrives. The JavaScript SDK is fully asynchronous — you must `await client.messages.create(...)` inside an `async` function. The parameter names, response structure, and method names are otherwise identical between the two SDKs.

---

**Q6: What error do you get if `ANTHROPIC_API_KEY` is not set, and how do you fix it?**

A: `anthropic.AuthenticationError` — the server rejects the request because the API key is missing or invalid. Fix: set the environment variable before running your script: `export ANTHROPIC_API_KEY="sk-ant-api03-..."` in bash, or use `os.environ["ANTHROPIC_API_KEY"] = "..."` in code (not recommended for production). Using `python-dotenv` with a `.env` file is the standard development pattern.

---

**Q7: What does `message.stop_reason` tell you about the response?**

A: It indicates why Claude stopped generating. `"end_turn"` means the response is complete. `"max_tokens"` means the response was cut off at your token limit — you may need to increase `max_tokens`. `"tool_use"` means Claude wants to call a function and the conversation is not finished. Always check `stop_reason` before assuming you have a complete response.

---

**Q8: How do you print both the response text and the token usage from a single API call?**

A:
```python
message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello!"}]
)
print(message.content[0].text)
print(f"Tokens: {message.usage.input_tokens} in, {message.usage.output_tokens} out")
```

---

## Advanced Questions

**Q9: How would you build a production-ready Claude client wrapper in Python that handles all error types gracefully?**

A: The wrapper should: (1) catch `AuthenticationError` and raise a clear startup error (fail fast on bad credentials); (2) catch `RateLimitError` with tenacity-based exponential backoff (start 1s, cap 60s, jitter ±25%); (3) catch `APIConnectionError` with retry for transient network issues; (4) catch `APIStatusError` for 5xx server errors with retry; (5) log all requests with model, tokens, latency, and stop_reason; (6) emit metrics for observability. The wrapper presents a simple `ask(prompt) -> str` interface to callers that abstracts all retry and error logic.

---

**Q10: Describe the internal steps the Python SDK takes between calling `client.messages.create()` and returning the response object.**

A: (1) Validate input parameters against the API schema (raises `ValidationError` if required fields are missing). (2) Serialize the Python dict/Pydantic model to JSON. (3) Construct HTTP headers: `x-api-key` from `ANTHROPIC_API_KEY`, `anthropic-version: 2023-06-01`, `content-type: application/json`. (4) Send HTTP POST to `https://api.anthropic.com/v1/messages` using `httpx`. (5) Receive HTTP response. (6) If status is 4xx/5xx, raise the appropriate exception subclass. (7) Deserialize JSON response body to a typed `Message` object with proper attribute access. (8) Return the `Message` object.

---

**Q11: What's the difference between using `client.messages.create()` synchronously vs the async variant in Python?**

A: The synchronous version blocks the thread until the response arrives — fine for scripts and simple applications. The async version, `await client.messages.create()` via `anthropic.AsyncAnthropic()`, uses Python's asyncio and is non-blocking — the event loop can process other tasks while waiting for the API response. Use the async client when building FastAPI endpoints, processing multiple requests concurrently, or integrating Claude into an async application. Using the sync client in an async context (e.g., a FastAPI route) will block the event loop and degrade throughput.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept guide |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Working code |

⬅️ **Prev:** [Messages API](../02_Messages_API/Interview_QA.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [System Prompts](../04_System_Prompts/Interview_QA.md)
