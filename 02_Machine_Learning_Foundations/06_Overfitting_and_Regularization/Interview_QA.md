# Overfitting and Regularization — Interview Q&A

## Beginner Level

**Q1: What is overfitting and how do you know when your model is overfitting?**

<details>
<summary>💡 Show Answer</summary>

A: Overfitting is when a model learns the training data so well that it memorizes noise and specific examples rather than learning the true underlying patterns. The model performs great on training data but poorly on new, unseen data. You know a model is overfitting when training accuracy is significantly higher than validation or test accuracy — a large gap between the two is the classic signal. In the extreme case, a model can get 99% training accuracy and 60% test accuracy, which is essentially memorization.

</details>

<br>

**Q2: What is the difference between overfitting and underfitting?**

<details>
<summary>💡 Show Answer</summary>

A: Overfitting means the model is too complex — it learned the training data including all its noise, so it cannot generalize. Training performance is great but test performance is poor. Underfitting means the model is too simple — it never captured the real patterns in the first place. Both training and test performance are poor. Overfitting is the more common problem in practice. The goal is the middle ground: a model complex enough to learn real patterns, but constrained enough not to memorize noise.

</details>

<br>

**Q3: What are two simple ways to reduce overfitting?**

<details>
<summary>💡 Show Answer</summary>

A: First, get more training data. With more diverse examples, it is much harder for a model to memorize specific cases — it is forced to learn general patterns. Second, simplify the model — use fewer parameters, shallower trees, or smaller networks. A simpler model literally cannot memorize complex noise. Both approaches reduce the gap between training and test performance without requiring deep technical knowledge.

</details>

---

## Intermediate Level

**Q4: What is the bias-variance tradeoff?**

<details>
<summary>💡 Show Answer</summary>

A: Every model's error has two learnable components. Bias is the error from the model being too simple — it makes systematic wrong assumptions and misses real patterns. High bias means underfitting. Variance is the error from the model being too sensitive to training data — small changes in training data produce very different models. High variance means overfitting. These tradeoff: making a model more complex reduces bias but increases variance. Making it simpler reduces variance but increases bias. The goal is to find the sweet spot where both are manageable.

</details>

<br>

**Q5: What is L2 regularization and how does it work?**

<details>
<summary>💡 Show Answer</summary>

A: L2 regularization (also called Ridge) adds a penalty to the loss function equal to the sum of all weights squared, multiplied by a regularization strength parameter (lambda). During training, the optimizer now minimizes both prediction error AND large weights. This forces the model to keep weights small. Large weights can only survive if they genuinely reduce prediction error enough to outweigh the penalty. The effect is a smoother, more distributed model that generalizes better. Lambda controls the tradeoff — too large and the model is over-constrained (underfits); too small and regularization has no effect.

</details>

<br>

**Q6: What is dropout in neural networks and when is it applied?**

<details>
<summary>💡 Show Answer</summary>

A: Dropout randomly sets a fraction of neurons to zero during each training step. If dropout rate is 0.5, half the neurons are randomly turned off in each forward pass. This prevents any single neuron from becoming overly important — the network is forced to learn redundant, distributed representations. At inference time, dropout is turned off and all neurons are active (with weights scaled accordingly). Dropout is one of the most effective regularization techniques for deep neural networks and is commonly set between 0.2 and 0.5 for hidden layers.

</details>

---

## Advanced Level

**Q7: How does early stopping work and why does validation loss eventually start rising?**

<details>
<summary>💡 Show Answer</summary>

A: Early stopping monitors validation loss after each epoch. Training continues as long as validation loss is decreasing. When validation loss stops improving (or starts rising), training is halted and the weights from the best validation epoch are restored. Validation loss eventually rises because the model starts fitting noise specific to the training set. At that point, every additional weight update improves training performance but makes the model less general — validation loss goes up because the model is getting less and less like what it will encounter in production.

</details>

<br>

**Q8: What is the difference between L1 and L2 regularization and when would you choose L1?**

<details>
<summary>💡 Show Answer</summary>

A: L2 adds squared weight magnitudes to the loss — it shrinks all weights toward zero but rarely makes them exactly zero. L1 adds absolute weight magnitudes — it can drive some weights to exactly zero, effectively removing those features from the model. L1 performs automatic feature selection. You would choose L1 when you have many features and believe only a few are truly relevant — L1 gives you a sparse model that is easier to interpret. L2 is the default for most cases because it is smoother (L1 has a non-differentiable point at zero, which requires special handling in gradient descent). In practice, ElasticNet combines both.

</details>

<br>

**Q9: How do you tune regularization strength (lambda) in practice?**

<details>
<summary>💡 Show Answer</summary>

A: You use a validation set and sweep over lambda values, typically on a log scale (0.0001, 0.001, 0.01, 0.1, 1, 10). For each lambda, train the model and evaluate validation performance. Plot validation loss vs lambda — it will show a U-shape or similar curve. Too small lambda: model overfits (high variance). Too large lambda: model underfits (high bias). The optimal lambda is near the minimum of the validation curve. In practice you use cross-validation for more reliable estimates of each lambda's performance, and tools like GridSearchCV or optuna can automate the search.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concept |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |

⬅️ **Prev:** [05 Model Evaluation](../05_Model_Evaluation/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [07 Feature Engineering](../07_Feature_Engineering/Theory.md)
