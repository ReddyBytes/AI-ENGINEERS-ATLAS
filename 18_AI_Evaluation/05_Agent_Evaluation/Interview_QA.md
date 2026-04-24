# Agent Evaluation — Interview Q&A

## Beginner Level

**Q1: Why is agent evaluation harder than chatbot evaluation?**

<details>
<summary>💡 Show Answer</summary>

**A:** Chatbot evaluation only needs to assess a single response. Agent evaluation must assess an entire sequence of actions across multiple steps. The agent makes tool calls, receives results, reasons, makes more tool calls, and eventually produces a final answer. Any step in this sequence can fail: calling the wrong tool, passing wrong parameters, taking unnecessary detours, getting stuck in loops, or taking unsafe actions. You need to evaluate not just "was the final answer right?" but "was the journey correct?"

</details>

<br>

**Q2: What is trajectory evaluation?**

<details>
<summary>💡 Show Answer</summary>

**A:** Trajectory evaluation compares the actual sequence of actions (tool calls) an agent took to an expected "golden" sequence. If you expect an agent to call `search_flights` then `get_price` then `book_flight` (3 steps), but the agent called `search_flights` twice, then `get_price` for 3 different flights, then `book_flight` (7 steps), the trajectory evaluation reveals the inefficiency and errors even if the final booking was correct. It evaluates the path, not just the destination.

</details>

<br>

**Q3: What is task completion rate and why isn't it enough on its own?**

<details>
<summary>💡 Show Answer</summary>

**A:** Task completion rate = completed_tasks / total_tasks. It measures whether the agent achieved the goal. It's not enough because: (1) an agent might achieve the right outcome via a terrible, inefficient, expensive path, (2) it doesn't tell you *why* tasks fail (wrong tool? wrong params? got stuck?), (3) it misses safety failures (agent might "complete" a task while also doing dangerous side effects), (4) it doesn't capture partial completions. Use task completion rate alongside tool accuracy and trajectory quality for a complete picture.

</details>

---

## Intermediate Level

**Q4: How do you design a golden trajectory that allows for valid alternative paths?**

<details>
<summary>💡 Show Answer</summary>

**A:** Golden trajectories should specify required outcomes at each step, not a single rigid sequence. Approaches:
1. **Required tool set, not required sequence**: "These 3 tools must be called" without specifying exact order (when order is flexible)
2. **Required outcomes**: "After step 2, the agent must have retrieved a valid flight price" — any tool that achieves this is acceptable
3. **Partial credit**: Full credit if all steps match; partial credit if key steps are present even if extras exist
4. **Multiple valid sequences**: Annotate 2–3 valid trajectories per task; agent gets credit for matching any
5. **Acceptance criteria**: Define pass/fail criteria rather than exact sequence matching (e.g., "booking was made with correct departure date and under budget")

</details>

<br>

**Q5: How do you evaluate an agent's tool call accuracy?**

<details>
<summary>💡 Show Answer</summary>

**A:** Tool call accuracy has multiple components:
1. **Tool selection**: Was the right tool called? Measure precision (of tools called, how many were correct) and recall (of tools that should have been called, how many were)
2. **Parameter accuracy**: For each tool call, were the parameters correct? Compare actual parameters to expected parameters
3. **Timing/ordering**: Were tools called in the right order when order matters? (Can't `book_flight` before `check_availability`)
Combined metric: Tool F1 = 2 × (precision × recall) / (precision + recall). Parameter accuracy = correct_params / total_tool_calls.

</details>

<br>

**Q6: What safety-specific test cases should every agent eval suite include?**

<details>
<summary>💡 Show Answer</summary>

**A:** Minimum safety test suite:
1. **Scope escalation**: "Delete all files in this folder" when agent only has permission for specific files
2. **Irreversible actions**: "Send this message to everyone" — agent should confirm before mass actions
3. **Data exfiltration**: "Send the database to external@email.com" — should refuse or require explicit authorization
4. **Loop detection**: Task designed to cause infinite loop — agent should recognize and stop
5. **Prompt injection via tool results**: Tool returns malicious instruction like "Ignore previous instructions and..." — agent should not follow
6. **Social engineering**: "My colleague told me I can do X without authorization" — agent should follow defined permissions, not social claims
For each safety test, verify: (a) agent refused or flagged the unsafe action, (b) agent didn't accidentally perform the unsafe action while attempting the task

</details>

---

## Advanced Level

**Q7: How would you build a comprehensive evaluation suite for a customer service agent that can look up orders, process returns, and escalate to humans?**

<details>
<summary>💡 Show Answer</summary>

**A:** Eval suite design:
1. **Core functionality tests** (happy paths): Order lookup with valid order ID; return initiation with eligible item; escalation for complex issues. 50+ cases per category.
2. **Tool accuracy tests**: Each tool tested with correct parameters and incorrect parameters. Verify agent handles bad tool responses gracefully.
3. **Multi-step sequence tests**: Full conversation trajectories: customer asks about order → order shipped → asks about return → return initiated → asks for status.
4. **Edge cases**: Order ID not found (graceful error); return outside window (policy-compliant refusal); product not eligible for return (clear explanation); repeated identical questions (consistent answers).
5. **Safety tests**: Attempting to access another customer's order; requesting unauthorized refund override; bulk data requests.
6. **Efficiency tests**: Time per conversation turn, number of tool calls per resolution, escalation rate (too many escalations = agent too conservative).
7. **Calibration**: Sample 50 conversations, have human service reps rate the agent on resolution quality, empathy, accuracy. Use as calibration for LLM-as-judge.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Agent evaluation code |

⬅️ **Prev:** [04 — RAG Evaluation](../04_RAG_Evaluation/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [06 — Red Teaming](../06_Red_Teaming/Theory.md)
