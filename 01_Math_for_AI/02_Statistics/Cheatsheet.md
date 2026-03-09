# Statistics — Cheatsheet

**One-liner:** Statistics turns a pile of raw numbers into meaningful summaries — where the center is, how spread out the data is, and what shape it takes.

---

## Key Terms

| Term | Definition | Formula |
|---|---|---|
| **Mean** | The average — sum divided by count | (x₁ + x₂ + ... + xₙ) / n |
| **Median** | The middle value when sorted | Middle value (or avg of two middle) |
| **Mode** | The value that appears most often | Most frequent value |
| **Variance** | Average squared distance from the mean | avg of (xᵢ - mean)² |
| **Standard Deviation (SD)** | Square root of variance — spread in original units | √Variance |
| **Normal Distribution** | Bell-shaped distribution centered at the mean | ~68% within 1 SD |
| **Outlier** | A data point unusually far from the mean | Typically > 3 SDs away |
| **Percentile** | What % of data falls below a value | 90th percentile = top 10% |

---

## When to Use Each Measure

| Situation | Use This |
|---|---|
| Symmetric data, no outliers | Mean |
| Data has extreme outliers (income, prices) | Median |
| Categorical data ("what's most popular?") | Mode |
| Measuring spread for ML feature scaling | Standard Deviation |
| Comparing how consistent two datasets are | Coefficient of Variation |

---

## The 68-95-99.7 Rule (Normal Distribution)

```
Within 1 SD of mean:  ~68% of data
Within 2 SDs of mean: ~95% of data
Within 3 SDs of mean: ~99.7% of data
```

---

## When to Use / Not Use

| Use statistics when... | Don't assume... |
|---|---|
| Summarizing large datasets | Mean always represents a "typical" value |
| Checking data quality before training | Normal distribution without checking |
| Evaluating ML model performance | Correlation means causation |
| Scaling/normalizing features | Higher SD is always bad |

---

## Golden Rules

1. Always look at mean AND median together — if they differ a lot, you have outliers or skew.
2. Standard deviation is the most useful single number for understanding spread.
3. More data = better statistical estimates. Small samples lie often.
4. Normal distribution is assumed by many ML algorithms — check this assumption.
5. Variance is additive. Standard deviation is not. (SD of combined data ≠ SD1 + SD2)
6. In ML, always normalize features: subtract mean, divide by SD. This stops large-valued features from dominating.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Intuition_First.md](./Intuition_First.md) | No-formula intuition primer |
| [📄 Mini_Exercise.md](./Mini_Exercise.md) | Practice exercises |

⬅️ **Prev:** [01 Probability](../01_Probability/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 Linear Algebra](../03_Linear_Algebra/Theory.md)
