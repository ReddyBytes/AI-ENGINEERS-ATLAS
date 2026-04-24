# Linear Regression — Interview Q&A

## Beginner Level

**Q1: What is linear regression and what type of problem does it solve?**

<details>
<summary>💡 Show Answer</summary>

A: Linear regression is a supervised learning algorithm that predicts a continuous numeric output. It models the relationship between input features and the output as a straight line (or hyperplane). Given labeled training data (input-output pairs), it finds the line that minimizes the total prediction error — measured by MSE. Once trained, you give it new inputs and it reads off the predicted value from the line. It solves regression problems: predicting house prices, estimating travel times, forecasting sales, predicting temperatures.

</details>

**Q2: What is MSE and why does linear regression use it as the loss function?**

<details>
<summary>💡 Show Answer</summary>

A: MSE (Mean Squared Error) is the average of squared differences between predicted and actual values: (1/n)×Σ(prediction - actual)². Linear regression uses it because: (1) squaring makes all errors positive so they do not cancel out; (2) it penalizes large errors more than small ones; (3) it is mathematically smooth and differentiable, which means gradient descent can navigate it cleanly. For linear regression specifically, MSE gives a convex loss surface — a perfect bowl shape with exactly one minimum, so gradient descent will always find the global optimum.

</details>

**Q3: What does R² (R-squared) tell you and what is a "good" value?**

<details>
<summary>💡 Show Answer</summary>

A: R² measures the proportion of variance in the output that is explained by the model. R²=1 means perfect predictions — the model explains all the variance. R²=0 means the model does no better than predicting the average every time. R²=0.7 means the model explains 70% of the variance. What is "good" depends on the domain: in physical sciences R²=0.99 might be expected; in social sciences predicting human behavior R²=0.3 might be considered good. Always check R² on the test set, not just training data — a model can have R²=0.95 on training and R²=0.2 on test, indicating overfitting.

</details>

---

## Intermediate Level

**Q4: What are the assumptions of linear regression and what happens when they are violated?**

<details>
<summary>💡 Show Answer</summary>

A: The key assumptions are: linearity (the true relationship is linear), independence (observations are not correlated with each other), homoscedasticity (the variance of errors is constant across all inputs), and normality of residuals (for statistical inference). Violating linearity means predictions are systematically biased — adding polynomial features or using a non-linear model fixes this. Violating independence (e.g., time-series data where consecutive points are correlated) invalidates standard error estimates — use time-series specific methods. Violating homoscedasticity (errors grow with input size) can be addressed with log-transforming the output. Normality only matters for computing confidence intervals — for prediction purposes, violations are less critical.

</details>

**Q5: What is multicollinearity and how does it affect linear regression?**

<details>
<summary>💡 Show Answer</summary>

A: Multicollinearity occurs when two or more features are highly correlated with each other. For example, including both "house size in sqft" and "house size in m²" — they carry identical information. The effect: the coefficient estimates become unstable and unreliable. A small change in the data can cause large swings in coefficient values. The model's predictions can still be good, but the individual coefficients cannot be interpreted as "the effect of this feature." Detection: calculate Variance Inflation Factor (VIF) for each feature. Fix: remove one of the correlated features, or use Ridge regression which handles multicollinearity by shrinking correlated coefficients together.

</details>

**Q6: What is Ridge regression (L2) and Lasso regression (L1)? When do you use each?**

<details>
<summary>💡 Show Answer</summary>

A: Both are regularized versions of linear regression that add a penalty to the loss function to prevent overfitting. Ridge adds λ×Σ(weights²) — it shrinks all weights toward zero but never to exactly zero. Lasso adds λ×Σ|weights| — it can drive some weights to exactly zero, performing automatic feature selection. Use Ridge when you believe most features are relevant but need to handle multicollinearity and mild overfitting. Use Lasso when you have many features and believe only a few are truly important — it will zero out the irrelevant ones. ElasticNet combines both penalties and is a good default when you are unsure.

</details>

---

## Advanced Level

**Q7: What is the normal equation for linear regression and when would you use it instead of gradient descent?**

<details>
<summary>💡 Show Answer</summary>

A: The normal equation gives the exact optimal weights in closed form: θ = (XᵀX)⁻¹Xᵀy. Unlike gradient descent, it does not iterate — it computes the answer directly. For small to medium datasets (under ~10,000 examples and under ~1,000 features) the normal equation is faster than running gradient descent for many epochs. The problem is computational cost: inverting XᵀX is O(n³) where n is the number of features. For large feature counts this becomes prohibitively slow. Gradient descent scales much better to large datasets and many features. sklearn uses the normal equation (or a close variant) under the hood for small problems.

</details>

**Q8: How would you handle a non-linear relationship using linear regression?**

<details>
<summary>💡 Show Answer</summary>

A: Linear regression can capture non-linear relationships through feature engineering. Polynomial features: add x², x³ as separate features — the model remains "linear in parameters" but can fit curves. Log transformation: if the relationship follows y ≈ log(x), transform the feature. Interaction terms: add x₁×x₂ as a feature to capture joint effects. Binning: convert a continuous feature into categorical bins. The key is that "linear" in linear regression refers to linear in the parameters (coefficients), not in the input features — you can transform inputs freely. For complex non-linearities, it is usually cleaner to switch to tree-based models or neural networks rather than adding many polynomial features.

</details>

**Q9: How would you evaluate two linear regression models and decide which is better?**

<details>
<summary>💡 Show Answer</summary>

A: Use multiple metrics on the test set, not just R². Check MSE and RMSE (root MSE, which is in the same units as the target) to understand the magnitude of typical errors in concrete terms. Check MAE for a more robust sense of typical error (less influenced by outliers). Compare R² — the model explaining more variance is generally better. Also check residual plots: plot predicted values vs residuals. A good model's residuals should look like random noise — no pattern. If residuals show a curve, the model is missing a non-linear relationship. If they fan out as predicted values increase, there is heteroscedasticity. If a model has higher R² but worse residual behavior, it may be overfitting or violating assumptions.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concept |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Math_Intuition.md](./Math_Intuition.md) | Math intuition behind the algorithm |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [10 Bias vs Variance](../../02_Machine_Learning_Foundations/10_Bias_vs_Variance/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [02 Logistic Regression](../02_Logistic_Regression/Theory.md)
