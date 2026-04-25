# 📋 Project 3 — Build Guide

## Overview

Build a neural network piece by piece, testing each component in isolation before assembling the full training loop. Every step maps to a specific mathematical concept from the theory.

**Total estimated time:** 4–6 hours. Spend extra time with Stage 5 (backpropagation) — it is the hardest and most valuable part.

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

Copy `src/starter.py` into your project folder as `neural_net.py`.

### Step 2: Understand the XOR dataset

XOR is tiny — 4 samples, 2 features, binary labels:

```python
X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])  # shape: (4, 2)
y = np.array([[0],    [1],    [1],    [0]])       # shape: (4, 1)
```

Getting shapes right is the most common source of bugs in neural networks. Keep the shape reference card from `02_ARCHITECTURE.md` open as you work.

---

## Stage 1 — Activation Functions

**Goal:** Write ReLU and sigmoid as standalone numpy functions.

**Concept:** Activation functions are what make neural networks non-linear. Without them, stacking layers collapses to a single linear operation — no matter how many layers you add. ReLU and sigmoid break this pattern and allow networks to learn complex shapes like XOR.

### Step 3: Implement `relu()` and `relu_derivative()`

<details><summary>💡 Hint</summary>

ReLU is `max(0, x)` applied element-wise. numpy's `np.maximum(0, Z)` does this.

The derivative of ReLU is 1 where Z > 0, and 0 everywhere else. Use `(Z > 0).astype(float)`.

</details>

<details><summary>✅ Answer</summary>

```python
def relu(Z):
    return np.maximum(0, Z)

def relu_derivative(Z):
    return (Z > 0).astype(float)
```

</details>

### Step 4: Implement `sigmoid()`

<details><summary>💡 Hint</summary>

`sigmoid(x) = 1 / (1 + exp(-x))`. Maps any number to (0, 1).

`sigmoid(0) = 0.5`, `sigmoid(10) ≈ 1.0`, `sigmoid(-10) ≈ 0.0`.

</details>

<details><summary>✅ Answer</summary>

```python
def sigmoid(Z):
    return 1 / (1 + np.exp(-Z))
```

</details>

**Verify Stage 1:** Test values — `relu(np.array([-2, 0, 2]))` should return `[0, 0, 2]`.

---

## Stage 2 — Initialize Weights

**Goal:** Create randomly initialized weight matrices and bias vectors.

**Concept:** Weights are the learnable parameters of the network. Initialize them to small random values — not zeros. If all weights start at zero, every neuron computes the same output and gradient, so they all learn identically and the network never breaks symmetry.

### Step 5: Understand the architecture dimensions

```
W1: shape (2, 4)  — transforms 2 input features to 4 hidden neurons
b1: shape (1, 4)  — one bias per hidden neuron
W2: shape (4, 1)  — transforms 4 hidden neurons to 1 output
b2: shape (1, 1)  — one bias for the output neuron
```

### Step 6: Implement `initialize_parameters()`

<details><summary>💡 Hint</summary>

- Weights: `np.random.randn(rows, cols) * 0.01` — small random values break symmetry
- Biases: `np.zeros((1, n))` — zeros are fine for biases

</details>

<details><summary>✅ Answer</summary>

```python
def initialize_parameters(n_input, n_hidden, n_output, seed=42):
    np.random.seed(seed)
    W1 = np.random.randn(n_input, n_hidden) * 0.01
    b1 = np.zeros((1, n_hidden))
    W2 = np.random.randn(n_hidden, n_output) * 0.01
    b2 = np.zeros((1, n_output))
    return {"W1": W1, "b1": b1, "W2": W2, "b2": b2}
```

</details>

**Verify Stage 2:** `params["W1"].shape` should be `(2, 4)`, `params["W2"].shape` should be `(4, 1)`.

---

## Stage 3 — Forward Pass

**Goal:** Compute the network's output for a given input.

**Concept:** The forward pass is how the network makes a prediction. Data flows forward through the network: inputs are multiplied by weights, biases are added, activations are applied, and the final output is a probability. No learning happens here — this is pure prediction.

### Step 7: Implement `forward_pass()`

The four computations in order:

```
Z1 = X @ W1 + b1          # (4,2) @ (2,4) + (1,4) = (4,4)
A1 = relu(Z1)             # (4,4) same shape
Z2 = A1 @ W2 + b2         # (4,4) @ (4,1) + (1,1) = (4,1)
A2 = sigmoid(Z2)          # (4,1) same shape — output probabilities
```

<details><summary>💡 Hint</summary>

Use the `@` operator for matrix multiplication. numpy broadcasts the bias addition automatically.

Store all intermediate values in a `cache` dict — you will need them in backprop.

</details>

<details><summary>✅ Answer</summary>

```python
def forward_pass(X, params):
    W1, b1, W2, b2 = params["W1"], params["b1"], params["W2"], params["b2"]
    Z1 = X @ W1 + b1
    A1 = relu(Z1)
    Z2 = A1 @ W2 + b2
    A2 = sigmoid(Z2)
    cache = {"Z1": Z1, "A1": A1, "Z2": Z2, "A2": A2, "X": X}
    return A2, cache
```

</details>

**Verify Stage 3:** With random initial weights, the output shape should be `(4, 1)` and values should be near 0.5 (maximum uncertainty).

---

## Stage 4 — Compute Loss

**Goal:** Measure how wrong the network's predictions are.

**Concept:** Binary cross-entropy loss penalizes wrong confident predictions most severely. If the network predicts 0.99 for a sample that should be 0, the loss is huge. If it predicts 0.5, the loss is moderate. This signal drives all learning.

### Step 8: Implement `compute_loss()`

The formula:
```
L = -mean(y * log(A2) + (1 - y) * log(1 - A2))
```

<details><summary>💡 Hint</summary>

Always add a small `epsilon = 1e-8` inside the `log()` to prevent `log(0)` which produces `-inf`. This is a standard numerical stability trick.

</details>

<details><summary>✅ Answer</summary>

```python
def compute_loss(A2, y):
    epsilon = 1e-8
    loss = -np.mean(y * np.log(A2 + epsilon) + (1 - y) * np.log(1 - A2 + epsilon))
    return float(loss)
```

</details>

**Verify Stage 4:** With random initial weights, the initial loss should be near `0.693` (which is `log(2)` — the maximum entropy for a binary prediction).

---

## Stage 5 — Backpropagation

**Goal:** Compute how much each weight contributed to the loss.

**Concept:** Backpropagation applies the chain rule of calculus backwards from the output error, layer by layer, each time multiplying by the derivative of that layer's activation. This is the heart of all neural network training.

### Step 9: Implement `backward_pass()`

Work through each gradient step carefully. Read the comment above each line before writing the code.

Output layer gradients:
```
dZ2 = A2 - y                      # output error (BCE + sigmoid simplifies to this)
dW2 = (A1.T @ dZ2) / m            # gradient for W2
db2 = mean(dZ2, axis=0)           # gradient for b2
```

Hidden layer gradients:
```
dA1 = dZ2 @ W2.T                  # pass error back through W2
dZ1 = dA1 * relu_derivative(Z1)   # ReLU gate: dead neurons contribute zero
dW1 = (X.T @ dZ1) / m            # gradient for W1
db1 = mean(dZ1, axis=0)           # gradient for b1
```

<details><summary>💡 Hint</summary>

The ReLU gate is the most conceptually important step. Neurons where `Z1 <= 0` had zero output during forward pass — they contribute zero gradient during backprop. This is what `relu_derivative(Z1)` computes.

Use `keepdims=True` in the mean calls to preserve the shape: `np.mean(dZ2, axis=0, keepdims=True)`.

</details>

<details><summary>✅ Answer</summary>

```python
def backward_pass(params, cache, y):
    m  = y.shape[0]
    W2 = params["W2"]
    Z1, A1, A2, X = cache["Z1"], cache["A1"], cache["A2"], cache["X"]

    dZ2 = A2 - y
    dW2 = (A1.T @ dZ2) / m
    db2 = np.mean(dZ2, axis=0, keepdims=True)

    dA1 = dZ2 @ W2.T
    dZ1 = dA1 * relu_derivative(Z1)
    dW1 = (X.T @ dZ1) / m
    db1 = np.mean(dZ1, axis=0, keepdims=True)

    return {"dW1": dW1, "db1": db1, "dW2": dW2, "db2": db2}
```

</details>

**Verify Stage 5:** `grads["dW1"].shape` must equal `params["W1"].shape` which is `(2, 4)`. Gradient shapes must always match the weight shapes they correspond to.

---

## Stage 6 — Weight Update

**Goal:** Adjust the weights to reduce the loss.

**Concept:** Gradient descent moves each weight in the direction that reduces the loss. The learning rate controls the step size. Too large and you overshoot. Too small and training is very slow.

### Step 10: Implement `update_parameters()`

<details><summary>💡 Hint</summary>

The update rule for every parameter: `parameter -= learning_rate * gradient`

</details>

<details><summary>✅ Answer</summary>

```python
def update_parameters(params, grads, learning_rate):
    params["W1"] -= learning_rate * grads["dW1"]
    params["b1"] -= learning_rate * grads["db1"]
    params["W2"] -= learning_rate * grads["dW2"]
    params["b2"] -= learning_rate * grads["db2"]
    return params
```

</details>

---

## Stage 7 — Training Loop

**Goal:** Combine all stages into a complete training loop.

**Concept:** One pass through the entire dataset is called an epoch. You run many epochs — each time adjusting weights slightly so the loss decreases. The loss curve shows whether training is working.

### Step 11: Implement `train()`

<details><summary>💡 Hint</summary>

The loop body has exactly 4 steps:
1. `forward_pass(X, params)` → get `A2, cache`
2. `compute_loss(A2, y)` → get `loss`
3. `backward_pass(params, cache, y)` → get `grads`
4. `update_parameters(params, grads, learning_rate)` → update `params`

</details>

<details><summary>✅ Answer</summary>

```python
def train(X, y, n_hidden=4, learning_rate=0.5, epochs=10000, print_every=1000):
    params = initialize_parameters(X.shape[1], n_hidden, y.shape[1])
    loss_history = []

    for epoch in range(epochs + 1):
        A2, cache = forward_pass(X, params)
        loss = compute_loss(A2, y)
        loss_history.append(loss)
        grads = backward_pass(params, cache, y)
        params = update_parameters(params, grads, learning_rate)

        if epoch % print_every == 0:
            print(f"Epoch {epoch:6d} | Loss: {loss:.4f}")

    return params, loss_history
```

</details>

---

## Stage 8 — Evaluate and Plot

### Step 12: Implement `plot_loss_curve()`

<details><summary>💡 Hint</summary>

`plt.plot(loss_history, color='steelblue', linewidth=1.5)` draws the curve. A healthy training run shows a smooth downward slope from near 0.693 to near zero.

</details>

<details><summary>✅ Answer</summary>

```python
def plot_loss_curve(loss_history, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    plt.figure(figsize=(8, 5))
    plt.plot(loss_history, color='steelblue', linewidth=1.5)
    plt.title('Training Loss — XOR Neural Network')
    plt.xlabel('Epoch')
    plt.ylabel('Binary Cross-Entropy Loss')
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "loss_curve.png"))
    plt.close()
```

</details>

### Step 13: Run everything

```bash
python neural_net.py
```

Confirm:
- Loss decreases from ~0.69 to near 0.01 or below
- All 4 XOR predictions are correct (Accuracy: 4/4 = 100.00%)
- `outputs/loss_curve.png` saved

---

## Extension Challenges

### Extension 1 — Try Different Learning Rates

<details><summary>💡 Hint</summary>

Change `learning_rate` from 0.5 to 0.01 and 2.0. Observe:
- Too low (0.01): training converges very slowly — loss barely moves
- Too high (2.0): training may diverge — loss goes up instead of down

</details>

### Extension 2 — Add More Hidden Neurons

Change `n_hidden` from 4 to 2, then to 8. Does XOR still work with only 2 neurons? Why? (Minimum needed is theoretically 2, but initialization randomness means 4 is more reliable.)

### Extension 3 — MNIST (Advanced)

Load MNIST from sklearn, flatten the 28x28 images to 784-dim vectors, change the output to 10 neurons with softmax, and re-derive the backprop equations for multi-class.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 01_MISSION.md](./01_MISSION.md) | Context and objectives |
| [📄 02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design and diagrams |
| 📄 **03_GUIDE.md** | You are here |
| [📄 src/starter.py](./src/starter.py) | Starter code with TODOs |
| [📄 04_RECAP.md](./04_RECAP.md) | Concepts recap and next steps |

⬅️ **Previous:** [02 — ML Model Comparison](../02_ML_Model_Comparison/01_MISSION.md)
➡️ **Next:** [04 — LLM Chatbot with Memory](../04_LLM_Chatbot_with_Memory/01_MISSION.md)
