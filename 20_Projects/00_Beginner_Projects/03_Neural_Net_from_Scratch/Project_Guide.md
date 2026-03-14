# Project 3 — Neural Net from Scratch

## The Story: Why This Project Matters

In Projects 1 and 2, you used scikit-learn. One line of code and a model appeared. But what actually happens inside `model.fit()`? What is backpropagation, really? When engineers say "the network learns," what does that mean mechanically?

Here's the uncomfortable truth: most people who use neural networks have never actually seen the math run. They type `model.compile()` and it works. But when something breaks — a loss that won't decrease, a gradient that explodes, a model that learns nothing — they're helpless, because they never understood what's actually happening under the hood.

This project removes that mystery. You'll build a 2-layer neural network using **nothing but numpy**. No PyTorch, no TensorFlow, no shortcuts. You'll write the forward pass yourself. You'll implement ReLU yourself. You'll derive and code the backpropagation equations yourself. You'll update the weights yourself.

When you're done, you'll have the deepest understanding of neural networks available to a beginner — the kind that makes everything else make sense. People who have built a neural net from scratch never struggle to understand the higher-level frameworks. They're the ones who explain things to everyone else.

---

## What You'll Build

A 2-layer MLP (Multi-Layer Perceptron) in pure numpy that:

1. Solves the XOR problem — a classic problem that linear models cannot solve
2. Implements a full forward pass: input -> hidden layer (ReLU) -> output layer (sigmoid)
3. Computes binary cross-entropy loss
4. Implements backpropagation — calculates gradients of the loss with respect to every weight
5. Updates weights using gradient descent
6. Plots the loss curve over training epochs
7. (Optional) Generalizes to MNIST for a bigger challenge

---

## Learning Objectives

By completing this project, you will be able to:

- Explain what a forward pass does and implement it in numpy
- Describe what ReLU does and why it's used instead of a linear activation
- Compute binary cross-entropy loss and explain what it measures
- Explain the chain rule and how backpropagation applies it layer-by-layer
- Update weights using gradient descent and explain each term in the update rule
- Recognize the signs of a healthy vs. stuck training run from a loss curve

---

## Topics Covered

| Phase | Topic | Concept Applied |
|---|---|---|
| Phase 5 | Perceptron (Topic 17) | Single neuron: weighted sum + activation |
| Phase 5 | MLPs (Topic 18) | Stacking layers to solve non-linear problems |
| Phase 5 | Activation Functions (Topic 19) | ReLU in hidden layer, sigmoid in output |
| Phase 5 | Backpropagation (Topic 20) | Chain rule, gradient computation, weight updates |

---

## Prerequisites

- Completed Projects 1 and 2 (or comfortable with numpy)
- Python 3.9+
- Library: `numpy` only (plus `matplotlib` for the loss curve)
- You've read: Perceptron Theory, MLPs Theory, Activation Functions Theory, Backpropagation Theory

---

## Difficulty

Medium — 4–6 hours. The math is the hard part. The code is short but each line requires real understanding.

---

## Tools & Libraries

| Tool | Purpose |
|---|---|
| `numpy` | ALL math: matrix multiplication, activation functions, gradients |
| `matplotlib` | Loss curve plot |

Note: No scikit-learn, no PyTorch, no TensorFlow. This is intentional.

---

## The XOR Problem — Why It Matters

XOR (exclusive or) takes two binary inputs and returns 1 if they differ, 0 if they're the same:

| X1 | X2 | XOR output |
|---|---|---|
| 0 | 0 | 0 |
| 0 | 1 | 1 |
| 1 | 0 | 1 |
| 1 | 1 | 0 |

A single-layer network (a perceptron) **cannot** solve XOR — there's no straight line that separates the 1s from the 0s. This was a famous limitation discovered in 1969 that nearly killed neural network research. A 2-layer network solves it easily. Your project demonstrates exactly why layers matter.

---

## Expected Output

```
=== Neural Network from Scratch — XOR ===

Architecture: 2 -> 4 -> 1
Activation: ReLU (hidden), Sigmoid (output)
Loss: Binary Cross-Entropy

Training for 10000 epochs...
Epoch    0 | Loss: 0.6931
Epoch 1000 | Loss: 0.5231
Epoch 2000 | Loss: 0.2847
Epoch 5000 | Loss: 0.0234
Epoch 10000 | Loss: 0.0089

--- Predictions ---
Input [0, 0] -> 0.02 (expected 0)  CORRECT
Input [0, 1] -> 0.98 (expected 1)  CORRECT
Input [1, 0] -> 0.97 (expected 1)  CORRECT
Input [1, 1] -> 0.03 (expected 0)  CORRECT

Accuracy: 4/4 = 100.00%
Loss curve saved to: outputs/loss_curve.png
```

---

## Key Learning: The Math You'll Implement

### Forward Pass
```
Z1 = X @ W1 + b1          # Linear transformation, hidden layer
A1 = ReLU(Z1)             # Non-linear activation
Z2 = A1 @ W2 + b2         # Linear transformation, output layer
A2 = sigmoid(Z2)          # Output probability (0 to 1)
```

### Loss
```
L = -mean(y * log(A2) + (1 - y) * log(1 - A2))   # Binary cross-entropy
```

### Backpropagation (chain rule)
```
dL/dZ2 = A2 - y                                    # Output error
dL/dW2 = A1.T @ dZ2 / m                           # Gradient for W2
dL/db2 = mean(dZ2)                                 # Gradient for b2
dL/dA1 = dZ2 @ W2.T                               # Pass error back
dL/dZ1 = dA1 * relu_derivative(Z1)               # Apply ReLU gate
dL/dW1 = X.T @ dZ1 / m                            # Gradient for W1
dL/db1 = mean(dZ1)                                 # Gradient for b1
```

### Weight Update
```
W -= learning_rate * dW    # Move weights in the direction that reduces loss
b -= learning_rate * db
```

---

## Extension Challenges

1. Try training on MNIST (28x28 images, 10 classes) — needs multi-class output with softmax
2. Add a second hidden layer and observe whether loss decreases faster
3. Implement momentum — a modification to gradient descent that helps escape flat regions
4. Plot the decision boundary for XOR using a color mesh plot

---

## 📂 Navigation

| File | |
|---|---|
| **Project_Guide.md** | You are here — overview and objectives |
| [Step_by_Step.md](./Step_by_Step.md) | Detailed build instructions |
| [Starter_Code.md](./Starter_Code.md) | Python starter code with TODOs |
| [Architecture_Blueprint.md](./Architecture_Blueprint.md) | System diagram |

**Project Series:** Project 3 of 5 — Beginner Projects
⬅️ **Previous:** [02 — ML Model Comparison](../02_ML_Model_Comparison/Project_Guide.md)
➡️ **Next:** [04 — LLM Chatbot with Memory](../04_LLM_Chatbot_with_Memory/Project_Guide.md)
