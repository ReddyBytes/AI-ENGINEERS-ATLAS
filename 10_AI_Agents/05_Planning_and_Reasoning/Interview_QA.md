# Planning and Reasoning — Interview Q&A

## Beginner

**Q1: Why do AI agents need planning for complex tasks?**

<details>
<summary>💡 Show Answer</summary>

Simple agents work well for 1-3 step tasks. But complex tasks — "research this topic, compare 5 options, write an analysis" — require tracking many steps simultaneously.

Without planning, an agent might:
- Lose track of what it's already done
- Repeat the same searches
- Miss important steps
- Give up before the task is complete

Planning solves this by breaking the goal into explicit, manageable steps **before** execution begins. The agent follows the plan one step at a time, which is much more reliable.

It's like the difference between cooking a complex dish with a recipe vs. just improvising. The recipe prevents you from forgetting an ingredient or doing steps in the wrong order.

</details>

---

**Q2: What is Chain-of-Thought prompting and how does it help with reasoning?**

<details>
<summary>💡 Show Answer</summary>

Chain-of-Thought (CoT) prompting asks the LLM to write out its reasoning step by step before giving the final answer.

Instead of: `Question → Answer`

You get: `Question → Step 1 → Step 2 → Step 3 → Answer`

Example — math problem:
```
Bad (no CoT): "What is 15% of 240?" → "36" (might be wrong)
Good (CoT): "15% of 240. First: 10% of 240 = 24. Then: 5% = 12. Total: 24 + 12 = 36." → "36"
```

CoT dramatically improves accuracy on math, logic, and multi-step reasoning because it forces the model to work through the problem rather than guess.

For agents, CoT is often built into the prompt: "Think step by step before taking any action."

</details>

---

**Q3: What is the Plan-and-Execute pattern?**

<details>
<summary>💡 Show Answer</summary>

Plan-and-Execute separates the agent into two phases:

1. **Planning phase**: A "planner" LLM takes the high-level goal and generates a structured task list.
   ```
   Goal: "Research Python web frameworks and recommend the best one for beginners"
   Tasks:
   1. Search for popular Python web frameworks
   2. For each framework, find beginner-friendliness reviews
   3. Compare frameworks on: learning curve, documentation, community
   4. Write a recommendation with reasoning
   ```

2. **Execution phase**: An "executor" agent takes each task one at a time, uses tools to complete it, and stores the results.

The planner sees the big picture. The executor stays focused on one task. This separation makes complex workflows much more reliable.

</details>

---

## Intermediate

**Q4: What is Tree of Thoughts and when should you use it?**

<details>
<summary>💡 Show Answer</summary>

Tree of Thoughts (ToT) is like playing chess instead of just following the first move that comes to mind.

Instead of generating one plan and following it, ToT:
1. Generates multiple possible next steps at each point
2. Evaluates which option is most promising
3. Explores the best branches
4. Backtracks if a branch leads to a dead end

This allows the agent to explore the "solution space" rather than committing to the first plan it thinks of.

**Use ToT when:**
- The problem has multiple valid approaches with different tradeoffs
- You need creative solutions (writing, design, strategy)
- Getting stuck is costly and backtracking is worth the extra computation

**Skip ToT when:**
- Tasks are sequential and structured (research → compile → write)
- Speed matters — ToT is significantly slower and more expensive
- The first obvious approach is usually the right one

</details>

---

**Q5: How does BabyAGI-style task management work?**

<details>
<summary>💡 Show Answer</summary>

BabyAGI (and similar systems like AutoGPT) use a dynamic task management loop:

1. Start with a single objective
2. Generate an initial task list
3. Execute the highest-priority task
4. Based on the result, **generate new tasks** (the output informs what needs to happen next)
5. Re-prioritize the entire task list
6. Execute the next task
7. Repeat until the objective is met

The key difference from Plan-and-Execute: the task list is **dynamic**. New tasks emerge as the agent learns more. The agent doesn't follow a fixed plan — it adapts as it goes.

This is more powerful for open-ended exploration, but harder to control. The agent can generate many tasks and loop endlessly if not constrained.

</details>

---

**Q6: What is replanning and when should an agent do it?**

<details>
<summary>💡 Show Answer</summary>

Replanning is when the agent updates its task list based on new information discovered during execution.

When to replan:
- A task fails and the original plan assumed success
- Executing a task reveals that the plan had wrong assumptions
- New information makes some planned tasks unnecessary
- A better approach becomes obvious mid-execution

Example:
```
Original plan:
  Task 1: Search for Python ORM libraries → Django ORM, SQLAlchemy, Peewee
  Task 2: Compare Django ORM vs SQLAlchemy
  Task 3: Recommend one

After Task 1 execution, the agent discovers that Peewee is discontinued.
Replanning: Update Task 2 to only compare Django ORM vs SQLAlchemy (Peewee removed)
```

Without replanning, agents follow a stale plan based on incorrect assumptions.

</details>

---

## Advanced

**Q7: How would you implement a Plan-and-Execute agent from scratch?**

<details>
<summary>💡 Show Answer</summary>

Core components:

```python
class PlanAndExecuteAgent:
    def __init__(self, planner_llm, executor_llm, tools):
        self.planner = planner_llm
        self.executor = executor_llm
        self.tools = tools

    def plan(self, goal: str) -> list[str]:
        response = self.planner.invoke(
            f"""Create a numbered task list to accomplish:
            Goal: {goal}

            Rules:
            - Each task should be concrete and executable
            - Tasks should be in the right order
            - Output as a numbered list only"""
        )
        return self.parse_tasks(response)

    def execute_task(self, task: str, context: list) -> str:
        context_str = "\n".join(context) if context else "No previous results yet."
        return self.executor.invoke(
            task=task,
            previous_results=context_str,
            tools=self.tools
        )

    def run(self, goal: str) -> str:
        tasks = self.plan(goal)
        results = []

        for i, task in enumerate(tasks):
            result = self.execute_task(task, results)
            results.append(f"Task {i+1}: {task}\nResult: {result}")

            # Optional: replan based on result
            if self.needs_replanning(result, tasks[i+1:]):
                remaining_tasks = self.replan(goal, results, tasks[i+1:])
                tasks[i+1:] = remaining_tasks

        return self.synthesize(goal, results)
```

</details>

---

**Q8: How do you evaluate the quality of an agent's plan?**

<details>
<summary>💡 Show Answer</summary>

A good plan has these properties:

1. **Completeness** — does it cover all steps needed to achieve the goal?
2. **Correctness** — are the steps in a logical order? Do later steps depend on earlier ones?
3. **Granularity** — are steps small enough to execute reliably? Not too broad, not too trivial.
4. **Independence** — can each step be executed without ambiguity?
5. **Coverage of edge cases** — does the plan account for likely failures?

Automated evaluation approaches:
- Have a separate "critic" LLM review the plan before execution
- Check if each task has a clear completion criterion
- Simulate execution on known test cases and measure success rate
- Human evaluation of a sample of generated plans

</details>

---

**Q9: Compare Plan-and-Execute with standard ReAct agents for a complex research task.**

<details>
<summary>💡 Show Answer</summary>

**Standard ReAct** on a complex task:
- Decides each action one step at a time
- May lose track of the overall goal after many steps
- Prone to getting stuck in local loops ("I need more information, let me search again...")
- Good for adaptive, exploratory tasks where the path isn't known

**Plan-and-Execute** on the same task:
- Starts with a full task list — maintains awareness of the complete picture
- Executor focuses on one small task — less likely to lose track
- Planner and executor have clear, separate roles
- Better for tasks where the structure is known upfront

**In practice**, production agents often combine both:
- Use a planner to create the task list
- Use a ReAct-style agent to execute each individual task (ReAct within each task step)
- Allow replanning when tasks fail

This gives you the structure of Plan-and-Execute with the adaptability of ReAct at the task level.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | Planning architectures deep dive |

⬅️ **Prev:** [04 Agent Memory](../04_Agent_Memory/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [06 Reflection and Self-Correction](../06_Reflection_and_Self_Correction/Theory.md)
