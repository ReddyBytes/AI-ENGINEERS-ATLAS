# XGBoost and Gradient Boosting — Cheatsheet

## Quick Comparison: Bagging vs Boosting

```
BAGGING (Random Forest)          BOOSTING (XGBoost)
────────────────────────         ──────────────────────────
Trees built in parallel          Trees built sequentially
Each tree sees random subset     Each tree learns from previous errors
Average predictions              Sum weighted predictions
Low variance                     Low bias + low variance
Good for noisy data              Better for structured tabular data
```

---

## XGBoost Key Parameters

| Parameter | Effect | Tuning Tip |
|---|---|---|
| `n_estimators` | Number of trees | Use early stopping, set high (1000) |
| `max_depth` | Tree depth | 3–6 for most problems; deeper = more overfit |
| `learning_rate` | Step size per tree | 0.01–0.1 with early stopping |
| `subsample` | Row sampling per tree | 0.6–0.9; reduces overfitting |
| `colsample_bytree` | Feature sampling per tree | 0.6–0.9; reduces overfitting |
| `reg_alpha` | L1 regularization | Increase when many irrelevant features |
| `reg_lambda` | L2 regularization | Default 1; increase for regularization |
| `gamma` | Min gain per split | 0–5; higher = simpler trees |
| `scale_pos_weight` | Imbalanced classes | Set to `neg_count / pos_count` |
| `min_child_weight` | Min sum of instance weight per leaf | Higher = more conservative splits |

---

## Quick Start Code

```python
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2)

model = xgb.XGBClassifier(
    n_estimators=1000,
    max_depth=5,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    eval_metric="logloss",
    early_stopping_rounds=50,
    random_state=42,
)

model.fit(
    X_train, y_train,
    eval_set=[(X_val, y_val)],
    verbose=100,
)

print(f"Best iteration: {model.best_iteration}")
print(f"Accuracy: {accuracy_score(y_val, model.predict(X_val)):.4f}")
```

---

## Feature Importance Types

| Type | What It Measures | When to Use |
|---|---|---|
| `weight` | Number of times feature used in splits | Quick baseline |
| `gain` | Average loss reduction per split | Better than weight |
| `cover` | Average number of samples per split | Dataset coverage |
| Permutation importance | Performance drop when feature shuffled | Most reliable; use sklearn |
| SHAP values | Contribution of each feature per prediction | Best for interpretability |

```python
import shap
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_val)
shap.summary_plot(shap_values, X_val)
```

---

## XGBoost vs LightGBM vs CatBoost

| | XGBoost | LightGBM | CatBoost |
|---|---|---|---|
| Speed (large data) | Moderate | Fastest | Moderate |
| Tree growth | Level-wise | Leaf-wise | Symmetric |
| Categoricals | Manual encode | Manual encode | Native |
| Overfitting risk | Low | Medium | Low |
| Install | `pip install xgboost` | `pip install lightgbm` | `pip install catboost` |
| Best use case | General default | Large datasets | Many categorical features |

---

## Hyperparameter Tuning Strategy

```python
# Step 1: fix learning_rate=0.1, tune tree structure
params_step1 = {
    "max_depth": [3, 5, 7],
    "min_child_weight": [1, 3, 5],
}

# Step 2: tune sampling
params_step2 = {
    "subsample": [0.6, 0.8, 1.0],
    "colsample_bytree": [0.6, 0.8, 1.0],
}

# Step 3: tune regularization
params_step3 = {
    "reg_alpha": [0, 0.1, 1.0],
    "reg_lambda": [0.5, 1.0, 5.0],
}

# Step 4: lower learning_rate, increase n_estimators with early stopping
```

---

## Golden Rules

1. Always use `early_stopping_rounds` — never guess `n_estimators`
2. Start with `learning_rate=0.1`, tune structure first, then lower to 0.01–0.05
3. `subsample` and `colsample_bytree` around 0.8 is a safe default
4. For imbalanced data: `scale_pos_weight = sum(negative) / sum(positive)`
5. XGBoost doesn't need feature scaling — tree splits are threshold-based
