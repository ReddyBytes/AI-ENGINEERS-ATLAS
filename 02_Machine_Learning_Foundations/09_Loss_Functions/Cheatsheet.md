# Loss Functions — Cheatsheet

**One-liner:** A loss function measures how wrong the model is — the model trains by making this number as small as possible.

---

## Key Terms

| Term | What It Means |
|---|---|
| **Loss function** | Measures the difference between model predictions and correct answers |
| **MSE** | Mean Squared Error — average of (prediction - actual)² — for regression |
| **MAE** | Mean Absolute Error — average of abs(prediction - actual) — more robust to outliers |
| **Cross-entropy** | Log-based loss for classification — punishes confident wrong predictions |
| **Binary cross-entropy** | Cross-entropy for 2-class problems |
| **Categorical cross-entropy** | Cross-entropy for multi-class problems |
| **Hinge loss** | Used in SVMs — margin-based classification loss |
| **Log loss** | Another name for cross-entropy loss |
| **Regularization loss** | Added to main loss to penalize large weights (L1/L2) |
| **Calibration** | How well predicted probabilities match true frequencies |

---

## Quick Reference

| Task | Loss Function | Formula (simplified) |
|---|---|---|
| Regression | MSE | mean((ŷ - y)²) |
| Regression, outliers present | MAE | mean(|ŷ - y|) |
| Binary classification | Binary cross-entropy | -[y·log(ŷ) + (1-y)·log(1-ŷ)] |
| Multi-class classification | Categorical cross-entropy | -Σ y·log(ŷ) |
| SVM classification | Hinge loss | max(0, 1 - y·ŷ) |

---

## MSE vs MAE Comparison

| Property | MSE | MAE |
|---|---|---|
| Penalty for big errors | Very high (squared) | Proportional (linear) |
| Sensitivity to outliers | High | Low |
| Gradient at zero | Smooth | Undefined (but handled) |
| When to use | Clean data, punish large errors | Noisy data, outliers present |

---

## Golden Rules

1. **Classification? Use cross-entropy.** Not MSE — it does not work well for probability outputs.
2. **Regression? Use MSE as your default.** Switch to MAE if your data has many outliers.
3. **Cross-entropy punishes confidence.** Being wrong with 99% confidence is far worse than being wrong with 51% confidence.
4. **The loss function is your objective.** The model will optimize exactly what you specify — nothing more, nothing less. Choose carefully.
5. **Add regularization loss to your main loss** to prevent overfitting. The total loss = prediction error + weight penalty.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concept |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |

⬅️ **Prev:** [08 Gradient Descent](../08_Gradient_Descent/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [10 Bias vs Variance](../10_Bias_vs_Variance/Theory.md)
