# Project 4 — Starter Code

Copy this to `chatbot.py`. Fill in every `# TODO:` section.

---

```python
"""
Project 4 — LLM Chatbot with Memory
======================================
A CLI chatbot using the Anthropic Claude API.
Features: streaming responses, rolling conversation history,
system prompt, /clear and /history commands.

Setup:
    export ANTHROPIC_API_KEY="sk-ant-your-key-here"
    pip install anthropic
    python chatbot.py
"""

import anthropic
import os


# ============================================================
# CONFIGURATION
# ============================================================

MODEL = "claude-opus-4-6"
MAX_TOKENS = 1024
MAX_HISTORY = 20  # Keep last 20 messages (10 conversation turns)

SYSTEM_PROMPT = (
    "You are a helpful AI tutor specializing in machine learning and AI. "
    "Explain concepts clearly using real-world analogies. Keep answers concise "
    "unless asked to go deeper. You may occasionally use dry humor."
)


# ============================================================
# SECTION 1 — API CLIENT SETUP
# ============================================================

def create_client() -> anthropic.Anthropic:
    """
    Create and return an Anthropic client.
    Reads the API key from the ANTHROPIC_API_KEY environment variable.
    Raises an error if the key is not set.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY environment variable is not set.\n"
            "Get your key at console.anthropic.com and run:\n"
            "  export ANTHROPIC_API_KEY='sk-ant-your-key-here'"
        )
    # The Anthropic client automatically reads ANTHROPIC_API_KEY from the environment
    return anthropic.Anthropic()


# ============================================================
# SECTION 2 — STREAMING RESPONSE
# ============================================================

def chat_streaming(client: anthropic.Anthropic,
                   messages: list,
                   system_prompt: str) -> str:
    """
    Send the messages to Claude and stream the response.
    Prints each text chunk as it arrives (token by token).

    Args:
        client:        Anthropic client instance
        messages:      list of {"role": ..., "content": ...} dicts
        system_prompt: the system prompt string

    Returns:
        full_response: the complete response text as a single string

    How streaming works:
        client.messages.stream() returns a context manager.
        Iterating over stream.text_stream yields text chunks as the
        model generates them. You print each chunk immediately with
        flush=True to bypass Python's output buffering.
    """
    full_response = ""

    # TODO: Use client.messages.stream() as a context manager
    # Pass: model=MODEL, max_tokens=MAX_TOKENS, system=system_prompt, messages=messages
    # Inside the with block, iterate over stream.text_stream
    # For each text_chunk:
    #   1. print it with end="" and flush=True (no newline, flush immediately)
    #   2. append it to full_response
    # After the with block, print a newline with print()

    # Hint structure:
    # with client.messages.stream(...) as stream:
    #     for text_chunk in stream.text_stream:
    #         print(text_chunk, end="", flush=True)
    #         full_response += text_chunk
    # print()

    pass  # TODO: replace with your implementation

    return full_response


# ============================================================
# SECTION 3 — CONVERSATION HISTORY MANAGEMENT
# ============================================================

def add_user_message(messages: list, content: str) -> list:
    """
    Append a user message to the conversation history.

    Args:
        messages: current conversation history list
        content:  the user's message string

    Returns:
        updated messages list

    The message format is: {"role": "user", "content": content}
    """
    # TODO: append {"role": "user", "content": content} to messages
    # return the updated messages list
    pass  # TODO: replace


def add_assistant_message(messages: list, content: str) -> list:
    """
    Append an assistant message to the conversation history.

    Args:
        messages: current conversation history list
        content:  the assistant's response string

    Returns:
        updated messages list

    The message format is: {"role": "assistant", "content": content}
    """
    # TODO: append {"role": "assistant", "content": content} to messages
    # return the updated messages list
    pass  # TODO: replace


def trim_history(messages: list, max_messages: int) -> list:
    """
    Keep only the most recent max_messages messages.
    Trims from the front when the list exceeds the limit.

    This prevents the conversation history from exceeding the
    model's context window over long conversations.

    Args:
        messages:     current conversation history
        max_messages: maximum number of messages to keep

    Returns:
        trimmed messages list (unchanged if already within limit)
    """
    # TODO: if len(messages) > max_messages, return messages[-max_messages:]
    # otherwise return messages unchanged
    pass  # TODO: replace


# ============================================================
# SECTION 4 — SLASH COMMAND HANDLER
# ============================================================

def handle_command(user_input: str, messages: list) -> tuple:
    """
    Check if the user input is a slash command and handle it.

    Supported commands:
        /quit or /exit — exit the chatbot
        /clear         — reset conversation history
        /history       — print the conversation so far

    Args:
        user_input: the raw string the user typed
        messages:   current conversation history

    Returns:
        (is_command, updated_messages) where:
            is_command = False  → user typed /quit (caller should exit)
            is_command = True   → command was handled (caller should continue)
            is_command = None   → not a command (caller should call the API)
    """
    stripped = user_input.strip().lower()

    # TODO: Handle /quit and /exit
    # Print "Goodbye!" and return (False, messages)
    if stripped in ("/quit", "/exit"):
        pass  # TODO

    # TODO: Handle /clear
    # Reset messages to an empty list []
    # Print "[Conversation history cleared. Starting fresh.]\n"
    # Return (True, [])
    elif stripped == "/clear":
        pass  # TODO

    # TODO: Handle /history
    # If messages is empty, print "[No conversation history yet.]\n"
    # Otherwise print each message in a readable format:
    #   "You: {first 100 chars of content}..." for user messages
    #   "Claude: {first 100 chars of content}..." for assistant messages
    # Return (True, messages)
    elif stripped == "/history":
        pass  # TODO

    # Not a command — return None to signal normal processing
    return None, messages


# ============================================================
# SECTION 5 — MAIN CHAT LOOP
# ============================================================

def run_chatbot(system_prompt: str = SYSTEM_PROMPT,
                max_history: int = MAX_HISTORY) -> None:
    """
    Main chatbot loop. Runs until the user types /quit or presses Ctrl+C.

    Loop structure:
        1. Read user input
        2. Check for slash commands (/clear, /history, /quit)
        3. If not a command: add to history, call API with streaming, add reply to history
        4. Trim history to max_history
        5. Repeat
    """
    # TODO: Create the Anthropic client using create_client()
    client = None  # TODO

    messages = []

    # Print welcome header
    print("=" * 52)
    print(f"  Claude CLI Chatbot  |  Model: {MODEL}")
    print(f"  /clear = reset  |  /history = view  |  /quit = exit")
    print("=" * 52)
    print(f"\nSystem: {system_prompt}\n")

    while True:
        # Read user input (handle Ctrl+C gracefully)
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        # Skip empty input
        if not user_input:
            continue

        # TODO: Call handle_command(user_input, messages)
        # Store the result as: is_command, messages = handle_command(...)
        # If is_command is False: break (user wants to quit)
        # If is_command is True: continue (command was handled, no API call needed)
        # If is_command is None: fall through to the API call
        is_command, messages = None, messages  # TODO: replace this line
        if is_command is False:
            break
        if is_command is True:
            continue

        # TODO: Add the user's message to history using add_user_message()
        messages = None  # TODO: add_user_message(messages, user_input)

        # Call the API with streaming
        print(f"\nClaude: ", end="", flush=True)
        try:
            # TODO: Call chat_streaming(client, messages, system_prompt)
            # Store the result in `reply`
            reply = None  # TODO

        except anthropic.AuthenticationError:
            print("[Error: Invalid API key. Check ANTHROPIC_API_KEY.]")
            messages = messages[:-1]  # Remove the failed user message
            continue
        except anthropic.RateLimitError:
            print("[Error: Rate limit hit. Please wait a moment.]")
            messages = messages[:-1]
            continue
        except anthropic.APIConnectionError:
            print("[Error: Could not connect. Check your internet connection.]")
            messages = messages[:-1]
            continue
        except anthropic.APIError as e:
            print(f"[API Error: {e}]")
            messages = messages[:-1]
            continue

        # TODO: Add the assistant's reply to history using add_assistant_message()
        messages = None  # TODO: add_assistant_message(messages, reply)

        # TODO: Trim history using trim_history(messages, max_history)
        messages = None  # TODO

        print()  # Extra blank line between turns


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    run_chatbot()
```

---

## What You Need to Fill In

| Function | What to implement | Key concept |
|---|---|---|
| `create_client()` | Already done — just understand how it works | API authentication |
| `chat_streaming()` | `client.messages.stream()` context manager loop | Streaming tokens |
| `add_user_message()` | Append `{"role": "user", "content": ...}` | Message format |
| `add_assistant_message()` | Append `{"role": "assistant", "content": ...}` | Message format |
| `trim_history()` | Return `messages[-max_messages:]` if too long | Context window |
| `handle_command()` | Check for `/quit`, `/clear`, `/history` | Control flow |
| `run_chatbot()` | Wire all functions together in the loop | Integration |

---

## How to Run

```bash
# Set your API key
export ANTHROPIC_API_KEY="sk-ant-your-key-here"

# Install the SDK
pip install anthropic

# Run the chatbot
python chatbot.py
```

---

## Checking Your Work

1. When you type a message, you should see Claude's response stream word by word
2. When you ask a follow-up ("what did you just say?"), Claude should remember the previous response
3. After `/clear`, follow-ups should have no context
4. `/history` should show the current conversation
5. `/quit` should exit cleanly

---

## Common Mistakes

| Problem | Likely cause |
|---|---|
| `AuthenticationError` | API key not set or incorrect |
| Response prints all at once (no streaming) | Missing `flush=True` in print |
| Model doesn't remember previous messages | `messages` not being updated correctly |
| History grows forever | `trim_history()` not called or not working |

---

## 📂 Navigation

| File | |
|---|---|
| [Project_Guide.md](./Project_Guide.md) | Overview and objectives |
| [Step_by_Step.md](./Step_by_Step.md) | Detailed build instructions |
| **Starter_Code.md** | You are here |
| [Architecture_Blueprint.md](./Architecture_Blueprint.md) | System diagram |
