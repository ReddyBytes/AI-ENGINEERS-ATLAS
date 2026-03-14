# Project 2 — Architecture Blueprint

## System Overview

This project is a **model evaluation pipeline** — a systematic process for comparing multiple ML algorithms on the same problem. This pattern (train multiple models → evaluate with consistent metrics → pick the best → explain why) is standard practice in machine learning.

---

## System Diagram

```mermaid
flowchart TD
    A[Iris Dataset\n150 samples × 4 features] --> B[train_test_split\n80% train / 20% test]
    B --> C[X_train / y_train\n120 samples]
    B --> D[X_test / y_test\n30 samples]

    C --> E1[Logistic Regression\nmodel.fit]
    C --> E2[Decision Tree\nmodel.fit]
    C --> E3[Random Forest\nmodel.fit]
    C --> E4[Naive Bayes\nmodel.fit]

    E1 --> F[model.predict on X_test]
    E2 --> F
    E3 --> F
    E4 --> F

    D --> F

    F --> G1[Accuracy / Precision\nRecall / F1]
    F --> G2[Train vs Test Gap\nOverfitting Check]
    F --> G3[Confusion Matrix\nBest Model Only]

    G1 --> H[Comparison Table\nDataFrame printed to terminal]
    G2 --> H
    G3 --> I[outputs/confusion_matrix.png]
```

---

## Training vs Evaluation Flow

```mermaid
sequenceDiagram
    participant Data as Dataset
    participant Split as train_test_split
    participant Model as Each Model x4
    participant Metrics as Metrics Engine
    participant Report as Final Report

    Data->>Split: 150 samples
    Split->>Model: X_train (120 rows)
    Model->>Model: .fit() — learns parameters
    Split->>Metrics: X_test (30 rows)
    Model->>Metrics: .predict(X_test)
    Metrics->>Report: accuracy, precision, recall, F1
    Model->>Report: .score(X_train) for overfit check
```

---

## Component Table

| Component | Library/Tool | Role | Key Parameters |
|---|---|---|---|
| Dataset | `sklearn.datasets.load_iris` | Provides feature matrix X and labels y | n_samples=150, n_features=4, n_classes=3 |
| Train/Test Split | `sklearn.model_selection.train_test_split` | Splits data into train and test sets | test_size=0.2, stratify=y, random_state=42 |
| Logistic Regression | `sklearn.linear_model` | Linear classifier, learns decision boundary | max_iter=200 |
| Decision Tree | `sklearn.tree` | Rule-based tree of feature splits | No max_depth = can overfit |
| Random Forest | `sklearn.ensemble` | Ensemble of 100 decision trees | n_estimators=100 |
| Naive Bayes | `sklearn.naive_bayes.GaussianNB` | Probabilistic classifier using Bayes theorem | Assumes feature independence |
| Metrics Engine | `sklearn.metrics` | Computes accuracy, precision, recall, F1 | average='weighted' for multi-class |
| Confusion Matrix | `sklearn.metrics.ConfusionMatrixDisplay` | Visual breakdown of prediction errors | 3x3 matrix for 3 classes |
| Results Table | `pandas.DataFrame` | Stores and formats model comparison | One row per model |

---

## Model Comparison: What Each Model Does Internally

```mermaid
flowchart LR
    subgraph LogReg["Logistic Regression"]
        LR1[Find linear boundary\nthat separates classes]
        LR2[Uses sigmoid / softmax\nfor probability output]
    end

    subgraph DTree["Decision Tree"]
        DT1[Ask yes/no questions\nabout features]
        DT2[Split until pure\nor depth limit]
    end

    subgraph RF["Random Forest"]
        RF1[Build 100 trees\neach on random subset]
        RF2[Vote for final\nprediction]
    end

    subgraph NB["Naive Bayes"]
        NB1[Estimate P-feature given class\nfrom training data]
        NB2[Use Bayes theorem\nto pick most likely class]
    end
```

---

## Overfitting Visualization Concept

```mermaid
flowchart TD
    A[Model trains on X_train] --> B{How complex is the model?}
    B -- Simple: Logistic Regression --> C[High Bias\nMight miss patterns\nbut generalizes well]
    B -- Moderate: Random Forest --> D[Good Balance\nLow gap between train/test]
    B -- Complex: Decision Tree no limit --> E[Low Bias on Train\nHigh Variance on Test\n= Overfitting]
    C --> F[Small train-test gap]
    D --> F
    E --> G[Large train-test gap]
```

---

## Metrics Reference

| Metric | Formula | When it matters most |
|---|---|---|
| Accuracy | correct / total | Balanced datasets |
| Precision | TP / (TP + FP) | When false positives are costly (e.g., spam filter) |
| Recall | TP / (TP + FN) | When false negatives are costly (e.g., cancer detection) |
| F1 Score | 2 * (P * R) / (P + R) | Imbalanced classes or when both precision and recall matter |

---

## Folder Structure

```
02_ML_Model_Comparison/
├── compare_models.py          ← Your main Python script
├── outputs/
│   └── confusion_matrix.png
├── Project_Guide.md
├── Step_by_Step.md
├── Starter_Code.md
└── Architecture_Blueprint.md
```

---

## Concepts Map

```mermaid
flowchart TD
    T9[Topic 9 — Model Evaluation] --> C1[evaluate_model function\naccuracy, precision, recall, F1]
    T10[Topic 10 — Overfitting] --> C2[check_overfitting function\ntrain vs test gap]
    T11[Topic 11 — Loss Functions] --> C3[Logistic Regression minimizes\ncross-entropy loss internally]
    T12[Topic 12 — Bias vs Variance] --> C4[Decision Tree = low bias high variance\nLogistic = high bias low variance]
    T14[Topic 14-16 — Algorithms] --> C5[4 model implementations\nall using sklearn interface]
    C1 --> R[Final Comparison Table]
    C2 --> R
    C4 --> R
    C5 --> R
```

---

## 📂 Navigation

| File | |
|---|---|
| [Project_Guide.md](./Project_Guide.md) | Overview and objectives |
| [Step_by_Step.md](./Step_by_Step.md) | Detailed build instructions |
| [Starter_Code.md](./Starter_Code.md) | Python starter code with TODOs |
| **Architecture_Blueprint.md** | You are here |
