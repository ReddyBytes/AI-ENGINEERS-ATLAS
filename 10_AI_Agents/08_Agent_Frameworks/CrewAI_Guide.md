# CrewAI — Quick Guide

Build role-based multi-agent systems with minimal code. CrewAI is the fastest way to get a crew of specialized agents working together.

---

## What Is CrewAI?

CrewAI is a framework built specifically for multi-agent collaboration.

You define:
- **Agents** with roles, goals, and tools
- **Tasks** with descriptions and expected outputs
- A **Crew** that runs them in a defined process

CrewAI handles the coordination, context passing, and execution.

---

## Core Concepts

### Agent

A specialist with a defined role:

```python
from crewai import Agent

agent = Agent(
    role="Senior Python Developer",          # Who they are
    goal="Write clean, tested Python code",  # What they're trying to achieve
    backstory="10 years Python experience, expert in Django and FastAPI",  # Shapes behavior
    tools=[search_tool, code_tool],          # What tools they can use
    verbose=True,                            # Show reasoning
    allow_delegation=False                   # Can't assign tasks to other agents
)
```

### Task

A specific piece of work:

```python
from crewai import Task

task = Task(
    description="Write a Python function that validates email addresses using regex",
    expected_output="A Python function with docstring, regex validation, and 3 test cases",
    agent=developer_agent,                   # Which agent does this
    context=[previous_task]                  # Optional: what to read from previous tasks
)
```

### Crew

The team and how they work:

```python
from crewai import Crew, Process

crew = Crew(
    agents=[agent1, agent2, agent3],
    tasks=[task1, task2, task3],
    process=Process.sequential,              # or Process.hierarchical
    verbose=True
)

result = crew.kickoff()
```

---

## Example: Research + Summarize Crew

```python
import os
from crewai import Agent, Task, Crew, Process
from crewai_tools import DuckDuckGoSearchRun

os.environ["OPENAI_API_KEY"] = "your-key-here"

search = DuckDuckGoSearchRun()

# Define agents
researcher = Agent(
    role="Research Specialist",
    goal="Find accurate, comprehensive information on any topic",
    backstory=(
        "Expert researcher with a talent for finding credible sources "
        "and synthesizing complex topics into clear findings."
    ),
    tools=[search],
    verbose=True
)

summarizer = Agent(
    role="Content Summarizer",
    goal="Transform research into clear, concise summaries",
    backstory=(
        "Specialist in distilling complex information into "
        "easy-to-understand summaries with key takeaways."
    ),
    verbose=True
)

# Define tasks
TOPIC = "The current state of quantum computing in 2024"

research_task = Task(
    description=f"Research: {TOPIC}. Find key facts, recent developments, and important statistics.",
    expected_output="A research brief with 5 key findings, each with supporting evidence.",
    agent=researcher
)

summary_task = Task(
    description=f"Create a clear 200-word summary of the research findings about {TOPIC}. Include: overview, top 3 developments, future outlook.",
    expected_output="A 200-word summary with three clear sections.",
    agent=summarizer,
    context=[research_task]  # Summarizer sees the research
)

# Create and run the crew
crew = Crew(
    agents=[researcher, summarizer],
    tasks=[research_task, summary_task],
    process=Process.sequential,
    verbose=True
)

result = crew.kickoff()
print(result)
```

---

## Sequential vs Hierarchical Process

### Sequential (most common)
Tasks run in order. Each task's output is available to subsequent tasks.

```python
process=Process.sequential
```

```
Task 1 → Task 2 → Task 3 → Final
```

### Hierarchical
A manager agent coordinates specialists. The manager decides which agent does what.

```python
from crewai import Agent

manager = Agent(
    role="Project Manager",
    goal="Coordinate the team to produce the best possible result",
    backstory="Experienced manager who delegates effectively and synthesizes results.",
)

crew = Crew(
    agents=[researcher, writer, editor],
    tasks=[task1, task2, task3],
    process=Process.hierarchical,
    manager_agent=manager  # or use manager_llm=llm
)
```

---

## When CrewAI Shines

**Perfect for:**
- Research + analysis + writing pipelines
- Content production workflows (research → write → edit → review)
- Any workflow that fits "a team of specialists"
- When you want readable, declarative agent configuration

**Less ideal for:**
- Simple single-agent tasks (overkill)
- Tasks requiring sophisticated memory across sessions
- Code generation + execution loops (use AutoGen)
- Tasks requiring complex conditional logic (use LangGraph)

---

## Practical Tips

**1. Role and backstory matter**

The `role` and `backstory` fields aren't just labels — they're injected into the system prompt and genuinely affect agent behavior. A "Harvard-trained researcher who values accuracy" behaves differently from a "quick research assistant."

**2. Expected output guides the agent**

Be specific in `expected_output`. "A list of 5 findings with sources" gets better results than "research findings."

**3. Context connects tasks**

```python
# Task 3 can see outputs of task1 AND task2
task3 = Task(
    ...,
    context=[task1, task2]
)
```

**4. Tools are optional**

Not every agent needs tools. The writer and editor agents typically don't need search tools — they work with what previous agents provide.

**5. Verbose helps debugging**

Keep `verbose=True` while building. You'll see each agent's reasoning and catch problems early.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Comparison.md](./Comparison.md) | Framework comparison |
| [📄 LangChain_Guide.md](./LangChain_Guide.md) | LangChain guide |
| [📄 AutoGen_Guide.md](./AutoGen_Guide.md) | AutoGen guide |
| 📄 **CrewAI_Guide.md** | ← you are here |

⬅️ **Prev:** [07 Multi-Agent Systems](../07_Multi_Agent_Systems/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [09 Build an Agent](../09_Build_an_Agent/Project_Guide.md)
