# Bias vs Variance — Interview Q&A

## Beginner Level

**Q1: What is the bias-variance tradeoff in machine learning?**

<details>
<summary>💡 Show Answer</summary>

A: The bias-variance tradeoff is the tension between two sources of model error. Bias is the error from a model that is too simple — it makes wrong assumptions and consistently misses the true pattern. Variance is the error from a model that is too sensitive to training data — it memorizes noise and performs differently on different datasets. Reducing one tends to increase the other: making a model more complex reduces bias but increases variance; simplifying a model reduces variance but increases bias. The goal is to find the complexity level where both are acceptably low.

</details>

<br>

**Q2: How do you tell whether your model is suffering from high bias or high variance?**

<details>
<summary>💡 Show Answer</summary>

A: Look at training performance versus test performance. If training accuracy is low and test accuracy is also low — the model fails everywhere — that is high bias. The model is too simple to learn the patterns at all. If training accuracy is high but test accuracy is significantly lower — the model nails training data but struggles on new data — that is high variance. The model has memorized the training set. The gap between training and test performance is the key diagnostic: a large gap signals overfitting (variance); both being poor signals underfitting (bias).

</details>

<br>

**Q3: Why does adding more training data help with variance but not bias?**

<details>
<summary>💡 Show Answer</summary>

A: Variance comes from overfitting to a specific, limited training set. More diverse data makes it harder for the model to memorize specifics — it must generalize. More data reduces variance. Bias, however, comes from the model being fundamentally too simple to represent the true pattern. Even with infinite data, a linear model cannot learn a non-linear relationship — the architecture itself is the constraint. More data cannot fix the wrong choice of model. You need a more expressive model to reduce bias.

</details>

---

## Intermediate Level

**Q4: How does regularization address the bias-variance tradeoff?**

<details>
<summary>💡 Show Answer</summary>

A: Regularization reduces variance by constraining the model — penalizing large weights or limiting complexity. This prevents the model from fitting noise in the training data too precisely, making predictions more stable across different training sets. The cost is a slight increase in bias — the model is now more constrained and may not perfectly fit even the training patterns. Done well, the gain in variance reduction outweighs the small increase in bias, and total error decreases. The regularization strength parameter controls this tradeoff directly: stronger regularization = more bias, less variance.

</details>

<br>

**Q5: How do ensemble methods like random forests reduce variance?**

<details>
<summary>💡 Show Answer</summary>

A: Random forests train many different decision trees, each on a different random sample of the data and a random subset of features. Each individual tree has low bias but high variance — it overfits its particular training subset. When you average predictions across 100 diverse trees, the individual trees' errors cancel each other out. The ensemble prediction is much more stable than any individual tree's prediction. This is the bias-variance insight behind bagging: each model has high variance, but combining diverse models averages away that variance while keeping bias low. Boosting works differently — it reduces bias by sequentially correcting errors, at the cost of some variance.

</details>

<br>

**Q6: What is the mathematical decomposition of prediction error?**

<details>
<summary>💡 Show Answer</summary>

A: The expected prediction error for any model decomposes into three terms: Bias² + Variance + Irreducible Noise. Bias squared is the squared difference between the model's expected prediction and the true value — how systematically wrong is the model on average? Variance is how much the model's prediction varies across different training sets — how sensitive is the model to which training data it saw? Irreducible noise is the inherent randomness in the true relationship between inputs and outputs — even a perfect model cannot eliminate this. The key insight: only bias and variance are in your control. Minimizing total error means finding the right balance between the two.

</details>

---

## Advanced Level

**Q7: How does the bias-variance tradeoff apply differently to deep learning versus classical ML?**

<details>
<summary>💡 Show Answer</summary>

A: Classical ML has a clear bias-variance curve: add complexity, bias decreases then variance increases, and there is an obvious optimal complexity. In deep learning, an interesting phenomenon called "double descent" occurs: as model size increases past a certain threshold, test error decreases again despite the model clearly overfitting. Very large overparameterized neural networks can achieve near-zero training loss while also generalizing well — defying the classical tradeoff. Theoretically, this is explained by implicit regularization from SGD and the geometry of overparameterized spaces. Practically, it means the classical recipe (find the sweet spot, avoid over-parameterization) does not always apply to modern deep learning — sometimes bigger is better, especially with proper regularization.

</details>

<br>

**Q8: How do you use learning curves to diagnose bias vs variance problems?**

<details>
<summary>💡 Show Answer</summary>

A: Learning curves plot training and validation error as a function of training set size. High bias pattern: both training error and validation error converge to a high value. Even with more data, both curves plateau high — the model cannot improve because its architecture is the bottleneck. High variance pattern: training error is low; validation error is high, but the gap decreases as you add more data. More data helps — both curves move toward convergence. If you see high bias, add model complexity or better features. If you see high variance with decreasing gap, collect more data. If you see high variance with a stable gap (no convergence), you need regularization or a simpler model — more data will not help enough.

</details>

<br>

**Q9: How does the bias-variance tradeoff relate to the choice of k in k-fold cross-validation?**

<details>
<summary>💡 Show Answer</summary>

A: The choice of k in cross-validation involves a bias-variance tradeoff at the level of the evaluation process itself. Low k (e.g., k=2): each fold uses only half the data for training — the evaluation has high variance because results depend heavily on the split, but low computational cost. High k (e.g., k=20 or leave-one-out): each fold uses nearly all the data for training — the evaluation has lower variance (more stable estimates) and lower bias (each model is trained on nearly the full dataset), but high computational cost. The standard k=10 is a widely-accepted compromise: low enough to be computationally practical, high enough that evaluation estimates are reliable. For small datasets (under a few hundred examples), leave-one-out cross-validation minimizes evaluation bias at the cost of high computation.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concept |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |

⬅️ **Prev:** [09 Loss Functions](../09_Loss_Functions/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [01 Linear Regression](../../03_Classical_ML_Algorithms/01_Linear_Regression/Theory.md)
