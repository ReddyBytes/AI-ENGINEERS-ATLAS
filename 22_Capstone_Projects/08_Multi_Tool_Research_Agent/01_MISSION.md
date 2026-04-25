# Project 08 — Multi-Tool Research Agent

## The Story

A product manager at a B2B SaaS company needed to write a competitive analysis every quarter. The process was always the same: Google the competitors, read their pricing pages, pull their Wikipedia descriptions, check recent news, do some rough market size math, then write it all up. Each report took a full day. Most of that day was mechanical information gathering — not thinking or writing.

He tried asking an LLM to do it directly. The LLM confidently produced a beautiful, detailed competitive analysis. It was also largely fabricated. The model's training data was 18 months old. The pricing figures were wrong. One competitor had been acquired. The "recent news" section cited headlines that never existed.

The problem was not the LLM's reasoning. It was that the LLM had no way to look things up. It was reasoning in the dark — drawing on memory instead of facts.

The solution is an agent: an LLM that can call tools, observe the results, and incorporate real information into its reasoning. When you give an LLM a web search tool, it stops guessing and starts researching. When you give it a calculator, it stops approximating and starts computing. This is the leap from chatbot to agent — and this project is where you make that leap.

---

## What You Will Build

A **ReAct agent** powered by Claude that has access to three tools:

1. `web_search(query)` — searches the web via DuckDuckGo and returns the top 5 results (title, URL, snippet)
2. `wikipedia_summary(topic)` — fetches a Wikipedia article summary for a topic
3. `calculator(expression)` — safely evaluates a mathematical expression and returns the result

The agent receives a research question, reasons step by step (Thought → Action → Observation), calls tools as needed, and produces a final synthesized answer. Conversation history is persisted so follow-up questions build on previous context.

### Expected Output

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
larger than New York City's metropolitan area (20.1 million).
```

---

## Real-World Motivation

ReAct agents with tools are the standard pattern for AI systems that need to access real, current information. They appear in:
- Research assistants that search the web and synthesize findings
- Customer support agents that query live product databases
- Data analysis agents that call computation or SQL tools
- Coding assistants that run tests or read documentation

---

## Concepts Covered

| Concept | What You Learn |
|---|---|
| Tool schema | JSON definition that tells Claude what a tool does and when to use it |
| ReAct loop | Alternating between reasoning and action until a final answer is reached |
| Tool result injection | How to correctly format tool outputs back into the conversation |
| Multi-turn tool use | Agents that call multiple tools across multiple reasoning steps |
| Conversation memory | Persisting full message history so follow-up questions have context |
| Safe evaluation | Using the AST module to evaluate math without `eval()` |
| Error recovery | Wrapping tool calls so failures return an error string, not a crash |

---

## Theory Files

| Section | Topic | File |
|---|---|---|
| 10_AI_Agents | Agent Fundamentals | `10_AI_Agents/01_Agent_Fundamentals/Theory.md` |
| 10_AI_Agents | ReAct Pattern | `10_AI_Agents/02_ReAct_Pattern/Theory.md` |
| 10_AI_Agents | Tool Use | `10_AI_Agents/03_Tool_Use/Theory.md` |
| 10_AI_Agents | Agent Memory | `10_AI_Agents/04_Agent_Memory/Theory.md` |

---

## Prerequisites

- Completed Project 07 (Personal Knowledge Base RAG) or equivalent
- Understand the Anthropic Messages API request/response structure
- Anthropic API key
- Python 3.10+

---

## Learning Format

**Tier:** Intermediate-Hard (4 / 5 stars)

The individual pieces are straightforward, but the ReAct loop requires careful attention to the Anthropic tool_use message format. The agent may make several tool calls before producing a final answer, and the conversation history must be assembled correctly or the API will return an error. Expect to spend time reading the Anthropic tool use documentation. Plan approximately 4 hours.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| 01_MISSION.md | you are here |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design and diagrams |
| [03_GUIDE.md](./03_GUIDE.md) | Progressive build steps |
| [src/starter.py](./src/starter.py) | Runnable starter code |
| [04_RECAP.md](./04_RECAP.md) | What you built + next steps |

⬅️ **Prev:** [07 — Personal Knowledge Base RAG](../07_Personal_Knowledge_Base_RAG/01_MISSION.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [09 — Custom LoRA Fine-Tuning](../09_Custom_LoRA_Fine_Tuning/01_MISSION.md)
