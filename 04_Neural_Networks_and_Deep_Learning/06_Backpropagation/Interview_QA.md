# Backpropagation — Interview Q&A

## Beginner

**Q1: What is backpropagation in simple terms?**

<details>
<summary>💡 Show Answer</summary>

Backpropagation is the training algorithm for neural networks. After the network makes a prediction, we measure how wrong it was (the loss). Backpropagation then works backward through the network to calculate how much each weight contributed to that error. Weights that were responsible for more of the error get a larger update. The updates push every weight in the direction that reduces the loss. It is called "backward" because it processes layers from output toward input — the opposite direction of the forward pass.

</details>

---

<br>

**Q2: What is the chain rule and why does backpropagation need it?**

<details>
<summary>💡 Show Answer</summary>

The chain rule is a rule from calculus for computing derivatives of composed functions. If y = f(g(x)), then dy/dx = df/dg × dg/dx. In a neural network, the loss depends on the output, which depends on layer 2, which depends on layer 1, which depends on the weights. To find how the loss changes with a weight deep in the network, we multiply together the derivatives at each step in the chain. This is exactly the chain rule. Backpropagation is efficient because it reuses intermediate computations from this chain rather than computing each derivative from scratch.

</details>

---

<br>

**Q3: What happens to weights after backpropagation?**

<details>
<summary>💡 Show Answer</summary>

Each weight is updated using the gradient descent rule: `w_new = w_old - learning_rate × gradient`. The gradient (`dL/dW`) tells us the direction and magnitude of change needed. The learning rate scales how big each step is. If the gradient is positive (the weight is making the loss larger), we decrease the weight. If the gradient is negative (the weight is making the loss smaller), we increase it. Over thousands of iterations, this nudges all weights toward values that produce lower loss.

</details>

---

## Intermediate

**Q4: How does backpropagation handle multiple layers — doesn't computing gradients for early layers get very expensive?**

<details>
<summary>💡 Show Answer</summary>

Backpropagation is efficient because of the dynamic programming principle. When computing the gradient for layer 1, you need the gradient from layer 2 — which has already been computed in this backward pass. You do not recompute it. Each layer passes its gradient to the previous layer. This means the total cost of computing all gradients is roughly the same as one forward pass. Without this reuse, the cost would grow exponentially with depth — making deep learning computationally impossible.

</details>

---

<br>

**Q5: What is vanishing gradient and how does it affect training?**

<details>
<summary>💡 Show Answer</summary>

The vanishing gradient problem occurs when gradients become extremely small as they travel backward through many layers. Each layer multiplies the gradient by the derivative of its activation function. For sigmoid, this derivative is at most 0.25. After ten layers: 0.25^10 ≈ 0.000001. Early layers receive almost no gradient signal — their weights barely update, so they fail to learn meaningful features. This was the main obstacle to training deep networks before ReLU. ReLU has a gradient of exactly 1 for positive inputs, so gradients do not shrink as they pass through active ReLU neurons.

</details>

---

<br>

**Q6: What is gradient clipping and when is it used?**

<details>
<summary>💡 Show Answer</summary>

Gradient clipping is a technique that caps the magnitude of gradients during backpropagation. If the gradient norm exceeds a threshold (e.g., 1.0), all gradients are scaled down proportionally to bring the norm back to the threshold. This prevents the exploding gradient problem — where large weights cause gradients to multiply to astronomical values, causing erratic weight updates and loss divergence. Gradient clipping is most commonly used with RNNs (which unroll over many time steps, creating very deep backprop chains) and in some large language model training.

</details>

---

## Advanced

**Q7: How does automatic differentiation differ from manually implementing backpropagation?**

<details>
<summary>💡 Show Answer</summary>

Manual backpropagation requires you to derive and code the gradient formula for every operation in your network — error-prone and inflexible. Automatic differentiation (autodiff), as used in PyTorch and TensorFlow, builds a computational graph of every operation during the forward pass. Each node in the graph knows its own local gradient formula. When you call `loss.backward()`, the framework traverses this graph in reverse, applying the chain rule automatically. You never write a gradient formula manually. PyTorch uses dynamic autodiff — the graph is rebuilt every forward pass, enabling control flow (if/else, loops) inside models. TensorFlow's eager mode does the same.

</details>

---

<br>

**Q8: What is the difference between backpropagation through time (BPTT) and standard backpropagation?**

<details>
<summary>💡 Show Answer</summary>

Standard backpropagation works on a static computation graph with a fixed number of layers. Backpropagation through time (BPTT) handles RNNs, where the same weights are applied repeatedly at each time step. An RNN processing a 100-step sequence is equivalent to a 100-layer network where all layers share weights. BPTT "unrolls" this network through time and applies standard backpropagation to the unrolled version. The challenge: 100-step unrolling creates 100 gradient multiplications — severe vanishing gradient. Solutions: truncated BPTT (only unroll k steps), LSTMs/GRUs (which have gating mechanisms that allow gradients to flow over long distances).

</details>

---

<br>

**Q9: In a large model with billions of parameters, is backpropagation still efficient?**

<details>
<summary>💡 Show Answer</summary>

Yes, but the memory requirements become the limiting factor. Backpropagation requires storing all intermediate activations (the outputs of every layer during the forward pass) to compute gradients during the backward pass. For a model with billions of parameters, this can require hundreds of gigabytes of GPU memory. Techniques to reduce this: (1) Gradient checkpointing — instead of storing all activations, recompute them on-the-fly during backprop (trades compute for memory). (2) Mixed precision training — store activations in float16 instead of float32, halving memory. (3) Model parallelism — distribute layers across multiple GPUs. (4) Gradient accumulation — simulate large batches with small ones by accumulating gradients over multiple forward passes before updating.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Math_Walkthrough.md](./Math_Walkthrough.md) | Step-by-step math walkthrough |

⬅️ **Prev:** [05 Forward Propagation](../05_Forward_Propagation/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [07 Optimizers](../07_Optimizers/Theory.md)
