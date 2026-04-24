# Activation Functions — Interview Q&A

## Beginner

**Q1: What is an activation function and why do neural networks need one?**

<details>
<summary>💡 Show Answer</summary>

An activation function is applied to the output of each neuron after the linear computation (weighted sum + bias). It introduces non-linearity. Without it, no matter how many layers you stack, the entire network collapses to a single linear operation — no more expressive than a simple linear regression. Activation functions allow the network to model curved, complex patterns.

</details>

---

**Q2: What is ReLU and why is it the most popular activation function?**

<details>
<summary>💡 Show Answer</summary>

ReLU stands for Rectified Linear Unit. The formula is `f(x) = max(0, x)`. If the input is positive, it passes through unchanged. If negative, it becomes 0. ReLU is popular for three reasons: it is extremely fast to compute (just a comparison), its gradient is 1 for positive inputs (no vanishing gradient problem on the active side), and it was shown empirically to train deep networks much faster than sigmoid or tanh. Most modern architectures use ReLU or a variant in hidden layers.

</details>

---

**Q3: What is the difference between sigmoid and softmax?**

<details>
<summary>💡 Show Answer</summary>

Both output values between 0 and 1, but they serve different purposes. Sigmoid outputs a single probability for a single neuron — used for binary classification (one output, one probability). Softmax operates on a vector of outputs and makes them sum to 1 — used for multi-class classification to give a probability distribution over all classes. Using sigmoid when you should use softmax (or vice versa) leads to incorrect probability interpretations.

</details>

---

## Intermediate

**Q4: What is the vanishing gradient problem and which activation functions cause it?**

<details>
<summary>💡 Show Answer</summary>

During backpropagation, gradients are multiplied layer by layer. If an activation function has a derivative less than 1 at most inputs — which is true for sigmoid and tanh at extreme values (where the function is flat) — then multiplying many of these small derivatives together causes the gradient to shrink exponentially toward zero. Early layers receive almost no update signal and fail to learn. Sigmoid saturates at approximately 0 and 1, where the gradient is near 0. This was a major obstacle to training deep networks before ReLU became widespread.

</details>

---

**Q5: What is the dying ReLU problem and how do you fix it?**

<details>
<summary>💡 Show Answer</summary>

A ReLU neuron outputs 0 for any negative input, and the gradient is also 0 for negative inputs. If a neuron's weights are updated such that it always receives negative inputs, it will always output 0, always have a zero gradient, and its weights will never update again. The neuron is "dead." This can happen with large learning rates or bad weight initialization. Fixes: LeakyReLU (passes a small fraction like 0.01x for negatives), ELU (smooth negative values), or PReLU (learned slope for negatives).

</details>

---

**Q6: Why should you use no activation function (linear) on the output layer for regression?**

<details>
<summary>💡 Show Answer</summary>

For regression, the target is an unbounded real number — it could be a house price, temperature, or stock movement. If you apply a sigmoid to the output, values are squashed to (0, 1). If you apply ReLU, negative predictions are impossible. Both would create a massive mismatch between what the network can predict and what the target actually is. Linear output means the network can predict any real number without constraint, which is what regression requires.

</details>

---

## Advanced

**Q7: Why does the choice of activation function affect weight initialization?**

<details>
<summary>💡 Show Answer</summary>

Weight initialization and activation functions interact. For ReLU, He initialization (weights drawn from a distribution with variance 2/n) is recommended because ReLU kills half the neurons (those receiving negative inputs), so you need larger initial weights to keep signal flowing. For sigmoid/tanh, Xavier/Glorot initialization is better — these activations use their full range, so the correct variance is 1/n or 2/(n_in + n_out). Using the wrong initialization with an activation can cause gradients to vanish or explode right from the start of training.

</details>

---

**Q8: What is the GELU activation function and why do transformers use it?**

<details>
<summary>💡 Show Answer</summary>

GELU (Gaussian Error Linear Unit) is defined as `f(x) = x × Φ(x)` where Φ is the standard normal CDF. In practice it is approximated as `f(x) ≈ 0.5x(1 + tanh(√(2/π)(x + 0.044715x³)))`. Unlike ReLU, it is smooth and stochastic — it weights the input by the probability of it being positive under a Gaussian distribution. This makes it differentiable everywhere (no hard 0 at negatives) and empirically performs better in very deep transformer models. GPT, BERT, and most modern transformers use GELU in their feed-forward layers.

</details>

---

**Q9: If softmax outputs sum to 1 and look like probabilities, are they actually calibrated probabilities?**

<details>
<summary>💡 Show Answer</summary>

Not necessarily. Softmax outputs are calibrated to be a valid probability distribution — they are non-negative and sum to 1. But they are not guaranteed to be accurate probabilities. A well-trained network might assign 0.99 probability to a class, but the true frequency of being correct at that confidence level might only be 0.85. This is the problem of calibration. A model is well-calibrated when its confidence scores match empirical accuracy. Techniques like temperature scaling (dividing logits by a temperature T before softmax) can adjust calibration post-training. This matters critically in medicine and finance where you act on model confidence.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Comparison.md](./Comparison.md) | Activation functions comparison |

⬅️ **Prev:** [02 MLPs](../02_MLPs/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 Loss Functions](../04_Loss_Functions/Theory.md)
