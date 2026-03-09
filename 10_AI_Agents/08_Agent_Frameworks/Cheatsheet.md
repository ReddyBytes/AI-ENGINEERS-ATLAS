# Agent Frameworks — Cheatsheet

**One-liner:** Agent frameworks abstract the agent loop, tool routing, memory, and prompt formatting so you build faster — LangChain for flexibility, CrewAI for role-based multi-agent, AutoGen for code execution.

---

## Key Terms

| Term | What it means |
|---|---|
| **Framework** | A library that handles the agent loop, tool routing, memory, and other plumbing |
| **LCEL** | LangChain Expression Language — pipe syntax for composing chains: `prompt \| llm \| parser` |
| **Chain** | A LangChain sequence of LLM calls or components |
| **AgentExecutor** | LangChain's class that runs the agent loop — perceive, think, act, observe, repeat |
| **Crew** | CrewAI's team of agents with defined roles and tasks |
| **Process** | CrewAI's execution order — sequential or hierarchical |
| **ConversableAgent** | AutoGen's base agent class — any agent that can send/receive messages |
| **UserProxyAgent** | AutoGen's special agent that can execute code and represent the human |
| **GroupChat** | AutoGen's managed multi-agent conversation |
| **Abstraction layer** | Code the framework provides so you don't have to write boilerplate |

---

## Framework Quick Start

### LangChain (ReAct Agent)
```python
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI

agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION)
agent.invoke({"input": "your question"})
```

### CrewAI (Multi-Agent Crew)
```python
from crewai import Agent, Task, Crew, Process

agent = Agent(role="...", goal="...", tools=[...])
task = Task(description="...", agent=agent)
crew = Crew(agents=[agent], tasks=[task], process=Process.sequential)
crew.kickoff()
```

### AutoGen (Conversational Agents)
```python
import autogen

assistant = autogen.AssistantAgent("assistant", llm_config=config)
user_proxy = autogen.UserProxyAgent("user_proxy", code_execution_config={"work_dir": "."})
user_proxy.initiate_chat(assistant, message="your task")
```

---

## Framework Comparison Summary

| | LangChain | CrewAI | AutoGen |
|---|---|---|---|
| **Best for** | Flexibility, prototyping | Role-based multi-agent | Code generation + execution |
| **Learning curve** | Medium | Low | Medium |
| **Multi-agent** | Yes (complex to set up) | Yes (built-in) | Yes (GroupChat) |
| **Code execution** | Via tool | Via tool | Native |
| **Production-ready** | Yes | Growing | Yes |
| **Ecosystem** | Very large | Growing | Medium |

---

## Golden Rules

1. **Start with the simplest framework for your use case.** Don't use AutoGen for a simple chatbot.

2. **Read the docs before diving in.** Each framework has its own mental model. 30 minutes of docs saves hours of confusion.

3. **Understand what the framework does for you.** Know where the agent loop lives in the code so you can debug it.

4. **Don't fight the framework's abstractions.** If you find yourself overriding everything, consider using a different framework or custom code.

5. **Use verbose/debug mode while building.** See exactly what the agent is doing and why.

6. **Frameworks change fast.** The agent framework space moves quickly. Pin your versions in production.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Comparison.md](./Comparison.md) | Framework comparison |
| [📄 LangChain_Guide.md](./LangChain_Guide.md) | LangChain guide |
| [📄 AutoGen_Guide.md](./AutoGen_Guide.md) | AutoGen guide |
| [📄 CrewAI_Guide.md](./CrewAI_Guide.md) | CrewAI guide |

⬅️ **Prev:** [07 Multi-Agent Systems](../07_Multi_Agent_Systems/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [09 Build an Agent](../09_Build_an_Agent/Project_Guide.md)
