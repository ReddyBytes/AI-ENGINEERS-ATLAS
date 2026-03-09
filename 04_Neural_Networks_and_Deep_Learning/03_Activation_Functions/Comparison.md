# Activation Functions — Comparison

## Full Comparison Table

| Function | Formula | Output Range | Gradient (Active) | Vanishing Gradient? | Dying Neuron? | Zero-Centered? | Typical Use Case |
|----------|---------|-------------|-------------------|---------------------|---------------|----------------|-----------------|
| Step | 1 if x≥0 else 0 | {0, 1} | 0 everywhere | N/A (not trainable) | N/A | No | Historical perceptrons only |
| Sigmoid | 1 / (1 + e^−x) | (0, 1) | Max 0.25 | Yes (severe) | No | No | Binary output layer |
| Tanh | (e^x − e^−x) / (e^x + e^−x) | (−1, 1) | Max 1.0 | Yes (moderate) | No | Yes | RNN hidden states |
| ReLU | max(0, x) | [0, ∞) | 1 for x>0, 0 for x<0 | No (active side) | Yes | No | Default hidden layers |
| LeakyReLU | max(0.01x, x) | (−∞, ∞) | 1 for x>0, 0.01 for x<0 | No | No | Hidden layers (if dying ReLU occurs) |
| ELU | x if x>0, α(e^x − 1) if x≤0 | (−α, ∞) | 1 for x>0, smooth for x<0 | No | No | Yes (approximately) | Deep hidden layers |
| GELU | x × Φ(x) | (−∞, ∞) | Smooth everywhere | No | No | Yes (approximately) | Transformers, BERT, GPT |
| Softmax | e^xi / Σe^xj | (0, 1) per class, sum=1 | Depends | No | No | No | Multi-class output layer only |
| Swish | x × sigmoid(x) | (−∞, ∞) | Smooth everywhere | No | No | Approximately | EfficientNet, deep CNNs |

---

## Gradient Behavior Visualization

```
Step:     flat — flat — JUMP — flat     ← no gradient, untrainable
Sigmoid:  0 ────── 0.25 ────── 0        ← squashes to near 0 at extremes
Tanh:     0 ──────  1   ────── 0        ← better than sigmoid but still saturates
ReLU:     0 | 1 ─────────────────       ← perfect gradient for positives, zero for negatives
LeakyReLU: 0.01 | 1 ──────────────     ← small gradient even for negatives
```

---

## Decision Guide

```
Starting a new hidden layer in a standard network?
  → ReLU (first choice always)

Seeing dead neurons (outputs always 0)?
  → Switch to LeakyReLU or ELU

Building a transformer or attention-based model?
  → GELU (or Swish)

Building an RNN / LSTM / GRU hidden state?
  → Tanh (standard for sequence models)

Output layer, binary classification (yes/no)?
  → Sigmoid

Output layer, multi-class (cat/dog/bird)?
  → Softmax

Output layer, regression (predict a number)?
  → No activation (linear output)
```

---

## Pros and Cons Summary

| Function | Pros | Cons |
|----------|------|------|
| Sigmoid | Outputs interpretable probabilities | Vanishing gradients, not zero-centered, slow |
| Tanh | Zero-centered, better than sigmoid | Still saturates at extremes |
| ReLU | Fast, simple, works great in practice | Dying neurons, not zero-centered |
| LeakyReLU | Fixes dying ReLU | Extra hyperparameter (slope), minor complexity |
| ELU | Zero-centered, smooth, no dying neurons | Slower to compute, requires α tuning |
| GELU | Smooth, best empirical performance | More expensive to compute |
| Softmax | Valid probability distribution | Overconfident, not calibrated automatically |

---

## Historical Notes

- **1943:** Step function used in the first neural model (McCulloch & Pitts)
- **1986:** Sigmoid became standard with backpropagation (Rumelhart et al.)
- **1990s:** Tanh replaced sigmoid in hidden layers due to zero-centering
- **2010:** ReLU shown to dramatically speed up deep network training (Nair & Hinton)
- **2015–2018:** LeakyReLU, ELU, PReLU variants address dying neuron problem
- **2018:** GELU published and adopted in BERT, becoming the transformer standard
- **2019:** Swish (x × sigmoid(x)) adopted in EfficientNet

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Comparison.md** | ← you are here |

⬅️ **Prev:** [02 MLPs](../02_MLPs/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 Loss Functions](../04_Loss_Functions/Theory.md)
