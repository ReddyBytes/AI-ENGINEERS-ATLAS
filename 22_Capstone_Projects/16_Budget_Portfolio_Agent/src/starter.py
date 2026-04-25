"""
Budget Portfolio Agent — Starter Code
======================================
Run: python starter.py --help

Fill in every # TODO block. Do not modify function signatures.
"""

import os
import json
import argparse
from pathlib import Path
from datetime import date
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BASE_DIR    = Path(__file__).parent.parent
DATA_DIR    = BASE_DIR / "data"
MEMORY_FILE = DATA_DIR / "category_memory.json"
REPORT_DIR  = BASE_DIR / "reports"

DATA_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# ---------------------------------------------------------------------------
# Step 1 — Bank CSV parser
# ---------------------------------------------------------------------------
BANK_SCHEMAS: dict = {
    # TODO: define schema dicts for hdfc, sbi, icici, axis
    # Each schema needs: date_col, narration_col, debit_col, credit_col, date_format
}

def parse_bank_csv(path: str, bank: str) -> pd.DataFrame:
    """Parse a bank CSV into unified schema: date, narration, amount, direction, source."""
    # TODO: load CSV using schema, normalise amount/direction columns
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Step 2 — Zerodha / Groww / CDSL parsers
# ---------------------------------------------------------------------------
def parse_zerodha_csv(path: str) -> pd.DataFrame:
    """Return: date, symbol, type (buy/sell), qty, price"""
    # TODO
    raise NotImplementedError


def parse_groww_csv(path: str) -> pd.DataFrame:
    """Return: date, type, fund_name, units, nav, amount"""
    # TODO
    raise NotImplementedError


def parse_cdsl_pdf(path: str) -> pd.DataFrame:
    """Return: isin, company, qty, avg_cost"""
    # TODO: use pdfplumber to extract holdings table
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Step 3 — Categorizer
# ---------------------------------------------------------------------------
CATEGORIES = ["food", "rent", "sip", "emi", "subscription",
              "shopping", "salary", "transfer", "other"]

def load_memory() -> dict:
    # TODO: load MEMORY_FILE if exists, else return {}
    raise NotImplementedError


def save_memory(memory: dict) -> None:
    # TODO: write memory dict to MEMORY_FILE as JSON
    raise NotImplementedError


def categorize_transaction(narration: str, memory: dict) -> str:
    """Return a single category string. Use memory first, then Claude API."""
    # TODO: check memory, then call anthropic client
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Step 4 — Portfolio: holdings + live prices + P&L
# ---------------------------------------------------------------------------
def compute_holdings(trades: pd.DataFrame) -> pd.DataFrame:
    """Return: symbol, qty_held, avg_buy_price"""
    # TODO: FIFO or weighted-average cost basis
    raise NotImplementedError


def fetch_live_prices(symbols: list) -> dict:
    """Return {symbol: live_price_inr} via yfinance .NS tickers."""
    # TODO: use yf.download with .NS suffix
    raise NotImplementedError


def compute_pnl(holdings: pd.DataFrame) -> pd.DataFrame:
    """Add live_price, invested_value, current_value, unrealized_pnl columns."""
    # TODO
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Step 5 — XIRR
# ---------------------------------------------------------------------------
def xirr(cashflows: list, dates: list) -> float:
    """Return annualised XIRR as decimal using scipy brentq."""
    # TODO: implement NPV function + brentq root finding
    raise NotImplementedError


def compute_sip_xirr(groww_df: pd.DataFrame) -> pd.DataFrame:
    """Return DataFrame: fund, xirr_pct"""
    # TODO: group by fund_name, build cashflow list, call xirr()
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Step 6 — Tax classification
# ---------------------------------------------------------------------------
def classify_gains(trades: pd.DataFrame) -> dict:
    """Return {stcg_gain, ltcg_gain, stcg_tax, ltcg_tax, total_tax_estimate}."""
    # TODO: FIFO queue per symbol; 365-day rule for LTCG
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Step 7 — Advisor briefing
# ---------------------------------------------------------------------------
def generate_briefing(user_name: str, spend_summary: dict,
                      pnl_summary: dict, tax_summary: dict,
                      sip_xirr: list) -> str:
    """Return plain-English briefing string from Claude."""
    # TODO: assemble context, call anthropic client
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Step 8 — What-if simulator
# ---------------------------------------------------------------------------
def simulate_savings(transactions_df: pd.DataFrame, category: str,
                     cut_pct: float, target_savings: float,
                     current_savings: float) -> dict:
    """Return {months_to_target, monthly_saving_increase, message}."""
    # TODO: 3-month avg spend in category, compute months
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Step 9 — PDF Report
# ---------------------------------------------------------------------------
def generate_pdf_report(user_name: str, month_label: str,
                        spend_df: pd.DataFrame, pnl_df: pd.DataFrame,
                        tax_summary: dict, output_path: str) -> None:
    """Generate monthly PDF report using reportlab."""
    # TODO: SimpleDocTemplate, Table, TableStyle
    raise NotImplementedError


# ---------------------------------------------------------------------------
# CLI Orchestrator
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Budget Portfolio Agent")
    sub = parser.add_subparsers(dest="command")

    # ingest subcommand
    ingest_p = sub.add_parser("ingest", help="Parse and categorise all inputs")
    ingest_p.add_argument("--bank-csv",    help="Bank CSV path")
    ingest_p.add_argument("--bank",        help="Bank name: hdfc/sbi/icici/axis")
    ingest_p.add_argument("--zerodha-csv", help="Zerodha tradebook CSV path")
    ingest_p.add_argument("--groww-csv",   help="Groww transaction CSV path")
    ingest_p.add_argument("--cdsl-pdf",    help="CDSL CAS PDF path")

    # briefing subcommand
    briefing_p = sub.add_parser("briefing", help="Generate weekly advisor briefing")
    briefing_p.add_argument("--name", default="Investor", help="Your first name")

    # simulate subcommand
    sim_p = sub.add_parser("simulate", help="Run what-if savings simulation")
    sim_p.add_argument("--category",        required=True)
    sim_p.add_argument("--cut-pct",         type=float, required=True)
    sim_p.add_argument("--target-savings",  type=float, required=True)
    sim_p.add_argument("--current-savings", type=float, required=True)

    # report subcommand
    sub.add_parser("report", help="Generate monthly PDF report")

    args = parser.parse_args()

    if args.command == "ingest":
        # TODO: call parsers, categorize, save to DATA_DIR/transactions.csv + holdings.csv
        print("TODO: implement ingest command")

    elif args.command == "briefing":
        # TODO: load saved data, call generate_briefing, print result
        print("TODO: implement briefing command")

    elif args.command == "simulate":
        # TODO: load transactions.csv, call simulate_savings, print result
        print("TODO: implement simulate command")

    elif args.command == "report":
        # TODO: call generate_pdf_report
        print("TODO: implement report command")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
