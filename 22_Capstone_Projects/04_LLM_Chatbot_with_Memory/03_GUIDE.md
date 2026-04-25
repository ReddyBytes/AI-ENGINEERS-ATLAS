# Project 4 — Build Guide

## Overview

This project is shorter in code than the previous ones but requires understanding a new domain: API calls, authentication, and streaming. Each stage is testable independently.

**Total estimated time:** 3 to 4 hours, including reading API documentation.

---

## Before You Start — Environment Setup

### Step 1: Get your Anthropic API key

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Create an account or sign in
3. Navigate to API Keys and create a new key
4. Copy the key — you will only see it once

### Step 2: Set the API key as an environment variable

Never hardcode API keys in your code. Always use environment variables.

```bash
# On macOS/Linux:
export ANTHROPIC_API_KEY="sk-ant-your-key-here"

# On Windows (Command Prompt):
set ANTHROPIC_API_KEY=sk-ant-your-key-here

# To make it permanent (macOS/Linux): add the export line to ~/.zshrc or ~/.bashrc
```

### Step 3: Set up your project

```bash
mkdir -p ~/ai-projects/04_chatbot
cd ~/ai-projects/04_chatbot
python -m venv venv
source venv/bin/activate
pip install anthropic
```

### Step 4: Verify the API key works

```python
import anthropic

client = anthropic.Anthropic()  # Reads ANTHROPIC_API_KEY from environment

message = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=100,
    messages=[{"role": "user", "content": "Say hello!"}]
)
print(message.content[0].text)
```

If you see a response, your API key works. If you see an authentication error, double-check the environment variable.

---

## Stage 1 — Understand the Message Format

**Concept applied:** The Claude API uses a structured message format. Every request includes a list of messages — alternating between "user" and "assistant" roles. This list is the conversation history, and it is what gives the model its apparent memory.

### Step 5: The messages array

```python
# A single-turn conversation (no history)
messages = [
    {"role": "user", "content": "What is AI?"}
]

# A two-turn conversation (with history)
messages = [
    {"role": "user",      "content": "What is AI?"},
    {"role": "assistant", "content": "AI is pattern recognition at scale..."},
    {"role": "user",      "content": "Can you give an example?"},
]
```

The model receives the **entire list** on every API call. It does not remember previous calls — you send the history yourself each time.

<details><summary>💡 Hint — what does the system prompt look like?</summary>

The system prompt is separate from the messages array. It appears as a `system` parameter in the API call:

```python
client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    system="You are a helpful assistant with a dry sense of humor.",
    messages=messages
)
```

The system prompt is not visible to the user and is prepended to every request automatically.

</details>

---

## Stage 2 — Non-Streaming Response (Baseline)

**Goal:** Make a basic API call and print the full response.

**Concept applied:** Before adding streaming, get the basic flow working. The model generates the entire response and sends it back as one block.

### Step 6: Make a basic API call

```python
import anthropic

def chat_once(client, messages: list, system_prompt: str) -> str:
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        system=system_prompt,
        messages=messages
    )
    return response.content[0].text

client = anthropic.Anthropic()
messages = [{"role": "user", "content": "What is backpropagation?"}]
reply = chat_once(client, messages, "You are a helpful AI tutor.")
print(reply)
```

### Step 7: Add the assistant's reply to the history

The key insight: after the model replies, you add both the user message AND the assistant reply to the history before the next turn.

```python
user_message = "What is gradient descent?"
messages.append({"role": "user", "content": user_message})

reply = chat_once(client, messages, system_prompt)

messages.append({"role": "assistant", "content": reply})
# Now messages has 2 entries. The next call will include this context.
```

<details><summary>💡 Hint — why must I add both messages?</summary>

The API requires strict alternation: user, assistant, user, assistant. If you send two consecutive user messages, the API will return an error. Every time the model responds, you must append its response with `role: "assistant"` before sending the next user message.

</details>

<details><summary>✅ Answer — the full two-turn exchange</summary>

```python
messages = []
messages.append({"role": "user", "content": "What is gradient descent?"})
reply = chat_once(client, messages, "You are an AI tutor.")
messages.append({"role": "assistant", "content": reply})

messages.append({"role": "user", "content": "Give me a concrete analogy."})
reply2 = chat_once(client, messages, "You are an AI tutor.")
messages.append({"role": "assistant", "content": reply2})
# reply2 will reference the previous exchange
```

</details>

---

## Stage 3 — Streaming Responses

**Goal:** Print tokens as they arrive instead of waiting for the full response.

**Concept applied:** LLMs generate text one token at a time. Streaming lets you display tokens as they are produced. Without streaming, the user stares at a blank screen for several seconds. With streaming, they see words appearing immediately.

### Step 8: Use the streaming context manager

```python
def chat_streaming(client, messages: list, system_prompt: str) -> str:
    full_response = ""

    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=1024,
        system=system_prompt,
        messages=messages
    ) as stream:
        for text_chunk in stream.text_stream:
            print(text_chunk, end="", flush=True)
            full_response += text_chunk

    print()  # Newline after the streaming completes
    return full_response
```

<details><summary>💡 Hint — why flush=True?</summary>

Without `flush=True`, Python buffers the output and prints it all at once anyway, defeating the purpose of streaming. The `flush=True` argument forces Python to write the chunk to the terminal immediately, even before the line is complete.

</details>

<details><summary>✅ Answer — test the streaming output</summary>

```python
messages = [{"role": "user", "content": "Explain attention in transformers simply."}]
reply = chat_streaming(client, messages, "You are a helpful AI tutor.")
```

You should see words appearing one by one (or in small chunks) as the model generates them. If it prints all at once, check that `flush=True` is present.

</details>

---

## Stage 4 — Rolling Memory

**Goal:** Keep only the last N messages to prevent exceeding the context window.

**Concept applied:** The context window is the maximum total tokens (input + output) the model can handle in one call. If your conversation history grows unbounded, you will eventually hit the limit and get an error. Keeping only the last N message pairs is the simplest solution.

### Step 9: Implement the memory window

```python
MAX_HISTORY = 20  # Keep last 20 messages (10 turns)

def trim_history(messages: list, max_messages: int) -> list:
    if len(messages) > max_messages:
        messages = messages[-max_messages:]
    return messages
```

### Step 10: Apply the trim after each turn

```python
# After adding both user message and assistant reply:
messages = trim_history(messages, MAX_HISTORY)
```

<details><summary>💡 Hint — why trim from the front?</summary>

You always want to keep the most recent context. The model needs to know what was just said to give a coherent reply. Older turns are less important. Trimming from the front (keeping `messages[-max_messages:]`) preserves the most recent conversation.

</details>

---

## Stage 5 — Slash Commands

**Goal:** Add `/clear`, `/history`, and `/quit` as special commands.

**Concept applied:** Real applications need control commands that do not go to the model. The chatbot must intercept these before sending to the API.

### Step 11: Implement command handling

```python
def handle_command(user_input: str, messages: list) -> tuple:
    stripped = user_input.strip().lower()

    if stripped in ("/quit", "/exit"):
        print("Goodbye!")
        return False, messages  # Signal to exit the loop

    elif stripped == "/clear":
        messages = []
        print("[Conversation history cleared. Starting fresh.]\n")
        return True, messages

    elif stripped == "/history":
        if not messages:
            print("[No conversation history yet.]\n")
        else:
            print("\n--- Conversation History ---")
            for msg in messages:
                role = "You" if msg["role"] == "user" else "Claude"
                print(f"{role}: {msg['content'][:100]}...")
            print("---\n")
        return True, messages

    return None, messages  # Not a command — return None to signal normal processing
```

<details><summary>💡 Hint — what do the three return values mean?</summary>

The function returns a tuple `(is_command, messages)` where:
- `False` means the user typed `/quit` — the caller should break out of the loop
- `True` means a command was handled — the caller should `continue` to skip the API call
- `None` means the input was not a command — the caller should fall through to the API

</details>

---

## Stage 6 — Main Chat Loop

**Goal:** Wire everything together into a working CLI chatbot.

### Step 12: Implement the main loop

```python
def run_chatbot(system_prompt: str, max_history: int = 20):
    client = anthropic.Anthropic()
    messages = []

    print("=" * 50)
    print(f"  Claude CLI Chatbot  |  claude-opus-4-6")
    print(f"  /clear = reset  |  /history = view  |  /quit = exit")
    print("=" * 50)
    print(f"\nSystem: {system_prompt}\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        is_command, messages = handle_command(user_input, messages)
        if is_command is False:
            break
        if is_command is True:
            continue

        messages.append({"role": "user", "content": user_input})

        print("\nClaude: ", end="", flush=True)
        try:
            reply = chat_streaming(client, messages, system_prompt)
        except anthropic.APIError as e:
            print(f"\n[API Error: {e}]")
            messages.pop()  # Remove the failed user message from history
            continue

        messages.append({"role": "assistant", "content": reply})
        messages = trim_history(messages, max_history)
        print()
```

### Step 13: Add entry point and run

```python
if __name__ == "__main__":
    SYSTEM_PROMPT = (
        "You are a helpful AI tutor specializing in machine learning and AI. "
        "Explain concepts clearly using analogies. Keep answers concise unless "
        "asked to go deeper. Occasionally use dry humor."
    )
    run_chatbot(system_prompt=SYSTEM_PROMPT, max_history=20)
```

```bash
python chatbot.py
```

Test it:
1. Ask a question — you should see streaming output
2. Ask a follow-up that references the first question — the model should remember
3. Type `/clear` and ask the same follow-up — the model should have no context
4. Type `/history` to see the message list
5. Type `/quit` to exit

---

## Stage 7 — Error Handling

**Goal:** Handle API errors gracefully without crashing.

### Step 14: Common errors to handle

```python
try:
    reply = chat_streaming(client, messages, system_prompt)
except anthropic.AuthenticationError:
    print("[Error: Invalid API key. Check ANTHROPIC_API_KEY environment variable.]")
except anthropic.RateLimitError:
    print("[Error: Rate limit exceeded. Wait a moment and try again.]")
except anthropic.APIConnectionError:
    print("[Error: Could not connect to the API. Check your internet connection.]")
except anthropic.APIError as e:
    print(f"[API Error: {e}]")
```

<details><summary>💡 Hint — which errors are most common?</summary>

- `AuthenticationError`: your `ANTHROPIC_API_KEY` is not set or is incorrect
- `RateLimitError`: you sent too many requests too quickly — wait a few seconds
- `APIConnectionError`: no internet connection, or the Anthropic API is down

</details>

---

## Extension Ideas

### Extension 1 — Token Counter

```python
def estimate_tokens(messages: list) -> int:
    """Rough estimate: ~4 characters per token."""
    total_chars = sum(len(m["content"]) for m in messages)
    return total_chars // 4

# In the loop after each turn:
print(f"[~{estimate_tokens(messages)} tokens in context]\n")
```

### Extension 2 — Conversation Saver

```python
import json
from datetime import datetime

def save_conversation(messages: list) -> str:
    filename = f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w") as f:
        json.dump(messages, f, indent=2)
    return filename
```

---

## 📂 Navigation

| File | |
|---|---|
| [01_MISSION.md](./01_MISSION.md) | Context and objectives |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design and diagrams |
| **03_GUIDE.md** | You are here |
| [src/starter.py](./src/starter.py) | Starter code with TODOs |
| [04_RECAP.md](./04_RECAP.md) | What you built and what comes next |
