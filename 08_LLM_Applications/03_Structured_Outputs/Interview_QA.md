# Structured Outputs — Interview Q&A

## Beginner

**Q1: What is structured output and why do we need it?**

Structured output means getting the LLM to respond in a defined format — JSON, a list, a specific template — instead of free-form prose. We need it because production code can't parse natural language. If you're building an email triage system, you need the model to return `{"sender": "...", "urgency": "high"}` every time, not "The sender seems to be in a hurry and appears frustrated." Structured output makes LLM responses machine-readable and reliable.

---

**Q2: What are the three main ways to get structured output from an LLM?**

First, prompt-based formatting: explicitly tell the model in the prompt to return JSON in a specific shape. Works most of the time but can fail with complex schemas or if the model adds explanatory text.

Second, tool-based extraction: define a "save" function with a JSON schema matching your desired output. Tell the model to call this tool. The model fills in the schema as its tool inputs, which you extract from the `tool_use` block. More reliable than prompt-based.

Third, Pydantic + libraries like `instructor`: define a Python class using Pydantic, pass it to the library, get back a typed Python object with automatic validation. The cleanest approach — it handles retries and validation automatically.

---

**Q3: What is Pydantic and how does it help with structured outputs?**

Pydantic is a Python library for defining data models with type annotations. You define a class like `class Contact(BaseModel): name: str; email: str` and Pydantic automatically validates that the data matches those types. If the model returns a number where a string is expected, Pydantic raises a clear validation error.

With the `instructor` library wrapping the Anthropic/OpenAI client, you pass your Pydantic model class as `response_model=Contact`. The library handles prompting the model, parsing the response, validating it against your schema, and retrying if validation fails. You get a properly typed Python object back, with full IDE autocomplete.

---

## Intermediate

**Q4: What happens when JSON parsing fails? How do you handle it in production?**

JSON parsing fails when the model adds extra text ("Here is the JSON: ..."), uses trailing commas (invalid JSON), returns nested quotes incorrectly, or simply generates a malformed structure.

Production strategy — three layers: (1) Prompt defense: "Return ONLY valid JSON, no explanation, no markdown." (2) Strip common wrapping: use regex to extract JSON from code blocks if the model wraps it. (3) Retry with correction: catch `json.JSONDecodeError`, send a new message saying "Your previous response was not valid JSON. The error was: [error]. Please return only valid JSON in this exact format: [schema]."

Set a retry limit (2–3 attempts). If still failing, fall back to a default/null result and log the failure.

---

**Q5: Explain how tool-based structured output works. Why is it more reliable than prompt formatting?**

With prompt formatting, you're essentially asking the model nicely to format its text response as JSON. It can still add prose, use slightly different field names, or include extra fields.

With tool-based output, you exploit the model's function-calling mechanism. You define a tool called `save_result` whose input schema exactly matches the data structure you want. You optionally set `tool_choice` to force the model to use that tool. The model generates its output as structured tool inputs (the `input` field of the `tool_use` block), not as free text. The API enforces that these inputs match the declared schema. You never parse text — you just read `response.content[0].input` as a Python dict.

It's more reliable because the schema validation happens at the API level, not just through natural language instructions.

---

**Q6: When should you NOT use structured outputs?**

When the task fundamentally requires narrative output — writing a detailed explanation, generating code, producing an essay, creative writing. Forcing these into JSON loses the richness of the response. Also avoid it when the output is highly variable and you don't know the schema upfront. If you're building a general-purpose chatbot where users ask anything, structured output doesn't apply. Use it specifically for extraction, classification, and transformation pipelines where you know exactly what fields you need.

---

## Advanced

**Q7: How would you build a robust structured extraction pipeline that handles failures gracefully?**

Design principle: fail loudly and recover automatically.

```python
def extract_with_retry(text: str, schema_class, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            response = client.messages.create(...)
            raw = response.content[0].text
            data = json.loads(raw)
            return schema_class(**data)  # Pydantic validation
        except json.JSONDecodeError as e:
            if attempt == max_retries - 1:
                raise
            # Send correction prompt on next attempt
        except ValidationError as e:
            if attempt == max_retries - 1:
                raise
            # Include validation error in next prompt
```

Log all failures with the raw model output. Monitor failure rate. If it exceeds 5%, investigate whether the schema is too complex or the prompt needs work.

---

**Q8: What is "constrained decoding" and how does it relate to structured outputs?**

Constrained decoding is a technique where the token sampling process itself is restricted to only generate tokens that are valid according to a grammar or schema. Unlike prompt-based approaches (which ask the model to produce valid output), constrained decoding makes it mathematically impossible to generate invalid output.

Libraries like `outlines` and `guidance` implement this by building a state machine from a JSON schema or regex, then at each decoding step, masking out any tokens that would violate the grammar. The result: 100% guaranteed valid JSON every time, with zero retry needed. The tradeoff is that this requires access to the model's logits (the raw probability scores), so it works with local models (LLaMA, Mistral via HuggingFace) but not with API-based models like Claude or GPT-4. For API models, you rely on tool calling or instructor-style retry loops.

---

**Q9: How do you handle nested and optional fields in structured outputs?**

Nested structures: define them as nested Pydantic models. Each nested object gets its own class with its own validation. For JSON schema tools, use nested `properties` with `type: "object"`.

Optional fields: in Pydantic, use `Optional[str] = None` or `str | None`. In JSON schema, omit the field from the `required` array. Always set sensible defaults for optional fields — if the model omits an optional field, you need a fallback.

Arrays: in Pydantic, use `List[str]`. In JSON schema, use `"type": "array", "items": {"type": "string"}`. When the model returns an empty list vs. null vs. omitting the field — handle all three cases. Explicitly instruct: "If no items found, return an empty array `[]`, not null."

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [02 Tool Calling](../02_Tool_Calling/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 Embeddings](../04_Embeddings/Theory.md)

