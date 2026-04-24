# Statistics — Interview Q&A

## Beginner Level

**Q1: What is the difference between mean, median, and mode?**

<details>
<summary>💡 Show Answer</summary>

Mean is the mathematical average — add all values and divide by the count. Median is the middle value when data is sorted — it ignores extreme values. Mode is the most frequently occurring value. Use mean for symmetric data, median when outliers exist, and mode for categorical data like "most popular color."

</details>

<br>

**Q2: What does standard deviation tell you?**

<details>
<summary>💡 Show Answer</summary>

Standard deviation measures how spread out the data points are around the mean. A small SD means data is tightly clustered near the mean. A large SD means data is scattered widely. For example, if the average test score is 75 with an SD of 5, most students scored between 70 and 80 — that's a tight, consistent class.

</details>

<br>

**Q3: Why is the median sometimes better than the mean?**

<details>
<summary>💡 Show Answer</summary>

Because the mean is sensitive to extreme outliers. If nine people earn $30,000 per year and one earns $10 million, the mean income is over $1 million — which doesn't represent anyone in the group. The median would be $30,000, which is far more representative. This is why statistics like household income almost always report medians.

</details>

---

## Intermediate Level

**Q4: What is variance and how is it different from standard deviation?**

<details>
<summary>💡 Show Answer</summary>

Variance is the average of the squared differences from the mean. Squaring means all distances are positive, but also means the units are squared (e.g., dollars²). Standard deviation is just the square root of variance, which brings it back to the original units. SD is more interpretable day-to-day, but variance is mathematically cleaner and often used inside formulas.

</details>

<br>

**Q5: What is the normal distribution and why does it matter in machine learning?**

<details>
<summary>💡 Show Answer</summary>

The normal distribution is a symmetric, bell-shaped distribution where most values cluster near the mean and values become rarer further away. It matters in ML because many algorithms assume normally distributed data — for example, linear regression assumes normally distributed errors. The 68-95-99.7 rule helps detect outliers, and normalization (standardizing features to mean=0, SD=1) is a common preprocessing step that assumes an approximately normal shape.

</details>

<br>

**Q6: What is the difference between population statistics and sample statistics?**

<details>
<summary>💡 Show Answer</summary>

Population statistics describe the entire group you care about. Sample statistics describe a subset you actually measured. In ML, you almost always work with samples — your training set is a sample of all possible data. This introduces sampling error: your sample mean may not equal the true population mean. Larger samples reduce this error, which is why "more data = better model" is generally true.

</details>

---

## Advanced Level

**Q7: What is the Central Limit Theorem and why is it foundational to ML?**

<details>
<summary>💡 Show Answer</summary>

The Central Limit Theorem states that if you take many random samples and calculate each sample's mean, those sample means will form a normal distribution — regardless of what the original data's distribution looked like. This is why normal distributions appear everywhere in statistics. In ML, it justifies using gradient estimates from mini-batches: the average gradient over a batch converges to the true gradient, and the distribution of those estimates becomes normal as batch sizes grow.

</details>

<br>

**Q8: What is covariance and correlation, and why do they matter for features in ML?**

<details>
<summary>💡 Show Answer</summary>

Covariance measures how two variables move together — positive covariance means they rise and fall together, negative means they move opposite. Correlation normalizes covariance to a -1 to +1 scale, making it easier to compare. In ML, highly correlated features are redundant — they give the model the same information twice, wasting capacity and sometimes causing instability. Feature selection and dimensionality reduction techniques like PCA are built on these concepts.

</details>

<br>

**Q9: What does it mean for a model's results to be "statistically significant"?**

<details>
<summary>💡 Show Answer</summary>

Statistical significance means the results are unlikely to have occurred by chance alone. We measure this using a p-value — if p < 0.05, there's less than a 5% chance the results are random noise. In ML evaluation, this matters when comparing models: if model A outperforms model B by 0.2% accuracy on one test set, is that real improvement or just luck? Proper statistical testing (t-tests, bootstrap confidence intervals) answers this and prevents teams from shipping "better" models that aren't actually better.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Intuition_First.md](./Intuition_First.md) | No-formula intuition primer |
| [📄 Mini_Exercise.md](./Mini_Exercise.md) | Practice exercises |

⬅️ **Prev:** [01 Probability](../01_Probability/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 Linear Algebra](../03_Linear_Algebra/Theory.md)
