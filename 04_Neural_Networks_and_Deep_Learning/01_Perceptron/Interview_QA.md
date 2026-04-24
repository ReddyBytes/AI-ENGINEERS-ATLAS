# Perceptron — Interview Q&A

## Beginner

**Q1: What is a perceptron?**

<details>
<summary>💡 Show Answer</summary>

A perceptron is the simplest artificial neuron. It takes several inputs, multiplies each by a weight (indicating how important that input is), sums everything up along with a bias term, and passes the result through a step function to produce a binary output (0 or 1).

</details>

---

**Q2: What is a weight in a perceptron?**

<details>
<summary>💡 Show Answer</summary>

A weight is a number that controls how much influence a particular input has on the output. A large positive weight means that input strongly pushes the output toward 1. A large negative weight means it pushes the output toward 0. Weights are learned from data during training.

</details>

---

**Q3: What is the bias in a perceptron and why do we need it?**

<details>
<summary>💡 Show Answer</summary>

The bias is a constant added to the weighted sum before the activation function. Without a bias, the decision boundary must pass through the origin of the input space. That is very restrictive. The bias allows the decision boundary to shift freely so the perceptron can fit a much wider range of problems.

</details>

---

## Intermediate

**Q4: What is linear separability and why does it matter for a perceptron?**

<details>
<summary>💡 Show Answer</summary>

A dataset is linearly separable if you can draw a single straight line (or hyperplane in higher dimensions) that perfectly separates the two classes. A perceptron can only learn a single linear decision boundary, so it can only solve linearly separable problems. If the data is not linearly separable — like XOR — the perceptron learning rule will never converge on a correct answer.

</details>

---

**Q5: Explain the XOR problem and why it matters historically.**

<details>
<summary>💡 Show Answer</summary>

XOR outputs 1 when exactly one of the two inputs is 1. When you plot the four possible XOR inputs on a 2D graph, the two classes (0 and 1) cannot be separated by any single straight line. Marvin Minsky and Seymour Papert proved this in their 1969 book "Perceptrons," which led to reduced funding for AI research. The solution — using multiple layers of neurons — was not widely adopted until the 1980s with backpropagation.

</details>

---

**Q6: What is the perceptron learning rule?**

<details>
<summary>💡 Show Answer</summary>

The perceptron learning rule updates each weight based on the prediction error:

`w_new = w_old + learning_rate × (target - prediction) × input`

If the perceptron predicts correctly, the error is 0 and weights don't change. If it predicts wrong, weights are adjusted in the direction that would have produced the correct answer. This is guaranteed to converge to a solution if the data is linearly separable.

</details>

---

## Advanced

**Q7: What is the difference between a perceptron and a logistic regression unit?**

<details>
<summary>💡 Show Answer</summary>

Both take a weighted sum of inputs plus bias. The difference is the activation function. A perceptron uses a hard step function — the output is exactly 0 or 1. Logistic regression uses a sigmoid function — the output is a smooth probability between 0 and 1. The sigmoid allows gradient-based optimization (backpropagation) because it has a defined derivative everywhere. The step function has zero gradient almost everywhere, making gradient-based learning impossible — which is one reason the original perceptron could not be used in deep networks.

</details>

---

**Q8: Why can a single perceptron not learn non-linear decision boundaries?**

<details>
<summary>💡 Show Answer</summary>

A perceptron computes a linear combination of its inputs: `w·x + b`. Setting this equal to zero defines a hyperplane — a flat, straight boundary. No matter what weights you choose, you can only ever produce a flat boundary. Non-linear problems like XOR, concentric circles, or spirals require curved boundaries, which require combining multiple linear boundaries — i.e., multiple layers. This is the core motivation for multi-layer networks.

</details>

---

**Q9: If a single perceptron is so limited, why is it still taught?**

<details>
<summary>💡 Show Answer</summary>

Three reasons. First, it is the foundation — every neuron in every modern network is a generalized perceptron with a better activation function. Understanding weights, bias, and the learning rule is essential before understanding backpropagation. Second, for linearly separable problems it is extremely fast and interpretable. Third, the perceptron convergence theorem is one of the first formal proofs in machine learning — understanding it builds intuition for why convergence proofs matter and when to trust them.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |

⬅️ **Prev:** [08 Naive Bayes](../../03_Classical_ML_Algorithms/08_Naive_Bayes/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [02 MLPs](../02_MLPs/Theory.md)
