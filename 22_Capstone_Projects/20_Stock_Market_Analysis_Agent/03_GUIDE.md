# Project 20 — Build Guide

## Format: Minimal Hints — you figure out the how, hints only where non-obvious

Work through each step in order. Each step has a clear requirement. A hint appears only where the mechanism is genuinely non-obvious. Test each step before moving to the next.

---

## Step 1 — Project Setup and API Verification

**Requirement:** Create a `.env` file with your `ANTHROPIC_API_KEY` and `NEWS_API_KEY`. Write a `setup_check()` function that loads both keys, verifies `ANTHROPIC_API_KEY` starts with `sk-ant-`, and prints a confirmation. The script should fail fast with a clear error message if either key is missing.

Verify: run the script — it should print both keys are loaded.

---

## Step 2 — Fetch and Validate Price Data

**Requirement:** Write a `fetch_price_data(ticker: str) -> pd.DataFrame` function. It should download 1 year of daily OHLCV data for the given ticker. Return the DataFrame. If the download returns an empty DataFrame, raise a `ValueError` with a message that tells the user the ticker was not found.

**Hint:** `yfinance.download(ticker, period='1y', auto_adjust=True)` returns a MultiIndex DataFrame in newer versions. Call `.xs('Close', axis=1, level=0)` to get the Close series, or use `df['Close']` directly depending on your yfinance version. Test with `df.shape` to confirm you have > 200 rows.

---

## Step 3 — Compute Technical Indicators

**Requirement:** Write a `compute_indicators(df: pd.DataFrame) -> dict` function that takes the price DataFrame and returns a dict with these keys: `current_price`, `high_52w`, `low_52w`, `dma_50`, `dma_200`, `rsi`, `macd`, `macd_signal`, `macd_hist`, `bb_upper`, `bb_middle`, `bb_lower`, `volume_avg_20`. All values should be the most recent (last row) rounded to 2 decimal places.

**Hint for RSI:** Compute `delta = df['Close'].diff()`. Use `.clip(lower=0)` for gains and `(-delta.clip(upper=0))` for losses. Apply `.rolling(14).mean()` to both. `RSI = 100 - (100 / (1 + gain/loss))`. Take the `.iloc[-1]` at the end.

**Hint for MACD:** `EMA12 = df['Close'].ewm(span=12, adjust=False).mean()`. Subtract `EMA26` to get MACD line. Signal is `MACD.ewm(span=9, adjust=False).mean()`.

---

## Step 4 — Fetch Fundamental Data

**Requirement:** Write a `fetch_fundamentals(ticker: str) -> dict` function. Use `yfinance.Ticker(ticker).info` to retrieve: `trailingPE`, `priceToBook`, `debtToEquity`, `returnOnEquity`, `marketCap`, `dividendYield`, `sector`, `industry`, `shortName`. Return a dict. If a field is missing from `.info`, default to `"N/A"`.

**Hint:** `.info` is a large dict. Access with `.get('trailingPE', 'N/A')` to avoid KeyErrors. `marketCap` is a raw integer — format it as `"$2.94T"` for readability. `returnOnEquity` from yfinance is a decimal (e.g., `1.47` = 147%) — multiply by 100 for display.

---

## Step 5 — Fetch News and Score Sentiment with Claude

**Requirement:** Write two functions:
- `fetch_news(ticker: str, api_key: str) -> list[dict]` — calls NewsAPI `GET /v2/everything` with `q=ticker`, `pageSize=10`, `sortBy=publishedAt`. Returns list of dicts with `title` and `description`.
- `score_news_sentiment(articles: list[dict], ticker: str, client) -> list[dict]` — sends all 10 headlines to Claude in one API call. Claude returns a JSON list where each item has `headline`, `sentiment` (`bullish`/`bearish`/`neutral`), and `reasoning`.

**Hint for NewsAPI URL:** `https://newsapi.org/v2/everything?q={ticker}&pageSize=10&sortBy=publishedAt&apiKey={key}`

**Hint for Claude JSON output:** Instruct Claude to respond with a raw JSON array, no markdown fences. Use `json.loads(response.content[0].text)` to parse. Add `try/except` in case Claude wraps it in markdown anyway — strip backticks and `json` prefix before parsing.

---

## Step 6 — Fetch Earnings Trend

**Requirement:** Write `fetch_earnings(ticker: str) -> list[dict]` that returns the last 4 quarters of revenue and net income. Each item in the list should have `quarter`, `revenue`, and `net_income`.

**Hint:** `yfinance.Ticker(ticker).quarterly_financials` returns a DataFrame where columns are `Timestamp` quarter-end dates and rows are labeled financial metrics. The row labels vary by company but commonly include `'Total Revenue'` and `'Net Income'`. Transpose with `.T` to make quarters the row index. Handle `KeyError` gracefully if either metric is missing.

---

## Step 7 — Fetch Competitor Comparison

**Requirement:** Write `fetch_peers(peer_tickers: list[str]) -> list[dict]` that fetches `.info` for each peer and returns a list of dicts with `ticker`, `name`, `pe_ratio`, and `revenue_growth`. Revenue growth is `revenueGrowth` from `.info` (a decimal like `0.148`). Wrap each peer fetch in a `try/except` and skip failed lookups silently.

---

## Step 8 — Assemble the Briefing and Call Claude

**Requirement:** Write `build_briefing(ticker, indicators, fundamentals, news_scored, earnings, peers) -> str` that formats all data into a structured multi-section text block. Then write `generate_report(briefing: str, ticker: str, client) -> str` that sends the briefing to Claude with the analyst system prompt and returns the full report text.

**Hint for token budget:** A full briefing for one stock runs roughly 1,200-2,000 tokens. The report response will be 1,500-3,000 tokens. Use `claude-sonnet-4-6` with `max_tokens=4000`. If you want a tighter, faster run, use `max_tokens=2000` and shorten the report instructions.

---

## Step 9 — Save the Report

**Requirement:** Write `save_report(report_text: str, ticker: str, output_dir: str = "output") -> str` that creates the output directory if it does not exist, writes `{TICKER}_analysis.md`, and returns the file path.

Then implement optional PDF generation: `save_pdf(report_text: str, ticker: str, output_dir: str) -> str`. Use `reportlab`'s `SimpleDocTemplate` and `Paragraph` with `getSampleStyleSheet()`. Strip markdown headers (`#`, `##`, `**`) for clean PDF rendering. Return the PDF path.

**Hint for PDF:** `SimpleDocTemplate` takes a filename. Build a list of `Paragraph` objects from each line of the report. Use `styles['Normal']` for body text and `styles['Heading2']` for lines that were `##` headers. Call `doc.build(story)` to render.

---

## Wiring It All Together

Write a `main()` function and a CLI entry point:

```python
if __name__ == "__main__":
    import sys
    ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    peer_tickers = sys.argv[2:] if len(sys.argv) > 2 else ["MSFT", "GOOGL", "META"]
    main(ticker, peer_tickers)
```

`main()` calls each function in order, prints progress for each step, and calls `save_report()`. PDF generation should be triggered by a `--pdf` flag or a `GENERATE_PDF=true` env var.

---

## Testing Checklist

- [ ] `AAPL` — baseline US ticker, all data should be available
- [ ] `RELIANCE.NS` — Indian ticker, verify yfinance returns data
- [ ] `NVDA` — high-growth stock, verify earnings trend shows acceleration
- [ ] Invalid ticker `ZZZZZ` — should raise `ValueError` at step 2
- [ ] Run with `NEWS_API_KEY` missing — should skip news and note it in the report

---

## 📂 Navigation

**In this folder:**

| File | |
|---|---|
| [📄 01_MISSION.md](./01_MISSION.md) | Mission briefing |
| [📄 02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design |
| 📄 **03_GUIDE.md** | ← you are here |
| [📄 src/starter.py](./src/starter.py) | Starter scaffold |
| [📄 src/solution.py](./src/solution.py) | Complete solution |
| [📄 04_RECAP.md](./04_RECAP.md) | What you built |

⬅️ **Prev:** [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [src/starter.py](./src/starter.py)
