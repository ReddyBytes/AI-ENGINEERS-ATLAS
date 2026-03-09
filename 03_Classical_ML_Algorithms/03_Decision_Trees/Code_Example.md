# Decision Trees — Code Example

## Training a Decision Tree and Reading Its Rules

We will train a decision tree on the Iris dataset, visualize the learned rules, and understand what the tree actually figured out.

```python
# ============================================================
# DECISION TREES — IRIS CLASSIFICATION
# Goal: Train a tree, read the rules, evaluate performance
# ============================================================

from sklearn.datasets import load_iris
from sklearn.tree import DecisionTreeClassifier, export_text, plot_tree
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import numpy as np

# ============================================================
# STEP 1: LOAD DATA
# ============================================================

iris = load_iris()
X = iris.data                # 4 features: sepal length/width, petal length/width
y = iris.target              # 3 classes: 0=setosa, 1=versicolor, 2=virginica
feature_names = iris.feature_names
class_names = iris.target_names

print(f"Dataset: {X.shape[0]} flowers, {X.shape[1]} features")
print(f"Classes: {list(class_names)}")

# ============================================================
# STEP 2: SPLIT DATA
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

print(f"Training: {len(X_train)}, Test: {len(X_test)}")

# ============================================================
# STEP 3: TRAIN TWO TREES — COMPARE DEPTH
# Tree 1: unlimited depth (will overfit)
# Tree 2: max_depth=3 (regularized)
# ============================================================

# Unlimited depth — will memorize training data
tree_full = DecisionTreeClassifier(random_state=42)
tree_full.fit(X_train, y_train)

# Limited depth — more generalizable
tree_limited = DecisionTreeClassifier(max_depth=3, random_state=42)
tree_limited.fit(X_train, y_train)

# Compare training vs test accuracy
print("\n=== OVERFITTING DEMONSTRATION ===")
print(f"{'Model':<25} {'Train Accuracy':<18} {'Test Accuracy'}")
print("-" * 55)
for name, model in [("Unlimited depth", tree_full), ("max_depth=3", tree_limited)]:
    train_acc = accuracy_score(y_train, model.predict(X_train))
    test_acc = accuracy_score(y_test, model.predict(X_test))
    print(f"{name:<25} {train_acc:<18.2%} {test_acc:.2%}")

# Note: unlimited tree has perfect training accuracy but lower test accuracy
# max_depth=3 has slightly lower training accuracy but better generalization

# ============================================================
# STEP 4: READ THE TREE RULES
# This is the main advantage of decision trees — you can see every rule
# ============================================================

print("\n=== TREE RULES (max_depth=3) ===")
rules = export_text(tree_limited, feature_names=feature_names)
print(rules)

# The output shows exactly what the tree learned, e.g.:
# |--- petal length (cm) <= 2.45
# |   |--- class: setosa
# |--- petal length (cm) > 2.45
# |   |--- petal width (cm) <= 1.75
# |   |   |--- class: versicolor
# |   |--- petal width (cm) > 1.75
# |   |   |--- class: virginica

# ============================================================
# STEP 5: FEATURE IMPORTANCE
# Which features did the tree find most useful?
# ============================================================

importances = tree_limited.feature_importances_
print("\n=== FEATURE IMPORTANCE (max_depth=3) ===")
for name, importance in zip(feature_names, importances):
    bar = "=" * int(importance * 30)
    print(f"  {name:<25} {importance:.3f}  {bar}")

# ============================================================
# STEP 6: EVALUATE ON TEST SET
# ============================================================

y_pred = tree_limited.predict(X_test)
print("\n=== TEST SET EVALUATION (max_depth=3) ===")
print(f"Accuracy: {accuracy_score(y_test, y_pred):.2%}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=class_names))

# ============================================================
# STEP 7: TRACE A SINGLE PREDICTION — WHAT PATH DID IT TAKE?
# ============================================================

# Pick one test example and trace its path through the tree
example_idx = 0
example = X_test[example_idx:example_idx+1]
actual_class = class_names[y_test[example_idx]]
predicted_class = class_names[tree_limited.predict(example)[0]]

print(f"\n=== TRACING ONE PREDICTION ===")
print(f"Example features:")
for name, value in zip(feature_names, example[0]):
    print(f"  {name}: {value:.1f}")
print(f"Actual:    {actual_class}")
print(f"Predicted: {predicted_class}")

# Show the decision path (which nodes were visited)
node_indicator = tree_limited.decision_path(example)
leaf_id = tree_limited.apply(example)
node_ids = node_indicator.indices

print(f"\nDecision path (node IDs visited): {list(node_ids)}")
print("  → The tree visited these nodes to reach its prediction")

# ============================================================
# WHAT A PLOT WOULD SHOW (requires matplotlib)
# ============================================================
# import matplotlib.pyplot as plt
# plt.figure(figsize=(12, 6))
# plot_tree(tree_limited, feature_names=feature_names,
#           class_names=class_names, filled=True, rounded=True)
# plt.title("Decision Tree (max_depth=3) — Iris Classification")
# plt.tight_layout()
# plt.show()
#
# The plot shows:
# - Each box is a node with: the question being asked,
#   the Gini impurity, the number of training samples,
#   and the dominant class (shown by color intensity)
# - Blue boxes: setosa, orange: versicolor, green: virginica
# - Deeper boxes are smaller and purer (more confident)
```

---

## What This Shows

- **Overfitting is real and visible.** The unlimited tree gets 100% training accuracy but lower test accuracy. max_depth=3 has slightly lower training accuracy but generalizes better to new data.

- **export_text() prints the actual rules.** This is unique to decision trees — you can read every if/else condition the model learned. This is what makes them so valuable in domains that require explainability.

- **Feature importance** shows that petal length and petal width dominate. Sepal measurements barely matter. This is a real insight — the model found that petal features separate the species more cleanly.

- **No feature scaling needed.** Notice we did not call StandardScaler anywhere. Decision trees use rank-based splits — the scale of features does not affect which split is chosen.

- **decision_path()** traces the exact path one example took through the tree — useful for explaining individual predictions to end users.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concept |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [02 Logistic Regression](../02_Logistic_Regression/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 Random Forests](../04_Random_Forests/Theory.md)
