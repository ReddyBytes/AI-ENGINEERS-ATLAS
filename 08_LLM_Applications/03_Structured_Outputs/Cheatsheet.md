# Structured Outputs — Cheatsheet

**One-liner:** Structured outputs force an LLM to respond in a defined format (JSON, list, template) instead of free-form prose — making its output reliably parseable by your code.

---

## Key Terms

| Term | Definition |
|------|-----------|
| **Structured output** | Model response in a fixed format (JSON, table, list) instead of prose |
| **JSON mode** | API setting that forces the model to return valid JSON |
| **Tool-based extraction** | Using a fake "save" tool to force the model to fill a schema |
| **Pydantic** | Python library for defining typed data models with validation |
| **instructor** | Python library that wraps LLM APIs to return Pydantic objects directly |
| **Schema** | The definition of a data structure — field names, types, and constraints |
| **Validation** | Checking that the output matches the expected structure and types |
| **Retry loop** | Re-calling the model with an error message if the output fails validation |

---

## Three Methods Compared

| Method | Reliability | Complexity | Best For |
|--------|------------|------------|---------|
| Prompt formatting | Medium | Low | Simple, one-off tasks |
| Tool-based output | High | Medium | Any production pipeline |
| Pydantic + instructor | Very High | Low (once set up) | Typed Python applications |

---

## Prompt Formatting Template

```
Extract the following information from the text below.
Return ONLY valid JSON — no explanation, no markdown code blocks:

{
  "field1": "description of field1",
  "field2": "description of field2",
  "field3": "low | medium | high"
}

Text:
[your input here]
```

---

## Tool Schema Template

```python
{
    "name": "save_result",
    "description": "Save the extracted information",
    "input_schema": {
        "type": "object",
        "properties": {
            "field1": {"type": "string", "description": "..."},
            "field2": {"type": "array", "items": {"type": "string"}},
            "field3": {"type": "number"}
        },
        "required": ["field1", "field2"]
    }
}
```

---

## When to Use / Not Use

| Use structured outputs when... | Don't use when... |
|-------------------------------|-------------------|
| Output will be parsed by code | You just need a human-readable answer |
| You need consistent field names | The output is a long essay or explanation |
| You're building a data pipeline | Flexibility in format is acceptable |
| Multiple fields need to be extracted | Single simple value is needed |

---

## Golden Rules

1. **Temperature = 0** for extraction tasks — consistency matters more than creativity.
2. **Specify the format twice** — once in instruction, once as an example shape.
3. **Use `required` fields in your schema** — the model will always fill them.
4. **Validate before using** — never assume the JSON is valid.
5. **Add retry logic** — if validation fails, send the error back to the model with a correction request.
6. **Tool-based > prompt-based** for reliability in production systems.
7. **Pydantic is your friend** — it validates types and gives you IDE autocomplete on the result.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [02 Tool Calling](../02_Tool_Calling/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 Embeddings](../04_Embeddings/Theory.md)
