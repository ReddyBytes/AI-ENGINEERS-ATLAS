# Calculus and Optimization — Cheatsheet

**One-liner:** Calculus tells you which direction to nudge each weight to make a model's error smaller — it's the engine behind all neural network training.

---

## Key Terms

| Term | Definition | AI Role |
|---|---|---|
| **Derivative f'(x)** | Rate of change of f at point x — the slope of the curve | Tells us how much the loss changes per weight change |
| **Gradient** | Vector of all partial derivatives — one per weight | Points in direction of steepest loss increase |
| **Partial derivative** | Derivative with respect to one variable, holding others fixed | How one weight affects the loss |
| **Gradient Descent** | Move weights opposite to the gradient to reduce loss | Core training algorithm for all neural networks |
| **Learning Rate (lr)** | How big each gradient descent step is | Too high = overshoot, too low = slow training |
| **Loss Function** | Measures how wrong the model is | What we're minimizing |
| **Backpropagation** | Chain rule applied backwards through the network | Computes gradients for all layers |
| **Chain Rule** | Rule for differentiating nested functions | How gradients flow through layers |
| **Local Minimum** | A valley that isn't the deepest valley | Can trap gradient descent |
| **Saddle Point** | Flat in some directions, curved in others | Common in high-dimensional loss landscapes |

---

## Core Formulas

```
Derivative (slope at a point):
  f'(x) = lim[h→0] (f(x+h) - f(x)) / h

Chain Rule:
  d/dx [f(g(x))] = f'(g(x)) × g'(x)

Gradient Descent Update:
  w_new = w_old - learning_rate × gradient

Partial Derivative (one weight at a time):
  ∂Loss/∂w_i  (how does loss change when w_i changes?)
```

---

## Common Derivatives to Know

| Function | Derivative | Notes |
|---|---|---|
| f(x) = x² | f'(x) = 2x | Parabola — minimum at x=0 |
| f(x) = x³ | f'(x) = 3x² | Always ≥ 0 |
| f(x) = eˣ | f'(x) = eˣ | Its own derivative! |
| f(x) = ln(x) | f'(x) = 1/x | Used in cross-entropy loss |
| ReLU: max(0,x) | f'(x) = 0 if x<0, 1 if x>0 | Most common neural activation |

---

## When to Use / Not Use

| Gradient descent works well when... | Watch out when... |
|---|---|
| Loss function is smooth and differentiable | Learning rate is too high (diverges) |
| Data is reasonably scaled | Learning rate is too low (very slow) |
| Using mini-batches for stability | Stuck in a sharp local minimum |
| Using momentum or Adam optimizer | Gradients vanish in very deep networks |

---

## Golden Rules

1. The gradient points UP the hill. Subtract it to go DOWN (minimize loss).
2. Learning rate is the most important hyperparameter to tune first.
3. Backprop is just the chain rule applied layer by layer — it's not magic.
4. If training loss is stuck, try adjusting the learning rate first.
5. Modern optimizers (Adam, AdaGrad) adjust the effective learning rate per weight automatically.
6. You don't need to calculate derivatives by hand — libraries like PyTorch do it automatically (autograd).

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Intuition_First.md](./Intuition_First.md) | No-formula intuition primer |
| [📄 Gradient_Intuition.md](./Gradient_Intuition.md) | Visual gradient intuition guide |

⬅️ **Prev:** [03 Linear Algebra](../03_Linear_Algebra/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 Information Theory](../05_Information_Theory/Theory.md)
