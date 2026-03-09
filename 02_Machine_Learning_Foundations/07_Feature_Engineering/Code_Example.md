# Feature Engineering — Code Example

## Pandas-Based Feature Engineering: Normalize, Encode, and Create Features

We will take a small customer dataset with messy raw data and transform it into model-ready features step by step.

```python
# ============================================================
# FEATURE ENGINEERING WITH PANDAS
# Goal: Transform raw customer data into clean, model-ready features
# Techniques: normalization, encoding, feature creation
# ============================================================

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler

# ============================================================
# STEP 1: CREATE THE RAW DATASET
# This simulates the kind of data you would get from a database
# Notice the issues: different scales, categorical text, raw dates
# ============================================================

data = {
    'customer_id':     [1, 2, 3, 4, 5, 6, 7, 8],
    'age':             [25, 45, 32, 52, 28, 61, 38, 47],
    'annual_income':   [35000, 85000, 52000, 120000, 41000, 95000, 68000, 78000],
    'membership_type': ['basic', 'premium', 'basic', 'vip', 'basic', 'vip', 'premium', 'premium'],
    'signup_year':     [2020, 2018, 2022, 2019, 2023, 2017, 2021, 2020],
    'num_purchases':   [5, 42, 12, 78, 3, 91, 25, 38],
}

df = pd.DataFrame(data)
print("=== RAW DATA ===")
print(df.to_string())
print()

# ============================================================
# STEP 2: FEATURE CREATION — Derive new features from existing ones
# This is where domain knowledge adds value
# ============================================================

# Create 'years_as_customer' from signup_year
# We know more than the model — longer customers are more valuable
CURRENT_YEAR = 2026
df['years_as_customer'] = CURRENT_YEAR - df['signup_year']

# Create 'purchases_per_year' = total purchases / years as customer
# This normalizes purchase count for how long they've been a customer
# Avoids: new customer with 10 purchases looks worse than old customer with 11
df['purchases_per_year'] = df['num_purchases'] / df['years_as_customer'].clip(lower=1)

# Create 'income_age_ratio' = income / age
# Captures purchasing power relative to life stage
df['income_age_ratio'] = df['annual_income'] / df['age']

print("=== AFTER FEATURE CREATION ===")
print(df[['customer_id', 'years_as_customer', 'purchases_per_year', 'income_age_ratio']].to_string())
print()

# ============================================================
# STEP 3: ENCODING CATEGORICAL VARIABLES
# Models need numbers. 'membership_type' is a string — we must encode it.
# 'basic' < 'premium' < 'vip' HAS an order, so we use ordinal encoding.
# ============================================================

# Ordinal encoding: basic=0, premium=1, vip=2
# This preserves the ranking — better than one-hot for ordered categories
membership_order = {'basic': 0, 'premium': 1, 'vip': 2}
df['membership_encoded'] = df['membership_type'].map(membership_order)

print("=== AFTER ENCODING ===")
print(df[['membership_type', 'membership_encoded']].to_string())
print()

# If membership had NO natural order (like city names), we would use one-hot:
# one_hot = pd.get_dummies(df['membership_type'], prefix='membership')
# df = pd.concat([df, one_hot], axis=1)

# ============================================================
# STEP 4: NORMALIZATION — Bring numeric features to the same scale
# Without scaling: annual_income (35k–120k) dominates age (25–61)
# StandardScaler: mean=0, std=1 (good general purpose choice)
# ============================================================

# Select numeric features that need scaling
# Note: we do NOT scale the target variable (if we had one)
features_to_scale = ['age', 'annual_income', 'years_as_customer',
                     'purchases_per_year', 'income_age_ratio']

scaler = StandardScaler()

# IMPORTANT: In a real project, fit ONLY on training data
# Here we fit on all data for demonstration
df_scaled = df.copy()
df_scaled[features_to_scale] = scaler.fit_transform(df[features_to_scale])

print("=== AFTER SCALING (StandardScaler) ===")
print("Before scaling — annual_income range:",
      df['annual_income'].min(), "to", df['annual_income'].max())
print("After scaling  — annual_income range:",
      f"{df_scaled['annual_income'].min():.2f} to {df_scaled['annual_income'].max():.2f}")
print()

# Check that scaled features have mean≈0 and std≈1
print("Scaled feature means (should be ~0):")
print(df_scaled[features_to_scale].mean().round(2).to_string())
print("\nScaled feature stds (should be ~1):")
print(df_scaled[features_to_scale].std().round(2).to_string())
print()

# ============================================================
# STEP 5: ASSEMBLE THE FINAL FEATURE MATRIX
# Select only the engineered, model-ready columns
# Drop raw columns that have been transformed or are redundant
# ============================================================

feature_columns = features_to_scale + ['membership_encoded']

X_final = df_scaled[feature_columns]

print("=== FINAL MODEL-READY FEATURE MATRIX ===")
print(X_final.round(2).to_string())
print(f"\nShape: {X_final.shape}")  # (8, 6) — 8 customers, 6 features
print("\nFeatures used:", list(X_final.columns))
```

---

## What This Shows

- **Feature creation adds domain knowledge.** A model given only `num_purchases` does not know whether that is over 1 year or 10 years. `purchases_per_year` encodes that context explicitly.

- **Encoding is mandatory for categorical data.** `membership_type = 'vip'` means nothing to a model. `membership_encoded = 2` can be used in calculations. Ordinal encoding preserves order when categories have a natural ranking.

- **Scaling matters for scale-sensitive models.** `annual_income` (35k–120k) and `age` (25–61) are on completely different scales. After StandardScaler, both have mean=0 and std=1, and neither dominates.

- **The fit/transform separation is critical.** In production, you fit the scaler on training data and call `transform` (not `fit_transform`) on test and production data. Fitting on test data is a form of data leakage.

- **The final feature matrix** is a clean numeric grid that any sklearn model can accept directly as input to `.fit()`.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concept |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [06 Overfitting and Regularization](../06_Overfitting_and_Regularization/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [08 Gradient Descent](../08_Gradient_Descent/Theory.md)
