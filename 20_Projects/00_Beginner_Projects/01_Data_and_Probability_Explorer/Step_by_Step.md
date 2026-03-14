# Project 1 — Step-by-Step Build Guide

## Overview

You'll build this project in 5 stages. Each stage is self-contained — you can run and test after every stage before moving to the next.

**Total estimated time:** 2–3 hours for core, 1–2 hours for extensions.

---

## Before You Start — Environment Setup

### Step 1: Create your project folder and virtual environment

Open your terminal and run:

```bash
mkdir -p ~/ai-projects/01_probability_explorer
cd ~/ai-projects/01_probability_explorer
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
pip install pandas numpy matplotlib
```

**Concept applied:** This is your development environment — a clean Python sandbox where all your dependencies are isolated.

### Step 2: Download the Titanic dataset

Option A — Download from the internet in your script (easiest):

```python
# pandas can read CSVs directly from a URL
url = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"
df = pd.read_csv(url)
```

Option B — Download manually from [Kaggle Titanic](https://www.kaggle.com/c/titanic/data) or any public source and save as `titanic.csv` in your project folder.

### Step 3: Create your output folder

```bash
mkdir outputs
```

### Step 4: Copy the starter code

Copy the code from `Starter_Code.md` into a file called `explorer.py` in your project folder.

---

## Stage 1 — Load and Inspect the Data

**Goal:** Get the data loaded and understand its shape.

**Concept applied:** The dataset is your **sample space** — every row is one observation (one passenger). Understanding the shape and columns before doing any math is mandatory.

### Step 5: Load the CSV

```python
import pandas as pd
df = pd.read_csv("https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv")
```

### Step 6: Inspect the data

Run these in Python to understand what you have:

```python
print(df.shape)        # (rows, columns)
print(df.columns)      # Column names
print(df.head())       # First 5 rows
print(df.dtypes)       # Data types of each column
print(df.isnull().sum()) # Count missing values per column
```

### Step 7: Understand the key columns

| Column | Meaning |
|---|---|
| `Survived` | 1 = survived, 0 = died |
| `Pclass` | Ticket class: 1 = first, 2 = second, 3 = third |
| `Sex` | "male" or "female" |
| `Age` | Passenger age (some missing values!) |
| `Fare` | How much they paid for the ticket |

**What to notice:** `Age` has missing values. For this project, drop rows where Age is missing using `df.dropna(subset=['Age'])`. In a real ML pipeline you'd impute (fill in) missing values — that's a topic for Project 2.

### Step 8: Verify Stage 1

Your script should print the shape and first 5 rows without errors. If you see `(891, 12)`, you're on track.

---

## Stage 2 — Descriptive Statistics

**Goal:** Calculate mean, variance, and standard deviation for numeric columns.

**Concept applied:** These are the three most fundamental **statistics**. Before any model can learn from data, it needs to understand the center (mean) and spread (variance/std) of the distribution.

### Step 9: Compute statistics manually for Age

The formulas are:
- Mean: `sum(values) / n`
- Variance: `sum((x - mean)^2) / n`
- Standard deviation: `sqrt(variance)`

```python
import numpy as np

ages = df['Age'].dropna().values   # Convert to numpy array

mean_age = np.mean(ages)
var_age = np.var(ages)
std_age = np.std(ages)

print(f"Age: mean={mean_age:.2f}, variance={var_age:.2f}, std={std_age:.2f}")
```

### Step 10: Verify with pandas

```python
print(df['Age'].describe())
```

The `mean` in the pandas output should match your numpy calculation exactly.

### Step 11: What do these numbers tell you?

- A high standard deviation means the data is **spread out** — passengers had very different ages
- A low variance means most values are **clustered** around the mean
- In ML, features with very different scales (Age: 0–80 vs Fare: 0–500) need to be normalized before training

---

## Stage 3 — Marginal Probabilities

**Goal:** Calculate the probability of each major outcome in the dataset.

**Concept applied:** **Marginal probability** P(A) is the simplest form — you count how many times event A occurs and divide by the total number of outcomes. This is the foundation of all probabilistic reasoning.

### Step 12: Calculate P(Survived)

```python
total = len(df)
survived = df['Survived'].sum()   # Sum works because 1=survived, 0=died

p_survived = survived / total
print(f"P(Survived) = {p_survived:.4f}")
```

### Step 13: Calculate P(Female) and P(Pclass=1)

```python
p_female = (df['Sex'] == 'female').sum() / total
p_first_class = (df['Pclass'] == 1).sum() / total

print(f"P(Female) = {p_female:.4f}")
print(f"P(Pclass=1) = {p_first_class:.4f}")
```

### Step 14: Sanity check

P(Survived) should be approximately 0.38. If you're getting 0 or 1, check whether you've loaded the right column.

---

## Stage 4 — Conditional Probabilities

**Goal:** Calculate P(A | B) — the probability of A given that B is true.

**Concept applied:** This is the core of Bayesian reasoning and is used everywhere in ML — from Naive Bayes classifiers to evaluating model performance by subgroup. The formula is:

```
P(A | B) = P(A and B) / P(B)
```

In pandas, the equivalent is: filter to rows where B is true, then calculate P(A) on that subset.

### Step 15: P(Survived | Pclass = 1)

```python
# Filter to first class passengers only
first_class = df[df['Pclass'] == 1]

# Calculate survival rate within that group
p_survived_given_first = first_class['Survived'].mean()
print(f"P(Survived | Pclass=1) = {p_survived_given_first:.4f}")
```

Why `.mean()` works: since Survived is 0 or 1, the average equals the proportion that survived.

### Step 16: Compare survival by class and by sex

```python
for pclass in [1, 2, 3]:
    subset = df[df['Pclass'] == pclass]
    p = subset['Survived'].mean()
    print(f"P(Survived | Pclass={pclass}) = {p:.4f}")

for sex in ['female', 'male']:
    subset = df[df['Sex'] == sex]
    p = subset['Survived'].mean()
    print(f"P(Survived | Sex={sex}) = {p:.4f}")
```

### Step 17: What story do the numbers tell?

The conditional probabilities reveal dramatic differences. First-class women had nearly a 97% survival rate. Third-class men had about 13%. This is what machine learning models will learn to capture — these conditional relationships between features and outcomes.

---

## Stage 5 — Plotting Distributions

**Goal:** Visualize the distribution of Age and Fare as histograms.

**Concept applied:** A histogram shows you the **shape** of a distribution. Is it bell-shaped (normal)? Skewed right? Bimodal? The shape matters because many ML algorithms assume certain distribution shapes.

### Step 18: Plot Age distribution

```python
import matplotlib.pyplot as plt
import os

os.makedirs("outputs", exist_ok=True)

plt.figure(figsize=(8, 5))
plt.hist(df['Age'].dropna(), bins=30, edgecolor='black', color='steelblue')
plt.title('Age Distribution — Titanic Passengers')
plt.xlabel('Age')
plt.ylabel('Count')
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig("outputs/age_distribution.png")
plt.close()
print("Saved: outputs/age_distribution.png")
```

### Step 19: Plot survival rates by class as a bar chart

```python
survival_by_class = df.groupby('Pclass')['Survived'].mean()

plt.figure(figsize=(7, 5))
survival_by_class.plot(kind='bar', color=['gold', 'silver', 'peru'], edgecolor='black')
plt.title('Survival Rate by Passenger Class')
plt.xlabel('Passenger Class')
plt.ylabel('Survival Rate')
plt.xticks(rotation=0)
plt.ylim(0, 1)
plt.tight_layout()
plt.savefig("outputs/survival_by_class.png")
plt.close()
print("Saved: outputs/survival_by_class.png")
```

### Step 20: Run the full script

Run `python explorer.py` and confirm:
- No errors in the terminal
- Statistics printed cleanly
- Two PNG files created in the `outputs/` folder
- The numbers match the expected output in Project_Guide.md

---

## Extend the Project

Once the core is working, try these challenges:

### Extension 1 — Joint Probability

Calculate P(Survived AND Female) directly, then verify it equals P(Survived | Female) * P(Female):

```python
p_survived_and_female = ((df['Survived'] == 1) & (df['Sex'] == 'female')).sum() / len(df)
p_survived_given_female = df[df['Sex'] == 'female']['Survived'].mean()
p_female = (df['Sex'] == 'female').sum() / len(df)

print(f"Direct:   P(Survived AND Female) = {p_survived_and_female:.4f}")
print(f"Computed: P(Survived|Female) * P(Female) = {p_survived_given_female * p_female:.4f}")
# These should match!
```

### Extension 2 — Switch to Iris

Replace the Titanic dataset with the Iris dataset. Iris has 4 numeric features and 3 classes. Plot the distribution of each feature for each class and see how they separate.

```python
from sklearn.datasets import load_iris
iris = load_iris(as_frame=True)
df = iris.frame
```

### Extension 3 — Bayes' Theorem verification

Pick two events A and B. Calculate P(A|B) using the filter method, then calculate it using Bayes' theorem: P(A|B) = P(B|A) * P(A) / P(B). Verify they give the same answer.

---

## 📂 Navigation

| File | |
|---|---|
| [Project_Guide.md](./Project_Guide.md) | Overview and objectives |
| **Step_by_Step.md** | You are here |
| [Starter_Code.md](./Starter_Code.md) | Python starter code with TODOs |
| [Architecture_Blueprint.md](./Architecture_Blueprint.md) | System diagram |
