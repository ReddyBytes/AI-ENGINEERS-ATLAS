# Linear Regression — Math Intuition

## The Core Equation: y = mx + b

This is the equation of a straight line. In linear regression it becomes:

```
predicted_price = m × square_feet + b
```

Using the road trip analogy:

```
predicted_time = m × distance + b
```

- **m (slope)** = how much time increases per km. If past trips show roughly 1 hour per 100 km, then m ≈ 0.01 (hours per km)
- **b (intercept)** = the predicted time when distance = 0. Realistically, even a 0 km trip has some overhead — packing, loading, checking directions. b might be 0.25 hours.

So the model says: `predicted_time = 0.01 × distance + 0.25`

For 280 km: `0.01 × 280 + 0.25 = 3.05 hours`

---

## What Does "Fitting the Line" Mean Mathematically?

You have a set of known points: (distance₁, actual_time₁), (distance₂, actual_time₂), etc.

You want to find m and b such that the line is as close as possible to all points.

"As close as possible" means: minimize the total squared vertical distance from each point to the line.

```
For each trip:
  error = predicted_time - actual_time

Squared error = error²
  (squaring makes all errors positive and punishes large errors more)

Total MSE = average of all squared errors
```

Visually: each data point has a vertical line connecting it to the regression line. MSE is the average of those vertical distances squared. You want to pull the line into the position where the sum of those squared distances is minimized.

---

## What is MSE and Why Squaring Matters

**Without squaring:**
- Trip 1: predicted 3h, actual 2h → error = +1
- Trip 2: predicted 1h, actual 2h → error = -1
- Average error = 0 (they cancel out)

This looks like the model is perfect — but it is not. It was off by 1 hour both times.

**With squaring:**
- Trip 1: error² = 1
- Trip 2: error² = 1
- Average squared error = 1

Now the model correctly shows non-zero error.

Squaring also has a second effect: **large errors are punished disproportionately.**

- Being off by 1 hour → squared error = 1
- Being off by 5 hours → squared error = 25 (25x worse, not 5x)

This tells the model: "One catastrophically wrong prediction is much worse than five slightly wrong predictions."

---

## Multiple Features: From a Line to a Plane

With one feature: `price = m × sqft + b` → a line in 2D space

With two features: `price = m₁ × sqft + m₂ × bedrooms + b` → a flat plane in 3D space

With many features: `price = m₁×sqft + m₂×bedrooms + m₃×bathrooms + m₄×age + ... + b` → a hyperplane in N-dimensional space

The math works the same way. You are still finding the flat surface that minimizes MSE across all training examples. You just cannot draw it anymore.

**Each coefficient (m) tells you:**
"If this feature increases by 1, and everything else stays the same, the predicted output changes by m."

For a trained house price model:
- m₁ = 150 means: each additional sqft adds $150 to predicted price
- m₂ = 20,000 means: each additional bedroom adds $20,000
- m₃ = -500 means: each additional year of age subtracts $500

This direct interpretability is why linear regression is still widely used in regulated industries.

---

## The Full Training Process

```
Start: pick random m and b (e.g., m=0, b=0)

Repeat until MSE stops decreasing:
  1. For each trip, compute: predicted = m × distance + b
  2. Compute MSE = average of (predicted - actual)²
  3. Compute gradient: how does MSE change if we nudge m up? If we nudge b up?
  4. Move m and b a tiny bit in the direction that reduces MSE

Stop when MSE is minimized → you have the best-fit line
```

This is gradient descent applied to linear regression. For linear regression specifically, the loss surface is a perfect bowl (convex), so gradient descent always finds the global minimum — it cannot get stuck.

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

⬅️ **Prev:** [10 Bias vs Variance](../../02_Machine_Learning_Foundations/10_Bias_vs_Variance/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [02 Logistic Regression](../02_Logistic_Regression/Theory.md)
