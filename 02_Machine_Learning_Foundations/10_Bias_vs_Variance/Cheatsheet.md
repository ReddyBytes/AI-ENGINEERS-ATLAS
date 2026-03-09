# Bias vs Variance — Cheatsheet

**One-liner:** Bias = consistently wrong. Variance = inconsistently right. You want both low.

---

## Key Terms

| Term | What It Means |
|---|---|
| **Bias** | Systematic error from a model that is too simple to learn the true pattern |
| **Variance** | Error from a model that is too sensitive to the specific training data used |
| **Underfitting** | High bias: model misses the real patterns in the data |
| **Overfitting** | High variance: model memorizes training data and fails on new data |
| **Model complexity** | Number of parameters / flexibility — higher complexity → lower bias, higher variance |
| **Irreducible error** | Noise in the data itself — cannot be eliminated by any model |
| **Total error** | Bias² + Variance + Irreducible noise |
| **Sweet spot** | The model complexity where total error is minimized |
| **Ensemble** | Combining multiple models to reduce variance without increasing bias |

---

## Diagnosis Table

| Training Error | Test Error | Diagnosis | Fix |
|---|---|---|---|
| High | High | High bias (underfitting) | More complex model, add features |
| Low | High | High variance (overfitting) | Regularization, more data, simpler model |
| Low | Low | Sweet spot | Nothing — deploy it |
| High | Very high | Both | Rethink model and data |

---

## Model Complexity vs Bias/Variance

| Model | Bias | Variance |
|---|---|---|
| Linear regression | High | Low |
| Deep neural network | Low | High (needs regularization) |
| Decision tree (no limit) | Low | Very high |
| Decision tree (shallow) | High | Low |
| Random forest | Low | Medium-low (bagging reduces variance) |

---

## Golden Rules

1. **If both training and test error are high, the problem is bias.** Adding more data won't fix it — change the model.
2. **If training error is low but test error is high, the problem is variance.** Regularize, simplify, or get more data.
3. **More data reduces variance but not bias.** Data helps with overfitting; it does not fix an underpowered model.
4. **Ensembles reduce variance.** Multiple diverse models average out each other's noise.
5. **The bias-variance tradeoff is real but manageable.** Regularization, cross-validation, and proper model selection let you find the sweet spot.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concept |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |

⬅️ **Prev:** [09 Loss Functions](../09_Loss_Functions/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [01 Linear Regression](../../03_Classical_ML_Algorithms/01_Linear_Regression/Theory.md)
