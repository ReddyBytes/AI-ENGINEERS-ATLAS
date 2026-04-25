# 🏁 Project 1 — Recap

## What You Built

A Python data analysis pipeline that loads the Titanic dataset, computes descriptive statistics and probability distributions, and visualizes the results as histograms and bar charts.

---

## Concepts Applied

| Concept | Where You Used It | Why It Matters |
|---|---|---|
| Sample space | The full Titanic DataFrame (891 rows) | Every ML dataset is a sample space — the rows are outcomes |
| Marginal probability P(A) | `marginal_probability()` — count / total | Basis of all probability calculations |
| Conditional probability P(A\|B) | `conditional_probability()` — filter then count | How models learn feature-outcome relationships |
| Mean, variance, std deviation | `compute_statistics()` using numpy | Describe the center and spread of any distribution |
| Distribution shape | Histograms of Age and Fare | Skewed distributions affect model assumptions |
| Missing data | `dropna(subset=['Age'])` | Real datasets are never clean — handling NaN is mandatory |
| Pandas groupby | `df.groupby('Pclass')['Survived'].mean()` | Aggregate statistics by category — used everywhere in EDA |

---

## Extension Ideas

- Add joint probability P(A AND B) and verify P(A|B) = P(A AND B) / P(B) numerically — this is Bayes' theorem in action
- Compute the Pearson correlation coefficient between Age and Fare using `np.corrcoef()` and interpret what the value means
- Load the Iris dataset instead of Titanic and compute class-conditional distributions for each feature — this is exactly what a Naive Bayes classifier does internally

---

## Job Mapping

| Role | How This Shows Up Daily |
|---|---|
| Data Scientist | Exploratory data analysis (EDA) before every modeling project — computing distributions, checking for skew, spotting class imbalance |
| ML Engineer | Understanding data distributions is required before choosing normalization strategies and verifying preprocessing pipelines |
| Data Analyst | Conditional probability queries are the foundation of cohort analysis, funnel analysis, and A/B test interpretation |
| AI Engineer | Feature inspection and distribution checking before fine-tuning datasets or building RAG document collections |

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

➡️ **Next Project:** [02 — ML Model Comparison](../02_ML_Model_Comparison/01_MISSION.md)
