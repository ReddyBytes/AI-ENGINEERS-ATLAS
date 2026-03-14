# Project 2 — Step-by-Step Build Guide

## Overview

This project trains 4 classifiers on the same dataset and compares them systematically. You'll build a reusable evaluation framework — the same pattern used by ML engineers in real projects.

**Total estimated time:** 3–4 hours for core, 1–2 hours for extensions.

---

## Before You Start — Environment Setup

### Step 1: Set up your environment

```bash
mkdir -p ~/ai-projects/02_ml_comparison
cd ~/ai-projects/02_ml_comparison
python -m venv venv
source venv/bin/activate
pip install scikit-learn matplotlib pandas numpy
mkdir outputs
```

### Step 2: Understand the Iris dataset

The Iris dataset is the "Hello World" of machine learning. It has:
- 150 samples (flowers)
- 4 features per sample: sepal length, sepal width, petal length, petal width
- 3 classes: Setosa, Versicolor, Virginica (50 samples each)

It's **balanced** — equal samples per class — which simplifies evaluation.

```python
from sklearn.datasets import load_iris
iris = load_iris()
print(iris.feature_names)   # ['sepal length (cm)', 'sepal width (cm)', ...]
print(iris.target_names)    # ['setosa', 'versicolor', 'virginica']
print(iris.data.shape)      # (150, 4)
```

---

## Stage 1 — Load Data and Split

**Goal:** Load the Iris dataset and split it into train/test sets.

**Concept applied:** The train/test split is the foundation of honest model evaluation. You train on one portion of the data and measure performance on a held-out portion the model has never seen. Without this split, you have no way to detect overfitting.

### Step 3: Load the dataset

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

iris = load_iris()
X = iris.data      # Feature matrix: shape (150, 4)
y = iris.target    # Labels: 0, 1, or 2
```

### Step 4: Split into train and test

```python
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,       # 20% for testing = 30 samples
    random_state=42,     # Fixed seed for reproducibility
    stratify=y           # Keep class proportions equal in both sets
)
print(f"Train size: {len(X_train)}  |  Test size: {len(X_test)}")
```

**Why `stratify=y`?** Without it, the random split might put all of one class into the test set. With stratify, each class has roughly equal representation in both sets.

**Why `random_state=42`?** Makes your results reproducible. Anyone running your code will get the same split.

---

## Stage 2 — Train the 4 Models

**Goal:** Train Logistic Regression, Decision Tree, Random Forest, and Naive Bayes.

**Concept applied:** All 4 models share the same scikit-learn interface: `.fit(X_train, y_train)`. This is the **training phase** — the model adjusts its internal parameters to minimize its loss on the training data.

### Step 5: Understand each model briefly

| Model | How it works | Strength | Weakness |
|---|---|---|---|
| Logistic Regression | Finds a linear boundary separating classes | Interpretable, fast | Struggles with non-linear data |
| Decision Tree | Recursively splits data by the best feature | Interpretable, non-linear | Prone to overfitting |
| Random Forest | Averages many decision trees | Robust, accurate | Slower, less interpretable |
| Naive Bayes | Assumes features are independent; uses Bayes theorem | Very fast, works with small data | Independence assumption often wrong |

### Step 6: Import and instantiate the models

```python
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB

models = {
    "Logistic Regression": LogisticRegression(max_iter=200, random_state=42),
    "Decision Tree":        DecisionTreeClassifier(random_state=42),
    "Random Forest":        RandomForestClassifier(n_estimators=100, random_state=42),
    "Naive Bayes":          GaussianNB(),
}
```

### Step 7: Train each model

```python
for name, model in models.items():
    model.fit(X_train, y_train)
    print(f"Trained: {name}")
```

All 4 models are now trained. The `.fit()` call is where all the learning happens.

---

## Stage 3 — Evaluate Each Model

**Goal:** Compute accuracy, precision, recall, and F1 for each model.

**Concept applied:** These 4 metrics measure different things:
- **Accuracy**: overall correct predictions / total predictions
- **Precision**: when you predict positive, how often are you right?
- **Recall**: when the answer is positive, how often do you catch it?
- **F1**: harmonic mean of precision and recall — the balance between the two

For balanced datasets like Iris, accuracy and F1 will be similar. On imbalanced data, they diverge dramatically.

### Step 8: Compute metrics for one model

```python
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

model = models["Logistic Regression"]
y_pred = model.predict(X_test)

accuracy  = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average='weighted')
recall    = recall_score(y_test, y_pred, average='weighted')
f1        = f1_score(y_test, y_pred, average='weighted')

print(f"Accuracy={accuracy:.4f}, Precision={precision:.4f}, Recall={recall:.4f}, F1={f1:.4f}")
```

**Why `average='weighted'`?** Iris has 3 classes. Weighted averaging computes the metric for each class then averages them, weighting by class size.

### Step 9: Loop over all models and collect results

```python
import pandas as pd

results = []
for name, model in models.items():
    y_pred = model.predict(X_test)
    results.append({
        "Model": name,
        "Accuracy":  accuracy_score(y_test, y_pred),
        "Precision": precision_score(y_test, y_pred, average='weighted'),
        "Recall":    recall_score(y_test, y_pred, average='weighted'),
        "F1":        f1_score(y_test, y_pred, average='weighted'),
    })

df_results = pd.DataFrame(results)
print(df_results.to_string(index=False))
```

---

## Stage 4 — Detect Overfitting

**Goal:** Compare each model's train accuracy vs. test accuracy.

**Concept applied:** **Overfitting** is when a model memorizes the training data instead of learning the underlying pattern. It scores high on train data but poorly on test data. The gap between train and test accuracy is your overfitting signal.

### Step 10: Calculate the train-test gap

```python
print("\n--- Train vs Test Accuracy (Overfitting Check) ---")
for name, model in models.items():
    train_acc = model.score(X_train, y_train)
    test_acc  = model.score(X_test, y_test)
    gap = train_acc - test_acc
    flag = " <- possible overfit!" if gap > 0.05 else ""
    print(f"{name:25s}  train={train_acc:.4f}  test={test_acc:.4f}  gap={gap:.4f}{flag}")
```

**What to look for:** The Decision Tree will likely show a gap — it has no regularization and will memorize training data. The Random Forest will have a smaller gap because averaging multiple trees reduces overfitting.

---

## Stage 5 — Confusion Matrix

**Goal:** Visualize the best model's predictions with a confusion matrix.

**Concept applied:** A confusion matrix shows you *exactly* where your model makes mistakes — not just *how many* mistakes. For Iris, you'll see which flower species get confused with each other.

### Step 11: Find the best model by F1

```python
best_model_name = df_results.loc[df_results['F1'].idxmax(), 'Model']
best_model = models[best_model_name]
print(f"\nBest model by F1: {best_model_name}")
```

### Step 12: Plot the confusion matrix

```python
import matplotlib.pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix
import numpy as np

y_pred_best = best_model.predict(X_test)
cm = confusion_matrix(y_test, y_pred_best)

fig, ax = plt.subplots(figsize=(7, 6))
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=iris.target_names)
disp.plot(ax=ax, cmap='Blues', colorbar=False)
ax.set_title(f'Confusion Matrix — {best_model_name}')
plt.tight_layout()
plt.savefig("outputs/confusion_matrix.png")
plt.close()
print("Confusion matrix saved to: outputs/confusion_matrix.png")
```

### Step 13: Read the confusion matrix

The rows are the **actual** class. The columns are the **predicted** class. A perfect model has all values on the diagonal (zero off-diagonal entries).

Common errors on Iris: Versicolor and Virginica sometimes get confused because their petal sizes overlap. Setosa is almost always classified perfectly.

---

## Stage 6 — Print the Final Report

### Step 14: Print a clean comparison

```python
print("\n=== Final Model Comparison ===")
print(df_results.round(4).to_string(index=False))
print(f"\nRecommendation: Use {best_model_name}")
print("Reason: Highest F1 score, no significant overfitting detected.")
```

### Step 15: Run everything

```bash
python compare_models.py
```

Confirm:
- 4 models trained and evaluated
- Comparison table printed
- Overfitting check printed
- `outputs/confusion_matrix.png` created

---

## Extend the Project

### Extension 1 — Cross-Validation

Instead of a single train/test split, use 5-fold cross-validation:

```python
from sklearn.model_selection import cross_val_score

for name, model in models.items():
    scores = cross_val_score(model, X, y, cv=5, scoring='f1_weighted')
    print(f"{name}: CV F1 = {scores.mean():.4f} (+/- {scores.std():.4f})")
```

This gives you a more reliable estimate by testing on 5 different subsets.

### Extension 2 — Use the Titanic Dataset

The Titanic dataset requires more preprocessing (handle missing values, encode categorical columns). Try it after completing this project and see how much harder real data is.

### Extension 3 — Tune the Decision Tree

Add `max_depth=3` to limit the tree and reduce overfitting. Compare its train/test gap before and after.

---

## 📂 Navigation

| File | |
|---|---|
| [Project_Guide.md](./Project_Guide.md) | Overview and objectives |
| **Step_by_Step.md** | You are here |
| [Starter_Code.md](./Starter_Code.md) | Python starter code with TODOs |
| [Architecture_Blueprint.md](./Architecture_Blueprint.md) | System diagram |
