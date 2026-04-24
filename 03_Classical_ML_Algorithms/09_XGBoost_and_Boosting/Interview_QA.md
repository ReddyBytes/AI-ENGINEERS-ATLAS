# XGBoost and Gradient Boosting — Interview Q&A

---

## Beginner

**Q1: What is the difference between bagging (Random Forest) and boosting (XGBoost)?**

<details>
<summary>💡 Show Answer</summary>

Bagging builds trees in parallel on random subsamples of data, then averages their predictions. Each tree is independent — it doesn't know what the others predicted. This reduces variance. Boosting builds trees sequentially — each new tree specifically targets the errors made by all previous trees combined. The first tree makes predictions, the second tree predicts the residuals, the third tree predicts the remaining residuals, and so on. This reduces both bias and variance. Random Forest is safer on noisy data; XGBoost typically achieves higher accuracy on clean structured data.

</details>

---

**Q2: What is the learning rate in XGBoost and why does it matter?**

<details>
<summary>💡 Show Answer</summary>

The learning rate (also called shrinkage, parameter `eta`) scales the contribution of each new tree. A learning rate of 0.1 means each tree contributes only 10% of its full prediction — the remaining error is left for the next tree to fix. Lower learning rates require more trees but produce more robust models. This is because small steps prevent any single tree from dominating the ensemble, smoothing out noise. The standard practice is to use `early_stopping_rounds` to find the optimal number of trees, then optionally lower the learning rate and increase trees proportionally for a final performance boost.

</details>

---

**Q3: Why doesn't XGBoost require feature scaling?**

<details>
<summary>💡 Show Answer</summary>

XGBoost is a tree-based algorithm. Decision tree splits are based on thresholds — "is feature X greater than value V?" — not on the magnitude of features. Whether salary is measured in dollars (50000) or thousands of dollars (50), the threshold just changes, and the optimal split remains the same. Algorithms that are scale-sensitive are those that use distances (k-NN), dot products (SVM, linear models), or gradient descent where magnitude affects step sizes. Feature scaling provides zero benefit for XGBoost and can be safely skipped.

</details>

---

## Intermediate

**Q4: How does XGBoost handle missing values natively?**

<details>
<summary>💡 Show Answer</summary>

During training, when XGBoost encounters a missing value at a split node, it tries both directions (left branch and right branch) and assigns the missing value to whichever direction reduces loss more. This "default direction" is stored in the model. At inference, any missing value at that node is automatically routed using the learned direction. This is more principled than imputation — the model learns the statistically optimal handling of missingness, which may differ by feature and by node location. It also means you do not need to impute before training or inference.

</details>

---

**Q5: What is the difference between `weight`, `gain`, and `cover` feature importance in XGBoost, and which should you use?**

<details>
<summary>💡 Show Answer</summary>

- **Weight**: counts how many times a feature is used in splits across all trees. Biased toward high-cardinality features that get split often.
- **Gain**: average loss reduction per split using this feature. More meaningful than weight — a feature that reduces loss by a lot on each use is more important than one that's used frequently but adds little.
- **Cover**: average number of training samples affected per split. Measures how broadly a feature's splits apply.

For model interpretation, prefer `gain` over `weight`. For the most reliable importance estimates, use **permutation importance** (shuffle a feature and measure performance drop) or **SHAP values** (the gold standard — additive feature attributions for each prediction).

</details>

---

**Q6: How does early stopping work in XGBoost and why is it important?**

<details>
<summary>💡 Show Answer</summary>

Early stopping monitors a validation metric during training. When the metric stops improving for `early_stopping_rounds` consecutive iterations, training stops and the model state from the best iteration is retained. This is important because: (1) it automatically finds the optimal number of trees without manual tuning, (2) it prevents overfitting — more trees do not always improve generalization, and (3) it saves training time by stopping when adding more trees provides no benefit. Always provide an `eval_set` with a held-out validation set and set `early_stopping_rounds` to 50–100 in practice.

</details>

---

## Advanced

**Q7: Explain the XGBoost objective function and how regularization terms prevent overfitting.**

<details>
<summary>💡 Show Answer</summary>

XGBoost minimizes: `Obj = Σ L(yᵢ, ŷᵢ) + Σ Ω(fₖ)` where `Ω(fₖ) = γT + ½λ||w||²`. The loss term `L` measures prediction error. The regularization term `Ω` penalizes tree complexity: `γ` penalizes the number of leaves T (simpler trees preferred), and `λ` penalizes the L2 norm of leaf weights w (smaller leaf predictions preferred). Together these prevent trees from memorizing training noise. XGBoost uses a second-order Taylor expansion of the loss to analytically compute the optimal leaf weight and gain from splitting — this is what makes it faster and more accurate than standard gradient boosting.

</details>

---

**Q8: When would you choose LightGBM over XGBoost?**

<details>
<summary>💡 Show Answer</summary>

Choose LightGBM when: (1) dataset has millions of rows — LightGBM's leaf-wise growth is significantly faster on large data; (2) memory is constrained — LightGBM uses histogram-based approximation for splits, reducing memory; (3) training speed is critical — LightGBM is typically 10×+ faster than XGBoost on large datasets. Caution with LightGBM: leaf-wise growth can overfit on small datasets (< 10,000 rows) because it creates very deep, unbalanced trees. Set `min_child_samples` (minimum rows per leaf) to control this. XGBoost's level-wise growth is more conservative and usually safer as a default on small-to-medium datasets.

</details>

---

**Q9: How would you handle a severely imbalanced dataset (99% class 0, 1% class 1) with XGBoost?**

<details>
<summary>💡 Show Answer</summary>

Multiple strategies:
1. **`scale_pos_weight`**: set to `sum(negative) / sum(positive)` = 99. This tells XGBoost that each positive example is worth 99 negative examples. Equivalent to oversampling the minority class.
2. **Threshold tuning**: XGBoost outputs probabilities. The default 0.5 threshold is wrong for imbalanced data. Tune the threshold on validation data to maximize the metric that matters (F1, precision@k, etc.).
3. **Evaluation metric**: use `eval_metric="aucpr"` (area under precision-recall curve) instead of `auc` — PR-AUC is more informative for imbalanced classification.
4. **SMOTE + XGBoost**: apply SMOTE oversampling to training data before training.
5. **Class-weighted loss**: `scale_pos_weight` is usually sufficient and simpler than SMOTE for XGBoost.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concept |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |

⬅️ **Prev:** [Naive Bayes](../08_Naive_Bayes/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Time Series Analysis](../10_Time_Series_Analysis/Theory.md)
