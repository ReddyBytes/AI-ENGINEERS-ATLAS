# Project 4 — LLM Chatbot with Memory

## The Story: Why This Project Matters

You've spent three projects understanding data and models from the inside out. Now you're going to use the most powerful AI systems in the world — large language models — without building them from scratch.

Here's the thing: calling an LLM API is not magic, and it's not as simple as it looks. When you type a message to ChatGPT or Claude on a website, there's engineering happening behind the scenes. The chat interface remembers what you said before. Each new message is actually sent to the model alongside the entire conversation history. The model streams its response token by token so you don't wait 10 seconds staring at a blank screen.

And none of that happens automatically when you use an API. You have to build it.

This project teaches you the mechanics of building real LLM applications. You'll understand context windows — why a chatbot "forgets" things after a long conversation. You'll understand streaming — how to make your app feel instant. You'll understand system prompts — the hidden instructions that shape the model's behavior.

These are the skills every developer uses when building AI-powered products. After this project, you'll be able to read the code of any LLM application and understand exactly what's happening.

---

## What You'll Build

A command-line chatbot using the Anthropic Claude API that:

1. Maintains a rolling conversation history (last N messages)
2. Streams responses in real time — words appear as Claude generates them
3. Has a customizable system prompt that sets the chatbot's persona
4. Supports a `/clear` command to reset conversation history
5. Supports a `/history` command to print the current conversation
6. Gracefully handles API errors and keyboard interrupts

---

## Learning Objectives

By completing this project, you will be able to:

- Call the Anthropic Claude API from Python and handle the response
- Explain what a system prompt is and how it controls model behavior
- Describe how multi-turn conversation history is sent to the API
- Implement streaming responses and explain why they improve user experience
- Explain the context window and why you need to limit conversation history
- Handle common API errors gracefully

---

## Topics Covered

| Phase | Topic | Concept Applied |
|---|---|---|
| Phase 6 | How LLMs Generate Text (Topic 21) | Tokens, sampling, why the response is streamed |
| Phase 6 | Context Windows & Tokens (Topic 24) | Why we only keep the last N messages |
| Phase 7 | Prompt Engineering (Topic 26) | Writing an effective system prompt |
| Phase 7 | Using LLM APIs (Topic 27) | Making API calls, message format, authentication |
| Phase 7 | Streaming Responses (Topic 30) | Streaming the response token by token |

---

## Prerequisites

- Completed Projects 1–3 (or comfortable with Python)
- Python 3.9+
- An Anthropic API key — get one at console.anthropic.com
- Library: `anthropic` Python SDK

---

## Difficulty

Medium — 3–4 hours. The API mechanics are new but the code is short. Most time is spent understanding how the messages array works.

---

## Tools & Libraries

| Tool | Purpose |
|---|---|
| `anthropic` Python SDK | Connects to Claude API, handles auth, streaming |
| Python `os` | Read API key from environment variable |
| Python standard library | No other dependencies needed |

---

## Expected Interaction

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

The "gradient" is the slope (how steep is it here?), and "descent" means
you're going downhill. Put them together and you've got the entire learning
algorithm of most AI systems, give or take a few billion parameters.

You: Can you give me a concrete analogy?

Claude: Sure. Imagine you're blindfolded on a hilly terrain and told to
find the lowest valley. You can feel the slope under your feet. You take
small steps in whichever direction feels most downhill. Eventually — if the
terrain isn't too weird and your steps aren't too large — you reach a valley.

That's gradient descent. The "terrain" is your loss function. Your position
is the current weights. The blindfold is the fact that you can't see the
full landscape, only the local slope.

You: /clear

[Conversation history cleared. Starting fresh.]

You: /quit

Goodbye!
```

---

## Key Learning: Concepts You'll Apply

- **System prompt**: A message with `role: "system"` that shapes the model's personality and instructions — sent on every request, never shown to the user
- **Message history**: The `messages` array sent to the API must include all previous turns — the model has no built-in memory between calls
- **Context window**: Claude has a limit on total tokens (input + output). Keeping only the last N messages prevents exceeding the limit
- **Streaming**: Using `client.messages.stream()` lets you print tokens as they arrive — users see the response build character by character
- **Token budget**: Every message costs tokens. Long histories are expensive and eventually exceed the context window

---

## Extension Challenges

1. Add a `/tokens` command that estimates the number of tokens used by the current conversation history
2. Add a `/save` command that writes the conversation to a JSON file
3. Add a `--model` command-line argument so you can switch between Claude models
4. Add support for the user to change the system prompt mid-conversation with `/system <new prompt>`

---

## 📂 Navigation

| File | |
|---|---|
| **Project_Guide.md** | You are here — overview and objectives |
| [Step_by_Step.md](./Step_by_Step.md) | Detailed build instructions |
| [Starter_Code.md](./Starter_Code.md) | Python starter code with TODOs |
| [Architecture_Blueprint.md](./Architecture_Blueprint.md) | System diagram |

**Project Series:** Project 4 of 5 — Beginner Projects
⬅️ **Previous:** [03 — Neural Net from Scratch](../03_Neural_Net_from_Scratch/Project_Guide.md)
➡️ **Next:** [05 — Intelligent Document Analyzer](../05_Intelligent_Document_Analyzer/Project_Guide.md)
