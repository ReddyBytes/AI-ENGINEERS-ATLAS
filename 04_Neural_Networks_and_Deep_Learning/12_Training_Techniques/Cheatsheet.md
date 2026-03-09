# Training Techniques — Cheatsheet

**One-liner:** Training techniques are the practical choices — batch size, learning rate schedule, initialization, transfer learning — that determine whether a neural network converges quickly, accurately, and generalizably.

---

## Key Terms

| Term | What it means |
|------|---------------|
| Epoch | One complete pass through the full training dataset |
| Batch size | Number of samples processed per weight update |
| Mini-batch | A small subset of data for each update (standard practice) |
| Learning rate schedule | Planned changes to lr during training |
| Weight initialization | How weights are set before training begins |
| Transfer learning | Using a model pretrained on one task as a starting point for another |
| Fine-tuning | Unfreezing pretrained weights and training them on new data |
| Feature extraction | Keeping pretrained weights frozen, only training the new head |
| Mixed precision | Using float16 for computation, float32 for storage |
| Gradient checkpointing | Trading compute for memory — recompute activations instead of storing them |
| Curriculum learning | Training on easy examples first, progressively harder ones later |

---

## Batch Size Guide

| Batch size | Gradient quality | Speed | Generalization |
|-----------|-----------------|-------|----------------|
| 8–32 | Noisy (rough) | Slow per epoch | Often better |
| 64–256 | Good balance | Fast | Standard |
| 512–4096 | Very accurate | Very fast on GPU | Risk of sharp minima |
| > 4096 | Extremely accurate | Maximizes GPU use | May need LR warmup |

Rule of thumb: If you 2× the batch size, 2× the learning rate.

---

## Learning Rate Schedule Comparison

| Schedule | When LR changes | Best for |
|----------|----------------|----------|
| Constant | Never | Quick experiments only |
| Step decay | At specific epochs | Classic CNNs |
| Cosine annealing | Smoothly throughout training | Vision, modern default |
| Warmup + decay | Up then down | Transformers |
| ReduceLROnPlateau | When val loss stagnates | General purpose |
| Cyclic LR | Oscillates between bounds | Fast convergence exploration |

---

## Weight Initialization Rules

| Activation | Initialization | Formula |
|------------|---------------|---------|
| ReLU | He | w ~ N(0, sqrt(2/n_in)) |
| Sigmoid / Tanh | Xavier | w ~ N(0, sqrt(1/n_in)) |
| Any | Random small | Avoid — causes vanishing/exploding from step 1 |
| Any | All zeros | Never — symmetry breaking required |

---

## Transfer Learning Decision Tree

```
Do you have labeled data for your task?
  → <1K samples:  Feature extraction only (freeze pretrained, train head)
  → 1K–10K:      Fine-tune last few layers + new head
  → >100K:       Fine-tune whole model, or train from scratch
  → Millions:    Train from scratch (may still benefit from pretrained init)
```

---

## When to Use / Not Use

| Technique | Use when... | Skip when... |
|-----------|-------------|-------------|
| Transfer learning | Limited data, similar domain | Huge dataset, very different domain |
| Mixed precision | Large model, modern GPU | Old hardware, tiny model |
| LR warmup | Transformer, large model | Small CNN, short training |
| Batch norm | Most architectures | RNNs (use Layer Norm instead) |
| Gradient clipping | RNNs, large LMs | Standard CNNs/MLPs |

---

## Golden Rules

1. Learning rate is the most impactful hyperparameter. Tune it first, always.
2. Transfer learning beats training from scratch for any task with < 100K examples.
3. Mixed precision is essentially free speedup on modern GPUs — always use it.
4. Monitor both train and validation loss every epoch. Act on divergence immediately.
5. Save checkpoints regularly — you cannot go back without them.
6. Normalize your inputs. Neural networks are extremely sensitive to input scale.
7. Start simple. Add complexity only when simple fails (underfits).

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Troubleshooting_Guide.md](./Troubleshooting_Guide.md) | Training troubleshooting guide |

⬅️ **Prev:** [11 GANs](../11_GANs/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [01 Text Preprocessing](../../05_NLP_Foundations/01_Text_Preprocessing/Theory.md)
