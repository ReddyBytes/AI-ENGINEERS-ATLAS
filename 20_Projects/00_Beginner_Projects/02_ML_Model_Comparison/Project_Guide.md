# Project 2 — ML Model Comparison

## The Story: Why This Project Matters

You've built your first probability explorer. Now someone asks you: "OK, so you have the Titanic data. Can you build something that *predicts* who survives?"

Here's the problem: there's no single "right" algorithm. There are dozens of ML models, and each one makes different assumptions about your data. A Decision Tree draws straight-line boundaries. Logistic Regression assumes the relationship is roughly linear. A Random Forest builds hundreds of trees and lets them vote.

Which one should you use? That question — "which model is best for this problem?" — is one of the most important questions in all of machine learning. And the answer is never obvious upfront.

This is why **model evaluation** exists. Every professional ML engineer does what you're about to do: train multiple models, compare them on the same test data, look at precision and recall, examine the confusion matrix, and *then* make a reasoned choice. You're not guessing — you're measuring.

This project teaches you the scientific method for machine learning.

---

## What You'll Build

A Python script that:

1. Loads the Iris dataset (4 features, 3 flower classes, 150 samples)
2. Splits the data into a training set and a test set
3. Trains 4 classifiers: Logistic Regression, Decision Tree, Random Forest, Naive Bayes
4. Evaluates each model using accuracy, precision, recall, and F1 score
5. Plots a confusion matrix for the best-performing model
6. Prints a comparison table and a recommendation

---

## Learning Objectives

By completing this project, you will be able to:

- Explain why you must split data into train and test sets
- Define accuracy, precision, recall, and F1 and know when each matters
- Describe what overfitting means and how to detect it with train vs. test scores
- Explain the bias-variance tradeoff in plain language
- Compare 4 classical ML algorithms and articulate their differences
- Read and interpret a confusion matrix

---

## Topics Covered

| Phase | Topic | Concept Applied |
|---|---|---|
| Phase 3 | Model Evaluation (Topic 9) | Accuracy, precision, recall, F1, confusion matrix |
| Phase 3 | Overfitting & Regularization (Topic 10) | Train vs. test score gap |
| Phase 3 | Loss Functions (Topic 11) | Cross-entropy (logistic regression loss) |
| Phase 3 | Bias vs. Variance (Topic 12) | Simple models vs. complex models |
| Phase 4 | Logistic Regression (Topic 14) | Linear classifier |
| Phase 4 | Decision Trees (Topic 15) | Rule-based splits |
| Phase 4 | Random Forests (Topic 16) | Ensemble of trees |
| Phase 4 | Naive Bayes (implicitly) | Probabilistic classifier |

---

## Prerequisites

- Completed Project 1 (or comfortable with pandas and numpy basics)
- Python 3.9+
- Libraries: `scikit-learn`, `matplotlib`, `pandas`, `numpy`
- You've read or skimmed: Model Evaluation, Overfitting, Logistic Regression, Decision Trees theories

---

## Difficulty

Easy-Medium — 3–4 hours for the core version. The concepts require careful reading; the code itself is short.

---

## Tools & Libraries

| Tool | Purpose |
|---|---|
| `scikit-learn` | All 4 classifiers, train/test split, metrics |
| `matplotlib` | Confusion matrix heatmap |
| `pandas` | Results comparison table |
| `numpy` | Array operations |

---

## Expected Output

```
=== ML Model Comparison — Iris Dataset ===

Dataset: 150 samples, 4 features, 3 classes
Train size: 120  |  Test size: 30

--- Model Comparison ---
Model                  Accuracy  Precision  Recall   F1
----------------------------------------------------------
Logistic Regression    0.9667    0.9683     0.9667   0.9667
Decision Tree          0.9333    0.9375     0.9333   0.9327
Random Forest          0.9667    0.9683     0.9667   0.9667
Naive Bayes            0.9667    0.9683     0.9667   0.9667

--- Train vs Test Accuracy (Overfitting Check) ---
Logistic Regression  train=0.9750  test=0.9667  gap=0.0083
Decision Tree        train=1.0000  test=0.9333  gap=0.0667  ← possible overfit
Random Forest        train=1.0000  test=0.9667  gap=0.0333
Naive Bayes          train=0.9583  test=0.9667  gap=-0.0083

--- Best Model: Logistic Regression ---
Confusion matrix saved to: outputs/confusion_matrix.png
```

---

## Key Learning: Concepts You'll Apply

- **Train/test split**: Never evaluate on the data you trained on — that's cheating
- **Accuracy vs. F1**: Accuracy is misleading on imbalanced datasets; F1 balances precision and recall
- **Overfitting**: A Decision Tree that memorizes training data scores 100% train, less on test
- **Ensemble methods**: Random Forest beats a single Decision Tree by averaging many trees
- **Bias-variance**: Simple models (Logistic Regression) have higher bias but often generalize better

---

## Extension Challenges

1. Add 5-fold cross-validation for each model using `cross_val_score()` and compare the mean CV score vs. the single test score
2. Try the Titanic dataset from Project 1 — you'll need to handle categorical features and missing values first
3. Add a learning curve plot (training score vs. dataset size) to visualize overfitting
4. Add a Random Forest with a limited `max_depth` and compare it to the unlimited version

---

## 📂 Navigation

| File | |
|---|---|
| **Project_Guide.md** | You are here — overview and objectives |
| [Step_by_Step.md](./Step_by_Step.md) | Detailed build instructions |
| [Starter_Code.md](./Starter_Code.md) | Python starter code with TODOs |
| [Architecture_Blueprint.md](./Architecture_Blueprint.md) | System diagram |

**Project Series:** Project 2 of 5 — Beginner Projects
⬅️ **Previous:** [01 — Data & Probability Explorer](../01_Data_and_Probability_Explorer/Project_Guide.md)
➡️ **Next:** [03 — Neural Net from Scratch](../03_Neural_Net_from_Scratch/Project_Guide.md)
