# Fine-Tuning — Interview Q&A

## Beginner

**Q1: What is fine-tuning and why do we do it?**

<details>
<summary>💡 Show Answer</summary>

Fine-tuning is the process of taking a pretrained model and continuing to train it on a smaller, task-specific dataset. The pretrained model already has broad knowledge of language, facts, and reasoning from seeing trillions of tokens. Fine-tuning steers that broad knowledge toward a specific use case.

We do it for several reasons:

1. **Specialization**: A medical chatbot should answer like a doctor, not a general assistant. Fine-tuning on medical Q&A pairs achieves this.
2. **Format consistency**: If your application needs JSON output or always follows a specific template, fine-tuning on examples trains that behavior more reliably than prompting.
3. **Efficiency**: Once fine-tuned, you don't need long system prompts with many examples. The behavior is baked into the weights. Shorter prompts = faster, cheaper inference.
4. **Private domain knowledge**: Your proprietary data can't go into API prompts if it's sensitive. Fine-tuning keeps it in-house.

The metaphor: pretraining is med school (broad). Fine-tuning is residency (specialized).

</details>

---

**Q2: What is LoRA? Why is it preferred over full fine-tuning?**

<details>
<summary>💡 Show Answer</summary>

LoRA (Low-Rank Adaptation) is a parameter-efficient fine-tuning technique. Instead of updating all the weights in a model (which could be 70 billion parameters), LoRA adds small trainable matrices alongside the frozen original weights.

How it works: For each weight matrix W in the model, LoRA trains two small matrices A and B such that the effective update is A × B. Since A and B are small (e.g., 4096×16 and 16×4096 instead of 4096×4096), the number of trainable parameters drops by ~99%.

Why it's preferred:
- **Cost**: Fine-tune a 7B model on a single consumer GPU (24GB) vs 8× A100s for full fine-tuning
- **Speed**: Fewer parameters to update = faster training
- **Quality**: Surprisingly close to full fine-tuning for most tasks
- **Composability**: Multiple LoRA adapters can be hot-swapped on the same base model

The key insight: most of the important adaptation is low-rank — you don't need to change all of W, just a small subspace of it.

</details>

---

**Q3: What kind of data do you need for fine-tuning?**

<details>
<summary>💡 Show Answer</summary>

You need (input, output) pairs that demonstrate the behavior you want. The format depends on the task:

**For instruction following (most common):**
```
{"instruction": "Summarize this article",
 "input": "<article text>",
 "output": "The article discusses..."}
```

**For chat fine-tuning:**
```
[{"role": "user", "content": "What is RLHF?"},
 {"role": "assistant", "content": "RLHF stands for..."}]
```

**For domain adaptation:**
Raw domain text (medical papers, legal documents) — same format as pretraining.

How much data you need depends on the task. Format changes: 100–500 examples. Domain Q&A: 1,000–10,000. Full chat fine-tune: 50,000+. Data quality matters enormously — 1,000 excellent examples from domain experts regularly beats 50,000 low-quality examples.

</details>

---

## Intermediate

**Q4: What is catastrophic forgetting? How do you prevent it during fine-tuning?**

<details>
<summary>💡 Show Answer</summary>

Catastrophic forgetting is when fine-tuning on new data degrades the model's performance on its original capabilities. The gradient updates from your new data overwrite weight configurations that encoded previously learned behavior.

Example: You fine-tune Llama 3 on medical data. After fine-tuning, the model is better at medical Q&A but has degraded at coding, math, and general knowledge. That's catastrophic forgetting.

How to prevent it:

1. **Data mixing**: Include a sample of general-purpose instruction data (from the original fine-tuning set) alongside your domain data. Typical ratio: 10–30% general, 70–90% domain.

2. **Low learning rate**: Use a very small learning rate (1e-5 or lower for full fine-tuning) so each gradient step is small and doesn't overwrite aggressively.

3. **LoRA**: Because LoRA keeps the base model frozen and only trains small adapter matrices, catastrophic forgetting is structurally prevented for LoRA runs. The base knowledge is in the frozen weights — untouched.

4. **Fewer training epochs**: Don't over-train. 1–3 epochs of fine-tuning is usually enough. More epochs means more overwriting.

5. **Regularization**: L2 regularization around the pretrained weights (Elastic Weight Consolidation).

For most practical cases: use LoRA (solves it structurally) and mix 20% general data with your domain data.

</details>

---

**Q5: How do you evaluate if fine-tuning worked? What metrics do you use?**

<details>
<summary>💡 Show Answer</summary>

Evaluation for fine-tuning depends on the task. There's no single universal metric — you need task-specific evaluation.

**Automated metrics:**
- **Accuracy / F1**: For classification tasks (e.g., sentiment, intent detection)
- **BLEU / ROUGE**: For summarization, translation. Measures n-gram overlap with reference outputs. Imperfect but fast.
- **Code execution rate**: For code generation — does the generated code run without errors?
- **Perplexity on held-out domain data**: Does the model predict domain text better?
- **Benchmark evals**: MMLU for knowledge, GSM8k for math, HumanEval for code — run before and after to check for regressions

**Human evaluation:**
- **Preference rating**: Show human raters outputs from base model vs fine-tuned model, blind. Ask which is better.
- **Rubric scoring**: Rate on dimensions like accuracy, helpfulness, tone, format.
- **Red-teaming**: Deliberately try to get the fine-tuned model to fail or exhibit problematic behavior.

**Practical checklist:**
1. Establish a baseline before fine-tuning
2. Create a held-out test set (not used in training)
3. Evaluate on your target task metrics
4. Evaluate on general benchmarks for regression
5. Do human review on a sample of outputs
6. Compare cost/latency vs the base model + prompt approach

</details>

---

**Q6: What is QLoRA? How does it differ from LoRA?**

<details>
<summary>💡 Show Answer</summary>

QLoRA (Quantized LoRA) combines two techniques: LoRA adapters + 4-bit quantization of the base model.

**Standard LoRA:**
- Base model weights: stored in float16 (2 bytes per param) or bfloat16
- LoRA adapter weights: float16
- 7B model memory: ~14GB for base + adapter training overhead ≈ ~20–28GB total

**QLoRA:**
- Base model weights: stored in NF4 (4-bit NormalFloat) — 0.5 bytes per param
- LoRA adapter weights: bfloat16 (standard precision, small)
- Gradient checkpointing + paged optimizer for memory efficiency
- 7B model memory: ~4GB for quantized base + adapters ≈ ~6–10GB total

This means:
- 7B model: fine-tunable on a 12GB GPU (consumer RTX 3090/4090)
- 13B model: fine-tunable on a 24GB GPU
- 65B model: fine-tunable on a single A100 80GB

The trade-off: quantization introduces some accuracy loss in the base model representations. Fine-tuning quality is usually very close to standard LoRA but occasionally slightly below full LoRA. For most practical applications the difference is negligible.

QLoRA is the standard approach for open-source community fine-tuning. Almost all the Alpaca, Vicuna, WizardLM family models were trained using QLoRA.

</details>

---

## Advanced

**Q7: How does LoRA's low-rank assumption work mathematically? When does it fail?**

<details>
<summary>💡 Show Answer</summary>

The key insight behind LoRA is that the weight updates during fine-tuning tend to have low intrinsic rank. This was shown empirically by Aghajanyan et al. (2020) who measured the "intrinsic dimensionality" of fine-tuning across tasks and found it's surprisingly small — often 100–1000 dimensions even for models with millions of parameters.

**Mathematical basis:**

For a weight matrix W ∈ ℝᵐˣⁿ, the full update ΔW also lives in ℝᵐˣⁿ. LoRA approximates:

```
ΔW ≈ AB,  where A ∈ ℝᵐˣʳ,  B ∈ ℝʳˣⁿ,  r << min(m, n)
```

A is initialized with random Gaussian values. B is initialized to zero. This means at the start of training, the LoRA perturbation is zero — we begin from the exact pretrained weights.

During training, gradient updates to A and B implicitly define a rank-r update to W.

**When it fails:**

1. **Tasks requiring large weight updates**: If the target task is very different from pretraining (e.g., training on a new language the base model has barely seen), a low-rank update may not have enough capacity. Solution: increase r.

2. **Very high-quality requirements**: For frontier model tasks where you need absolute maximum performance, full fine-tuning can still be 1–3% better than LoRA.

3. **All layers need adaptation**: LoRA is typically applied only to attention projection matrices (q, k, v, o). If the MLP layers also need significant adaptation, applying LoRA only to attention may be insufficient. Solution: apply LoRA to all linear layers.

4. **Long training**: LoRA adapters trained for many epochs on large datasets can still cause catastrophic forgetting through the adapter parameters — the freeze only protects the original weights, not the overall behavior.

**Choosing rank r in practice**: Start with r=16. If quality is insufficient, try r=32 or r=64. Higher r = more expressive but more parameters and slightly more compute. Most practitioners find r=8 to r=32 covers the vast majority of tasks.

</details>

---

**Q8: What are the differences between SFT, instruction tuning, and domain adaptation? When do you use each?**

<details>
<summary>💡 Show Answer</summary>

These three terms overlap but refer to different emphases:

**Supervised Fine-Tuning (SFT)**
The general technique: train on (input, output) pairs with supervised cross-entropy loss. All three methods below are types of SFT.

**Instruction Tuning**
- Goal: teach the model to follow natural language instructions
- Data format: (instruction, [optional input], output) triples
- Focus: task generalization — model should follow any instruction, not just the ones in training
- Key dataset: FLAN (60+ tasks as instructions), Alpaca (52k GPT-4-generated instructions), ShareGPT (real user conversations)
- Result: a base model → instruction-following model
- Use when: you want a general assistant model that follows commands

**Domain Adaptation (Continued Pretraining)**
- Goal: improve model familiarity and fluency in a specific domain
- Data format: raw domain text (same as pretraining, not instruction format)
- Focus: absorbing domain vocabulary, facts, and writing style
- Examples: fine-tune on medical papers to improve medical knowledge; fine-tune on legal contracts for legal assistant
- Result: model becomes more fluent and accurate in domain, but not necessarily better at following instructions
- Use when: your domain has specialized vocabulary, concepts, or reasoning patterns not well-covered in base model

**Domain Instruction Tuning (Combined)**
- Goal: domain-specialized assistant
- Two-stage: first domain adaptation (raw domain text), then instruction tuning (domain Q&A pairs)
- Best of both: model knows the domain deeply and follows instructions helpfully
- Example: BioMedLM, MedPaLM, LexAI

**Practical decision:**
- Need general instruction following? → Instruction tuning
- Need to improve domain knowledge? → Domain adaptation
- Need a domain expert assistant? → Both, in sequence

</details>

---

**Q9: How does the HuggingFace PEFT + Trainer ecosystem work? What are the key components?**

<details>
<summary>💡 Show Answer</summary>

HuggingFace provides a full stack for fine-tuning open-weight models:

**`transformers` library:**
- `AutoModelForCausalLM.from_pretrained()`: Load base model
- `AutoTokenizer.from_pretrained()`: Load tokenizer
- `TrainingArguments`: Configure epochs, batch size, learning rate, output dir
- `Trainer`: Orchestrates the training loop, handles distributed training, logging, checkpointing

**`peft` library (Parameter-Efficient Fine-Tuning):**
- `LoraConfig`: Define r, alpha, target_modules, dropout
- `get_peft_model()`: Wraps base model with LoRA adapters, freezes everything else
- Handles merge_and_unload() to merge adapters into base model post-training

**`bitsandbytes` library:**
- Provides 4-bit (NF4) and 8-bit quantization for QLoRA
- `BitsAndBytesConfig`: Configure quantization type, compute dtype

**`datasets` library:**
- `load_dataset()`: Load from HuggingFace Hub or local JSON/CSV
- `map()`: Apply tokenization, formatting transforms in parallel
- `DataCollatorForSeq2Seq` / `DataCollatorWithPadding`: Batch and pad sequences

**Typical training loop (see Code_Example.md for full code):**
```python
# 1. Load model in 4-bit (for QLoRA)
model = AutoModelForCausalLM.from_pretrained(model_id, quantization_config=bnb_config)

# 2. Add LoRA adapters
model = get_peft_model(model, lora_config)

# 3. Load and format dataset
dataset = load_dataset("json", data_files="train.jsonl")
dataset = dataset.map(format_instruction)  # apply prompt template

# 4. Train
trainer = Trainer(model=model, args=training_args, train_dataset=dataset)
trainer.train()

# 5. Save
model.save_pretrained("./my-fine-tuned-model")
```

**Key things to know for interviews:**
- PEFT wraps the base model, frozen base model weights are not saved separately
- Adapter weights are tiny (~10–50MB for a 7B model with r=16) — only these need to be saved and shared
- `merge_and_unload()` combines adapters into base weights for faster inference (no extra forward pass overhead)
- For distributed training, `accelerate` library handles multi-GPU coordination
- Weights & Biases or TensorBoard integration built into Trainer for experiment tracking

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |
| [📄 When_to_Use.md](./When_to_Use.md) | When to fine-tune vs other approaches |

⬅️ **Prev:** [03 Pretraining](../03_Pretraining/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 Instruction Tuning](../05_Instruction_Tuning/Theory.md)
