# Using LLM APIs — Interview Q&A

## Beginner

**Q1: How does an LLM API work? What happens when you make a call?**

<details>
<summary>💡 Show Answer</summary>

An LLM API is a REST endpoint. You send an HTTP POST request with a JSON body containing your prompt and parameters. The server processes the request, runs the LLM inference, and returns a JSON response with the generated text.

Here's the lifecycle of an API call:

1. **Client side**: You construct a JSON payload with model, messages, and parameters (temperature, max_tokens, etc.)
2. **Network**: The request travels to the API server
3. **Tokenization**: The server tokenizes your input text into token IDs
4. **Inference**: The model runs a forward pass over the tokens and generates output tokens autoregressively
5. **Detokenization**: Output token IDs are converted back to text
6. **Response**: The server returns JSON with the generated text and metadata (token usage, stop reason, etc.)

The client never touches the model directly — it's all abstracted behind the HTTP interface. This is why LLM APIs can be called from any language (Python, JavaScript, curl, etc.) and why you pay per token rather than per model weight.

</details>

---

<br>

**Q2: What is the system prompt and why is it important?**

<details>
<summary>💡 Show Answer</summary>

The system prompt is a special message in the conversation that contains instructions for the model. It's separate from the user conversation (doesn't appear in the user/assistant exchange) and sets the model's behavior for the entire session.

What you put in the system prompt:
- The model's role or persona: "You are a customer service agent for Acme Corp."
- Constraints: "Respond only in English. Keep responses under 100 words."
- Context: "The user is a beginner developer."
- Format instructions: "Always respond with a numbered list."
- Safety guardrails: "Do not discuss competitor products."

Why it's important:
1. It's processed once and applies to all messages — no need to repeat instructions in every user message
2. It's the authoritative instruction source — the model treats system prompts with high confidence
3. It shapes model behavior without taking up user-turn context
4. It's how you configure an LLM-powered product to behave consistently

In Anthropic's Claude API, the system prompt is a top-level parameter. In OpenAI's API, it's the first message with role="system".

</details>

---

<br>

**Q3: What does max_tokens do? What happens if you set it too low or too high?**

<details>
<summary>💡 Show Answer</summary>

max_tokens sets the maximum number of tokens the model is allowed to generate in the response. It's an upper bound — the model will stop when it generates a natural ending OR when it hits this limit, whichever comes first.

**If too low:**
The model gets cut off mid-sentence. The response is incomplete. The stop_reason in the API response will be "max_tokens" instead of "end_turn".

```python
# Example: response cut off
response = client.messages.create(
    max_tokens=10,  # Too low for meaningful output
    messages=[{"role": "user", "content": "Explain machine learning."}]
)
# Output: "Machine learning is a subset of artificial"  (truncated)
# stop_reason: "max_tokens"
```

**If too high:**
The model generates a long response when you needed a short one. This wastes tokens and increases cost and latency. A model generating 2,000 tokens when you needed 100 is costing you 20x more than necessary.

**Best practice:**
Set max_tokens to a reasonable upper bound for your use case:
- Classification/sentiment: 20–50 tokens
- Single question Q&A: 200–500 tokens
- Analysis or explanation: 500–1500 tokens
- Document summarization: 500–2000 tokens
- Code generation: 500–4096 tokens (code can be long)

Always check response.stop_reason. If it's frequently "max_tokens", increase your limit. If responses are much shorter than max_tokens, you're paying for potential that you never use.

</details>

---

## Intermediate

**Q4: How does streaming work in LLM APIs? When should you use it?**

<details>
<summary>💡 Show Answer</summary>

Without streaming, the API waits for the complete response to be generated, then returns everything at once. With streaming, tokens are sent to the client as soon as they're generated — the client receives the response incrementally.

**How it works technically:**
The API uses Server-Sent Events (SSE) or HTTP chunked transfer encoding. The server sends partial tokens in a stream, the client reads them as they arrive and renders them progressively.

**When to use streaming:**

Use streaming when:
- Building a user-facing chat interface (user sees text appear, not wait 5+ seconds)
- Response could be long (essays, code, analysis) — user gets value immediately
- You want to show "thinking" progress to the user

Don't use streaming when:
- Processing responses programmatically (you need the full text to parse it)
- Building batch pipelines (non-interactive, latency doesn't matter)
- Using tool use/function calling (need complete tool_use blocks)

**Implementation (Claude SDK):**

```python
import anthropic

client = anthropic.Anthropic()

# Non-streaming (wait for all)
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1000,
    messages=[{"role": "user", "content": "Write a poem about coding."}]
)
print(response.content[0].text)  # All at once

# Streaming (get tokens as they arrive)
with client.messages.stream(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1000,
    messages=[{"role": "user", "content": "Write a poem about coding."}]
) as stream:
    for text_chunk in stream.text_stream:
        print(text_chunk, end="", flush=True)
```

The user experience difference between streaming and non-streaming on a long response is dramatic — seconds vs immediate first words.

</details>

---

<br>

**Q5: How do you implement multi-turn conversation with an LLM API? What are the limitations?**

<details>
<summary>💡 Show Answer</summary>

LLM APIs are stateless — each call is independent. To create a multi-turn conversation, you include the entire conversation history in the messages array of each request.

```python
import anthropic

client = anthropic.Anthropic()
conversation_history = []

def chat(user_message):
    # Add the new user message
    conversation_history.append({
        "role": "user",
        "content": user_message
    })

    # Send the full conversation history
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        system="You are a helpful assistant.",
        messages=conversation_history  # Full history every time
    )

    # Extract assistant response
    assistant_message = response.content[0].text

    # Add assistant response to history for next turn
    conversation_history.append({
        "role": "assistant",
        "content": assistant_message
    })

    return assistant_message

# Usage
print(chat("My name is Alice. What's your name?"))
print(chat("What's my name?"))  # Model can answer because history includes it
```

**Limitations:**

1. **Context window overflow**: As the conversation grows, it eventually exceeds the context window. Old messages must be dropped or summarized.

2. **Cost grows with conversation length**: Every message in history costs tokens on every subsequent call. A 50-turn conversation means turn 50 includes all 49 previous turns as input tokens.

3. **Stateless by design**: If the server crashes or the user starts a new session, the history is gone. You must persist conversation history in your database.

4. **No cross-session memory**: The model doesn't remember user "Alice" from a previous conversation unless you explicitly provide that context.

**Managing context overflow:**
- Sliding window: only keep the last N turns
- Summarization: periodically summarize old turns and replace with the summary
- Token counting: measure history size and truncate when approaching the limit

</details>

---

<br>

**Q6: How does structured output (tool use) work? When should you use it instead of prompting for JSON?**

<details>
<summary>💡 Show Answer</summary>

Structured output via tool use is more reliable than prompting the model to output JSON.

**Plain JSON prompting (less reliable):**
```
"Respond with a JSON object with keys 'name' and 'age'."
```
Problems: model might add explanatory text before/after the JSON, might format it slightly differently, might omit required fields.

**Tool use (more reliable):**
You define a JSON schema. The model is guaranteed to return data that matches that schema (or use a different stop reason if it can't).

```python
import json
import anthropic

client = anthropic.Anthropic()

# Define the schema for structured extraction
tools = [{
    "name": "extract_contact_info",
    "description": "Extract contact information from text",
    "input_schema": {
        "type": "object",
        "properties": {
            "full_name": {
                "type": "string",
                "description": "Person's full name"
            },
            "email": {
                "type": "string",
                "description": "Email address if present"
            },
            "phone": {
                "type": "string",
                "description": "Phone number if present"
            }
        },
        "required": ["full_name"]
    }
}]

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=500,
    tools=tools,
    # Force tool use (don't let model respond with text)
    tool_choice={"type": "tool", "name": "extract_contact_info"},
    messages=[{
        "role": "user",
        "content": "Contact me at sarah.jones@example.com or call 555-0100. - Sarah Jones"
    }]
)

# Extract the structured data
if response.stop_reason == "tool_use":
    tool_block = next(b for b in response.content if b.type == "tool_use")
    data = tool_block.input
    print(json.dumps(data, indent=2))
    # {"full_name": "Sarah Jones", "email": "sarah.jones@example.com", "phone": "555-0100"}
```

**When to use tool use:**
- Data extraction (entities, facts, structured records)
- Classification (sentiment, category, intent)
- Any time you need reliable, parseable output for programmatic use
- When JSON validity is required (not optional)

**When plain prompting is fine:**
- Prototyping (faster to iterate)
- Outputs that will be shown to humans (don't need perfect structure)
- When you're using a simple schema and the model is reliable

</details>

---

## Advanced

**Q7: How does prompt caching work and when does it provide significant cost savings?**

<details>
<summary>💡 Show Answer</summary>

Prompt caching allows you to mark a prefix of your prompt as cacheable. The API processes this prefix once, stores the resulting KV cache, and reuses it across subsequent requests that share the same prefix.

**How it works (Anthropic):**
```python
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    system=[{
        "type": "text",
        "text": "You are a helpful assistant. [your very long system prompt...]",
        "cache_control": {"type": "ephemeral"}  # Mark for caching
    }],
    messages=[{"role": "user", "content": user_question}]
)
```

When the same prefix (marked for caching) is seen again within the cache TTL (5 minutes for Anthropic), the model reuses the cached computation. Cached tokens cost ~10% of normal input token price.

**Cost savings calculation:**
```
Without caching (1,000 calls, 2,000-token system prompt):
  Input: 1,000 × 2,000 = 2M tokens × $3/M = $6.00
  Cache write cost: 1 call × 2,000 × $3.75/M = $0.0075 (slightly more expensive)

With caching (1,000 calls, same system prompt):
  Cache write: 1 × 2,000 × $3.75/M = $0.0075
  Cache reads: 999 × 2,000 × $0.30/M = $0.60
  Total: ~$0.61

  Savings: $6.00 - $0.61 = $5.39 (90% reduction)
```

**When prompt caching helps significantly:**
- Long system prompts (>1,000 tokens) reused across many requests
- RAG patterns where the same documents are embedded in context for many queries
- Multi-turn conversations with the same session (cache the conversation so far)

**When it doesn't help:**
- Each request has a unique prompt prefix
- Request volume is low (not enough cache hits to justify setup)
- Prompts change frequently between requests

Note: caching behavior and pricing differ between providers. Check current documentation.

</details>

---

<br>

**Q8: How do you manage conversation history efficiently to avoid context window overflow?**

<details>
<summary>💡 Show Answer</summary>

Managing conversation history is a real engineering problem for production chat applications. Here are the main strategies:

**Strategy 1: Fixed-length sliding window**
```python
MAX_HISTORY_TURNS = 10  # Keep last 10 exchanges

def get_messages_for_api(full_history):
    # Take last MAX_HISTORY_TURNS * 2 messages (user + assistant pairs)
    recent = full_history[-MAX_HISTORY_TURNS * 2:]
    return recent
```
Simple, predictable. Cons: loses older context abruptly.

**Strategy 2: Token-aware truncation**
```python
import tiktoken  # or anthropic's token counter

def get_messages_within_budget(full_history, token_budget=50000):
    enc = tiktoken.encoding_for_model("gpt-4")  # approximate

    result = []
    tokens_used = 0

    # Add from most recent backwards
    for msg in reversed(full_history):
        msg_tokens = len(enc.encode(msg["content"]))
        if tokens_used + msg_tokens > token_budget:
            break
        result.insert(0, msg)
        tokens_used += msg_tokens

    return result
```
More precise. Retains as much history as fits.

**Strategy 3: Summarization**
```python
def summarize_old_history(old_messages):
    """Use the LLM to summarize old conversation turns."""
    summary_prompt = f"""
Summarize the following conversation in 3-5 bullet points.
Capture: key facts established, decisions made, user preferences, important context.

Conversation:
{format_messages(old_messages)}

Summary (bullet points):"""

    response = client.messages.create(
        model="claude-3-5-haiku-20241022",  # Cheap model for summarization
        max_tokens=300,
        messages=[{"role": "user", "content": summary_prompt}]
    )
    return response.content[0].text

# When history gets too long:
def manage_history(full_history, max_tokens=60000):
    if count_tokens(full_history) > max_tokens:
        # Summarize the oldest half
        split = len(full_history) // 2
        old_messages = full_history[:split]
        recent_messages = full_history[split:]

        summary = summarize_old_history(old_messages)

        # Replace old messages with summary
        summary_message = {
            "role": "user",
            "content": f"[Earlier conversation summary: {summary}]"
        }
        return [summary_message] + recent_messages

    return full_history
```

**Which to use:**
- Low-stakes chat: sliding window is fine
- Customer service / support: token-aware truncation keeps more relevant context
- Long-running projects or complex conversations: summarization preserves important context

</details>

---

<br>

**Q9: How do you design an LLM API integration for production reliability? What are the key engineering considerations?**

<details>
<summary>💡 Show Answer</summary>

Production LLM integrations have requirements beyond "it works in a demo." Key considerations:

**1. Resilience and retries**

Never let a single API failure crash your application. Implement:
- Exponential backoff on 429 and 5xx errors
- Circuit breaker to stop hammering a failing API
- Fallback models (if Claude Sonnet is down, try Claude Haiku)
- Request timeouts (don't wait forever)

**2. Observability**

Log everything you need to debug problems:
```python
import logging
import time

def traced_api_call(client, **kwargs):
    start = time.time()
    request_id = str(uuid.uuid4())[:8]

    logging.info(f"[{request_id}] API call start: model={kwargs['model']}, "
                 f"input_tokens_est={estimate_tokens(kwargs['messages'])}")

    response = client.messages.create(**kwargs)
    elapsed = time.time() - start

    logging.info(f"[{request_id}] API call complete: "
                 f"input={response.usage.input_tokens}, "
                 f"output={response.usage.output_tokens}, "
                 f"latency={elapsed:.2f}s, "
                 f"stop_reason={response.stop_reason}")

    return response
```

Track per request: model, input tokens, output tokens, latency, stop reason, errors. This data helps you optimize cost and find reliability issues.

**3. Cost controls**

- Set max_tokens on every request (hard cost ceiling per call)
- Track daily/monthly spend in your own database
- Alert when daily cost exceeds a threshold
- Use smaller models for non-critical tasks (Haiku vs Sonnet)

**4. Content validation**

Don't blindly trust LLM output:
- Validate JSON structure (try/except json.loads)
- Check output length is reasonable
- Scan for unexpected content patterns
- For critical outputs, add a second-pass validation model call

**5. Prompt versioning**

Treat prompts like code:
```python
PROMPT_VERSION = "v2.3"
SYSTEM_PROMPT = """
You are a helpful assistant.
[full prompt here]
"""
# Log prompt version with each request for debugging
```

When you change prompts, behavior changes — and changes might be subtle. Version your prompts, A/B test important changes, and have rollback capability.

**6. Rate limit management**

If you're making many requests:
- Track requests per minute, tokens per minute in your code
- Implement a token bucket or leaky bucket rate limiter
- Queue requests and process at a controlled rate
- For large batch jobs, use the Batch API (cheaper, async)

**7. Security**

- Store API keys in environment variables or secret managers (never in code)
- Sanitize user inputs before inserting into prompts (prompt injection attacks)
- Don't echo sensitive user data in logs
- Consider whether the model's responses could expose other users' data (if using shared history)

These considerations turn a working prototype into a reliable, observable, cost-controlled production service.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Cookbook.md](./Code_Cookbook.md) | Code cookbook for LLM API calls |
| [📄 Cost_Guide.md](./Cost_Guide.md) | Cost optimization guide |

⬅️ **Prev:** [08 Hallucination and Alignment](../08_Hallucination_and_Alignment/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [01 Prompt Engineering](../../08_LLM_Applications/01_Prompt_Engineering/Theory.md)