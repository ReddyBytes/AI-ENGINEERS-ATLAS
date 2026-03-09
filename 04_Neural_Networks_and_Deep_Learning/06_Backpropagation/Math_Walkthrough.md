# Backpropagation — Math Walkthrough

## Continuing From Forward Propagation

This walkthrough uses the exact same network and values from `../05_Forward_Propagation/Math_Walkthrough.md`.

**Recap of forward pass results:**
```
Input:          x  = [0.5, 0.8]
Layer 1 output: a1 = [0.78, 0.37]   (after ReLU)
Layer 2 input:  z2 = 0.661
Prediction:     ŷ  = 0.660          (after sigmoid)
True label:     y  = 1
Loss:           L  = 0.415
```

**Weights used:**
```
W1 = [[0.4,  0.6],
      [-0.3, 0.9]]
b1 = [0.1, -0.2]
W2 = [[0.7, -0.5]]
b2 = [0.3]
```

**Learning rate:** lr = 0.1

---

## The Goal

Compute the gradient of the loss with respect to every weight and bias:
`dL/dW2, dL/db2, dL/dW1, dL/db1`

Then update each weight to reduce the loss.

---

## Step 1: Gradient at the Output (dL/dŷ combined with sigmoid)

For binary cross-entropy loss combined with sigmoid output, the combined gradient simplifies beautifully:

```
dL/dz2 = ŷ - y = 0.660 - 1 = -0.340
```

This means: the pre-activation value z2 needs to increase to make the prediction closer to 1.

---

## Step 2: Gradients for Layer 2 Weights (dL/dW2, dL/db2)

The layer 2 computation was: `z2 = W2 × a1 + b2`

**Gradient for W2:**
```
dL/dW2[0,0] = dL/dz2 × a1[0] = -0.340 × 0.78 = -0.265
dL/dW2[0,1] = dL/dz2 × a1[1] = -0.340 × 0.37 = -0.126
```

**Gradient for b2:**
```
dL/db2 = dL/dz2 = -0.340
```

---

## Step 3: Update Layer 2 Weights

```
W2_new[0,0] = W2[0,0] - lr × dL/dW2[0,0]
            = 0.7 - 0.1 × (-0.265)
            = 0.7 + 0.0265
            = 0.7265

W2_new[0,1] = W2[0,1] - lr × dL/dW2[0,1]
            = -0.5 - 0.1 × (-0.126)
            = -0.5 + 0.0126
            = -0.4874

b2_new = b2 - lr × dL/db2
       = 0.3 - 0.1 × (-0.340)
       = 0.3 + 0.034
       = 0.334
```

Both W2 weights increased slightly. Since the model was predicting too low (0.660 vs 1.0), increasing W2 will push the output higher next time.

---

## Step 4: Propagate Error Back to Layer 1 (dL/da1)

The gradient flowing back to layer 1 activations:

```
dL/da1[0] = dL/dz2 × W2[0,0] = -0.340 × 0.7  = -0.238
dL/da1[1] = dL/dz2 × W2[0,1] = -0.340 × (-0.5) = 0.170
```

---

## Step 5: Pass Through ReLU (dL/dz1)

ReLU derivative: 1 if z > 0, else 0.

From the forward pass: z1 = [0.78, 0.37]. Both are positive, so both ReLU derivatives are 1.

```
dL/dz1[0] = dL/da1[0] × ReLU'(z1[0]) = -0.238 × 1 = -0.238
dL/dz1[1] = dL/da1[1] × ReLU'(z1[1]) =  0.170 × 1 =  0.170
```

If either z1 had been negative, ReLU would have killed the gradient (multiplied by 0).

---

## Step 6: Gradients for Layer 1 Weights (dL/dW1, dL/db1)

Layer 1 computation was: `z1 = W1 × x + b1`

**Gradient for W1:**
```
dL/dW1[0,0] = dL/dz1[0] × x[0] = -0.238 × 0.5 = -0.119
dL/dW1[0,1] = dL/dz1[0] × x[1] = -0.238 × 0.8 = -0.190
dL/dW1[1,0] = dL/dz1[1] × x[0] =  0.170 × 0.5 =  0.085
dL/dW1[1,1] = dL/dz1[1] × x[1] =  0.170 × 0.8 =  0.136
```

**Gradient for b1:**
```
dL/db1[0] = dL/dz1[0] = -0.238
dL/db1[1] = dL/dz1[1] =  0.170
```

---

## Step 7: Update Layer 1 Weights

```
W1_new[0,0] = 0.4  - 0.1 × (-0.119) = 0.4  + 0.0119 = 0.412
W1_new[0,1] = 0.6  - 0.1 × (-0.190) = 0.6  + 0.019  = 0.619
W1_new[1,0] = -0.3 - 0.1 × (0.085)  = -0.3 - 0.0085 = -0.309
W1_new[1,1] = 0.9  - 0.1 × (0.136)  = 0.9  - 0.0136 = 0.886

b1_new[0] = 0.1  - 0.1 × (-0.238) = 0.1  + 0.0238 = 0.124
b1_new[1] = -0.2 - 0.1 × (0.170)  = -0.2 - 0.017  = -0.217
```

---

## Summary: Before and After

| Parameter | Before | Gradient | After |
|-----------|--------|----------|-------|
| W2[0,0] | 0.700 | -0.265 | 0.727 |
| W2[0,1] | -0.500 | -0.126 | -0.487 |
| b2[0] | 0.300 | -0.340 | 0.334 |
| W1[0,0] | 0.400 | -0.119 | 0.412 |
| W1[0,1] | 0.600 | -0.190 | 0.619 |
| W1[1,0] | -0.300 | 0.085 | -0.309 |
| W1[1,1] | 0.900 | 0.136 | 0.886 |
| b1[0] | 0.100 | -0.238 | 0.124 |
| b1[1] | -0.200 | 0.170 | -0.217 |

---

## What Happens Next?

Run the next forward pass with the updated weights. The prediction will be closer to 1. The loss will be lower. Repeat thousands of times. That is training.

---

## The Chain Rule Path Visualized

```
Loss L
  ↑  dL/dz2 = ŷ - y = -0.340
z2
  ↑  dL/dW2 = dL/dz2 × a1    (layer 2 weights)
  ↑  dL/da1 = dL/dz2 × W2    (propagate back to layer 1)
a1  (ReLU)
  ↑  dL/dz1 = dL/da1 × ReLU' (through activation)
z1
  ↑  dL/dW1 = dL/dz1 × x     (layer 1 weights)
  ↑  dL/db1 = dL/dz1          (layer 1 biases)
```

Each arrow is one application of the chain rule. This is exactly what `loss.backward()` does in PyTorch — automatically.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Math_Walkthrough.md** | ← you are here |

⬅️ **Prev:** [05 Forward Propagation](../05_Forward_Propagation/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [07 Optimizers](../07_Optimizers/Theory.md)
