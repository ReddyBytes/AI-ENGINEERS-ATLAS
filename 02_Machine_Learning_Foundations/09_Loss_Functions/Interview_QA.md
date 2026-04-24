# Loss Functions — Interview Q&A

## Beginner Level

**Q1: What is a loss function and what role does it play in training?**

<details>
<summary>💡 Show Answer</summary>

A: A loss function measures how different a model's prediction is from the correct answer. It produces a single number — the loss — that represents how wrong the model is right now. During training, the model's entire goal is to minimize this number. The optimizer (gradient descent) computes the gradient of the loss with respect to every weight and updates the weights to make the loss smaller. Without a loss function there is no signal — the model has no way to know if it is improving. The loss is the compass that guides every weight update.

</details>

<br>

**Q2: What is Mean Squared Error (MSE) and when do you use it?**

<details>
<summary>💡 Show Answer</summary>

A: MSE is the average of squared differences between predictions and actual values: mean((ŷ - y)²). You use it for regression tasks where the output is a continuous number — predicting house prices, temperatures, sales figures. The squaring does two things: makes all errors positive (no canceling out), and heavily penalizes large errors. A prediction that is off by 10 contributes 100 to the loss; a prediction off by 1 contributes only 1. This makes MSE appropriate when large errors are significantly worse than small ones.

</details>

<br>

**Q3: What is cross-entropy loss and when do you use it?**

<details>
<summary>💡 Show Answer</summary>

A: Cross-entropy loss measures how different the model's predicted probability distribution is from the true distribution. For binary classification: -[y·log(ŷ) + (1-y)·log(1-ŷ)]. You use it for classification tasks. Its key property: it punishes confident wrong predictions extremely harshly. If the model says 99% probability of spam and the email is not spam, the loss is -log(0.01) ≈ 4.6. If it says 51%, the loss is -log(0.49) ≈ 0.7. This encourages the model to be well-calibrated — not just predicting the right class but with appropriate confidence.

</details>

---

## Intermediate Level

**Q4: When would you choose MAE over MSE for a regression problem?**

<details>
<summary>💡 Show Answer</summary>

A: MAE (Mean Absolute Error) uses the absolute value of errors rather than squaring them: mean(|ŷ - y|). Choose MAE over MSE when your data has significant outliers. MSE's squaring amplifies outlier errors enormously — one prediction off by 1000 contributes 1,000,000 to the MSE while all other predictions might contribute only a few hundred total. MAE treats that same outlier as contributing 1000 — proportional to its magnitude. In practical terms: if you are predicting house prices and a few extreme luxury properties are 10x more expensive than typical homes, MAE is more appropriate because MSE would cause training to obsess over those few outliers.

</details>

<br>

**Q5: Why should you not use MSE for a classification problem?**

<details>
<summary>💡 Show Answer</summary>

A: Using MSE for classification (where outputs should be probabilities) creates several problems. First, MSE has no mechanism to constrain outputs to [0, 1] — the model could output negative values or values above 1. Second, MSE provides weak gradient signal near 0 and 1 with sigmoid activations (the "vanishing gradient" problem for the output layer). Third, MSE treats a prediction of 0.4 and 0.6 equally wrong for a true label of 1, even though 0.6 is closer to correct. Cross-entropy's logarithmic scale gives much stronger gradient signal in the critical probability ranges, leading to faster and better convergence for classification.

</details>

<br>

**Q6: What is the relationship between the loss function and the evaluation metric?**

<details>
<summary>💡 Show Answer</summary>

A: The loss function is what the model optimizes during training. The evaluation metric is what you report to stakeholders or use to compare models. They are often related but not always the same. For example: you train with binary cross-entropy loss, but report accuracy or F1-score as the metric. The reason they differ: loss functions must be differentiable (so gradient descent can work), but many useful metrics like accuracy are not differentiable. In some cases the mismatch matters — a model trained on cross-entropy may not maximize F1, especially on imbalanced data. This is why you sometimes need to adjust decision thresholds or use specialized losses (like focal loss) when optimizing for specific metrics.

</details>

---

## Advanced Level

**Q7: What is focal loss and why was it created?**

<details>
<summary>💡 Show Answer</summary>

A: Focal loss was introduced for object detection (RetinaNet) to handle extreme class imbalance. In a typical image with thousands of background regions and only a few objects, standard cross-entropy is overwhelmed by easy background examples — the loss is dominated by correctly-classified easy cases, and the gradients from hard cases (the actual objects) are negligible. Focal loss adds a modulating factor (1 - ŷ)^γ to cross-entropy. For easy examples where the model is confident and correct, ŷ is high and (1-ŷ)^γ is near zero — the loss contribution is heavily down-weighted. For hard examples where the model is uncertain, the contribution is close to regular cross-entropy. This refocuses training on examples the model has not yet learned well.

</details>

<br>

**Q8: What is the KL divergence and how does it relate to cross-entropy?**

<details>
<summary>💡 Show Answer</summary>

A: KL divergence (Kullback-Leibler divergence) measures how much one probability distribution differs from another. Cross-entropy H(p, q) = H(p) + KL(p||q), where H(p) is the entropy of the true distribution and KL(p||q) is the divergence from true to predicted. When you minimize cross-entropy during training, you are simultaneously minimizing KL divergence (since H(p) is fixed — the true labels do not change). This connection matters in generative models: VAEs minimize a loss that includes KL divergence between the learned latent distribution and a prior. Language models trained with cross-entropy are implicitly minimizing KL divergence between the model's token distribution and the true data distribution.

</details>

<br>

**Q9: How do you choose a loss function for a multi-task learning problem?**

<details>
<summary>💡 Show Answer</summary>

A: In multi-task learning a model simultaneously optimizes multiple objectives (e.g., a medical model predicting both disease classification and severity score). You combine multiple loss functions with weights: total_loss = λ₁·loss₁ + λ₂·loss₂. The challenge is balancing them. If one loss is in the range of thousands and another in the range of 0–1, the optimizer ignores the small one. Solutions include normalizing each loss to similar scales, using uncertainty weighting (a method that learns the task weights automatically based on homoscedastic task uncertainty — tasks with higher uncertainty get lower weight), and gradient normalization (normalizing gradient magnitudes from each task). The weights λ are hyperparameters that significantly affect what the model learns — they encode the relative business importance of each task.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concept |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |

⬅️ **Prev:** [08 Gradient Descent](../08_Gradient_Descent/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [10 Bias vs Variance](../10_Bias_vs_Variance/Theory.md)
