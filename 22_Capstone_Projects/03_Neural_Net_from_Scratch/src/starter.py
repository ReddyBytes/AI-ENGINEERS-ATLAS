"""
Project 3 — Neural Network from Scratch
=========================================
A 2-layer MLP built using only numpy.
Solves the XOR problem to demonstrate that hidden layers
enable non-linear decision boundaries.

Architecture: 2 -> 4 -> 1
Activations:  ReLU (hidden), Sigmoid (output)
Loss:         Binary Cross-Entropy

Libraries required: pip install numpy matplotlib
Run: python starter.py
"""

import numpy as np
import matplotlib.pyplot as plt
import os


# ============================================================
# SECTION 1 — DATASET
# ============================================================

# XOR truth table — the classic problem a single layer cannot solve
X = np.array([[0, 0],
              [0, 1],
              [1, 0],
              [1, 1]], dtype=float)   # shape (4, 2) — 4 samples, 2 features

y = np.array([[0],
              [1],
              [1],
              [0]], dtype=float)      # shape (4, 1) — 4 binary labels


# ============================================================
# SECTION 2 — ACTIVATION FUNCTIONS
# ============================================================

def relu(Z: np.ndarray) -> np.ndarray:
    """
    ReLU activation: max(0, Z), applied element-wise.
    Negative values become 0. Positive values are unchanged.
    This non-linearity is what lets the network solve XOR.

    Args:
        Z: numpy array of any shape (pre-activation values)
    Returns:
        array of same shape with negatives zeroed out
    """
    # TODO: return np.maximum(0, Z)
    pass  # TODO: replace


def relu_derivative(Z: np.ndarray) -> np.ndarray:
    """
    Derivative of ReLU, applied element-wise.
    Returns 1.0 where Z > 0, else 0.0.
    Used in backpropagation as a "gate" — dead neurons pass no gradient.

    Args:
        Z: the pre-activation values (BEFORE relu was applied, not after)
    Returns:
        binary array: 1.0 where Z > 0, 0.0 elsewhere
    """
    # TODO: return (Z > 0).astype(float)
    pass  # TODO: replace


def sigmoid(Z: np.ndarray) -> np.ndarray:
    """
    Sigmoid activation: 1 / (1 + exp(-Z)), applied element-wise.
    Maps any real number to the open interval (0, 1).
    Interpret the output as "probability of class 1".

    Args:
        Z: numpy array of any shape
    Returns:
        array of same shape with values strictly between 0 and 1
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
        W1: (n_input, n_hidden)    2 × 4 for XOR
        b1: (1, n_hidden)          1 × 4
        W2: (n_hidden, n_output)   4 × 1 for XOR
        b2: (1, n_output)          1 × 1

    Weights: small random values (× 0.01) to break symmetry.
    Biases:  zeros (safe to start at zero).

    Args:
        n_input:  number of input features (2 for XOR)
        n_hidden: number of hidden neurons (4 by default)
        n_output: number of output neurons (1 for binary)
        seed:     random seed for reproducibility
    Returns:
        dict with keys: W1, b1, W2, b2
    """
    np.random.seed(seed)  # ← ensures same random values every run

    # TODO: W1 = np.random.randn(n_input, n_hidden) * 0.01
    W1 = None  # TODO: replace

    # TODO: b1 = np.zeros((1, n_hidden))
    b1 = None  # TODO: replace

    # TODO: W2 = np.random.randn(n_hidden, n_output) * 0.01
    W2 = None  # TODO: replace

    # TODO: b2 = np.zeros((1, n_output))
    b2 = None  # TODO: replace

    return {"W1": W1, "b1": b1, "W2": W2, "b2": b2}


# ============================================================
# SECTION 4 — FORWARD PASS
# ============================================================

def forward_pass(X: np.ndarray, params: dict) -> tuple:
    """
    Compute the network's output for input X.

    Layer 1:  Z1 = X @ W1 + b1   (4,2)@(2,4)+(1,4) = (4,4)
              A1 = relu(Z1)        same shape (4,4)
    Layer 2:  Z2 = A1 @ W2 + b2  (4,4)@(4,1)+(1,1) = (4,1)
              A2 = sigmoid(Z2)     same shape (4,1) — output probabilities

    Args:
        X:      input array, shape (m, n_input)
        params: dict with W1, b1, W2, b2
    Returns:
        A2:    output predictions, shape (m, 1)
        cache: dict of intermediates needed for backprop (Z1, A1, Z2, A2, X)
    """
    W1, b1, W2, b2 = params["W1"], params["b1"], params["W2"], params["b2"]

    # TODO: Z1 = X @ W1 + b1   (use @ for matrix multiply)
    Z1 = None  # TODO

    # TODO: A1 = relu(Z1)
    A1 = None  # TODO

    # TODO: Z2 = A1 @ W2 + b2
    Z2 = None  # TODO

    # TODO: A2 = sigmoid(Z2)   — final output, values in (0, 1)
    A2 = None  # TODO

    cache = {"Z1": Z1, "A1": A1, "Z2": Z2, "A2": A2, "X": X}  # ← saved for backprop
    return A2, cache


# ============================================================
# SECTION 5 — LOSS FUNCTION
# ============================================================

def compute_loss(A2: np.ndarray, y: np.ndarray) -> float:
    """
    Binary Cross-Entropy loss.

    Formula: L = -mean(y * log(A2) + (1 - y) * log(1 - A2))

    Penalizes wrong confident predictions most severely.
    Starting loss near 0.693 (= log(2)) is normal — it means 50/50 predictions.

    Args:
        A2: predictions, shape (m, 1), values in (0, 1)
        y:  true labels, shape (m, 1), values are 0 or 1
    Returns:
        scalar loss value (float)
    """
    epsilon = 1e-8  # ← prevents log(0) = -inf — never remove this

    # TODO: Implement BCE: -np.mean(y * np.log(A2 + epsilon) + (1-y) * np.log(1-A2 + epsilon))
    loss = None  # TODO

    return float(loss)


# ============================================================
# SECTION 6 — BACKPROPAGATION
# ============================================================

def backward_pass(params: dict, cache: dict, y: np.ndarray) -> dict:
    """
    Compute gradients of the loss w.r.t. all parameters using the chain rule.

    Output layer (work backwards from the loss):
        dZ2 = A2 - y                          output error (BCE + sigmoid simplifies to this)
        dW2 = (A1.T @ dZ2) / m               how much did each W2 weight contribute?
        db2 = mean(dZ2, axis=0)

    Hidden layer:
        dA1 = dZ2 @ W2.T                      pass error signal back through W2
        dZ1 = dA1 * relu_derivative(Z1)       ReLU gate: dead neurons pass zero gradient
        dW1 = (X.T @ dZ1) / m
        db1 = mean(dZ1, axis=0)

    Args:
        params: dict with W1, b1, W2, b2
        cache:  dict with Z1, A1, Z2, A2, X (from forward_pass)
        y:      true labels, shape (m, 1)
    Returns:
        grads: dict with keys dW1, db1, dW2, db2
    """
    m  = y.shape[0]   # ← number of samples (4 for XOR)

    W2 = params["W2"]
    Z1 = cache["Z1"]
    A1 = cache["A1"]
    A2 = cache["A2"]
    X  = cache["X"]

    # --- Output layer ---

    # TODO: dZ2 = A2 - y
    # This is the output error: how far are our predictions from truth?
    dZ2 = None  # TODO

    # TODO: dW2 = (A1.T @ dZ2) / m
    # Tells us how much each weight in W2 contributed to the loss
    dW2 = None  # TODO

    # TODO: db2 = np.mean(dZ2, axis=0, keepdims=True)
    db2 = None  # TODO

    # --- Hidden layer ---

    # TODO: dA1 = dZ2 @ W2.T
    # Pass the error signal backwards through W2 to reach the hidden layer
    dA1 = None  # TODO

    # TODO: dZ1 = dA1 * relu_derivative(Z1)
    # ReLU gate: neurons that were off (Z1 <= 0) contribute zero gradient
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
    Gradient descent update rule: parameter = parameter - learning_rate * gradient.
    The minus sign moves weights in the direction that reduces loss.

    Args:
        params:        current weights and biases
        grads:         gradients from backward_pass
        learning_rate: step size (try 0.1 to 1.0 for XOR)
    Returns:
        updated params dict
    """
    params["W1"] -= learning_rate * grads["dW1"]  # ← done as example — do the rest

    # TODO: update b1 using the same pattern
    params["b1"] = None  # TODO: params["b1"] - learning_rate * grads["db1"]

    # TODO: update W2
    params["W2"] = None  # TODO

    # TODO: update b2
    params["b2"] = None  # TODO

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
    Full training loop. Each epoch runs 4 steps:
    1. Forward pass  — compute predictions
    2. Compute loss  — measure how wrong we are
    3. Backward pass — compute gradients (backprop)
    4. Update params — move weights to reduce loss

    Args:
        X:             input data (4, 2) for XOR
        y:             true labels (4, 1)
        n_hidden:      number of hidden neurons
        learning_rate: gradient descent step size
        epochs:        number of training iterations
        print_every:   print loss every N epochs
    Returns:
        params:       trained parameters dict
        loss_history: list of loss values (one per epoch)
    """
    params = initialize_parameters(X.shape[1], n_hidden, y.shape[1])
    loss_history = []

    for epoch in range(epochs + 1):
        # TODO: 1. forward_pass(X, params) → A2, cache
        A2, cache = None, None  # TODO: replace

        # TODO: 2. compute_loss(A2, y) → loss
        loss = None  # TODO: replace

        loss_history.append(loss)

        # TODO: 3. backward_pass(params, cache, y) → grads
        grads = None  # TODO: replace

        # TODO: 4. update_parameters(params, grads, learning_rate) → params
        params = None  # TODO: replace

        if epoch % print_every == 0:
            print(f"Epoch {epoch:6d} | Loss: {loss:.4f}")

    return params, loss_history


# ============================================================
# SECTION 9 — PREDICT AND EVALUATE
# ============================================================

def predict(X: np.ndarray, params: dict, threshold: float = 0.5) -> np.ndarray:
    """Convert network output probabilities to binary predictions (0 or 1)."""
    A2, _ = forward_pass(X, params)
    return (A2 >= threshold).astype(int)  # ← threshold converts probability to hard label


def evaluate(X: np.ndarray, y: np.ndarray, params: dict) -> None:
    """Print each input, predicted probability, expected label, and CORRECT/WRONG."""
    A2, _ = forward_pass(X, params)
    y_pred = predict(X, params)

    print("\n--- Predictions ---")
    for i in range(len(X)):
        prob      = float(A2[i])
        expected  = int(y[i])
        predicted = int(y_pred[i])
        status    = "CORRECT" if predicted == expected else "WRONG"
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

    # TODO: plt.plot(loss_history, color='steelblue', linewidth=1.5)
    # TODO: Add title 'Training Loss — XOR Neural Network'
    # TODO: Add xlabel 'Epoch', ylabel 'Binary Cross-Entropy Loss'

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

    params, loss_history = train(
        X, y,
        n_hidden=4,
        learning_rate=0.5,
        epochs=10000,
        print_every=1000
    )

    evaluate(X, y, params)

    print()
    plot_loss_curve(loss_history, "outputs")


if __name__ == "__main__":
    main()
