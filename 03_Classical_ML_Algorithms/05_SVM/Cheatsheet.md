# SVM — Cheatsheet

**One-liner:** SVM finds the hyperplane that separates two classes with the maximum possible margin, defined by the support vectors closest to the boundary.

---

## Key Terms

| Term | What It Means |
|---|---|
| Hyperplane | The decision boundary (a line in 2D, a plane in 3D, a flat surface in N-D) |
| Margin | The total gap between the two class boundaries on either side of the hyperplane |
| Support Vectors | The data points closest to the hyperplane — they define its position |
| Maximum Margin Classifier | The SVM goal: find the hyperplane with the widest margin |
| Kernel Trick | A mathematical shortcut to project data into higher dimensions without explicit computation |
| RBF Kernel | Radial Basis Function — the most common kernel, handles complex non-linear boundaries |
| C Parameter | Controls penalty for misclassification — high C = strict, low C = relaxed |
| Soft Margin | Allowing some misclassifications in the training data (via C) for better generalization |
| Hard Margin | Zero tolerance for misclassifications — only works if data is perfectly separable |

---

## When to Use vs When Not to Use

| Use SVM When | Avoid SVM When |
|---|---|
| Dataset is small to medium (< 100k rows) | Dataset is very large — training is slow |
| Data has many features (text, images) | Classes heavily overlap with no clear margin |
| You want a clean decision boundary | You need probability outputs (SVM doesn't give these by default) |
| Classes are clearly separable | Data has lots of noise |
| High-dimensional sparse data (e.g. NLP) | You need fast real-time predictions at scale |

---

## Common Kernels

| Kernel | Best For | Notes |
|---|---|---|
| `linear` | Linearly separable data, text classification | Fast, interpretable |
| `rbf` | Non-linear patterns, most general use | Default in sklearn, most popular |
| `poly` | Curved boundaries | Degree parameter controls complexity |
| `sigmoid` | Neural-network style boundaries | Rarely used in practice |

---

## Golden Rules

1. **Always scale your features** before using SVM. It is very sensitive to feature scale. Use `StandardScaler`.
2. **Start with RBF kernel** when you do not know the data structure.
3. **Tune C and gamma** together — use `GridSearchCV` or `RandomizedSearchCV`.
4. **Support vectors are all that matter** — the model ignores all other training points after training.
5. **SVM does not output probabilities** — use `SVC(probability=True)` only if you need them (it uses cross-validation internally and is slower).
6. **For multi-class problems** sklearn SVM uses one-vs-one by default — it trains `n*(n-1)/2` classifiers.
7. **Kernel trick is free in computation** — it computes similarity in the original space using the kernel function, never explicitly creates the high-dimensional representation.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [Theory.md](./Theory.md) | Core concepts, how SVM works, when to use |
| **Cheatsheet.md** | ← you are here |
| [Interview_QA.md](./Interview_QA.md) | Beginner to advanced interview questions |
| [Math_Intuition.md](./Math_Intuition.md) | Hyperplane geometry, kernel trick, C parameter |

⬅️ **Prev:** [04 Random Forests](../04_Random_Forests/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [06 K-Means Clustering](../06_K_Means_Clustering/Theory.md)
