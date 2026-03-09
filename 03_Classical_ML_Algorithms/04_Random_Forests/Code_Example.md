# Random Forests — Code Example

## Comparing Single Tree vs Random Forest on Tabular Data

We will train both a single decision tree and a random forest on the same dataset, directly comparing accuracy, overfitting, and feature importance.

```python
# ============================================================
# RANDOM FORESTS — IRIS CLASSIFICATION
# Comparing decision tree vs random forest side by side
# ============================================================

from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report
import numpy as np

# ============================================================
# STEP 1: LOAD DATA
# ============================================================

iris = load_iris()
X = iris.data
y = iris.target
feature_names = iris.feature_names
class_names = iris.target_names

# ============================================================
# STEP 2: TRAIN/TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.25,
    random_state=42,
    stratify=y
)

print(f"Training: {len(X_train)} samples | Test: {len(X_test)} samples")

# ============================================================
# STEP 3: TRAIN BOTH MODELS
# Decision tree: prone to overfitting (no depth limit)
# Random forest: ensemble of 100 diverse trees
# ============================================================

# Single decision tree — the "one friend" approach
single_tree = DecisionTreeClassifier(random_state=42)
single_tree.fit(X_train, y_train)

# Random forest — the "ask 100 friends" approach
# n_estimators: number of trees (100 is the default)
# max_features='sqrt': each split considers sqrt(4) ≈ 2 features at random
# oob_score=True: use out-of-bag samples for a free validation estimate
forest = RandomForestClassifier(
    n_estimators=100,
    max_features='sqrt',
    oob_score=True,
    random_state=42,
    n_jobs=-1   # use all CPU cores — trees train in parallel
)
forest.fit(X_train, y_train)

# ============================================================
# STEP 4: COMPARE TRAINING vs TEST ACCURACY
# The "gap" between train and test reveals overfitting
# ============================================================

print("\n=== OVERFITTING COMPARISON ===")
print(f"{'Model':<25} {'Train Acc':<15} {'Test Acc':<15} {'Gap'}")
print("-" * 60)

for name, model in [("Single Decision Tree", single_tree), ("Random Forest (100)", forest)]:
    train_acc = accuracy_score(y_train, model.predict(X_train))
    test_acc = accuracy_score(y_test, model.predict(X_test))
    gap = train_acc - test_acc
    print(f"{name:<25} {train_acc:<15.2%} {test_acc:<15.2%} {gap:.2%}")

# Random forest OOB score — free evaluation, no test set needed
print(f"\nRandom Forest OOB Score: {forest.oob_score_:.2%}")
print("(This is an unbiased estimate from examples each tree didn't train on)")

# ============================================================
# STEP 5: DETAILED EVALUATION OF RANDOM FOREST
# ============================================================

y_pred_forest = forest.predict(X_test)

print("\n=== RANDOM FOREST — TEST EVALUATION ===")
print(f"Accuracy: {accuracy_score(y_test, y_pred_forest):.2%}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred_forest, target_names=class_names))

# ============================================================
# STEP 6: CROSS-VALIDATION — MORE RELIABLE ACCURACY ESTIMATE
# 5-fold CV: train 5 times on different splits, average the scores
# This gives a more stable estimate than a single train/test split
# ============================================================

cv_scores_tree = cross_val_score(single_tree, X, y, cv=5, scoring='accuracy')
cv_scores_forest = cross_val_score(forest, X, y, cv=5, scoring='accuracy')

print("\n=== 5-FOLD CROSS-VALIDATION ===")
print(f"Decision Tree: {cv_scores_tree.mean():.2%} ± {cv_scores_tree.std():.2%}")
print(f"Random Forest: {cv_scores_forest.mean():.2%} ± {cv_scores_forest.std():.2%}")
print("(Lower std = more consistent, more reliable model)")

# ============================================================
# STEP 7: FEATURE IMPORTANCE
# Which features does the forest use most across all 100 trees?
# ============================================================

importances = forest.feature_importances_
std = np.std([tree.feature_importances_ for tree in forest.estimators_], axis=0)

print("\n=== FEATURE IMPORTANCE ===")
print(f"{'Feature':<30} {'Importance':<12} {'Std Dev'}")
print("-" * 55)

# Sort by importance
indices = np.argsort(importances)[::-1]
for i in indices:
    bar = "=" * int(importances[i] * 40)
    print(f"{feature_names[i]:<30} {importances[i]:.3f} ± {std[i]:.3f}  {bar}")

print("\nInsight: Features near top drive most of the predictions")
print("High std = importance varies between trees = less reliable signal")

# ============================================================
# STEP 8: PREDICT A NEW FLOWER WITH PROBABILITIES
# Random forest outputs the fraction of trees voting for each class
# This is more informative than a hard 0/1 label
# ============================================================

new_flower = [[6.5, 3.0, 5.2, 2.0]]  # looks like virginica
probabilities = forest.predict_proba(new_flower)[0]
prediction = forest.predict(new_flower)[0]

print(f"\n=== NEW FLOWER PREDICTION ===")
print(f"Features: sepal_l=6.5, sepal_w=3.0, petal_l=5.2, petal_w=2.0")
print(f"\nProbability breakdown (fraction of trees voting for each class):")
for class_name, prob in zip(class_names, probabilities):
    bar = "=" * int(prob * 30)
    print(f"  {class_name:<15}: {prob:.3f}  {bar}")
print(f"\nFinal prediction: {class_names[prediction]}")
```

---

## What This Shows

- **The gap reveals overfitting.** The single decision tree has 100% training accuracy but lower test accuracy — it memorized the training data. The random forest's training accuracy is lower (it does not overfit each specific sample), but test accuracy is higher or equal. The gap is smaller.

- **OOB score is a free validation metric.** Because each tree only trains on ~63% of examples, you get a built-in validation score without using any test data. It closely approximates what cross-validation would give you.

- **Cross-validation mean ± std** tells you both accuracy and reliability. The random forest typically shows not just higher mean accuracy but lower standard deviation — more consistent across different data splits.

- **Feature importance** shows that petal measurements dominate, with sepal measurements barely contributing. This is a real insight about which physical measurements distinguish iris species.

- **predict_proba()** gives you the fraction of trees that voted for each class — a natural probability from the forest. If 95 out of 100 trees agree, you have a confident, reliable prediction. If 55 vote one way and 45 the other, the model is uncertain and you should treat the prediction cautiously.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concept |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [03 Decision Trees](../03_Decision_Trees/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 SVM](../05_SVM/Theory.md)
