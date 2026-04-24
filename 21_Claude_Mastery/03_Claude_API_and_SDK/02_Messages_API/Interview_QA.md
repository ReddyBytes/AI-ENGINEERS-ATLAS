# Messages API — Interview Q&A

## Beginner Questions

**Q1: What are the three required fields in a Messages API request body?**

<details>
<summary>💡 Show Answer</summary>

A: `model` (which Claude model to use), `max_tokens` (maximum output tokens to generate), and `messages` (the array of conversation turns). All other fields — system, temperature, tools, stream — are optional.

</details>

---

<br>

**Q2: What are the two valid values for the `role` field in a message?**

<details>
<summary>💡 Show Answer</summary>

A: `"user"` and `"assistant"`. Messages must alternate between these two roles, and the final message in the array must always be a user message. Claude will respond as the next assistant turn.

</details>

---

<br>

**Q3: How do you extract the text from a Messages API response in Python?**

<details>
<summary>💡 Show Answer</summary>

A: `response.content[0].text`. The `content` field is a list of content blocks, not a string. The most common response has a single text block at index 0. For safety, also check `response.content[0].type == "text"` before accessing `.text`.

</details>

---

<br>

**Q4: What does `stop_reason: "max_tokens"` mean, and what should you do about it?**

<details>
<summary>💡 Show Answer</summary>

A: It means Claude's response was cut off because it reached the `max_tokens` limit you set — the answer is incomplete. You should either increase `max_tokens`, or implement response continuation by appending Claude's truncated response to the history and asking it to continue.

</details>

---

## Intermediate Questions

**Q5: Explain the four content block types and when each is used.**

<details>
<summary>💡 Show Answer</summary>

A: (1) `"text"` — plain text content, used in both user and assistant messages for regular conversation. (2) `"image"` — used in user messages to send images for vision tasks, with either `base64` or `url` source types. (3) `"tool_use"` — appears in assistant messages when Claude decides to call a tool; contains the tool name and input parameters. (4) `"tool_result"` — used in user messages to return the output of a tool call back to Claude, referenced by `tool_use_id`.

</details>

---

<br>

**Q6: The Messages API is stateless. How do you implement a persistent chatbot?**

<details>
<summary>💡 Show Answer</summary>

A: Maintain a conversation history list in your application. On each user turn: (1) append `{"role": "user", "content": user_message}` to the list; (2) send the full list in the `messages` field; (3) append `{"role": "assistant", "content": response_text}` to the list after receiving the response. Store this list in a database (PostgreSQL, Redis, DynamoDB) keyed by session/user ID so it persists across server restarts.

</details>

---

<br>

**Q7: What is the difference between the `system` parameter and the first `user` message?**

<details>
<summary>💡 Show Answer</summary>

A: The `system` parameter sets persistent instructions that apply across the entire conversation — Claude treats it as the highest-priority context. It is not part of the `messages` array. A user message in the array is a turn in the conversation and is subject to the same alternating role rules. System prompts are used for persona definition, output format instructions, and constraints. They are also the most cost-effective place to put cacheable content with prompt caching.

</details>

---

<br>

**Q8: What happens if you send two consecutive user messages in the messages array?**

<details>
<summary>💡 Show Answer</summary>

A: The API returns a 400 Bad Request error. The messages array must strictly alternate roles: user, assistant, user, assistant. If you need to represent multiple user inputs before a response, combine them into a single user message (using multiple content blocks or a concatenated string).

</details>

---

## Advanced Questions

**Q9: Describe the complete message flow for a tool-use conversation with two tool calls.**

<details>
<summary>💡 Show Answer</summary>

A: Turn 1: User sends a question → Claude responds with `stop_reason: "tool_use"` and a `tool_use` content block in the assistant message. Turn 2: You execute the tool, then send a new user message containing a `tool_result` content block with the result → Claude uses the result, may call another tool (another `tool_use` block), or generate a final response with `stop_reason: "end_turn"`. Turn 3: If another tool call: execute it, send another `tool_result` user message. The conversation continues until Claude produces `stop_reason: "end_turn"`. The history must include all assistant messages (with `tool_use` blocks) and all user `tool_result` messages.

</details>

---

<br>

**Q10: How does prompt caching interact with the messages array structure?**

<details>
<summary>💡 Show Answer</summary>

A: Prompt caching is enabled by adding `"cache_control": {"type": "ephemeral"}` to specific content blocks. Cacheable positions are: (1) the `system` parameter content, (2) the `tools` array, (3) the first N messages in the `messages` array (the static conversation prefix). The cache key is computed from everything in the request up to and including the marked block. The 5-minute TTL resets on each cache hit. The `usage.cache_creation_input_tokens` and `usage.cache_read_input_tokens` fields in the response tell you whether caching was active.

</details>

---

<br>

**Q11: When would you use an array of content blocks for the `content` field vs a simple string?**

<details>
<summary>💡 Show Answer</summary>

A: Use a simple string for text-only user messages in basic chat — it's syntactic sugar that the API converts to `[{"type":"text","text":"..."}]` internally. Use an explicit content block array when: (1) sending images alongside text (vision), (2) sending tool results (requires `tool_result` block type), (3) applying prompt caching markers (`cache_control`) to specific blocks, (4) combining multiple distinct content pieces in one message. The SDK accepts both forms.

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

⬅️ **Prev:** [API Basics](../01_API_Basics/Interview_QA.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [First API Call](../03_First_API_Call/Interview_QA.md)
