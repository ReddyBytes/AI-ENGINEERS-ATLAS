# 📋 Project 2 — Build Guide

## Overview

This project trains 4 classifiers on the same dataset and compares them systematically. You will build a reusable evaluation framework — the same pattern used by ML engineers in real projects.

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

Copy `src/starter.py` into your project folder as `compare_models.py`.

### Step 2: Understand the Iris dataset

The Iris dataset is the "Hello World" of machine learning:
- 150 samples (flowers)
- 4 features per sample: sepal length, sepal width, petal length, petal width
- 3 classes: Setosa, Versicolor, Virginica (50 samples each)
- Balanced — equal samples per class, which simplifies evaluation

---

## Stage 1 — Load Data and Split

**Goal:** Load the Iris dataset and split it into train/test sets.

**Concept:** The train/test split is the foundation of honest model evaluation. You train on one portion of the data and measure performance on a held-out portion the model has never seen. Without this split, you have no way to detect overfitting.

### Step 3: Implement `load_and_split()`

<details><summary>💡 Hint</summary>

`train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)` gives you 4 arrays: X_train, X_test, y_train, y_test.

`stratify=y` ensures each class appears in roughly equal proportion in both train and test sets.

</details>

<details><summary>✅ Answer</summary>

```python
def load_and_split(test_size=0.2, random_state=42):
    iris = load_iris()
    X, y = iris.data, iris.target
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size,
        random_state=random_state, stratify=y
    )
    return X_train, X_test, y_train, y_test, iris.target_names
```

</details>

**Verify Stage 1:** Train size should be 120, test size 30.

---

## Stage 2 — Train the 4 Models

**Goal:** Instantiate and train all 4 classifiers.

**Concept:** All 4 models share the same scikit-learn interface — `.fit(X_train, y_train)`. This is the training phase where the model adjusts its internal parameters to minimize its loss on the training data.

### Step 4: Understand each model

| Model | How it works | Strength | Weakness |
|---|---|---|---|
| Logistic Regression | Finds a linear boundary separating classes | Interpretable, fast | Struggles with non-linear data |
| Decision Tree | Recursively splits data by the best feature | Interpretable, non-linear | Prone to overfitting |
| Random Forest | Averages many decision trees | Robust, accurate | Slower, less interpretable |
| Naive Bayes | Assumes features are independent; uses Bayes theorem | Very fast, small data | Independence assumption often wrong |

### Step 5: Implement `get_models()`

<details><summary>💡 Hint</summary>

Use these classes from scikit-learn:
- `LogisticRegression(max_iter=200, random_state=42)`
- `DecisionTreeClassifier(random_state=42)`
- `RandomForestClassifier(n_estimators=100, random_state=42)`
- `GaussianNB()`

</details>

<details><summary>✅ Answer</summary>

```python
def get_models():
    return {
        "Logistic Regression": LogisticRegression(max_iter=200, random_state=42),
        "Decision Tree":        DecisionTreeClassifier(random_state=42),
        "Random Forest":        RandomForestClassifier(n_estimators=100, random_state=42),
        "Naive Bayes":          GaussianNB(),
    }
```

</details>

### Step 6: Implement `train_all_models()`

<details><summary>💡 Hint</summary>

Loop over the dictionary items. Call `model.fit(X_train, y_train)` for each model.

</details>

<details><summary>✅ Answer</summary>

```python
def train_all_models(models, X_train, y_train):
    for name, model in models.items():
        model.fit(X_train, y_train)
        print(f"Trained: {name}")
```

</details>

---

## Stage 3 — Evaluate Each Model

**Goal:** Compute accuracy, precision, recall, and F1 for each model.

**Concept:** These 4 metrics measure different things:
- **Accuracy**: overall correct predictions / total predictions
- **Precision**: when you predict positive, how often are you right?
- **Recall**: when the answer is positive, how often do you catch it?
- **F1**: harmonic mean of precision and recall — the balance between the two

For balanced datasets like Iris, accuracy and F1 will be similar. On imbalanced data, they diverge dramatically.

### Step 7: Implement `evaluate_model()`

<details><summary>💡 Hint</summary>

Call `model.predict(X_test)` to get predictions. Then call each of the 4 sklearn metric functions with `average='weighted'` (required for multi-class).

</details>

<details><summary>✅ Answer</summary>

```python
def evaluate_model(model, X_test, y_test):
    y_pred    = model.predict(X_test)
    accuracy  = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted')
    recall    = recall_score(y_test, y_pred, average='weighted')
    f1        = f1_score(y_test, y_pred, average='weighted')
    return {"Accuracy": accuracy, "Precision": precision, "Recall": recall, "F1": f1}
```

</details>

**Why `average='weighted'`?** Iris has 3 classes. Weighted averaging computes the metric for each class then averages them, weighted by class size.

**Verify Stage 3:** Logistic Regression F1 should be approximately 0.9667.

---

## Stage 4 — Detect Overfitting

**Goal:** Compare each model's train accuracy vs. test accuracy.

**Concept:** Overfitting is when a model memorizes the training data instead of learning the underlying pattern. It scores high on train data but poorly on test data. The gap between train and test accuracy is your overfitting signal.

### Step 8: Implement `check_overfitting()`

<details><summary>💡 Hint</summary>

`model.score(X_train, y_train)` returns train accuracy. `model.score(X_test, y_test)` returns test accuracy. Flag any model where the gap exceeds 0.05.

</details>

<details><summary>✅ Answer</summary>

```python
def check_overfitting(models, X_train, y_train, X_test, y_test):
    print("--- Train vs Test Accuracy (Overfitting Check) ---")
    for name, model in models.items():
        train_acc = model.score(X_train, y_train)
        test_acc  = model.score(X_test, y_test)
        gap  = train_acc - test_acc
        flag = " <- possible overfit!" if gap > 0.05 else ""
        print(f"{name:25s}  train={train_acc:.4f}  test={test_acc:.4f}  gap={gap:+.4f}{flag}")
```

</details>

**What to look for:** The Decision Tree will likely show a large gap — it has no regularization and memorizes training data. The Random Forest will show a smaller gap because averaging multiple trees reduces overfitting.

---

## Stage 5 — Confusion Matrix

**Goal:** Visualize the best model's predictions.

**Concept:** A confusion matrix shows you exactly where your model makes mistakes — not just how many mistakes. For Iris, you will see which flower species get confused with each other.

### Step 9: Implement `find_best_model()` and `plot_confusion_matrix()`

<details><summary>💡 Hint</summary>

For the best model: `df_results.loc[df_results['F1'].idxmax(), 'Model']`.

For the confusion matrix: call `model.predict(X_test)`, then `confusion_matrix(y_test, y_pred)`, then wrap it in `ConfusionMatrixDisplay`.

</details>

<details><summary>✅ Answer</summary>

```python
def find_best_model(df_results):
    return df_results.loc[df_results['F1'].idxmax(), 'Model']

def plot_confusion_matrix(model, X_test, y_test, class_names, model_name, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    y_pred = model.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)
    fig, ax = plt.subplots(figsize=(7, 6))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_names)
    disp.plot(ax=ax, cmap='Blues', colorbar=False)
    ax.set_title(f'Confusion Matrix — {model_name}')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "confusion_matrix.png"))
    plt.close()
```

</details>

**Reading the matrix:** Rows are actual class, columns are predicted class. A perfect model has all values on the diagonal. Setosa is almost always classified perfectly; Versicolor and Virginica sometimes get confused.

---

## Stage 6 — Print the Final Report

### Step 10: Run everything

```bash
python compare_models.py
```

Confirm:
- 4 models trained and evaluated
- Comparison table printed
- Overfitting check printed with Decision Tree flagged
- `outputs/confusion_matrix.png` created

---

## Extension Challenges

### Extension 1 — Cross-Validation

Instead of a single train/test split, use 5-fold cross-validation:

<details><summary>💡 Hint</summary>

`cross_val_score(model, X, y, cv=5, scoring='f1_weighted')` returns 5 scores — one per fold. Take the mean and standard deviation.

</details>

<details><summary>✅ Answer</summary>

```python
from sklearn.model_selection import cross_val_score

for name, model in models.items():
    scores = cross_val_score(model, X, y, cv=5, scoring='f1_weighted')
    print(f"{name}: CV F1 = {scores.mean():.4f} (+/- {scores.std():.4f})")
```

</details>

### Extension 2 — Use the Titanic Dataset

The Titanic dataset requires more preprocessing (missing values, categorical columns). Try it after completing this project and see how much harder real data is.

### Extension 3 — Tune the Decision Tree

Add `max_depth=3` to limit the tree and reduce overfitting:

```python
"Decision Tree (depth=3)": DecisionTreeClassifier(max_depth=3, random_state=42)
```

Compare its train/test gap before and after.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 01_MISSION.md](./01_MISSION.md) | Context and objectives |
| [📄 02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design and diagrams |
| 📄 **03_GUIDE.md** | You are here |
| [📄 src/starter.py](./src/starter.py) | Starter code with TODOs |
| [📄 04_RECAP.md](./04_RECAP.md) | Concepts recap and next steps |

⬅️ **Previous:** [01 — Data & Probability Explorer](../01_Data_and_Probability_Explorer/01_MISSION.md)
➡️ **Next:** [03 — Neural Net from Scratch](../03_Neural_Net_from_Scratch/01_MISSION.md)
