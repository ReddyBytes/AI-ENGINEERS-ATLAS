# Classical ML Algorithms — Section Overview

## What Are Classical ML Algorithms?

Classical ML algorithms are the foundational, well-understood machine learning methods developed primarily between the 1950s and 2000s — before deep learning dominated. They include linear regression, logistic regression, decision trees, random forests, support vector machines, k-means clustering, PCA, and naive Bayes.

"Classical" does not mean outdated. These algorithms are still used every day in production systems across industry. They remain the first choice for many problems.

---

## When Classical ML Still Beats Deep Learning

| Situation | Why Classical ML Wins |
|---|---|
| **Small or medium datasets** (under ~50k rows) | Deep learning needs vast data to generalize — classical algorithms work well on limited data |
| **Tabular data** (spreadsheets, databases) | XGBoost/random forests consistently outperform neural nets on tabular data in benchmarks |
| **Interpretability required** | "The loan was denied because debt_to_income > 0.4" — you cannot say this with a neural net |
| **Fast training needed** | Training a random forest takes seconds; a neural network might need hours |
| **Limited compute** | Classical algorithms run on a laptop; deep learning often needs GPUs |
| **Regulated industries** | Healthcare, finance, and law often require explainable decisions |

---

## The 8 Algorithms in This Section

| # | Algorithm | Type | Best For |
|---|---|---|---|
| 01 | Linear Regression | Regression | Predicting continuous values |
| 02 | Logistic Regression | Classification | Probability-based binary classification |
| 03 | Decision Trees | Both | Interpretable rule-based decisions |
| 04 | Random Forests | Both | High accuracy on tabular data |
| 05 | Support Vector Machines | Classification | High-dimensional data, clear margin |
| 06 | K-Means Clustering | Clustering | Finding natural groups without labels |
| 07 | PCA | Dimensionality Reduction | Compressing features, visualization |
| 08 | Naive Bayes | Classification | Text classification, fast probabilistic inference |

---

## How to Navigate This Section

Each algorithm folder contains:

- **Theory.md** — Start here. Story-based explanation, core concepts, visual diagram.
- **Cheatsheet.md** — Quick reference: key terms, when to use, golden rules.
- **Interview_QA.md** — 9 questions across beginner/intermediate/advanced levels.
- **Math_Intuition.md** (selected algorithms) — The key math, explained intuitively without formulas as the focus.
- **Code_Example.md** — Working Python code with heavy comments.

**Recommended reading order:** Theory → Cheatsheet → Code Example → Interview Q&A

---

## The Algorithm Comparison

See `Algorithm_Comparison.md` in this folder for a side-by-side comparison of all 8 algorithms and a decision flowchart to help you pick the right one for your problem.

---

## Prerequisites

Before diving in, make sure you are comfortable with:
- What features and labels are (`02_Machine_Learning_Foundations/03_Supervised_Learning`)
- What training and evaluation mean (`02_Machine_Learning_Foundations/05_Model_Evaluation`)
- What overfitting is (`02_Machine_Learning_Foundations/06_Overfitting_and_Regularization`)

These concepts apply to all 8 algorithms in this section.
