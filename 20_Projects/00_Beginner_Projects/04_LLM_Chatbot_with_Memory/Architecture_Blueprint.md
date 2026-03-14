# Project 4 — Architecture Blueprint

## System Overview

This project is a **stateful CLI application** built around the Anthropic API. The key insight is that the model itself is stateless — it has no memory between API calls. All memory management happens in your code.

---

## System Diagram

```mermaid
flowchart TD
    A[User types message\nin terminal] --> B{Is it a\nslash command?}

    B -- /clear --> C[Reset messages list\nto empty]
    B -- /history --> D[Print current\nconversation history]
    B -- /quit --> E[Exit the loop]
    B -- normal message --> F[add_user_message\nAppend to history]

    F --> G[trim_history\nKeep last N messages]
    G --> H[chat_streaming\nclient.messages.stream]

    H --> I[Anthropic API\nClaude claude-opus-4-6]
    I -- token stream --> J[Print each chunk\nflush=True]
    J --> K[Accumulate full_response]
    K --> L[add_assistant_message\nAppend reply to history]
    L --> G2[trim_history again]
    G2 --> A

    C --> A
    D --> A
```

---

## Message History: What Gets Sent to the API

```mermaid
sequenceDiagram
    participant User
    participant App as chatbot.py
    participant Memory as messages list
    participant API as Anthropic API

    User->>App: "What is backprop?"
    App->>Memory: Append {role:user, content:...}
    App->>API: POST /messages\n{system:..., messages:[turn1]}
    API-->>App: Stream tokens...
    App-->>User: Print tokens live
    App->>Memory: Append {role:assistant, content:...}

    User->>App: "Can you explain more?"
    App->>Memory: Append {role:user, content:...}
    App->>API: POST /messages\n{system:..., messages:[turn1, turn2]}
    API-->>App: Stream tokens (with context)...
    App-->>User: Print tokens live
    App->>Memory: Append {role:assistant, content:...}
```

The model receives the FULL history on every request. It has no persistent state.

---

## Context Window Management

```mermaid
flowchart LR
    subgraph Context["Context Window (200K tokens for Claude)"]
        SP[System Prompt\n~100 tokens]
        H1[Turn 1 user + assistant\n~300 tokens]
        H2[Turn 2 user + assistant\n~400 tokens]
        Dots[...\nolder turns get trimmed]
        HN[Turn N user + assistant\n~300 tokens]
    end

    TrimRule["trim_history rule:\nKeep last 20 messages\n= 10 conversation turns"]
    TrimRule --> Dots
```

---

## Component Table

| Component | Function | Role | Key Detail |
|---|---|---|---|
| CLI Input | `input("You: ")` | Reads user messages from terminal | Handles Ctrl+C via try/except |
| Command Router | `handle_command()` | Intercepts /clear, /history, /quit | Returns (is_command, messages) tuple |
| Message Builder | `add_user_message()` / `add_assistant_message()` | Maintains the messages list | Messages always alternate user/assistant |
| History Trimmer | `trim_history()` | Caps context window usage | Removes oldest messages from the front |
| Streaming Client | `chat_streaming()` | Calls the API with streaming | Uses `client.messages.stream()` context manager |
| Anthropic SDK | `anthropic.Anthropic()` | HTTP client for the Claude API | Reads key from ANTHROPIC_API_KEY env var |
| Claude API | Remote service | Generates the actual text | Stateless: receives full history each call |
| Error Handler | try/except in `run_chatbot()` | Handles API errors gracefully | Removes failed message from history |

---

## The Messages Array State Over Time

```mermaid
stateDiagram-v2
    [*] --> Empty: App starts
    Empty --> Turn1: User sends first message
    Turn1 --> Turn1Done: Claude replies, reply appended
    Turn1Done --> Turn2: User sends second message
    Turn2 --> Turn2Done: Claude replies

    Turn2Done --> Trimmed: trim_history fires\nif > MAX_HISTORY messages

    Trimmed --> TurnN: Conversation continues...

    Turn1Done --> Empty: /clear command
    TurnN --> Empty: /clear command
    Empty --> [*]: /quit command
```

---

## Streaming: How It Works

```mermaid
flowchart TD
    A[client.messages.stream called] --> B[API starts generating\ntokens server-side]
    B --> C{Token ready?}
    C -- yes --> D[Send token chunk\nover HTTP stream]
    D --> E[print chunk\nend=  flush=True]
    E --> F[Append to full_response string]
    F --> C
    C -- generation done --> G[Context manager exits]
    G --> H[Return full_response]
```

Without streaming (`client.messages.create`): user waits for all tokens before seeing any output.
With streaming (`client.messages.stream`): user sees tokens appear immediately, response feels instant.

---

## Folder Structure

```
04_LLM_Chatbot_with_Memory/
├── chatbot.py              ← Your main Python script
├── Project_Guide.md
├── Step_by_Step.md
├── Starter_Code.md
└── Architecture_Blueprint.md
```

---

## Concepts Map

```mermaid
flowchart TD
    T21[Topic 21 — How LLMs Generate Text] --> C1[chat_streaming\nTokens printed one by one]
    T24[Topic 24 — Context Windows] --> C2[trim_history\nKeep last N messages only]
    T26[Topic 26 — Prompt Engineering] --> C3[SYSTEM_PROMPT constant\nShapes Claude behavior]
    T27[Topic 27 — Using LLM APIs] --> C4[anthropic.Anthropic client\nmessages format user/assistant]
    T30[Topic 30 — Streaming] --> C5[client.messages.stream\nstream.text_stream iterator]
    C1 --> R[Working chatbot\nwith memory and streaming]
    C2 --> R
    C3 --> R
    C4 --> R
    C5 --> R
```

---

## 📂 Navigation

| File | |
|---|---|
| [Project_Guide.md](./Project_Guide.md) | Overview and objectives |
| [Step_by_Step.md](./Step_by_Step.md) | Detailed build instructions |
| [Starter_Code.md](./Starter_Code.md) | Python starter code with TODOs |
| **Architecture_Blueprint.md** | You are here |
