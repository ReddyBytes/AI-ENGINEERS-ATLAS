# Random Forests — Interview Q&A

## Beginner Level

**Q1: What is a random forest and how does it differ from a single decision tree?**

<details>
<summary>💡 Show Answer</summary>

A: A random forest is a collection of decision trees that work together. A single decision tree asks one series of questions to make a prediction. A random forest trains hundreds of trees — each on a different random sample of the training data and each considering a random subset of features at each split. For a new prediction, every tree makes its own prediction, and the forest takes a majority vote (classification) or average (regression). The result is far more accurate and robust than any single tree, because the individual trees' errors cancel each other out.

</details>

<br>

**Q2: What is bagging and why does it improve performance?**

<details>
<summary>💡 Show Answer</summary>

A: Bagging (Bootstrap Aggregating) trains each tree on a randomly sampled subset of the training data, drawn with replacement. This means some training examples appear multiple times in a given tree's training set, and some not at all. Each tree ends up with slightly different training data, so it learns slightly different patterns and makes different errors. When you average hundreds of trees with different errors, those individual errors cancel out. What remains is the consistent signal present across all trees. Bagging reduces variance without significantly increasing bias — the ensemble is more stable than any individual model.

</details>

<br>

**Q3: How does a random forest make predictions for classification vs regression?**

<details>
<summary>💡 Show Answer</summary>

A: For classification: each tree in the forest votes for a class label. The class with the most votes wins — this is the majority vote. If 70 out of 100 trees predict "spam" and 30 predict "not spam," the forest predicts "spam." For regression: each tree predicts a numeric value. The forest takes the average of all tree predictions. If 100 trees predict house prices ranging from $195,000 to $215,000, the forest might predict $205,000. The averaging smooths out individual tree variability.

</details>

---

## Intermediate Level

**Q4: What is the out-of-bag (OOB) score and how does it work?**

<details>
<summary>💡 Show Answer</summary>

A: When bagging trains each tree, about 37% of training examples are not selected for that tree's bootstrap sample. These "out-of-bag" examples can be used to evaluate each tree without a separate validation set — the tree never saw them during its training. The OOB score is computed by having each training example evaluated only by trees that did not train on it, then checking overall accuracy. This gives a nearly unbiased estimate of generalization performance for free, without consuming any validation data. It is equivalent to a rough cross-validation estimate. Set oob_score=True in sklearn to enable it.

</details>

<br>

**Q5: How does feature randomness (max_features) in random forests help reduce overfitting?**

<details>
<summary>💡 Show Answer</summary>

A: Without feature randomness, all trees would ask the same first question — the single most informative feature in the full dataset. This would create highly correlated trees that make the same mistakes. By limiting each split to a random subset of features (typically sqrt(n_features) for classification), trees are forced to find the best split using different combinations of features. This creates diverse trees with different strengths and blind spots. When diverse trees vote together, their uncorrelated errors cancel out much more effectively than correlated trees' errors would. Feature randomness is what makes random forests truly random and what separates them from simple bagged decision trees.

</details>

<br>

**Q6: What is feature importance in random forests and what are its limitations?**

<details>
<summary>💡 Show Answer</summary>

A: Random forest feature importance measures how much each feature contributed to reducing impurity (Gini or entropy) across all splits in all trees, weighted by the number of samples at each split. Features used frequently near roots of trees (large splits, high impurity reduction) get high importance. Limitations: it can be biased toward features with more unique values (continuous features and high-cardinality categoricals get inflated importance). Correlated features split their importance arbitrarily between them. It measures correlation with the target, not causation. For more reliable importance estimates, use permutation importance (measure performance drop when you randomly shuffle each feature) or SHAP values.

</details>

---

## Advanced Level

**Q7: How does a random forest compare to gradient boosting (XGBoost) and when would you choose one over the other?**

<details>
<summary>💡 Show Answer</summary>

A: Both are tree-based ensembles but work differently. Random forests train trees in parallel — each tree is independent. Gradient boosting trains trees sequentially — each tree corrects the errors of the previous ones. Gradient boosting typically achieves higher accuracy on tabular data because it directly optimizes for the residual errors. However, it is more prone to overfitting and requires more careful hyperparameter tuning (learning rate, n_estimators, max_depth). Random forests are more robust, easier to tune (n_estimators and max_depth are the main knobs), train faster in parallel, and work well out of the box. In practice: try random forest first for a reliable baseline; move to XGBoost or LightGBM when you need the extra accuracy and can afford the tuning time.

</details>

<br>

**Q8: What are SHAP values and how do they extend feature importance from random forests?**

<details>
<summary>💡 Show Answer</summary>

A: SHAP (SHapley Additive exPlanations) values provide per-prediction feature attributions rather than global averages. Based on game theory (Shapley values), SHAP calculates the marginal contribution of each feature for each specific prediction by considering all possible subsets of features. For a specific house price prediction, SHAP might say: "this prediction of $320,000 was driven by +$50,000 from location, +$30,000 from size, -$20,000 from age, and -$5,000 from condition." Standard random forest feature importance only gives global averages. SHAP values are more useful for explaining individual predictions and debugging model behavior. TreeSHAP is an efficient implementation specifically for tree-based models.

</details>

<br>

**Q9: How would you reduce the prediction latency of a random forest in a production system?**

<details>
<summary>💡 Show Answer</summary>

A: Several approaches. Reduce n_estimators: fewer trees mean fewer computation paths. Since accuracy typically plateaus after 100-200 trees, you can often cut to 50 trees with minimal accuracy loss. Limit tree depth: shallower trees evaluate faster. Use parallel inference: sklearn's predict already uses n_jobs for parallelism. Convert to a more efficient format: tools like treelite compile sklearn tree ensembles to optimized C code, giving 10-100x speedup. Model distillation: train a much simpler model (logistic regression, shallow neural network) to mimic the random forest's predictions on a large set of inputs — the simpler model is fast at inference. Consider alternative formats: ONNX or Core ML for mobile/edge deployment. For extremely latency-sensitive applications (sub-millisecond), linear models or small neural networks may be more appropriate than any tree ensemble.

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

⬅️ **Prev:** [03 Decision Trees](../03_Decision_Trees/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 SVM](../05_SVM/Theory.md)
