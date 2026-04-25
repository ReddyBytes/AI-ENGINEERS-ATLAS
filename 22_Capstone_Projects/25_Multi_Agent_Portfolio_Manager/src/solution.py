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
    holdings: dict                                        # {ticker: weight}
    period: str                                           # yfinance period string
    price_data: str                                       # JSON-serialized price DataFrame
    market_analysis: Annotated[dict, operator.or_]       # populated by market_analyst
    fundamental_analysis: Annotated[dict, operator.or_]  # populated by fundamental_researcher
    risk_metrics: dict                                    # populated by risk_manager
    recommendation: str                                   # populated by portfolio_advisor
    report_path: str                                      # populated by save_report


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def call_claude(system: str, user: str, max_tokens: int = 2048) -> str:
    """Call Claude and return the text response."""
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return response.content[0].text.strip()


def compute_rsi(series: pd.Series, period: int = 14) -> float:
    """
    Compute RSI for the most recent data point.
    RSI = 100 - (100 / (1 + avg_gain / avg_loss)) over `period` trading days.
    """
    delta = series.diff().dropna()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(period).mean().iloc[-1]
    avg_loss = loss.rolling(period).mean().iloc[-1]
    if pd.isna(avg_gain) or pd.isna(avg_loss):
        return float("nan")
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)


def compute_macd(series: pd.Series) -> dict:
    """
    Compute MACD line (EMA-12 minus EMA-26), signal line (EMA-9 of MACD),
    and crossover direction.
    """
    ema12 = series.ewm(span=12, adjust=False).mean()
    ema26 = series.ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    latest_macd = round(float(macd_line.iloc[-1]), 4)
    latest_signal = round(float(signal_line.iloc[-1]), 4)
    crossover = "bullish" if latest_macd > latest_signal else "bearish"
    return {"macd": latest_macd, "signal": latest_signal, "crossover": crossover}


# ---------------------------------------------------------------------------
# Node 1: fetch_data
# ---------------------------------------------------------------------------

def fetch_data(state: PortfolioState):
    """
    Download price history for all holdings.
    Returns a list of Send objects to launch market_analyst and
    fundamental_researcher in parallel.
    """
    print("[fetch_data] downloading price history...")
    tickers = list(state["holdings"].keys())
    period = state.get("period", "1y")

    raw = yf.download(tickers, period=period, auto_adjust=True, progress=False)

    # Handle MultiIndex columns returned for multiple tickers
    if isinstance(raw.columns, pd.MultiIndex):
        price_df = raw["Close"]
    else:
        # Single ticker returns flat columns
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

    print(f"[fetch_data] {len(price_df)} trading days for {tickers}")

    # Parallel dispatch to both analyst nodes
    return [
        Send("market_analyst", updated_state),
        Send("fundamental_researcher", updated_state),
    ]


# ---------------------------------------------------------------------------
# Node 2a: market_analyst
# ---------------------------------------------------------------------------

def market_analyst(state: PortfolioState) -> dict:
    """
    Compute technical indicators per ticker and ask Claude for a
    brief market outlook for each position.
    """
    t_start = time.time()
    print(f"[market_analyst] starting... ({datetime.now().strftime('%H:%M:%S.%f')[:12]})")

    price_df = pd.read_json(state["price_data"])
    # First column is the date index after reset_index
    price_df = price_df.set_index(price_df.columns[0])
    # Ensure datetime index
    price_df.index = pd.to_datetime(price_df.index)

    analysis = {}
    for ticker in state["holdings"]:
        if ticker not in price_df.columns:
            analysis[ticker] = {"error": "no price data"}
            continue

        series = price_df[ticker].dropna()
        if len(series) < 30:
            analysis[ticker] = {"error": "insufficient history (<30 days)"}
            continue

        rsi = compute_rsi(series)
        macd_data = compute_macd(series)

        ma50 = round(float(series.rolling(50).mean().iloc[-1]), 2) if len(series) >= 50 else None
        ma200 = round(float(series.rolling(200).mean().iloc[-1]), 2) if len(series) >= 200 else None
        current_price = round(float(series.iloc[-1]), 2)

        if ma50 is not None and ma200 is not None:
            trend = "bullish" if ma50 > ma200 else "bearish"
            ma_cross = "golden cross (MA50 > MA200)" if ma50 > ma200 else "death cross (MA50 < MA200)"
        else:
            trend = "trend undetermined"
            ma_cross = "insufficient history for MA200"

        analysis[ticker] = {
            "current_price": current_price,
            "rsi_14": rsi,
            "macd": macd_data,
            "ma_50": ma50,
            "ma_200": ma200,
            "trend": trend,
            "ma_cross": ma_cross,
        }

    # Claude interprets the indicators
    indicators_text = json.dumps(analysis, indent=2)
    claude_response = call_claude(
        system=(
            "You are a technical analyst. Be concise and data-driven. "
            "No emojis. Cite specific numbers."
        ),
        user=(
            "Write a 2-3 sentence technical market outlook for each ticker below.\n"
            "Reference: RSI (overbought >70, oversold <30), MACD crossover direction, "
            "and moving average trend.\n\n"
            f"Indicators:\n{indicators_text}\n\n"
            'Format your response as JSON: {"TICKER": "2-3 sentence outlook", ...}\n'
            "Respond with only the JSON object, no other text."
        ),
        max_tokens=1024,
    )

    try:
        summaries = json.loads(claude_response)
    except json.JSONDecodeError:
        summaries = {t: "Technical summary unavailable." for t in analysis}

    for ticker in analysis:
        analysis[ticker]["summary"] = summaries.get(ticker, "")

    elapsed = round(time.time() - t_start, 2)
    print(f"[market_analyst] complete in {elapsed}s")
    return {"market_analysis": analysis}


# ---------------------------------------------------------------------------
# Node 2b: fundamental_researcher
# ---------------------------------------------------------------------------

def fundamental_researcher(state: PortfolioState) -> dict:
    """
    Fetch fundamental data from yfinance for each holding and ask Claude
    for a brief assessment of valuation and quality.
    """
    t_start = time.time()
    print(f"[fundamental_researcher] starting... ({datetime.now().strftime('%H:%M:%S.%f')[:12]})")

    analysis = {}
    for ticker in state["holdings"]:
        try:
            info = yf.Ticker(ticker).info
            current_price = info.get("currentPrice") or info.get("regularMarketPrice")
            target_price = info.get("targetMeanPrice")

            upside_pct = None
            if current_price and target_price and current_price > 0:
                upside_pct = round((target_price - current_price) / current_price * 100, 1)

            analysis[ticker] = {
                "current_price": current_price,
                "trailing_pe": info.get("trailingPE"),
                "forward_pe": info.get("forwardPE"),
                "trailing_eps": info.get("trailingEps"),
                "revenue_growth": info.get("revenueGrowth"),
                "analyst_rating": info.get("recommendationKey", "n/a"),
                "target_price": target_price,
                "upside_pct": upside_pct,
                "sector": info.get("sector", "n/a"),
                "company_name": info.get("longName", ticker),
            }
        except Exception as exc:
            analysis[ticker] = {"error": str(exc)}

    fundamentals_text = json.dumps(analysis, indent=2)
    claude_response = call_claude(
        system=(
            "You are a fundamental equity analyst. Be precise and quantitative. "
            "No emojis. Reference specific numbers."
        ),
        user=(
            "Write a 2-3 sentence fundamental assessment for each ticker below.\n"
            "Cover: valuation (P/E vs growth), analyst consensus, "
            "and upside/downside to mean price target.\n"
            "Flag any concerning metrics explicitly.\n\n"
            f"Data:\n{fundamentals_text}\n\n"
            'Format as JSON: {"TICKER": "2-3 sentence assessment", ...}\n'
            "Respond with only the JSON object."
        ),
        max_tokens=1024,
    )

    try:
        summaries = json.loads(claude_response)
    except json.JSONDecodeError:
        summaries = {t: "Fundamental summary unavailable." for t in analysis}

    for ticker in analysis:
        analysis[ticker]["summary"] = summaries.get(ticker, "")

    elapsed = round(time.time() - t_start, 2)
    print(f"[fundamental_researcher] complete in {elapsed}s")
    return {"fundamental_analysis": analysis}


# ---------------------------------------------------------------------------
# Node 3: risk_manager
# ---------------------------------------------------------------------------

def risk_manager(state: PortfolioState) -> dict:
    """
    Compute portfolio-level risk metrics from the price history:
    annualized return, volatility, Sharpe ratio, max drawdown, VaR, correlation.
    """
    print("[risk_manager] computing portfolio risk metrics...")

    price_df = pd.read_json(state["price_data"])
    price_df = price_df.set_index(price_df.columns[0])
    price_df.index = pd.to_datetime(price_df.index)

    holdings = state["holdings"]
    tickers = [t for t in holdings if t in price_df.columns]

    if not tickers:
        print("[risk_manager] no valid tickers in price data")
        return {"risk_metrics": {"error": "no valid tickers found in price data"}}

    prices = price_df[tickers].dropna()
    daily_returns = prices.pct_change().dropna()

    # Normalized weights
    weights = np.array([holdings[t] for t in tickers], dtype=float)
    weights = weights / weights.sum()

    # Portfolio daily return series
    port_returns = daily_returns.values @ weights

    ann_return = port_returns.mean() * 252
    ann_vol = port_returns.std() * np.sqrt(252)
    sharpe = round((ann_return - RISK_FREE_RATE) / ann_vol, 3) if ann_vol > 0 else None

    # Max drawdown
    cumulative = pd.Series((1 + port_returns).cumprod())
    rolling_peak = cumulative.cummax()
    drawdown = (cumulative - rolling_peak) / rolling_peak
    max_drawdown = round(float(drawdown.min()) * 100, 2)

    # VaR at 95% confidence (5th percentile of daily returns)
    var_95 = round(float(np.percentile(port_returns, 5)) * 100, 3)

    # Correlation matrix
    corr = daily_returns[tickers].corr().round(3).to_dict()

    risk_metrics = {
        "tickers_analyzed": tickers,
        "weights_used": {t: round(float(w), 4) for t, w in zip(tickers, weights)},
        "period_trading_days": int(len(prices)),
        "annualized_return_pct": round(float(ann_return) * 100, 2),
        "annualized_volatility_pct": round(float(ann_vol) * 100, 2),
        "sharpe_ratio": float(sharpe) if sharpe is not None else None,
        "max_drawdown_pct": max_drawdown,
        "var_95_daily_pct": var_95,
        "correlation_matrix": corr,
    }

    print(
        f"[risk_manager] sharpe={sharpe}, "
        f"max_drawdown={max_drawdown}%, "
        f"var_95={var_95}%"
    )
    return {"risk_metrics": risk_metrics}


# ---------------------------------------------------------------------------
# Node 4: portfolio_advisor
# ---------------------------------------------------------------------------

def portfolio_advisor(state: PortfolioState) -> dict:
    """
    Synthesize all specialist agent findings into a complete investment
    analysis report with concrete rebalancing recommendations.
    """
    print("[portfolio_advisor] synthesizing recommendations...")

    holdings_text = json.dumps(state["holdings"], indent=2)
    market_text = json.dumps(state.get("market_analysis", {}), indent=2)
    fundamental_text = json.dumps(state.get("fundamental_analysis", {}), indent=2)
    risk_text = json.dumps(state.get("risk_metrics", {}), indent=2)

    prompt = f"""You are a senior portfolio manager writing a formal investment committee report.
Use the specialist research below to write a complete portfolio analysis.

CURRENT HOLDINGS (ticker: allocation weight):
{holdings_text}

MARKET ANALYSIS (technical indicators and outlook per ticker):
{market_text}

FUNDAMENTAL ANALYSIS (valuation, quality, and analyst consensus per ticker):
{fundamental_text}

PORTFOLIO RISK METRICS:
{risk_text}

---

Write the report with EXACTLY these five section headings (use ## for each):

## Current Portfolio State
Describe the portfolio composition, total value context, and overall market environment.
Include the annualized return and Sharpe ratio in this section.

## Market Analysis
For each ticker: cite the specific RSI value, MACD crossover status, and MA trend.
Indicate which positions look technically extended and which look oversold.

## Fundamental Analysis
For each ticker: cite the P/E ratio, analyst rating, and percentage upside to mean price target.
Identify the highest-conviction and lowest-conviction positions based on fundamentals.

## Risk Assessment
Interpret the Sharpe ratio (good: >1.0, acceptable: 0.5-1.0, poor: <0.5).
Comment on max drawdown severity, VaR implications for daily loss expectation,
and any high-correlation pairs that represent concentration risk.

## Recommended Actions
For each ticker provide exactly this format:
**TICKER** — [BUY / ADD / HOLD / TRIM / SELL] — Target allocation: X%
Rationale: [Two sentences citing specific data from the market and fundamental analysis above.]

End with a 2-3 sentence overall rebalancing thesis paragraph."""

    report_body = call_claude(
        system=(
            "You are a senior portfolio manager writing a professional investment analysis report "
            "for an investment committee. Be precise. Cite specific numbers. "
            "Make concrete, actionable recommendations. No emojis. No filler language."
        ),
        user=prompt,
        max_tokens=3500,
    )

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_report = f"# Portfolio Analysis Report\n\nGenerated: {timestamp}\n\n{report_body}"

    print("[portfolio_advisor] complete")
    return {"recommendation": full_report}


# ---------------------------------------------------------------------------
# Node 5: save_report
# ---------------------------------------------------------------------------

def save_report(state: PortfolioState) -> dict:
    """Write the full report to portfolio_report.md."""
    path = "portfolio_report.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(state["recommendation"])

    line_count = len(state["recommendation"].splitlines())
    print(f"\n[save_report] Report saved to: {path} ({line_count} lines)")
    return {"report_path": path}


# ---------------------------------------------------------------------------
# Graph Construction
# ---------------------------------------------------------------------------

def build_graph():
    """
    Build the LangGraph StateGraph.

    Topology:
      fetch_data
        ├── market_analyst       (via Send — parallel)
        └── fundamental_researcher (via Send — parallel)
             both → risk_manager → portfolio_advisor → save_report → END
    """
    graph = StateGraph(PortfolioState)

    graph.add_node("fetch_data", fetch_data)
    graph.add_node("market_analyst", market_analyst)
    graph.add_node("fundamental_researcher", fundamental_researcher)
    graph.add_node("risk_manager", risk_manager)
    graph.add_node("portfolio_advisor", portfolio_advisor)
    graph.add_node("save_report", save_report)

    graph.set_entry_point("fetch_data")

    # fetch_data returns Send objects; conditional edges route to both parallel nodes
    graph.add_conditional_edges(
        "fetch_data",
        lambda state: ["market_analyst", "fundamental_researcher"],
        ["market_analyst", "fundamental_researcher"],
    )

    # Both parallel nodes converge into risk_manager
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
            try:
                weight = float(parts[1].strip())
                result[ticker] = weight
            except ValueError:
                print(f"Warning: could not parse weight for {ticker}, skipping")
    if not result:
        raise ValueError("No valid holdings parsed. Format: AAPL:0.25,MSFT:0.25")
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
        choices=["1mo", "3mo", "6mo", "1y", "2y"],
        help="Historical period to analyze",
    )
    args = parser.parse_args()

    holdings = parse_holdings(args.holdings)
    print(f"\nPortfolio Manager — Multi-Agent System")
    print(f"Holdings: {holdings}")
    print(f"Period:   {args.period}\n")

    initial_state: PortfolioState = {
        "holdings": holdings,
        "period": args.period,
        "price_data": "",
        "market_analysis": {},
        "fundamental_analysis": {},
        "risk_metrics": {},
        "recommendation": "",
        "report_path": "",
    }

    app = build_graph()
    t0 = time.time()
    final_state = app.invoke(initial_state)
    elapsed = round(time.time() - t0, 1)

    print(f"\nTotal time: {elapsed}s")
    print(f"Report:     {final_state.get('report_path', 'not saved')}")

    # Print the first 600 characters of the report as a preview
    report_preview = final_state.get("recommendation", "")[:600]
    if report_preview:
        print("\n--- Report Preview ---")
        print(report_preview)
        print("...")
