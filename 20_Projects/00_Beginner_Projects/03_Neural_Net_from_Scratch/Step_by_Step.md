# Project 3 — Step-by-Step Build Guide

## Overview

You'll build a neural network piece by piece, testing each component in isolation before assembling the full training loop. Every step maps to a specific mathematical concept from the theory.

**Total estimated time:** 4–6 hours. Spend extra time with the backprop section — it's the hardest and most valuable part.

---

## Before You Start — Environment Setup

### Step 1: Set up your environment

```bash
mkdir -p ~/ai-projects/03_neural_net
cd ~/ai-projects/03_neural_net
python -m venv venv
source venv/bin/activate
pip install numpy matplotlib
mkdir outputs
```

### Step 2: Understand the XOR dataset

XOR is tiny — 4 samples, 2 features, binary labels. The entire dataset fits in 4 lines:

```python
import numpy as np

X = np.array([[0, 0],
              [0, 1],
              [1, 0],
              [1, 1]])   # shape: (4, 2)

y = np.array([[0],
              [1],
              [1],
              [0]])      # shape: (4, 1)
```

Notice the shapes: X is (4, 2) meaning 4 samples with 2 features each. y is (4, 1). Getting shapes right is the most common source of bugs in neural networks.

---

## Stage 1 — Implement Activation Functions

**Goal:** Write ReLU and sigmoid as standalone numpy functions.

**Concept applied:** Activation functions are what make neural networks non-linear. Without them, stacking layers is the same as one layer — you'd just be multiplying matrices together, which collapses to a single linear operation. ReLU and sigmoid break this — they introduce non-linearity, which is what allows networks to learn complex patterns like XOR.

### Step 3: Implement ReLU

ReLU stands for Rectified Linear Unit. It's simple: max(0, x).

```python
def relu(Z):
    """
    Apply ReLU activation element-wise.
    ReLU(x) = max(0, x)
    """
    return np.maximum(0, Z)

def relu_derivative(Z):
    """
    Derivative of ReLU.
    d/dx ReLU(x) = 1 if x > 0 else 0
    This is used in backpropagation.
    """
    return (Z > 0).astype(float)
```

Test it:
```python
Z_test = np.array([-2, -1, 0, 1, 2])
print(relu(Z_test))           # [0. 0. 0. 1. 2.]
print(relu_derivative(Z_test)) # [0. 0. 0. 1. 1.]
```

### Step 4: Implement Sigmoid

Sigmoid maps any number to a value between 0 and 1, making it perfect for a binary output (probability of class 1).

```python
def sigmoid(Z):
    """
    Apply sigmoid activation element-wise.
    sigmoid(x) = 1 / (1 + exp(-x))
    Output is always between 0 and 1.
    """
    return 1 / (1 + np.exp(-Z))
```

Test it:
```python
print(sigmoid(0))    # 0.5  — at zero, probability is 50/50
print(sigmoid(10))   # ~1.0 — very confident it's class 1
print(sigmoid(-10))  # ~0.0 — very confident it's class 0
```

---

## Stage 2 — Initialize Weights

**Goal:** Create randomly initialized weight matrices and bias vectors.

**Concept applied:** Weights are the learnable parameters of the network. You initialize them to small random values — not zeros. If all weights start at zero, every neuron computes the same output and gradient, so they all learn the same thing and the network never breaks symmetry. Small random values break symmetry so each neuron specializes.

### Step 5: Understand the architecture dimensions

Your network: 2 inputs -> 4 hidden neurons -> 1 output

```
W1: shape (2, 4)  — transforms 2 input features to 4 hidden neurons
b1: shape (1, 4)  — one bias per hidden neuron
W2: shape (4, 1)  — transforms 4 hidden neurons to 1 output
b2: shape (1, 1)  — one bias for the output neuron
```

### Step 6: Initialize the parameters

```python
def initialize_parameters(n_input, n_hidden, n_output, seed=42):
    """
    Initialize weights randomly and biases to zero.
    Returns a dict with keys: W1, b1, W2, b2
    """
    np.random.seed(seed)

    W1 = np.random.randn(n_input, n_hidden) * 0.01
    b1 = np.zeros((1, n_hidden))
    W2 = np.random.randn(n_hidden, n_output) * 0.01
    b2 = np.zeros((1, n_output))

    return {"W1": W1, "b1": b1, "W2": W2, "b2": b2}

params = initialize_parameters(2, 4, 1)
print("W1 shape:", params["W1"].shape)  # (2, 4)
print("W2 shape:", params["W2"].shape)  # (4, 1)
```

**Why multiply by 0.01?** Large initial weights cause large activations, which lead to very large or very small gradients. Small initial weights help training start smoothly.

---

## Stage 3 — Forward Pass

**Goal:** Compute the network's output for a given input.

**Concept applied:** The forward pass is how the network makes a prediction. Data flows forward through the network: inputs are multiplied by weights, biases are added, activations are applied, and the final output is a probability. No learning happens here — this is pure prediction.

### Step 7: Implement the forward pass

```python
def forward_pass(X, params):
    """
    Compute the forward pass of the network.

    Layer 1: Z1 = X @ W1 + b1   (linear combination)
             A1 = relu(Z1)       (non-linear activation)
    Layer 2: Z2 = A1 @ W2 + b2  (linear combination)
             A2 = sigmoid(Z2)    (output probability)

    Returns:
        A2: output predictions, shape (m, 1)
        cache: dict of intermediate values needed for backprop
    """
    W1, b1, W2, b2 = params["W1"], params["b1"], params["W2"], params["b2"]

    Z1 = X @ W1 + b1   # (m, 2) @ (2, 4) + (1, 4) = (m, 4)
    A1 = relu(Z1)      # (m, 4) — same shape, applied element-wise
    Z2 = A1 @ W2 + b2  # (m, 4) @ (4, 1) + (1, 1) = (m, 1)
    A2 = sigmoid(Z2)   # (m, 1) — output probabilities

    cache = {"Z1": Z1, "A1": A1, "Z2": Z2, "A2": A2, "X": X}
    return A2, cache
```

### Step 8: Test the forward pass

```python
params = initialize_parameters(2, 4, 1)
A2, cache = forward_pass(X, params)
print("Output shape:", A2.shape)  # (4, 1)
print("First prediction:", A2[0]) # Should be close to 0.5 (random weights)
```

---

## Stage 4 — Compute Loss

**Goal:** Measure how wrong the network's predictions are.

**Concept applied:** Binary cross-entropy loss penalizes the network for wrong confident predictions more than uncertain ones. If the network predicts 0.99 for a sample that should be 0, the loss is huge. If it predicts 0.5, the loss is moderate. This is the signal that drives learning.

### Step 9: Implement binary cross-entropy

```python
def compute_loss(A2, y):
    """
    Binary cross-entropy loss.
    L = -mean(y * log(A2) + (1-y) * log(1-A2))

    This measures how far the predictions A2 are from the true labels y.
    """
    m = y.shape[0]
    epsilon = 1e-8  # Small constant to prevent log(0)

    loss = -np.mean(y * np.log(A2 + epsilon) + (1 - y) * np.log(1 - A2 + epsilon))
    return loss
```

### Step 10: Verify the loss

```python
# For random predictions (~0.5), loss should be near log(2) ≈ 0.693
A2, cache = forward_pass(X, params)
loss = compute_loss(A2, y)
print(f"Initial loss: {loss:.4f}")  # Should be ~0.69
```

An initial loss near 0.693 is correct — it's what you get when predictions are 50/50 (maximum uncertainty).

---

## Stage 5 — Backpropagation

**Goal:** Compute how much each weight contributed to the loss.

**Concept applied:** Backpropagation applies the chain rule of calculus to efficiently compute the gradient of the loss with respect to every weight in the network. It works backwards from the output error, layer by layer, each time multiplying by the derivative of that layer's activation function. This is the heart of all neural network training.

### Step 11: Implement backpropagation

Work through each gradient step carefully. Read the comment above each line.

```python
def backward_pass(params, cache, y):
    """
    Compute gradients of the loss with respect to all parameters.
    Uses the chain rule, working backwards from the output.

    Returns:
        grads: dict with keys dW1, db1, dW2, db2
    """
    m = y.shape[0]  # number of samples

    W2 = params["W2"]
    Z1, A1, A2, X = cache["Z1"], cache["A1"], cache["A2"], cache["X"]

    # --- Output layer gradients ---
    # dL/dZ2: derivative of BCE loss w.r.t. Z2 before sigmoid
    # When sigmoid is the output activation and BCE is the loss,
    # these simplify beautifully to: (A2 - y)
    dZ2 = A2 - y                          # shape (m, 1)

    # dL/dW2: how much does each weight in W2 contribute to the loss?
    dW2 = (A1.T @ dZ2) / m               # shape (4, 1)

    # dL/db2: average of all output errors
    db2 = np.mean(dZ2, axis=0, keepdims=True)   # shape (1, 1)

    # --- Hidden layer gradients ---
    # Pass the error signal backwards through W2
    dA1 = dZ2 @ W2.T                     # shape (m, 4)

    # Apply the ReLU gate: neurons with Z1 <= 0 had zero output,
    # so they contribute zero gradient (the gate is closed)
    dZ1 = dA1 * relu_derivative(Z1)      # shape (m, 4)

    # dL/dW1: how much does each weight in W1 contribute?
    dW1 = (X.T @ dZ1) / m               # shape (2, 4)

    # dL/db1
    db1 = np.mean(dZ1, axis=0, keepdims=True)   # shape (1, 4)

    return {"dW1": dW1, "db1": db1, "dW2": dW2, "db2": db2}
```

### Step 12: Verify gradient shapes

```python
A2, cache = forward_pass(X, params)
grads = backward_pass(params, cache, y)

print("dW1 shape:", grads["dW1"].shape)  # (2, 4) — matches W1
print("dW2 shape:", grads["dW2"].shape)  # (4, 1) — matches W2
```

Gradient shapes must always match the shape of the weights they correspond to.

---

## Stage 6 — Weight Update

**Goal:** Adjust the weights to reduce the loss.

**Concept applied:** Gradient descent moves each weight in the direction that reduces the loss. The learning rate controls how big each step is. Too large and you overshoot. Too small and training is very slow.

### Step 13: Implement the update step

```python
def update_parameters(params, grads, learning_rate):
    """
    Update weights and biases using gradient descent.
    W = W - learning_rate * dW
    b = b - learning_rate * db
    """
    params["W1"] -= learning_rate * grads["dW1"]
    params["b1"] -= learning_rate * grads["db1"]
    params["W2"] -= learning_rate * grads["dW2"]
    params["b2"] -= learning_rate * grads["db2"]
    return params
```

---

## Stage 7 — Training Loop

**Goal:** Combine forward pass, loss, backprop, and update into a training loop.

**Concept applied:** One pass through the entire dataset is called an **epoch**. You run many epochs, and with each pass the weights get a little better. The loss curve shows you whether training is working.

### Step 14: Implement the training loop

```python
def train(X, y, n_hidden=4, learning_rate=0.1, epochs=10000, print_every=1000):
    """
    Full training loop: initialize, then repeat forward/backward/update.
    Returns trained parameters and loss history.
    """
    n_input = X.shape[1]
    n_output = y.shape[1]

    # Initialize
    params = initialize_parameters(n_input, n_hidden, n_output)
    loss_history = []

    for epoch in range(epochs + 1):
        # Forward pass
        A2, cache = forward_pass(X, params)

        # Compute loss
        loss = compute_loss(A2, y)
        loss_history.append(loss)

        # Backpropagation
        grads = backward_pass(params, cache, y)

        # Update weights
        params = update_parameters(params, grads, learning_rate)

        # Print progress
        if epoch % print_every == 0:
            print(f"Epoch {epoch:6d} | Loss: {loss:.4f}")

    return params, loss_history
```

### Step 15: Train on XOR

```python
params, loss_history = train(X, y, n_hidden=4, learning_rate=0.5, epochs=10000)
```

---

## Stage 8 — Evaluate and Plot

### Step 16: Make predictions and check accuracy

```python
def predict(X, params, threshold=0.5):
    """Make binary predictions (0 or 1) from the trained network."""
    A2, _ = forward_pass(X, params)
    return (A2 >= threshold).astype(int)

y_pred = predict(X, params)
for i in range(len(X)):
    status = "CORRECT" if y_pred[i] == y[i] else "WRONG"
    print(f"Input {X[i]} -> {float(forward_pass(X[params] if False else X, params)[0][i]):.2f} (expected {y[i][0]})  {status}")

accuracy = (y_pred == y).mean()
print(f"\nAccuracy: {int(accuracy * len(y))}/{len(y)} = {accuracy * 100:.2f}%")
```

### Step 17: Plot the loss curve

```python
import matplotlib.pyplot as plt

plt.figure(figsize=(8, 5))
plt.plot(loss_history, color='steelblue', linewidth=1.5)
plt.title('Training Loss — XOR Neural Network')
plt.xlabel('Epoch')
plt.ylabel('Binary Cross-Entropy Loss')
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("outputs/loss_curve.png")
plt.close()
print("Loss curve saved to: outputs/loss_curve.png")
```

A good training run shows the loss starting near 0.693 and smoothly decreasing toward near zero.

### Step 18: Run everything

```bash
python neural_net.py
```

Confirm:
- Loss decreases from ~0.69 to near 0.01 or below
- All 4 XOR predictions are correct
- Loss curve PNG saved

---

## Extend the Project

### Extension 1 — Try Different Learning Rates

Change learning_rate from 0.5 to 0.01 and 2.0. Observe:
- Too low (0.01): training converges very slowly
- Too high (2.0): training may diverge (loss goes up instead of down)

### Extension 2 — Add More Hidden Neurons

Change `n_hidden` from 4 to 2, then to 8. Does XOR still work with only 2 neurons? Why?

### Extension 3 — MNIST (Advanced)

Load MNIST from sklearn, flatten the 28x28 images to 784-dim vectors, change the output to 10 neurons with softmax, and re-derive the backprop equations for multi-class.

---

## 📂 Navigation

| File | |
|---|---|
| [Project_Guide.md](./Project_Guide.md) | Overview and objectives |
| **Step_by_Step.md** | You are here |
| [Starter_Code.md](./Starter_Code.md) | Python starter code with TODOs |
| [Architecture_Blueprint.md](./Architecture_Blueprint.md) | System diagram |
