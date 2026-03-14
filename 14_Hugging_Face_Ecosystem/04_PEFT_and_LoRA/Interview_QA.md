# PEFT and LoRA — Interview Q&A

## Beginner Level

**Q1: What problem does PEFT solve? Why can't we just fine-tune the whole model?**

**A:** Fine-tuning an entire large language model requires storing and updating every single parameter. For a 7B parameter model in 16-bit precision:

- Model weights: ~14 GB
- Gradients (same size as weights): ~14 GB
- AdamW optimizer states (2× weights for momentum and variance): ~28 GB
- Total: ~56 GB

Almost no one has a GPU (or even several GPUs) with 56 GB of VRAM sitting around. Even when hardware is available, training all parameters is very slow and expensive — hours to days on expensive A100s.

PEFT (Parameter-Efficient Fine-Tuning) solves this by freezing the base model entirely and adding small trainable modules. For LoRA with `r=8`, only 0.1–0.5% of parameters are actually updated. You still need the model in memory, but you eliminate the massive gradient and optimizer state overhead for the frozen 99.9% of parameters.

---

**Q2: Explain LoRA to someone who has never heard of it.**

**A:** Imagine you have a completed jigsaw puzzle representing a model's knowledge. Full fine-tuning means taking it apart completely and rebuilding it with new pieces — expensive and slow. LoRA instead sticks a small transparent overlay on top of the puzzle. The overlay has just enough detail to change what you see in specific areas, while the puzzle underneath stays completely intact.

Technically: LoRA identifies the weight matrices in the attention layers of a transformer (typically the query and value projections). Instead of modifying these large matrices directly, it adds two small matrices alongside each one — call them A and B. A projects the hidden state down to a small bottleneck dimension `r`, and B projects it back up. Only A and B are trained; the original weight matrix is completely frozen.

The output of a LoRA layer is: `original output + (B × A × input) × scaling`. At initialization, B is zero, so the model starts identical to the base model and gradually deviates only in the directions LoRA has learned.

---

**Q3: What is the rank `r` in LoRA and how do you choose it?**

**A:** The rank `r` controls the bottleneck dimension of the two LoRA matrices. If the original weight matrix is [4096 × 4096], LoRA adds matrices of shape [4096 × r] and [r × 4096].

- **Low r (4–8):** Very few parameters. Good for simple task adaptation like instruction following on a narrow domain. Use when VRAM is very limited.
- **Medium r (16–32):** Standard choice for most fine-tuning tasks. Balances capacity and efficiency.
- **High r (64–128):** More capacity, approaching full fine-tuning quality. Used for complex tasks like code generation or when the adaptation required is large.

The rule of thumb: start with `r=8` and increase if the model isn't learning well enough. For most instruction-following and chat-format fine-tuning, `r=8` or `r=16` is sufficient.

---

## Intermediate Level

**Q4: What is QLoRA and how does it differ from regular LoRA?**

**A:** QLoRA (Quantized LoRA) extends LoRA by also quantizing the frozen base model to 4-bit precision. Regular LoRA keeps the base model in 16-bit (FP16 or BF16), which still requires ~14 GB for a 7B model. QLoRA compresses the base model to 4-bit using a format called NF4 (Normal Float 4), which was specifically designed for the normally distributed weight values in neural networks.

The result:
- Regular LoRA on 7B model: ~14 GB base + ~1 GB gradients/optimizer states = ~15 GB
- QLoRA on 7B model: ~4 GB base (4-bit) + ~1 GB LoRA states = ~5-6 GB

This means QLoRA can fine-tune a 7B LLM on a consumer GPU with just 8-10 GB of VRAM — something that was impossible before.

The technical trick: during the forward pass, the quantized 4-bit weights are temporarily dequantized to BF16 for computation. The gradient flows only through the LoRA matrices (which are in BF16), not through the frozen quantized weights. This avoids the numerical instability of computing gradients through 4-bit values.

---

**Q5: What are `target_modules` in LoRA and how do you choose which layers to target?**

**A:** `target_modules` specifies which weight matrix names in the model receive LoRA adapters. The names vary by model family:

**LLaMA / Mistral style:**
```python
target_modules=["q_proj", "k_proj", "v_proj", "o_proj",    # Attention
                 "gate_proj", "up_proj", "down_proj"]         # FFN
```

**GPT-2 style:**
```python
target_modules=["c_attn", "c_proj"]
```

**OPT / BLOOM style:**
```python
target_modules=["q_proj", "v_proj"]
```

**How to choose:**
- **Minimum (most efficient):** Target only `q_proj` and `v_proj` — the query and value projections in attention. This is the original LoRA paper recommendation.
- **Standard:** Add `k_proj` and `o_proj` for all attention projections.
- **Maximum (best quality):** Also target the feedforward layers (gate_proj, up_proj, down_proj in LLaMA). More parameters but better adaptation.

To find the exact layer names for any model, run:
```python
for name, module in model.named_modules():
    if isinstance(module, torch.nn.Linear):
        print(name)
```

---

**Q6: How do you save, share, and reload a LoRA adapter?**

**A:** LoRA adapters are stored separately from the base model. This is a major advantage — the adapter file is typically 10-100 MB, not 14 GB.

**Saving:**
```python
# After training
lora_model.save_pretrained("./my-lora-adapter")
# Creates adapter_config.json + adapter_model.safetensors
```

**Pushing to Hub (only the adapter — not the full model):**
```python
lora_model.push_to_hub("your-username/my-lora-adapter")
```

**Loading and using:**
```python
from peft import PeftModel
from transformers import AutoModelForCausalLM

# Load base model first
base = AutoModelForCausalLM.from_pretrained("facebook/opt-350m")

# Load adapter on top
model = PeftModel.from_pretrained(base, "your-username/my-lora-adapter")

# For deployment: merge to eliminate inference overhead
merged = model.merge_and_unload()
```

The `adapter_config.json` file records which base model the adapter was trained on, so users know exactly what model to pair it with.

---

## Advanced Level

**Q7: Explain the mathematical insight behind why low-rank matrices are a good approximation for fine-tuning updates.**

**A:** The key insight comes from research on weight matrices in over-parameterized neural networks: the updates (ΔW) that occur during fine-tuning tend to have low **intrinsic rank**. That is, even though the matrices are high-dimensional, the meaningful changes during adaptation can be captured by matrices with much lower rank.

Formally, any matrix ΔW of shape [d × k] can be decomposed as B × A where B is [d × r] and A is [r × k], as long as rank(ΔW) ≤ r. If the "effective" rank of the fine-tuning update is actually small (empirically observed to be in the range of 1–64 even for large models), then a rank-8 or rank-16 decomposition can approximate it with minimal loss of quality.

This is consistent with broader findings in ML: the loss landscape for fine-tuning is lower-dimensional than the total parameter space suggests. Pre-trained models already capture most generalizable knowledge; fine-tuning only needs to steer the model slightly toward a new task, not restructure its core representations.

The practical implication: if the ΔW for your task requires higher rank than you've set, your LoRA adaptation will underfit — you'll see the training loss plateau before reaching competitive performance. The fix is to increase `r`.

---

**Q8: A team deployed a QLoRA fine-tuned model but found that performance was noticeably worse than their validation metrics suggested. What might have gone wrong?**

**A:** Several QLoRA-specific issues can create a gap between validation metrics and deployed performance:

1. **Quantization format mismatch:** If training used 4-bit NF4 quantization but deployment loads the merged model in full FP16, the merge operation should be fine. But if the merged weights were saved incorrectly (e.g., saving the 4-bit base + unmerged adapter), the deployed model is different from what was evaluated.

2. **Not merging before deployment:** If `merge_and_unload()` was not called, the model at inference time has the PEFT wrapper adding LoRA on top. This is correct but adds overhead and, if the wrapper is configured differently (e.g., different `lora_alpha`), gives different results.

3. **Double quantization effects:** Validation was run with quantized weights (NF4) but deployment used the dequantized merged float model, or vice versa. The small numerical differences from quantization can cause meaningful output distribution shifts.

4. **Evaluation data leakage:** Validation set was accidentally part of the fine-tuning data, so validation metrics were inflated relative to true generalization.

5. **Temperature/sampling parameters:** Training used greedy decoding for evaluation but production uses sampling, or vice versa. Different decoding strategies produce very different outputs even with the same model.

**Recommended debugging process:** Run inference on the same 50 examples using both the checkpoint used for validation and the deployed model. If outputs differ, the deployment path has a model mismatch. If outputs match, the issue is either data distribution shift or evaluation methodology.

---

**Q9: Compare LoRA, prefix tuning, and prompt tuning. When is each method preferable?**

**A:**

**LoRA (Low-Rank Adaptation):**
- **Mechanism:** Adds trainable matrices alongside attention weight matrices
- **Parameters:** 0.1–1% of total parameters
- **Quality:** Closest to full fine-tuning among PEFT methods
- **Use when:** You need high adaptation quality with limited resources; you want to share adapters separately; almost all practical fine-tuning scenarios

**Prefix Tuning:**
- **Mechanism:** Prepends trainable "virtual tokens" to the key and value matrices at every layer. These are continuous embeddings, not discrete tokens.
- **Parameters:** ~0.1% of total; depends on prefix length
- **Quality:** Good for generation tasks, slightly below LoRA for classification
- **Use when:** You're doing language generation tasks (summarization, dialogue) and want a clean separation between task conditioning and model weights

**Prompt Tuning (soft prompts):**
- **Mechanism:** Learns a small set of trainable embedding vectors prepended to the input sequence at the embedding layer only
- **Parameters:** Very few — often just 100–1000 vectors
- **Quality:** Weakest among the three; works well for very large models (>10B) where the base model is already very capable
- **Use when:** You need an extremely lightweight adapter; the model is very large and powerful; you want to switch between many tasks by swapping a small prompt

**Summary:** For almost all practical applications in 2024-2025, **LoRA** (or **QLoRA** on limited hardware) is the default choice. Prefix tuning and prompt tuning have niche applications but LoRA offers better quality-to-cost tradeoff for the vast majority of tasks.

---

## 📂 Navigation

**In this folder:**

| File | Description |
|------|-------------|
| [📄 Theory.md](./Theory.md) | Full PEFT and LoRA explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | Interview questions (you are here) |
| [📄 Code_Example.md](./Code_Example.md) | LoRA fine-tuning with PEFT library |
| [📄 When_to_Use.md](./When_to_Use.md) | Decision guide for fine-tuning approaches |

⬅️ **Prev:** [Datasets Library](../03_Datasets_Library/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Trainer API](../05_Trainer_API/Theory.md)
