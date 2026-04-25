# 📋 Project 1 — Build Guide

## Overview

Build in 5 stages. Each stage is self-contained — run and verify after every stage before moving to the next.

**Total estimated time:** 2–3 hours for core, 1–2 hours for extensions.

---

## Before You Start — Environment Setup

### Step 1: Create your project folder and virtual environment

```bash
mkdir -p ~/ai-projects/01_probability_explorer
cd ~/ai-projects/01_probability_explorer
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
pip install pandas numpy matplotlib
mkdir outputs
```

Copy `src/starter.py` into your project folder as `explorer.py`.

---

## Stage 1 — Load and Inspect the Data

**Goal:** Get the data loaded and understand its shape.

**Concept:** The dataset is your sample space — every row is one observation (one passenger). Understanding the shape and columns before doing any math is mandatory.

### Step 2: Load the CSV

<details><summary>💡 Hint</summary>

`pandas.read_csv()` accepts a URL directly — no need to download the file first.

```python
url = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"
df = pd.read_csv(url)
```

</details>

<details><summary>✅ Answer</summary>

```python
def load_data(url: str) -> pd.DataFrame:
    df = pd.read_csv(url)
    print(f"Dataset shape: {df.shape}")
    return df
```

</details>

### Step 3: Understand the key columns

| Column | Meaning |
|---|---|
| `Survived` | 1 = survived, 0 = died |
| `Pclass` | Ticket class: 1 = first, 2 = second, 3 = third |
| `Sex` | "male" or "female" |
| `Age` | Passenger age (some missing values!) |
| `Fare` | How much they paid for the ticket |

### Step 4: Clean the data

`Age` has missing values. For this project, drop rows where Age is missing.

<details><summary>💡 Hint</summary>

`df.dropna(subset=['Age'])` keeps only rows with a valid Age value.

</details>

<details><summary>✅ Answer</summary>

```python
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df_clean = df.dropna(subset=['Age'])
    print(f"After cleaning: {df_clean.shape[0]} rows remain")
    return df_clean
```

</details>

**Verify Stage 1:** Your script should print the shape `(891, 12)` and `714 rows remain` after cleaning.

---

## Stage 2 — Descriptive Statistics

**Goal:** Calculate mean, variance, and standard deviation for numeric columns.

**Concept:** These three numbers describe the center (mean) and spread (variance/std) of any distribution. Before a model can learn from data, it has to understand these fundamentals.

### Step 5: Implement `compute_statistics()`

The formulas:
- Mean: `sum(values) / n`
- Variance: `sum((x - mean)^2) / n`
- Standard deviation: `sqrt(variance)`

<details><summary>💡 Hint</summary>

`np.mean()`, `np.var()`, and `np.std()` all work on numpy arrays. Convert the DataFrame column to an array first with `.values`.

</details>

<details><summary>✅ Answer</summary>

```python
def compute_statistics(df, column):
    values = df[column].values
    mean     = np.mean(values)
    variance = np.var(values)
    std      = np.std(values)
    return {"mean": mean, "variance": variance, "std": std}
```

</details>

**Verify Stage 2:** Age mean should be approximately 29.70, std approximately 14.53.

---

## Stage 3 — Marginal Probabilities

**Goal:** Calculate the probability of each major outcome in the dataset.

**Concept:** Marginal probability P(A) is the simplest form — count how many times event A occurs and divide by the total number of outcomes.

### Step 6: Implement `marginal_probability()`

<details><summary>💡 Hint</summary>

`(df[column] == value).sum()` gives you the count of matching rows. Divide by `len(df)` to get the probability.

</details>

<details><summary>✅ Answer</summary>

```python
def marginal_probability(df, column, value):
    total = len(df)
    count = (df[column] == value).sum()
    return count / total
```

</details>

### Step 7: Call it for three events

```python
p_survived = marginal_probability(df, "Survived", 1)    # ~0.3838
p_female   = marginal_probability(df, "Sex", "female")  # ~0.3524
p_first    = marginal_probability(df, "Pclass", 1)      # ~0.2424
```

**Verify Stage 3:** P(Survived) should be approximately 0.38. If you get 0 or 1, check you are using the correct column.

---

## Stage 4 — Conditional Probabilities

**Goal:** Calculate P(A | B) — the probability of A given that B is true.

**Concept:** This is the core of Bayesian reasoning. The formula is `P(A | B) = P(A and B) / P(B)`. In pandas, the equivalent is: filter to rows where B is true, then calculate P(A) on that subset.

### Step 8: Implement `conditional_probability()`

<details><summary>💡 Hint</summary>

Two steps:
1. `subset = df[df[condition_col] == condition_val]` — filter the DataFrame
2. `(subset[target_col] == target_val).sum() / len(subset)` — calculate proportion

</details>

<details><summary>✅ Answer</summary>

```python
def conditional_probability(df, target_col, target_val, condition_col, condition_val):
    subset = df[df[condition_col] == condition_val]
    probability = (subset[target_col] == target_val).sum() / len(subset)
    return probability
```

</details>

### Step 9: Compare survival across classes and sexes

```python
# Expected results
# P(Survived | Pclass=1) ≈ 0.6296
# P(Survived | Pclass=3) ≈ 0.2424
# P(Survived | female)   ≈ 0.7420
# P(Survived | male)     ≈ 0.1889
```

**What story do the numbers tell?** First-class women had nearly a 97% survival rate. Third-class men had about 13%. This conditional structure is exactly what machine learning models will learn to capture.

---

## Stage 5 — Plotting Distributions

**Goal:** Visualize the distribution of Age and Fare as histograms.

**Concept:** A histogram shows you the shape of a distribution. Is it bell-shaped (normal)? Skewed right? Bimodal? The shape matters because many ML algorithms assume certain distribution shapes.

### Step 10: Implement `plot_histogram()`

<details><summary>💡 Hint</summary>

`plt.hist(df[column], bins=30, edgecolor='black', color='steelblue')` draws the histogram. Add `plt.title()`, `plt.xlabel()`, `plt.ylabel()` before saving.

</details>

<details><summary>✅ Answer</summary>

```python
def plot_histogram(df, column, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    plt.figure(figsize=(8, 5))
    plt.hist(df[column], bins=30, edgecolor='black', color='steelblue')
    plt.title(f'{column} Distribution — Titanic Passengers')
    plt.xlabel(column)
    plt.ylabel('Count')
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    filepath = os.path.join(output_dir, f"{column.lower()}_distribution.png")
    plt.savefig(filepath)
    plt.close()
```

</details>

### Step 11: Implement `plot_survival_by_class()`

<details><summary>💡 Hint</summary>

`df.groupby('Pclass')['Survived'].mean()` gives you the survival rate per class as a Series. Call `.plot(kind='bar')` on that Series.

</details>

<details><summary>✅ Answer</summary>

```python
def plot_survival_by_class(df, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    survival_by_class = df.groupby('Pclass')['Survived'].mean()
    plt.figure(figsize=(7, 5))
    survival_by_class.plot(kind='bar', color=['gold', 'silver', 'peru'], edgecolor='black')
    plt.title('Survival Rate by Passenger Class')
    plt.xlabel('Passenger Class')
    plt.ylabel('Survival Rate')
    plt.xticks(rotation=0)
    plt.ylim(0, 1)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "survival_by_class.png"))
    plt.close()
```

</details>

### Step 12: Run the full script

```bash
python explorer.py
```

Confirm:
- No errors in the terminal
- Statistics printed cleanly
- Two PNG files created in the `outputs/` folder
- The numbers match the expected output in `01_MISSION.md`

---

## Extension Challenges

### Extension 1 — Joint Probability

Calculate P(Survived AND Female) directly, then verify it equals P(Survived | Female) * P(Female):

<details><summary>💡 Hint</summary>

Use `&` to combine two boolean conditions: `(df['Survived'] == 1) & (df['Sex'] == 'female')`.

</details>

<details><summary>✅ Answer</summary>

```python
p_survived_and_female = ((df['Survived'] == 1) & (df['Sex'] == 'female')).sum() / len(df)
p_survived_given_female = df[df['Sex'] == 'female']['Survived'].mean()
p_female = (df['Sex'] == 'female').sum() / len(df)

print(f"Direct:   P(Survived AND Female) = {p_survived_and_female:.4f}")
print(f"Computed: P(Survived|Female) * P(Female) = {p_survived_given_female * p_female:.4f}")
# These should match!
```

</details>

### Extension 2 — Switch to Iris

Replace the Titanic dataset with the Iris dataset and compute class-conditional distributions for each feature.

```python
from sklearn.datasets import load_iris
iris = load_iris(as_frame=True)
df = iris.frame
```

### Extension 3 — Bayes' Theorem Verification

Pick two events A and B. Calculate P(A|B) using the filter method, then calculate it using Bayes' theorem: `P(A|B) = P(B|A) * P(A) / P(B)`. Verify they give the same answer.

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

➡️ **Next Project:** [02 — ML Model Comparison](../02_ML_Model_Comparison/01_MISSION.md)
