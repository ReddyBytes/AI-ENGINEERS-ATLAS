# Project 3 — Multi-Tool Research Agent

## Why This Project Matters

A product manager at a B2B SaaS company needed to write a competitive analysis every quarter. The process was always the same: Google the competitors, read their pricing pages, pull their Wikipedia descriptions, check recent news, do some rough market size math, then write it all up. Each report took a full day. Most of that day was mechanical information gathering — not thinking or writing.

He tried asking an LLM to do it directly. The LLM confidently produced a beautiful, detailed competitive analysis. It was also largely fabricated. The model's training data was 18 months old. The pricing figures were wrong. One competitor had been acquired. The "recent news" section cited headlines that never existed.

The problem was not the LLM's reasoning. It was that the LLM had no way to look things up. It was reasoning in the dark — drawing on memory instead of facts.

The solution is an **agent**: an LLM that can call tools, observe the results, and incorporate real information into its reasoning. When you give an LLM a web search tool, it stops guessing and starts researching. When you give it a calculator, it stops approximating and starts computing. This is the leap from chatbot to agent — and this project is where you make that leap.

---

## What You Will Build

A **ReAct agent** powered by Claude that has access to three tools:

1. **`web_search(query)`** — searches the web via DuckDuckGo and returns the top 5 results (title, URL, snippet)
2. **`wikipedia_summary(topic)`** — fetches a Wikipedia article summary for a topic
3. **`calculator(expression)`** — safely evaluates a mathematical expression and returns the result

The agent receives a research question, reasons step by step (Thought → Action → Observation), calls tools as needed, and produces a final synthesized answer. Conversation history is persisted so follow-up questions build on previous context.

---

## Learning Objectives

By completing this project you will be able to:

- Define a tool schema in the Anthropic tool_use format
- Implement the ReAct loop: parse tool call → execute tool → inject result → continue
- Handle multi-turn tool use (the agent may call tools multiple times)
- Persist conversation history across turns
- Write safe tool implementations that cannot be exploited

---

## Topics Covered

| Phase | Topic | Theory File |
|---|---|---|
| Phase 4 | Agent Fundamentals | `10_AI_Agents/01_Agent_Fundamentals/Theory.md` |
| Phase 4 | ReAct Pattern | `10_AI_Agents/02_ReAct_Pattern/Theory.md` |
| Phase 4 | Tool Use | `10_AI_Agents/03_Tool_Use/Theory.md` |
| Phase 4 | Agent Memory | `10_AI_Agents/04_Agent_Memory/Theory.md` |

---

## Prerequisites

- Completed Project 2 (Personal Knowledge Base RAG) or equivalent
- Understand the Anthropic Messages API
- Anthropic API key
- Comfortable reading API documentation

---

## Difficulty

Medium-Hard (4 / 5 stars)

The individual pieces are straightforward, but the ReAct loop requires careful attention to the Anthropic tool_use message format. The agent may make several tool calls before producing a final answer, and the conversation history must be assembled correctly or the API will return an error. Expect to spend time reading the Anthropic tool use documentation.

---

## Expected Output

```
Research Agent ready. Ask a research question (or 'quit' to exit).

You: How does the population of Tokyo compare to New York, and what is the ratio?

Agent thinking...
  [Tool call] wikipedia_summary("Tokyo")
  [Observation] Tokyo is the capital of Japan with a population of approximately
                13.96 million in the city proper and 37.4 million in the greater
                metropolitan area...

  [Tool call] wikipedia_summary("New York City")
  [Observation] New York City has a population of approximately 8.3 million in
                the five boroughs and 20.1 million in the metropolitan area...

  [Tool call] calculator("37.4 / 20.1")
  [Observation] 1.860696517...

Agent: Tokyo's greater metropolitan area (37.4 million) is approximately 1.86 times
larger than New York City's metropolitan area (20.1 million). For city-proper comparisons,
Tokyo (13.96 million) is about 1.68 times larger than New York (8.3 million).

You: What year was each city founded?

Agent thinking...
  [Tool call] web_search("Tokyo founding year history")
  [Observation] ...

Agent: Tokyo was founded in 1457 as Edo, a small castle town. New York was established
as New Amsterdam by Dutch settlers in 1626, becoming New York in 1664 under British rule.
```

---

## Key Concepts You Will Learn

**Tool Schema**: The JSON definition that tells Claude what a tool does, what parameters it takes, and what it returns. Claude uses this schema to decide when and how to call the tool.

**ReAct Loop**: The agent alternates between Reasoning (Claude's internal thought) and Acting (tool calls). Each tool result becomes an Observation that informs the next Reasoning step. This loop continues until Claude produces a final text answer.

**Tool Result Injection**: After executing a tool, you must inject the result back into the conversation as a `tool_result` message. The format is specific — get it wrong and the API returns an error.

**Safe Evaluation**: The `calculator` tool uses `ast.literal_eval` or a restricted expression evaluator rather than Python's `eval()`. Never use raw `eval()` on user input in production.

**Conversation Persistence**: All messages (user, assistant tool calls, tool results) are stored in a list. On the next user message, this full history is sent to Claude, giving it context about previous exchanges.

---

## Project Structure

```
03_Multi_Tool_Research_Agent/
├── Project_Guide.md
├── Step_by_Step.md
├── Starter_Code.md
├── Architecture_Blueprint.md
└── research_agent.py       ← your implementation
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| Project_Guide.md | ← you are here |
| [Step_by_Step.md](./Step_by_Step.md) | Build instructions |
| [Starter_Code.md](./Starter_Code.md) | Code with TODOs |
| [Architecture_Blueprint.md](./Architecture_Blueprint.md) | System diagram |

⬅️ **Prev:** [02 — Personal Knowledge Base RAG](../02_Personal_Knowledge_Base_RAG/Project_Guide.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 — Custom LoRA Fine-Tuning](../04_Custom_LoRA_Fine_Tuning/Project_Guide.md)
