# System Prompts — Code Examples

## Example 1: Basic persona system prompt

```python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=512,
    system="You are Zara, a cheerful assistant for a flower shop. Always recommend flowers and end every response with a flower emoji.",
    messages=[
        {"role": "user", "content": "What's a good gift for a birthday?"}
    ]
)

print(response.content[0].text)
# Output: "For birthdays, I'd recommend a vibrant sunflower arrangement! 🌻"
```

---

## Example 2: Output format enforcement

```python
import anthropic
import json

client = anthropic.Anthropic()

JSON_EXTRACTOR_SYSTEM = """You are a data extraction engine.
Extract the requested fields from the user's text.
Return ONLY valid JSON. No markdown. No explanation. No prose before or after.
If a field is not found in the text, use null.
"""

def extract_fields(text: str, fields: list[str]) -> dict:
    field_list = ", ".join(fields)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=JSON_EXTRACTOR_SYSTEM,
        messages=[
            {
                "role": "user",
                "content": f"Extract these fields: {field_list}\n\nText: {text}"
            }
        ]
    )
    return json.loads(response.content[0].text)

result = extract_fields(
    text="John Smith, 34 years old, lives in Seattle. Contact: john@example.com",
    fields=["name", "age", "city", "email", "phone"]
)
print(result)
# {"name": "John Smith", "age": 34, "city": "Seattle", "email": "john@example.com", "phone": null}
```

---

## Example 3: Domain restriction

```python
import anthropic

client = anthropic.Anthropic()

PYTHON_TUTOR_SYSTEM = """You are a Python programming tutor.
Your only topic is Python programming.
If asked about other programming languages, say: "I only teach Python. Try asking about the Python equivalent?"
If asked about non-programming topics, say: "I'm specialized in Python programming. I can't help with that, but happy to answer Python questions!"
Always include a code example in your Python answers."""

def ask_tutor(question: str) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=PYTHON_TUTOR_SYSTEM,
        messages=[{"role": "user", "content": question}]
    )
    return response.content[0].text

# In scope
print(ask_tutor("How do list comprehensions work?"))

# Out of scope — Python topic
print(ask_tutor("How do I do list comprehensions in JavaScript?"))

# Out of scope — non-programming
print(ask_tutor("What's the weather like in Paris?"))
```

---

## Example 4: Multi-turn with persistent system prompt

```python
import anthropic

client = anthropic.Anthropic()

SOCRATIC_SYSTEM = """You are a Socratic tutor.
NEVER give direct answers to factual questions.
Instead, ask questions that guide the student step by step toward the answer.
Use the student's own words and build on their previous responses.
After 3 questions, you may reveal the answer if they haven't figured it out."""

history = []

def socratic_session(user_input: str) -> str:
    history.append({"role": "user", "content": user_input})
    
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=SOCRATIC_SYSTEM,
        messages=history
    )
    
    reply = response.content[0].text
    history.append({"role": "assistant", "content": reply})
    return reply

# Session
print("Tutor:", socratic_session("I want to understand why the sky is blue."))
print("Tutor:", socratic_session("Because light bounces off the air?"))
print("Tutor:", socratic_session("Different colors scatter differently?"))
```

---

## Example 5: XML-structured system prompt for customer service

```python
import anthropic

client = anthropic.Anthropic()

SUPPORT_SYSTEM = """
<persona>
You are Alex, a customer support specialist for CloudStore.
You are professional, empathetic, and solution-focused.
Always address the customer by name if they mention it.
</persona>

<scope>
In scope: account questions, billing, product features, technical issues, returns.
Out of scope: competitor comparisons, salary questions, internal company information.
For out-of-scope questions: "I'm not able to help with that, but I'd be happy to assist with your CloudStore account."
</scope>

<escalation>
Escalate to human agent (say "I'm connecting you with a specialist") when:
- Customer mentions legal action or regulatory complaints
- Account security breach suspected
- Billing dispute over $500
- Customer has been waiting more than 3 business days for a resolution
</escalation>

<format>
- Keep responses under 150 words
- Use numbered steps for instructions
- Always end with: "Is there anything else I can help you with today?"
</format>
"""

def handle_support(customer_message: str) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=SUPPORT_SYSTEM,
        messages=[{"role": "user", "content": customer_message}]
    )
    return response.content[0].text

print(handle_support("Hi, I'm Sarah and I can't log into my account."))
print(handle_support("I'm going to sue your company over this billing issue!"))
```

---

## Example 6: System prompt with prompt caching

```python
import anthropic

client = anthropic.Anthropic()

# Long system prompt — ideal for caching
LARGE_SYSTEM_PROMPT = """
You are an expert financial analyst assistant...
""" + ("This system knows extensive financial modeling techniques. " * 100)

def analyze_with_cache(query: str) -> dict:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        # Pass system as array to enable cache_control
        system=[
            {
                "type": "text",
                "text": LARGE_SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"}
            }
        ],
        messages=[{"role": "user", "content": query}]
    )
    
    return {
        "text": response.content[0].text,
        "cache_created": response.usage.cache_creation_input_tokens,
        "cache_read": response.usage.cache_read_input_tokens,
    }

# First call — writes cache (charged at 1.25x)
result1 = analyze_with_cache("What is P/E ratio?")
print(f"Cache created: {result1['cache_created']} tokens")

# Second call within 5 minutes — reads cache (charged at 0.1x)
result2 = analyze_with_cache("What is EBITDA?")
print(f"Cache read: {result2['cache_read']} tokens")
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept guide |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [First API Call](../03_First_API_Call/Code_Example.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Tool Use](../05_Tool_Use/Code_Example.md)
