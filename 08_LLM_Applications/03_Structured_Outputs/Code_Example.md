# Structured Outputs — Code Example

Extract structured data from a messy email. Three approaches: prompt-based, tool-based, and Pydantic.

```python
import anthropic
import json
from typing import Optional

client = anthropic.Anthropic()

# The messy input email we want to extract data from
SAMPLE_EMAIL = """
Hey there,

This is Marcus from GlobalTrade Ltd writing in because we have been
trying to reach someone about our account for three weeks now and
nobody has responded. Our main contact is m.johnson@globaltrade.com

The problem: We ordered 500 units of product SKU-4421 back on Feb 3rd
and were charged $12,400 but the order never shipped. Our warehouse
manager is furious and we might have to cancel our entire contract.

Please respond ASAP. This is extremely urgent.

Marcus Johnson
Head of Procurement
GlobalTrade Ltd
"""


# ─────────────────────────────────────────────
# APPROACH 1: Prompt-Based Structured Output
# Simplest, but needs validation
# ─────────────────────────────────────────────

def extract_prompt_based(email: str) -> dict:
    """Extract structured data using prompt instructions."""

    prompt = f"""Extract information from this customer email.
Return ONLY valid JSON with exactly these fields — no explanation, no markdown:

{{
  "sender_name": "full name of the person writing",
  "sender_email": "email address if present, else null",
  "company": "company name",
  "issue_summary": "one sentence describing the problem",
  "urgency": "low | medium | high",
  "financial_amount": "dollar amount if mentioned, else null",
  "requires_immediate_action": true or false
}}

Email:
{email}"""

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=512,
        temperature=0,  # deterministic for extraction
        messages=[{"role": "user", "content": prompt}]
    )

    raw_text = response.content[0].text.strip()

    # Strip markdown code blocks if model adds them
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
        raw_text = raw_text.strip()

    return json.loads(raw_text)


# ─────────────────────────────────────────────
# APPROACH 2: Tool-Based Structured Output
# More reliable — schema is enforced by the API
# ─────────────────────────────────────────────

def extract_tool_based(email: str) -> dict:
    """Use a tool schema to force structured extraction."""

    extraction_tool = {
        "name": "save_email_data",
        "description": "Save the extracted information from the email",
        "input_schema": {
            "type": "object",
            "properties": {
                "sender_name": {
                    "type": "string",
                    "description": "Full name of the email sender"
                },
                "sender_email": {
                    "type": "string",
                    "description": "Email address of the sender"
                },
                "company": {
                    "type": "string",
                    "description": "Company or organization name"
                },
                "issue_summary": {
                    "type": "string",
                    "description": "One sentence summary of the issue"
                },
                "urgency": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "Urgency level based on tone and content"
                },
                "financial_amount": {
                    "type": "number",
                    "description": "Dollar amount mentioned, as a number (e.g. 12400)"
                },
                "requires_immediate_action": {
                    "type": "boolean",
                    "description": "Whether this requires immediate response"
                }
            },
            "required": ["sender_name", "company", "issue_summary", "urgency", "requires_immediate_action"]
        }
    }

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=512,
        temperature=0,
        tools=[extraction_tool],
        tool_choice={"type": "tool", "name": "save_email_data"},  # force this tool
        messages=[
            {"role": "user", "content": f"Extract information from this email:\n\n{email}"}
        ]
    )

    # The structured data is in the tool_use input — no text parsing needed
    for block in response.content:
        if block.type == "tool_use" and block.name == "save_email_data":
            return block.input

    return {}


# ─────────────────────────────────────────────
# APPROACH 3: Pydantic + instructor
# Cleanest approach for typed Python applications
# pip install instructor pydantic
# ─────────────────────────────────────────────

def extract_pydantic_based(email: str) -> dict:
    """
    Use instructor + Pydantic for typed extraction with automatic validation.
    Uncomment when you have instructor installed.
    """

    # from pydantic import BaseModel, EmailStr
    # import instructor
    #
    # class EmailExtraction(BaseModel):
    #     sender_name: str
    #     sender_email: Optional[str] = None
    #     company: str
    #     issue_summary: str
    #     urgency: str  # "low" | "medium" | "high"
    #     financial_amount: Optional[float] = None
    #     requires_immediate_action: bool
    #
    # patched_client = instructor.from_anthropic(client)
    #
    # result = patched_client.messages.create(
    #     model="claude-opus-4-6",
    #     max_tokens=512,
    #     response_model=EmailExtraction,
    #     messages=[{"role": "user", "content": f"Extract info from:\n\n{email}"}]
    # )
    #
    # return result.model_dump()

    return {"note": "Uncomment above after pip install instructor pydantic"}


# ─────────────────────────────────────────────
# RUN ALL THREE AND COMPARE
# ─────────────────────────────────────────────

print("=" * 60)
print("APPROACH 1: Prompt-based extraction")
print("=" * 60)
try:
    result1 = extract_prompt_based(SAMPLE_EMAIL)
    print(json.dumps(result1, indent=2))
except json.JSONDecodeError as e:
    print(f"JSON parse failed: {e}")

print("\n" + "=" * 60)
print("APPROACH 2: Tool-based extraction")
print("=" * 60)
result2 = extract_tool_based(SAMPLE_EMAIL)
print(json.dumps(result2, indent=2))

print("\n" + "=" * 60)
print("APPROACH 3: Pydantic-based (install instructor to activate)")
print("=" * 60)
result3 = extract_pydantic_based(SAMPLE_EMAIL)
print(json.dumps(result3, indent=2))
```

**Expected output (Approach 2 — tool-based):**
```json
{
  "sender_name": "Marcus Johnson",
  "sender_email": "m.johnson@globaltrade.com",
  "company": "GlobalTrade Ltd",
  "issue_summary": "Order of 500 units charged $12,400 was never shipped after 3 weeks",
  "urgency": "high",
  "financial_amount": 12400,
  "requires_immediate_action": true
}
```

**Running this:**
```bash
pip install anthropic
export ANTHROPIC_API_KEY="your-key"
python structured_outputs.py
```

**Key differences between the three approaches:**
- Approach 1: Easy to write, needs JSON validation, can fail if model adds prose
- Approach 2: Schema enforced by API, most reliable without extra libraries
- Approach 3: Typed Python objects, IDE autocomplete, automatic retry — best for large codebases

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [02 Tool Calling](../02_Tool_Calling/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 Embeddings](../04_Embeddings/Theory.md)
