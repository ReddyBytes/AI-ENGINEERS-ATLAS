# Prompt Engineering — Code Examples

Different prompting strategies using the Anthropic Python SDK.

```python
import anthropic
import json

client = anthropic.Anthropic()  # uses ANTHROPIC_API_KEY env var

# ─────────────────────────────────────────────
# 1. ZERO-SHOT PROMPTING
# No examples — just the instruction
# ─────────────────────────────────────────────

response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=256,
    messages=[
        {
            "role": "user",
            "content": "Classify this review as positive, negative, or neutral. "
                       "Reply with just one word.\n\n"
                       "Review: 'The product arrived on time but broke after a week.'"
        }
    ]
)
print("Zero-shot:", response.content[0].text)
# Output: negative


# ─────────────────────────────────────────────
# 2. FEW-SHOT PROMPTING
# Show 3 examples before the real task
# ─────────────────────────────────────────────

few_shot_prompt = """Classify customer tickets by department. Reply with one word only.

Input: "My order hasn't arrived in 3 weeks"
Output: logistics

Input: "I was charged twice for one purchase"
Output: billing

Input: "The app crashes when I upload a photo"
Output: technical

Input: "I want to cancel my subscription"
Output:"""

response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=10,
    messages=[{"role": "user", "content": few_shot_prompt}]
)
print("Few-shot:", response.content[0].text.strip())
# Output: billing


# ─────────────────────────────────────────────
# 3. CHAIN-OF-THOUGHT PROMPTING
# "Think step by step" improves reasoning accuracy
# ─────────────────────────────────────────────

cot_prompt = """A customer bought 3 items: $12.99, $8.50, and $24.00.
They have a 15% discount coupon and must pay 8% sales tax.
What is their final total?

Think through this step by step before giving the final answer."""

response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=400,
    messages=[{"role": "user", "content": cot_prompt}]
)
print("Chain-of-Thought:\n", response.content[0].text)


# ─────────────────────────────────────────────
# 4. ROLE PROMPTING (SYSTEM MESSAGE)
# Use the system message to set a persistent persona
# ─────────────────────────────────────────────

response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=256,
    system=(
        "You are a senior security engineer. "
        "You explain vulnerabilities in plain English for non-technical executives. "
        "Keep answers under 3 sentences. Use an analogy."
    ),
    messages=[
        {"role": "user", "content": "What is SQL injection?"}
    ]
)
print("Role prompting:\n", response.content[0].text)


# ─────────────────────────────────────────────
# 5. OUTPUT FORMAT CONTROL — JSON
# Tell the model exactly what JSON structure to return
# ─────────────────────────────────────────────

email_text = """
Hi, I'm Sarah from Acme Corp. Our payment system stopped working at 9am today
and we can't process any orders. This is blocking our entire sales team.
Please call me at 555-1234.
"""

extraction_prompt = f"""Extract key information from this support email.
Return ONLY valid JSON with exactly these fields — no explanation, no markdown:

{{
  "sender_name": "first name only",
  "company": "company name",
  "issue": "one sentence description",
  "urgency": "low | medium | high",
  "contact_info": "phone or email if mentioned, else null"
}}

Email:
{email_text}"""

response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=256,
    temperature=0,  # deterministic output for structured extraction
    messages=[{"role": "user", "content": extraction_prompt}]
)

raw = response.content[0].text
result = json.loads(raw)
print("Structured output:", json.dumps(result, indent=2))


# ─────────────────────────────────────────────
# 6. MULTI-TURN CONVERSATION
# Build a conversation by appending to the messages list
# ─────────────────────────────────────────────

conversation = [
    {"role": "user", "content": "I want to learn Python. Where do I start?"}
]

# First turn
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=300,
    system="You are a friendly programming tutor. Keep answers concise.",
    messages=conversation
)
assistant_reply = response.content[0].text
print("Turn 1:", assistant_reply)

# Add assistant reply and continue conversation
conversation.append({"role": "assistant", "content": assistant_reply})
conversation.append({"role": "user", "content": "How long will it take to get job-ready?"})

response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=300,
    system="You are a friendly programming tutor. Keep answers concise.",
    messages=conversation
)
print("Turn 2:", response.content[0].text)


# ─────────────────────────────────────────────
# 7. TEMPERATURE COMPARISON
# Same prompt, different temperature — see the difference
# ─────────────────────────────────────────────

prompt = "Give me a creative name for a coffee shop that focuses on productivity."

for temp in [0.0, 0.5, 1.0]:
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=50,
        temperature=temp,
        messages=[{"role": "user", "content": prompt}]
    )
    print(f"Temperature {temp}: {response.content[0].text.strip()}")

# temp=0.0 always returns the same name
# temp=1.0 returns a different creative name each run
```

**Running this code:**
```bash
pip install anthropic
export ANTHROPIC_API_KEY="your-key-here"
python prompt_examples.py
```

**Key takeaways from the code:**
- Use `system=` for persistent role/rules, `messages=` for the conversation
- Set `temperature=0` for extraction and classification tasks
- Parse JSON with `json.loads()` — always validate the structure
- Multi-turn: keep appending `{"role": "assistant", ...}` and `{"role": "user", ...}` to the messages list

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |
| [📄 Common_Mistakes.md](./Common_Mistakes.md) | Common prompt engineering mistakes |
| [📄 Prompt_Patterns.md](./Prompt_Patterns.md) | Reusable prompt patterns |

⬅️ **Prev:** [09 Using LLM APIs](../../07_Large_Language_Models/09_Using_LLM_APIs/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [02 Tool Calling](../02_Tool_Calling/Theory.md)
