# Project 1 — Data & Probability Explorer

## The Story: Why This Project Matters

Imagine you're a doctor trying to predict whether a patient will survive a surgery. You have a spreadsheet with hundreds of patients — their age, blood type, medical history — and whether they made it through. How do you turn that raw data into a number like "this patient has a 73% chance of survival"?

That number doesn't come from nowhere. It comes from probability — the mathematical language of uncertainty. Before any AI can make a prediction, it has to understand the *distribution* of its data. It has to know: what's typical? What's rare? What happens when two factors occur together?

This project builds that intuition from the ground up. You'll load a real dataset, compute real probability distributions, and ask conditional questions like "given that a passenger was in first class, what's the probability they survived?" By the end, you'll understand exactly what an AI sees when it looks at raw data — and that understanding is the bedrock of everything else in machine learning.

---

## What You'll Build

A Python script that:

1. Loads the Titanic CSV dataset using pandas
2. Computes basic descriptive statistics (mean, variance, standard deviation) for numeric columns
3. Plots histograms to visualize data distributions
4. Calculates marginal and conditional probabilities (e.g., P(Survived), P(Survived | Class=1))
5. Prints a clean summary report to the terminal

---

## Learning Objectives

By completing this project, you will be able to:

- Load and inspect a real-world dataset with pandas
- Compute mean, variance, and standard deviation manually and verify with numpy
- Explain what a probability distribution is and plot one as a histogram
- Calculate conditional probability P(A | B) from a dataset
- Describe the difference between a sample and a population
- Interpret what a skewed distribution means for a model

---

## Topics Covered

| Phase | Topic | Concept Applied |
|---|---|---|
| Phase 2 | Probability (Topic 5) | Sample space, P(A), P(A\|B), independence |
| Phase 2 | Statistics (Topic 6) | Mean, variance, standard deviation, distributions |
| Phase 2 | Linear Algebra basics (Topic 7) | Vectors of features, matrix shape of a dataset |

---

## Prerequisites

- Python installed (3.9+)
- Basic Python knowledge: variables, loops, functions, print statements
- Libraries: `pandas`, `numpy`, `matplotlib` (install via pip)
- You've read or skimmed: Probability Theory, Statistics Theory from the Beginner Path

---

## Difficulty

Easy — 2–3 hours to complete the core version, optional extensions for 1–2 more hours.

---

## Tools & Libraries

| Tool | Purpose |
|---|---|
| `pandas` | Load CSV, filter rows, groupby operations |
| `numpy` | Compute statistics, array math |
| `matplotlib` | Plot histograms and bar charts |

---

## Expected Output

When you run the completed script, you will see:

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

## Key Learning: Concepts You'll Apply

- **Sample space**: the full Titanic dataset is your sample space — every row is one outcome
- **P(A)**: count the rows where A is true, divide by total rows
- **P(A | B)**: filter to rows where B is true first, then calculate P(A) on that subset
- **Mean/Variance**: numpy makes this easy, but understanding the formula matters
- **Distribution shape**: histograms reveal whether data is normal, skewed, or bimodal

---

## Extension Challenges

1. Add P(A and B) — joint probability — and verify P(A|B) = P(A and B) / P(B)
2. Compute the correlation coefficient between Age and Fare
3. Load the Iris dataset instead and compute class-conditional distributions for each feature
4. Add a bar chart comparing survival rates across all three passenger classes

---

## 📂 Navigation

| File | |
|---|---|
| **Project_Guide.md** | You are here — overview and objectives |
| [Step_by_Step.md](./Step_by_Step.md) | Detailed build instructions |
| [Starter_Code.md](./Starter_Code.md) | Python starter code with TODOs |
| [Architecture_Blueprint.md](./Architecture_Blueprint.md) | System diagram |

**Project Series:** Project 1 of 5 — Beginner Projects
➡️ **Next Project:** [02 — ML Model Comparison](../02_ML_Model_Comparison/Project_Guide.md)
