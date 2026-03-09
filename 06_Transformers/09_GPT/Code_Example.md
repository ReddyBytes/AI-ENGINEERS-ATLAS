# GPT — Code Example

## Load GPT-2 and Generate Text

```python
# pip install transformers torch

from transformers import GPT2LMHeadModel, GPT2Tokenizer, pipeline

# ─────────────────────────────────────────
# 1. Basic text generation with pipeline
# ─────────────────────────────────────────
generator = pipeline("text-generation", model="gpt2")

prompts = [
    "The future of artificial intelligence is",
    "Once upon a time, a scientist discovered",
    "The best way to learn machine learning is",
]

print("=== GPT-2 Text Generation ===")
for prompt in prompts:
    outputs = generator(
        prompt,
        max_new_tokens=60,
        num_return_sequences=1,
        temperature=0.8,
        do_sample=True,
    )
    generated = outputs[0]["generated_text"]
    print(f"\nPrompt: {prompt}")
    print(f"Output: {generated}")
    print("-" * 60)
```

**Example output:**

```
Prompt: The future of artificial intelligence is
Output: The future of artificial intelligence is uncertain, but there are
signs it will reshape every industry from healthcare to transportation.
Machines are already outperforming humans in narrow tasks, and the question
is no longer whether AI can do X but whether humans will remain in the loop.
```

---

## Temperature comparison

```python
# ─────────────────────────────────────────
# 2. Compare different temperatures
# ─────────────────────────────────────────
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2")

import torch

prompt = "The robot looked at the human and said"
inputs = tokenizer(prompt, return_tensors="pt")

temperatures = [0.3, 0.7, 1.0, 1.5]

print("=== Temperature Comparison ===")
print(f"Prompt: {prompt}\n")

for temp in temperatures:
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=40,
            temperature=temp,
            do_sample=(temp > 0),
            pad_token_id=tokenizer.eos_token_id,
        )
    text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    continuation = text[len(prompt):]
    print(f"Temperature {temp}: ...{continuation.strip()}")
    print()
```

**Example output:**

```
Temperature 0.3: ..."I am here to help you." The robot smiled and walked away.

Temperature 0.7: ..."We need to talk." The human backed against the wall, eyes wide.

Temperature 1.0: ..."You're not what I expected," and reached for the console nearby.

Temperature 1.5: ..."Krrrzxx signal," and then vanished in a swirl of misty circuits.
```

Low temperature: predictable, coherent. High temperature: creative, sometimes incoherent.

---

## Tokenization inspection

```python
# ─────────────────────────────────────────
# 3. See how GPT-2 tokenizes text
# ─────────────────────────────────────────
texts = [
    "The future of AI",
    "ChatGPT is amazing",
    "Supercalifragilistic",
    "1 + 1 = 2",
]

print("=== GPT-2 Tokenization ===")
print(f"{'Text':<30} {'Tokens':<45} {'Count'}")
print("-" * 80)

for text in texts:
    token_ids = tokenizer.encode(text)
    tokens = tokenizer.convert_ids_to_tokens(token_ids)
    print(f"{text:<30} {str(tokens):<45} {len(tokens)}")
```

**Output:**

```
Text                           Tokens                                        Count
--------------------------------------------------------------------------------
The future of AI               ['The', 'Ġfuture', 'Ġof', 'ĠAI']            4
ChatGPT is amazing             ['Chat', 'G', 'PT', 'Ġis', 'Ġamazing']       5
Supercalifragilistic           ['Super', 'cal', 'ifrag', 'il', 'istic']      5
1 + 1 = 2                      ['1', 'Ġ+', 'Ġ1', 'Ġ=', 'Ġ2']               5
```

Note: `Ġ` prefix = space before the token (GPT-2's way of marking word boundaries).

---

## Few-shot prompting (GPT-style)

```python
# ─────────────────────────────────────────
# 4. Few-shot text classification via prompting
# ─────────────────────────────────────────
# This works much better with GPT-3/4 via API, but illustrates the concept

few_shot_prompt = """Classify the sentiment of each review as POSITIVE or NEGATIVE.

Review: "This product is absolutely amazing!"
Sentiment: POSITIVE

Review: "Terrible quality, broke after one day."
Sentiment: NEGATIVE

Review: "Best purchase I've made this year."
Sentiment: POSITIVE

Review: "I can't believe how bad this is."
Sentiment: NEGATIVE

Review: "Works exactly as described, very happy."
Sentiment:"""

inputs = tokenizer(few_shot_prompt, return_tensors="pt")

with torch.no_grad():
    output = model.generate(
        **inputs,
        max_new_tokens=5,
        temperature=0.1,  # low temp for more deterministic output
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id,
    )

result = tokenizer.decode(output[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
print(f"GPT-2 prediction: {result.strip()}")
# Expected: POSITIVE (small models may not get this right reliably)
```

---

## Comparing GPT-2 with larger instruction-tuned models

```python
# Using HuggingFace's text-generation-inference or OpenAI API for larger models
# Here we compare GPT-2 with a small instruction-tuned model

from transformers import pipeline

# GPT-2 (raw pretrained — just completes text)
gpt2_gen = pipeline("text-generation", model="gpt2")

print("=== GPT-2 (raw): 'Explain neural networks in one sentence.' ===")
result = gpt2_gen(
    "Explain neural networks in one sentence.",
    max_new_tokens=50,
    temperature=0.7,
    do_sample=True,
)
print(result[0]["generated_text"])

# Note: GPT-2 will just continue the text, not actually explain anything
# A model fine-tuned with RLHF (like GPT-3.5-turbo via API) would give
# a proper explanation because it was trained to follow instructions.
print()
print("Key insight: GPT-2 completes text. InstructGPT/ChatGPT follows instructions.")
print("The difference is RLHF fine-tuning, not just scale.")
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [08 BERT](../08_BERT/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [10 Vision Transformers](../10_Vision_Transformers/Theory.md)