# Loss Functions — Interview Q&A

## Beginner

**Q1: What is a loss function and why does every neural network need one?**

<details>
<summary>💡 Show Answer</summary>

A loss function is a function that measures how wrong the model's predictions are compared to the true answers. It outputs a single number — the loss — where 0 means perfect predictions. The neural network cannot know how to improve without this signal. During training, backpropagation uses the loss to compute gradients — essentially asking: "if I nudge each weight slightly, how does the loss change?" Without a loss function, there is nothing to minimize and nothing to learn from.

</details>

---

**Q2: What is MSE and when would you use it?**

<details>
<summary>💡 Show Answer</summary>

MSE stands for Mean Squared Error. It calculates the average of the squared differences between predicted and actual values: `(1/n) × Σ(predicted - actual)²`. You use MSE for regression tasks — predicting continuous numeric outputs like house prices, temperatures, or scores. The squaring serves two purposes: it makes all errors positive (so errors don't cancel out), and it punishes large errors much more severely than small ones (a prediction 10 off gets 100x the penalty of a prediction 1 off).

</details>

---

**Q3: What is cross-entropy loss and when is it used?**

<details>
<summary>💡 Show Answer</summary>

Cross-entropy loss is used for classification. For binary classification it is: `-[y×log(p) + (1-y)×log(1-p)]` where y is the true label and p is the predicted probability. The key insight is logarithmic penalty: if the model is 99% confident but wrong, `log(0.01)` is a very large negative number, making the loss very large. If the model is 99% confident and correct, `log(0.99)` is near 0. This makes the model pay dearly for overconfident wrong predictions.

</details>

---

## Intermediate

**Q4: Why should you never use MSE for classification?**

<details>
<summary>💡 Show Answer</summary>

MSE can technically be used for classification, but it fails in practice for two reasons. First, with sigmoid output, the gradient of MSE is `(prediction - target) × sigmoid' × feature`. The sigmoid derivative is at most 0.25 and shrinks near 0 and 1. This makes gradients very small, especially when the model is already somewhat confident — training slows to a crawl. Second, MSE treats all probability errors linearly — being wrong by 0.1 at probability 0.5 is treated the same as being wrong by 0.1 at probability 0.99, even though the latter is a much more confident mistake. Cross-entropy captures this distinction naturally through the logarithm.

</details>

---

**Q5: What is the difference between MAE and MSE, and when would you prefer MAE?**

<details>
<summary>💡 Show Answer</summary>

MAE (Mean Absolute Error) averages the absolute differences, while MSE averages the squared differences. The key difference is sensitivity to outliers. MSE squares errors — a single outlier with error 10 contributes 100 to the loss, potentially dominating training. MAE just adds 10. So MAE is preferred when your data has outliers you don't want to overfit to. The trade-off is optimization: MSE has a smooth gradient everywhere that grows with error magnitude, which is good for gradient descent. MAE has a constant gradient regardless of error size, which can cause the optimizer to oscillate near the minimum.

</details>

---

**Q6: What is Focal Loss and when would you use it?**

<details>
<summary>💡 Show Answer</summary>

Focal Loss is a modification of cross-entropy designed for highly imbalanced datasets (e.g., object detection where 99% of image regions contain background). Standard cross-entropy gives equal weight to easy and hard examples. If 99% of examples are easy (background), the network gets dominated by those easy examples and fails to learn the rare hard ones. Focal Loss adds a factor `(1-p)^γ` that down-weights easy examples (high confidence → low weight). Hard examples (low confidence) maintain full weight. This was introduced in the RetinaNet paper and is widely used in object detection and imbalanced classification.

</details>

---

## Advanced

**Q7: From an information theory perspective, why does cross-entropy make sense as a loss for classification?**

<details>
<summary>💡 Show Answer</summary>

Cross-entropy originates from information theory. The entropy of a distribution p is `-Σ p(x) log p(x)` — the minimum average bits needed to encode events from that distribution. Cross-entropy between true distribution q and predicted distribution p is `-Σ q(x) log p(x)`. Minimizing cross-entropy is equivalent to minimizing KL divergence between the true and predicted distributions: `KL(q||p) = cross-entropy(q,p) - entropy(q)`. Since the entropy of the true labels is fixed, minimizing cross-entropy = minimizing KL divergence = making the model's probability distribution as close as possible to the true distribution. This is exactly what maximum likelihood estimation does.

</details>

---

**Q8: What is label smoothing and how does it modify the cross-entropy loss?**

<details>
<summary>💡 Show Answer</summary>

Label smoothing replaces hard 0/1 labels with soft labels: instead of `y = 1`, use `y = 1 - ε`; instead of `y = 0`, use `y = ε/k` (where k is the number of classes and ε is a small value like 0.1). This prevents the model from becoming overconfident — with hard labels, the model is rewarded for making predictions arbitrarily close to 1.0, which can cause the logits to grow unboundedly and reduce generalization. Label smoothing forces the model to maintain some uncertainty, acting as a regularizer. It was introduced in Inception-v3 and is commonly used in image classification and machine translation.

</details>

---

**Q9: How does the choice of loss function interact with class imbalance?**

<details>
<summary>💡 Show Answer</summary>

Standard cross-entropy treats all classes equally. With class imbalance (e.g., 95% class 0, 5% class 1), the model can achieve 95% accuracy by predicting class 0 always — and the loss will actually be quite low. Solutions: (1) Weighted cross-entropy — multiply the loss for the minority class by a weight `w = n_majority / n_minority`. (2) Focal Loss — down-weights easy majority-class examples dynamically. (3) Oversampling / undersampling before training to create a balanced dataset. (4) Using different metrics (F1, AUC-ROC) alongside the loss to detect when the loss is misleadingly low. The loss function alone is insufficient for imbalanced problems — it must be combined with sampling strategy or weighting.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Comparison.md](./Comparison.md) | Loss functions comparison |

⬅️ **Prev:** [03 Activation Functions](../03_Activation_Functions/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 Forward Propagation](../05_Forward_Propagation/Theory.md)
