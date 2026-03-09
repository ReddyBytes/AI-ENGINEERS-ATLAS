# Regularization — Cheatsheet

**One-liner:** Regularization is any technique that reduces a model's tendency to overfit training data by penalizing complexity, adding noise, or limiting training.

---

## Key Terms

| Term | What it means |
|------|---------------|
| Overfitting | Model performs well on training data but poorly on new data (memorized instead of learned) |
| Underfitting | Model is too simple to capture the pattern — poor on both train and test |
| Regularization | Any technique that improves generalization by reducing overfitting |
| L1 (Lasso) | Adds sum of absolute weights to loss — creates sparse (zero) weights |
| L2 (Ridge) | Adds sum of squared weights to loss — shrinks all weights toward zero |
| Lambda (λ) | Regularization strength — hyperparameter to tune |
| Dropout | Randomly zeros neurons during training |
| Dropout rate | Fraction of neurons zeroed (e.g., 0.5 = 50%) |
| Early stopping | Stop training when validation loss stops improving |
| Data augmentation | Creating new training examples via transformations |
| Sparsity | Many weights exactly equal to zero (created by L1) |

---

## Regularization Techniques at a Glance

| Technique | How it works | Added cost |
|-----------|-------------|-----------|
| L1 | Penalty = λ × Σ\|w\| | Near zero — just adds term to loss |
| L2 | Penalty = λ × Σw² | Near zero — just adds term to loss |
| Dropout | Zero out p% of neurons per forward pass | Minor training slowdown |
| Early stopping | Monitor val loss, stop at best point | Just monitoring overhead |
| Data augmentation | Transform training samples on-the-fly | Compute cost per transform |
| Batch normalization | Normalize activations per mini-batch | Small overhead, large stability gain |

---

## L1 vs L2

| | L1 (Lasso) | L2 (Ridge) |
|--|------------|-----------|
| Penalty | Sum of absolute values | Sum of squares |
| Effect on weights | Drives some to exactly 0 (sparse) | Drives all toward 0 (never exactly) |
| Feature selection | Yes — irrelevant features zeroed | No — all features kept, just smaller |
| Use when | You suspect many features irrelevant | You want smooth, distributed weights |
| Gradient behavior | Constant (-1 or +1) | Proportional to weight magnitude |

---

## When to Use / Not Use

| Technique | Use when... | Avoid when... |
|-----------|-------------|--------------|
| L2 | Almost always — good default | When interpretability via sparsity is needed |
| L1 | Many irrelevant features, want feature selection | Usually worse than L2 for deep nets |
| Dropout | Fully-connected layers, general overfitting | Batch normalization already used (overlap) |
| Early stopping | Always — free regularization | You've underfit and need more training |
| Data augmentation | Image/audio/text — almost always helps | Tabular structured data (hard to augment) |

---

## Golden Rules

1. The first thing to try when overfitting: more data > data augmentation > dropout > L2 > reduce model size.
2. L2 (weight decay) is so effective it is included in optimizers like AdamW by default.
3. Dropout rate of 0.2–0.5 for fully-connected layers; lower (0.1) or none for convolutional layers.
4. Always monitor both training loss and validation loss — overfitting is visible as a gap between the two.
5. Early stopping requires saving a checkpoint at the best validation loss — don't just stop training, save the weights.
6. Data augmentation is the most powerful regularizer when more data is not available.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |

⬅️ **Prev:** [07 Optimizers](../07_Optimizers/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [09 CNNs](../09_CNNs/Theory.md)
