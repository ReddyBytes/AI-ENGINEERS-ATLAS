# Prompt Engineering — Interview Q&A

## Beginner Questions

**Q1: What is the difference between zero-shot and few-shot prompting?**

<details>
<summary>💡 Show Answer</summary>

A: Zero-shot prompting gives Claude a task description with no examples — you rely on the model's training to understand the task. Few-shot prompting includes 2-5 labeled examples before the actual task, teaching Claude the exact format, style, and edge cases through demonstration. Few-shot is more reliable for tasks with unusual output formats or domain-specific classification schemas.

</details>

---

**Q2: What does "chain-of-thought" prompting do and when should you use it?**

<details>
<summary>💡 Show Answer</summary>

A: Chain-of-thought (CoT) asks Claude to reason through the problem step by step before giving a final answer. Phrases like "think step by step" trigger this behavior. Use CoT for: multi-step math problems, logical reasoning, code debugging, and any task where the answer depends on correctly executing a sequence of sub-tasks. Avoid it for simple fact lookup or classification — it wastes tokens.

</details>

---

**Q3: Why do XML tags improve Claude's prompt adherence?**

<details>
<summary>💡 Show Answer</summary>

A: Claude was trained on large amounts of XML-structured text and learned to associate XML tags with semantic containers. Using `<task>`, `<rules>`, `<examples>`, and `<output_format>` tags tells Claude how to parse different sections of a complex prompt. It reduces ambiguity between what is instruction vs what is data vs what is an example. Well-tagged prompts have more consistent outputs than unstructured ones.

</details>

---

**Q4: What is prefilling the assistant turn, and when is it useful?**

<details>
<summary>💡 Show Answer</summary>

A: Prefilling adds an incomplete assistant message as the last message in the array. Claude must continue from exactly that text. Use it to guarantee output format: prefill `"{"` to force JSON output, prefill a function signature to force code completion, or prefill a specific starting phrase for constrained generation. It's the most reliable way to control the start of Claude's output.

</details>

---

## Intermediate Questions

**Q5: How do you decide between using zero-shot, few-shot, and chain-of-thought for a specific task?**

<details>
<summary>💡 Show Answer</summary>

A: Use a decision tree: (1) If the task is simple and Claude's training covers it well (translation, summarization, simple classification) — try zero-shot first. (2) If the output format is specific or unusual (custom JSON schema, specific labeling vocabulary) — use few-shot with 2-3 examples. (3) If the task requires multi-step reasoning (math, logic puzzles, complex analysis) — use CoT. (4) Combinations work: few-shot CoT examples are especially powerful for reasoning tasks. Measure on 10-20 test cases before deciding.

</details>

---

**Q6: How does temperature affect output quality for different task types?**

<details>
<summary>💡 Show Answer</summary>

A: Temperature controls randomness in token sampling. At `0.0`, Claude always picks the most likely next token — outputs are deterministic and consistent across runs (ideal for classification, data extraction, and code generation). At `1.0`, sampling is more random — outputs vary significantly run-to-run (good for creative writing and brainstorming). For most production tasks, `0.7` (default) balances quality and consistency. For evals and testing, `0.0` is standard because it makes outputs reproducible.

</details>

---

**Q7: What's the most common mistake engineers make with prompt engineering?**

<details>
<summary>💡 Show Answer</summary>

A: Insufficient specificity about output format. "Summarize this" without saying how long, what structure, and for what audience produces widely varying results. Experienced prompt engineers always specify: format (bullet points/prose/JSON), length (words/sentences/tokens), structure (sections/headers/fields), and level of detail (executive summary vs technical deep-dive). The second most common mistake is over-constraining — too many contradictory rules that Claude must guess how to prioritize.

</details>

---

**Q8: How would you extract structured data from unstructured text reliably using Claude?**

<details>
<summary>💡 Show Answer</summary>

A: Use three layers of enforcement: (1) System prompt with explicit JSON schema in the instructions. (2) Few-shot examples showing how to handle edge cases (missing fields → null, ambiguous values → best guess). (3) Prefill `{"` to force JSON immediately. Additionally, set `temperature=0.0` for consistency and wrap the call in a validator that checks the JSON schema — retry if invalid. For high-volume pipelines, log the exact inputs that produce invalid JSON and use them as regression test cases.

</details>

---

## Advanced Questions

**Q9: Design a few-shot prompt for classifying support tickets into 5 categories with high accuracy.**

<details>
<summary>💡 Show Answer</summary>

A: Structure: (1) System: "Classify support tickets into exactly one of: BILLING, TECHNICAL, ACCOUNT_ACCESS, FEATURE_REQUEST, OTHER. Return only the category label." (2) Few-shot examples — 2-3 per category (10-15 total), chosen to cover edge cases (billing question with technical words, feature request disguised as a bug report). (3) Example format: "Ticket: [text]\nCategory: BILLING". (4) Cover hardest edge cases in examples (not the obvious ones). (5) For the actual ticket: "Ticket: {text}\nCategory:". Measure accuracy on a labeled test set of 100 tickets before deploying. Target: rewrite examples for any category below 85% accuracy.

</details>

---

**Q10: Explain how to build a prompt that reliably generates valid JSON with nested objects and arrays.**

<details>
<summary>💡 Show Answer</summary>

A: Use the following stack: (1) System prompt with exact schema defined (use TypeScript-style notation or JSON Schema — both work well). (2) Explicit instruction: "Return ONLY valid JSON. No markdown fences. No prose. No comments in JSON." (3) Few-shot examples showing the schema with various data. (4) Prefill `{"` to guarantee JSON start. (5) Set `temperature=0.0`. (6) Parse the response with `json.loads()` in a try/except. (7) If parsing fails, retry with: "Your previous output was not valid JSON. Return only valid JSON: [previous output]". (8) After 3 failures, fall back to a simpler schema. Monitor JSON parse failure rate and alert if it exceeds 1%.

</details>

---

**Q11: How does prompt engineering interact with model selection? When does Haiku vs Sonnet vs Opus change your prompting strategy?**

<details>
<summary>💡 Show Answer</summary>

A: Smaller models (Haiku) benefit more from extensive few-shot examples — they need more demonstration to match the quality of Sonnet's zero-shot. Chain-of-thought prompting can overcomplicate Haiku for simple tasks — the extended reasoning may introduce errors. Opus is most reliable with minimal prompting — it's powerful enough to infer intent from short instructions. For complex multi-step prompts on Haiku, XML structure helps significantly because it reduces the parsing burden on the model. In cost-sensitive pipelines, the strategy is: start with Sonnet prompts, then simplify them for Haiku routing by adding more examples and explicit structure.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept guide |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Common_Mistakes.md](./Common_Mistakes.md) | Common mistakes |
| [📄 Code_Example.md](./Code_Example.md) | Working code |

⬅️ **Prev:** [Vision](../07_Vision/Interview_QA.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Prompt Caching](../09_Prompt_Caching/Interview_QA.md)
