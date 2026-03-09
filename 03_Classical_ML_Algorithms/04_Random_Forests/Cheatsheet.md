# Random Forests — Cheatsheet

**One-liner:** A random forest trains many diverse decision trees on random data subsets, then combines their votes — more accurate and robust than any single tree.

---

## Key Terms

| Term | What It Means |
|---|---|
| **Ensemble** | Combining multiple models to get better predictions than any single model |
| **Bagging** | Bootstrap Aggregating — train each tree on a random sample (with replacement) |
| **Bootstrapping** | Sampling with replacement — the same data point can appear multiple times in one sample |
| **Out-of-bag (OOB)** | Training examples NOT selected for a particular tree — can be used for free evaluation |
| **Feature randomness** | Each split considers only a random subset of features — creates tree diversity |
| **n_estimators** | Number of trees in the forest — more trees = more stable, slower to train |
| **Feature importance** | How much each feature contributed to impurity reduction across all trees |
| **Majority vote** | How classification prediction works — most trees win |
| **Averaging** | How regression prediction works — average of all tree outputs |
| **max_features** | Fraction or count of features to consider per split (controls diversity) |

---

## Key Hyperparameters

| Parameter | Default | What It Controls |
|---|---|---|
| `n_estimators` | 100 | Number of trees — more = better up to a point, then diminishing returns |
| `max_depth` | None | Depth of each tree — None usually fine (bagging prevents overfitting) |
| `max_features` | 'sqrt' for classification | Features per split — lower = more diversity, lower = slightly higher bias |
| `min_samples_leaf` | 1 | Minimum leaf size — increase to add regularization |
| `n_jobs` | 1 | Parallelism — set to -1 to use all CPU cores |
| `oob_score` | False | Set to True to get a free validation score using out-of-bag examples |

---

## When to Use / Not Use

| Use Random Forest When... | Avoid When... |
|---|---|
| Tabular data classification or regression | You need full interpretability of each prediction |
| You want high accuracy with minimal tuning | Extremely large datasets (training 1000 trees is slow) |
| Mixed feature types | Real-time prediction with strict latency requirements |
| You want free feature importance | A simpler model (logistic regression) is sufficient |
| Dataset is medium-large (thousands of rows) | Extremely high-dimensional sparse data (try linear models first) |

---

## Golden Rules

1. **Start with n_estimators=100.** More trees rarely hurt, but returns diminish after ~200-500.
2. **Random forests almost never overfit.** Bagging reduces variance dramatically — the main risk is slow training.
3. **Feature importance is useful but not causal.** Correlated features split importance arbitrarily between them.
4. **Use oob_score=True for a free validation estimate** without needing a separate validation split.
5. **Random forests are the best first-try model for tabular data.** Before trying XGBoost or neural networks, see what a random forest gives you.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concept |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [03 Decision Trees](../03_Decision_Trees/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 SVM](../05_SVM/Theory.md)
