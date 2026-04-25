# 🎯 Project 3 — Neural Net from Scratch

## The Story

In Projects 1 and 2, you used scikit-learn. One line of code and a model appeared. But what actually happens inside `model.fit()`? What is backpropagation, really? When engineers say "the network learns," what does that mean mechanically?

Here is the uncomfortable truth: most people who use neural networks have never actually seen the math run. They type `model.compile()` and it works. But when something breaks — a loss that will not decrease, a gradient that explodes, a model that learns nothing — they are helpless, because they never understood what is actually happening under the hood.

This project removes that mystery. You will build a 2-layer neural network using nothing but numpy. No PyTorch, no TensorFlow, no shortcuts. You will write the forward pass yourself. You will implement ReLU yourself. You will derive and code the backpropagation equations yourself. You will update the weights yourself.

When you are done, you will have the deepest understanding of neural networks available to a beginner — the kind that makes everything else make sense. People who have built a neural net from scratch never struggle to understand the higher-level frameworks. They are the ones who explain things to everyone else.

---

## What You Build

A 2-layer MLP (Multi-Layer Perceptron) in pure numpy that:

1. Solves the XOR problem — a classic problem that linear models cannot solve
2. Implements a full forward pass: input → hidden layer (ReLU) → output layer (sigmoid)
3. Computes binary cross-entropy loss
4. Implements backpropagation — calculates gradients of the loss with respect to every weight
5. Updates weights using gradient descent
6. Plots the loss curve over training epochs

---

## The XOR Problem — Why It Matters

XOR (exclusive or) takes two binary inputs and returns 1 if they differ, 0 if they are the same:

| X1 | X2 | XOR output |
|---|---|---|
| 0 | 0 | 0 |
| 0 | 1 | 1 |
| 1 | 0 | 1 |
| 1 | 1 | 0 |

A single-layer network (a perceptron) cannot solve XOR — there is no straight line that separates the 1s from the 0s. This was a famous limitation discovered in 1969 that nearly killed neural network research. A 2-layer network solves it easily. Your project demonstrates exactly why layers matter.

---

## Concepts Covered

| Phase | Topic | Concept Applied |
|---|---|---|
| Phase 5 | Perceptron (Topic 17) | Single neuron: weighted sum + activation |
| Phase 5 | MLPs (Topic 18) | Stacking layers to solve non-linear problems |
| Phase 5 | Activation Functions (Topic 19) | ReLU in hidden layer, sigmoid in output |
| Phase 5 | Backpropagation (Topic 20) | Chain rule, gradient computation, weight updates |

---

## What Success Looks Like

```
=== Neural Network from Scratch — XOR ===

Architecture: 2 -> 4 -> 1
Activation: ReLU (hidden), Sigmoid (output)
Loss: Binary Cross-Entropy

Training for 10000 epochs...
Epoch      0 | Loss: 0.6931
Epoch   1000 | Loss: 0.5231
Epoch   5000 | Loss: 0.0234
Epoch  10000 | Loss: 0.0089

--- Predictions ---
Input [0, 0] -> 0.02 (expected 0)  CORRECT
Input [0, 1] -> 0.98 (expected 1)  CORRECT
Input [1, 0] -> 0.97 (expected 1)  CORRECT
Input [1, 1] -> 0.03 (expected 0)  CORRECT

Accuracy: 4/4 = 100.00%
Loss curve saved to: outputs/loss_curve.png
```

---

## Key Concepts to Lock In

- **Forward pass**: data flows through the network layer by layer to produce a prediction
- **ReLU**: max(0, x) — introduces non-linearity so the network can learn XOR
- **Backpropagation**: applies the chain rule backwards from the loss to compute every gradient
- **Gradient descent**: subtract a fraction of the gradient from each weight to reduce loss
- **Loss curve**: a smooth downward curve confirms healthy training

---

## Prerequisites

- Completed Projects 1 and 2 (or comfortable with numpy)
- Python 3.9+
- Libraries: `numpy`, `matplotlib` only (no scikit-learn — intentional)
- You have read: Perceptron Theory, MLPs Theory, Activation Functions Theory, Backpropagation Theory

---

## Learning Format

**Tier:** Beginner — Medium  
**Estimated time:** 4–6 hours. The math is the hard part; the code is short but each line requires real understanding.  
**Style:** Build in 8 stages. The backpropagation stage (Stage 5) is the hardest — give it extra time.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| 📄 **01_MISSION.md** | You are here |
| [📄 02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design and diagrams |
| [📄 03_GUIDE.md](./03_GUIDE.md) | Step-by-step build guide |
| [📄 src/starter.py](./src/starter.py) | Starter code with TODOs |
| [📄 04_RECAP.md](./04_RECAP.md) | Concepts recap and next steps |

⬅️ **Previous:** [02 — ML Model Comparison](../02_ML_Model_Comparison/01_MISSION.md)
➡️ **Next:** [04 — LLM Chatbot with Memory](../04_LLM_Chatbot_with_Memory/01_MISSION.md)
