# LangChain for Agents — Quick Guide

Build your first LangChain agent in 20 lines. Understand the key concepts. Know when to use it.

---

## What Is LangChain?

LangChain is a framework for building LLM-powered applications. It provides:

- **Chains** — composable sequences of LLM calls
- **Agents** — LLMs with tools and a reasoning loop
- **Memory** — conversation history management
- **Tools** — pluggable functions for agents
- **Integrations** — 100+ pre-built connections (databases, APIs, vector stores)

The core value: it handles the boilerplate so you write less code.

---

## Key Concepts

### 1. LCEL — LangChain Expression Language

The modern way to build in LangChain. Uses pipe syntax `|` to chain components:

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Simple chain: prompt | model | parser
chain = (
    ChatPromptTemplate.from_template("Explain {topic} in one sentence.")
    | ChatOpenAI(model="gpt-4o-mini")
    | StrOutputParser()
)

result = chain.invoke({"topic": "neural networks"})
```

### 2. Tools

Functions wrapped with a name and description:

```python
from langchain.tools import Tool

def my_function(query: str) -> str:
    return "result"

tool = Tool(name="tool_name", func=my_function, description="what it does")
```

### 3. AgentExecutor

Runs the agent loop (think → act → observe → repeat):

```python
from langchain.agents import AgentExecutor, create_react_agent
```

### 4. Memory

Keeps conversation history:

```python
from langchain.memory import ConversationBufferMemory
memory = ConversationBufferMemory()
```

---

## Build a ReAct Agent in 20 Lines

```python
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
import math

# 1. Define tools
def calculator(expr: str) -> str:
    try:
        return str(eval(expr, {"__builtins__": {}}, {"math": math}))
    except Exception as e:
        return f"Error: {e}"

tools = [
    Tool(name="calculator",
         func=calculator,
         description="Evaluate math expressions. Input: Python math expression.")
]

# 2. Create LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# 3. Create agent
agent = initialize_agent(
    tools=tools, llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True, max_iterations=5
)

# 4. Run it
result = agent.invoke({"input": "What is 15% of 240?"})
print(result["output"])
```

That's it. 20 lines. A working ReAct agent with a tool.

---

## The Modern Way (LCEL + create_react_agent)

```python
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain_openai import ChatOpenAI
from langchain.tools import DuckDuckGoSearchRun

# Pull the standard ReAct prompt from LangChain hub
prompt = hub.pull("hwchase17/react")

llm = ChatOpenAI(model="gpt-4o", temperature=0)
tools = [DuckDuckGoSearchRun()]

# Create agent using LCEL
agent = create_react_agent(llm, tools, prompt)

# Wrap in executor (handles the loop)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=5,
    handle_parsing_errors=True
)

result = agent_executor.invoke({"input": "What is the latest Python version?"})
print(result["output"])
```

---

## Adding Memory

```python
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent, AgentType

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

agent_with_memory = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    memory=memory,
    verbose=True
)

# First message
agent_with_memory.invoke({"input": "My name is Alex and I'm building a Django app."})

# Second message — agent remembers "Alex" and "Django"
agent_with_memory.invoke({"input": "What framework should I use for the database layer?"})
```

---

## Important LangChain Agent Types

| Agent Type | When to use |
|---|---|
| `ZERO_SHOT_REACT_DESCRIPTION` | Single agent, ReAct pattern, most common |
| `CHAT_CONVERSATIONAL_REACT_DESCRIPTION` | Same but with conversational memory |
| `STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION` | Tools with complex parameters |
| `OPENAI_FUNCTIONS` | Use OpenAI function calling (more reliable) |
| `OPENAI_MULTI_FUNCTIONS` | Multiple tool calls per step |

---

## When to Use LangChain

**LangChain is great for:**
- Learning agent concepts (verbose output shows everything)
- Prototyping quickly with pre-built integrations
- Building RAG + agent hybrid systems
- When you need fine-grained control over the agent loop
- Production systems that use many different LLM providers

**LangChain gets difficult when:**
- You need a role-based multi-agent system (use CrewAI instead)
- You need code execution as a first-class feature (use AutoGen)
- You hit LCEL syntax confusion (it's powerful but takes time to learn)

---

## Debugging Tips

```python
# See the full prompt the agent receives
agent.agent.llm_chain.prompt.messages[0].prompt.template

# See tool schemas
for tool in tools:
    print(f"{tool.name}: {tool.description}")

# Enable callback for detailed logging
from langchain.callbacks import StdOutCallbackHandler
handler = StdOutCallbackHandler()
agent.invoke({"input": "question"}, config={"callbacks": [handler]})
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Comparison.md](./Comparison.md) | Framework comparison |
| 📄 **LangChain_Guide.md** | ← you are here |
| [📄 AutoGen_Guide.md](./AutoGen_Guide.md) | AutoGen guide |
| [📄 CrewAI_Guide.md](./CrewAI_Guide.md) | CrewAI guide |

⬅️ **Prev:** [07 Multi-Agent Systems](../07_Multi_Agent_Systems/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [09 Build an Agent](../09_Build_an_Agent/Project_Guide.md)
