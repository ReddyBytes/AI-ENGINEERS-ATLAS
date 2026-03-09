# Loss Functions — Comparison

## Full Comparison Table

| Loss Function | Task Type | Formula (simplified) | Output Activation | Pros | Cons |
|--------------|-----------|----------------------|-------------------|------|------|
| MSE | Regression | mean((ŷ - y)²) | Linear (none) | Smooth gradient, penalizes large errors heavily | Sensitive to outliers, not for classification |
| MAE | Regression | mean(\|ŷ - y\|) | Linear (none) | Robust to outliers | Constant gradient, can oscillate near minimum |
| Huber Loss | Regression | MSE when small, MAE when large | Linear (none) | Best of MSE and MAE — smooth + robust | One extra hyperparameter (delta) |
| Binary Cross-Entropy | Binary classification | -[y·log(p) + (1-y)·log(1-p)] | Sigmoid | Strongly penalizes confident wrong answers | Only for 2 classes |
| Categorical Cross-Entropy | Multi-class classification | -Σ y_i · log(p_i) | Softmax | Standard for multi-class | All classes assumed mutually exclusive |
| Sparse Categorical Cross-Entropy | Multi-class (integer labels) | Same as CE, but takes integer y directly | Softmax | Convenient — no one-hot encoding needed | Same limitations as CE |
| Binary CE (per output) | Multi-label classification | BCE applied to each output independently | Sigmoid per output | Handles multiple correct labels | Each output treated independently |
| Focal Loss | Imbalanced classification | -(1-p)^γ · y · log(p) | Sigmoid/Softmax | Down-weights easy examples, focuses on hard ones | Extra hyperparameter γ |
| KL Divergence | Probability distributions | Σ p · log(p/q) | Softmax | Measures distribution distance | Not symmetric, not a true distance |
| Contrastive Loss | Metric learning / Siamese nets | Complex | Embedding | Learns similarity metric | Requires pairs of examples |
| Triplet Loss | Metric learning | Anchor-Positive-Negative triplets | Embedding | Learns rich similarity space | Hard to mine good triplets |

---

## Decision Guide

```
Is your output a number?
  → Regression
    → Outliers in data? → Huber or MAE
    → Clean data?       → MSE

Is your output a category?
  → Classification
    → Two classes (yes/no)? → Binary Cross-Entropy
    → Multiple classes, one correct? → Categorical Cross-Entropy
    → Multiple correct labels (tags)? → Binary CE per output

Special cases:
    → Very imbalanced classes? → Focal Loss or Weighted CE
    → Learning similarity/distance? → Contrastive or Triplet Loss
    → Comparing probability distributions? → KL Divergence
```

---

## How Error Magnitude Affects Each Loss

| Error size | MSE penalty | MAE penalty | Cross-Entropy (wrong at 0.9 confidence) |
|-----------|-------------|-------------|----------------------------------------|
| 1 | 1 | 1 | — |
| 2 | 4 | 2 | — |
| 5 | 25 | 5 | — |
| 10 | 100 | 10 | — |
| Confident wrong | — | — | -log(0.1) ≈ 2.3 |
| Very confident wrong | — | — | -log(0.01) ≈ 4.6 |
| Perfect wrong (0.999) | — | — | -log(0.001) ≈ 6.9 |

Cross-entropy grows logarithmically toward infinity as confidence in the wrong answer increases — this is its most important property.

---

## Framework Naming Reference

| Concept | PyTorch | Keras/TensorFlow |
|---------|---------|-----------------|
| MSE | `nn.MSELoss()` | `'mse'` |
| MAE | `nn.L1Loss()` | `'mae'` |
| Binary Cross-Entropy | `nn.BCELoss()` or `nn.BCEWithLogitsLoss()` | `'binary_crossentropy'` |
| Categorical Cross-Entropy | `nn.CrossEntropyLoss()` | `'categorical_crossentropy'` |
| Sparse Categorical CE | `nn.CrossEntropyLoss()` | `'sparse_categorical_crossentropy'` |

**Note:** In PyTorch, `nn.CrossEntropyLoss()` combines `LogSoftmax + NLLLoss` — do NOT apply softmax before this loss. `nn.BCEWithLogitsLoss()` combines `Sigmoid + BCE` — do NOT apply sigmoid before this loss. Both are numerically more stable than applying the activation separately.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Comparison.md** | ← you are here |

⬅️ **Prev:** [03 Activation Functions](../03_Activation_Functions/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 Forward Propagation](../05_Forward_Propagation/Theory.md)
