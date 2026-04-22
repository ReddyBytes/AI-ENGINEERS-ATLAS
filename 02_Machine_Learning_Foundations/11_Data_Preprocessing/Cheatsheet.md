# Data Preprocessing — Cheatsheet

## sklearn Class Reference

| Class | Module | What It Does |
|---|---|---|
| `SimpleImputer` | `sklearn.impute` | Fill NaN with mean / median / most_frequent / constant |
| `KNNImputer` | `sklearn.impute` | Fill NaN using k-nearest-neighbor rows |
| `IterativeImputer` | `sklearn.impute` | Fill NaN via multivariate regression (MICE) |
| `OrdinalEncoder` | `sklearn.preprocessing` | Integer encode ordered categorical features |
| `OneHotEncoder` | `sklearn.preprocessing` | Binary columns for nominal categorical features |
| `TargetEncoder` | `sklearn.preprocessing` | Replace category with mean target value |
| `MinMaxScaler` | `sklearn.preprocessing` | Scale to [0, 1] |
| `StandardScaler` | `sklearn.preprocessing` | Zero mean, unit variance |
| `RobustScaler` | `sklearn.preprocessing` | Median-centered, IQR-scaled (outlier-resistant) |
| `PowerTransformer` | `sklearn.preprocessing` | Box-Cox / Yeo-Johnson to Gaussianize skewed features |
| `Pipeline` | `sklearn.pipeline` | Chain steps, enforce fit/transform sequencing |
| `ColumnTransformer` | `sklearn.compose` | Different transforms per column subset |

---

## Scaler Selection Guide

| Scaler | Use When | Avoid When |
|---|---|---|
| **StandardScaler** | Linear models, SVM, PCA, logistic regression | Heavy outliers present |
| **MinMaxScaler** | Neural networks, bounded inputs needed | Outliers present (compress the range) |
| **RobustScaler** | Outliers present and cannot be removed | Algorithm needs strict [0,1] bounds |
| **PowerTransformer** | Highly skewed feature, using linear model | Tree-based models (scale-invariant) |
| **No scaling** | Decision trees, Random Forest, XGBoost | — |

---

## Encoding Decision Guide

| Feature Type | Correct Encoder | Example |
|---|---|---|
| Ordinal (natural order) | `OrdinalEncoder` | low / medium / high |
| Nominal, low cardinality | `OneHotEncoder(drop="first")` | cat / dog / rabbit |
| Nominal, high cardinality | `TargetEncoder` | city with 500 values |
| Target variable `y` only | `LabelEncoder` | class labels |

---

## Imputation Strategy Quick Reference

| Strategy | Use When |
|---|---|
| `mean` | Numeric, symmetric, no outliers |
| `median` | Numeric, skewed or outliers present |
| `most_frequent` | Categorical or binary numeric |
| `KNNImputer` | Missingness correlates with other features |
| `IterativeImputer` | Maximum accuracy, compute available |
| Drop row | < 5% missing, clearly random (MCAR) |
| Drop column | > 40% missing, low feature value |

---

## Outlier Detection Quick Reference

| Method | Best For | Threshold |
|---|---|---|
| **IQR fence** | Univariate, any distribution | Outside Q1−1.5×IQR / Q3+1.5×IQR |
| **Z-score** | Univariate, normal distribution | \|z\| > 3 |
| **LocalOutlierFactor** | Multivariate, density-based | contamination parameter |
| **IsolationForest** | High-dimensional, many anomalies | contamination parameter |

---

## Algorithm Scaling Sensitivity

| Algorithm | Needs Scaling? |
|---|---|
| Linear / Logistic Regression | Yes |
| SVM | Yes |
| k-NN | Yes |
| PCA | Yes |
| Neural Networks | Yes |
| Decision Tree | No |
| Random Forest | No |
| XGBoost / LightGBM | No |

---

## Data Leakage Rules

1. **Split first, preprocess second** — never fit any transformer on the full dataset
2. **Use sklearn Pipeline** — auto-applies `fit_transform` on train, `transform` on test
3. **Save the fitted Pipeline** with `joblib.dump()` — reload at inference time
4. **TargetEncoder inside CV folds** — use sklearn's built-in cross-fitting

---

## Pipeline Template

```python
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
import joblib

preprocessor = ColumnTransformer([
    ("num", Pipeline([
        ("imp", SimpleImputer(strategy="median")),
        ("scl", StandardScaler()),
    ]), numeric_cols),
    ("cat", Pipeline([
        ("imp", SimpleImputer(strategy="most_frequent")),
        ("enc", OneHotEncoder(handle_unknown="ignore", drop="first")),
    ]), categorical_cols),
])

pipeline = Pipeline([("prep", preprocessor), ("model", your_model)])
pipeline.fit(X_train, y_train)
joblib.dump(pipeline, "pipeline.pkl")   # serialize for inference
```

---

## Golden Rules

1. Always use Pipeline — manual fit/transform is a leakage timebomb
2. Median > mean for skewed numeric features
3. One-hot for nominal, ordinal for ordered — never LabelEncoder on features
4. Serialize the entire Pipeline alongside the model
5. Scaling is irrelevant for tree-based models — skip it for XGBoost/RF
