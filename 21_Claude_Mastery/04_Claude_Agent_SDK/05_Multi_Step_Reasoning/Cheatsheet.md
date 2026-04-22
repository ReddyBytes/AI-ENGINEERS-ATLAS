# Multi-Step Reasoning — Cheatsheet

## Multi-Step vs Single Call

| | Single Call | Multi-Step Agent |
|---|---|---|
| Path known upfront? | Yes (one step) | No (discovered at runtime) |
| Tool calls | 0–1 | 2–N |
| Plan adapts? | No | Yes |
| Context grows | No | Yes (with each step) |
| Cost | Low | High (multiplied by steps) |
| Use when | Simple Q&A | Complex goal requiring exploration |

---

## System Prompt for Multi-Step

```python
system = """You are a [role] that solves complex tasks step by step.

When given a goal:
1. Analyze what information you need
2. Use tools to gather that information
3. Build your answer incrementally
4. Only return your final answer when you have all the pieces

Important:
- Always check your intermediate results before proceeding
- If a tool returns unexpected data, adjust your approach
- Think through each step before calling a tool"""
```

---

## Termination Conditions

| Condition | How to Set |
|---|---|
| Model produces final answer | Automatic — model stops calling tools |
| Max steps | `Agent(max_steps=20)` |
| Token limit | `Agent(max_tokens_per_step=4096)` |
| Time limit | Wrap `agent.run()` with a timeout |
| Error threshold | Use `on_step` callback to count errors |

Always set at least `max_steps`.

---

## Context Growth Pattern

```
Step 1: 750 tokens
Step 2: 750 + 1 tool call + result = ~1,500 tokens
Step 3: 1,500 + 1 tool call + result = ~2,500 tokens
Step N: grows approximately linearly

Rule: long agents need context compression strategy
```

Context compression options:
1. Truncate tool outputs at the source
2. Ask model to summarize after every 5 steps
3. Use external memory for large intermediate results

---

## Task Decomposition Patterns

```
Sequential:    A → B → C → D → result
               (each depends on previous)

Parallel:      A, B, C all at once → merge → result
               (independent subtasks)

Conditional:   A → if X: B  else: C → result
               (path depends on result)

Iterative:     A → B → check → A again (if not done)
               (refinement loop)
```

---

## Planning Prompt

Force the model to plan before acting:

```python
system = """When given a complex goal, first create a numbered plan 
of the steps needed, then execute each step using tools. 
Show your plan before starting."""
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Chained tool call examples |

⬅️ **Prev:** [Tool Calling in Agents](../04_Tool_Calling_in_Agents/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Agent Memory](../06_Agent_Memory/Theory.md)
