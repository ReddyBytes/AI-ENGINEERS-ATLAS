"""
Project 25 — Multi-Agent Portfolio Manager
Starter scaffold — implement every TODO to complete the project.

Run:
  python starter.py --holdings AAPL:0.25,MSFT:0.20,NVDA:0.30,GOOGL:0.25 --period 1y

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
# State Definition
# ---------------------------------------------------------------------------

class PortfolioState(TypedDict):
    holdings: dict                                        # {ticker: weight}
    period: str                                           # yfinance period
    price_data: dict                                      # serialized price DataFrame
    market_analysis: Annotated[dict, operator.or_]       # populated by market_analyst
    fundamental_analysis: Annotated[dict, operator.or_]  # populated by fundamental_researcher
    risk_metrics: dict                                    # populated by risk_manager
    recommendation: str                                   # populated by portfolio_advisor
    report_path: str                                      # populated by save_report


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def call_claude(system: str, user: str, max_tokens: int = 2048) -> str:
    """Call Claude and return the response text."""
    # TODO: instantiate anthropic.Anthropic(), call messages.create(), return text
    raise NotImplementedError


def compute_rsi(series: pd.Series, period: int = 14) -> float:
    """
    Compute the Relative Strength Index for the last data point.
    RSI = 100 - (100 / (1 + avg_gain / avg_loss)) over `period` days.
    """
    # TODO: compute delta, separate gains/losses, rolling mean, RSI formula
    raise NotImplementedError


def compute_macd(series: pd.Series) -> dict:
    """
    Compute MACD line, signal line, and crossover direction.
    MACD = EMA-12 - EMA-26
    Signal = EMA-9 of MACD
    """
    # TODO: use .ewm(span=N, adjust=False).mean() for EMAs
    # Return {"macd": float, "signal": float, "crossover": "bullish" | "bearish"}
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Node 1: fetch_data
# ---------------------------------------------------------------------------

def fetch_data(state: PortfolioState):
    """
    Download historical price data for all holdings using yfinance.
    Return a list of Send objects to dispatch market_analyst and
    fundamental_researcher in parallel.
    """
    print("[fetch_data] downloading price history...")
    # TODO:
    # 1. yf.download(tickers, period=period, auto_adjust=True, progress=False)
    # 2. Extract "Close" prices (handle MultiIndex for multiple tickers)
    # 3. Forward-fill and drop NaN
    # 4. Serialize to JSON (price_df.reset_index().to_json(date_format="iso"))
    # 5. Build updated_state with price_data and empty dicts for analysis fields
    # 6. Return [Send("market_analyst", updated_state), Send("fundamental_researcher", updated_state)]
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Node 2a: market_analyst
# ---------------------------------------------------------------------------

def market_analyst(state: PortfolioState) -> dict:
    """
    For each ticker: compute RSI, MACD, MA-50, MA-200.
    Classify trend (bullish/bearish based on MA cross).
    Call Claude to generate a 2-3 sentence technical outlook per ticker.
    Return {"market_analysis": {ticker: {..., "summary": "..."}}}
    """
    t_start = time.time()
    print(f"[market_analyst] starting... ({datetime.now().strftime('%H:%M:%S.%f')[:12]})")
    # TODO: implement
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Node 2b: fundamental_researcher
# ---------------------------------------------------------------------------

def fundamental_researcher(state: PortfolioState) -> dict:
    """
    For each ticker: fetch yf.Ticker(ticker).info dict.
    Extract trailingPE, forwardPE, trailingEps, revenueGrowth,
    recommendationKey, targetMeanPrice, currentPrice.
    Compute upside_pct = (target - current) / current * 100.
    Call Claude to generate a 2-3 sentence fundamental assessment per ticker.
    Return {"fundamental_analysis": {ticker: {..., "summary": "..."}}}
    """
    t_start = time.time()
    print(f"[fundamental_researcher] starting... ({datetime.now().strftime('%H:%M:%S.%f')[:12]})")
    # TODO: implement
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Node 3: risk_manager
# ---------------------------------------------------------------------------

def risk_manager(state: PortfolioState) -> dict:
    """
    Compute portfolio-level risk metrics:
    - Annualized return and volatility
    - Sharpe ratio (RISK_FREE_RATE = 0.04)
    - Max drawdown
    - VaR at 95% confidence (5th percentile of daily returns)
    - Pairwise correlation matrix
    Return {"risk_metrics": {...}}
    """
    print("[risk_manager] computing portfolio risk metrics...")
    # TODO: implement using numpy and pandas
    # Normalize weights so they sum to 1.0
    # Portfolio daily return = daily_returns.values @ weights
    # Max drawdown: (cumulative.cummax() - cumulative) / cumulative.cummax()
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Node 4: portfolio_advisor
# ---------------------------------------------------------------------------

def portfolio_advisor(state: PortfolioState) -> dict:
    """
    Synthesize all three agent outputs into a complete portfolio report.
    Call Claude with all findings in a single prompt.
    The report must contain sections:
      ## Current Portfolio State
      ## Market Analysis
      ## Fundamental Analysis
      ## Risk Assessment
      ## Recommended Actions
    Each recommendation: BUY/HOLD/TRIM/SELL + target % + 2-sentence rationale.
    Return {"recommendation": full_markdown_report}
    """
    print("[portfolio_advisor] synthesizing recommendations...")
    # TODO: implement
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Node 5: save_report
# ---------------------------------------------------------------------------

def save_report(state: PortfolioState) -> dict:
    """Write the recommendation to portfolio_report.md."""
    # TODO: write state["recommendation"] to "portfolio_report.md"
    # Return {"report_path": "portfolio_report.md"}
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Graph Construction
# ---------------------------------------------------------------------------

def build_graph():
    """
    Build and compile the LangGraph StateGraph.

    Topology:
      fetch_data
        ├── market_analyst      (parallel via Send)
        └── fundamental_researcher (parallel via Send)
              both → risk_manager → portfolio_advisor → save_report → END
    """
    graph = StateGraph(PortfolioState)

    # TODO: add all nodes
    # TODO: set entry point to "fetch_data"
    # TODO: add conditional edges from fetch_data (returns Send objects)
    # TODO: add edges: both parallel nodes → risk_manager → portfolio_advisor → save_report → END
    # TODO: return graph.compile()
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

def parse_holdings(holdings_str: str) -> dict:
    result = {}
    for pair in holdings_str.split(","):
        parts = pair.strip().split(":")
        if len(parts) == 2:
            ticker = parts[0].strip().upper()
            weight = float(parts[1].strip())
            result[ticker] = weight
    total = sum(result.values())
    return {k: round(v / total, 4) for k, v in result.items()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-Agent Portfolio Manager")
    parser.add_argument("--holdings", default="AAPL:0.25,MSFT:0.25,NVDA:0.25,GOOGL:0.25")
    parser.add_argument("--period", default="1y")
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
    print(f"Report: {final_state.get('report_path', 'not saved')}")
