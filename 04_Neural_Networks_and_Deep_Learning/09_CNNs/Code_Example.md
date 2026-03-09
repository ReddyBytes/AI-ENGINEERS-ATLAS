# CNNs — Code Example

## Simple CNN for MNIST Digit Classification

We build a CNN from scratch in PyTorch to classify handwritten digits (0–9). Every line is commented.

```python
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

# ── Step 1: Set device ────────────────────────────────────────────────────
# Use GPU if available, otherwise CPU
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# ── Step 2: Data loading and preprocessing ────────────────────────────────
# MNIST: 70,000 grayscale images, 28×28 pixels, 10 classes (digits 0-9)

# transforms.Compose chains multiple preprocessing steps
transform = transforms.Compose([
    transforms.ToTensor(),        # Convert PIL image to tensor, scale 0-255 → 0.0-1.0
    transforms.Normalize((0.1307,), (0.3081,))  # Normalize: mean=0.1307, std=0.3081
    # These values are the global mean and std of the MNIST dataset
])

# Download and load training set
train_dataset = datasets.MNIST(
    root='./data',      # where to store the downloaded data
    train=True,         # training set (60,000 images)
    download=True,      # download if not already present
    transform=transform
)

# Download and load test set
test_dataset = datasets.MNIST(
    root='./data',
    train=False,        # test set (10,000 images)
    download=True,
    transform=transform
)

# DataLoader: handles batching, shuffling, and parallel data loading
train_loader = DataLoader(
    train_dataset,
    batch_size=64,       # process 64 images per weight update
    shuffle=True         # shuffle data each epoch to prevent order bias
)

test_loader = DataLoader(
    test_dataset,
    batch_size=1000,     # larger batch for evaluation (no gradients = more memory)
    shuffle=False        # no need to shuffle test data
)

# ── Step 3: Define the CNN architecture ──────────────────────────────────
class SimpleCNN(nn.Module):
    def __init__(self):
        super(SimpleCNN, self).__init__()

        # === FEATURE EXTRACTION BLOCK 1 ===
        # Conv2d(in_channels, out_channels, kernel_size)
        # in_channels=1 because MNIST is grayscale (1 channel)
        # out_channels=32 means we learn 32 different filters
        # kernel_size=3 means 3×3 filters
        self.conv1 = nn.Conv2d(in_channels=1, out_channels=32, kernel_size=3)
        # Input:  1 × 28 × 28
        # Output: 32 × 26 × 26  (28-3+1=26, no padding)

        self.relu1 = nn.ReLU()

        # MaxPool2d(kernel_size=2) — takes max in each 2×2 non-overlapping region
        self.pool1 = nn.MaxPool2d(kernel_size=2)
        # Input:  32 × 26 × 26
        # Output: 32 × 13 × 13  (26/2=13)

        # === FEATURE EXTRACTION BLOCK 2 ===
        # in_channels=32 must match previous layer's out_channels
        self.conv2 = nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3)
        # Input:  32 × 13 × 13
        # Output: 64 × 11 × 11  (13-3+1=11)

        self.relu2 = nn.ReLU()

        self.pool2 = nn.MaxPool2d(kernel_size=2)
        # Input:  64 × 11 × 11
        # Output: 64 × 5 × 5  (floor(11/2)=5)

        # === CLASSIFICATION HEAD ===
        # After pool2, we have 64 × 5 × 5 = 1600 values
        # Flatten (done in forward()) + fully-connected layers

        self.fc1 = nn.Linear(64 * 5 * 5, 128)  # 1600 → 128
        self.relu3 = nn.ReLU()
        self.dropout = nn.Dropout(p=0.5)  # regularization: randomly zero 50% of neurons
        self.fc2 = nn.Linear(128, 10)     # 128 → 10 classes (digits 0-9)
        # Note: no activation here — CrossEntropyLoss applies softmax internally

    def forward(self, x):
        # x shape at start: (batch_size, 1, 28, 28)

        # Block 1
        x = self.conv1(x)    # → (batch, 32, 26, 26)
        x = self.relu1(x)    # → (batch, 32, 26, 26)
        x = self.pool1(x)    # → (batch, 32, 13, 13)

        # Block 2
        x = self.conv2(x)    # → (batch, 64, 11, 11)
        x = self.relu2(x)    # → (batch, 64, 11, 11)
        x = self.pool2(x)    # → (batch, 64, 5, 5)

        # Flatten 3D tensor → 1D vector (keep batch dimension)
        x = x.view(x.size(0), -1)  # → (batch, 1600)
        # x.size(0) = batch size
        # -1 means "compute this dimension automatically" = 64×5×5 = 1600

        # Classification
        x = self.fc1(x)      # → (batch, 128)
        x = self.relu3(x)    # → (batch, 128)
        x = self.dropout(x)  # → (batch, 128) — some zeroed during training
        x = self.fc2(x)      # → (batch, 10)  — 10 raw scores (logits)

        return x

# ── Step 4: Instantiate model, loss, optimizer ───────────────────────────
model = SimpleCNN().to(device)  # move model to GPU if available

# Print model summary: parameter count per layer
total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f"Total trainable parameters: {total_params:,}")

# CrossEntropyLoss: combines LogSoftmax + NLLLoss
# Do NOT apply softmax before this — it is included internally
criterion = nn.CrossEntropyLoss()

# Adam optimizer — good default for CNNs
optimizer = optim.Adam(model.parameters(), lr=0.001)

# ── Step 5: Training function ─────────────────────────────────────────────
def train_epoch(model, loader, optimizer, criterion, device):
    model.train()  # enable dropout, batch norm in training mode
    total_loss = 0
    correct = 0
    total = 0

    for batch_idx, (images, labels) in enumerate(loader):
        # Move data to device (GPU or CPU)
        images, labels = images.to(device), labels.to(device)

        # CRITICAL: clear gradients from previous step
        # Without this, gradients accumulate and weights explode
        optimizer.zero_grad()

        # Forward pass: get predictions
        outputs = model(images)        # shape: (64, 10)

        # Compute loss
        loss = criterion(outputs, labels)  # compare logits to true labels

        # Backward pass: compute gradients
        loss.backward()

        # Update weights using gradients
        optimizer.step()

        # Track metrics
        total_loss += loss.item()
        _, predicted = outputs.max(1)          # index of highest score = predicted class
        correct += (predicted == labels).sum().item()
        total += labels.size(0)

        # Print progress every 100 batches
        if batch_idx % 100 == 0:
            print(f"  Batch {batch_idx}/{len(loader)}, Loss: {loss.item():.4f}")

    avg_loss = total_loss / len(loader)
    accuracy = correct / total
    return avg_loss, accuracy

# ── Step 6: Evaluation function ───────────────────────────────────────────
def evaluate(model, loader, criterion, device):
    model.eval()  # disable dropout
    total_loss = 0
    correct = 0
    total = 0

    with torch.no_grad():  # disable gradient computation — saves memory at inference
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)

            outputs = model(images)
            loss = criterion(outputs, labels)

            total_loss += loss.item()
            _, predicted = outputs.max(1)
            correct += (predicted == labels).sum().item()
            total += labels.size(0)

    return total_loss / len(loader), correct / total

# ── Step 7: Training loop ─────────────────────────────────────────────────
EPOCHS = 5  # 5 epochs is enough for MNIST (~99% accuracy)

for epoch in range(1, EPOCHS + 1):
    print(f"\nEpoch {epoch}/{EPOCHS}")
    print("-" * 40)

    train_loss, train_acc = train_epoch(model, train_loader, optimizer, criterion, device)
    test_loss, test_acc = evaluate(model, test_loader, criterion, device)

    print(f"Train: Loss={train_loss:.4f}, Accuracy={train_acc:.2%}")
    print(f"Test:  Loss={test_loss:.4f}, Accuracy={test_acc:.2%}")

# ── Step 8: Make predictions on a sample ─────────────────────────────────
model.eval()
sample_images, sample_labels = next(iter(test_loader))
sample_images = sample_images[:5].to(device)

with torch.no_grad():
    outputs = model(sample_images)
    probabilities = torch.softmax(outputs, dim=1)  # convert logits to probabilities
    _, predictions = outputs.max(1)

print("\nSample predictions:")
for i in range(5):
    predicted_digit = predictions[i].item()
    confidence = probabilities[i][predicted_digit].item()
    true_digit = sample_labels[i].item()
    print(f"  Image {i+1}: True={true_digit}, Predicted={predicted_digit}, "
          f"Confidence={confidence:.1%}")
```

---

## Expected Output

After 5 epochs, you should see approximately:
```
Train: Loss=0.0200, Accuracy=99.4%
Test:  Loss=0.0350, Accuracy=98.9%
```

MNIST is a relatively easy dataset — a simple CNN achieves ~99% accuracy.

---

## What to Experiment With

1. **Add Batch Normalization** after each conv layer: `nn.BatchNorm2d(out_channels)` — does training become more stable?
2. **Remove Dropout** — does the gap between train and test accuracy grow?
3. **Add a third conv block** — does accuracy improve?
4. **Try different learning rates** (0.0001, 0.01) — which converges fastest?
5. **Replace MaxPool with stride=2 in conv** — many modern networks avoid pooling layers entirely

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | CNN architecture deep dive |

⬅️ **Prev:** [08 Regularization](../08_Regularization/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [10 RNNs](../10_RNNs/Theory.md)
