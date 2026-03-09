# AutoGen — Quick Guide

Microsoft's framework for conversational agents that can write and execute code. Built for iterative workflows where agents talk to each other.

---

## What Is AutoGen?

AutoGen is a framework from Microsoft Research that focuses on **conversational multi-agent systems**.

Key idea: agents are "conversable" — they communicate by sending messages to each other. A `UserProxyAgent` can execute the code that the `AssistantAgent` writes. They go back and forth until the task is done.

---

## Core Concepts

### ConversableAgent

The base class. Any agent that can send and receive messages.

```python
import autogen

# Any agent can be created from this
agent = autogen.ConversableAgent(
    name="agent_name",
    system_message="Your role and instructions here",
    llm_config={"config_list": [{"model": "gpt-4o", "api_key": "your-key"}]},
    human_input_mode="NEVER",  # NEVER, TERMINATE, or ALWAYS
)
```

### AssistantAgent

The LLM-powered agent. Writes plans, code, and responses.

```python
assistant = autogen.AssistantAgent(
    name="assistant",
    system_message="You are a helpful AI assistant.",
    llm_config={"config_list": config_list}
)
```

### UserProxyAgent

Represents the user. Can execute code. Drives the conversation.

```python
user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",      # Fully automated
    code_execution_config={
        "work_dir": "coding",       # Directory to run code in
        "use_docker": False         # Set True for sandboxed Docker execution
    },
    max_consecutive_auto_reply=10  # Stop after 10 auto-replies
)
```

### GroupChat

Manages a conversation between multiple agents.

```python
groupchat = autogen.GroupChat(
    agents=[agent1, agent2, agent3],
    messages=[],
    max_round=10                   # Max conversation rounds
)

manager = autogen.GroupChatManager(
    groupchat=groupchat,
    llm_config={"config_list": config_list}
)
```

---

## Basic Example: Code Generation + Execution

The classic AutoGen use case: an assistant writes code, the user proxy runs it, the loop continues until it works.

```python
import autogen
import os

config_list = [{
    "model": "gpt-4o",
    "api_key": os.environ["OPENAI_API_KEY"]
}]

# The AI assistant that writes code
assistant = autogen.AssistantAgent(
    name="coding_assistant",
    system_message=(
        "You are an expert Python programmer. When asked to solve a problem, "
        "write clean Python code. The user_proxy will execute the code and "
        "report back. If there's an error, fix it. Keep trying until it works."
    ),
    llm_config={"config_list": config_list}
)

# The agent that executes code
user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    code_execution_config={
        "work_dir": "coding_workspace",
        "use_docker": False
    },
    max_consecutive_auto_reply=5,
    is_termination_msg=lambda msg: "TASK_COMPLETE" in msg.get("content", "")
)

# Start the conversation
user_proxy.initiate_chat(
    assistant,
    message=(
        "Write a Python script that:\n"
        "1. Generates a list of the first 20 Fibonacci numbers\n"
        "2. Saves them to a CSV file called 'fibonacci.csv'\n"
        "3. Reads the CSV back and prints the sum\n"
        "Say TASK_COMPLETE when it works correctly."
    )
)
```

**What happens:**
1. AssistantAgent writes the Python code
2. UserProxyAgent executes it in `coding_workspace/`
3. If there's an error, the error goes back to AssistantAgent
4. AssistantAgent fixes the code
5. Loop continues until `TASK_COMPLETE` appears or max replies

---

## Multi-Agent GroupChat Example

Three agents working together: a researcher, a developer, and a critic.

```python
config_list = [{"model": "gpt-4o", "api_key": os.environ["OPENAI_API_KEY"]}]
llm_config = {"config_list": config_list}

# Define the specialist agents
researcher = autogen.AssistantAgent(
    name="researcher",
    system_message=(
        "You are a researcher. When asked about a topic, provide factual "
        "information and context. Be concise and cite your reasoning."
    ),
    llm_config=llm_config
)

developer = autogen.AssistantAgent(
    name="developer",
    system_message=(
        "You are a Python developer. When asked to implement something, "
        "write clean, working Python code. Include comments."
    ),
    llm_config=llm_config
)

critic = autogen.AssistantAgent(
    name="critic",
    system_message=(
        "You are a code reviewer and quality critic. Review code for: "
        "bugs, edge cases, readability, and best practices. Be specific."
    ),
    llm_config=llm_config
)

# The human/executor proxy
user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    code_execution_config={"work_dir": "group_workspace", "use_docker": False},
    max_consecutive_auto_reply=15,
)

# Create the group chat
groupchat = autogen.GroupChat(
    agents=[user_proxy, researcher, developer, critic],
    messages=[],
    max_round=12,
    speaker_selection_method="auto"  # LLM decides who speaks next
)

manager = autogen.GroupChatManager(
    groupchat=groupchat,
    llm_config=llm_config
)

# Start the conversation
user_proxy.initiate_chat(
    manager,
    message=(
        "Build a simple Python rate limiter class. "
        "First researcher: explain what a rate limiter is and common algorithms. "
        "Then developer: implement a token bucket rate limiter. "
        "Then critic: review the implementation. "
        "Then developer: fix any issues. "
        "End when the implementation is solid."
    )
)
```

---

## Termination Conditions

Always define when the conversation should stop:

```python
# Option 1: Custom termination function
def is_done(message):
    content = message.get("content", "").lower()
    return any(phrase in content for phrase in [
        "task complete",
        "terminating",
        "all done",
        "no more changes needed"
    ])

user_proxy = autogen.UserProxyAgent(
    ...,
    is_termination_msg=is_done,
    max_consecutive_auto_reply=10  # Hard backup limit
)

# Option 2: Max rounds in GroupChat
groupchat = autogen.GroupChat(
    ...,
    max_round=15
)
```

---

## When AutoGen Shines

**Perfect for:**
- Code generation that needs execution feedback
- Iterative debugging where the error message drives the next attempt
- Multi-agent conversations where agents critique each other
- Workflows that benefit from the "conversational" mental model
- Azure OpenAI integration (Microsoft ecosystem)

**Less ideal for:**
- Structured content pipelines (use CrewAI)
- Simple chatbots with memory (use LangChain)
- Tasks that don't involve code (the conversational loop overhead isn't worth it)

---

## Key Differences from CrewAI

| | CrewAI | AutoGen |
|---|---|---|
| Mental model | Crew of workers | Conversation between agents |
| Code execution | Via custom tool | Native (UserProxyAgent) |
| Task structure | Explicit tasks with expected outputs | Emergent from conversation |
| Best fit | Role-based content workflows | Code gen + iterative debugging |
| Control | Highly structured | More conversational/open |

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
| 📄 **AutoGen_Guide.md** | ← you are here |
| [📄 CrewAI_Guide.md](./CrewAI_Guide.md) | CrewAI guide |

⬅️ **Prev:** [07 Multi-Agent Systems](../07_Multi_Agent_Systems/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [09 Build an Agent](../09_Build_an_Agent/Project_Guide.md)
