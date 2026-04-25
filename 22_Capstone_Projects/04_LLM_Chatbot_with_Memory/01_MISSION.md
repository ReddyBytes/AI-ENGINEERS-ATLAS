# Project 4 — LLM Chatbot with Memory

## The Story

You have been using chat interfaces your whole career. Every time you open a new browser tab and type a message to an AI, something invisible happens: the application sends your entire conversation history along with your new message. The model does not remember anything. Your code does.

This project is about pulling back the curtain. When ChatGPT "remembers" what you said three turns ago, a list of message objects is being assembled and sent on every request. When responses appear word by word instead of all at once, that is streaming — the model's output is piped to your screen as tokens are generated, not after the whole response is done.

These mechanics are invisible to end users but central to every LLM application developer. After this project, you will be able to read the source code of any AI chat product and understand exactly what is happening at each line.

---

## What You Build

A command-line chatbot using the Anthropic Claude API that:

1. Maintains a rolling conversation history (last N messages)
2. Streams responses in real time — words appear as Claude generates them
3. Has a customizable system prompt that sets the chatbot's persona
4. Supports `/clear` to reset conversation history
5. Supports `/history` to print the current conversation
6. Gracefully handles API errors and keyboard interrupts

---

## Concepts Covered

| Phase | Topic | Concept Applied |
|---|---|---|
| Phase 6 | How LLMs Generate Text | Tokens, sampling, why the response is streamed |
| Phase 6 | Context Windows and Tokens | Why we only keep the last N messages |
| Phase 7 | Prompt Engineering | Writing an effective system prompt |
| Phase 7 | Using LLM APIs | Making API calls, message format, authentication |
| Phase 7 | Streaming Responses | Streaming the response token by token |

---

## Prerequisites

- Completed Projects 1–3 (or comfortable with Python)
- Python 3.9+
- An Anthropic API key — get one at console.anthropic.com
- Library: `anthropic` Python SDK

---

## What Success Looks Like

```
=================================================
  Claude CLI Chatbot  |  Model: claude-opus-4-6
  Type /clear to reset | /history to view | /quit to exit
=================================================

System: You are a helpful assistant with a dry sense of humor.

You: What is gradient descent?

Claude: Gradient descent is how neural networks learn — the mathematical
equivalent of feeling around in the dark for the lowest point on a floor.
You nudge your parameters in the direction that makes your loss function
decrease, take a small step, then repeat a few thousand times.

You: Can you give me a concrete analogy?

Claude: Sure. Imagine you are blindfolded on a hilly terrain and told to
find the lowest valley. You can feel the slope under your feet...

You: /clear

[Conversation history cleared. Starting fresh.]

You: /quit

Goodbye!
```

---

## Learning Format

**Difficulty:** Medium — 3 to 4 hours

**Format:** The build is short in code but high in concept density. Most time is spent understanding how the messages array works and why streaming requires `flush=True`. Each function is small and independently testable.

---

## Key Terms

- **System prompt**: A message with `role: "system"` that shapes the model's personality — sent on every request, never shown to the user
- **Message history**: The `messages` array must include all previous turns — the model has no built-in memory between API calls
- **Context window**: Claude has a limit on total tokens (input + output); keeping only the last N messages prevents exceeding it
- **Streaming**: `client.messages.stream()` lets you print tokens as they arrive — users see the response build character by character
- **Token budget**: Every message costs tokens; long histories are expensive and eventually hit the context limit

---

## 📂 Navigation

| File | |
|---|---|
| **01_MISSION.md** | You are here |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design and diagrams |
| [03_GUIDE.md](./03_GUIDE.md) | Step-by-step build guide |
| [src/starter.py](./src/starter.py) | Starter code with TODOs |
| [04_RECAP.md](./04_RECAP.md) | What you built and what comes next |

**Project Series:** Project 4 of 5 — Beginner Projects
⬅️ **Previous:** [03 — Neural Net from Scratch](../03_Neural_Net_from_Scratch/01_MISSION.md)
➡️ **Next:** [05 — Intelligent Document Analyzer](../05_Intelligent_Document_Analyzer/01_MISSION.md)
