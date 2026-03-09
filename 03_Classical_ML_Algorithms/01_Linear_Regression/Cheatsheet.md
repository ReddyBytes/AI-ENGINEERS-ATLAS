# Linear Regression — Cheatsheet

**One-liner:** Linear regression finds the best-fit straight line through your data to predict a continuous numeric output.

---

## Key Terms

| Term | What It Means |
|---|---|
| **Slope (m)** | How much the output changes for each unit increase in the input |
| **Intercept (b)** | The predicted output when all inputs are zero |
| **Coefficients** | The m values for each feature in multiple linear regression |
| **MSE** | Mean Squared Error — the loss function minimized during training |
| **R² (R-squared)** | How much of the variance in the output is explained by the model (0=nothing, 1=perfect) |
| **Residual** | The difference between actual and predicted value for one example |
| **Multicollinearity** | When two or more features are highly correlated — destabilizes coefficients |
| **Regularized versions** | Ridge (L2), Lasso (L1) — add penalties to prevent overfitting |

---

## When to Use / Not Use

| Use Linear Regression When... | Avoid When... |
|---|---|
| Output is a continuous number | Output is a category (use logistic regression) |
| Relationship is roughly linear | Relationship is clearly non-linear (use tree models) |
| You need to know which features matter | Interpretability is not required |
| Dataset is small to medium | You have complex feature interactions |
| You need a fast baseline | Data has heavy outliers (try MAE-based regression) |

---

## Golden Rules

1. **Linear regression is your regression baseline.** Always start here before trying complex models.
2. **Check residuals.** If they have a pattern (not random), the relationship is non-linear — linear regression is the wrong tool.
3. **Scale your features.** Especially when comparing coefficients across features with different units.
4. **High R² on training data ≠ good model.** Check test R² and residual plots.
5. **Use Ridge or Lasso if you have many features.** Plain linear regression overfits with many features.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concept |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Math_Intuition.md](./Math_Intuition.md) | Math intuition behind the algorithm |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [10 Bias vs Variance](../../02_Machine_Learning_Foundations/10_Bias_vs_Variance/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [02 Logistic Regression](../02_Logistic_Regression/Theory.md)
