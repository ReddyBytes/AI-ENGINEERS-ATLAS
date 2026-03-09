# Loss Functions — Cheatsheet

**One-liner:** A loss function is a mathematical score of how wrong the model's predictions are — the optimizer then minimizes this score during training.

---

## Key Terms

| Term | What it means |
|------|---------------|
| Loss | A number measuring how wrong the model is — 0 is perfect |
| MSE | Mean Squared Error — average squared difference between predictions and actuals |
| MAE | Mean Absolute Error — average absolute difference (less sensitive to outliers than MSE) |
| Cross-Entropy | Loss for classification — penalizes confident wrong predictions logarithmically |
| Binary Cross-Entropy | Cross-entropy for two-class problems |
| Log Loss | Another name for Binary Cross-Entropy |
| Logits | Raw output scores before softmax/sigmoid |
| Gradient of loss | The signal that tells the optimizer which direction to update weights |

---

## Formula Quick Reference

```
MSE  = (1/n) × Σ (y_pred - y_true)²

MAE  = (1/n) × Σ |y_pred - y_true|

BCE  = -[ y × log(p) + (1-y) × log(1-p) ]

CE   = -Σ y_i × log(p_i)  →  simplifies to  -log(p_correct_class)
```

---

## Task → Loss Function

| Task | Loss | Output Activation |
|------|------|------------------|
| Regression | MSE or MAE | Linear (none) |
| Binary classification | Binary Cross-Entropy | Sigmoid |
| Multi-class classification | Categorical Cross-Entropy | Softmax |
| Multi-label classification | Binary Cross-Entropy per label | Sigmoid per output |
| Ordinal regression | MSE or Ordinal Cross-Entropy | Linear |

---

## MSE vs MAE

| | MSE | MAE |
|--|-----|-----|
| Formula | Mean of squared errors | Mean of absolute errors |
| Outlier sensitivity | High — outliers get squared, dominate loss | Low — outliers treated proportionally |
| Gradient | Large near big errors (good for optimization) | Constant (can oscillate near minimum) |
| Use when | Outliers are rare, you want smooth optimization | Outliers are common and you want robustness |

---

## When to Use / Not Use

| Use when... | Do NOT use when... |
|-------------|-------------------|
| MSE: regression with normally distributed errors | MSE: when outliers would distort training |
| BCE: binary classification, sigmoid output | BCE: multi-class problems |
| CE: multi-class, softmax output | CE: regression — meaningless here |
| MAE: regression with outliers | MAE: as sole loss — can cause training instability |

---

## Golden Rules

1. Loss function choice is determined by task — not by tuning.
2. Classification always uses cross-entropy, not MSE (MSE with sigmoid causes slow training and bad gradients).
3. Cross-entropy penalizes confident wrong predictions extremely harshly (log of near-0 → very large number).
4. The loss for a perfectly confident correct prediction approaches 0. The loss for a perfectly confident wrong prediction approaches infinity.
5. Always pair the correct loss with the correct output activation (sigmoid ↔ BCE, softmax ↔ CE, linear ↔ MSE).

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Comparison.md](./Comparison.md) | Loss functions comparison |

⬅️ **Prev:** [03 Activation Functions](../03_Activation_Functions/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 Forward Propagation](../05_Forward_Propagation/Theory.md)
