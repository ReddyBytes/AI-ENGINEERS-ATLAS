# Multi-Agent Systems — Code Example

A CrewAI example: Research Agent + Writer Agent working together to produce an article.

---

## Setup

```bash
pip install crewai crewai-tools langchain-openai duckduckgo-search
```

```python
import os
os.environ["OPENAI_API_KEY"] = "your-key-here"
```

---

## Define the Tools

```python
from crewai_tools import DuckDuckGoSearchRun, FileWriterTool

# Search tool for the research agent
search_tool = DuckDuckGoSearchRun()

# File writer for the writer agent (optional — to save the article)
# file_writer = FileWriterTool()
```

---

## Define the Agents

```python
from crewai import Agent

# Agent 1: The Researcher
researcher = Agent(
    role="Senior Technology Researcher",
    goal=(
        "Find accurate, up-to-date information about the assigned topic. "
        "Gather key facts, statistics, trends, and expert perspectives."
    ),
    backstory=(
        "You are an experienced technology journalist with 10 years of experience "
        "researching AI and software topics. You excel at finding credible sources "
        "and synthesizing complex information into clear findings. You always "
        "cite your sources and distinguish between facts and speculation."
    ),
    tools=[search_tool],
    verbose=True,
    allow_delegation=False  # This agent doesn't delegate to others
)

# Agent 2: The Writer
writer = Agent(
    role="Technology Content Writer",
    goal=(
        "Transform research findings into engaging, well-structured articles "
        "that are accurate, readable, and informative."
    ),
    backstory=(
        "You are a skilled technology writer who specializes in making complex "
        "topics accessible to a general technical audience. You write with clarity, "
        "use concrete examples, and structure content logically. You never "
        "fabricate information — if a fact isn't in the research, you don't include it."
    ),
    verbose=True,
    allow_delegation=False
)

# Agent 3: The Editor (optional — adds quality review stage)
editor = Agent(
    role="Senior Editor",
    goal=(
        "Review the article for accuracy, clarity, structure, and completeness. "
        "Provide specific improvements while maintaining the author's voice."
    ),
    backstory=(
        "You are a meticulous editor with expertise in technology journalism. "
        "You check facts, improve clarity, fix logical gaps, and ensure articles "
        "meet professional publication standards."
    ),
    verbose=True,
    allow_delegation=False
)
```

---

## Define the Tasks

```python
from crewai import Task

TOPIC = "The practical applications of AI agents in software development in 2024"

# Task 1: Research
research_task = Task(
    description=f"""Research the following topic thoroughly:

Topic: {TOPIC}

Your research should cover:
1. Current state and adoption of AI agents in software development
2. Specific tools and frameworks being used (LangChain, GitHub Copilot, Cursor, etc.)
3. Concrete examples of what developers are using AI agents for (code generation, testing, debugging, documentation)
4. Key statistics or survey data on developer adoption
5. Expert opinions on the impact and limitations

Provide your findings as a structured research brief with:
- 5-7 key findings (each 2-3 sentences with source)
- A list of specific examples and tools
- Notable quotes or statistics
- Areas of uncertainty or conflicting information""",

    expected_output=(
        "A research brief with 5-7 clearly numbered key findings, "
        "each supported by evidence and sources. Include specific examples, "
        "statistics, and tool names where found."
    ),
    agent=researcher
)

# Task 2: Write the Article
writing_task = Task(
    description=f"""Write a 600-800 word article based on the research findings provided.

Topic: {TOPIC}

Article requirements:
- Engaging headline and opening paragraph that hooks the reader
- Clear structure: introduction, 3 main body sections, conclusion
- Use concrete examples from the research (specific tools, use cases)
- Include at least 2 statistics or data points from the research
- Accessible to developers who are not yet using AI agents
- Professional but conversational tone
- End with a practical takeaway

Format as markdown.""",

    expected_output=(
        "A complete 600-800 word markdown article with headline, "
        "clear section structure, concrete examples, and a practical conclusion."
    ),
    agent=writer,
    context=[research_task]  # Writer sees the researcher's output
)

# Task 3: Edit the Article
editing_task = Task(
    description="""Review and improve the article draft.

Check for:
1. Factual accuracy against the research findings (flag anything not supported by research)
2. Clarity — are complex concepts explained clearly?
3. Flow — does the article read smoothly from section to section?
4. Structure — is the 3-part body structure clear and logical?
5. Opening and conclusion strength

Provide the improved, final version of the article.
Make changes directly — produce the polished final article, not a list of suggestions.""",

    expected_output=(
        "The final, polished article in markdown format. "
        "All improvements integrated. Ready for publication."
    ),
    agent=editor,
    context=[writing_task]  # Editor sees the writer's draft
)
```

---

## Assemble and Run the Crew

```python
from crewai import Crew, Process

crew = Crew(
    agents=[researcher, writer, editor],
    tasks=[research_task, writing_task, editing_task],
    process=Process.sequential,  # Tasks run in order
    verbose=True  # See each agent's work
)

# Run the crew!
print("Starting the research + writing crew...")
print("="*60)

result = crew.kickoff()

print("\n" + "="*60)
print("FINAL ARTICLE")
print("="*60)
print(result)
```

---

## What You'll See in the Output

The verbose output shows you each agent's internal reasoning:

```
[2024-01-15 10:30:01][DEBUG]: Working Agent: Senior Technology Researcher
[2024-01-15 10:30:01][INFO]: Starting Task: Research the following topic...

> Entering new CrewAgentExecutor chain...
Thought: I need to research AI agents in software development. Let me search for current information.
Action: duckduckgo_search
Action Input: AI agents software development tools 2024
Observation: [search results about GitHub Copilot, Cursor, Devin, etc.]

Thought: Good results. Let me also search for adoption statistics.
Action: duckduckgo_search
Action Input: developer AI agent adoption statistics survey 2024
Observation: [results about Stack Overflow survey, GitHub stats, etc.]

Thought: I have enough information to write a comprehensive research brief.
Final Answer: [Structured research brief with findings]

[2024-01-15 10:31:45][DEBUG]: Working Agent: Technology Content Writer
[2024-01-15 10:31:45][INFO]: Starting Task: Write a 600-800 word article...
[... writer agent output ...]

[2024-01-15 10:33:10][DEBUG]: Working Agent: Senior Editor
[... editor agent reviewing and improving ...]
```

---

## Customizing the Crew

### Change the Topic

```python
TOPIC = "How AI is changing code review processes in 2024"
# Or any other topic — the crew structure stays the same
```

### Change the Output Length

```python
writing_task = Task(
    description=f"""Write a {TARGET_LENGTH}-word article...""",
    # ...
)
```

### Add a Fact-Checker Agent

```python
fact_checker = Agent(
    role="Fact Checker",
    goal="Verify every claim in the article against the research findings",
    backstory="You are rigorous fact-checker who cross-references every statement.",
    verbose=True
)

fact_check_task = Task(
    description="Cross-reference every factual claim in the article against the research brief. Flag any unsupported claims.",
    expected_output="The article with any unsupported claims marked [UNVERIFIED: ...] and a summary of fact-check results.",
    agent=fact_checker,
    context=[research_task, writing_task]  # Sees both research and draft
)
```

---

## Key Things to Notice

1. **Each agent has a persona** — the role and backstory shape how the agent writes and what it prioritizes

2. **Context flows forward** — the writer sees the researcher's output; the editor sees the writer's draft

3. **Each task has a clear expected output** — this guides the agent on what "done" looks like

4. **Verbose=True shows you everything** — use this for debugging, turn off for production

5. **The result is better than one agent doing all three jobs** — the specialization genuinely makes each phase better

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | Multi-agent architecture deep dive |

⬅️ **Prev:** [06 Reflection and Self-Correction](../06_Reflection_and_Self_Correction/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [08 Agent Frameworks](../08_Agent_Frameworks/Theory.md)
