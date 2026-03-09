# Backpropagation — Cheatsheet

**One-liner:** Backpropagation computes the gradient of the loss with respect to every weight in the network by applying the chain rule backward from output to input — enabling gradient-based weight updates.

---

## Key Terms

| Term | What it means |
|------|---------------|
| Gradient | How much the loss changes when a specific weight changes |
| Chain rule | Mathematical rule for computing derivatives of compositions of functions |
| dL/dW | Gradient of loss with respect to weight W — tells you how to update W |
| Backward pass | Running backpropagation after the forward pass |
| Learning rate (lr) | How big a step to take when updating weights |
| Vanishing gradient | Gradients shrink to near-zero as they travel back through many layers |
| Exploding gradient | Gradients grow to extremely large numbers, causing unstable training |
| Gradient clipping | Cap gradients at a maximum value to prevent explosion |

---

## The Update Rule

```
w_new = w_old - learning_rate × (dL/dW)

If dL/dW > 0: weight is increased the loss, so decrease it
If dL/dW < 0: weight decreased the loss, so increase it
```

---

## One Training Step (Full Loop)

```
1. Forward pass:
   x → Layer 1 → Layer 2 → ŷ
   Loss L = loss(ŷ, y)

2. Backward pass (backprop):
   dL/dŷ          ← gradient of loss w.r.t. output
   dL/dz2         ← chain rule through output activation
   dL/dW2, dL/db2 ← gradients for layer 2 weights
   dL/da1         ← gradient flowing back to layer 1
   dL/dz1         ← chain rule through layer 1 activation
   dL/dW1, dL/db1 ← gradients for layer 1 weights

3. Update:
   W2 -= lr × dL/dW2
   b2 -= lr × dL/db2
   W1 -= lr × dL/dW1
   b1 -= lr × dL/db1
```

---

## Key Derivatives to Remember

| Operation | Derivative |
|-----------|-----------|
| Sigmoid: σ(z) | σ(z) × (1 - σ(z)) — max 0.25, causes vanishing grad |
| Tanh: tanh(z) | 1 - tanh²(z) — max 1.0, still saturates |
| ReLU: max(0,z) | 1 if z>0, else 0 — clean, no vanishing |
| MSE loss | 2 × (ŷ - y) / n |
| BCE loss w.r.t. ŷ | ŷ - y (after combining sigmoid + BCE) |

---

## When to Use / Not Use

| Aspect | Notes |
|--------|-------|
| Backprop runs during training | Every training step: forward → loss → backward → update |
| Backprop does NOT run at inference | At prediction time, only the forward pass runs |
| Backprop requires differentiable operations | Non-differentiable operations (like argmax) block gradient flow |
| Detach or stop_gradient | Use when you don't want gradients to flow through part of a graph |

---

## Golden Rules

1. Backprop is just the chain rule applied efficiently — one backward pass, all gradients computed.
2. The gradient tells the direction and magnitude of the update for each weight.
3. ReLU solved vanishing gradients for most networks — prefer it over sigmoid in hidden layers.
4. Gradient clipping is a cheap fix for exploding gradients — use it in RNNs.
5. In PyTorch: `loss.backward()` runs backprop. `optimizer.step()` applies the updates. `optimizer.zero_grad()` clears old gradients before the next step. Missing `zero_grad()` is a common bug.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Math_Walkthrough.md](./Math_Walkthrough.md) | Step-by-step math walkthrough |

⬅️ **Prev:** [05 Forward Propagation](../05_Forward_Propagation/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [07 Optimizers](../07_Optimizers/Theory.md)
