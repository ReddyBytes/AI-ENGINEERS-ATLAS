# Gradient Descent — Cheatsheet

**One-liner:** Gradient descent = find the model settings that minimize error by taking small steps downhill on the loss surface.

---

## Key Terms

| Term | What It Means |
|---|---|
| **Gradient** | The slope of the loss — tells you which direction is "uphill" for the error |
| **Descent** | Moving in the opposite direction of the gradient — downhill |
| **Learning rate** | How big each step is (too big = bounce; too small = crawl) |
| **Loss surface** | The mathematical landscape where height = model error |
| **Local minimum** | A valley that is not the deepest — gradient descent can get stuck here |
| **Global minimum** | The lowest possible loss — the ideal endpoint |
| **Epoch** | One full pass through the entire training dataset |
| **Batch size** | How many examples are used to compute one gradient update |
| **Convergence** | When the loss stops meaningfully decreasing — training is done |
| **Divergence** | When the loss grows instead of shrinking — learning rate too large |

---

## Three Types of Gradient Descent

| Type | Data Used Per Update | Speed | Stability | Common Use |
|---|---|---|---|---|
| Batch GD | Entire dataset | Slow | Very stable | Small datasets |
| Stochastic GD (SGD) | 1 example | Fast | Very noisy | Online learning |
| Mini-batch GD | Small batch (32–256) | Balanced | Balanced | Standard in deep learning |

---

## Learning Rate Guide

| Learning Rate | Effect |
|---|---|
| Way too high | Loss explodes — model diverges |
| Too high | Bounces around the valley, never settles |
| Too low | Takes forever to converge |
| Just right | Smooth, steady decrease in loss |
| Adaptive (Adam) | Adjusts automatically per parameter — usually the best choice |

---

## When to Use / Not Use

| Use Gradient Descent When... | Consider Alternatives When... |
|---|---|
| Training neural networks | Dataset is tiny — closed-form solutions exist (linear regression: normal equation) |
| Training large-scale ML models | The loss function is non-differentiable |
| Optimizing any differentiable loss | You need interpretable optimization steps |

---

## Golden Rules

1. **Always normalize input features.** Unnormalized features make the loss surface lopsided and training unstable.
2. **Start with a small learning rate if unsure.** Too small is slow; too large is broken.
3. **Use mini-batch, not full batch.** Mini-batch is faster and the noise actually helps escape local minima.
4. **Use Adam as your default optimizer.** It adapts learning rates automatically and works well out of the box.
5. **Watch the loss curve.** A flat curve means the learning rate is too low. An exploding curve means it is too high.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concept |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |

⬅️ **Prev:** [07 Feature Engineering](../07_Feature_Engineering/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [09 Loss Functions](../09_Loss_Functions/Theory.md)
