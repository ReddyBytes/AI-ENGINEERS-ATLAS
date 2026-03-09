# Optimizers — Comparison

## Core Comparison Table

| Optimizer | Core Idea | Adapts LR per param? | Uses Momentum? | Pros | Cons | Best For |
|-----------|-----------|---------------------|----------------|------|------|----------|
| SGD | Basic gradient step | No | No | Simple, predictable | Slow, sensitive to lr | Convex problems, baselines |
| SGD + Momentum | Accumulate velocity | No | Yes | Faster, escapes shallow minima | Still needs tuned lr | Vision SOTA with schedule |
| Nesterov SGD | Look-ahead momentum | No | Yes (corrected) | Slightly better convergence | Slightly more complex | Vision tasks, minor improvement |
| Adagrad | Divide by historical gradient sum | Yes | No | Good for sparse gradients | lr shrinks to 0 eventually | NLP with sparse features |
| RMSProp | Divide by exponential gradient avg | Yes | No | Fixes Adagrad's decay issue | No momentum | RNNs, LSTMs |
| Adam | Momentum + RMSProp | Yes | Yes | Fast, robust default | Can generalize less than SGD | NLP, quick experiments |
| AdamW | Adam + decoupled weight decay | Yes | Yes | Better regularization than Adam | — | Transformers, large models |
| Adadelta | No manual lr, adaptive | Yes | No | No lr to tune | Less popular, complex | Older NLP |
| Nadam | Adam + Nesterov momentum | Yes | Yes (Nesterov) | Slight improvement over Adam | Rarely significant | Fine-tuning |
| LAMB | Adam scaled for large batches | Yes | Yes | Enables huge batch training | Complex | BERT pre-training |

---

## Convergence Speed vs Generalization Tradeoff

```
Convergence Speed (fast → slow):
Adam > RMSProp > SGD+Momentum > SGD

Generalization on Vision (best → worst, roughly):
SGD+Momentum > Adam > RMSProp > SGD

Generalization on NLP/Transformers (best → worst):
AdamW > Adam > SGD+Momentum
```

This tradeoff is well documented: adaptive optimizers (Adam) converge faster but sometimes generalize worse on structured tasks like image classification. For NLP, Adam/AdamW consistently outperforms SGD.

---

## Learning Rate Schedules

| Schedule | Behavior | Formula | Use Case |
|----------|----------|---------|----------|
| Constant | lr never changes | lr = const | Small experiments only |
| Step Decay | Drop lr by factor at epochs | lr = lr × 0.1 every 30 epochs | Classic CNNs |
| Exponential Decay | Smooth continuous decrease | lr = lr₀ × e^(-kt) | General purpose |
| Cosine Annealing | Follows cosine curve | lr = lr_min + 0.5(lr_max - lr_min)(1 + cos(πt/T)) | Vision, modern default |
| Warm-up + Decay | Small → peak → decay | Linear up, then cosine/linear down | Transformers |
| Cyclic LR | Oscillates between bounds | Repeating triangles | Fast training, exploration |
| ReduceLROnPlateau | Reduce when loss stagnates | Monitor val loss, reduce if no improvement | General purpose, safe |

---

## When to Choose Which Optimizer

```
Starting a new project?
  → Adam (lr=0.001)

Training a transformer (BERT, GPT)?
  → AdamW (lr=1e-4 to 3e-4, with warmup)

Want the best vision accuracy (ImageNet, CIFAR)?
  → SGD + Momentum (lr=0.1, cosine schedule, momentum=0.9)

Training an RNN/LSTM?
  → RMSProp or Adam

Very large batch training (batch > 4096)?
  → LAMB or Adam with linear scaling rule

Loss not converging with Adam?
  → Try AdamW, or switch to SGD and tune lr
```

---

## PyTorch Code Reference

```python
import torch.optim as optim

# SGD
optimizer = optim.SGD(model.parameters(), lr=0.01)

# SGD + Momentum
optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.9)

# Adam
optimizer = optim.Adam(model.parameters(), lr=0.001)

# AdamW
optimizer = optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.01)

# RMSProp
optimizer = optim.RMSprop(model.parameters(), lr=0.001)

# Learning rate scheduler (cosine)
scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=100)

# In training loop:
optimizer.zero_grad()
loss.backward()
optimizer.step()
scheduler.step()  # after each epoch
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Comparison.md** | ← you are here |

⬅️ **Prev:** [06 Backpropagation](../06_Backpropagation/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [08 Regularization](../08_Regularization/Theory.md)
