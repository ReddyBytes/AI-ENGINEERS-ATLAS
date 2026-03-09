# MLPs — Interview Q&A

## Beginner

**Q1: What is the difference between a perceptron and an MLP?**

A perceptron is a single neuron with a step function. It can only solve linearly separable problems. An MLP (Multi-Layer Perceptron) has multiple layers of neurons with non-linear activation functions. This allows it to solve non-linear problems — including XOR, image recognition, and language tasks. The MLP is the standard "vanilla" neural network.

---

**Q2: What is a hidden layer and what does it do?**

A hidden layer is any layer between the input and output layers. The word "hidden" just means it is not directly observable from outside the network. Each hidden layer transforms the data into a new representation. Earlier layers tend to detect simple features (edges, single words). Deeper layers combine those into more abstract features (shapes, sentence meaning). Hidden layers are where the network does its actual "thinking."

---

**Q3: Why does an MLP need activation functions?**

Without activation functions, each layer performs a linear transformation (multiply by weights, add bias). The composition of linear transformations is still a linear transformation. No matter how many layers you add, the whole network would be equivalent to one single linear layer — no more powerful than logistic regression. Activation functions introduce non-linearity, allowing layers to combine in ways that can represent curves, clusters, and complex boundaries.

---

## Intermediate

**Q4: What is the Universal Approximation Theorem?**

The Universal Approximation Theorem states that an MLP with a single hidden layer containing a sufficient number of neurons (with a non-linear activation) can approximate any continuous function to arbitrary precision. This is theoretically powerful but practically limited — "sufficient neurons" can be exponentially many for complex functions. In practice we use more layers (deeper networks) with fewer neurons per layer, which tends to work better with reasonable compute.

---

**Q5: How do you choose the number of hidden layers and neurons?**

There is no single formula. Common starting points:
- 1–2 hidden layers for most tabular data problems
- 64–256 neurons per layer for small/medium tasks
- Start simple, measure validation loss, then increase capacity if underfitting

Wider networks increase capacity within a layer. Deeper networks allow more abstract representations but are harder to train. Use cross-validation to tune these as hyperparameters.

---

**Q6: What is the difference between depth and width in an MLP?**

**Depth** is the number of layers. More depth lets the network learn more abstract hierarchical representations. **Width** is the number of neurons per layer. More width gives each layer more capacity to represent diverse patterns at that level of abstraction. Deeper networks are generally more parameter-efficient than wider ones for complex tasks, which is why deep learning replaced "wide, shallow" models for things like image recognition.

---

## Advanced

**Q7: Why does the vanishing gradient problem affect deep MLPs?**

During backpropagation, gradients are multiplied layer by layer (via the chain rule). If activation functions have gradients less than 1 (like sigmoid, which saturates near 0 and 1), multiplying many small numbers together causes the gradient to shrink exponentially toward zero as you go back through layers. Early layers get almost no training signal — their weights barely update. This is the vanishing gradient problem. Solutions include ReLU activation (which has gradient exactly 1 for positive inputs), batch normalization, and residual connections.

---

**Q8: What is the role of the output layer activation, and how does it differ from hidden layer activations?**

Hidden layer activations (typically ReLU) introduce non-linearity to help the network learn complex representations. The output layer activation is chosen based on the task:
- **Sigmoid** for binary classification — squeezes output to [0,1] giving a probability
- **Softmax** for multi-class classification — outputs a probability distribution summing to 1
- **No activation (linear)** for regression — the raw value is the prediction

Using the wrong output activation causes training to fail in subtle ways — for example, using sigmoid for multi-class forces you to pick arbitrary thresholds instead of letting the network express relative confidence.

---

**Q9: How would you explain the information bottleneck perspective of MLPs?**

The information bottleneck theory (Tishby et al.) proposes that during training, an MLP goes through two phases. First, it compresses: early layers reduce the input to the most task-relevant features, throwing away noise. Second, it generalizes: later layers map the compressed representation to outputs. This explains why deep networks generalize — they are forced to find compact, informative representations of the input rather than memorizing it. The theory is debated but provides useful intuition for why regularization (which prevents memorization) improves generalization.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [01 Perceptron](../01_Perceptron/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 Activation Functions](../03_Activation_Functions/Theory.md)
