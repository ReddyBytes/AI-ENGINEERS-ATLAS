# Logistic Regression — Math Intuition

## The Sigmoid Function: Making Any Number a Probability

The core question: how do you turn a linear equation (which can output anything) into a probability (which must be between 0 and 1)?

The answer: the sigmoid function.

```
sigmoid(z) = 1 / (1 + e^(-z))
```

What does it look like?

```
Output
1.0  |                    ..............
     |               .....
0.9  |           ....
     |         ..
0.5  |........·  ← crossover at z=0
     |    ....
0.1  |   ..
     | ...
0.0  |...._________________________
     -6  -4  -2   0   2   4   6    Input z
```

The S-shape (sigmoid = S-shaped) has three key zones:
- **z very negative** → output near 0 (confident "not this class")
- **z near 0** → output near 0.5 (uncertain)
- **z very positive** → output near 1 (confident "this class")

---

## Why It Squishes to (0, 1)

For any value of z:
- When z → +∞: e^(-z) → 0, so denominator → 1+0 = 1, so sigmoid → 1/1 = 1
- When z → -∞: e^(-z) → ∞, so denominator → ∞, so sigmoid → 1/∞ ≈ 0
- When z = 0: e^0 = 1, so sigmoid = 1/(1+1) = 0.5

The output is always strictly between 0 and 1. Any real number maps to a valid probability.

---

## The Linear Equation Inside

Before the sigmoid, there is a linear equation (same structure as linear regression):

```
z = w₁×feature₁ + w₂×feature₂ + w₃×feature₃ + b
```

For the emergency room:
```
z = 0.05 × heart_rate + 0.03 × age + 2.1 × chest_pain - 8.0

Patient: HR=140, age=68, chest_pain=1
z = 0.05×140 + 0.03×68 + 2.1×1 - 8.0
z = 7.0 + 2.04 + 2.1 - 8.0 = 3.14

sigmoid(3.14) = 1 / (1 + e^(-3.14)) = 1 / (1 + 0.043) ≈ 0.96

P(emergency) = 96%  →  EMERGENCY
```

---

## Decision Boundary: Where the Line Is

The decision boundary is where the model is exactly 50/50 — sigmoid output = 0.5.

Sigmoid = 0.5 when z = 0.

So the decision boundary is:
```
w₁×feature₁ + w₂×feature₂ + b = 0
```

In ASCII art with two features (feature₁ = heart rate, feature₂ = age):

```
Age
 80 |   ●   ●  Emergency |
    |  ●  ●   ●          |
 60 |●   ●    /  ●       |
    |     ●  /           |
 40 |    ●  /  × × ×     |
    |   × ×/  ×  ×  ×    |
 20 |    ×/ ×   ×   ×    |
    |____|_______________ Heart Rate
         |
     Decision boundary
     (the line where probability = 0.5)

● = Emergency (actual), × = Not emergency (actual)
```

Everything above-left of the line: "Emergency." Everything below-right: "Not emergency."

This boundary is always a straight line. If the actual boundary in your problem is curved, logistic regression will be suboptimal without feature engineering.

---

## What the Weights Tell You

Each weight wᵢ controls how much feature i shifts the probability:

- **Positive weight + increase in feature → probability goes up**
- **Negative weight + increase in feature → probability goes down**
- **Large magnitude weight → feature strongly influences the outcome**
- **Weight near zero → feature barely matters**

After training a loan approval model, you might see:
```
credit_score:     w = +0.008  (higher score → more likely approved)
missed_payments:  w = -0.42   (more missed payments → much less likely approved)
income:           w = +0.0001 (higher income → slightly more likely approved)
age:              w = +0.01   (older → slightly more likely approved)
```

This tells you missed_payments is the most influential feature (largest absolute weight). This interpretability is why logistic regression is still used in credit scoring and medical risk models where decisions must be explainable.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concept |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Math_Intuition.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [01 Linear Regression](../01_Linear_Regression/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 Decision Trees](../03_Decision_Trees/Theory.md)
