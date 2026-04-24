# Multimodal Agents — Interview Q&A

## Beginner Level

**Q1: What is a computer use agent?**

<details>
<summary>💡 Show Answer</summary>

**A:** A computer use agent is an AI agent that interacts with a computer by looking at screenshots of the screen (like a human would) and executing actions — mouse clicks, keyboard input, scrolling. Instead of calling a structured API, it perceives the raw visual UI and acts on what it sees. Anthropic's Computer Use feature (launched 2024) is the most visible example. It enables agents to operate any software, even software with no programmatic API.

</details>

<br>

**Q2: What is the grounding problem in multimodal agents?**

<details>
<summary>💡 Show Answer</summary>

**A:** Grounding is the challenge of connecting a language description ("click the Submit button") to the actual pixel coordinates on a screen. The agent might understand "Submit button" semantically but needs to know exactly where it is (e.g., x=450, y=820) to click it. This is harder than it sounds because UI layouts vary, buttons aren't always where you'd expect, and vision models aren't precise at outputting exact coordinates.

</details>

<br>

**Q3: What is a voice agent and how does it work?**

<details>
<summary>💡 Show Answer</summary>

**A:** A voice agent combines three AI systems in sequence: (1) STT (Speech-to-Text, typically Whisper) converts user's spoken words to text, (2) an LLM processes the text and generates a response, (3) TTS (Text-to-Speech, like ElevenLabs or OpenAI TTS) converts the response text to spoken audio. This creates a natural voice-in, voice-out conversational interface.

</details>

---

## Intermediate Level

**Q4: What is Set-of-Marks (SoM) and why does it improve computer use agents?**

<details>
<summary>💡 Show Answer</summary>

**A:** Set-of-Marks is a prompting technique where you pre-process the screenshot by overlaying numbered labels (1, 2, 3...) on all detected interactive UI elements, then ask the model "which element number do you want to interact with?" Instead of asking the model to output precise pixel coordinates (which it does poorly), you ask it to choose a number (which it does well). The runtime maps the chosen number back to the pre-detected coordinates. SoM dramatically improves grounding accuracy compared to asking for raw coordinates.

</details>

<br>

**Q5: What are the main latency and cost challenges in computer use agents?**

<details>
<summary>💡 Show Answer</summary>

**A:** Each step in a computer use agent involves: screenshot capture (~100ms) + vision API call (1–5 seconds) + action execution (~100ms). A 20-step task takes 20–120 seconds. Cost: at ~$0.02–0.05 per screenshot (depends on resolution and model), a 20-step task costs $0.40–$1.00. Optimization strategies: (1) resize screenshots to 1280×720 (saves ~50% tokens), (2) use efficient models like Claude Haiku for perception, (3) cache UI state when it hasn't changed, (4) decompose tasks into parallel sub-tasks where possible.

</details>

<br>

**Q6: What safety considerations are critical for computer use agents?**

<details>
<summary>💡 Show Answer</summary>

**A:** Key safety requirements:
1. **Sandboxing**: Always run in an isolated VM or container. An uncontrolled agent can delete files, send emails, make purchases.
2. **Irreversible action confirmation**: Before any action that can't be undone (form submission, file deletion, email sending), pause and require human confirmation.
3. **Action logging**: Record every screenshot and every action taken for audit.
4. **Step limits**: Set a maximum number of steps to prevent infinite loops.
5. **Network isolation**: Disable internet access by default unless the task explicitly requires it.
6. **Credential hygiene**: Never pass passwords or API keys in the agent's context — use a secure credential vault instead.

</details>

---

## Advanced Level

**Q7: How would you architect a production computer use agent that handles long, multi-step tasks reliably?**

<details>
<summary>💡 Show Answer</summary>

**A:** Architecture for a reliable long-horizon computer use agent:
1. **Task decomposition**: Before executing, have the LLM decompose the task into discrete subtasks with defined completion criteria
2. **Checkpointing**: After each subtask completion, save a checkpoint (screenshot + extracted state). On failure, resume from last successful checkpoint
3. **Verification steps**: After each major action, take a screenshot and verify the expected result occurred ("the form was successfully submitted" = confirmation dialog visible)
4. **Context compression**: After 10+ steps, summarize earlier history to avoid context window overflow
5. **Error recovery**: Define error states (element not found, page timeout, unexpected dialog) and recovery strategies for each
6. **Sandboxed environment**: Run in a containerized browser (Playwright) or VM snapshot that can be reset
7. **Human-in-the-loop gates**: Escalate to human review for ambiguous states or high-stakes confirmations
8. **Monitoring**: Track success rate per task type, average steps per task, cost per task

</details>

<br>

**Q8: Compare DOM-based web agents vs pure vision-based web agents. When would you use each?**

<details>
<summary>💡 Show Answer</summary>

**A:**
- **DOM-based agents** (e.g., Playwright with element selectors): Parse the HTML structure, identify elements by CSS selectors or ARIA labels, interact programmatically. Pros: precise, fast, doesn't need visual AI. Cons: fails on canvas-based UIs, doesn't handle dynamically loaded content well, doesn't work on non-web interfaces.
- **Pure vision-based agents** (screenshot → VLM → action): Process screenshots like a human. Pros: works on any interface (desktop apps, games, web), understands visual context, handles unusual layouts. Cons: more expensive (token cost per screenshot), slower (LLM inference per step), less precise for small UI elements.
- **Hybrid approach** (recommended): Use DOM for web tasks when possible (precise + cheap), fall back to vision when DOM fails or for non-web interfaces. Use Set-of-Marks to bridge visual understanding with programmatic element IDs.

</details>

<br>

**Q9: System design question: Design a voice customer support agent that handles order tracking, returns, and refunds.**

<details>
<summary>💡 Show Answer</summary>

**A:** Architecture:
1. **Input processing**:
   - Phone/web audio → streaming STT (Deepgram real-time) → incremental text
   - VAD to detect end of utterance, start processing immediately
2. **Intent classification**: Fast LLM call to classify: order_tracking | return_request | refund_request | escalate_human | other
3. **Tool-calling agent**:
   - `get_order_status(order_id)` → database/API call
   - `create_return_request(order_id, reason)` → OMS integration
   - `process_refund(order_id, amount)` → payment system
   - `escalate_to_human(context)` → transfer with summary
4. **Response generation**: Streaming LLM → streaming TTS (ElevenLabs Flash for low latency)
5. **Multi-turn memory**: Maintain conversation state within session; customer account context loaded at start
6. **Guardrails**: Never confirm refund >$X without human approval; log all transactions
7. **Quality monitoring**: Record conversations (with consent), run LLM-as-judge on sample, track resolution rate
Key metric: first-contact resolution rate. Escalation rate to human: keep below 30% for good AI ROI.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | Architecture diagrams |
| [📄 Code_Example.md](./Code_Example.md) | Code examples |

⬅️ **Prev:** [06 — Multimodal Embeddings](../06_Multimodal_Embeddings/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Section 18 — AI Evaluation](../../18_AI_Evaluation/01_Evaluation_Fundamentals/Theory.md)
