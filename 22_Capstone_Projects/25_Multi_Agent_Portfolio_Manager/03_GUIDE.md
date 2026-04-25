# Project 25 — Build Guide

**Format:** Build Yourself — you receive the full specification and acceptance criteria. Implement it from scratch. The reference solution is at the bottom of this file inside a `<details>` block.

---

## Specification

Build a LangGraph multi-agent system that produces a portfolio analysis report.

### Entry Point

```python
python solution.py --holdings AAPL:0.25,MSFT:0.20,NVDA:0.20,GOOGL:0.15,AMZN:0.20 --period 1y
```

Holdings are provided as `TICKER:weight` pairs. Weights should sum to approximately 1.0 (the system may normalize them).

### Required Output

A file named `portfolio_report.md` in the current directory containing these five sections in order:

```
# Portfolio Analysis Report
Generated: [timestamp]

## Current Portfolio State
## Market Analysis
## Fundamental Analysis
## Risk Assessment
## Recommended Actions
```

Each section must be substantive — not placeholder text.

---

## Acceptance Criteria

All four must pass before you consider the project complete:

**AC-1 — All four agents fire.**
Add a print statement at the start of each agent node: `"[market_analyst] starting..."`, etc. Run the program and verify all four appear in stdout.

**AC-2 — Parallel execution is verified.**
Add a `time.time()` timestamp at the start of market_analyst and fundamental_researcher. The timestamps should be within 1 second of each other (they run in parallel, not sequentially).

**AC-3 — Report contains all four analysis sections.**
After the run, open `portfolio_report.md` and verify all five section headings are present. Each section must contain at least 50 words.

**AC-4 — Recommendations include allocations and rationale.**
The "Recommended Actions" section must include a specific percentage allocation for each ticker and at least one sentence of rationale per ticker citing data from the analysis (e.g., "RSI at 72 indicates overbought" or "P/E of 28 is below sector median").

---

## Architecture Constraints

These are not suggestions — they are required patterns:

1. Use `langgraph.graph.StateGraph` with a `TypedDict` state
2. Use `langgraph.types.Send` for parallel dispatch of market_analyst and fundamental_researcher
3. State must have at least: `holdings`, `period`, `market_analysis`, `fundamental_analysis`, `risk_metrics`, `recommendation`
4. Risk metrics must be computed with numpy/pandas — not estimated by Claude
5. The final synthesis call must pass all three agent outputs to Claude in a single prompt

---

## Guidance Notes (minimal)

- yfinance: `yf.download(tickers, period=period)["Close"]` returns a DataFrame with tickers as columns
- RSI formula: `100 - (100 / (1 + avg_gain / avg_loss))` over 14 periods
- MACD: EMA-12 minus EMA-26; signal line is EMA-9 of MACD
- Sharpe: `(mean_daily_return * 252 - 0.04) / (std_daily_return * sqrt(252))`
- Max drawdown: `(cummax - cumulative_returns).max() / cummax.max()`
- VaR 95%: `np.percentile(daily_returns, 5)`
- Handle missing yfinance data with `.fillna(method="ffill").dropna()`
- LangGraph's Send API: a node can return `[Send("node_name", state_dict), ...]` to dispatch multiple parallel nodes

---

## Acceptance Test Procedure

```bash
# 1. Run the system
python solution.py --holdings AAPL:0.25,MSFT:0.20,NVDA:0.30,GOOGL:0.25 --period 1y

# 2. Verify all agents fired (check stdout)

# 3. Check report exists and has content
wc -l portfolio_report.md          # should be > 50 lines
grep "## " portfolio_report.md     # should show all 5 headings

# 4. Spot check a recommendation
grep -A 3 "AAPL" portfolio_report.md
```

---

<details>
<summary>Reference Solution — click to expand after attempting the project yourself</summary>

```python
"""
Project 25 — Multi-Agent Portfolio Manager
Complete reference solution.

Run:
  python solution.py --holdings AAPL:0.25,MSFT:0.20,NVDA:0.30,GOOGL:0.25 --period 1y

Setup:
  pip install anthropic langgraph langchain-anthropic yfinance pandas numpy python-dotenv
  echo "ANTHROPIC_API_KEY=your-key" > .env
"""

import os
import time
import json
import argparse
import operator
from datetime import datetime
from typing import Annotated

import numpy as np
import pandas as pd
import yfinance as yf
import anthropic
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langgraph.types import Send
from typing_extensions import TypedDict

load_dotenv()

CLAUDE_MODEL = "claude-sonnet-4-6"
RISK_FREE_RATE = 0.04


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

class PortfolioState(TypedDict):
    holdings: dict          # {ticker: weight}
    period: str             # yfinance period string
    price_data: dict        # serialized DataFrame (JSON)
    market_analysis: Annotated[dict, operator.or_]
    fundamental_analysis: Annotated[dict, operator.or_]
    risk_metrics: dict
    recommendation: str
    report_path: str


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def call_claude(system: str, user: str, max_tokens: int = 2048) -> str:
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return response.content[0].text.strip()


def compute_rsi(series: pd.Series, period: int = 14) -> float:
    delta = series.diff().dropna()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(period).mean().iloc[-1]
    avg_loss = loss.rolling(period).mean().iloc[-1]
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)


def compute_macd(series: pd.Series) -> dict:
    ema12 = series.ewm(span=12, adjust=False).mean()
    ema26 = series.ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    latest_macd = round(macd_line.iloc[-1], 4)
    latest_signal = round(signal_line.iloc[-1], 4)
    crossover = "bullish" if latest_macd > latest_signal else "bearish"
    return {"macd": latest_macd, "signal": latest_signal, "crossover": crossover}


# ---------------------------------------------------------------------------
# Node 1: fetch_data — downloads price history, dispatches parallel agents
# ---------------------------------------------------------------------------

def fetch_data(state: PortfolioState):
    print("[fetch_data] downloading price history...")
    tickers = list(state["holdings"].keys())
    period = state.get("period", "1y")

    raw = yf.download(tickers, period=period, auto_adjust=True, progress=False)

    # yfinance returns MultiIndex for multiple tickers
    if isinstance(raw.columns, pd.MultiIndex):
        price_df = raw["Close"]
    else:
        price_df = raw[["Close"]]
        price_df.columns = tickers

    price_df = price_df.ffill().dropna()
    price_json = price_df.reset_index().to_json(date_format="iso")

    updated_state = {
        **state,
        "price_data": price_json,
        "market_analysis": {},
        "fundamental_analysis": {},
        "risk_metrics": {},
        "recommendation": "",
        "report_path": "",
    }

    print(f"[fetch_data] got {len(price_df)} trading days for {tickers}")

    # Parallel dispatch
    return [
        Send("market_analyst", updated_state),
        Send("fundamental_researcher", updated_state),
    ]


# ---------------------------------------------------------------------------
# Node 2a: market_analyst — technical indicators
# ---------------------------------------------------------------------------

def market_analyst(state: PortfolioState) -> dict:
    t_start = time.time()
    print(f"[market_analyst] starting... ({datetime.now().strftime('%H:%M:%S.%f')[:12]})")

    price_df = pd.read_json(state["price_data"])
    price_df = price_df.set_index(price_df.columns[0])

    analysis = {}
    for ticker in state["holdings"]:
        if ticker not in price_df.columns:
            analysis[ticker] = {"error": "no price data"}
            continue

        series = price_df[ticker].dropna()
        if len(series) < 30:
            analysis[ticker] = {"error": "insufficient data"}
            continue

        rsi = compute_rsi(series)
        macd_data = compute_macd(series)
        ma50 = round(series.rolling(50).mean().iloc[-1], 2) if len(series) >= 50 else None
        ma200 = round(series.rolling(200).mean().iloc[-1], 2) if len(series) >= 200 else None
        current_price = round(series.iloc[-1], 2)

        # Trend classification
        if ma50 and ma200:
            trend = "bullish" if ma50 > ma200 else "bearish"
            cross = "golden cross" if ma50 > ma200 else "death cross"
        else:
            trend = "insufficient data for MA cross"
            cross = "n/a"

        analysis[ticker] = {
            "current_price": current_price,
            "rsi_14": rsi,
            "macd": macd_data,
            "ma_50": ma50,
            "ma_200": ma200,
            "trend": trend,
            "ma_cross": cross,
        }

    # Ask Claude for interpretation
    indicators_text = json.dumps(analysis, indent=2)
    summary = call_claude(
        system="You are a technical analyst. Be concise and data-driven. No emojis.",
        user=f"""Given these technical indicators for a portfolio, write a 2-3 sentence 
market outlook for each ticker. Focus on RSI (overbought >70, oversold <30), 
MACD crossover signal, and moving average trend.

Indicators:
{indicators_text}

Format as JSON: {{"TICKER": "2-3 sentence summary", ...}}
Respond with only the JSON object.""",
        max_tokens=1024,
    )

    try:
        summaries = json.loads(summary)
    except json.JSONDecodeError:
        summaries = {t: "Summary unavailable." for t in analysis}

    for ticker in analysis:
        analysis[ticker]["summary"] = summaries.get(ticker, "")

    elapsed = round(time.time() - t_start, 2)
    print(f"[market_analyst] complete in {elapsed}s")
    return {"market_analysis": analysis}


# ---------------------------------------------------------------------------
# Node 2b: fundamental_researcher — valuation and quality
# ---------------------------------------------------------------------------

def fundamental_researcher(state: PortfolioState) -> dict:
    t_start = time.time()
    print(f"[fundamental_researcher] starting... ({datetime.now().strftime('%H:%M:%S.%f')[:12]})")

    analysis = {}
    for ticker in state["holdings"]:
        try:
            info = yf.Ticker(ticker).info
            current_price = info.get("currentPrice") or info.get("regularMarketPrice")
            target_price = info.get("targetMeanPrice")

            upside = None
            if current_price and target_price and current_price > 0:
                upside = round((target_price - current_price) / current_price * 100, 1)

            analysis[ticker] = {
                "trailing_pe": info.get("trailingPE"),
                "forward_pe": info.get("forwardPE"),
                "trailing_eps": info.get("trailingEps"),
                "revenue_growth": info.get("revenueGrowth"),
                "analyst_rating": info.get("recommendationKey", "n/a"),
                "target_price": target_price,
                "current_price": current_price,
                "upside_pct": upside,
                "sector": info.get("sector", "n/a"),
            }
        except Exception as e:
            analysis[ticker] = {"error": str(e)}

    # Ask Claude for fundamentals narrative
    fundamentals_text = json.dumps(analysis, indent=2)
    summary = call_claude(
        system="You are a fundamental equity analyst. Be precise and quantitative. No emojis.",
        user=f"""Write a 2-3 sentence fundamental assessment for each ticker below.
Cover: valuation (P/E vs growth), analyst consensus, and upside/downside to price target.
Flag any concerning metrics.

Data:
{fundamentals_text}

Format as JSON: {{"TICKER": "2-3 sentence assessment", ...}}
Respond with only the JSON object.""",
        max_tokens=1024,
    )

    try:
        summaries = json.loads(summary)
    except json.JSONDecodeError:
        summaries = {t: "Assessment unavailable." for t in analysis}

    for ticker in analysis:
        analysis[ticker]["summary"] = summaries.get(ticker, "")

    elapsed = round(time.time() - t_start, 2)
    print(f"[fundamental_researcher] complete in {elapsed}s")
    return {"fundamental_analysis": analysis}


# ---------------------------------------------------------------------------
# Node 3: risk_manager — portfolio-level metrics
# ---------------------------------------------------------------------------

def risk_manager(state: PortfolioState) -> dict:
    print("[risk_manager] computing portfolio risk metrics...")

    price_df = pd.read_json(state["price_data"])
    price_df = price_df.set_index(price_df.columns[0])

    holdings = state["holdings"]
    tickers = [t for t in holdings if t in price_df.columns]

    if not tickers:
        return {"risk_metrics": {"error": "no valid tickers"}}

    prices = price_df[tickers].dropna()
    daily_returns = prices.pct_change().dropna()
    weights = np.array([holdings[t] for t in tickers])
    weights = weights / weights.sum()  # normalize

    # Portfolio daily returns
    port_returns = daily_returns.values @ weights
    ann_return = port_returns.mean() * 252
    ann_vol = port_returns.std() * np.sqrt(252)
    sharpe = round((ann_return - RISK_FREE_RATE) / ann_vol, 3) if ann_vol > 0 else None

    # Max drawdown
    cumulative = (1 + port_returns).cumprod()
    rolling_max = cumulative.cummax()
    drawdown = (cumulative - rolling_max) / rolling_max
    max_drawdown = round(drawdown.min() * 100, 2)

    # VaR 95%
    var_95 = round(np.percentile(port_returns, 5) * 100, 3)

    # Correlation matrix
    corr = daily_returns[tickers].corr().round(3).to_dict()

    risk_metrics = {
        "annualized_return_pct": round(ann_return * 100, 2),
        "annualized_volatility_pct": round(ann_vol * 100, 2),
        "sharpe_ratio": sharpe,
        "max_drawdown_pct": max_drawdown,
        "var_95_daily_pct": var_95,
        "correlation_matrix": corr,
        "period_days": len(prices),
    }

    print(f"[risk_manager] sharpe={sharpe}, max_drawdown={max_drawdown}%, var_95={var_95}%")
    return {"risk_metrics": risk_metrics}


# ---------------------------------------------------------------------------
# Node 4: portfolio_advisor — synthesis and recommendations
# ---------------------------------------------------------------------------

def portfolio_advisor(state: PortfolioState) -> dict:
    print("[portfolio_advisor] synthesizing recommendations...")

    holdings_text = json.dumps(state["holdings"], indent=2)
    market_text = json.dumps(state["market_analysis"], indent=2)
    fundamental_text = json.dumps(state["fundamental_analysis"], indent=2)
    risk_text = json.dumps(state["risk_metrics"], indent=2)

    prompt = f"""You are a senior portfolio manager. Using the analyst reports below, write a complete 
portfolio analysis report in markdown format.

CURRENT HOLDINGS (ticker: weight):
{holdings_text}

MARKET ANALYSIS (technical indicators + outlook per ticker):
{market_text}

FUNDAMENTAL ANALYSIS (valuation + quality per ticker):
{fundamental_text}

RISK METRICS (portfolio-level):
{risk_text}

Write the report with these exact section headings:

## Current Portfolio State
Summarize the current portfolio composition and overall performance context.

## Market Analysis
Technical outlook for each position. Reference specific indicator values (RSI, MACD, moving averages).

## Fundamental Analysis
Valuation and quality assessment for each position. Reference P/E, growth, analyst ratings, price targets.

## Risk Assessment
Interpret the portfolio risk metrics. Comment on Sharpe ratio quality, drawdown severity, VaR implications, and any high-correlation pairs that create concentration risk.

## Recommended Actions
For each ticker: BUY / HOLD / TRIM / SELL with a specific target allocation percentage.
Format each recommendation as:
**TICKER** — [ACTION] — Target: X%
Rationale: [2 sentences citing specific data from the analysis above]

End with a summary paragraph of the overall rebalancing thesis."""

    report_body = call_claude(
        system="You are a senior portfolio manager writing a professional investment analysis report. Be precise, cite specific numbers, and make actionable recommendations. No emojis. No fluff.",
        user=prompt,
        max_tokens=3000,
    )

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_report = f"# Portfolio Analysis Report\n\nGenerated: {timestamp}\n\n{report_body}"

    print("[portfolio_advisor] complete")
    return {"recommendation": full_report}


# ---------------------------------------------------------------------------
# Node 5: save_report
# ---------------------------------------------------------------------------

def save_report(state: PortfolioState) -> dict:
    path = "portfolio_report.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(state["recommendation"])
    print(f"\n[save_report] Report saved to: {path}")
    print(f"[save_report] Lines: {len(state['recommendation'].splitlines())}")
    return {"report_path": path}


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------

def build_graph() -> StateGraph:
    graph = StateGraph(PortfolioState)

    graph.add_node("fetch_data", fetch_data)
    graph.add_node("market_analyst", market_analyst)
    graph.add_node("fundamental_researcher", fundamental_researcher)
    graph.add_node("risk_manager", risk_manager)
    graph.add_node("portfolio_advisor", portfolio_advisor)
    graph.add_node("save_report", save_report)

    graph.set_entry_point("fetch_data")

    # fetch_data returns Send objects for parallel dispatch
    graph.add_conditional_edges(
        "fetch_data",
        lambda state: state,  # pass-through; actual routing via Send in node return
        ["market_analyst", "fundamental_researcher"],
    )

    # Both parallel nodes converge to risk_manager
    graph.add_edge("market_analyst", "risk_manager")
    graph.add_edge("fundamental_researcher", "risk_manager")

    graph.add_edge("risk_manager", "portfolio_advisor")
    graph.add_edge("portfolio_advisor", "save_report")
    graph.add_edge("save_report", END)

    return graph.compile()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def parse_holdings(holdings_str: str) -> dict:
    """Parse 'AAPL:0.25,MSFT:0.20' into {'AAPL': 0.25, 'MSFT': 0.20}."""
    result = {}
    for pair in holdings_str.split(","):
        parts = pair.strip().split(":")
        if len(parts) == 2:
            ticker = parts[0].strip().upper()
            weight = float(parts[1].strip())
            result[ticker] = weight
    # Normalize weights
    total = sum(result.values())
    return {k: round(v / total, 4) for k, v in result.items()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-Agent Portfolio Manager")
    parser.add_argument(
        "--holdings",
        default="AAPL:0.25,MSFT:0.25,NVDA:0.25,GOOGL:0.25",
        help="Holdings as TICKER:weight pairs, comma-separated",
    )
    parser.add_argument(
        "--period",
        default="1y",
        help="yfinance period (1mo, 3mo, 6mo, 1y, 2y)",
    )
    args = parser.parse_args()

    holdings = parse_holdings(args.holdings)
    print(f"\nPortfolio: {holdings}")
    print(f"Period: {args.period}\n")

    initial_state = PortfolioState(
        holdings=holdings,
        period=args.period,
        price_data={},
        market_analysis={},
        fundamental_analysis={},
        risk_metrics={},
        recommendation="",
        report_path="",
    )

    app = build_graph()
    t0 = time.time()
    final_state = app.invoke(initial_state)
    elapsed = round(time.time() - t0, 1)

    print(f"\nDone in {elapsed}s")
    print(f"Report: {final_state['report_path']}")
    print("\nFirst 500 chars of report:")
    print(final_state["recommendation"][:500])
```

</details>

---

## 📂 Navigation

| File | |
|------|---|
| [01_MISSION.md](./01_MISSION.md) | Project brief |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | LangGraph state diagram |
| **03_GUIDE.md** | You are here |
| [src/starter.py](./src/starter.py) | Starter scaffold |
| [src/solution.py](./src/solution.py) | Complete reference solution |
| [04_RECAP.md](./04_RECAP.md) | What you learned |
