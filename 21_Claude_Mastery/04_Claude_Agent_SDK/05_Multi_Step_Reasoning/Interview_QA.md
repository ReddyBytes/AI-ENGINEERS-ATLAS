# Multi-Step Reasoning — Interview Q&A

## Beginner Level

**Q1: What distinguishes multi-step reasoning from a single tool call?**

A: A single tool call is one action: the model calls a function, gets a result, and produces a final answer. Multi-step reasoning is a sequence of tool calls where each result informs the next action. The key property is that the path is not predetermined — the model decides at each step what to do next based on what it has observed so far. If step 3 returns an unexpected result, the model adapts its plan for steps 4-10 rather than following a script. This adaptive quality is what makes multi-step reasoning powerful for complex tasks and what separates agents from fixed chains.

---

**Q2: What is a "stop condition" in multi-step reasoning, and why must you always set one?**

A: A stop condition is the rule that ends the agent loop. The primary natural condition is when Claude produces a final text response with no tool call — the model has concluded the task. But this alone is insufficient: if the goal is ambiguous or the model gets into a pattern of tool calls without converging on a final answer, the loop runs indefinitely. Always set `max_steps` to a finite number (e.g., 20) as a hard backstop. Additional conditions include: total token budget exhaustion, wall-clock timeout, or a consecutive error threshold. Without explicit stop conditions, a multi-step agent is an unbounded loop and a potential runaway cost.

---

**Q3: How does context grow in a multi-step agent and why does this matter?**

A: Every tool call and its result are appended to the message history. Each API call passes this complete history. So: step 1 costs ~750 tokens, step 5 costs ~3,000 tokens (the 750 plus 4 tool call/result pairs), step 15 costs ~10,000+ tokens. Token costs multiply with each step. There's also a hard limit: the context window. For Claude Sonnet 4.6 (200K tokens), a long agent processing large tool outputs can exhaust the window before completing the task. This matters for both cost and reliability — design tool outputs to be concise, truncate large results, and use external memory for information that's needed later but doesn't need to stay in the active context.

---

## Intermediate Level

**Q4: How does a multi-step agent decompose a complex task? Is the decomposition explicit or implicit?**

A: In most agent implementations including the Claude Agent SDK, decomposition is implicit — the model breaks down the task internally as part of its reasoning, not in an explicit planning step. Claude receives the goal and starts taking the most immediately useful action. However, explicit planning can be encouraged through the system prompt: "Before using any tools, write out your plan as a numbered list, then execute each step." This trades a small amount of upfront context for more coherent multi-step execution — the model commits to a plan and follows it, rather than improvising step by step. For complex, multi-stage tasks (research, code analysis), explicit planning often improves reliability and makes the agent's reasoning more transparent.

---

**Q5: What is the difference between sequential and parallel tool call chaining, and when would you use each?**

A: Sequential chaining: tool B uses the result of tool A. The model calls A, gets the result, then calls B with that result. Required when there's a data dependency — you can't call B without A's output. Example: get the customer ID, then use that ID to get the order history.

Parallel chaining: tools A, B, and C all take the same input and can run simultaneously. Parallelism in a single agent is not native — the model calls one tool at a time. To run parallel tasks, you use multi-agent patterns (see Topic 07): spawn subagents, each running one of A/B/C simultaneously. Use sequential for dependent steps; use parallel agents for independent sub-tasks that would otherwise serialize unnecessarily.

---

**Q6: How would you debug an agent that keeps calling the same tool repeatedly without making progress?**

A: This "looping" behavior typically has three causes:

1. **Ambiguous goal**: the model doesn't know what "done" looks like. Fix: add explicit success criteria to the system prompt — "Return your final answer as soon as you have all the required information."

2. **Tool output not meaningful**: the tool returns data but the model can't figure out how to use it to advance the goal. Fix: check the tool's return format and docstring — is the output clearly described and usable?

3. **Missing tool**: the model calls the closest available tool but needs a different one that doesn't exist. Fix: check what tool would break the loop; either add it or refine the goal so it's solvable with existing tools.

Debug approach: add an `on_step` callback to log every tool call and argument. If the same tool is called with the same arguments repeatedly, the model isn't using the results. If called with slightly different arguments each time, it's searching but not finding the right data.

---

## Advanced Level

**Q7: How does Tree-of-Thought (ToT) differ from the default greedy multi-step reasoning in agents, and when would you implement it?**

A: Default agent multi-step reasoning is greedy: at each step, the model takes the single best-looking next action without exploring alternatives. If step 4 takes a suboptimal path, all subsequent steps build on that mistake.

Tree-of-Thought (ToT) explores multiple paths simultaneously: at each decision point, the model generates N candidate next actions, evaluates each, and follows the most promising. It's like a beam search over action sequences vs greedy decoding.

Implement ToT when: the task has many plausible strategies with uncertain outcomes, backtracking is valuable (discovering a dead end and trying another path), or the quality of the final answer is more important than speed.

Implementation approach with the Agent SDK: at critical decision points, spawn N subagents each trying a different approach, collect their results, and let an evaluator agent pick the best path. This is computationally expensive (N × cost of each subagent) but produces better results on difficult reasoning tasks.

---

**Q8: In a multi-step agent that processes large tool outputs, how do you prevent context window exhaustion without losing critical information?**

A: A four-layer strategy:

**Layer 1 — Tool output truncation at source**: every tool function truncates its return value before returning. A web page returns the first 500 words, not the full HTML. A database query returns the first 20 rows.

**Layer 2 — On-demand compression**: after every 5 steps, instruct the model to "summarize all findings so far in 200 words, then continue." The SDK can do this automatically with a `every_N_steps_hook`.

**Layer 3 — External memory for bulky data**: large intermediate results (full documents, raw datasets) are stored in a vector DB or file; only a reference or summary is kept in context.

**Layer 4 — Selective retrieval**: instead of keeping all intermediate results in context, store them externally and retrieve only what's needed for the current step via a `recall_intermediate(topic)` tool.

Applied together: a 50-step agent analyzing 20 large documents can maintain context coherence without hitting the 200K limit.

---

**Q9: What are the quality vs cost tradeoffs in multi-step agent design, and how do you navigate them?**

A: The tradeoffs are:

**More steps → better quality, higher cost**: additional verification steps, cross-checking, and iterative refinement improve accuracy at linear cost increase.

**Fewer steps → lower cost, lower quality**: aggressive truncation and compression save tokens but risk losing critical details.

**Larger model → smarter planning, higher cost per step**: using Opus for multi-step reasoning vs Sonnet can double the cost.

Navigation strategy:
1. **Route by task complexity**: use a small model (Haiku) to classify whether the task needs 1, 5, or 20 steps. Use Sonnet for medium tasks, Opus only for genuinely complex ones.
2. **Max steps by task type**: limit research tasks to 10 steps, analysis to 15, writing to 5.
3. **Quality checkpoints**: add an evaluation step at the end ("Check your answer against the original goal") — this catches most quality issues without adding many steps.
4. **Monitor in production**: track average steps per task and cost per task. Outliers (20+ steps) indicate goals that need to be decomposed upstream.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Chained tool call examples |

⬅️ **Prev:** [Tool Calling in Agents](../04_Tool_Calling_in_Agents/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Agent Memory](../06_Agent_Memory/Theory.md)
