# Prompt Engineering — Common Mistakes

10 mistakes that make prompts fail in production. For each: what it looks like, why it happens, and how to fix it.

---

## Mistake 1: Vague Instructions

**What it looks like:**
```
"Write something about our product."
```

**Why it happens:** You know what you want in your head, but you haven't said it out loud. Seems obvious to you, isn't to the model.

**How to fix it:**
```
"Write a 3-sentence product description for our noise-cancelling headphones.
Target audience: remote workers aged 25–40. Tone: professional but warm.
Highlight: 30-hour battery life, 40dB noise cancellation, foldable design."
```

Specify: who it's for, what tone, what to include, how long.

---

## Mistake 2: No Output Format

**What it looks like:**
You need JSON for your code but you wrote: "Extract the name and email from this message."

The model returns: "The name is John Smith and the email is john@example.com."

Your `json.loads()` crashes.

**Why it happens:** Natural language is the model's default. It doesn't know you need structured data unless you say so.

**How to fix it:**
```
"Extract name and email. Return ONLY this JSON, no other text:
{"name": "...", "email": "..."}"
```

Always specify the exact output format in production prompts.

---

## Mistake 3: Over-Constraining

**What it looks like:**
```
"Answer in exactly 47 words, use no adjectives, always start with a verb,
include a statistic, don't use the word 'the', and use bullet points."
```

**Why it happens:** You want control. Too many constraints conflict with each other.

**How to fix it:** Pick the 2–3 constraints that actually matter. Let the model handle the rest. Over-constraining causes the model to fail some constraints while trying to satisfy others.

---

## Mistake 4: Ignoring Temperature

**What it looks like:**
Using default temperature (0.7–1.0) for a data extraction task that needs consistent output.

Every run returns slightly different JSON structure. Your parsing code breaks on 20% of calls.

**Why it happens:** Temperature defaults are set for general use. Most extraction/classification tasks need determinism.

**How to fix it:** Set `temperature=0` for:
- Data extraction
- Classification
- Code generation
- Any task where you parse the output programmatically

Use higher temperature only for creative writing and brainstorming.

---

## Mistake 5: No Examples for Custom Formats

**What it looks like:**
"Classify this ticket using our internal priority system."

The model doesn't know your internal priority system. It guesses.

**Why it happens:** You assume the model knows your system. It doesn't.

**How to fix it:** Add 3 examples of your actual classification system:
```
P0: Production down, customer-facing, financial impact
P1: Major feature broken, workaround exists
P2: Minor bug, low customer impact

Example: "Database is down in production" → P0
Example: "Report exports are slow" → P2
```

---

## Mistake 6: Putting Instructions at the End Only

**What it looks like:**
```
[Long email here — 500 words]

Now summarize this in 2 sentences.
```

**Why it happens:** Feels natural — describe the thing, then the task.

**How to fix it:** Put the key instruction at the beginning AND the end for long prompts:
```
Summarize the following email in exactly 2 sentences.

[Long email here — 500 words]

Remember: exactly 2 sentences, focus on action items.
```

Models pay more attention to content at the start and end of context. Sandwich your instructions.

---

## Mistake 7: Relying on the Model to Know Implicit Rules

**What it looks like:**
"Write a blog post about machine learning."

You expected it to avoid jargon because your site is for beginners. It uses terms like "gradient descent" and "backpropagation" with no explanation.

**Why it happens:** Your assumptions aren't in the prompt. The model doesn't know your audience.

**How to fix it:** Make every assumption explicit:
```
"Write a 500-word blog post about machine learning for complete beginners (age 15+).
Avoid all technical jargon. If you must use a technical term, explain it immediately.
Use one analogy per concept."
```

---

## Mistake 8: Not Testing Edge Cases

**What it looks like:**
Your email extraction prompt works great on test cases. In production, it fails when:
- The email is empty
- There are two email addresses
- The email is in Spanish
- The message is just "???"

**Why it happens:** You test the happy path. Edge cases only appear in production.

**How to fix it:**
- Test with empty input
- Test with ambiguous input
- Test with wrong language
- Test with adversarial input
- Add instructions for failure cases: "If no email is found, return `{"email": null}`"

---

## Mistake 9: Forgetting Token Limits

**What it looks like:**
You stuff 50 customer reviews into one prompt and ask for individual analysis of each.

The model runs out of context window and truncates, or gives a summary response instead of per-review analysis.

**Why it happens:** Context limits aren't obvious until you hit them.

**How to fix it:**
- Know your model's context window (Claude: 200K tokens, GPT-4o: 128K tokens)
- For large inputs: chunk them and process in batches
- For long conversations: summarize earlier messages instead of keeping the full history
- Estimate: 1 token ≈ 0.75 words; 1 page ≈ 500 tokens

---

## Mistake 10: Not Iterating on Failures

**What it looks like:**
The prompt returns a bad output. You change the model. Or add more instructions randomly. Output is still bad. You give up.

**Why it happens:** No systematic debugging process.

**How to fix it — the debugging loop:**
1. Find the specific failure (what exactly is wrong?)
2. Isolate the cause (missing context? Wrong format? Model doesn't know this?)
3. Make one change at a time and test
4. Log your prompt versions and their results

Prompt engineering is iterative. A prompt that works 95% of the time might need 10 iterations to get to 99%.

---

## Quick Reference: Mistake Checklist

Before shipping any prompt to production, check:

- [ ] Task is described specifically with audience and constraints
- [ ] Output format is explicitly specified
- [ ] `temperature=0` for extraction/classification tasks
- [ ] 2–3 examples included for custom patterns
- [ ] Tested with empty, ambiguous, and adversarial inputs
- [ ] Instructions appear at both start and end for long prompts
- [ ] All implicit assumptions are made explicit
- [ ] Token limits considered for large inputs
- [ ] Failure cases handled ("if not found, return null")
- [ ] Iterating on specific failures, not random changes

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |
| 📄 **Common_Mistakes.md** | ← you are here |
| [📄 Prompt_Patterns.md](./Prompt_Patterns.md) | Reusable prompt patterns |

⬅️ **Prev:** [09 Using LLM APIs](../../07_Large_Language_Models/09_Using_LLM_APIs/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [02 Tool Calling](../02_Tool_Calling/Theory.md)
