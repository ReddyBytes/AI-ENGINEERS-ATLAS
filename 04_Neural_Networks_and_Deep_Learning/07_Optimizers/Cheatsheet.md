# Optimizers — Cheatsheet

**One-liner:** An optimizer is the algorithm that updates neural network weights using gradients — the choice of optimizer affects how fast and how reliably the network converges.

---

## Key Terms

| Term | What it means |
|------|---------------|
| Gradient descent | Update weights in the direction of steepest loss decrease |
| SGD | Stochastic Gradient Descent — basic optimizer using mini-batch gradients |
| Mini-batch | A small subset of training data used for one weight update |
| Learning rate (lr) | How big a step to take per update |
| Momentum | Accumulating velocity from past gradients to speed up convergence |
| Adaptive learning rate | Different effective lr per parameter based on gradient history |
| Adam | The most popular optimizer — combines momentum + adaptive lr |
| LR schedule | Planned changes to learning rate during training |
| Convergence | When the loss stops decreasing and weights stabilize |

---

## Formula Quick Reference

```
SGD:
  w = w - lr × g

SGD + Momentum:
  v = β × v + g
  w = w - lr × v

RMSProp:
  v = β × v + (1-β) × g²
  w = w - (lr / sqrt(v + ε)) × g

Adam:
  m = β1 × m + (1-β1) × g         [1st moment — momentum]
  v = β2 × v + (1-β2) × g²        [2nd moment — RMSProp]
  m̂ = m / (1 - β1^t)              [bias-corrected]
  v̂ = v / (1 - β2^t)              [bias-corrected]
  w = w - lr × m̂ / (sqrt(v̂) + ε)
```

---

## Default Hyperparameters

| Optimizer | Key hyperparameters | Good defaults |
|-----------|---------------------|---------------|
| SGD | lr, momentum | lr=0.01, momentum=0.9 |
| Adam | lr, beta1, beta2, eps | lr=0.001, β1=0.9, β2=0.999, ε=1e-8 |
| RMSProp | lr, rho, eps | lr=0.001, rho=0.9, ε=1e-8 |
| AdamW | Same as Adam + weight_decay | lr=0.001, weight_decay=0.01 |

---

## When to Use / Not Use

| Optimizer | Use when... | Avoid when... |
|-----------|-------------|---------------|
| SGD | You have a well-tuned lr, want max control, training CNNs for SOTA | First experiments, complex schedules needed |
| SGD + Momentum | Standard image classification | Non-stationary gradients |
| Adam | Default choice, NLP, transformers, quick experiments | Sometimes generalizes slightly worse than SGD on vision |
| AdamW | Transformers (BERT, GPT), fine-tuning | — (generally better than Adam) |
| RMSProp | RNNs, LSTMs, non-stationary environments | — |

---

## Golden Rules

1. **Adam first.** Start with Adam. It works well with minimal tuning.
2. **SGD for SOTA.** If you need that last 1% of accuracy on a benchmark, switch to SGD + momentum + LR schedule.
3. **AdamW over Adam.** AdamW decouples weight decay properly — use it for transformers.
4. **Learning rate is the most important hyperparameter.** Getting it right matters more than optimizer choice.
5. **Always use a learning rate schedule for long training runs.** A decaying LR helps convergence to a better minimum.
6. Reduce LR by 10x when loss plateaus. This is the most reliable tuning trick.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Comparison.md](./Comparison.md) | Optimizers comparison (SGD, Adam, RMSProp) |

⬅️ **Prev:** [06 Backpropagation](../06_Backpropagation/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [08 Regularization](../08_Regularization/Theory.md)
