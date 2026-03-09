# Training Troubleshooting Guide

A practical reference for diagnosing and fixing common training problems. For each symptom, you will find: what it means, the most likely causes, and how to fix it.

---

## Quick Symptom Index

| Symptom | Jump to |
|---------|---------|
| Loss is not decreasing | [Section 1](#1-loss-is-not-decreasing) |
| Loss explodes or becomes NaN | [Section 2](#2-loss-explodes-or-becomes-nan) |
| Overfitting (train good, val bad) | [Section 3](#3-overfitting) |
| Underfitting (both train and val bad) | [Section 4](#4-underfitting) |
| Training is too slow | [Section 5](#5-training-too-slow) |
| Model predicts one class for everything | [Section 6](#6-model-predicts-one-class-always) |
| Loss oscillates wildly | [Section 7](#7-loss-oscillates-wildly) |

---

## 1. Loss Is Not Decreasing

**What it means:** The model is not learning. Loss stays flat from the first epoch onward.

| Likely Cause | How to Diagnose | Fix |
|-------------|----------------|-----|
| Learning rate too small | Plot loss — barely moves | Increase lr by 10× |
| Wrong loss function | Check task type vs loss used | Use CE for classification, MSE for regression |
| Wrong output activation | Check final layer | Sigmoid for binary, Softmax for multi-class, None for regression |
| Bug in training loop | Print losses each step | Check you are calling `loss.backward()` and `optimizer.step()` |
| Forgetting to zero gradients | Check PyTorch code | Add `optimizer.zero_grad()` before each forward pass |
| Data not loading correctly | Print first batch | Verify shapes, labels, and label range |
| Model not in training mode | Check mode | Call `model.train()` before training loop |

**Quick check list:**
```python
optimizer.zero_grad()    # ← must be first
outputs = model(inputs)  # forward
loss = criterion(outputs, labels)
loss.backward()          # compute gradients
optimizer.step()         # update weights
```

---

## 2. Loss Explodes or Becomes NaN

**What it means:** Loss jumps to very large values or becomes `nan` (not a number). Training is unstable.

| Likely Cause | How to Diagnose | Fix |
|-------------|----------------|-----|
| Learning rate too large | Explodes in first few steps | Reduce lr by 10× |
| Vanishing/exploding gradients | Print gradient norms | Add gradient clipping: `clip_grad_norm_(model.parameters(), 1.0)` |
| NaN in input data | Check `torch.isnan(inputs).any()` | Remove or impute NaN values before training |
| Bad weight initialization | Check activations at init | Use He/Xavier init, avoid zeros or very large values |
| Numerical instability in loss | Check if softmax is applied before CrossEntropyLoss | Use `nn.CrossEntropyLoss()` directly on logits — it is numerically stable |
| Batch normalization with batch size 1 | BatchNorm needs >1 sample | Use batch size ≥ 2, or switch to LayerNorm |

**Gradient clipping in PyTorch:**
```python
loss.backward()
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
optimizer.step()
```

---

## 3. Overfitting

**What it means:** Training loss is low and continues to drop, but validation loss is high and rising. The model has memorized training data.

| Likely Cause | How to Diagnose | Fix |
|-------------|----------------|-----|
| Model is too large | Large gap between train and val loss | Reduce number of layers or neurons |
| Not enough training data | Compare train/val loss gap | Collect more data |
| No regularization | Check model code | Add L2 (weight_decay in optimizer), Dropout |
| Training too long | Loss gap grows with epochs | Use early stopping |
| Insufficient data augmentation | Check transforms | Add augmentation (flip, crop, color jitter for images) |
| Learning rate too small | Model converges on train, not val | Slightly increase lr |

**Regularization checklist:**
```python
# L2 weight decay in optimizer
optimizer = torch.optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-4)

# Dropout in model
self.dropout = nn.Dropout(p=0.5)  # use in fully-connected layers

# Early stopping: save best checkpoint
if val_loss < best_val_loss:
    best_val_loss = val_loss
    torch.save(model.state_dict(), 'best_model.pth')
```

---

## 4. Underfitting

**What it means:** Both training loss and validation loss are high. The model is not learning enough — too simple for the task.

| Likely Cause | How to Diagnose | Fix |
|-------------|----------------|-----|
| Model is too small | Loss plateaus at high value | Add more layers or more neurons per layer |
| Too much regularization | L2 lambda or dropout too high | Reduce weight_decay, reduce dropout rate |
| Too few epochs | Loss still decreasing at end | Train longer, add early stopping to prevent over-running |
| Learning rate too large | Loss bounces around | Reduce lr — large lr prevents convergence to good minima |
| Features not informative enough | Check feature engineering | Add more relevant features, engineer interactions |
| Wrong model architecture for task | Using MLP for image data | Use CNN for images, RNN/LSTM for sequences |

---

## 5. Training Too Slow

**What it means:** Each epoch takes far too long. You cannot iterate experiments quickly.

| Likely Cause | How to Diagnose | Fix |
|-------------|----------------|-----|
| Data loading is the bottleneck | GPU utilization < 80% | Set `num_workers > 0` in DataLoader |
| Not using GPU | `torch.cuda.is_available()` returns True but model is on CPU | Call `model.to(device)` and `data.to(device)` |
| Batch size too small | Low GPU utilization | Increase batch size until GPU memory is ~80% full |
| Not using mixed precision | Check if amp is enabled | Use `torch.cuda.amp.autocast()` |
| Model is unnecessarily large | Profile forward pass | Use a smaller architecture, depthwise separable convolutions |
| Python overhead in data pipeline | GPU waits for CPU | Use `pin_memory=True` in DataLoader, precompute transforms |

**Fast DataLoader:**
```python
loader = DataLoader(
    dataset,
    batch_size=256,
    num_workers=4,      # parallel data loading threads
    pin_memory=True,    # faster host-to-GPU transfer
    persistent_workers=True  # avoid re-creating workers each epoch
)
```

---

## 6. Model Predicts One Class Always

**What it means:** The model collapses to predicting the same class for every input — even with 99% "accuracy" on imbalanced data.

| Likely Cause | How to Diagnose | Fix |
|-------------|----------------|-----|
| Class imbalance | Check label distribution | Use class weights in loss: `nn.CrossEntropyLoss(weight=class_weights)` |
| Learning rate too large | Early collapse | Reduce lr, add warmup |
| Wrong output activation | Using ReLU on output for classification | Use Sigmoid (binary) or Softmax (multi-class) |
| Loss function mismatch | E.g., MSE for classification | Switch to Cross-Entropy |
| Bad weight initialization | All neurons compute same thing | Check for all-zero weight init |

**Weighted cross-entropy:**
```python
# Count class frequencies
class_counts = torch.tensor([count_class_0, count_class_1], dtype=torch.float)
class_weights = 1.0 / class_counts
class_weights = class_weights / class_weights.sum()  # normalize

criterion = nn.CrossEntropyLoss(weight=class_weights.to(device))
```

---

## 7. Loss Oscillates Wildly

**What it means:** Loss goes up and down erratically from batch to batch or epoch to epoch, never converging smoothly.

| Likely Cause | How to Diagnose | Fix |
|-------------|----------------|-----|
| Learning rate too large | Loss zigzags on training plot | Reduce lr by 5-10× |
| Batch size too small | Very noisy gradient estimates | Increase batch size |
| Bad data (outliers, corrupted labels) | Check sample loss distribution | Inspect and clean dataset |
| No learning rate schedule | Loss improves early then oscillates | Add cosine decay or ReduceLROnPlateau |
| Missing BatchNorm | Activation values very large | Add BatchNorm after conv layers |
| Very imbalanced loss across classes | Per-class loss varies wildly | Use class weights, focal loss |

---

## General Debugging Protocol

When something goes wrong, follow this order:

```
1. Sanity check: overfit on a tiny batch (2–10 samples)
   → If it can't overfit 10 samples, there's a code bug

2. Check shapes: print tensor shapes at every layer
   → Shape mismatches are the #1 bug source

3. Check loss: compute loss on first batch manually
   → Initial cross-entropy should be ≈ log(num_classes)
   → For 10 classes: log(10) ≈ 2.3

4. Check gradients: print gradient norms after first backward
   → All None = backward not called / graph broken
   → All zero = dead neurons or wrong loss
   → Very large (>100) = exploding gradients

5. Check data: visualize first batch
   → Are labels correct? Normalized? Expected range?

6. Ablate: disable one component at a time
   → Remove dropout, remove augmentation, try different lr
```

---

## Sanity Check Code

```python
# Test: can the model overfit a tiny batch?
# This should ALWAYS work — if it doesn't, there's a bug.

tiny_x = X_train[:4]   # just 4 samples
tiny_y = y_train[:4]

optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

for step in range(200):
    model.train()
    optimizer.zero_grad()
    pred = model(tiny_x)
    loss = criterion(pred, tiny_y)
    loss.backward()
    optimizer.step()

    if step % 50 == 0:
        print(f"Step {step}: Loss = {loss.item():.4f}")

# If loss doesn't approach 0 after 200 steps:
# → Wrong loss function, wrong output activation, or broken training loop
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Troubleshooting_Guide.md** | ← you are here |

⬅️ **Prev:** [11 GANs](../11_GANs/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [01 Text Preprocessing](../../05_NLP_Foundations/01_Text_Preprocessing/Theory.md)
