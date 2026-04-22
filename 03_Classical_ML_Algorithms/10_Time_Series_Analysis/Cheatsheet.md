# Time Series Analysis — Cheatsheet

## Components of a Time Series

| Component | Description | Example |
|---|---|---|
| **Trend** | Long-term direction (up/down/flat) | Population growth over decades |
| **Seasonality** | Regular, fixed-period patterns | Holiday sales spike every December |
| **Cyclical** | Irregular long-period patterns | Business cycles (2–10 years) |
| **Residual** | Random noise after removing above | Daily weather fluctuations |

---

## Stationarity Tests

```python
from statsmodels.tsa.stattools import adfuller

result = adfuller(series)
print(f"ADF Statistic: {result[0]:.4f}")
print(f"p-value: {result[1]:.4f}")
# p-value < 0.05 → reject null → series IS stationary
# p-value > 0.05 → fail to reject → series is NON-stationary → difference it
```

**How to achieve stationarity:**
- Linear trend → first difference: `series.diff(1).dropna()`
- Multiplicative trend → log transform + difference: `np.log(series).diff(1).dropna()`
- Seasonal non-stationarity → seasonal difference: `series.diff(12).dropna()` (monthly data)

---

## ACF / PACF Interpretation

```python
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 2, figsize=(12, 4))
plot_acf(stationary_series, lags=40, ax=axes[0])
plot_pacf(stationary_series, lags=40, ax=axes[1])
plt.show()
```

| Pattern | Suggests |
|---|---|
| PACF cuts off at lag p, ACF tails off | AR(p) |
| ACF cuts off at lag q, PACF tails off | MA(q) |
| Both tail off gradually | ARMA(p,q) |
| ACF shows slow decay | Non-stationary — difference first |

---

## ARIMA(p, d, q) Reference

| Parameter | Name | Choose Based On |
|---|---|---|
| **p** | AR order | PACF cutoff lag |
| **d** | Integration / differencing | Number of differences for stationarity |
| **q** | MA order | ACF cutoff lag |

```python
from statsmodels.tsa.arima.model import ARIMA

# Fit
model = ARIMA(train, order=(p, d, q))
result = model.fit()

# Forecast
forecast = result.get_forecast(steps=h)
pred = forecast.predicted_mean
ci = forecast.conf_int()      # confidence intervals

# Auto-select p,d,q
# pip install pmdarima
from pmdarima import auto_arima
best = auto_arima(train, seasonal=False, information_criterion="aic")
print(best.summary())
```

---

## SARIMA Quick Reference

```python
from statsmodels.tsa.statespace.sarimax import SARIMAX

# SARIMA(p,d,q)(P,D,Q,s)
# s = seasonal period: 12=monthly/yearly, 7=daily/weekly, 4=quarterly
model = SARIMAX(train, order=(1,1,1), seasonal_order=(1,1,1,12))
result = model.fit(disp=False)
forecast = result.forecast(steps=24)
```

---

## Prophet Quick Reference

```python
from prophet import Prophet
import pandas as pd

# Prophet requires columns named "ds" (datetime) and "y" (value)
df = pd.DataFrame({"ds": pd.date_range("2020-01-01", periods=len(y), freq="M"),
                   "y": y})

model = Prophet(
    yearly_seasonality=True,
    weekly_seasonality=True,
    daily_seasonality=False,
    changepoint_prior_scale=0.05,   # higher = more flexible trend
)
model.fit(df)

future = model.make_future_dataframe(periods=12, freq="M")
forecast = model.predict(future)
fig = model.plot(forecast)
fig2 = model.plot_components(forecast)   # shows trend + seasonality
```

---

## Evaluation Metrics

| Metric | Formula | Use When |
|---|---|---|
| **RMSE** | `√mean((pred−true)²)` | Penalize large errors; common default |
| **MAE** | `mean(|pred−true|)` | Robust to outliers; interpretable units |
| **MAPE** | `mean(|pred−true| / |true|) × 100%` | Percentage error; **avoid when y can be 0** |
| **SMAPE** | Symmetric MAPE | Better than MAPE for near-zero values |

---

## Walk-Forward Validation

```python
from sklearn.metrics import mean_squared_error
import numpy as np

def walk_forward_validate(series, order, n_test=30):
    train_size = len(series) - n_test
    errors = []
    for i in range(n_test):
        train = series[:train_size + i]
        test_val = series[train_size + i]
        model = ARIMA(train, order=order).fit()
        pred = model.forecast(steps=1)[0]
        errors.append((pred - test_val) ** 2)
    return np.sqrt(np.mean(errors))   # RMSE
```

---

## ARIMA vs Prophet vs ML Decision Guide

| Situation | Recommended |
|---|---|
| Single variable, short series, need statistical tests | ARIMA / SARIMA |
| Business data with holidays, multiple seasonalities | Prophet |
| Many features (external regressors), large dataset | XGBoost with lag features |
| Long sequences, complex patterns | LSTM / Temporal Fusion Transformer |
| Quick baseline | Prophet |

---

## Golden Rules

1. Never shuffle time series data — always split chronologically
2. Check stationarity (ADF test) before fitting ARIMA
3. Walk-forward validation only — no k-fold
4. Use RMSE or MAE over MAPE (MAPE breaks when y≈0)
5. `auto_arima` from pmdarima saves hours of manual ACF/PACF reading
