# Project 4 — Recap

## What You Built

A command-line chatbot that connects to the Anthropic Claude API with streaming responses, rolling conversation memory, and a set of slash commands for controlling the session. The chatbot maintains a list of message objects that grows with each turn, sends the full list to the API on every request, and trims the oldest messages when the list exceeds a configured limit.

---

## Concepts Applied

| Concept | Where it appeared |
|---|---|
| API authentication | `ANTHROPIC_API_KEY` environment variable, read by the Anthropic SDK |
| Message format | `{"role": "user"/"assistant", "content": "..."}` dicts in the `messages` list |
| System prompt | Separate `system=` parameter, sent on every request, shapes model behavior |
| Streaming | `client.messages.stream()` context manager with `stream.text_stream` iterator |
| `flush=True` | Bypasses Python output buffering so tokens appear as they arrive |
| Context window | Hard limit on total tokens; rolling trim keeps the history within budget |
| `trim_history()` | `messages[-max_messages:]` — preserves recent context, discards the oldest |
| Slash commands | Pre-API interception: `/clear`, `/history`, `/quit` handled before the model sees input |
| Error handling | `anthropic.AuthenticationError`, `RateLimitError`, `APIConnectionError` — graceful recovery |
| Stateless API | The model has no memory; your code assembles and maintains the full conversation state |

---

## Extension Ideas

1. **Token counter**: Add a `/tokens` command that estimates the number of tokens in the current conversation history using the rough heuristic of 4 characters per token — or use `client.messages.count_tokens()` for an exact count.

2. **Conversation persistence**: Add a `/save` command that writes the conversation to a timestamped JSON file, and a `--load` command-line flag that resumes a saved conversation.

3. **Model switching**: Add a `--model` flag so you can swap between `claude-haiku-4-5` (fast/cheap) and `claude-opus-4-6` (most capable) at launch, and compare response quality and latency.

---

## Job Mapping

| Role | How this project maps |
|---|---|
| AI Application Developer | Every production LLM chat app is built on this exact pattern: history management, system prompts, streaming |
| ML Engineer | Streaming and context window management appear in every model inference pipeline |
| Backend Engineer | Stateless API + client-side state management is a core pattern in distributed systems |
| Product Engineer | Understanding streaming UX — why flush=True matters — is essential for building responsive AI products |
| Prompt Engineer | System prompt design and the relationship between persona, tone, and instructions |

---

## 📂 Navigation

| File | |
|---|---|
| [01_MISSION.md](./01_MISSION.md) | Context and objectives |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design and diagrams |
| [03_GUIDE.md](./03_GUIDE.md) | Step-by-step build guide |
| [src/starter.py](./src/starter.py) | Starter code with TODOs |
| **04_RECAP.md** | You are here |

**Project Series:** Project 4 of 5 — Beginner Projects
⬅️ **Previous:** [03 — Neural Net from Scratch](../03_Neural_Net_from_Scratch/01_MISSION.md)
➡️ **Next:** [05 — Intelligent Document Analyzer](../05_Intelligent_Document_Analyzer/01_MISSION.md)
