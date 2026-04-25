"""
Project 4 — LLM Chatbot with Memory
======================================
A CLI chatbot using the Anthropic Claude API.
Features: streaming responses, rolling conversation history,
system prompt, /clear and /history commands.

Setup:
    export ANTHROPIC_API_KEY="sk-ant-your-key-here"
    pip install anthropic
    python starter.py
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
    return anthropic.Anthropic()  # ← reads ANTHROPIC_API_KEY automatically


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

    # TODO: Use client.messages.stream() as a context manager.
    # Pass: model=MODEL, max_tokens=MAX_TOKENS, system=system_prompt, messages=messages
    # Inside the with block, iterate over stream.text_stream.
    # For each text_chunk:
    #   1. print it with end="" and flush=True  ← no newline, flush immediately
    #   2. append it to full_response
    # After the with block, print a newline with print()

    # Structure to implement:
    # with client.messages.stream(...) as stream:
    #     for text_chunk in stream.text_stream:
    #         print(text_chunk, end="", flush=True)  # ← flush bypasses buffering
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

    The message format is: {"role": "user", "content": content}
    Messages must alternate: user, assistant, user, assistant...
    """
    # TODO: append {"role": "user", "content": content} to messages
    # return the updated messages list
    pass  # TODO: replace


def add_assistant_message(messages: list, content: str) -> list:
    """
    Append an assistant message to the conversation history.

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

    Example: if max_messages=4 and messages has 6 items,
    return messages[-4:]  ← keep the last 4
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
        /quit or /exit  — exit the chatbot
        /clear          — reset conversation history
        /history        — print the conversation so far

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
    return None, messages  # ← None means: fall through to API call


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
        3. If not a command: add to history, call API with streaming, add reply
        4. Trim history to max_history
        5. Repeat
    """
    # TODO: Create the Anthropic client using create_client()
    client = None  # TODO: client = create_client()

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
        # Store result as: is_command, messages = handle_command(...)
        # If is_command is False: break  ← /quit
        # If is_command is True: continue  ← command handled
        # If is_command is None: fall through to API call
        is_command, messages = None, messages  # TODO: replace this line
        if is_command is False:
            break
        if is_command is True:
            continue

        # TODO: Add the user's message to history using add_user_message()
        messages = None  # TODO: messages = add_user_message(messages, user_input)

        # Call the API with streaming
        print(f"\nClaude: ", end="", flush=True)
        try:
            # TODO: Call chat_streaming(client, messages, system_prompt)
            # Store result in `reply`
            reply = None  # TODO: reply = chat_streaming(...)

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
        messages = None  # TODO: messages = add_assistant_message(messages, reply)

        # TODO: Trim history using trim_history(messages, max_history)
        messages = None  # TODO: messages = trim_history(messages, max_history)

        print()  # Extra blank line between turns


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    run_chatbot()
