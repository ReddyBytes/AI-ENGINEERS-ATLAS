# MLPs — Cheatsheet

**One-liner:** An MLP is a neural network with one or more hidden layers between input and output, where each layer is fully connected to the next and activation functions enable non-linear learning.

---

## Key Terms

| Term | What it means |
|------|---------------|
| Input layer | Receives raw features, no computation |
| Hidden layer | Internal layers that transform the data |
| Output layer | Produces the final prediction |
| Fully connected (dense) | Every neuron in one layer connects to every neuron in the next |
| Activation function | Non-linear function applied after each layer's linear computation |
| Non-linearity | What makes stacked layers more powerful than one layer |
| Depth | Number of layers in the network |
| Width | Number of neurons in a layer |
| Universal Approximation | One hidden layer with enough neurons can approximate any function |
| Parameters | All the weights and biases the network learns |

---

## Architecture Formula

```
Layer output = activation( W × input + b )

Total parameters in one fully-connected layer =
    (input_size × output_size) + output_size
    =  weights + biases
```

---

## Typical Layer Sizes

| Problem | Input | Hidden | Output |
|---------|-------|--------|--------|
| Binary classification | n features | 64–256 | 1 (sigmoid) |
| Multi-class (10 classes) | n features | 128–512 | 10 (softmax) |
| Regression | n features | 64–256 | 1 (linear) |

---

## When to Use / Not Use

| Use MLPs when... | Do NOT use when... |
|------------------|--------------------|
| Tabular / structured data | Image data (use CNN instead) |
| Small to medium datasets | Sequential / time-series data (use RNN) |
| Feature vectors are fixed-size | Spatial relationships matter in data |
| You need a simple baseline fast | Explainability is critical |

---

## Golden Rules

1. You need at least one hidden layer for non-linear problems.
2. More layers = more capacity, but also harder to train and more prone to overfitting.
3. Without activation functions, stacking layers is useless — it all collapses to one linear transformation.
4. Output layer activation depends on task: sigmoid for binary, softmax for multi-class, none (linear) for regression.
5. Always normalize your inputs — neural networks are sensitive to input scale.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [01 Perceptron](../01_Perceptron/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 Activation Functions](../03_Activation_Functions/Theory.md)
