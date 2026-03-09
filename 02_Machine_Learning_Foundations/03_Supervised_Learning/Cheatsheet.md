# Supervised Learning — Cheatsheet

**One-liner:** Supervised learning = teach the model using examples that already have the right answers.

---

## Key Terms

| Term | What It Means |
|---|---|
| **Label** | The correct answer attached to each training example |
| **Feature** | An input variable the model uses to make a prediction |
| **Classification** | Predicting a category (spam/not-spam, cat/dog) |
| **Regression** | Predicting a number (house price, temperature) |
| **Training set** | The labeled examples used to teach the model |
| **Test set** | Held-out examples used to evaluate the trained model |
| **Overfitting** | Model memorized training examples instead of learning patterns |
| **Generalization** | The model works well on data it has never seen before |
| **Prediction** | The model's output for a new, unseen input |

---

## When to Use / Not Use

| Use Supervised Learning When... | Avoid When... |
|---|---|
| You have labeled training data | You have no labels (use unsupervised) |
| The output is a known category or number | The output is free-form or unknown |
| You need accurate predictions on specific targets | You want to discover hidden patterns |
| Examples: spam, fraud, diagnosis, price prediction | Examples: customer segmentation, anomaly detection |

---

## Golden Rules

1. **No labels = no supervised learning.** Labels are the fuel.
2. **Garbage labels = garbage model.** Label quality matters more than quantity.
3. **Always evaluate on data the model has never seen.** Otherwise you're cheating.
4. **Classification = category output. Regression = numeric output.** Know which one you need.
5. **More diverse training examples = better generalization.** One type of example is not enough.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concept |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [02 Training vs Inference](../02_Training_vs_Inference/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 Unsupervised Learning](../04_Unsupervised_Learning/Theory.md)
