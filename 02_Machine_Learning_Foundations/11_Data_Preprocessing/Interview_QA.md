# Data Preprocessing — Interview Q&A

---

## Beginner

**Q1: What is data preprocessing and why is it necessary?**

Data preprocessing is the set of transformations applied to raw data before feeding it to a machine learning model. It is necessary because real-world data almost never arrives model-ready: it has missing values, features on different scales, text categories instead of numbers, and extreme outlier values. Models are mathematical functions — they cannot operate on NaNs or strings. Even when data is numeric, scale differences cause gradient-based and distance-based algorithms to be dominated by high-magnitude features.

---

**Q2: What is the difference between StandardScaler and MinMaxScaler?**

StandardScaler subtracts the mean and divides by the standard deviation, producing output with mean=0 and std=1. Output is unbounded — a value 3 standard deviations from the mean scales to 3.0. MinMaxScaler subtracts the minimum and divides by the range, mapping every value to [0, 1]. StandardScaler is preferred for linear models, SVM, and PCA (which assume normality). MinMaxScaler is preferred for neural networks and bounded input requirements. MinMaxScaler is more sensitive to outliers — one extreme value compresses all other values toward zero.

---

**Q3: When should you use median imputation instead of mean imputation?**

Use median imputation when the feature has a skewed distribution or contains outliers. The mean is pulled toward extreme values — a salary column with a few billionaires will have a mean that misrepresents most employees. The median is unaffected by extremes. Practical rule: if the mean and median differ notably, default to median. For symmetric, normally distributed features without outliers, both produce similar results.

---

## Intermediate

**Q4: What is data leakage in preprocessing and how does a sklearn Pipeline prevent it?**

Data leakage occurs when information from the test set contaminates training. The most common example: fitting a StandardScaler on the full dataset before splitting. The scaler computes mean and std using test set values — the model effectively "sees" test set information during training, inflating evaluation metrics. A sklearn Pipeline prevents this by design: `pipeline.fit(X_train, y_train)` calls `fit_transform` on training data only for each step. `pipeline.predict(X_test)` calls only `transform` using the training-time statistics.

---

**Q5: When should you use OneHotEncoder vs OrdinalEncoder?**

Use OrdinalEncoder when categories have a meaningful natural order: `["low", "medium", "high"]`, `["bronze", "silver", "gold"]`. The integers 0, 1, 2 correctly represent the ordering. Use OneHotEncoder when categories are nominal — no natural order: `["cat", "dog", "rabbit"]`, `["New York", "London", "Tokyo"]`. Applying OrdinalEncoder to nominal data creates a false numeric relationship (the model may learn Tokyo=2 is "twice" London=1) which introduces noise and hurts performance.

---

**Q6: What is Winsorization and when would you choose it over dropping outliers?**

Winsorization caps outliers at the IQR fence values rather than removing them. The row is retained but the extreme value is replaced with the fence boundary. Choose Winsorization when: the dataset is small and you cannot afford to lose rows; the outlier is a genuine extreme value rather than a data error (a house that sold for $5M is real information); you need to preserve training examples. Drop rows only when the outlier is clearly a data entry error (age=999) and the dataset is large enough to absorb the loss.

---

**Q7: Why should you never apply LabelEncoder to a nominal input feature?**

LabelEncoder assigns arbitrary integers to categories — `{"cat": 0, "dog": 1, "rabbit": 2}`. This creates a false numeric relationship: the model interprets `rabbit` as numerically twice `dog`. For algorithms that use numeric magnitudes (linear models, SVMs, k-NN), these false relationships introduce systematic bias. OrdinalEncoder is correct for genuinely ordered features. OneHotEncoder is correct for nominal features — it makes no numeric claims about the categories. LabelEncoder is appropriate only for encoding the target variable `y` in classification.

---

## Advanced

**Q8: Explain train-serve skew and how a serialized Pipeline prevents it.**

Train-serve skew is the divergence between preprocessing at training time versus production inference. Example: a StandardScaler fitted on training data computes mean=45,000 for salary. A developer later writes fresh preprocessing code at inference and computes a new scaler on production data, getting mean=47,000. The model receives differently-scaled inputs than it was trained on — predictions degrade silently. A serialized Pipeline (`joblib.dump("pipeline.pkl")`) stores the exact fitted scaler parameters. At inference, loading the pipeline restores the identical scaler, guaranteeing the same transform is applied to every production input.

---

**Q9: When would you use KNNImputer or IterativeImputer over SimpleImputer?**

Use KNNImputer when missingness in one feature is correlated with other features. Example: income and years_of_experience are correlated — rows with missing income can be imputed more accurately by averaging the incomes of rows with similar experience values. Use IterativeImputer (MICE) when you need highest accuracy and have compute budget — it treats each feature with missing values as a regression target using all other features, cycling iteratively until convergence. Use SimpleImputer when missingness is completely random (MCAR) and you need fast, simple imputation. For production systems with latency requirements, SimpleImputer is preferred — KNNImputer and IterativeImputer are significantly slower at inference.

---

**Q10: How does TargetEncoder work and what precautions prevent leakage?**

TargetEncoder replaces each category with the mean of the target variable for rows in that category. If rows with `city="Paris"` have mean salary 65,000, every occurrence of Paris is replaced with 65,000. This is powerful for high-cardinality features because it produces one informative numeric column instead of hundreds of sparse binary columns. The leakage risk: computing target means on the full training set and using those features in cross-validation means the encoder "saw" the target for those rows. sklearn's `TargetEncoder` handles this with internal cross-fitting — means are computed from out-of-fold data only. Smoothing (blending category mean with global mean) prevents overfitting on rare categories.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concept |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |

⬅️ **Prev:** [Bias vs Variance](../10_Bias_vs_Variance/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Linear Regression](../../03_Classical_ML_Algorithms/01_Linear_Regression/Theory.md)
