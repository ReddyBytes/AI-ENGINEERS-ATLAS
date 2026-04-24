# Logistic Regression — Interview Q&A

## Beginner Level

**Q1: Why is logistic regression used for classification even though it has "regression" in the name?**

<details>
<summary>💡 Show Answer</summary>

A: The name is historical. Logistic regression models the log-odds of the target class using a linear combination of features — that linear relationship is the "regression" part. But the output is passed through the sigmoid function, which converts it to a probability between 0 and 1. You then apply a threshold (typically 0.5) to get a class label. The output is a classification decision. It is called logistic regression because the underlying model is linear (like linear regression) but the output is a probability via the logistic/sigmoid function.

</details>

**Q2: What is the sigmoid function and why is it essential to logistic regression?**

<details>
<summary>💡 Show Answer</summary>

A: The sigmoid function is sigmoid(z) = 1 / (1 + e^(-z)). It maps any real number to the range (0, 1). It is essential because logistic regression's linear equation can produce any value from negative infinity to positive infinity. Raw values of -10 or +20 cannot be interpreted as probabilities. The sigmoid squishes every possible value into a valid probability. A large positive input gives a probability near 1. A large negative input gives a probability near 0. An input near 0 gives 0.5. This conversion is what makes the linear model's output interpretable as a classification probability.

</details>

**Q3: What is the decision boundary in logistic regression?**

<details>
<summary>💡 Show Answer</summary>

A: The decision boundary is the set of input values where the model outputs exactly 0.5 probability — it is the line (or plane) that separates the two classes. When the sigmoid output equals 0.5, the input to the sigmoid (z) equals 0. So the decision boundary is where the linear equation z = w₁x₁ + w₂x₂ + b = 0. In 2D feature space, this is a straight line. In higher dimensions, it is a hyperplane. This boundary is always linear — which means logistic regression cannot separate classes that require a curved boundary without feature engineering.

</details>

---

## Intermediate Level

**Q4: How do you interpret the coefficients of a logistic regression model?**

<details>
<summary>💡 Show Answer</summary>

A: The coefficients directly control the log-odds. For a coefficient w₁ associated with feature x₁: a unit increase in x₁ changes the log-odds by w₁, which means it multiplies the odds by e^(w₁). For example: if heart_rate has coefficient 0.05, each 1 bpm increase in heart rate multiplies the odds of "emergency" by e^0.05 ≈ 1.05 — a 5% increase in odds. Large positive coefficients mean the feature strongly predicts class 1. Large negative coefficients predict class 0. This interpretability makes logistic regression valuable in regulated contexts — you can explain which factors drove a decision.

</details>

**Q5: What happens when you change the decision threshold from 0.5? When would you do this?**

<details>
<summary>💡 Show Answer</summary>

A: Lowering the threshold (e.g., to 0.3) makes the model more sensitive — it predicts class 1 for more examples, increasing recall but decreasing precision. Raising the threshold (e.g., to 0.7) makes it more conservative — fewer class 1 predictions, higher precision but lower recall. You would lower the threshold when missing real positives is costly: in a cancer screening test, you want to catch almost all real cancer cases even at the cost of more false alarms. You would raise the threshold when false alarms are costly: in a spam filter, you would rather let some spam through than block legitimate emails. The optimal threshold depends on the relative cost of false positives vs false negatives in your specific application.

</details>

**Q6: How does logistic regression handle multi-class classification?**

<details>
<summary>💡 Show Answer</summary>

A: Standard logistic regression is binary. For multiple classes, there are two main extensions. One-vs-Rest (OvR): train one binary logistic regression for each class against all others (e.g., "is this class A vs not-A?"). The class with the highest probability wins. Multinomial (softmax) logistic regression: extends directly to multiple classes by replacing sigmoid with softmax, which outputs a probability distribution across all classes simultaneously. sklearn's LogisticRegression supports both with the multi_class parameter. Softmax is generally preferred for multi-class problems because it models all classes jointly, leading to better-calibrated probabilities.

</details>

---

## Advanced Level

**Q7: What is the relationship between logistic regression and maximum likelihood estimation?**

<details>
<summary>💡 Show Answer</summary>

A: Logistic regression training via minimizing cross-entropy loss is mathematically equivalent to maximum likelihood estimation (MLE). The MLE objective asks: what weights maximize the probability of observing the actual labels given the training features? For binary labels with sigmoid outputs, this probability is ŷᵢ for each positive example and (1-ŷᵢ) for each negative example. Maximizing the log of this joint probability gives exactly the negative cross-entropy loss. So when you minimize cross-entropy, you are finding the weights that make the observed data most likely under the model. This gives logistic regression strong theoretical grounding — the learned probabilities are calibrated in a statistically meaningful way.

</details>

**Q8: How do you deal with class imbalance in logistic regression?**

<details>
<summary>💡 Show Answer</summary>

A: Several approaches work. Class weights: sklearn supports class_weight='balanced' which automatically adjusts the loss to weight minority class errors more heavily — effectively tells the optimizer to care more about getting minority examples right. Threshold adjustment: after training, lower the decision threshold to increase recall on the minority class. Resampling: oversample the minority class (SMOTE) or undersample the majority class before training. Choosing the right evaluation metric: use F1, precision-recall AUC, or Matthews Correlation Coefficient instead of accuracy. In practice, class_weight='balanced' combined with threshold tuning on a validation set is the most straightforward approach.

</details>

**Q9: When would logistic regression outperform a random forest?**

<details>
<summary>💡 Show Answer</summary>

A: Several scenarios favor logistic regression over random forests. Small datasets: with limited data, simpler models generalize better — random forests can overfit on small samples. Linearly separable data: if the true decision boundary is linear, logistic regression captures it perfectly while a random forest uses a jagged approximation. Interpretability requirements: logistic regression gives direct coefficient-based explanations; random forests are much harder to explain. Fast training/inference requirements: logistic regression trains in milliseconds and predictions are simple matrix multiplication; random forests require evaluating many trees. Calibrated probabilities needed: logistic regression outputs well-calibrated probabilities by design; random forests require separate calibration. When feature engineering can capture the non-linearity, logistic regression with engineered features can match random forest performance while remaining interpretable.

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

⬅️ **Prev:** [01 Linear Regression](../01_Linear_Regression/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 Decision Trees](../03_Decision_Trees/Theory.md)
