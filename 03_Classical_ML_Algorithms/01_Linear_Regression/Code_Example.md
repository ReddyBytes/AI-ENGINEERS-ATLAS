# Linear Regression — Code Example

## Predicting House Prices from Square Footage

We will build a model that takes a house's square footage and predicts its price. This is the simplest possible regression problem — one feature, one output, find the best-fit line.

```python
# ============================================================
# LINEAR REGRESSION — HOUSE PRICE PREDICTION
# Goal: Learn the relationship between square footage and price
# ============================================================

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# ============================================================
# STEP 1: CREATE THE DATASET
# We simulate 20 house sales: square footage → sale price
# In real life, you would load this from a CSV or database
# ============================================================

# Square footage of each house
sq_ft = np.array([
     800, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800,
    1900, 2000, 2100, 2200, 2300, 2500, 2700, 3000, 3200, 3500
]).reshape(-1, 1)  # reshape to 2D array — sklearn expects (n_samples, n_features)

# Sale price of each house (roughly: $100 per sqft + some noise)
price = np.array([
     85000, 102000, 115000, 118000, 132000, 140000, 148000, 161000, 175000, 182000,
    192000, 203000, 214000, 225000, 233000, 251000, 275000, 305000, 322000, 356000
])

print(f"Dataset: {len(sq_ft)} houses")
print(f"Square footage range: {sq_ft.min()} to {sq_ft.max()} sqft")
print(f"Price range: ${price.min():,} to ${price.max():,}")

# ============================================================
# STEP 2: SPLIT INTO TRAINING AND TEST SETS
# 80% of houses for training, 20% for evaluation
# The model will NEVER see test houses during training
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    sq_ft, price,
    test_size=0.2,    # 4 houses held out for testing
    random_state=42
)

print(f"\nTraining houses: {len(X_train)}")
print(f"Test houses: {len(X_test)}")

# ============================================================
# STEP 3: CREATE AND TRAIN THE MODEL
# LinearRegression finds the m (slope) and b (intercept)
# that minimize MSE on the training data
# ============================================================

model = LinearRegression()

# fit() = training — the model studies X_train and y_train
# Internally: finds optimal m and b that minimize MSE
model.fit(X_train, y_train)

# Extract what the model learned
slope = model.coef_[0]         # m — price increase per sqft
intercept = model.intercept_   # b — base price at 0 sqft

print(f"\nModel learned:")
print(f"  Slope (m):     ${slope:.2f} per sqft")
print(f"  Intercept (b): ${intercept:,.2f}")
print(f"\n  Price formula: price = {slope:.1f} × sqft + {intercept:,.0f}")

# ============================================================
# STEP 4: MAKE PREDICTIONS ON THE TEST SET
# Model only sees square footage — it predicts the price
# ============================================================

y_pred = model.predict(X_test)

print("\nTest set predictions:")
print(f"{'Square Ft':<12} {'Actual Price':<18} {'Predicted Price':<18} {'Error'}")
print("-" * 65)
for sqft, actual, predicted in zip(X_test.flatten(), y_test, y_pred):
    error = predicted - actual
    print(f"{sqft:<12,.0f} ${actual:<16,} ${predicted:<16,.0f} ${error:+,.0f}")

# ============================================================
# STEP 5: EVALUATE THE MODEL
# MSE, RMSE: how far off are predictions in dollar terms?
# R²: what fraction of price variation does sqft explain?
# ============================================================

mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)

print(f"\nModel Performance:")
print(f"  MSE:  ${mse:,.0f}")
print(f"  RMSE: ${rmse:,.0f}  ← typical prediction error in dollars")
print(f"  R²:   {r2:.3f}   ← model explains {r2*100:.1f}% of price variance")

# ============================================================
# STEP 6: PREDICT A NEW HOUSE
# This is what real inference looks like
# ============================================================

new_house_sqft = [[1750]]   # a house we have never seen before
predicted_price = model.predict(new_house_sqft)
print(f"\nNew house (1,750 sqft) → Predicted price: ${predicted_price[0]:,.0f}")

# ============================================================
# WHAT A PLOT WOULD SHOW (if you run this with matplotlib)
# ============================================================
# import matplotlib.pyplot as plt
# plt.scatter(sq_ft, price, color='blue', alpha=0.6, label='Actual prices')
# plt.plot(sq_ft, model.predict(sq_ft), color='red', linewidth=2, label='Regression line')
# plt.xlabel('Square Footage')
# plt.ylabel('Price ($)')
# plt.title('Linear Regression: House Price vs Size')
# plt.legend()
# plt.show()
#
# The plot shows:
# - Blue dots: the actual house prices (scattered around the line)
# - Red line: the model's best-fit line through the data
# - The line trends upward — larger houses cost more
# - Points are never perfectly on the line — that's the residual error
```

---

## What This Shows

- **model.fit(X_train, y_train)** is all the training. sklearn internally finds the optimal m and b that minimize MSE.

- **model.coef_ and model.intercept_** expose what the model learned. In this case: roughly $100 per sqft plus a base price. These coefficients are directly interpretable.

- **RMSE** tells you the typical prediction error in the same units as the target (dollars). If RMSE=$8,000, your predictions are typically off by about $8,000 — which may or may not be acceptable depending on the use case.

- **R²** tells you how much of the price variation is explained by square footage alone. A high R² (close to 1) means square footage is a strong predictor. In real life you would add more features (bedrooms, location, age) to improve R².

- **The prediction line** in the plot is the model. Every prediction the model makes lies exactly on that line. The scatter of actual prices around the line represents the irreducible noise — factors beyond square footage that affect price.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concept |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Math_Intuition.md](./Math_Intuition.md) | Math intuition behind the algorithm |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [10 Bias vs Variance](../../02_Machine_Learning_Foundations/10_Bias_vs_Variance/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [02 Logistic Regression](../02_Logistic_Regression/Theory.md)
