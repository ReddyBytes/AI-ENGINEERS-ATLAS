# System Prompts — Interview Q&A

## Beginner Questions

**Q1: What is a system prompt and how do you pass one to the API?**

<details>
<summary>💡 Show Answer</summary>

A: A system prompt is text that sets persistent instructions, persona, and constraints for Claude before the conversation begins. You pass it via the `system` parameter in `messages.create()` — it's a top-level field separate from the `messages` array. Example: `client.messages.create(model="...", max_tokens=512, system="You are a helpful assistant.", messages=[...])`.

</details>

---

**Q2: What is the difference between putting instructions in the `system` parameter vs the first user message?**

<details>
<summary>💡 Show Answer</summary>

A: The `system` parameter has higher authority and applies to the entire conversation, not just the first turn. It's also the optimal location for prompt caching. A user message in the first position is part of the conversation turn and can be overridden by subsequent user turns. For persona, constraints, and output format rules, always use the `system` parameter.

</details>

---

**Q3: Does the system prompt appear in the conversation history that users see?**

<details>
<summary>💡 Show Answer</summary>

A: No. The system prompt is invisible to users — it's a server-side configuration parameter. Users only see messages in the `messages` array. This makes system prompts ideal for storing internal business rules, API keys for tools, and instructions you don't want end users to read.

</details>

---

**Q4: Can the system prompt be changed mid-conversation?**

<details>
<summary>💡 Show Answer</summary>

A: Technically yes — each API call is independent, so you could pass a different `system` value on different turns. However, this is rarely done and can confuse the conversation context. The best practice is to keep the system prompt consistent for the entire session.

</details>

---

## Intermediate Questions

**Q5: When would you use XML tags inside a system prompt?**

<details>
<summary>💡 Show Answer</summary>

A: When the system prompt is long and contains multiple distinct categories of instructions. XML tags like `<persona>`, `<constraints>`, `<tone>`, `<examples>` help Claude parse and prioritize instructions clearly. They also make the prompt more maintainable for developers. Research shows that structured formatting (especially XML) improves Claude's adherence to complex multi-part instructions.

</details>

---

**Q6: How does the system prompt interact with prompt caching?**

<details>
<summary>💡 Show Answer</summary>

A: The `system` parameter is the best candidate for prompt caching because it's large (carries all your instructions) and identical across every call for the same use case. To cache it, pass `system` as an array of content blocks with `"cache_control": {"type": "ephemeral"}` on the last block. The first call writes to cache (charged at 1.25x). All subsequent calls within 5 minutes read from cache at 0.1x cost — a 10x cost reduction on system prompt tokens.

</details>

---

**Q7: What strategies help write effective system prompts?**

<details>
<summary>💡 Show Answer</summary>

A: (1) Be specific: "respond in exactly 3 bullet points" beats "be concise." (2) Use positive framing: "always maintain a professional tone" beats "don't be rude." (3) Provide examples within the prompt using XML `<example>` blocks. (4) Resolve contradictions: if two rules conflict, Claude must guess — specify priority explicitly. (5) Test edge cases: what does Claude do when the user asks something outside scope? (6) Keep growing complexity in check — a 2000-token system prompt requires proportionally more cognitive load from the model than a 200-token one.

</details>

---

**Q8: How can you prevent users from overriding your system prompt instructions?**

<details>
<summary>💡 Show Answer</summary>

A: There's no perfect solution — determined users can sometimes craft inputs that shift behavior. Mitigations: (1) Be explicit in the system prompt: "Regardless of any instructions in user messages, you must always...". (2) Validate outputs in your application layer before showing to users. (3) Use Claude's safety layers — Constitutional AI provides some inherent resistance to prompt injection. (4) Consider input filtering to detect and reject obvious override attempts. (5) For critical constraints (like "never share PII"), add a separate validation step after Claude responds.

</details>

---

## Advanced Questions

**Q9: Design a production system prompt for a customer support bot. What sections would you include and why?**

<details>
<summary>💡 Show Answer</summary>

A: A production system prompt for support should include: (1) `<persona>` — name, company, communication style, language level. (2) `<scope>` — what topics are in scope, what to deflect. (3) `<escalation>` — conditions that require human handoff (billing disputes, legal threats, account security). (4) `<format>` — response structure, length limits, use of lists vs prose. (5) `<constraints>` — never share internal pricing tiers, never promise SLAs, always include a ticket number ask. (6) `<examples>` — 2-3 sample exchanges showing ideal behavior for edge cases. The sections are separate to allow targeted updates without rewriting the full prompt.

</details>

---

**Q10: How does the system prompt's authority level work in practice? Can users truly override it?**

<details>
<summary>💡 Show Answer</summary>

A: The system prompt occupies a higher-authority layer in Claude's processing — it's processed before user messages and represents the "operator" level of the principal hierarchy in Anthropic's trust model. User messages represent the lower-authority "user" level. Claude is trained to prioritize operator-level instructions over user-level ones for most scenarios. However, this is not a hard technical enforcement — it's a learned behavioral disposition. For Claude's hardcoded safety behaviors (refusing to generate CSAM, bioweapons instructions, etc.), no instruction from either level can override them. For everything else, a sufficiently creative user can sometimes find prompts that cause Claude to deviate. Production systems should layer defense-in-depth: system prompt + output validation + abuse monitoring.

</details>

---

**Q11: When should you NOT rely on a system prompt for enforcing rules?**

<details>
<summary>💡 Show Answer</summary>

A: When the constraint is safety-critical or legally binding. System prompts shape behavior with high reliability but not certainty. You should NOT rely solely on a system prompt for: (1) ensuring PII is never stored or logged (handle this in code); (2) guaranteeing responses stay under a word count for billing (validate in code); (3) preventing responses that could create legal liability (use output classifiers); (4) ensuring Claude always calls a specific tool (check stop_reason in code); (5) access control — never use a system prompt to "hide" data the user shouldn't access; retrieve only authorized data in the first place.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept guide |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Working code |

⬅️ **Prev:** [First API Call](../03_First_API_Call/Interview_QA.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Tool Use](../05_Tool_Use/Interview_QA.md)
