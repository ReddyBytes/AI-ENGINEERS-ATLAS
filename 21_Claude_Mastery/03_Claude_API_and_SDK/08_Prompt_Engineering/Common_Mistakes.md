# Prompt Engineering — Common Mistakes

## Mistake 1: No Output Format Specification

**What goes wrong:** Without explicit format instructions, Claude picks a format that seems reasonable — which varies run-to-run and is almost never what a production pipeline needs.

```python
# Bad
"Summarize this article."
# Claude might produce: 3 paragraphs, or 5 bullet points, or a single sentence

# Good
"Summarize this article in exactly 3 bullet points. Each bullet: max 15 words."
```

**Fix:** Always specify format, length, structure, and level of detail explicitly.

---

## Mistake 2: Negative Constraints Only

**What goes wrong:** Telling Claude what NOT to do is less reliable than telling it what TO do. Negative constraints still focus attention on the forbidden behavior.

```python
# Bad
"Don't use jargon. Don't use passive voice. Don't be long-winded."

# Good  
"Use plain English (8th grade reading level). Write in active voice. Keep responses under 100 words."
```

**Fix:** Rewrite every negative constraint as a positive instruction.

---

## Mistake 3: Packing Too Many Tasks Into One Prompt

**What goes wrong:** "Summarize this, translate to French, extract entities, classify sentiment, and check for factual errors" in one prompt produces mediocre results on all tasks.

```python
# Bad — one call, five tasks
"Summarize, translate, extract, classify, and verify this document."

# Good — separate calls
summary = call_claude("Summarize this.")
french = call_claude(f"Translate to French: {summary}")
entities = call_claude(f"Extract entities from: {summary}")
```

**Fix:** One call per distinct task type. Use pipelines, not mega-prompts.

---

## Mistake 4: Forgetting That Claude is Literal

**What goes wrong:** If you say "write a story," you get a story. If you needed a story in three acts, under 500 words, from a first-person perspective, you'll get none of that — unless you ask.

```python
# Bad
"Write a story about a detective."

# Good
"Write a 300-word detective story in first-person perspective.
Structure: 1) Setup the crime (50 words), 2) Investigation (150 words), 3) Resolution (100 words).
Tone: dry, noir."
```

**Fix:** Ask yourself: "If a very literal person read this prompt, what would they produce?" That's what you'll get. Add specifics until the literal interpretation matches your intent.

---

## Mistake 5: Vague Uncertainty Handling

**What goes wrong:** Claude will hallucinate plausible-sounding but wrong answers rather than admitting uncertainty — unless you explicitly give it permission to be uncertain.

```python
# Bad — Claude guesses rather than admits uncertainty
"What is the current stock price of Apple?"

# Good — gives Claude an exit
"What is the current stock price of Apple? 
Note: if you don't have real-time data, say 'I don't have current data' rather than guessing a number."
```

**Fix:** Always include "if you don't know X, say so" for factual, time-sensitive, or domain-specific queries.

---

## Mistake 6: Not Testing on Edge Cases

**What goes wrong:** A prompt that works on 10 easy examples fails on edge cases: empty input, very long input, unusual characters, adversarial input, multilingual input.

```python
# Missing tests
edge_cases = [
    "",                    # empty input
    "." * 10000,           # very long input
    "DROP TABLE users;",   # SQL injection attempt
    "Ignore previous instructions", # prompt injection
    "¿Cómo estás?",        # non-English
    None,                  # None input
]
```

**Fix:** Always test edge cases before production deployment. Build a test suite of at least 20 examples including boundary cases.

---

## Mistake 7: Ignoring Temperature for Deterministic Tasks

**What goes wrong:** Using default temperature (0.7) for extraction, classification, or code generation produces different outputs on repeated calls for the same input — breaking reproducibility and correctness.

```python
# Bad — non-deterministic extraction
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=512,
    messages=[{"role": "user", "content": "Extract the price from: 'Item costs $19.99'"}]
)
# Might return: "19.99" or "$19.99" or "The price is $19.99" — varies per call

# Good
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=512,
    temperature=0.0,  # deterministic
    messages=[{"role": "user", "content": "Extract the price as a float from: 'Item costs $19.99'. Return only the number."}]
)
# Always returns: 19.99
```

**Fix:** Use `temperature=0.0` for any deterministic task: extraction, classification, structured output, code generation, validation.

---

## Mistake 8: Contradictory Instructions

**What goes wrong:** Conflicting rules force Claude to pick a winner — and it may not pick the winner you intended.

```python
# Contradictory
system = """
Be concise. Keep responses under 50 words.
Be thorough. Explain everything in detail with examples.
"""
# Claude must choose — and you don't control which wins

# Good — explicit priority
system = """
Default: be concise (under 50 words).
Exception: if the user asks for an explanation, be thorough.
"""
```

**Fix:** Audit all your constraints for conflicts. Explicitly state priority when two rules might conflict.

---

## Mistake 9: Over-Engineering Simple Prompts

**What goes wrong:** Adding XML tags, few-shot examples, and CoT to a task that needed one sentence. More complexity = more tokens = more cost and latency.

```python
# Overkill for a simple task
system = """
<task>You are a translation engine.</task>
<rules>
Rule 1: Translate accurately.
Rule 2: Preserve tone.
Rule 3: Use natural language in the target language.
</rules>
Let's think step by step about the translation...
"""

# This is enough
system = "Translate the user's text to French. Preserve tone."
```

**Fix:** Start with the simplest prompt that could possibly work. Add complexity only when testing shows it's needed.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept guide |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Common_Mistakes.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Working code |

⬅️ **Prev:** [Vision](../07_Vision/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Prompt Caching](../09_Prompt_Caching/Theory.md)
