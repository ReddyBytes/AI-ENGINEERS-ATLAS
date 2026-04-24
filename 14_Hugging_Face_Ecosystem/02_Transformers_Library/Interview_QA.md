# Transformers Library — Interview Q&A

## Beginner Level

**Q1: What is the Hugging Face `transformers` library? Why do developers use it instead of writing model code from scratch?**

<details>
<summary>💡 Show Answer</summary>

**A:** The `transformers` library is an open-source Python package that provides implementations of hundreds of transformer-based model architectures (BERT, GPT, T5, LLaMA, Whisper, ViT, and many more) with a unified API. Developers use it instead of writing from scratch for several reasons:

1. **Speed** — going from zero to a working BERT-powered sentiment classifier takes about 5 lines of code instead of hundreds
2. **Correctness** — tokenization must exactly match how the model was trained; the library bundles the right tokenizer with each model checkpoint
3. **Maintenance** — the library handles GPU placement, batching, and format conversions that would otherwise require boilerplate in every project
4. **Access to SOTA** — new models (LLaMA, Gemma, Mistral) are added quickly, so you can use the latest architectures without reimplementing them

</details>

---

**Q2: What is the `pipeline()` API and what does it abstract away?**

<details>
<summary>💡 Show Answer</summary>

**A:** `pipeline()` is the highest-level interface in `transformers`. A single call like `pipeline("sentiment-analysis")` creates an object that handles the entire inference workflow:

1. Downloads and loads the appropriate default model and tokenizer
2. Takes raw text as input (strings — no need to know about tokens)
3. Tokenizes the text internally (text → integer IDs)
4. Creates attention masks and handles padding
5. Runs the model forward pass
6. Post-processes the raw output (converts logits to labels with confidence scores)
7. Returns a human-readable result (e.g., `[{'label': 'POSITIVE', 'score': 0.9998}]`)

Without `pipeline()`, you would write all seven steps yourself.

</details>

---

**Q3: What is the difference between `AutoModel` and `AutoModelForSequenceClassification`?**

<details>
<summary>💡 Show Answer</summary>

**A:** Both load a model from the Hub, but they attach different **output heads** (the final layers that produce task-specific outputs):

- **`AutoModel`:** Returns the base model with no task-specific head. Output is raw **hidden states** (dense vectors of shape `[batch, sequence_length, hidden_dim]`). Use this when you want embeddings or when you'll add your own custom head on top.

- **`AutoModelForSequenceClassification`:** Adds a classification head (a linear layer) on top of the base model. Output is **logits** (shape `[batch, num_labels]`) which you apply softmax to get class probabilities. Use this for sentiment analysis, topic classification, etc.

Rule of thumb: if your task is in the class name (SequenceClassification, TokenClassification, QuestionAnswering), use the task-specific class.

</details>

---

## Intermediate Level

**Q4: Explain what a tokenizer does and why the tokenizer must match the model checkpoint.**

<details>
<summary>💡 Show Answer</summary>

**A:** A tokenizer converts raw text into the integer sequences a model expects. It does this through several steps:
1. **Normalization** — lowercasing, Unicode normalization, etc.
2. **Pre-tokenization** — split on whitespace/punctuation
3. **Subword tokenization** — further split words into subword pieces using a vocabulary (e.g., "running" → ["run", "##ing"] in BERT, or "running" → ["run", "ning"] in GPT with BPE)
4. **ID lookup** — map each piece to its integer ID in the vocabulary

The tokenizer **must** match the model because the model's embedding matrix was trained with a specific vocabulary. Token ID 7392 means "running" in one vocabulary and something completely different in another. If you use BERT's tokenizer with a GPT-2 model (or vice versa), the model will receive tokens it was never trained to interpret, producing meaningless outputs with no error message to warn you.

`AutoTokenizer.from_pretrained("same-checkpoint-as-model")` guarantees the match.

</details>

---

**Q5: What does `attention_mask` do and when does it matter?**

<details>
<summary>💡 Show Answer</summary>

**A:** The `attention_mask` is a binary tensor (1s and 0s) with the same shape as the input token IDs. It tells the transformer which positions are real tokens (1) and which are padding (0).

It matters critically in **batched inference**. When you process multiple texts at once, they must all be the same length — shorter texts get padded with a special `[PAD]` token. Without the attention mask, the model would attend to padding positions as if they were meaningful content, corrupting the representations.

Example:
```python
# Two texts of different lengths in a batch
texts = ["Hi", "Hello world, how are you?"]
inputs = tokenizer(texts, return_tensors="pt", padding=True)
# attention_mask might be:
# [[1, 1, 0, 0, 0, 0, 0],   ← "Hi" with 5 padding positions masked out
#  [1, 1, 1, 1, 1, 1, 1]]   ← full sentence, no masking
```

The tokenizer creates the attention mask automatically when you pass `padding=True`.

</details>

---

**Q6: What is `device_map="auto"` and when would you use it?**

<details>
<summary>💡 Show Answer</summary>

**A:** `device_map="auto"` is a parameter for `from_pretrained()` that automatically distributes a model's layers across all available hardware — multiple GPUs if present, or GPU + CPU if the model is too large for GPU memory alone.

Without `device_map="auto"`:
```python
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf")
# Tries to load entire 7B model onto one GPU → OOM error if VRAM < ~14GB
```

With `device_map="auto"`:
```python
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    device_map="auto",
    torch_dtype=torch.float16
)
# Automatically splits layers across 2x GPUs + CPU offload if needed
```

It uses the `accelerate` library under the hood to create a device map that fits the model in available memory. This is essential for running large models (7B+ parameters) on consumer hardware.

</details>

---

## Advanced Level

**Q7: You have a text classification model that was fine-tuned on customer support tickets. You now need to run inference on 100,000 new tickets. What are the key performance considerations when using `transformers` for this scale?**

<details>
<summary>💡 Show Answer</summary>

**A:** Key considerations at 100K inference scale:

1. **Batching:** Never process one ticket at a time. Batch your inputs — a batch size of 32-128 uses GPU parallelism and can be 50-100x faster than one at a time. Use `pipeline(..., batch_size=64)` or manually batch with `DataLoader`.

2. **Half precision:** Load with `torch_dtype=torch.float16` — reduces VRAM by 2x and increases throughput on modern GPUs with no meaningful accuracy loss for inference.

3. **`torch.no_grad()` and `model.eval()`:** Disables gradient tracking and dropout. Required for any inference code, reduces memory by ~30-40%.

4. **Dynamic padding per batch:** If you sort inputs by length and pad within each batch (not to global max length), you reduce wasted computation on padding tokens. The `DataCollatorWithPadding` class handles this.

5. **Truncation strategy:** Very long tickets may exceed model max length (512 for BERT). Decide on a strategy (truncate head, tail, or middle) appropriate to where the key information lives in your tickets.

6. **Quantization:** For even higher throughput, load with `load_in_8bit=True` (bitsandbytes) to reduce memory and increase throughput further.

7. **GPU utilization:** Use `nvidia-smi` to monitor GPU utilization — if it's below 80%, your batch size is too small or data loading is the bottleneck.

</details>

---

**Q8: Explain how `trust_remote_code=True` works and when it's a security risk.**

<details>
<summary>💡 Show Answer</summary>

**A:** Some models on the Hub define custom Python code (in `modeling_*.py` files in their repository) that isn't part of the standard `transformers` library — for example, novel attention mechanisms or custom tokenizers. When you call `from_pretrained(..., trust_remote_code=True)`, the library downloads and executes this custom code on your machine.

The security risk is significant: `trust_remote_code=True` is essentially saying "I trust this repository's author enough to run arbitrary Python code on my machine." A malicious repository could execute commands to:
- Exfiltrate files or credentials
- Install backdoors
- Corrupt your data

**Safe usage guidelines:**
- Only use `trust_remote_code=True` with repos from authors you trust (major companies, verified researchers)
- Pin to a specific commit hash — so you're not running code that was added after your review
- Audit the custom code files in the repo before running
- Never use it in automated pipelines that pull from arbitrary Hub repos

For well-known models from major providers (Mistral, Meta, Google), `trust_remote_code=True` is generally safe. For unknown repos, treat it with the same caution as running an arbitrary shell script.

</details>

---

**Q9: What is the difference between `pipeline("text-generation")` and `pipeline("text2text-generation")`? When would you use each?**

<details>
<summary>💡 Show Answer</summary>

**A:** They correspond to two fundamentally different model architectures:

**`"text-generation"` (causal/decoder-only models like GPT, LLaMA):**
- Takes a prompt and generates a continuation
- Model only sees previous tokens when generating each new token (causal masking)
- Output includes the original prompt + generated continuation
- Use for: open-ended generation, chatbots, code completion, creative writing

```python
gen = pipeline("text-generation", model="gpt2")
result = gen("Once upon a time", max_new_tokens=50)
# Output includes "Once upon a time" + 50 new tokens
```

**`"text2text-generation"` (encoder-decoder models like T5, BART):**
- Takes an input and generates a completely new output sequence
- Encoder reads the full input; decoder generates the output
- Output is only the generated sequence, not the input
- Use for: translation, summarization, question answering, instruction following

```python
t2t = pipeline("text2text-generation", model="google/flan-t5-base")
result = t2t("Translate English to French: The cat sat on the mat")
# Output is only "Le chat était assis sur le tapis"
```

The choice is determined by the task: if you're completing/continuing text, use causal generation. If you're transforming one piece of text into a different piece of text, use seq2seq.

</details>

---

## 📂 Navigation

**In this folder:**

| File | Description |
|------|-------------|
| [📄 Theory.md](./Theory.md) | Full library explanation with diagrams |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | Interview questions (you are here) |
| [📄 Code_Example.md](./Code_Example.md) | Working pipeline code |
| [📄 Pipeline_Guide.md](./Pipeline_Guide.md) | Complete guide to all pipeline types |

⬅️ **Prev:** [Hub and Model Cards](../01_Hub_and_Model_Cards/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Datasets Library](../03_Datasets_Library/Theory.md)
