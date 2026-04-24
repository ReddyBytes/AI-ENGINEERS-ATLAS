# Feature Engineering — Interview Q&A

## Beginner Level

**Q1: What is feature engineering and why does it matter?**

<details>
<summary>💡 Show Answer</summary>

A: Feature engineering is the process of transforming raw data into features — the input variables a model will actually use for learning. It includes selecting which columns to use, creating new columns by combining or transforming existing ones, scaling numeric values to the same range, and encoding categorical variables as numbers. It matters because a model can only learn from what you give it. Even the best algorithm cannot find patterns in poorly prepared data. In practice, feature engineering often has more impact on model performance than choosing a more complex algorithm.

</details>

**Q2: What is one-hot encoding and when do you use it?**

<details>
<summary>💡 Show Answer</summary>

A: One-hot encoding converts a categorical variable into a set of binary columns — one for each unique category. For example, a "Color" column with values Red, Blue, Green becomes three columns: Color_Red, Color_Blue, Color_Green. Each row has a 1 in the column matching its category and 0s elsewhere. You use it for nominal categories — categories with no natural ordering, like colors, cities, or product types. You avoid it for ordinal categories (like Small/Medium/Large where order matters) and for very high-cardinality features (like country codes with 200 values) which would create too many columns.

</details>

**Q3: Why do you need to scale features and which models require it?**

<details>
<summary>💡 Show Answer</summary>

A: Many models use distance calculations or gradient descent, and both are sensitive to the scale of features. If one feature is house price (0–1,000,000) and another is number of bedrooms (1–10), the gradient descent optimization will be dominated by house price — it will make huge updates in that direction and tiny updates for bedrooms. Scaling brings both features to the same range so each has equal influence. Models that need scaling: KNN, SVM, logistic regression, neural networks, PCA. Models that do NOT need scaling: decision trees, random forests, XGBoost (they split on ranks, not distances).

</details>

---

## Intermediate Level

**Q4: What is the difference between normalization (min-max scaling) and standardization (z-score scaling)?**

<details>
<summary>💡 Show Answer</summary>

A: Min-max normalization rescales all values to a fixed range, typically [0, 1], using (x - min)/(max - min). It preserves the relative distances but is sensitive to outliers — one extreme value compresses all other values into a small range. Z-score standardization shifts features to have mean=0 and standard deviation=1, using (x - mean)/std. It handles outliers better because it is based on mean and standard deviation rather than the extreme values. Use min-max when you know the feature has a natural bounded range (e.g., pixel values 0–255). Use standardization as the default for most cases.

</details>

**Q5: What is feature leakage and how can it occur in feature engineering?**

<details>
<summary>💡 Show Answer</summary>

A: Feature leakage is when a feature contains information about the target that would not be available at prediction time in production. This causes the model to look great in testing but fail in deployment. In feature engineering it can occur in several ways: including future data in time-series features (e.g., using tomorrow's stock price to predict tomorrow's stock price), fitting a scaler or encoder on the combined train+test data (the test data influences the transformation), or creating a feature that is a direct proxy for the target. The fix: always fit all transformations only on training data, and rigorously audit features for any information they could not have at prediction time.

</details>

**Q6: How do you handle missing values in a feature engineering pipeline?**

<details>
<summary>💡 Show Answer</summary>

A: The approach depends on why values are missing. If missing completely at random (MCAR), simple imputation works: fill numeric columns with the mean or median, fill categorical columns with the mode. If the missingness is not random (MAR or MNAR), you should first create a binary "was_missing" indicator column before imputing — the fact that a value was missing might be predictive (e.g., a field left blank on a loan application might signal something). For high-missingness columns (>50% missing), consider dropping the column entirely. Never impute the test set using test set statistics — fit the imputer on training data and apply to test data.

</details>

---

## Advanced Level

**Q7: What are interaction features and when do they add value?**

<details>
<summary>💡 Show Answer</summary>

A: An interaction feature is a new feature created by combining two or more existing features. For example, multiplying age × income creates a feature that captures the combined effect of both. Linear models like logistic regression can only use features independently — they cannot discover that age and income together predict something that neither does alone. By explicitly creating the interaction term, you give the model the ability to use that combined signal. Tree-based models discover interactions automatically by splitting on multiple features sequentially. So interaction features matter most for linear models. For neural networks, the model can learn interactions through multiple layers. You should still create domain-informed interaction features when you know from expertise that two features combine in a meaningful way.

</details>

**Q8: How do you handle high-cardinality categorical features (e.g., a "city" column with 500 unique values)?**

<details>
<summary>💡 Show Answer</summary>

A: One-hot encoding 500 values creates 500 sparse columns — this causes memory issues, slow training, and the curse of dimensionality. Better approaches: target encoding (replace each category with the mean of the target variable for that category — effective but requires careful cross-validation to avoid leakage), frequency encoding (replace each category with how often it appears), binary encoding (convert category index to binary bits — 500 categories need only 9 columns), or embedding (for neural networks, learn a dense vector representation for each category as part of training). The best choice depends on dataset size, model type, and whether the categories have meaningful relationships.

</details>

**Q9: How do you approach feature engineering for a time-series prediction problem?**

<details>
<summary>💡 Show Answer</summary>

A: Time-series feature engineering requires careful attention to temporal order. You cannot use any information from the future. Common features include: lag features (the value at time t-1, t-2, t-7, etc.), rolling window statistics (7-day rolling mean, 30-day rolling max), time-based features (hour of day, day of week, month, is_holiday, days_since_event), and trend/seasonality decomposition components. You must use a time-aware train/test split — test data must come after all training data chronologically, never randomly shuffled. Lag features require careful handling of the "warm-up" period at the start of the series where not enough history exists. Standard cross-validation is invalid here — use rolling or expanding window cross-validation instead.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concept |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [06 Overfitting and Regularization](../06_Overfitting_and_Regularization/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [08 Gradient Descent](../08_Gradient_Descent/Theory.md)
