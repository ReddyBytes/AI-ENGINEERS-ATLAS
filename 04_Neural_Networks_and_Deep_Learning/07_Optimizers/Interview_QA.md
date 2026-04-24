# Optimizers — Interview Q&A

## Beginner

**Q1: What is the difference between gradient descent and SGD?**

<details>
<summary>💡 Show Answer</summary>

Gradient descent (specifically "batch gradient descent") computes the loss over the entire training dataset before taking one weight update. This gives a very accurate gradient direction but is extremely slow — a single update requires processing all data. SGD (Stochastic Gradient Descent) uses a small random mini-batch of data (typically 32–256 samples) per update. The gradient is noisy — not exactly the true gradient — but updates are very frequent and fast. In practice, mini-batch SGD is used almost everywhere because it converges much faster in wall-clock time.

</details>

---

**Q2: What is the learning rate and why does it matter so much?**

<details>
<summary>💡 Show Answer</summary>

The learning rate controls how large a step the optimizer takes in the direction of the gradient: `w = w - lr × gradient`. If lr is too large, the optimizer takes huge steps and overshoots the minimum — the loss might oscillate or diverge. If lr is too small, the optimizer takes tiny steps and training takes forever or gets stuck. The learning rate is often called the most important hyperparameter in deep learning. Common starting points: 0.001 for Adam, 0.01 for SGD. Always monitor training loss — if it diverges, reduce lr; if it barely decreases, consider increasing it.

</details>

---

**Q3: What is momentum and what problem does it solve?**

<details>
<summary>💡 Show Answer</summary>

Momentum keeps a running average of recent gradients and uses that to update weights, rather than just the current gradient. This is like a ball rolling downhill — it builds up speed in the consistent direction of the slope. Momentum solves two problems: First, it speeds up convergence by accelerating in directions where gradients consistently agree. Second, it helps escape shallow local minima — if the ball has built up speed, it can roll through a small dip without stopping. The momentum coefficient (beta, typically 0.9) controls how much past velocity is retained.

</details>

---

## Intermediate

**Q4: How does Adam combine momentum and RMSProp?**

<details>
<summary>💡 Show Answer</summary>

Adam maintains two running averages. The first moment (m) is a running average of gradients — equivalent to momentum. The second moment (v) is a running average of squared gradients — equivalent to RMSProp's adaptive scaling. The weight update uses `m / sqrt(v)`: the numerator provides momentum-based direction, the denominator scales down the learning rate for weights with large recent gradient history (preventing overshooting). Adam also includes bias correction for the first few steps, since m and v start at zero. The result: momentum-based direction + per-parameter adaptive learning rate.

</details>

---

**Q5: Why does Adam sometimes generalize worse than SGD on image classification tasks?**

<details>
<summary>💡 Show Answer</summary>

Research (particularly Wilson et al. 2017) showed that while Adam converges faster, models trained with SGD + momentum often achieve better final test accuracy on vision benchmarks like CIFAR-10 and ImageNet. The hypothesis: Adam's adaptive learning rates can find sharp minima in the loss landscape — areas where the loss is very low on training data but the loss landscape is very steep, meaning small data changes cause large accuracy drops (poor generalization). SGD with momentum tends to find flatter minima, which generalize better. In practice: use Adam for quick experiments and transformers; use SGD + momentum + LR schedule for vision tasks where you need SOTA performance.

</details>

---

**Q6: What is AdamW and why is it preferred over Adam for transformers?**

<details>
<summary>💡 Show Answer</summary>

Standard Adam implements weight decay (L2 regularization) by adding the regularization gradient to the main gradient before the adaptive scaling. This means the adaptive scaling also affects the weight decay, weakening its regularization effect for parameters with small gradient variance. AdamW decouples weight decay from the gradient update: `w = w - lr × adam_update - lr × weight_decay × w`. The weight decay is applied directly to the parameter, not through the gradient. This gives proper L2 regularization regardless of the adaptive scaling. AdamW is now the standard for training transformers (BERT, GPT) and has become the default in most large model training.

</details>

---

## Advanced

**Q7: What is a learning rate warmup and why does it matter for transformer training?**

<details>
<summary>💡 Show Answer</summary>

Learning rate warmup starts with a very small learning rate (near 0) and linearly increases it to the target value over the first few thousand training steps. This is particularly important for transformers for two reasons. First, early in training, the model's parameters are randomly initialized and activations are noisy — large initial learning rates cause erratic updates that can permanently damage early convergence. Second, the second moment estimate in Adam (v) starts at zero and needs a few steps to accurately reflect the gradient variance. During this warm-up period, Adam's denominator is unreliable. The standard transformer schedule (from "Attention is All You Need") is: linear warmup for 4000 steps, then inverse-square-root decay.

</details>

---

**Q8: What is the relationship between batch size and learning rate?**

<details>
<summary>💡 Show Answer</summary>

When you double the batch size, each gradient estimate is computed over twice as many samples, making it twice as accurate and reducing gradient noise. To take advantage of this, you can use a proportionally larger learning rate — this is the "linear scaling rule" (Goyal et al., 2017): if you double the batch size, double the learning rate. Intuition: with a more accurate gradient, you can safely take a larger step. However, this rule breaks down at very large batch sizes. Beyond a critical batch size, increasing the batch size stops reducing gradient variance meaningfully, and very large learning rates cause divergence. Large batch training (e.g., 8192 or 65536) typically needs learning rate warmup and careful tuning.

</details>

---

**Q9: What are second-order optimization methods and why aren't they used more often in deep learning?**

<details>
<summary>💡 Show Answer</summary>

First-order methods (SGD, Adam) only use the gradient (first derivative) of the loss. Second-order methods use the Hessian — the matrix of second derivatives — to make more informed updates. The intuition: the gradient tells you which way is downhill. The Hessian tells you the curvature — whether the slope is getting steeper or flatter. With curvature information, you can take a much more precise step directly toward the minimum in one shot (Newton's method). The problem is scale: the Hessian for a model with N parameters is an N×N matrix. For a model with 100 million parameters, the Hessian has 10^16 entries — impossible to store, let alone invert. Approximate second-order methods (K-FAC, Shampoo) exist and show promise, but the overhead is still much larger than Adam, limiting their practical use.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Comparison.md](./Comparison.md) | Optimizers comparison (SGD, Adam, RMSProp) |

⬅️ **Prev:** [06 Backpropagation](../06_Backpropagation/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [08 Regularization](../08_Regularization/Theory.md)
