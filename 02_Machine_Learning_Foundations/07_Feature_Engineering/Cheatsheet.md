# Feature Engineering — Cheatsheet

**One-liner:** Feature engineering = transforming raw data into the right inputs so the model can actually learn what matters.

---

## Key Terms

| Term | What It Means |
|---|---|
| **Feature** | A single input variable the model uses to make predictions |
| **Feature selection** | Removing irrelevant or redundant features |
| **Feature creation** | Deriving new features from existing ones |
| **Normalization** | Rescaling features to the same range (e.g., 0–1) |
| **Standardization** | Rescaling features to mean=0, std=1 |
| **One-hot encoding** | Turning a categorical variable into binary columns (one per category) |
| **Label encoding** | Assigning a number to each category (for ordinal categories only) |
| **Imputation** | Filling in missing values |
| **Interaction feature** | A new feature created by combining two existing features (e.g., age × income) |
| **Cardinality** | Number of unique values in a categorical feature — high cardinality can cause issues |

---

## Encoding Methods Quick Reference

| Method | When To Use | When NOT To Use |
|---|---|---|
| One-hot encoding | Nominal categories (no order): colors, cities | High-cardinality categories (100+ values) |
| Label encoding | Ordinal categories (have order): small/medium/large | Nominal categories — implies false ordering |
| Target encoding | High-cardinality categories | Small datasets — risk of target leakage |
| Binary encoding | High-cardinality + memory-limited | When interpretability matters |

---

## Scaling Methods Quick Reference

| Method | Formula | Use When |
|---|---|---|
| Min-Max (Normalization) | (x - min) / (max - min) | Known bounded range; neural networks |
| StandardScaler (Z-score) | (x - mean) / std | Unknown range; general purpose |
| No scaling needed | — | Tree-based models (decision trees, random forests) |

---

## Golden Rules

1. **Tree-based models (decision trees, random forests, XGBoost) do NOT need scaling.** Everything else does.
2. **Never one-hot encode ordinal features.** Use label encoding or ordinal encoding.
3. **Create features that encode domain knowledge.** You know things the model does not — put that knowledge into the features.
4. **Fit the scaler on training data only. Apply to test data.** Fitting on test data is data leakage.
5. **Missingness itself can be a feature.** Create a "was_this_field_missing" binary column before imputing.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concept |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [06 Overfitting and Regularization](../06_Overfitting_and_Regularization/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [08 Gradient Descent](../08_Gradient_Descent/Theory.md)
