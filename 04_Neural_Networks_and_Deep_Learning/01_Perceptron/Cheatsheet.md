# Perceptron — Cheatsheet

**One-liner:** A perceptron is a single artificial neuron that takes weighted inputs, adds a bias, and outputs 0 or 1 via a step function.

---

## Key Terms

| Term | What it means |
|------|---------------|
| Input (x) | Raw data fed into the neuron |
| Weight (w) | How important each input is (learned) |
| Bias (b) | A constant that shifts the decision threshold |
| Weighted sum | w1×x1 + w2×x2 + ... + b |
| Step function | If sum ≥ 0 → output 1, else → output 0 |
| Linear separability | Can the two classes be split by one straight line? |
| XOR problem | A problem no single perceptron can solve — not linearly separable |
| Perceptron learning rule | Update weights based on prediction error |
| Convergence | Perceptron is guaranteed to find correct weights IF data is linearly separable |

---

## Formula

```
output = step( Σ(wi × xi) + b )
```

Where `step(z) = 1 if z ≥ 0, else 0`

---

## Perceptron Learning Rule

```
w_new = w_old + lr × (target - prediction) × x
b_new = b_old + lr × (target - prediction)
```

`lr` = learning rate (a small number like 0.1)

---

## When to Use / Not Use

| Use a Perceptron when... | Do NOT use when... |
|--------------------------|--------------------|
| Problem is linearly separable | Problem is non-linear (XOR, circles, spirals) |
| Binary classification only | Multi-class classification needed |
| Learning the concept of weights/bias | You need real accuracy on real data |
| Baseline understanding | Any serious production task |

---

## Golden Rules

1. Weights control importance. Bias controls threshold.
2. A single perceptron = a single straight line decision boundary.
3. The XOR problem shows a single perceptron has hard limits.
4. Perceptron learning is guaranteed to converge on linearly separable data — but will loop forever on non-separable data.
5. Every layer of every neural network is just many perceptrons running in parallel, with better activation functions.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |

⬅️ **Prev:** [08 Naive Bayes](../../03_Classical_ML_Algorithms/08_Naive_Bayes/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [02 MLPs](../02_MLPs/Theory.md)
