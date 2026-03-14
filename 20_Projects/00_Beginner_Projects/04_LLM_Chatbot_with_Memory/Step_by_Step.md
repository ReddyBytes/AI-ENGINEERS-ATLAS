# Project 4 — Step-by-Step Build Guide

## Overview

This project is shorter in code than the previous ones but requires understanding a new domain: API calls, authentication, and streaming. Each stage is testable independently.

**Total estimated time:** 3–4 hours, including reading API documentation.

---

## Before You Start — Environment Setup

### Step 1: Get your Anthropic API key

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Create an account or sign in
3. Navigate to API Keys and create a new key
4. Copy the key — you'll only see it once

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

**Concept applied:** The Claude API uses a structured message format. Every request you send includes a list of messages — alternating between "user" and "assistant" roles. This list is the conversation history, and it's what gives the model its memory.

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

The model receives the **entire list** on every API call. It doesn't remember previous calls — you send the history yourself each time.

### Step 6: The system prompt

The system prompt is separate from the messages array. It appears as a `system` parameter in the API call:

```python
client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    system="You are a helpful assistant with a dry sense of humor.",
    messages=messages
)
```

The system prompt:
- Is not visible to the user
- Is prepended to every request automatically by the API
- Sets the model's persona, tone, and any standing instructions

---

## Stage 2 — Non-Streaming Response (Baseline)

**Goal:** Make a basic API call and print the full response.

**Concept applied:** Before adding streaming, get the basic flow working. The model generates the entire response and sends it back as one block.

### Step 7: Make a basic API call

```python
import anthropic

def chat_once(client, messages: list, system_prompt: str) -> str:
    """Send messages and return the full response as a string."""
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

### Step 8: Add the assistant's reply to the history

The key insight: after the model replies, you add both the user message AND the assistant reply to the history before the next turn.

```python
# User sends a message
user_message = "What is gradient descent?"
messages.append({"role": "user", "content": user_message})

# Get the response
reply = chat_once(client, messages, system_prompt)

# Add the assistant's reply to history
messages.append({"role": "assistant", "content": reply})

# Now messages has 2 entries. The next call will include this context.
```

---

## Stage 3 — Streaming Responses

**Goal:** Print tokens as they arrive instead of waiting for the full response.

**Concept applied:** LLMs generate text one token at a time. Streaming lets you display tokens as they're produced. Without streaming, the user stares at a blank screen for several seconds. With streaming, they see words appearing immediately — the response feels instant.

### Step 9: Use the streaming context manager

```python
def chat_streaming(client, messages: list, system_prompt: str) -> str:
    """
    Stream the response and print tokens as they arrive.
    Returns the full response text when done.
    """
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

**Why `flush=True`?** Without it, Python buffers the output and prints it all at once anyway, defeating the purpose of streaming.

### Step 10: Test streaming

```python
messages = [{"role": "user", "content": "Explain attention in transformers simply."}]
reply = chat_streaming(client, messages, "You are a helpful AI tutor.")
```

You should see words appearing one by one (or in small chunks) as the model generates them.

---

## Stage 4 — Rolling Memory

**Goal:** Keep only the last N messages to prevent exceeding the context window.

**Concept applied:** The context window is the maximum total tokens (input + output) the model can handle in one call. If your conversation history grows unbounded, you'll eventually hit the limit and get an error. Keeping only the last N message pairs is the simplest solution.

### Step 11: Implement the memory window

```python
MAX_HISTORY = 20  # Keep last 20 messages (10 turns)

def trim_history(messages: list, max_messages: int) -> list:
    """
    Keep only the last max_messages messages.
    Always keeps pairs: trim from the front in pairs to maintain
    the user/assistant alternation pattern.
    """
    if len(messages) > max_messages:
        # Trim from the front, keep the most recent messages
        messages = messages[-max_messages:]
    return messages
```

### Step 12: Apply the trim after each turn

```python
# After adding both user message and assistant reply:
messages = trim_history(messages, MAX_HISTORY)
```

This ensures the conversation history never exceeds MAX_HISTORY entries.

---

## Stage 5 — Slash Commands

**Goal:** Add `/clear`, `/history`, and `/quit` as special commands.

**Concept applied:** Real applications need control commands that don't go to the model. The chatbot must intercept these before sending to the API.

### Step 13: Implement command handling

```python
def handle_command(user_input: str, messages: list) -> tuple[bool, list]:
    """
    Handle slash commands. Returns (should_continue, updated_messages).
    If is_command is True, the caller should skip the API call.
    """
    stripped = user_input.strip().lower()

    if stripped == "/quit" or stripped == "/exit":
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

---

## Stage 6 — Main Chat Loop

**Goal:** Wire everything together into a working CLI chatbot.

### Step 14: Implement the main loop

```python
def run_chatbot(system_prompt: str, max_history: int = 20):
    """Main chatbot loop."""
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

        # Handle slash commands
        is_command, messages = handle_command(user_input, messages)
        if is_command is False:
            break           # /quit was called
        if is_command is True:
            continue        # /clear or /history was handled

        # Normal message: add to history and send
        messages.append({"role": "user", "content": user_input})

        print("\nClaude: ", end="", flush=True)
        try:
            reply = chat_streaming(client, messages, system_prompt)
        except anthropic.APIError as e:
            print(f"\n[API Error: {e}]")
            messages.pop()  # Remove the failed user message from history
            continue

        # Add the reply to history
        messages.append({"role": "assistant", "content": reply})

        # Trim to keep within context window budget
        messages = trim_history(messages, max_history)
        print()
```

### Step 15: Add entry point

```python
if __name__ == "__main__":
    SYSTEM_PROMPT = (
        "You are a helpful AI tutor specializing in machine learning and AI. "
        "Explain concepts clearly using analogies. Keep answers concise unless "
        "asked to go deeper. Occasionally use dry humor."
    )
    run_chatbot(system_prompt=SYSTEM_PROMPT, max_history=20)
```

### Step 16: Run the chatbot

```bash
python chatbot.py
```

Test it:
1. Ask a question — you should see streaming output
2. Ask a follow-up that references the first question — the model should remember
3. Type `/clear` and ask the same follow-up — the model should have no context now
4. Type `/history` to see the message list
5. Type `/quit` to exit

---

## Stage 7 — Error Handling

**Goal:** Handle API errors gracefully without crashing.

### Step 17: Common errors to handle

```python
import anthropic

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

---

## Extension Ideas

### Extension 1 — Token Counter

Use `client.messages.count_tokens()` (or estimate at ~4 chars/token) to show token usage:

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
| [Project_Guide.md](./Project_Guide.md) | Overview and objectives |
| **Step_by_Step.md** | You are here |
| [Starter_Code.md](./Starter_Code.md) | Python starter code with TODOs |
| [Architecture_Blueprint.md](./Architecture_Blueprint.md) | System diagram |
