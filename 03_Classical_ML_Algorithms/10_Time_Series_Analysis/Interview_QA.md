# Time Series Analysis — Interview Q&A

---

## Beginner

**Q1: What makes time series data different from regular tabular data?**

In regular tabular data, rows are assumed to be independent — shuffling the rows doesn't change anything meaningful. In time series data, rows are ordered in time and are explicitly dependent on each other. Today's stock price depends on yesterday's. This week's electricity demand depends on last week's seasonal pattern. This **autocorrelation** (correlation of a variable with its own past values) violates the independence assumption that most standard ML algorithms rely on. It also means you cannot use standard k-fold cross-validation, which shuffles data randomly.

---

**Q2: What is stationarity and why does ARIMA require it?**

A time series is **stationary** if its statistical properties — mean, variance, and autocorrelation structure — are constant over time. A series with an upward trend is not stationary because its mean changes over time. ARIMA requires stationarity because the model's mathematical formulation assumes that the data-generating process is stable — the same AR and MA coefficients apply at every time point. A trend would require different coefficients at different times, making the model unstable. You check stationarity with the Augmented Dickey-Fuller (ADF) test and achieve it by differencing.

---

**Q3: What are the p, d, q parameters in ARIMA?**

- **p (AR order)**: how many past values to use as predictors. `AR(2)` means the current value depends on the last 2 values: `y_t = c + φ₁y_{t-1} + φ₂y_{t-2} + ε`.
- **d (differencing order)**: how many times to difference the series to achieve stationarity. A series with a linear trend needs d=1 (one difference). d=0 means the series is already stationary.
- **q (MA order)**: how many past error terms to include. `MA(1)` means the current value depends on the last forecast error: `y_t = c + ε_t + θ₁ε_{t-1}`.

---

## Intermediate

**Q4: Why can't you use k-fold cross-validation on time series data?**

K-fold cross-validation shuffles data and creates random train/test splits. For time series, this creates temporal leakage: the test set may contain observations from January while the training set contains observations from February. The model learns to "predict the past from the future" — a task that is impossible in real deployment. The correct approach is **walk-forward validation** (also called time series cross-validation): always train on data up to time t, test on data after t, then expand the training window and repeat. Each test fold must be strictly chronologically after its training fold.

---

**Q5: How do you choose p, d, q for an ARIMA model?**

1. **Choose d**: run the ADF test. If p-value > 0.05, difference the series and retest. The number of differences needed is d.
2. **Choose p**: examine the PACF plot of the stationary series. The lag at which PACF cuts off (drops below the significance band) suggests p.
3. **Choose q**: examine the ACF plot of the stationary series. The lag at which ACF cuts off suggests q.
4. **Validate with AIC/BIC**: fit several candidate models and choose the one with the lowest AIC (Akaike Information Criterion). Alternatively, use `auto_arima` from the pmdarima library to search automatically.

---

**Q6: When would you use Prophet instead of ARIMA?**

Use Prophet when:
- The data has multiple seasonalities (daily + weekly + yearly) — Prophet handles all of them automatically
- The data includes holidays or special events — Prophet accepts a holiday calendar
- There are missing values or irregular timestamps — Prophet handles both gracefully
- You need fast iteration without deep statistical expertise — Prophet requires no stationarity transformation or ACF/PACF reading
- The series has structural breakpoints (trend changes) — Prophet detects changepoints automatically

Use ARIMA when:
- You need formal statistical inference (confidence intervals based on distributional assumptions)
- The series is short (< 2 years of data) — Prophet needs enough data to fit multiple seasonalities
- You need to add exogenous regressors with statistical significance testing (use SARIMAX)

---

## Advanced

**Q7: How would you use XGBoost for time series forecasting?**

XGBoost is not natively a time series model, but time series can be reframed as a tabular supervised learning problem using feature engineering:

1. **Lag features**: create columns for `y_{t-1}`, `y_{t-2}`, ..., `y_{t-k}`
2. **Rolling statistics**: `rolling_mean_7`, `rolling_std_7`, `rolling_max_30`
3. **Calendar features**: `day_of_week`, `month`, `quarter`, `is_holiday`, `week_of_year`
4. **Expanding window features**: cumulative mean, cumulative std

```python
df["lag_1"] = df["y"].shift(1)
df["lag_7"] = df["y"].shift(7)
df["rolling_mean_7"] = df["y"].shift(1).rolling(7).mean()
df["month"] = df["ds"].dt.month
df.dropna(inplace=True)
```

Train/test split must be chronological. Walk-forward cross-validation is required. XGBoost with good feature engineering often outperforms ARIMA on complex non-linear time series.

---

**Q8: What is the difference between additive and multiplicative decomposition?**

In **additive decomposition**: `Y = Trend + Seasonal + Residual`. The seasonal variation has constant magnitude regardless of the level of the trend. Example: a metric that always increases by 100 units in December regardless of the overall level.

In **multiplicative decomposition**: `Y = Trend × Seasonal × Residual`. The seasonal variation scales with the trend level. Example: retail sales that increase by 20% in December — the absolute increase is larger when the baseline is higher. If a series shows increasing seasonal amplitude over time (fan-shaped variance), use multiplicative decomposition or log-transform before additive decomposition.

---

**Q9: How do you detect seasonality and determine the seasonal period?**

Methods to detect seasonality and find period s:
1. **Visual inspection**: plot the series and look for repeating patterns
2. **ACF plot**: significant spikes at regular lags (e.g., lags 12, 24, 36 for monthly data with yearly seasonality)
3. **Periodogram / spectral analysis**: `scipy.signal.periodogram` — peaks correspond to dominant frequencies
4. **Autocorrelation at seasonal lags**: `series.autocorr(lag=12)` — large positive value confirms yearly seasonality in monthly data
5. **Domain knowledge**: monthly sales (s=12), daily data with weekly patterns (s=7), hourly data with daily patterns (s=24)

Once s is determined, use SARIMA with seasonal order `(P,D,Q,s)` or Prophet which detects seasonality automatically.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concept |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |

⬅️ **Prev:** [XGBoost and Boosting](../09_XGBoost_and_Boosting/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Recommendation Systems](../11_Recommendation_Systems/Theory.md)
