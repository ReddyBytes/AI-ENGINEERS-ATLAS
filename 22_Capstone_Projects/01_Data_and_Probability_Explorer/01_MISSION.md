# 🎯 Project 1 — Data & Probability Explorer

## The Story

Imagine you are a doctor trying to predict whether a patient will survive a surgery. You have a spreadsheet with hundreds of patients — their age, blood type, medical history — and whether they made it through. How do you turn that raw data into a number like "this patient has a 73% chance of survival"?

That number does not come from nowhere. It comes from probability — the mathematical language of uncertainty. Before any AI can make a prediction, it has to understand the distribution of its data. It has to know: what is typical? What is rare? What happens when two factors occur together?

This project builds that intuition from the ground up. You will load a real dataset, compute real probability distributions, and ask conditional questions like "given that a passenger was in first class, what is the probability they survived?" By the end, you will understand exactly what an AI sees when it looks at raw data — and that understanding is the bedrock of everything else in machine learning.

---

## What You Build

A Python script that:

1. Loads the Titanic CSV dataset using pandas
2. Computes descriptive statistics (mean, variance, standard deviation) for numeric columns
3. Plots histograms to visualize data distributions
4. Calculates marginal and conditional probabilities — P(Survived), P(Survived | Class=1)
5. Prints a clean summary report to the terminal

---

## Concepts Covered

| Phase | Topic | Concept Applied |
|---|---|---|
| Phase 2 | Probability (Topic 5) | Sample space, P(A), P(A\|B), independence |
| Phase 2 | Statistics (Topic 6) | Mean, variance, standard deviation, distributions |
| Phase 2 | Linear Algebra basics (Topic 7) | Vectors of features, matrix shape of a dataset |

---

## What Success Looks Like

When you run the completed script you will see:

```
=== Titanic Dataset — Probability Explorer ===

Dataset shape: (891, 12)

--- Descriptive Statistics ---
Age:    mean=29.70, variance=211.02, std=14.53
Fare:   mean=32.20, variance=2469.44, std=49.69

--- Marginal Probabilities ---
P(Survived)            = 0.3838
P(Female)              = 0.3524
P(Pclass=1)            = 0.2424

--- Conditional Probabilities ---
P(Survived | Pclass=1) = 0.6296
P(Survived | Pclass=3) = 0.2424
P(Survived | Female)   = 0.7420
P(Survived | Male)     = 0.1889

--- Histogram plots saved to: outputs/ ---
```

Plus 2–3 saved histogram images in an `outputs/` folder.

---

## Key Concepts to Lock In

- **Sample space**: the full Titanic dataset is your sample space — every row is one outcome
- **P(A)**: count the rows where A is true, divide by total rows
- **P(A | B)**: filter to rows where B is true first, then calculate P(A) on that subset
- **Mean/Variance**: numpy makes this easy, but understanding the formula matters
- **Distribution shape**: histograms reveal whether data is normal, skewed, or bimodal

---

## Prerequisites

- Python installed (3.9+)
- Basic Python knowledge: variables, loops, functions, print statements
- Libraries: `pandas`, `numpy`, `matplotlib` (install via pip)
- You have read or skimmed: Probability Theory, Statistics Theory from the Beginner Path

---

## Learning Format

**Tier:** Beginner — Easy  
**Estimated time:** 2–3 hours for the core version, 1–2 hours for optional extensions  
**Style:** Build in 5 self-contained stages. Run and verify after each stage.

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

➡️ **Next Project:** [02 — ML Model Comparison](../02_ML_Model_Comparison/01_MISSION.md)
