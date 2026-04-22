# Prompt Engineering — Code Examples

## Example 1: Zero-shot vs few-shot comparison

```python
import anthropic

client = anthropic.Anthropic()

TEXT = "The product arrived 3 days late and the packaging was torn, but the item itself works great."

# Zero-shot
resp_zero = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=64,
    messages=[{
        "role": "user",
        "content": f"Classify sentiment as POSITIVE, NEGATIVE, NEUTRAL, or MIXED:\n{TEXT}"
    }]
)
print("Zero-shot:", resp_zero.content[0].text)

# Few-shot
FEW_SHOT = """Classify sentiment as POSITIVE, NEGATIVE, NEUTRAL, or MIXED. Return label only.

Text: "Amazing product, arrived early!"
Sentiment: POSITIVE

Text: "Completely broken, waste of money."
Sentiment: NEGATIVE

Text: "It's fine, does what it says."
Sentiment: NEUTRAL

Text: "Love the design but disappointed by battery life."
Sentiment: MIXED

Text: "{text}"
Sentiment:"""

resp_few = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=16,
    temperature=0.0,
    messages=[{
        "role": "user",
        "content": FEW_SHOT.format(text=TEXT)
    }]
)
print("Few-shot:", resp_few.content[0].text.strip())
```

---

## Example 2: Chain-of-thought for math

```python
import anthropic

client = anthropic.Anthropic()

PROBLEM = """A train leaves Chicago at 9am traveling at 60 mph toward New York. 
Another train leaves New York at 11am traveling at 80 mph toward Chicago. 
The cities are 790 miles apart. At what time do the trains meet?"""

# Without CoT
resp_direct = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=256,
    messages=[{"role": "user", "content": PROBLEM}]
)
print("Direct:", resp_direct.content[0].text[:100])

# With CoT
resp_cot = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=512,
    messages=[{
        "role": "user",
        "content": PROBLEM + "\n\nThink step by step, showing each calculation."
    }]
)
print("\nWith CoT:", resp_cot.content[0].text)
```

---

## Example 3: XML-structured extraction system prompt

```python
import anthropic
import json

client = anthropic.Anthropic()

SYSTEM = """
<task>
Extract job posting information from the text the user provides.
</task>

<output_format>
Return valid JSON matching this schema exactly:
{
  "title": "string",
  "company": "string",
  "location": "string",
  "salary_min": number_or_null,
  "salary_max": number_or_null,
  "remote": boolean,
  "required_skills": ["string"],
  "experience_years": number_or_null
}
Return ONLY the JSON object. No markdown. No prose.
</output_format>

<rules>
- Use null for fields not mentioned in the text
- salary values should be annual USD numbers (no currency symbols)
- remote is true only if explicitly mentioned
- required_skills: only list explicitly required skills, max 8
</rules>
"""

def extract_job(posting_text: str) -> dict:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=SYSTEM,
        temperature=0.0,
        messages=[{"role": "user", "content": posting_text}]
    )
    return json.loads(response.content[0].text)

posting = """
Senior Python Developer — TechCorp, San Francisco (Remote OK)
$130,000 - $160,000/year
5+ years experience required. Must know Python, FastAPI, PostgreSQL, and Docker.
Nice to have: Kubernetes, Redis.
"""

result = extract_job(posting)
print(json.dumps(result, indent=2))
```

---

## Example 4: Prefilling assistant turn for guaranteed JSON

```python
import anthropic
import json

client = anthropic.Anthropic()

def extract_with_prefill(text: str) -> dict:
    """Use prefilling to guarantee JSON output."""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system="Extract contact information as JSON. Include: name, email, phone, company. Use null for missing fields.",
        temperature=0.0,
        messages=[
            {"role": "user", "content": f"Extract contact info:\n{text}"},
            {"role": "assistant", "content": "{"}  # prefill forces JSON start
        ]
    )
    
    # Response starts after the prefilled "{"
    full_json = "{" + response.content[0].text
    return json.loads(full_json)

result = extract_with_prefill(
    "Contact our CEO Mike Chen at mike@techcorp.io or 415-555-0199"
)
print(result)
# {"name": "Mike Chen", "email": "mike@techcorp.io", "phone": "415-555-0199", "company": "techcorp"}
```

---

## Example 5: Role prompting for expert analysis

```python
import anthropic

client = anthropic.Anthropic()

CODE = """
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    result = db.execute(query)
    return result.fetchone()
"""

# Generic analysis
generic = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=512,
    messages=[{"role": "user", "content": f"Review this code:\n{CODE}"}]
)

# Expert security review
security_review = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    system="""You are a senior application security engineer with 15 years of experience.
Your reviews follow OWASP Top 10 and focus on: SQL injection, XSS, authentication, authorization, data exposure.
Format: one vulnerability per finding. For each: severity (Critical/High/Medium/Low), description, fix.""",
    messages=[{
        "role": "user",
        "content": f"Security review:\n\n```python\n{CODE}\n```"
    }]
)

print("Generic:", generic.content[0].text[:200])
print("\nSecurity:", security_review.content[0].text)
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept guide |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Common_Mistakes.md](./Common_Mistakes.md) | Common mistakes |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [Vision](../07_Vision/Code_Example.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Prompt Caching](../09_Prompt_Caching/Code_Example.md)
