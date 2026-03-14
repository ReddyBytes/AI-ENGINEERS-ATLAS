# Project 3 — Starter Code

Copy this to `neural_net.py`. Fill in every `# TODO:` section.
This is the hardest project in the beginner series — take your time with backpropagation.

---

```python
"""
Project 3 — Neural Network from Scratch
=========================================
A 2-layer MLP built using only numpy.
Solves the XOR problem to demonstrate that layers
enable non-linear decision boundaries.

Architecture: 2 -> 4 -> 1
Activations: ReLU (hidden), Sigmoid (output)
Loss: Binary Cross-Entropy

Libraries required: pip install numpy matplotlib
"""

import numpy as np
import matplotlib.pyplot as plt
import os


# ============================================================
# SECTION 1 — DATASET
# ============================================================

# XOR truth table
X = np.array([[0, 0],
              [0, 1],
              [1, 0],
              [1, 1]], dtype=float)   # shape (4, 2)

y = np.array([[0],
              [1],
              [1],
              [0]], dtype=float)      # shape (4, 1)


# ============================================================
# SECTION 2 — ACTIVATION FUNCTIONS
# ============================================================

def relu(Z: np.ndarray) -> np.ndarray:
    """
    ReLU activation: max(0, Z), applied element-wise.

    Args:
        Z: numpy array of any shape

    Returns:
        array of same shape with all negative values set to 0
    """
    # TODO: return np.maximum(0, Z)
    pass  # TODO: replace


def relu_derivative(Z: np.ndarray) -> np.ndarray:
    """
    Derivative of ReLU, applied element-wise.
    Returns 1.0 where Z > 0, else 0.0.
    Used in backpropagation to "gate" gradients.

    Args:
        Z: the pre-activation values (before ReLU was applied)

    Returns:
        binary array: 1.0 where Z > 0, 0.0 elsewhere
    """
    # TODO: return (Z > 0).astype(float)
    pass  # TODO: replace


def sigmoid(Z: np.ndarray) -> np.ndarray:
    """
    Sigmoid activation: 1 / (1 + exp(-Z)), applied element-wise.
    Maps any value to (0, 1) — interpret as probability.

    Args:
        Z: numpy array of any shape

    Returns:
        array of same shape with values in (0, 1)
    """
    # TODO: return 1 / (1 + np.exp(-Z))
    pass  # TODO: replace


# ============================================================
# SECTION 3 — PARAMETER INITIALIZATION
# ============================================================

def initialize_parameters(n_input: int, n_hidden: int,
                           n_output: int, seed: int = 42) -> dict:
    """
    Initialize weight matrices and bias vectors.

    Weight shapes:
        W1: (n_input, n_hidden)   — input to hidden
        b1: (1, n_hidden)          — hidden bias
        W2: (n_hidden, n_output)  — hidden to output
        b2: (1, n_output)          — output bias

    Weights are initialized to small random values (* 0.01).
    Biases are initialized to zeros.

    Args:
        n_input:  number of input features (2 for XOR)
        n_hidden: number of hidden neurons (4 by default)
        n_output: number of output neurons (1 for binary)
        seed:     random seed for reproducibility

    Returns:
        dict with keys: W1, b1, W2, b2
    """
    np.random.seed(seed)

    # TODO: Initialize W1 as a random matrix of shape (n_input, n_hidden) * 0.01
    W1 = None  # TODO: np.random.randn(n_input, n_hidden) * 0.01

    # TODO: Initialize b1 as zeros of shape (1, n_hidden)
    b1 = None  # TODO: np.zeros((1, n_hidden))

    # TODO: Initialize W2 as a random matrix of shape (n_hidden, n_output) * 0.01
    W2 = None  # TODO: np.random.randn(n_hidden, n_output) * 0.01

    # TODO: Initialize b2 as zeros of shape (1, n_output)
    b2 = None  # TODO: np.zeros((1, n_output))

    return {"W1": W1, "b1": b1, "W2": W2, "b2": b2}


# ============================================================
# SECTION 4 — FORWARD PASS
# ============================================================

def forward_pass(X: np.ndarray, params: dict) -> tuple:
    """
    Compute the network's output for input X.

    Steps:
        Z1 = X @ W1 + b1      (linear: input -> hidden)
        A1 = relu(Z1)          (activation: hidden)
        Z2 = A1 @ W2 + b2     (linear: hidden -> output)
        A2 = sigmoid(Z2)       (activation: output probability)

    Args:
        X:      input array, shape (m, n_input) where m = number of samples
        params: dict with W1, b1, W2, b2

    Returns:
        A2:    output predictions, shape (m, n_output)
        cache: dict of intermediate values needed for backprop
               keys: Z1, A1, Z2, A2, X
    """
    W1, b1, W2, b2 = params["W1"], params["b1"], params["W2"], params["b2"]

    # TODO: Compute Z1 = X @ W1 + b1
    # Hint: Use the @ operator for matrix multiplication
    Z1 = None  # TODO

    # TODO: Apply relu activation to Z1 to get A1
    A1 = None  # TODO

    # TODO: Compute Z2 = A1 @ W2 + b2
    Z2 = None  # TODO

    # TODO: Apply sigmoid activation to Z2 to get A2 (output probabilities)
    A2 = None  # TODO

    cache = {"Z1": Z1, "A1": A1, "Z2": Z2, "A2": A2, "X": X}
    return A2, cache


# ============================================================
# SECTION 5 — LOSS FUNCTION
# ============================================================

def compute_loss(A2: np.ndarray, y: np.ndarray) -> float:
    """
    Binary Cross-Entropy loss.

    Formula:
        L = -mean(y * log(A2) + (1 - y) * log(1 - A2))

    Args:
        A2: predictions, shape (m, 1), values in (0, 1)
        y:  true labels, shape (m, 1), values are 0 or 1

    Returns:
        scalar loss value (float)
    """
    epsilon = 1e-8  # Prevent log(0) — never remove this!

    # TODO: Implement binary cross-entropy loss using the formula above
    # Hint: np.mean(-( y * np.log(A2 + epsilon) + (1 - y) * np.log(1 - A2 + epsilon) ))
    loss = None  # TODO

    return float(loss)


# ============================================================
# SECTION 6 — BACKPROPAGATION
# ============================================================

def backward_pass(params: dict, cache: dict, y: np.ndarray) -> dict:
    """
    Compute gradients of the loss w.r.t. all parameters using backprop.

    Chain rule, working backwards:

    Output layer:
        dZ2 = A2 - y                         (gradient of BCE + sigmoid)
        dW2 = (A1.T @ dZ2) / m
        db2 = mean(dZ2, axis=0)

    Hidden layer:
        dA1 = dZ2 @ W2.T                     (pass error back through W2)
        dZ1 = dA1 * relu_derivative(Z1)      (gate through ReLU)
        dW1 = (X.T @ dZ1) / m
        db1 = mean(dZ1, axis=0)

    Args:
        params: dict with W1, b1, W2, b2
        cache:  dict with Z1, A1, Z2, A2, X (from forward_pass)
        y:      true labels, shape (m, 1)

    Returns:
        grads: dict with keys dW1, db1, dW2, db2
    """
    m = y.shape[0]

    W2 = params["W2"]
    Z1 = cache["Z1"]
    A1 = cache["A1"]
    A2 = cache["A2"]
    X  = cache["X"]

    # --- Output layer ---

    # TODO: dZ2 = A2 - y
    # This is the error at the output: how far are our predictions from truth?
    dZ2 = None  # TODO

    # TODO: dW2 = (A1.T @ dZ2) / m
    # This tells us how much each weight in W2 contributed to the loss
    dW2 = None  # TODO

    # TODO: db2 = np.mean(dZ2, axis=0, keepdims=True)
    db2 = None  # TODO

    # --- Hidden layer ---

    # TODO: dA1 = dZ2 @ W2.T
    # Pass the error signal backwards through W2 to reach the hidden layer
    dA1 = None  # TODO

    # TODO: dZ1 = dA1 * relu_derivative(Z1)
    # ReLU gate: neurons that were inactive (Z1 <= 0) contribute zero gradient
    dZ1 = None  # TODO

    # TODO: dW1 = (X.T @ dZ1) / m
    dW1 = None  # TODO

    # TODO: db1 = np.mean(dZ1, axis=0, keepdims=True)
    db1 = None  # TODO

    return {"dW1": dW1, "db1": db1, "dW2": dW2, "db2": db2}


# ============================================================
# SECTION 7 — WEIGHT UPDATE
# ============================================================

def update_parameters(params: dict, grads: dict, learning_rate: float) -> dict:
    """
    Gradient descent parameter update.

    Rule: parameter = parameter - learning_rate * gradient

    Args:
        params:        current weights and biases
        grads:         gradients from backward_pass
        learning_rate: step size (hyperparameter)

    Returns:
        updated params dict
    """
    # TODO: For each of W1, b1, W2, b2:
    # Subtract learning_rate * the corresponding gradient from the parameter
    # Example: params["W1"] -= learning_rate * grads["dW1"]

    params["W1"] -= learning_rate * grads["dW1"]  # done for you as example
    params["b1"] = None  # TODO: update b1
    params["W2"] = None  # TODO: update W2
    params["b2"] = None  # TODO: update b2

    return params


# ============================================================
# SECTION 8 — TRAINING LOOP
# ============================================================

def train(X: np.ndarray, y: np.ndarray,
          n_hidden: int = 4,
          learning_rate: float = 0.5,
          epochs: int = 10000,
          print_every: int = 1000) -> tuple:
    """
    Full training loop. Initializes parameters, then for each epoch:
    1. Forward pass (compute predictions)
    2. Compute loss
    3. Backward pass (compute gradients)
    4. Update parameters

    Args:
        X:             input data
        y:             true labels
        n_hidden:      number of hidden neurons
        learning_rate: gradient descent step size
        epochs:        number of training iterations
        print_every:   how often to print loss

    Returns:
        params:       trained parameters
        loss_history: list of loss values per epoch
    """
    n_input  = X.shape[1]
    n_output = y.shape[1]

    params = initialize_parameters(n_input, n_hidden, n_output)
    loss_history = []

    for epoch in range(epochs + 1):
        # TODO: 1. Call forward_pass(X, params) to get A2 and cache
        A2, cache = None, None  # TODO

        # TODO: 2. Call compute_loss(A2, y) to get the loss
        loss = None  # TODO

        loss_history.append(loss)

        # TODO: 3. Call backward_pass(params, cache, y) to get gradients
        grads = None  # TODO

        # TODO: 4. Call update_parameters(params, grads, learning_rate) to update weights
        params = None  # TODO

        if epoch % print_every == 0:
            print(f"Epoch {epoch:6d} | Loss: {loss:.4f}")

    return params, loss_history


# ============================================================
# SECTION 9 — PREDICT AND EVALUATE
# ============================================================

def predict(X: np.ndarray, params: dict, threshold: float = 0.5) -> np.ndarray:
    """Convert network output probabilities to binary predictions (0 or 1)."""
    A2, _ = forward_pass(X, params)
    return (A2 >= threshold).astype(int)


def evaluate(X: np.ndarray, y: np.ndarray, params: dict) -> None:
    """Print predictions vs. expected for each input."""
    A2, _ = forward_pass(X, params)
    y_pred = predict(X, params)

    print("\n--- Predictions ---")
    for i in range(len(X)):
        prob = float(A2[i])
        expected = int(y[i])
        predicted = int(y_pred[i])
        status = "CORRECT" if predicted == expected else "WRONG"
        print(f"Input {X[i].astype(int)} -> {prob:.2f} (expected {expected})  {status}")

    accuracy = (y_pred == y).mean()
    print(f"\nAccuracy: {int(accuracy * len(y))}/{len(y)} = {accuracy * 100:.2f}%")


# ============================================================
# SECTION 10 — PLOT LOSS CURVE
# ============================================================

def plot_loss_curve(loss_history: list, output_dir: str) -> None:
    """Plot and save the training loss curve."""
    os.makedirs(output_dir, exist_ok=True)

    plt.figure(figsize=(8, 5))

    # TODO: Plot loss_history as a line chart
    # Use plt.plot(loss_history, color='steelblue', linewidth=1.5)
    # Add title: 'Training Loss — XOR Neural Network'
    # Add x-label: 'Epoch', y-label: 'Binary Cross-Entropy Loss'

    plt.grid(alpha=0.3)
    plt.tight_layout()
    filepath = os.path.join(output_dir, "loss_curve.png")
    plt.savefig(filepath)
    plt.close()
    print(f"Loss curve saved to: {filepath}")


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 50)
    print("  Neural Network from Scratch — XOR")
    print("=" * 50)
    print()
    print("Architecture: 2 -> 4 -> 1")
    print("Activation: ReLU (hidden), Sigmoid (output)")
    print("Loss: Binary Cross-Entropy")
    print()

    # Train
    params, loss_history = train(
        X, y,
        n_hidden=4,
        learning_rate=0.5,
        epochs=10000,
        print_every=1000
    )

    # Evaluate
    evaluate(X, y, params)

    # Plot
    print()
    plot_loss_curve(loss_history, "outputs")


if __name__ == "__main__":
    main()
```

---

## What You Need to Fill In

| Function | What to implement | Difficulty |
|---|---|---|
| `relu()` | `np.maximum(0, Z)` | Easy |
| `relu_derivative()` | `(Z > 0).astype(float)` | Easy |
| `sigmoid()` | `1 / (1 + np.exp(-Z))` | Easy |
| `initialize_parameters()` | Random weights * 0.01, zero biases | Easy |
| `forward_pass()` | Z1, A1, Z2, A2 with matrix multiply | Medium |
| `compute_loss()` | Binary cross-entropy formula | Medium |
| `backward_pass()` | All 6 gradient calculations | Hard |
| `update_parameters()` | Subtract lr * gradient for each param | Easy |
| `train()` | Wire forward/loss/backward/update loop | Medium |
| `plot_loss_curve()` | `plt.plot(loss_history, ...)` | Easy |

---

## Shape Reference Card

Keep this handy while implementing:

```
X  shape: (4, 2)   — 4 samples, 2 features
y  shape: (4, 1)   — 4 labels

W1 shape: (2, 4)   — connects 2 inputs to 4 hidden neurons
b1 shape: (1, 4)   — 4 biases for hidden layer
Z1 shape: (4, 4)   — X @ W1 result
A1 shape: (4, 4)   — relu(Z1), same shape

W2 shape: (4, 1)   — connects 4 hidden to 1 output
b2 shape: (1, 1)   — 1 bias for output
Z2 shape: (4, 1)   — A1 @ W2 result
A2 shape: (4, 1)   — sigmoid(Z2), same shape

dZ2 shape: (4, 1)  — matches Z2
dW2 shape: (4, 1)  — matches W2
db2 shape: (1, 1)  — matches b2
dA1 shape: (4, 4)  — matches A1
dZ1 shape: (4, 4)  — matches Z1
dW1 shape: (2, 4)  — matches W1
db1 shape: (1, 4)  — matches b1
```

---

## 📂 Navigation

| File | |
|---|---|
| [Project_Guide.md](./Project_Guide.md) | Overview and objectives |
| [Step_by_Step.md](./Step_by_Step.md) | Detailed build instructions |
| **Starter_Code.md** | You are here |
| [Architecture_Blueprint.md](./Architecture_Blueprint.md) | System diagram |
