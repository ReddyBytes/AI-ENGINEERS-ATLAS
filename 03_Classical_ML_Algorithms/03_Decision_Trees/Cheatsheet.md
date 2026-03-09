# Decision Trees — Cheatsheet

**One-liner:** A decision tree learns a series of yes/no questions that split data into increasingly pure groups — fully readable, no scaling needed.

---

## Key Terms

| Term | What It Means |
|---|---|
| **Root node** | The first split — the most informative question on all the data |
| **Internal node** | Any split that is not the first or last |
| **Leaf node** | The end of a branch — the final prediction |
| **Depth** | How many levels of splits the tree has |
| **Gini impurity** | How mixed a node is (0 = pure, 0.5 = maximally mixed) |
| **Information gain** | How much a split reduces impurity |
| **Entropy** | Another impurity measure (from information theory) |
| **max_depth** | The key hyperparameter — limits tree size to control overfitting |
| **min_samples_leaf** | Minimum examples required to create a leaf — prevents over-splitting |
| **Feature importance** | How much each feature contributed to reducing impurity across all splits |

---

## When to Use / Not Use

| Use Decision Trees When... | Avoid When... |
|---|---|
| Interpretability is essential | You need high accuracy (use random forest instead) |
| Mixed feature types (numeric + categorical) | Data is very noisy (deep trees memorize noise) |
| No time for feature scaling | Class boundaries are smooth (logistic regression may work better) |
| Quick, explainable baseline | Regression with many continuous features |
| The decision structure itself is valuable | Production accuracy matters more than explainability |

---

## Hyperparameter Quick Reference

| Parameter | Default | Effect |
|---|---|---|
| `max_depth` | None (unlimited) | Limits tree depth — most important for preventing overfitting |
| `min_samples_split` | 2 | Minimum samples needed to split a node |
| `min_samples_leaf` | 1 | Minimum samples in a leaf — higher = more regularization |
| `max_features` | All features | Randomly limit features per split — adds diversity |
| `criterion` | gini | gini or entropy — usually makes little practical difference |

---

## Golden Rules

1. **Always set max_depth.** Unlimited trees always overfit. Start with depth 3–5.
2. **No feature scaling required.** Trees use rank-based splits, not distances.
3. **Decision trees are a great baseline but almost never the best model.** Use random forests for real accuracy.
4. **Print the tree.** `export_text()` in sklearn shows you every rule. If it looks nonsensical, your data or features need review.
5. **Feature importance from trees is informative.** Features used near the root with high gain are genuinely predictive.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concept |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [02 Logistic Regression](../02_Logistic_Regression/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 Random Forests](../04_Random_Forests/Theory.md)
