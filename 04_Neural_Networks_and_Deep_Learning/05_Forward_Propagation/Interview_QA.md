# Forward Propagation — Interview Q&A

## Beginner

**Q1: What is forward propagation?**

<details>
<summary>💡 Show Answer</summary>

Forward propagation is the process of passing input data through a neural network from the first layer to the last to produce a prediction. At each layer, the data undergoes a linear transformation (multiplied by weights, plus bias) and then a non-linear transformation (activation function). The final layer outputs the network's prediction. It is called "forward" because information flows strictly in one direction — from input toward output.

</details>

---

**Q2: What are the two operations that happen at each layer during forward propagation?**

<details>
<summary>💡 Show Answer</summary>

Every layer performs two operations in sequence. First, a linear transformation: `z = W · x + b` — the input is multiplied by the layer's weight matrix and the bias is added. This computes a weighted sum for each neuron. Second, an activation: `a = f(z)` — the result is passed through a non-linear activation function like ReLU or sigmoid. The output `a` becomes the input for the next layer.

</details>

---

**Q3: Does forward propagation change any weights?**

<details>
<summary>💡 Show Answer</summary>

No. Forward propagation is purely a computation — it runs the current weights and biases through the network to produce a prediction. The weights do not change during forward propagation. Weight updates only happen during backpropagation, which runs after the forward pass to compute how much each weight contributed to the error.

</details>

---

## Intermediate

**Q4: Why do we use matrix multiplication instead of computing each neuron one at a time?**

<details>
<summary>💡 Show Answer</summary>

A fully-connected layer has N neurons, each computing a weighted sum over M inputs. If done one neuron at a time, that is N separate computations. Matrix multiplication does them all at once: `z = W · x + b` computes all N weighted sums in a single operation. Modern hardware (GPUs, TPUs) is specifically designed for large matrix multiplications — this is why neural networks can run so fast. Computing neurons one at a time would be orders of magnitude slower.

</details>

---

**Q5: What is the role of bias in forward propagation?**

<details>
<summary>💡 Show Answer</summary>

Bias is a constant value added to the weighted sum before the activation: `z = W·x + b`. It allows the activation function to fire (produce non-zero output) even when all inputs are zero. Without bias, every neuron's decision boundary must pass through the origin of the input space — very limiting. Bias shifts the activation function horizontally, giving each neuron the flexibility to activate at different threshold levels regardless of the input values.

</details>

---

**Q6: How does a network's depth affect the forward pass?**

<details>
<summary>💡 Show Answer</summary>

Deeper networks have more sequential transformations. Each layer sees a transformed version of the original data — not the raw input. Layer 1 extracts simple features. Layer 2 extracts features of those features. This hierarchical representation building is how deep networks learn complex patterns from simple inputs. The downside: each additional layer adds computation time per forward pass and increases the risk of vanishing or exploding gradients during backpropagation. This is why very deep networks require techniques like residual connections (skip connections in ResNets) that let gradients bypass layers.

</details>

---

## Advanced

**Q7: How does batch processing work in forward propagation?**

<details>
<summary>💡 Show Answer</summary>

In practice, we never process one sample at a time. We process a batch — say 32 or 256 samples simultaneously. The input becomes a matrix of shape (batch_size, features) instead of a vector. The weight matrix W stays the same. The layer computes `Z = X·W^T + b` all at once, producing output of shape (batch_size, neurons). This is efficient because matrix multiplications on modern hardware scale nearly perfectly. Batch processing also provides a benefit for backpropagation — the gradient is averaged over the batch, reducing variance in weight updates.

</details>

---

**Q8: What happens to Dropout during the forward pass at inference time?**

<details>
<summary>💡 Show Answer</summary>

Dropout randomly zeros out neurons during training to prevent overfitting. But at inference time, Dropout is disabled — all neurons are active. To compensate for the fact that more neurons are active at inference than training, there are two approaches: (1) Inverted dropout (used in PyTorch and modern frameworks): during training, active neurons are scaled up by 1/keep_prob so their expected output matches inference. At inference, no scaling needed. (2) Standard dropout (historical): no scaling at training; at inference, multiply all weights by keep_prob. Modern frameworks use inverted dropout. In PyTorch: `model.train()` enables Dropout, `model.eval()` disables it.

</details>

---

**Q9: In the context of a transformer, how does forward propagation differ from a standard MLP?**

<details>
<summary>💡 Show Answer</summary>

In a standard MLP, each token (or sample) is processed independently — there is no interaction between different positions in the sequence. In a transformer, the forward pass includes a self-attention mechanism where each position in the sequence attends to all other positions. The attention computation is `softmax(QK^T / sqrt(d_k)) × V` — this means the output for each position is a weighted combination of all other positions' values. This is still a deterministic forward pass (no weights change), but it is a richer operation than pure feed-forward layers because it captures relationships across the sequence. The MLP blocks within each transformer layer perform standard forward propagation.

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

⬅️ **Prev:** [04 Loss Functions](../04_Loss_Functions/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [06 Backpropagation](../06_Backpropagation/Theory.md)
