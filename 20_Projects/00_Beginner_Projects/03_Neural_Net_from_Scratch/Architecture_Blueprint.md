# Project 3 — Architecture Blueprint

## System Overview

This project implements a **2-layer Multi-Layer Perceptron (MLP)** using only numpy. The architecture is minimal by design — enough to solve XOR, small enough to understand every parameter.

---

## Network Architecture Diagram

```mermaid
flowchart LR
    subgraph Input["Input Layer (2 neurons)"]
        X1["x₁"]
        X2["x₂"]
    end

    subgraph Hidden["Hidden Layer (4 neurons)"]
        H1["h₁"]
        H2["h₂"]
        H3["h₃"]
        H4["h₄"]
    end

    subgraph Output["Output Layer (1 neuron)"]
        O1["ŷ"]
    end

    X1 --> H1
    X1 --> H2
    X1 --> H3
    X1 --> H4
    X2 --> H1
    X2 --> H2
    X2 --> H3
    X2 --> H4
    H1 --> O1
    H2 --> O1
    H3 --> O1
    H4 --> O1

    note1["W1: shape 2×4\n8 weights + 4 biases"]
    note2["W2: shape 4×1\n4 weights + 1 bias"]
```

---

## Training Pipeline

```mermaid
flowchart TD
    A[XOR Dataset\nX: 4×2, y: 4×1] --> B[Initialize Weights\nW1 2×4, W2 4×1\nSmall random values]
    B --> C[Training Loop\n10000 epochs]

    C --> D[Forward Pass\nZ1 = X at W1 + b1\nA1 = relu-Z1\nZ2 = A1 at W2 + b2\nA2 = sigmoid-Z2]

    D --> E[Compute Loss\nBinary Cross-Entropy\nL = -mean log-likelihood]

    E --> F[Backward Pass\nChain rule\nCompute dW1 dW2 db1 db2]

    F --> G[Update Weights\nW = W - lr times dW\nb = b - lr times db]

    G --> H{epoch done?}
    H -- more epochs --> D
    H -- training done --> I[Final Predictions\npredict-X-params]
    I --> J[Evaluation\naccuracy on XOR]
    I --> K[Loss Curve Plot\noutputs/loss_curve.png]
```

---

## Forward Pass: Data Shapes at Each Step

```mermaid
flowchart LR
    A["X\n4 × 2"] -- "@ W1 (2×4) + b1 (1×4)" --> B["Z1\n4 × 4"]
    B -- "relu()" --> C["A1\n4 × 4"]
    C -- "@ W2 (4×1) + b2 (1×1)" --> D["Z2\n4 × 1"]
    D -- "sigmoid()" --> E["A2\n4 × 1\nprobabilities"]
```

---

## Backpropagation: Gradient Flow

```mermaid
flowchart RL
    A2["A2 - y\ndZ2: 4×1\nOutput error"] --> dW2["dW2 = A1.T at dZ2 / m\n4×1"]
    A2 --> db2["db2 = mean-dZ2\n1×1"]
    A2 -- "dZ2 @ W2.T" --> dA1["dA1: 4×4\nHidden error"]
    dA1 -- "times relu_deriv-Z1" --> dZ1["dZ1: 4×4\nGated gradient"]
    dZ1 --> dW1["dW1 = X.T at dZ1 / m\n2×4"]
    dZ1 --> db1["db1 = mean-dZ1\n1×4"]
```

---

## Component Table

| Component | Function | Math Operation | Key Shape |
|---|---|---|---|
| Input | Raw data | — | (4, 2) |
| Layer 1 Linear | `Z1 = X @ W1 + b1` | Matrix multiply + broadcast | (4, 4) |
| ReLU Activation | `A1 = relu(Z1)` | Element-wise max(0, x) | (4, 4) |
| Layer 2 Linear | `Z2 = A1 @ W2 + b2` | Matrix multiply + broadcast | (4, 1) |
| Sigmoid Activation | `A2 = sigmoid(Z2)` | Element-wise 1/(1+e^-x) | (4, 1) |
| BCE Loss | `compute_loss(A2, y)` | -mean log-likelihood | scalar |
| Output grad | `dZ2 = A2 - y` | Subtraction | (4, 1) |
| W2 gradient | `dW2 = A1.T @ dZ2 / m` | Matrix multiply | (4, 1) |
| Hidden error | `dA1 = dZ2 @ W2.T` | Matrix multiply | (4, 4) |
| ReLU gate | `dZ1 = dA1 * relu_deriv(Z1)` | Element-wise multiply | (4, 4) |
| W1 gradient | `dW1 = X.T @ dZ1 / m` | Matrix multiply | (2, 4) |
| Update | `W -= lr * dW` | Element-wise subtract | same as W |

---

## Why XOR Needs Two Layers

```mermaid
flowchart TD
    subgraph OneLayer["Single Layer (Perceptron) — FAILS"]
        P1[Draw one straight line\nthrough 4 XOR points]
        P2[Impossible: points are\nnot linearly separable]
        P1 --> P2
    end

    subgraph TwoLayer["Two Layers (MLP) — WORKS"]
        T1[Hidden layer creates\ntwo internal boundaries]
        T2[Output layer combines them\nto isolate XOR=1 region]
        T1 --> T2
    end
```

The hidden layer transforms the input space into a new representation where the problem *becomes* linearly separable. Then the output layer draws the final boundary in that transformed space.

---

## Parameters Count

| Parameter | Shape | Count |
|---|---|---|
| W1 | (2, 4) | 8 |
| b1 | (1, 4) | 4 |
| W2 | (4, 1) | 4 |
| b2 | (1, 1) | 1 |
| **Total** | | **17** |

This tiny network has only 17 learnable parameters — yet it solves XOR perfectly. Modern LLMs have billions of parameters solving incomparably harder problems, but the same fundamental algorithm (forward pass, backpropagation, gradient descent) applies.

---

## Concepts Map

```mermaid
flowchart TD
    T17[Topic 17 — Perceptron] --> C1[Single neuron = weighted sum + activation\nOne such neuron per hidden/output unit]
    T18[Topic 18 — MLPs] --> C2[Stack of layers\nHidden layer enables non-linear boundary]
    T19[Topic 19 — Activation Functions] --> C3[ReLU in hidden: relu and relu_derivative\nSigmoid at output: probability output]
    T20[Topic 20 — Backpropagation] --> C4[backward_pass function\nChain rule: dZ2 dW2 dA1 dZ1 dW1]
    C1 --> F[forward_pass function]
    C2 --> F
    C3 --> F
    C4 --> G[update_parameters function]
    F --> H[Training Loop: loss decreases to 0]
    G --> H
```

---

## Folder Structure

```
03_Neural_Net_from_Scratch/
├── neural_net.py              ← Your main Python script
├── outputs/
│   └── loss_curve.png
├── Project_Guide.md
├── Step_by_Step.md
├── Starter_Code.md
└── Architecture_Blueprint.md
```

---

## 📂 Navigation

| File | |
|---|---|
| [Project_Guide.md](./Project_Guide.md) | Overview and objectives |
| [Step_by_Step.md](./Step_by_Step.md) | Detailed build instructions |
| [Starter_Code.md](./Starter_Code.md) | Python starter code with TODOs |
| **Architecture_Blueprint.md** | You are here |
