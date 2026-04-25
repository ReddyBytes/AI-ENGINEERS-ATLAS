# Project 08 — Multi-Tool Research Agent: Recap

## What You Built

A **ReAct agent** powered by Claude with three tools: `web_search` (DuckDuckGo, no API key), `wikipedia_summary` (Wikipedia API), and `calculator` (safe AST-based math evaluator). The agent receives a research question, reasons step by step, calls tools as needed, and produces a synthesized final answer. Conversation history is accumulated across turns so follow-up questions have context without re-searching. The main CLI loop supports `clear` to reset memory and a `max_tool_calls` guard to prevent infinite loops.

---

## Concepts Applied

| Concept | Where it appeared |
|---|---|
| Tool schema | JSON objects with `name`, `description`, `input_schema` passed to the API |
| ReAct loop | `while tool_call_count < MAX`: call API → if tool_use, execute → if end_turn, return |
| Tool result injection | `{"role": "user", "content": [{"type": "tool_result", "tool_use_id": block.id, ...}]}` |
| Multi-turn tool use | Agent may call 3+ tools before producing a final answer |
| Conversation memory | Full `conversation_history` list sent on every API call |
| Memory trimming | `trim_history()` drops oldest pairs when history exceeds threshold |
| Safe evaluation | `ast.parse()` + recursive `_safe_eval_node()` — only numeric ops, no `eval()` |
| Error recovery | `execute_tool()` wraps all tool calls in try/except — errors become observations |
| Tool description quality | Strong descriptions reduce tool misuse and improve multi-step reasoning |
| stop_reason handling | `"end_turn"` = final answer; `"tool_use"` = continue loop; others = error |

---

## Extension Ideas

1. **Add a file_reader tool**: Given a relative file path, read and return the content. Allows the agent to reason over local documents without a full RAG setup. Implement path sandboxing (only allow reads within a designated `./workspace/` folder) so the agent cannot read arbitrary files.

2. **Tool use logging**: Write every tool call (name, input, output, timestamp, turn number) to a JSONL file as a structured audit trail. After a session, load the log and calculate: how many calls per tool, average result length, which tool was called first most often.

3. **Streaming output**: Switch to the Anthropic streaming API (`client.messages.stream(...)`) so the agent's reasoning and final answer appear token by token rather than waiting for the full response. Add special handling to still capture tool_use blocks during streaming.

---

## Job Role Mapping

| Role | How this project is relevant |
|---|---|
| AI Engineer | ReAct tool-use is the standard pattern behind every serious AI agent product |
| Backend Engineer | Tool implementations (search, wiki, calculator) are the same as building microservice integrations |
| ML Engineer | Understanding how tool descriptions affect model behavior is a core LLM engineering skill |
| AI Product Engineer | You now know how to turn an LLM into a research assistant with real-world data access |
| Security Engineer | Safe evaluation (AST vs eval) and tool sandboxing are production requirements, not nice-to-haves |

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [01_MISSION.md](./01_MISSION.md) | Context and goals |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design and diagrams |
| [03_GUIDE.md](./03_GUIDE.md) | Progressive build steps |
| [src/starter.py](./src/starter.py) | Runnable starter code |
| 04_RECAP.md | you are here |

⬅️ **Prev:** [07 — Personal Knowledge Base RAG](../07_Personal_Knowledge_Base_RAG/01_MISSION.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [09 — Custom LoRA Fine-Tuning](../09_Custom_LoRA_Fine_Tuning/01_MISSION.md)
