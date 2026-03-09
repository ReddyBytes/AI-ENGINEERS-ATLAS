# Agent Troubleshooting Guide

Symptoms, causes, and fixes for the most common agent problems.

---

## Symptom 1: Agent Loops Forever

**What you see:**
The agent keeps running, making the same tool calls repeatedly without reaching a Final Answer. Your terminal scrolls indefinitely until you kill the process.

**Cause:**
One of several things:
- The agent doesn't know what "done" looks like
- The agent keeps getting incomplete tool results and keeps retrying
- The Final Answer format isn't being recognized by the framework
- The agent thinks it needs more information but can't get it

**Fixes:**

1. **Set `max_iterations`** — this is your most important safety net:
```python
agent = initialize_agent(
    ...,
    max_iterations=6,    # Hard stop after 6 tool calls
    early_stopping_method="generate"  # Return best answer if limit hit
)
```

2. **Clarify the stopping condition in the system prompt:**
```python
system_message = """...
When you have enough information to answer the question fully,
write your FINAL ANSWER. Don't keep searching for more information
once you can answer the question.
"""
```

3. **Check for identical repeated actions** — if the agent is calling `search_web("same query")` three times in a row, something is wrong with how observations are being processed. Check your tool implementation and that observations are being added to context.

4. **Reduce the number of tools** — too many choices can cause the agent to loop between them without deciding.

---

## Symptom 2: Agent Ignores Tools

**What you see:**
The agent writes an answer directly from its training data without using any tools. It doesn't search, doesn't read URLs, just generates a response and calls it done.

**Cause:**
- Tool descriptions aren't compelling enough
- The agent's system prompt doesn't emphasize tool use
- The question type doesn't trigger tool use behavior
- Wrong agent type (not a ReAct agent)

**Fixes:**

1. **Strengthen the system prompt to mandate tool use:**
```python
system_message = """You are a research agent.
RULE: You MUST always search before answering any factual question.
Never answer from memory alone. Always verify with search_web first."""
```

2. **Improve tool descriptions with "when to use" language:**
```python
Tool(
    description=(
        "Search for ANY factual information. "
        "Use this for EVERY question about facts, events, people, or current information. "
        "Do NOT answer without searching first."
    )
)
```

3. **Check you're using the right agent type.** A `ZERO_SHOT_REACT_DESCRIPTION` agent should use tools. A basic `LLMChain` won't.

4. **Test your tools work first.** If the tool is broken and returns an error, the agent may give up and answer from training data. Test tools independently before connecting to the agent.

---

## Symptom 3: Wrong Tool Is Chosen

**What you see:**
The agent calls a search tool when it should calculate, or reads a URL when it should search. Tool selection is consistently wrong.

**Cause:**
Tool descriptions are overlapping, vague, or missing "when to use" guidance.

**Fixes:**

1. **Add clear "use this when" and "don't use this when" to descriptions:**
```python
calculator_tool = Tool(
    description=(
        "Evaluate mathematical expressions precisely. "
        "Use this for ALL math calculations — addition, multiplication, percentages, powers. "
        "Do NOT use this for looking up information — use search_web for that. "
        "Input: a Python math expression like '15 * 0.20' or '2 ** 16'."
    )
)

search_tool = Tool(
    description=(
        "Search the internet for information, facts, definitions, current events. "
        "Use this when you need information about the world. "
        "Do NOT use this for math calculations — use calculator for that."
    )
)
```

2. **Reduce tool count.** 2-3 clearly distinct tools are better than 5 overlapping ones.

3. **Use structured tool calling** if available (`OPENAI_FUNCTIONS` agent type) — it's more reliable than text parsing.

---

## Symptom 4: Hallucinated Tool Calls

**What you see:**
The agent tries to call a tool that doesn't exist ("I'll use the `translate_text` tool" — but you never defined that), or calls a real tool with completely wrong parameters.

**Cause:**
- The LLM is generating tool names that sound plausible but aren't in your toolset
- The LLM is confusing tool names from training data (other frameworks)
- Weak output parsing allowing malformed tool calls

**Fixes:**

1. **List your exact tool names explicitly in the system prompt:**
```python
system_message = f"""You have exactly these tools available:
- search_web: for searching the internet
- read_url: for reading a webpage
- calculator: for math

You ONLY have these 3 tools. Do not try to use any other tool names."""
```

2. **Enable `handle_parsing_errors=True`:**
```python
agent = initialize_agent(
    ...,
    handle_parsing_errors=True  # Gracefully handle malformed tool calls
)
```

3. **Switch to OpenAI function calling agent type** — it uses structured JSON tool calls instead of text parsing, which eliminates this class of errors:
```python
agent=AgentType.OPENAI_FUNCTIONS
```

4. **Log all tool calls.** Add a callback to catch what the agent is requesting before it's parsed.

---

## Symptom 5: Out of Context (Answer Ignores Earlier Parts of Conversation)

**What you see:**
In a multi-turn conversation, the agent seems to forget what was discussed earlier. Ask "What was the first thing I asked?" and it doesn't know. Or it contradicts information it found earlier.

**Cause:**
- Context window exceeded — earlier messages were dropped
- Memory configuration is wrong — memory isn't being loaded
- Wrong memory type for the use case

**Fixes:**

1. **Check your memory configuration** — is it actually being saved and loaded?
```python
# After a few turns, check what's in memory:
print(memory.load_memory_variables({}))
# Should show conversation history
```

2. **Switch from BufferMemory to SummaryBufferMemory** for long conversations:
```python
from langchain.memory import ConversationSummaryBufferMemory

memory = ConversationSummaryBufferMemory(
    llm=llm,
    max_token_limit=2000,   # Keep recent messages verbatim
    return_messages=True
)
```

3. **Use a sliding window:**
```python
from langchain.memory import ConversationBufferWindowMemory

memory = ConversationBufferWindowMemory(
    k=10,  # Keep only the last 10 turns
    return_messages=True
)
```

4. **Check token usage.** If using `gpt-3.5-turbo` (4K context), a long research conversation will overflow. Switch to `gpt-4o` (128K context) for research tasks.

---

## Symptom 6: Agent Gives Confident but Wrong Answers

**What you see:**
The agent produces a well-formatted, confident-sounding answer that is factually wrong. It may have searched but used the search results incorrectly, or it ignored the search results and answered from training data.

**Cause:**
- Agent is generating plausible-sounding answers rather than grounding in search results
- The agent skipped the search step (see Symptom 2)
- Search results were vague and the agent filled gaps with hallucination

**Fixes:**

1. **Require explicit citation in the system prompt:**
```python
system_message = """CRITICAL RULE: Every factual claim in your final answer
MUST be supported by a specific search result or URL you read.
If you don't have a source for a fact, don't include it.
End every answer with a numbered Sources list."""
```

2. **Add a reflection step** — after generating the answer, have the agent check each claim:
```python
# After the main answer, run a critique:
critique_prompt = """Review your answer above.
For each factual claim: is it directly supported by the search results you gathered?
If any claim is NOT supported, remove it or mark it as [unverified]."""
```

3. **Use a more capable model.** `gpt-4o` is significantly better at grounding answers in retrieved content than smaller models.

4. **Make search results more prominent in context.** If the search results are buried deep in a long context, the model may not attend to them properly.

---

## Quick Reference: Symptom → Fix

| Symptom | First thing to try |
|---|---|
| Loops forever | Set `max_iterations=6` |
| Ignores tools | Add "ALWAYS search before answering" to system prompt |
| Wrong tool chosen | Rewrite tool descriptions with explicit "use when" / "don't use when" |
| Hallucinated tool calls | Use `AgentType.OPENAI_FUNCTIONS` + explicit tool list in prompt |
| Forgets earlier conversation | Check memory is connected; switch to SummaryBufferMemory |
| Confident but wrong | Require explicit citations; add self-critique step |

---

## Debug Mode

When in doubt, turn everything on:

```python
import langchain
langchain.debug = True  # Maximum verbosity

agent = initialize_agent(
    ...,
    verbose=True,
    handle_parsing_errors=True
)
```

This shows you every step: the full prompt sent to the LLM, the raw LLM response, how it was parsed, what tool was called, and what was returned. It's verbose, but when something breaks, it shows you exactly where.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Architecture_Blueprint.md](./Architecture_Blueprint.md) | System architecture diagram |
| [📄 Project_Guide.md](./Project_Guide.md) | Project overview |
| [📄 Step_by_Step.md](./Step_by_Step.md) | Step-by-step build guide |
| 📄 **Troubleshooting.md** | ← you are here |

⬅️ **Prev:** [08 Agent Frameworks](../08_Agent_Frameworks/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [01 MCP Fundamentals](../../11_MCP_Model_Context_Protocol/01_MCP_Fundamentals/Theory.md)
