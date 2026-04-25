# 🏁 Project 2 — Recap

## What You Built

A model evaluation pipeline that trains 4 classifiers on the Iris dataset, compares them using accuracy, precision, recall, and F1, detects overfitting via train/test score gaps, and visualizes the best model's predictions as a confusion matrix.

---

## Concepts Applied

| Concept | Where You Used It | Why It Matters |
|---|---|---|
| Train/test split | `train_test_split()` with stratify=y | Prevents data leakage and enables honest evaluation |
| Accuracy | `accuracy_score()` | Simple correctness measure — valid for balanced datasets |
| Precision | `precision_score(average='weighted')` | Measures cost of false positives |
| Recall | `recall_score(average='weighted')` | Measures cost of false negatives |
| F1 score | `f1_score(average='weighted')` | Harmonic mean — best single metric for multi-class |
| Overfitting | Train vs. test accuracy gap | Decision Tree shows gap ≥ 0.06 — a memorization signal |
| Bias-variance tradeoff | Logistic Regression vs. Decision Tree | Simpler models generalize better despite lower train scores |
| Confusion matrix | `ConfusionMatrixDisplay` | Shows exactly which classes get confused with each other |
| Ensemble methods | Random Forest vs. single Decision Tree | Averaging 100 trees reduces variance and narrows the train/test gap |

---

## Extension Ideas

- Add 5-fold cross-validation with `cross_val_score()` and compare mean CV F1 to single-split F1 — the difference tells you how much your single split was luck
- Apply `max_depth=3` to the Decision Tree, retrain, and measure whether the train/test gap shrinks — this directly demonstrates regularization through depth limiting
- Run the full pipeline on the Titanic dataset from Project 1 and experience firsthand why real-world data (missing values, categorical columns) requires preprocessing before any model can see it

---

## Job Mapping

| Role | How This Shows Up Daily |
|---|---|
| ML Engineer | Runs model comparison experiments before committing to a production model — same pattern, bigger datasets |
| Data Scientist | Builds evaluation frameworks, interprets confusion matrices, decides which metric to optimize based on business cost of false positives vs. false negatives |
| AI Engineer | Evaluates fine-tuned model checkpoints using precision/recall/F1 to choose the best checkpoint before deployment |
| MLOps Engineer | Automates this pipeline — train → evaluate → compare → promote — as part of CI/CD for ML systems |

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 01_MISSION.md](./01_MISSION.md) | Context and objectives |
| [📄 02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design and diagrams |
| [📄 03_GUIDE.md](./03_GUIDE.md) | Step-by-step build guide |
| [📄 src/starter.py](./src/starter.py) | Starter code with TODOs |
| 📄 **04_RECAP.md** | You are here |

⬅️ **Previous:** [01 — Data & Probability Explorer](../01_Data_and_Probability_Explorer/01_MISSION.md)
➡️ **Next:** [03 — Neural Net from Scratch](../03_Neural_Net_from_Scratch/01_MISSION.md)
