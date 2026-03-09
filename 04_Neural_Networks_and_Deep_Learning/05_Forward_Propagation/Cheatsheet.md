# Forward Propagation — Cheatsheet

**One-liner:** Forward propagation is the process of passing input data through each layer of the network (linear transform → activation) to produce a prediction.

---

## Key Terms

| Term | What it means |
|------|---------------|
| Forward pass | One complete run of data from input to output |
| z (pre-activation) | The raw weighted sum: z = W·x + b |
| a (activation) | The output after applying the activation function: a = f(z) |
| W | Weight matrix for a layer |
| b | Bias vector for a layer |
| ŷ (y-hat) | The network's prediction (output of the final layer) |
| Matrix multiplication | How all neurons in a layer are computed simultaneously |
| Layer depth | How many transformations the data has passed through |

---

## Per-Layer Formula

```
z = W · a_prev + b        ← linear transformation
a = activation_function(z) ← non-linear transformation

Where:
  a_prev = output from the previous layer (or input x for layer 1)
  W      = weight matrix  shape: (this_layer_size, prev_layer_size)
  b      = bias vector    shape: (this_layer_size,)
  z      = pre-activation shape: (this_layer_size,)
  a      = activation     shape: (this_layer_size,)
```

---

## Dimension Tracking

| Layer | Input shape | Weight shape | Output shape |
|-------|-------------|--------------|-------------|
| Input | (batch, features) | — | (batch, features) |
| Dense(64) | (batch, n) | (n, 64) | (batch, 64) |
| Dense(32) | (batch, 64) | (64, 32) | (batch, 32) |
| Dense(1) | (batch, 32) | (32, 1) | (batch, 1) |

Tracking shapes is essential for debugging. A shape mismatch will crash; a silent shape error (from broadcasting) will give wrong results.

---

## Full Forward Pass (2-layer network)

```
Input:    x

Layer 1:  z1 = W1 · x  + b1
          a1 = ReLU(z1)

Layer 2:  z2 = W2 · a1 + b2
          a2 = sigmoid(z2)

Output:   ŷ = a2
Loss:     L = loss(ŷ, y)
```

---

## When to Use / Not Use

| Forward prop is... | Notes |
|-------------------|-------|
| Used at training time | Every training step starts with a forward pass |
| Used at inference time | When making real predictions, only forward pass runs |
| NOT where learning happens | Weights do not change during forward prop |
| Deterministic (mostly) | Same input → same output (unless Dropout is active during training) |

---

## Golden Rules

1. Forward prop just computes a prediction — no weights change.
2. Every layer: (1) multiply by W, (2) add b, (3) apply activation. Repeat.
3. The output of one layer is the input of the next.
4. Track tensor shapes. Mismatches are the #1 source of bugs in neural networks.
5. The final layer's activation is determined by the task (sigmoid, softmax, or none).
6. Forward prop happens billions of times during training — keeping each layer efficient matters.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Math_Walkthrough.md](./Math_Walkthrough.md) | Step-by-step math walkthrough |

⬅️ **Prev:** [04 Loss Functions](../04_Loss_Functions/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [06 Backpropagation](../06_Backpropagation/Theory.md)
