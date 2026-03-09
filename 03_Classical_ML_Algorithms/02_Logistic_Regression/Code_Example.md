# Logistic Regression — Code Example

## Binary Classification: Predicting Hospital Emergency vs Non-Emergency

We will train a logistic regression model on simulated patient data to predict whether a patient needs emergency care.

```python
# ============================================================
# LOGISTIC REGRESSION — EMERGENCY CLASSIFICATION
# Goal: Predict if a patient needs emergency care (1) or not (0)
# Features: heart_rate, age, chest_pain_score
# ============================================================

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import (classification_report, confusion_matrix,
                              accuracy_score, roc_auc_score)
from sklearn.preprocessing import StandardScaler

# ============================================================
# STEP 1: CREATE THE DATASET
# 100 patients with 3 features each + emergency label
# ============================================================

np.random.seed(42)
n = 100

# Emergency patients (50): high heart rate, older, high chest pain
emergency = np.column_stack([
    np.random.normal(130, 15, 50),   # heart rate: ~130 bpm
    np.random.normal(60, 12, 50),    # age: ~60 years
    np.random.normal(7, 1.5, 50),    # chest pain score: ~7/10
])

# Non-emergency patients (50): lower heart rate, younger, low chest pain
non_emergency = np.column_stack([
    np.random.normal(80, 12, 50),    # heart rate: ~80 bpm
    np.random.normal(35, 12, 50),    # age: ~35 years
    np.random.normal(2, 1, 50),      # chest pain score: ~2/10
])

# Stack into one dataset
X = np.vstack([emergency, non_emergency])
y = np.array([1]*50 + [0]*50)  # 1 = emergency, 0 = not emergency

feature_names = ['heart_rate', 'age', 'chest_pain_score']
print(f"Dataset: {len(X)} patients")
print(f"Emergency: {y.sum()}, Non-emergency: {(y==0).sum()}")

# ============================================================
# STEP 2: SPLIT AND SCALE
# Logistic regression uses gradient descent — scale the features
# so all features contribute equally to the linear equation
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
    # stratify=y: ensure test set has same class ratio as full dataset
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)   # fit on train, transform train
X_test_scaled = scaler.transform(X_test)          # only transform on test (no fit!)

# ============================================================
# STEP 3: TRAIN THE MODEL
# C=1.0 controls regularization (smaller C = stronger regularization)
# Default solver works well for small datasets
# ============================================================

model = LogisticRegression(C=1.0, random_state=42, max_iter=200)
model.fit(X_train_scaled, y_train)

print("\nModel trained!")
print("Learned coefficients:")
for name, coef in zip(feature_names, model.coef_[0]):
    print(f"  {name:<22}: {coef:+.3f}")
print(f"  {'intercept':<22}: {model.intercept_[0]:+.3f}")

# ============================================================
# STEP 4: PREDICT — TWO MODES
# predict()         → class labels (0 or 1) using default threshold 0.5
# predict_proba()   → probability for each class [P(class0), P(class1)]
# ============================================================

y_pred = model.predict(X_test_scaled)
y_prob = model.predict_proba(X_test_scaled)[:, 1]  # probability of class 1 (emergency)

print("\nSample predictions:")
print(f"{'Actual':<10} {'Predicted':<12} {'P(Emergency)'}")
print("-" * 38)
for actual, pred, prob in zip(y_test[:8], y_pred[:8], y_prob[:8]):
    correct = "✓" if actual == pred else "✗"
    print(f"{actual:<10} {pred:<12} {prob:.3f}  {correct}")

# ============================================================
# STEP 5: EVALUATE
# ============================================================

print("\n=== EVALUATION ===")
print(f"Accuracy: {accuracy_score(y_test, y_pred):.2%}")
print(f"ROC-AUC:  {roc_auc_score(y_test, y_prob):.3f}")

print("\nConfusion Matrix:")
cm = confusion_matrix(y_test, y_pred)
print(f"  Predicted:  Not-Emergency  Emergency")
print(f"Actual Not:   {cm[0,0]:<15} {cm[0,1]}")
print(f"Actual Yes:   {cm[1,0]:<15} {cm[1,1]}")

print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=['Not Emergency', 'Emergency']))

# ============================================================
# STEP 6: PREDICT A NEW PATIENT — REAL INFERENCE
# ============================================================

# New patient: HR=145, age=72, chest_pain=8
new_patient = [[145, 72, 8]]
new_patient_scaled = scaler.transform(new_patient)

prob_emergency = model.predict_proba(new_patient_scaled)[0, 1]
decision = model.predict(new_patient_scaled)[0]

print(f"\nNew patient: HR=145, age=72, chest_pain=8")
print(f"P(Emergency): {prob_emergency:.3f}")
print(f"Decision: {'EMERGENCY' if decision == 1 else 'Can wait'}")

# ============================================================
# THRESHOLD ADJUSTMENT: What if we lower the threshold?
# Lower threshold = catch more emergencies (higher recall)
# but also more false alarms (lower precision)
# ============================================================

threshold = 0.3  # more cautious — flag as emergency if >30% chance
y_pred_cautious = (y_prob >= threshold).astype(int)

print(f"\nWith threshold={threshold} (more cautious):")
print(f"Emergency predictions: {y_pred_cautious.sum()} (vs {y_pred.sum()} at 0.5)")
print(classification_report(y_test, y_pred_cautious,
                             target_names=['Not Emergency', 'Emergency'],
                             zero_division=0))
```

---

## What This Shows

- **predict() vs predict_proba()** — `predict()` gives you a hard class label (0 or 1). `predict_proba()` gives you the underlying probability. In many real applications you want the probability — so you can rank patients by risk, not just split them into two groups.

- **Coefficients are interpretable** — the learned coefficients tell you which features drive the emergency prediction. Large positive coefficient = strong predictor of emergency. This is something random forests cannot do as cleanly.

- **Scale before training** — the scaler is fit on training data only, then applied to test data. Fitting on test data would be leakage.

- **Threshold adjustment** — the 0.5 default is not always right. In medical contexts you would lower the threshold to catch more real emergencies, even at the cost of more false alarms.

- **ROC-AUC measures ranking quality** — how well the model separates emergency from non-emergency patients across all possible thresholds.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concept |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Math_Intuition.md](./Math_Intuition.md) | Math intuition behind the algorithm |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [01 Linear Regression](../01_Linear_Regression/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 Decision Trees](../03_Decision_Trees/Theory.md)
