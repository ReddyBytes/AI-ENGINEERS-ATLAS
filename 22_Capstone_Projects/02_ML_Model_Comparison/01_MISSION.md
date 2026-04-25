# 🎯 Project 2 — ML Model Comparison

## The Story

You have built your first probability explorer. Now someone asks you: "OK, so you have the Titanic data. Can you build something that predicts who survives?"

Here is the problem: there is no single "right" algorithm. There are dozens of ML models, and each one makes different assumptions about your data. A Decision Tree draws straight-line boundaries. Logistic Regression assumes the relationship is roughly linear. A Random Forest builds hundreds of trees and lets them vote.

Which one should you use? That question — "which model is best for this problem?" — is one of the most important questions in all of machine learning. And the answer is never obvious upfront.

This is why model evaluation exists. Every professional ML engineer does what you are about to do: train multiple models, compare them on the same test data, look at precision and recall, examine the confusion matrix, and then make a reasoned choice. You are not guessing — you are measuring.

This project teaches you the scientific method for machine learning.

---

## What You Build

A Python script that:

1. Loads the Iris dataset (4 features, 3 flower classes, 150 samples)
2. Splits the data into a training set and a test set
3. Trains 4 classifiers: Logistic Regression, Decision Tree, Random Forest, Naive Bayes
4. Evaluates each model using accuracy, precision, recall, and F1 score
5. Plots a confusion matrix for the best-performing model
6. Prints a comparison table and a recommendation

---

## Concepts Covered

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

## What Success Looks Like

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
Decision Tree        train=1.0000  test=0.9333  gap=0.0667  ← possible overfit

--- Best Model: Logistic Regression ---
Confusion matrix saved to: outputs/confusion_matrix.png
```

---

## Key Concepts to Lock In

- **Train/test split**: Never evaluate on the data you trained on — that is cheating
- **Accuracy vs. F1**: Accuracy is misleading on imbalanced datasets; F1 balances precision and recall
- **Overfitting**: A Decision Tree that memorizes training data scores 100% train, less on test
- **Ensemble methods**: Random Forest beats a single Decision Tree by averaging many trees
- **Bias-variance**: Simple models (Logistic Regression) have higher bias but often generalize better

---

## Prerequisites

- Completed Project 1 (or comfortable with pandas and numpy basics)
- Python 3.9+
- Libraries: `scikit-learn`, `matplotlib`, `pandas`, `numpy`
- You have read or skimmed: Model Evaluation, Overfitting, Logistic Regression, Decision Trees theories

---

## Learning Format

**Tier:** Beginner — Easy-Medium  
**Estimated time:** 3–4 hours for the core version, 1–2 hours for extensions  
**Style:** Build in 6 stages. Each stage adds one new concept to the pipeline.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| 📄 **01_MISSION.md** | You are here |
| [📄 02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design and diagrams |
| [📄 03_GUIDE.md](./03_GUIDE.md) | Step-by-step build guide |
| [📄 src/starter.py](./src/starter.py) | Starter code with TODOs |
| [📄 04_RECAP.md](./04_RECAP.md) | Concepts recap and next steps |

⬅️ **Previous:** [01 — Data & Probability Explorer](../01_Data_and_Probability_Explorer/01_MISSION.md)
➡️ **Next:** [03 — Neural Net from Scratch](../03_Neural_Net_from_Scratch/01_MISSION.md)
