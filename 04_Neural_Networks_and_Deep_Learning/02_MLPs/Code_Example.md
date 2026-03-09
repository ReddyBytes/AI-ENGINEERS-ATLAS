# MLPs — Code Example

## Two Approaches: scikit-learn and PyTorch

We will train an MLP on the classic Iris dataset (3 flower species, 4 features). Both examples are heavily commented so you can follow every step.

---

## Approach 1: scikit-learn MLPClassifier (5 minutes)

```python
# scikit-learn has a built-in MLP — great for quick experiments

from sklearn.datasets import load_iris
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report

# ── Step 1: Load data ──────────────────────────────────────────────────────
iris = load_iris()
X = iris.data    # shape: (150, 4)  — 150 samples, 4 features
y = iris.target  # shape: (150,)    — labels 0, 1, or 2

# ── Step 2: Split into train and test sets ─────────────────────────────────
# 80% training, 20% testing. random_state makes it reproducible.
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ── Step 3: Scale the features ────────────────────────────────────────────
# Neural networks are sensitive to input scale.
# StandardScaler makes each feature have mean=0, std=1.
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)  # fit on train, transform train
X_test  = scaler.transform(X_test)       # only transform test (never fit on test!)

# ── Step 4: Build the MLP ─────────────────────────────────────────────────
# hidden_layer_sizes=(64, 32) means:
#   - first hidden layer: 64 neurons
#   - second hidden layer: 32 neurons
# activation='relu' — ReLU for hidden layers (best default)
# max_iter=300       — train for up to 300 epochs
# random_state=42    — reproducibility

model = MLPClassifier(
    hidden_layer_sizes=(64, 32),
    activation='relu',
    solver='adam',       # Adam optimizer (we cover this in topic 07)
    max_iter=300,
    random_state=42
)

# ── Step 5: Train ─────────────────────────────────────────────────────────
model.fit(X_train, y_train)
# Internally: forward pass → compute loss → backprop → update weights. Repeat.

# ── Step 6: Evaluate ──────────────────────────────────────────────────────
y_pred = model.predict(X_test)
print(f"Accuracy: {accuracy_score(y_test, y_pred):.2%}")
print(classification_report(y_test, y_pred, target_names=iris.target_names))

# ── Step 7: Make a single prediction ──────────────────────────────────────
sample = X_test[0:1]              # one sample (keep 2D shape)
prediction = model.predict(sample)
proba = model.predict_proba(sample)
print(f"Predicted class: {iris.target_names[prediction[0]]}")
print(f"Class probabilities: {proba.round(3)}")
```

**Expected output:** ~97% accuracy. The Iris dataset is quite simple for an MLP.

---

## Approach 2: PyTorch MLP (full control)

```python
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import numpy as np

# ── Step 1: Prepare data (same as above) ─────────────────────────────────
iris = load_iris()
X, y = iris.data, iris.target

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test  = scaler.transform(X_test)

# PyTorch works with tensors, not numpy arrays.
# float32 for features, int64 (long) for labels.
X_train_t = torch.tensor(X_train, dtype=torch.float32)
y_train_t = torch.tensor(y_train, dtype=torch.long)
X_test_t  = torch.tensor(X_test,  dtype=torch.float32)
y_test_t  = torch.tensor(y_test,  dtype=torch.long)

# ── Step 2: Define the MLP ────────────────────────────────────────────────
# We subclass nn.Module — the standard way to build models in PyTorch.

class MLP(nn.Module):
    def __init__(self, input_size, hidden1, hidden2, output_size):
        super(MLP, self).__init__()

        # nn.Linear(in, out) creates a fully-connected layer:
        # it holds a weight matrix (in × out) and a bias vector (out,)
        self.layer1 = nn.Linear(input_size, hidden1)
        self.layer2 = nn.Linear(hidden1, hidden2)
        self.output = nn.Linear(hidden2, output_size)

        # ReLU activation — we apply this between layers
        self.relu = nn.ReLU()

        # Dropout for regularization (randomly zeros 20% of neurons during training)
        self.dropout = nn.Dropout(p=0.2)

    def forward(self, x):
        # This defines the forward pass — how data flows through the network.
        # x shape: (batch_size, 4)

        x = self.relu(self.layer1(x))   # (batch_size, 4) → (batch_size, 64)
        x = self.dropout(x)             # randomly zero some neurons (training only)
        x = self.relu(self.layer2(x))   # (batch_size, 64) → (batch_size, 32)
        x = self.output(x)              # (batch_size, 32) → (batch_size, 3)
        # Note: no activation on output — CrossEntropyLoss includes softmax internally
        return x

# Create the model
# 4 input features, 64 and 32 hidden neurons, 3 output classes
model = MLP(input_size=4, hidden1=64, hidden2=32, output_size=3)
print(model)  # prints architecture summary

# ── Step 3: Loss function and optimizer ───────────────────────────────────
# CrossEntropyLoss is the standard loss for multi-class classification.
# It combines LogSoftmax + NLLLoss internally.
criterion = nn.CrossEntropyLoss()

# Adam optimizer with learning rate 0.001
# model.parameters() gives Adam all the weights and biases to update
optimizer = optim.Adam(model.parameters(), lr=0.001)

# ── Step 4: Training loop ─────────────────────────────────────────────────
EPOCHS = 150  # how many full passes through the training data

for epoch in range(EPOCHS):
    # ── Training phase ──
    model.train()  # tells dropout to be active

    optimizer.zero_grad()   # clear gradients from last step (IMPORTANT!)

    outputs = model(X_train_t)          # forward pass: get predictions
    loss = criterion(outputs, y_train_t) # compare predictions to true labels

    loss.backward()    # backpropagation: compute gradients
    optimizer.step()   # update weights using those gradients

    # ── Evaluation phase (every 10 epochs) ──
    if (epoch + 1) % 10 == 0:
        model.eval()   # tells dropout to be inactive
        with torch.no_grad():  # no need to compute gradients for evaluation
            test_outputs = model(X_test_t)
            test_loss = criterion(test_outputs, y_test_t)

            # Get predicted class: argmax of the 3 output scores
            _, predicted = torch.max(test_outputs, 1)
            accuracy = (predicted == y_test_t).float().mean()

        print(f"Epoch {epoch+1:3d} | Train Loss: {loss.item():.4f} | "
              f"Test Loss: {test_loss.item():.4f} | Test Acc: {accuracy:.2%}")

# ── Step 5: Final evaluation ─────────────────────────────────────────────
model.eval()
with torch.no_grad():
    test_outputs = model(X_test_t)
    _, predicted = torch.max(test_outputs, 1)
    final_acc = (predicted == y_test_t).float().mean()
    print(f"\nFinal Test Accuracy: {final_acc:.2%}")
```

---

## Key Differences Between the Two Approaches

| Aspect | scikit-learn | PyTorch |
|--------|-------------|---------|
| Code length | ~10 lines | ~50 lines |
| Control | Low | Full |
| Debugging | Hard | Easy (you see every step) |
| Custom architectures | Not possible | Anything goes |
| When to use | Quick baseline | Research, production, custom models |

---

## What to Experiment With

1. **Change hidden layer sizes** — try (128, 64) and see if accuracy improves
2. **Change learning rate** — try 0.01 (too fast?) and 0.0001 (too slow?)
3. **Remove dropout** — does the model overfit on training data more?
4. **Add more layers** — does a 3-layer MLP beat a 2-layer one on this dataset?
5. **Remove the scaler** — watch the training become unstable

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [01 Perceptron](../01_Perceptron/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 Activation Functions](../03_Activation_Functions/Theory.md)
