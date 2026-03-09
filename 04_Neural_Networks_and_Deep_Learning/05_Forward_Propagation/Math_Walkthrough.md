# Forward Propagation — Math Walkthrough

## The Network

We use a tiny 2-layer network so every number is visible.

**Architecture:**
- 2 inputs
- Layer 1: 2 neurons, ReLU activation
- Layer 2: 1 neuron, sigmoid activation
- 1 output (binary prediction)

---

## Given Values

**Input:**
```
x = [0.5, 0.8]
```

**Layer 1 weights and bias:**
```
W1 = [[0.4,  0.6],    ← neuron 1's weights for x1 and x2
       [-0.3, 0.9]]   ← neuron 2's weights for x1 and x2

b1 = [0.1, -0.2]
```

**Layer 2 weights and bias:**
```
W2 = [[0.7, -0.5]]   ← single output neuron's weights for a1[0] and a1[1]

b2 = [0.3]
```

**True label:**
```
y = 1  (the correct answer is "yes")
```

---

## Step 1: Layer 1 Linear Transformation

Compute `z1 = W1 × x + b1`

```
Neuron 1:
  z1[0] = W1[0,0]×x[0] + W1[0,1]×x[1] + b1[0]
        = 0.4×0.5 + 0.6×0.8 + 0.1
        = 0.20   + 0.48   + 0.10
        = 0.78

Neuron 2:
  z1[1] = W1[1,0]×x[0] + W1[1,1]×x[1] + b1[1]
        = -0.3×0.5 + 0.9×0.8 + (-0.2)
        = -0.15   + 0.72   - 0.20
        = 0.37
```

**Result:** `z1 = [0.78, 0.37]`

---

## Step 2: Layer 1 Activation (ReLU)

```
ReLU(z) = max(0, z)

a1[0] = max(0, 0.78) = 0.78
a1[1] = max(0, 0.37) = 0.37
```

**Result:** `a1 = [0.78, 0.37]`

Both values are positive, so ReLU passes them through unchanged. If either were negative, it would become 0.

---

## Step 3: Layer 2 Linear Transformation

Compute `z2 = W2 × a1 + b2`

```
Output neuron:
  z2[0] = W2[0,0]×a1[0] + W2[0,1]×a1[1] + b2[0]
        = 0.7×0.78 + (-0.5)×0.37 + 0.3
        = 0.546    -  0.185      + 0.3
        = 0.661
```

**Result:** `z2 = [0.661]`

---

## Step 4: Layer 2 Activation (Sigmoid)

```
sigmoid(z) = 1 / (1 + e^(-z))

ŷ = sigmoid(0.661)
  = 1 / (1 + e^(-0.661))
  = 1 / (1 + 0.516)
  = 1 / 1.516
  = 0.660
```

**Result:** `ŷ = 0.660`

The network predicts a 66% probability that the answer is class 1.

---

## Step 5: Compute the Loss

True label y = 1. Predicted probability ŷ = 0.660.

Using **Binary Cross-Entropy:**
```
Loss = -[ y × log(ŷ) + (1-y) × log(1-ŷ) ]
     = -[ 1 × log(0.660) + 0 × log(0.340) ]
     = -[ log(0.660) ]
     = -[ -0.415 ]
     = 0.415
```

**Result:** Loss = 0.415

This is moderately wrong — the model predicted 0.66 when the answer was 1. If it had predicted 0.99, loss would be about 0.01. If it had predicted 0.01, loss would be about 4.6.

---

## Summary: All Values at Each Step

| Step | Variable | Value |
|------|----------|-------|
| Input | x | [0.5, 0.8] |
| Layer 1 pre-activation | z1 | [0.78, 0.37] |
| Layer 1 output | a1 | [0.78, 0.37] |
| Layer 2 pre-activation | z2 | [0.661] |
| Layer 2 output (prediction) | ŷ | 0.660 |
| True label | y | 1 |
| Loss | L | 0.415 |

---

## What Comes Next?

These values are saved. Backpropagation will take the loss (0.415) and work backward through this same network, computing how much each weight contributed to the error. The next document (`../06_Backpropagation/Math_Walkthrough.md`) continues from exactly this point.

---

## Quick Mental Model

```
Input [0.5, 0.8]
  ↓  multiply by W1, add b1
z1 = [0.78, 0.37]
  ↓  ReLU
a1 = [0.78, 0.37]
  ↓  multiply by W2, add b2
z2 = [0.661]
  ↓  Sigmoid
ŷ  = [0.660]
  ↓  compare to y=1
Loss = 0.415
```

That is the entire forward pass. No mystery. Just multiply, add, apply function. Repeat.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Math_Walkthrough.md** | ← you are here |

⬅️ **Prev:** [04 Loss Functions](../04_Loss_Functions/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [06 Backpropagation](../06_Backpropagation/Theory.md)
