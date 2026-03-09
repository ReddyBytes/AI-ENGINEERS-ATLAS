# Logistic Regression — Cheatsheet

**One-liner:** Logistic regression predicts the probability of belonging to a class by squishing a linear equation through the sigmoid function.

---

## Key Terms

| Term | What It Means |
|---|---|
| **Sigmoid** | A function that maps any number to (0, 1): 1/(1+e^-z) |
| **Decision boundary** | The input values where the model outputs exactly 0.5 — the classification line |
| **Threshold** | The probability cutoff for deciding class 1 vs class 0 (default 0.5) |
| **Log loss** | The loss function — penalizes confident wrong predictions |
| **Weights / coefficients** | The learned values that determine which features matter most |
| **Odds** | P(event) / P(not event) — logistic regression models the log of odds |
| **Log-odds (logit)** | The linear equation inside logistic regression: log(P/(1-P)) |
| **Multiclass** | Logistic regression extends to multiple classes via softmax (multinomial) |
| **Regularization** | C parameter in sklearn — smaller C = more regularization |

---

## When to Use / Not Use

| Use Logistic Regression When... | Avoid When... |
|---|---|
| Binary classification problem | Output is continuous (use linear regression) |
| You need probability outputs (not just class) | Decision boundary is strongly non-linear |
| Interpretability is required | Data has complex feature interactions |
| Quick, reliable baseline | More than 2 classes with complex boundaries |
| Small to medium dataset | Very high-dimensional data with sparse features (try Naive Bayes) |

---

## Golden Rules

1. **Logistic regression IS a classification algorithm.** The word "regression" is historical — it outputs probabilities, not numbers.
2. **The default threshold (0.5) is not always optimal.** For imbalanced data or asymmetric error costs, tune the threshold.
3. **Regularize by default.** sklearn's LogisticRegression has L2 regularization on by default (C=1). This is appropriate.
4. **Always use cross-entropy as the loss — never MSE for classification.**
5. **Great as a baseline.** Before trying random forests or neural networks, logistic regression tells you the floor of what a simple model can do.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concept |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Math_Intuition.md](./Math_Intuition.md) | Math intuition behind the algorithm |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [01 Linear Regression](../01_Linear_Regression/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 Decision Trees](../03_Decision_Trees/Theory.md)
