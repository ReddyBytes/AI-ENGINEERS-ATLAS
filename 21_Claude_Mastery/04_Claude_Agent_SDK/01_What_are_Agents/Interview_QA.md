# What Are Agents? — Interview Q&A

## Beginner Level

**Q1: What is an AI agent and how is it different from a regular chatbot?**

<details>
<summary>💡 Show Answer</summary>

A: A chatbot receives a message and returns a single response. An AI agent receives a goal and works toward it through multiple steps — choosing tools, executing actions, observing results, and adapting its plan — without requiring a human to direct each step. The defining difference is the loop: an agent runs perception → reasoning → action → observation repeatedly until the goal is achieved. A chatbot has no loop; it answers once and waits for your next message.

</details>

---

<br>

**Q2: What are the four core components of an agent?**

<details>
<summary>💡 Show Answer</summary>

A: Every agent has:
1. **LLM** — the reasoning engine that decides what to do at each step (in Claude's case, the Claude model)
2. **Tools** — the actions the agent can take: web search, code execution, file read/write, API calls
3. **Context** — the running record of the conversation, past actions, and tool results that serves as the agent's working memory
4. **Loop** — the infrastructure that keeps executing until the goal is met or a stop condition is reached

</details>

---

<br>

**Q3: What is a "stop condition" and why is it critical for agents?**

<details>
<summary>💡 Show Answer</summary>

A: A stop condition is a rule that ends the agent loop. Without one, an agent can loop indefinitely — burning tokens, time, and potentially taking harmful actions repeatedly. Common stop conditions include: the model produces a final answer with no tool call, a maximum number of steps is reached, the token budget is exhausted, or a human interrupt is triggered. Every agent in production must have at least a max-steps safeguard.

</details>

---

## Intermediate Level

**Q4: What is the ReAct loop and how does it relate to the agent pattern?**

<details>
<summary>💡 Show Answer</summary>

A: ReAct (Reason + Act) is the foundational agent loop formulation. At each step, the model explicitly produces a "thought" (reasoning about what to do), an "action" (the tool to call), then observes the result — and repeats. The insight is that interleaving reasoning traces with tool calls makes agents much more reliable than blindly calling tools without reasoning. Modern agent SDKs implement ReAct implicitly: Claude's responses that include tool calls are the "act" phase, and the model's natural reasoning (or extended thinking) handles the "reason" phase. The ReAct paper (Yao et al., 2022) first formalized this as superior to pure chain-of-thought or pure tool use.

</details>

---

<br>

**Q5: At what point on the spectrum from "single call" to "agent" is something actually an agent? How do you classify it?**

<details>
<summary>💡 Show Answer</summary>

A: The spectrum is: Single call → Prompt chain → DAG of prompts → Agent. Something is an agent when it exhibits adaptive autonomy — the path through steps is decided by the model at runtime based on what it observes, not predetermined by the programmer. A fixed chain of 5 prompts is not an agent even if it uses tools; the programmer decided the sequence. An agent is one where the model decides at step N whether to call tool A or tool B (or stop), based on the result of step N-1. The practical test: can the model take a different path than expected if something fails or the data is unexpected? If yes, it's an agent.

</details>

---

<br>

**Q6: Why can't you achieve agent behavior with just a single very long prompt?**

<details>
<summary>💡 Show Answer</summary>

A: A single prompt cannot take actions in the world. No matter how long or carefully engineered the prompt, it produces text — it cannot run code, query a database, call an API, or observe results from the real world. Agents are defined by the combination of reasoning and real-world actions. Additionally, a single call cannot adapt to runtime information — you cannot give the model the result of a Google search until you actually run the search, which requires exiting the single-call paradigm. The loop is necessary to handle the temporal dependency: "do X, then based on the result of X, do Y."

</details>

---

## Advanced Level

**Q7: What are the reliability challenges unique to agents that don't exist in single-call LLM applications?**

<details>
<summary>💡 Show Answer</summary>

A: Agents introduce several failure modes absent from single calls:

**Error propagation**: mistakes in step 3 corrupt the context for all subsequent steps. Unlike a chatbot where each turn is somewhat independent, agent errors compound.

**Loop termination failure**: if the model never decides it's "done," the loop runs until it hits a resource limit. Poorly defined success criteria cause this.

**Context window exhaustion**: long tool outputs (entire web pages, large files) can fill the context, leaving no room for reasoning in later steps.

**Tool execution ordering**: the model may call tools in suboptimal order, or get "stuck" in a local search pattern.

**Hallucinated tool calls**: the model may fabricate tool parameters or call non-existent tools if tool schemas are ambiguous.

**Adversarial content in tool results**: a web search result could contain prompt injection targeting the agent's next actions (see Topic 10, Safety in Agents).

Mitigations include: max-step limits, tool output truncation, defensive tool schemas, explicit success criteria in the system prompt, and human-in-the-loop checkpoints.

</details>

---

<br>

**Q8: How does the agent's context window grow during a long loop, and what are the strategies to manage it?**

<details>
<summary>💡 Show Answer</summary>

A: Each loop iteration appends to context: the tool call and its full result. A web search returning 10,000 characters of text, repeated 15 times, can consume most of a 200K token context window before the task is complete. Strategies to manage this:

**Truncation**: cap tool outputs at N tokens before appending (e.g., first 500 tokens of a web page)
**Summarization**: before appending a long result, have the model summarize it (adds a step but reduces growth)
**Sliding window**: keep only the last K messages in context (risks losing earlier critical information)
**External memory**: store detailed results in a vector DB, keep only a reference in context (see Topic 06)
**Hierarchical agents**: have a subagent process a large document and return only a summary to the parent (see Topic 08)

The Agent SDK handles context passing but the engineer must design the memory strategy.

</details>

---

<br>

**Q9: Compare the agent pattern to traditional software automation (RPA, scripted workflows). When is an agent better and when is it worse?**

<details>
<summary>💡 Show Answer</summary>

A: Traditional RPA (Robotic Process Automation) uses scripted, deterministic paths: click button A, fill field B, extract text from location C. It's fast, predictable, and auditable — but breaks when the UI changes or the input doesn't match expectations.

Agents are adaptive but non-deterministic. They can handle unstructured inputs, varied formats, and unexpected situations by reasoning about them. They're better when: inputs are varied or unstructured, tasks require judgment, the path cannot be predetermined, or the task involves synthesis/summarization.

Agents are worse when: you need strict auditability (the path varies), latency matters (loops take multiple LLM calls), cost matters (every loop step is a billable API call), or the task is fully deterministic and can be scripted. In practice, the best systems combine both: use scripted automation for well-defined sub-tasks and agents for the coordination layer and exception handling.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Visual_Guide.md](./Visual_Guide.md) | Step-by-step diagrams |

⬅️ **Prev:** [Track 3: Model Reference](../../03_Claude_API_and_SDK/13_Model_Reference/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Why Agent SDK?](../02_Why_Agent_SDK/Theory.md)
