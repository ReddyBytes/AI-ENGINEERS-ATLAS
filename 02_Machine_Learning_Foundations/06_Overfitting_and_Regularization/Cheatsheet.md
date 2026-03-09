# Overfitting and Regularization — Cheatsheet

**One-liner:** Overfitting = model memorizes training data. Regularization = techniques that force it to generalize instead.

---

## Key Terms

| Term | What It Means |
|---|---|
| **Overfitting** | Model learned training data too well — performs great on training, badly on new data |
| **Underfitting** | Model too simple — performs badly on both training and new data |
| **Generalization** | The ability to perform well on unseen data |
| **Bias** | Error from the model being too simple — misses real patterns |
| **Variance** | Error from the model being too complex — reacts to noise in training data |
| **Regularization** | Techniques that add constraints to prevent overfitting |
| **L1 (Lasso)** | Regularization that drives some weights to zero — good for feature selection |
| **L2 (Ridge)** | Regularization that shrinks all weights — most common default |
| **Dropout** | Randomly deactivating neurons during training to prevent co-dependence |
| **Early stopping** | Stop training when validation loss stops improving |
| **Train/val gap** | Large gap between training and validation accuracy = overfitting signal |

---

## Overfitting vs Underfitting Quick Reference

| Symptom | Problem | Fix |
|---|---|---|
| Train accuracy high, test accuracy low | Overfitting | More data, regularization, simpler model |
| Both train and test accuracy low | Underfitting | More complex model, more features, longer training |
| Validation loss rises while training loss falls | Overfitting | Early stopping, dropout, L1/L2 |
| Model works on training set, fails on production | Overfitting | Check for distribution shift + regularization |

---

## When to Use Each Regularization Method

| Method | Best For | Notes |
|---|---|---|
| **L2 (Ridge)** | Most models by default | Shrinks all weights, never zeros them |
| **L1 (Lasso)** | High-dimensional data with many irrelevant features | Zeros out irrelevant features automatically |
| **Dropout** | Neural networks | Only used during training, not inference |
| **Early stopping** | Any iterative training | Monitor validation loss, stop at minimum |
| **Max depth / min samples** | Decision trees | Direct complexity control |

---

## Golden Rules

1. **A small gap between train and validation accuracy = healthy.** A large gap = overfitting.
2. **More data beats regularization.** If you can get more labeled data, do that first.
3. **Always use a validation set.** You cannot spot overfitting without held-out data.
4. **Regularization is a knob — tune it.** Too much regularization causes underfitting.
5. **Early stopping is free.** Always monitor validation loss. There is no reason not to.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concept |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |

⬅️ **Prev:** [05 Model Evaluation](../05_Model_Evaluation/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [07 Feature Engineering](../07_Feature_Engineering/Theory.md)
