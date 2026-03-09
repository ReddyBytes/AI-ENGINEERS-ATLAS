# Activation Functions — Cheatsheet

**One-liner:** Activation functions introduce non-linearity between layers — without them, a deep network is no more powerful than a single linear layer.

---

## Key Terms

| Term | What it means |
|------|---------------|
| Non-linearity | An operation that is not a straight line — allows the network to learn curves |
| Saturating function | Output becomes flat at extremes (gradients → 0) — bad for deep nets |
| Vanishing gradient | Gradients shrink to near-zero through deep layers — early layers stop learning |
| Dying ReLU | A ReLU neuron stuck at 0 forever because all its inputs are negative |
| Zero-centered | Output mean is 0 — helps optimizer updates be more symmetric |
| Derivative / gradient | How much the output changes per unit change in input — needed for backprop |

---

## Quick Formula Reference

| Function | Formula | Output Range |
|----------|---------|-------------|
| Step | 1 if x≥0 else 0 | {0, 1} |
| Sigmoid | 1 / (1 + e^−x) | (0, 1) |
| Tanh | (e^x − e^−x) / (e^x + e^−x) | (−1, 1) |
| ReLU | max(0, x) | [0, ∞) |
| LeakyReLU | max(0.01x, x) | (−∞, ∞) |
| Softmax | e^xi / Σe^xj | (0, 1), sums to 1 |

---

## Where to Use Each

| Layer type | Best choice | Why |
|------------|-------------|-----|
| Hidden layers (standard) | ReLU | Fast, no vanishing gradient on active neurons |
| Hidden layers (if dying ReLU) | LeakyReLU or ELU | Keeps dead neurons alive |
| Hidden layers in RNNs | Tanh | Bounded output helps with sequence memory |
| Output — binary classification | Sigmoid | Output = probability between 0 and 1 |
| Output — multi-class | Softmax | Outputs sum to 1, gives class probabilities |
| Output — regression | None (linear) | Raw number, no squashing needed |

---

## When to Use / Not Use

| Use when... | Do NOT use when... |
|-------------|-------------------|
| Hidden layers: almost always ReLU | Never use Step in a trainable network |
| Output binary: Sigmoid | Don't use Sigmoid in hidden layers (vanishing grad) |
| Output multi-class: Softmax | Don't use Softmax in hidden layers |
| Deep nets prone to dying ReLU: LeakyReLU | Avoid complex activations as a first choice |

---

## Golden Rules

1. Default: ReLU for hidden layers, Softmax for multi-class output, Sigmoid for binary output.
2. Sigmoid and Tanh saturate at extremes — dangerous in deep hidden layers.
3. ReLU is fast but can cause dead neurons — watch for neurons always outputting 0.
4. Softmax outputs must always be interpreted as relative, not absolute, probabilities.
5. The activation function on the output layer is determined by your task (classification type or regression) — it is not a tunable hyperparameter.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Comparison.md](./Comparison.md) | Activation functions comparison |

⬅️ **Prev:** [02 MLPs](../02_MLPs/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 Loss Functions](../04_Loss_Functions/Theory.md)
