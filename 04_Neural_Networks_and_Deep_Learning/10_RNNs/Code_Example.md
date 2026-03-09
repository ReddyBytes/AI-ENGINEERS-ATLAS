# RNNs — Code Example

## LSTM for Time-Series Prediction

We build an LSTM to predict the next value in a sine wave sequence. This demonstrates the core RNN pattern cleanly — no NLP tokenization complexity.

```python
import torch
import torch.nn as nn
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt

# ── Step 1: Generate data ─────────────────────────────────────────────────
# Create a sine wave: predictable sequential pattern
torch.manual_seed(42)
np.random.seed(42)

# Generate 1000 time steps of a sine wave
t = np.linspace(0, 100, 1000)
data = np.sin(t).astype(np.float32)

# ── Step 2: Create sequences ──────────────────────────────────────────────
# We use SEQ_LEN past values to predict the NEXT value
SEQ_LEN = 50  # look at 50 past values

def create_sequences(data, seq_len):
    """
    Convert a 1D time series into (input, target) pairs.
    Input:  data[i : i+seq_len]      — a window of seq_len values
    Target: data[i+seq_len]          — the next value after the window
    """
    X, y = [], []
    for i in range(len(data) - seq_len):
        X.append(data[i : i + seq_len])       # input sequence
        y.append(data[i + seq_len])           # next value to predict
    return np.array(X), np.array(y)

X, y = create_sequences(data, SEQ_LEN)
print(f"Total sequences: {len(X)}")
print(f"Input shape: {X.shape}")   # (950, 50)
print(f"Target shape: {y.shape}")  # (950,)

# ── Step 3: Train/test split ──────────────────────────────────────────────
# Use first 80% for training, last 20% for testing
split = int(0.8 * len(X))
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

# Convert to PyTorch tensors
# LSTM expects shape: (batch_size, seq_len, input_size)
# input_size=1 because we have one feature per time step (the sine value)
X_train_t = torch.tensor(X_train).unsqueeze(-1)  # (760, 50, 1)
X_test_t  = torch.tensor(X_test).unsqueeze(-1)   # (190, 50, 1)
y_train_t = torch.tensor(y_train).unsqueeze(-1)  # (760, 1)
y_test_t  = torch.tensor(y_test).unsqueeze(-1)   # (190, 1)

print(f"Training tensor shape: {X_train_t.shape}")

# ── Step 4: Define the LSTM model ─────────────────────────────────────────
class LSTMPredictor(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size):
        super(LSTMPredictor, self).__init__()

        self.hidden_size = hidden_size
        self.num_layers = num_layers

        # nn.LSTM arguments:
        # input_size  = number of features per time step (1 for our sine wave)
        # hidden_size = number of LSTM units (neurons)
        # num_layers  = how many LSTM layers to stack (2 = stacked LSTM)
        # batch_first = True means input shape is (batch, seq, features)
        #               False means (seq, batch, features) — batch_first=True is more intuitive
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.2 if num_layers > 1 else 0  # dropout between LSTM layers
        )

        # After LSTM, take the final hidden state and predict one value
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        # x shape: (batch_size, seq_len, input_size)
        batch_size = x.size(0)

        # Initialize hidden state and cell state to zeros
        # Shape: (num_layers, batch_size, hidden_size)
        h0 = torch.zeros(self.num_layers, batch_size, self.hidden_size)
        c0 = torch.zeros(self.num_layers, batch_size, self.hidden_size)

        # Run LSTM over the sequence
        # lstm_out: (batch_size, seq_len, hidden_size) — output at each time step
        # (hn, cn): final hidden and cell states
        lstm_out, (hn, cn) = self.lstm(x, (h0, c0))

        # We only care about the LAST time step's output
        # lstm_out[:, -1, :] takes the output of the final time step for each sample
        last_output = lstm_out[:, -1, :]  # shape: (batch_size, hidden_size)

        # Linear layer to get the prediction
        prediction = self.fc(last_output)  # shape: (batch_size, 1)

        return prediction

# Create model
model = LSTMPredictor(
    input_size=1,     # one feature per time step
    hidden_size=64,   # 64 LSTM units
    num_layers=2,     # stacked LSTM: 2 layers
    output_size=1     # predict one value
)

total_params = sum(p.numel() for p in model.parameters())
print(f"\nModel parameters: {total_params:,}")

# ── Step 5: Training setup ────────────────────────────────────────────────
criterion = nn.MSELoss()  # regression: predict a continuous value
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# ── Step 6: Training loop ─────────────────────────────────────────────────
EPOCHS = 50
BATCH_SIZE = 32

# Create DataLoader for batching
from torch.utils.data import TensorDataset, DataLoader
train_dataset = TensorDataset(X_train_t, y_train_t)
train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)

train_losses = []
test_losses  = []

for epoch in range(1, EPOCHS + 1):
    # ── Training ──
    model.train()
    epoch_loss = 0

    for X_batch, y_batch in train_loader:
        optimizer.zero_grad()

        predictions = model(X_batch)       # forward pass
        loss = criterion(predictions, y_batch)  # MSE loss

        loss.backward()  # backpropagation through time (BPTT)

        # IMPORTANT: clip gradients to prevent exploding gradients in RNNs
        # max_norm=1.0 is a common safe value
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

        optimizer.step()
        epoch_loss += loss.item()

    avg_train_loss = epoch_loss / len(train_loader)
    train_losses.append(avg_train_loss)

    # ── Evaluation ──
    model.eval()
    with torch.no_grad():
        test_pred = model(X_test_t)
        test_loss = criterion(test_pred, y_test_t).item()
        test_losses.append(test_loss)

    if epoch % 10 == 0:
        print(f"Epoch {epoch:3d} | Train Loss: {avg_train_loss:.6f} | Test Loss: {test_loss:.6f}")

# ── Step 7: Visualize predictions ────────────────────────────────────────
model.eval()
with torch.no_grad():
    test_predictions = model(X_test_t).numpy().flatten()

true_values = y_test_t.numpy().flatten()

plt.figure(figsize=(12, 4))
plt.plot(true_values[:100], label='True Values', linewidth=2)
plt.plot(test_predictions[:100], label='LSTM Predictions', linewidth=2, linestyle='--')
plt.title('LSTM Sine Wave Prediction (first 100 test steps)')
plt.xlabel('Time Step')
plt.ylabel('Value')
plt.legend()
plt.tight_layout()
plt.savefig('lstm_predictions.png', dpi=100)
print("\nPlot saved as lstm_predictions.png")

# ── Step 8: Make one step-ahead prediction ────────────────────────────────
model.eval()
with torch.no_grad():
    # Take the last SEQ_LEN values from the data
    last_sequence = torch.tensor(data[-SEQ_LEN:]).unsqueeze(0).unsqueeze(-1)
    # Shape: (1, 50, 1) — batch of 1, 50 time steps, 1 feature

    next_value = model(last_sequence).item()
    print(f"\nPredicted next sine value: {next_value:.4f}")
    print(f"True next value would be: {np.sin(t[-1] + (t[1]-t[0])):.4f}")
```

---

## What the Code Demonstrates

| Concept | Where in code |
|---------|--------------|
| Sequential input format | `X_train_t.shape = (760, 50, 1)` — batch, time, features |
| LSTM hidden/cell state init | `h0, c0 = zeros(...)` in forward() |
| Using only last time step | `lstm_out[:, -1, :]` — ignoring intermediate outputs |
| Gradient clipping | `clip_grad_norm_(model.parameters(), max_norm=1.0)` |
| Stacked LSTM | `num_layers=2` in nn.LSTM |

---

## What to Experiment With

1. **Change SEQ_LEN** to 10 or 100 — does prediction quality change?
2. **Try a vanilla RNN** — replace `nn.LSTM` with `nn.RNN` — does loss get worse?
3. **Try a GRU** — replace `nn.LSTM` with `nn.GRU` — same performance with fewer parameters?
4. **Predict multiple steps ahead** — instead of next-1, try predicting the next 5 values (change output_size=5)
5. **Remove gradient clipping** — does loss diverge?

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | RNN architecture deep dive |

⬅️ **Prev:** [09 CNNs](../09_CNNs/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [11 GANs](../11_GANs/Theory.md)
