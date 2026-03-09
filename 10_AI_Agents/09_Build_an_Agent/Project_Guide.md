# Build a Research Agent — Project Guide

This is the capstone project. You'll build a fully functional research agent from scratch.

---

## What You're Building

A **Research Agent** that takes a question, searches the web for relevant sources, reads and synthesizes the information, and returns a well-structured answer with citations.

**Example interaction:**

```
User: What are the key differences between transformer and Mamba architectures for language modeling?

Agent:
[Searches for recent papers and articles]
[Reads multiple sources]
[Synthesizes the information]
[Returns structured answer]

RESEARCH ANSWER:

# Transformer vs Mamba: Key Architectural Differences

## Core Mechanism
Transformers use self-attention (quadratic complexity with sequence length)...
Mamba uses selective state spaces (linear complexity)...

## When to Use Each
- Transformers: tasks where global context and parallel training matter
- Mamba: long sequences where memory efficiency is critical

## Sources
1. "Mamba: Linear-Time Sequence Modeling with Selective State Spaces" (Gu & Dao, 2023)
2. "Attention Is All You Need" (Vaswani et al., 2017)
3. [web article URL]
```

---

## What This Agent Demonstrates

By the end of this project, you'll have built an agent that uses:

- **Tool use** — web search + document reading
- **Planning** — breaking the research into steps
- **Memory** — maintaining research context across tool calls
- **ReAct pattern** — thinking before acting, using tool results
- **Output formatting** — structured answer with citations

---

## Tech Stack

| Component | Tool |
|---|---|
| Language | Python 3.10+ |
| Agent Framework | LangChain (or raw API calls — explained in both) |
| LLM | OpenAI GPT-4o (or Anthropic Claude via API) |
| Search | Tavily Search API (free tier available) |
| Web reading | BeautifulSoup (free, no API key needed) |
| Output formatting | Pydantic models |

---

## Prerequisites

Before starting, make sure you have:

- [ ] Python 3.10+ installed
- [ ] An OpenAI API key (or Anthropic API key)
- [ ] A Tavily API key (free at [tavily.com](https://tavily.com))
- [ ] Completed sections 01-08 of this module (or comfortable with agents, tools, memory)

---

## What You'll Learn

1. How to define multiple tools and connect them to an agent
2. How to structure the agent's output for clarity
3. How to manage context as the agent accumulates research
4. How to handle tool failures gracefully
5. How to add memory so the agent remembers research context
6. How to format the final answer with proper citations

---

## Project Structure

```
research_agent/
├── main.py              # Entry point — run the agent
├── agent.py             # Agent setup and configuration
├── tools/
│   ├── __init__.py
│   ├── search.py        # Web search tool
│   └── reader.py        # URL reading tool
├── memory.py            # Memory configuration
├── output.py            # Output formatting
└── requirements.txt
```

---

## Setup

```bash
# Create project directory
mkdir research_agent && cd research_agent

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Mac/Linux
# venv\Scripts\activate     # Windows

# Install dependencies
pip install langchain langchain-openai langchain-community \
            tavily-python requests beautifulsoup4 pydantic
```

Create a `.env` file:
```
OPENAI_API_KEY=your-openai-key-here
TAVILY_API_KEY=your-tavily-key-here
```

---

## Time to Complete

- **Step 1** (Setup): 10 minutes
- **Step 2** (Tools): 20 minutes
- **Step 3** (Agent): 15 minutes
- **Step 4** (Memory): 10 minutes
- **Step 5** (Output): 10 minutes
- **Testing and tweaking**: 15 minutes

**Total: About 80 minutes for a working research agent**

---

## Success Criteria

Your agent is working when it can:

1. Search for a topic and find relevant sources
2. Read at least one source URL for deeper content
3. Synthesize information from multiple sources
4. Return an answer with numbered citations
5. Handle a follow-up question using research it already did

---

## Extensions (After the Core Project)

Once the basic agent works:

- **Add a second search tool** for academic papers (Semantic Scholar API)
- **Add memory persistence** — save research across sessions
- **Add multi-agent** — research agent + writer agent working together
- **Add a critique step** — evaluate the answer quality before returning
- **Add a UI** — simple Streamlit frontend

The full code for each step is in `Step_by_Step.md`.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Architecture_Blueprint.md](./Architecture_Blueprint.md) | System architecture diagram |
| 📄 **Project_Guide.md** | ← you are here |
| [📄 Step_by_Step.md](./Step_by_Step.md) | Step-by-step build guide |
| [📄 Troubleshooting.md](./Troubleshooting.md) | Common issues and fixes |

⬅️ **Prev:** [08 Agent Frameworks](../08_Agent_Frameworks/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [01 MCP Fundamentals](../../11_MCP_Model_Context_Protocol/01_MCP_Fundamentals/Theory.md)
