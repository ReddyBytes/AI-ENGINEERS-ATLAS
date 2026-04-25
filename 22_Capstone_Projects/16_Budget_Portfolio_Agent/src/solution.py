"""
Budget Portfolio Agent — Complete Solution
==========================================
Run:
    python solution.py ingest --bank-csv data/hdfc.csv --bank hdfc \\
                              --zerodha-csv data/zerodha.csv \\
                              --groww-csv data/groww.csv \\
                              --cdsl-pdf data/cdsl.pdf
    python solution.py briefing --name Priya
    python solution.py simulate --category food --cut-pct 50 \\
                                --target-savings 1000000 --current-savings 250000
    python solution.py report

Requirements:
    pip install anthropic pdfplumber pandas yfinance scipy reportlab python-dotenv httpx
"""

import os
import re
import json
import math
import argparse
from pathlib import Path
from datetime import date as date_type
from collections import deque

import pandas as pd
from dotenv import load_dotenv

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
# Ingestion — Bank CSVs
# ---------------------------------------------------------------------------
BANK_SCHEMAS = {
    "hdfc": {
        "date_col": "Date",
        "narration_col": "Narration",
        "debit_col": "Withdrawal Amt.",
        "credit_col": "Deposit Amt.",
        "date_format": "%d/%m/%Y",
        "skiprows": 0,
    },
    "sbi": {
        "date_col": "Txn Date",
        "narration_col": "Description",
        "debit_col": "Debit",
        "credit_col": "Credit",
        "date_format": "%d %b %Y",
        "skiprows": 0,
    },
    "icici": {
        "date_col": "Transaction Date",
        "narration_col": "Transaction Remarks",
        "debit_col": "Withdrawal Amount (INR )",
        "credit_col": "Deposit Amount (INR )",
        "date_format": "%d/%m/%Y",
        "skiprows": 0,
    },
    "axis": {
        "date_col": "Tran Date",
        "narration_col": "PARTICULARS",
        "debit_col": "DR",
        "credit_col": "CR",
        "date_format": "%d-%m-%Y",
        "skiprows": 0,
    },
}


def parse_bank_csv(path: str, bank: str) -> pd.DataFrame:
    """Parse bank CSV into unified: date, narration, amount, direction, source."""
    schema = BANK_SCHEMAS[bank.lower()]
    df = pd.read_csv(path, skiprows=schema.get("skiprows", 0))
    df = df.rename(columns={
        schema["date_col"]:      "date",
        schema["narration_col"]: "narration",
        schema["debit_col"]:     "debit",
        schema["credit_col"]:    "credit",
    })
    df["date"] = pd.to_datetime(
        df["date"], format=schema["date_format"], errors="coerce"
    )

    def _clean_num(series):
        return pd.to_numeric(
            series.astype(str).str.replace(",", "").str.strip(),
            errors="coerce",
        ).fillna(0)

    df["debit"]  = _clean_num(df["debit"])
    df["credit"] = _clean_num(df["credit"])

    rows = []
    for _, row in df.dropna(subset=["date"]).iterrows():
        if row["debit"] > 0:
            rows.append({
                "date": row["date"], "narration": str(row["narration"]),
                "amount": row["debit"], "direction": "debit", "source": bank,
            })
        elif row["credit"] > 0:
            rows.append({
                "date": row["date"], "narration": str(row["narration"]),
                "amount": row["credit"], "direction": "credit", "source": bank,
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Ingestion — Zerodha tradebook
# ---------------------------------------------------------------------------
def parse_zerodha_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["trade_date"] = pd.to_datetime(df["trade_date"], errors="coerce")
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["price"]    = pd.to_numeric(df["price"],    errors="coerce")
    return df[["trade_date", "tradingsymbol", "trade_type", "quantity", "price"]].rename(
        columns={
            "trade_date":    "date",
            "tradingsymbol": "symbol",
            "trade_type":    "type",
            "quantity":      "qty",
        }
    )


# ---------------------------------------------------------------------------
# Ingestion — Groww
# ---------------------------------------------------------------------------
def parse_groww_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [
        c.strip().lower().replace(" ", "_").replace("/", "_")
        for c in df.columns
    ]
    df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")
    rename_map = {}
    for col in df.columns:
        if "scheme" in col or "stock" in col:
            rename_map[col] = "fund_name"
        if "nav" in col or "price" in col:
            rename_map[col] = "nav"
    df = df.rename(columns=rename_map)
    df["amount"] = pd.to_numeric(
        df.get("amount", pd.Series(dtype=float)).astype(str).str.replace(",", ""),
        errors="coerce",
    )
    df["units"] = pd.to_numeric(df.get("units", pd.Series(dtype=float)), errors="coerce")
    df["nav"]   = pd.to_numeric(df.get("nav",   pd.Series(dtype=float)), errors="coerce")
    cols = ["date", "type", "fund_name", "units", "nav", "amount"]
    return df[[c for c in cols if c in df.columns]]


# ---------------------------------------------------------------------------
# Ingestion — CDSL CAS PDF
# ---------------------------------------------------------------------------
ISIN_RE = re.compile(r"^IN[A-Z0-9]{10}$")   # ← ISINs are always 12 chars starting with IN


def parse_cdsl_pdf(path: str) -> pd.DataFrame:
    try:
        import pdfplumber
    except ImportError:
        raise ImportError("Install pdfplumber: pip install pdfplumber")

    rows = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            for table in (page.extract_tables() or []):
                for row in table:
                    if not row or not row[0]:
                        continue
                    isin = str(row[0]).strip()
                    if ISIN_RE.match(isin):
                        rows.append({
                            "isin":     isin,
                            "company":  str(row[1]).strip() if len(row) > 1 else "",
                            "qty":      _safe_float(row[2]) if len(row) > 2 else 0,
                            "avg_cost": _safe_float(row[3]) if len(row) > 3 else 0,
                        })
    return pd.DataFrame(rows)


def _safe_float(val) -> float:
    try:
        return float(str(val).replace(",", "").strip() or 0)
    except (ValueError, TypeError):
        return 0.0


# ---------------------------------------------------------------------------
# Categorizer
# ---------------------------------------------------------------------------
CATEGORIES = [
    "food", "rent", "sip", "emi", "subscription",
    "shopping", "salary", "transfer", "other",
]


def load_memory() -> dict:
    if MEMORY_FILE.exists():
        return json.loads(MEMORY_FILE.read_text())
    return {}


def save_memory(memory: dict) -> None:
    MEMORY_FILE.write_text(json.dumps(memory, indent=2))


def categorize_transaction(narration: str, memory: dict) -> str:
    """Return category. Checks memory first; calls Claude only for unknowns."""
    narration_lower = narration.lower()
    for fragment, category in memory.items():          # ← O(n) over memory dict
        if fragment in narration_lower:
            return category

    import anthropic
    client = anthropic.Anthropic(api_key=API_KEY)
    prompt = (
        f"Classify this Indian bank transaction into exactly one category.\n"
        f"Categories: {', '.join(CATEGORIES)}\n"
        f"Transaction narration: {narration}\n"
        f"Reply with ONE word only — the category name."
    )
    try:
        resp = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=16,                             # ← one word is enough
            messages=[{"role": "user", "content": prompt}],
        )
        category = resp.content[0].text.strip().lower()
    except Exception:
        category = "other"

    if category not in CATEGORIES:
        category = "other"

    key = narration_lower[:40]                         # ← store first 40 chars as key
    memory[key] = category
    return category


def categorize_all(df: pd.DataFrame, memory: dict) -> list:
    categories = [categorize_transaction(str(n), memory) for n in df["narration"]]
    save_memory(memory)
    return categories


# ---------------------------------------------------------------------------
# Portfolio — holdings + P&L
# ---------------------------------------------------------------------------
def compute_holdings(trades: pd.DataFrame) -> pd.DataFrame:
    """Weighted-average cost basis. Returns: symbol, qty_held, avg_buy_price."""
    holdings: dict = {}
    for _, row in trades.sort_values("date").iterrows():
        sym   = row["symbol"]
        qty   = float(row["qty"])
        price = float(row["price"])
        if sym not in holdings:
            holdings[sym] = {"qty": 0.0, "total_cost": 0.0}

        if str(row["type"]).lower() == "buy":
            holdings[sym]["total_cost"] += qty * price   # ← accumulate cost basis
            holdings[sym]["qty"]        += qty
        else:
            holdings[sym]["qty"] = max(0, holdings[sym]["qty"] - qty)

    rows = []
    for sym, h in holdings.items():
        if h["qty"] > 0:
            avg = h["total_cost"] / h["qty"] if h["qty"] else 0
            rows.append({"symbol": sym, "qty_held": h["qty"], "avg_buy_price": avg})
    return pd.DataFrame(rows) if rows else pd.DataFrame(
        columns=["symbol", "qty_held", "avg_buy_price"]
    )


def fetch_live_prices(symbols: list) -> dict:
    """Fetch last closing price for each symbol from NSE via yfinance."""
    import yfinance as yf

    if not symbols:
        return {}
    nse_tickers = [f"{s}.NS" for s in symbols]          # ← NSE ticker format
    try:
        raw = yf.download(
            nse_tickers, period="2d", auto_adjust=True, progress=False
        )
        if raw.empty:
            return {}
        close = raw["Close"] if "Close" in raw else raw
        last = close.iloc[-1]
        return {
            sym: float(last.get(f"{sym}.NS", 0) or 0)
            for sym in symbols
        }
    except Exception:
        return {sym: 0.0 for sym in symbols}


def compute_pnl(holdings: pd.DataFrame) -> pd.DataFrame:
    if holdings.empty:
        return holdings
    symbols = holdings["symbol"].tolist()
    prices  = fetch_live_prices(symbols)
    h = holdings.copy()
    h["live_price"]     = h["symbol"].map(prices).fillna(0)
    h["invested_value"] = h["qty_held"] * h["avg_buy_price"]
    h["current_value"]  = h["qty_held"] * h["live_price"]
    h["unrealized_pnl"] = h["current_value"] - h["invested_value"]
    h["pnl_pct"]        = (
        h["unrealized_pnl"] / h["invested_value"].replace(0, float("nan")) * 100
    ).round(2).fillna(0)
    return h


# ---------------------------------------------------------------------------
# XIRR
# ---------------------------------------------------------------------------
def xirr(cashflows: list, dates: list) -> float:
    """Annualised XIRR via scipy brentq. Returns decimal (0.14 = 14%)."""
    from scipy.optimize import brentq

    if len(cashflows) < 2:
        return 0.0
    d0 = dates[0]

    def npv(rate):
        return sum(
            cf / (1 + rate) ** ((d - d0).days / 365)   # ← time-weighted discount
            for cf, d in zip(cashflows, dates)
        )

    try:
        return brentq(npv, -0.999, 100.0, maxiter=1000)
    except (ValueError, RuntimeError):
        return 0.0


def compute_sip_xirr(groww_df: pd.DataFrame) -> pd.DataFrame:
    if groww_df.empty:
        return pd.DataFrame(columns=["fund", "xirr_pct"])
    results = []
    for fund, group in groww_df.groupby("fund_name"):
        group = group.sort_values("date")
        cfs   = [-float(r["amount"]) for _, r in group.iterrows()]
        dates = [r["date"].date() for _, r in group.iterrows()]
        total_units = group["units"].sum()
        latest_nav  = group.sort_values("date").iloc[-1]["nav"]
        cfs.append(float(total_units * latest_nav))   # ← current value as final inflow
        dates.append(date_type.today())
        rate = xirr(cfs, dates)
        results.append({"fund": fund, "xirr_pct": round(rate * 100, 2)})
    return pd.DataFrame(results)


# ---------------------------------------------------------------------------
# Tax Agent — STCG / LTCG
# ---------------------------------------------------------------------------
STCG_RATE    = 0.20       # ← 20% flat post July 2024 budget
LTCG_RATE    = 0.125      # ← 12.5% post budget 2024
LTCG_EXEMPT  = 125_000    # ← ₹1.25L annual exemption


def classify_gains(trades: pd.DataFrame) -> dict:
    """FIFO-based STCG/LTCG classifier. Returns tax summary dict."""
    buy_queues: dict = {}
    stcg_total = 0.0
    ltcg_total = 0.0

    for _, row in trades.sort_values("date").iterrows():
        sym   = row["symbol"]
        qty   = float(row["qty"])
        price = float(row["price"])
        dt    = row["date"].date() if hasattr(row["date"], "date") else row["date"]

        if str(row["type"]).lower() == "buy":
            buy_queues.setdefault(sym, deque())
            buy_queues[sym].append((dt, qty, price))

        elif str(row["type"]).lower() == "sell" and sym in buy_queues:
            remaining = qty
            while remaining > 0 and buy_queues[sym]:
                buy_date, buy_qty, buy_price = buy_queues[sym][0]
                matched = min(remaining, buy_qty)
                gain = matched * (price - buy_price)
                holding_days = (dt - buy_date).days

                if holding_days >= 365:                # ← 12-month rule for equity
                    ltcg_total += gain
                else:
                    stcg_total += gain

                if matched == buy_qty:
                    buy_queues[sym].popleft()
                else:
                    buy_queues[sym][0] = (buy_date, buy_qty - matched, buy_price)
                remaining -= matched

    ltcg_taxable = max(0.0, ltcg_total - LTCG_EXEMPT)   # ← apply ₹1.25L exemption
    return {
        "stcg_gain":          round(stcg_total, 2),
        "ltcg_gain":          round(ltcg_total, 2),
        "stcg_tax":           round(max(0.0, stcg_total) * STCG_RATE, 2),
        "ltcg_tax":           round(ltcg_taxable * LTCG_RATE, 2),
        "total_tax_estimate": round(
            max(0.0, stcg_total) * STCG_RATE + ltcg_taxable * LTCG_RATE, 2
        ),
    }


# ---------------------------------------------------------------------------
# Advisor Agent
# ---------------------------------------------------------------------------
ADVISOR_SYSTEM = """
You are a sharp, friendly personal finance advisor for Indian retail investors.
Write weekly briefings that are clear, specific, and actionable.
Use INR (₹) for all monetary figures. Keep responses under 300 words.
Do not use jargon without a brief explanation.
""".strip()


def generate_briefing(
    user_name: str,
    spend_summary: dict,
    pnl_summary: dict,
    tax_summary: dict,
    sip_xirr: list,
) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=API_KEY)

    sip_lines = "\n".join(
        f"  {item.get('fund', '?')}: {item.get('xirr_pct', 0):.1f}% XIRR"
        for item in sip_xirr
    ) or "  No SIP data available"

    spend_lines = "\n".join(
        f"  {k}: ₹{v:,.0f}" for k, v in spend_summary.items()
    ) or "  No spend data"

    context = f"""
User: {user_name}

SPENDING THIS MONTH (₹):
{spend_lines}

EQUITY PORTFOLIO:
  Total invested:  ₹{pnl_summary.get('invested_value', 0):,.0f}
  Current value:   ₹{pnl_summary.get('current_value', 0):,.0f}
  Unrealized P&L:  ₹{pnl_summary.get('unrealized_pnl', 0):,.0f}

SIP XIRR (annualised returns):
{sip_lines}

TAX ESTIMATE (FY so far):
  STCG tax: ₹{tax_summary.get('stcg_tax', 0):,.0f}
  LTCG tax: ₹{tax_summary.get('ltcg_tax', 0):,.0f}
  Total:    ₹{tax_summary.get('total_tax_estimate', 0):,.0f}
""".strip()

    resp = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=512,
        system=ADVISOR_SYSTEM,
        messages=[{
            "role": "user",
            "content": f"Write this week's financial briefing for {user_name}:\n\n{context}",
        }],
    )
    return resp.content[0].text


# ---------------------------------------------------------------------------
# What-if Simulator
# ---------------------------------------------------------------------------
def simulate_savings(
    transactions_df: pd.DataFrame,
    category: str,
    cut_pct: float,
    target_savings: float,
    current_savings: float,
) -> dict:
    df = transactions_df.copy()
    df["date"] = pd.to_datetime(df["date"])

    cutoff = df["date"].max() - pd.DateOffset(months=3)   # ← last 3 months window
    mask = (
        (df["date"] >= cutoff)
        & (df["category"] == category)
        & (df["direction"] == "debit")
    )
    monthly_avg = df.loc[mask, "amount"].sum() / 3         # ← simple 3-month average
    monthly_increase = monthly_avg * (cut_pct / 100)

    if monthly_increase <= 0:
        return {"months_to_target": None, "monthly_saving_increase": 0.0,
                "message": f"No {category} spend found in last 3 months."}

    gap = target_savings - current_savings
    if gap <= 0:
        return {"months_to_target": 0,
                "monthly_saving_increase": round(monthly_increase, 2),
                "message": "You have already reached your target!"}

    months = math.ceil(gap / monthly_increase)
    return {
        "months_to_target": months,
        "monthly_saving_increase": round(monthly_increase, 2),
        "message": (
            f"Cutting {category} spend by {cut_pct:.0f}% saves "
            f"₹{monthly_increase:,.0f}/month. "
            f"You hit ₹{target_savings:,.0f} in {months} months "
            f"({months // 12} years {months % 12} months)."
        ),
    }


# ---------------------------------------------------------------------------
# Report Generator
# ---------------------------------------------------------------------------
def generate_pdf_report(
    user_name: str,
    month_label: str,
    spend_df: pd.DataFrame,
    pnl_df: pd.DataFrame,
    tax_summary: dict,
    output_path: str,
) -> None:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        )
        from reportlab.lib.styles import getSampleStyleSheet
    except ImportError:
        raise ImportError("Install reportlab: pip install reportlab")

    doc    = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story  = []

    # Header
    story.append(Paragraph(
        f"Monthly Financial Report — {user_name} — {month_label}",
        styles["Title"],
    ))
    story.append(Spacer(1, 0.5 * cm))

    # Spending breakdown table
    if not spend_df.empty:
        story.append(Paragraph("Spending Breakdown", styles["Heading2"]))
        spend_data = [["Category", "Amount (₹)"]] + [
            [row["category"], f"₹{row['amount']:,.0f}"]
            for _, row in spend_df.groupby("category")["amount"].sum().reset_index().iterrows()
        ]
        _add_table(story, spend_data, colors.lightblue)

    story.append(Spacer(1, 0.5 * cm))

    # Portfolio P&L table
    if not pnl_df.empty:
        story.append(Paragraph("Portfolio P&L", styles["Heading2"]))
        pnl_cols = ["symbol", "qty_held", "avg_buy_price", "live_price", "unrealized_pnl", "pnl_pct"]
        pnl_cols = [c for c in pnl_cols if c in pnl_df.columns]
        pnl_data = [pnl_cols] + pnl_df[pnl_cols].values.tolist()
        _add_table(story, pnl_data, colors.lightgreen)

    story.append(Spacer(1, 0.5 * cm))

    # Tax summary
    story.append(Paragraph("Tax Estimate (FY so far)", styles["Heading2"]))
    tax_data = [["Item", "Amount (₹)"]] + [
        [k.replace("_", " ").title(), f"₹{v:,.0f}"]
        for k, v in tax_summary.items()
    ]
    _add_table(story, tax_data, colors.lightyellow)

    doc.build(story)
    print(f"PDF report saved to {output_path}")


def _add_table(story, data, header_color):
    from reportlab.platypus import Table, TableStyle
    from reportlab.lib import colors

    t = Table([[str(cell) for cell in row] for row in data])
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, 0), header_color),
        ("TEXTCOLOR",   (0, 0), (-1, 0), colors.black),
        ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ("GRID",        (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN",       (0, 0), (-1, -1), "LEFT"),
        ("TOPPADDING",  (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t)


# ---------------------------------------------------------------------------
# CLI Orchestrator
# ---------------------------------------------------------------------------
def build_parser():
    parser = argparse.ArgumentParser(description="Budget Portfolio Agent")
    sub = parser.add_subparsers(dest="command")

    # ingest
    ing = sub.add_parser("ingest", help="Parse and categorise all inputs")
    ing.add_argument("--bank-csv",    default=None)
    ing.add_argument("--bank",        default="hdfc")
    ing.add_argument("--zerodha-csv", default=None)
    ing.add_argument("--groww-csv",   default=None)
    ing.add_argument("--cdsl-pdf",    default=None)

    # briefing
    br = sub.add_parser("briefing", help="Generate weekly advisor briefing")
    br.add_argument("--name", default="Investor")

    # simulate
    sim = sub.add_parser("simulate", help="What-if savings simulation")
    sim.add_argument("--category",        required=True)
    sim.add_argument("--cut-pct",         type=float, required=True)
    sim.add_argument("--target-savings",  type=float, required=True)
    sim.add_argument("--current-savings", type=float, required=True)

    # report
    sub.add_parser("report", help="Generate monthly PDF report")

    return parser


def main():
    parser = build_parser()
    args   = parser.parse_args()

    txn_path      = DATA_DIR / "transactions.csv"
    holdings_path = DATA_DIR / "holdings.csv"
    tax_path      = DATA_DIR / "tax_summary.json"

    # -----------------------------------------------------------------------
    if args.command == "ingest":
        all_txns = []
        memory   = load_memory()

        if args.bank_csv:
            bank_df = parse_bank_csv(args.bank_csv, args.bank)
            bank_df["category"] = categorize_all(bank_df, memory)
            all_txns.append(bank_df)
            print(f"Bank ({args.bank}): {len(bank_df)} transactions categorised")

        if all_txns:
            combined = pd.concat(all_txns, ignore_index=True)
            combined.to_csv(txn_path, index=False)
            print(f"Saved {len(combined)} transactions -> {txn_path}")

        if args.zerodha_csv:
            trades = parse_zerodha_csv(args.zerodha_csv)
            holdings = compute_holdings(trades)
            pnl      = compute_pnl(holdings)
            pnl.to_csv(holdings_path, index=False)
            print(f"Portfolio: {len(pnl)} holdings -> {holdings_path}")
            tax = classify_gains(trades)
            tax_path.write_text(json.dumps(tax, indent=2))
            print(f"Tax summary: {tax}")

        if args.groww_csv:
            groww_df = parse_groww_csv(args.groww_csv)
            sip      = compute_sip_xirr(groww_df)
            print("SIP XIRR:")
            print(sip.to_string(index=False))

        if args.cdsl_pdf:
            cdsl = parse_cdsl_pdf(args.cdsl_pdf)
            print(f"CDSL holdings: {len(cdsl)} entries")
            print(cdsl.to_string(index=False))

    # -----------------------------------------------------------------------
    elif args.command == "briefing":
        if not txn_path.exists():
            print("No transactions found. Run 'ingest' first.")
            return
        txn_df = pd.read_csv(txn_path)
        spend  = (
            txn_df[txn_df["direction"] == "debit"]
            .groupby("category")["amount"].sum()
            .to_dict()
        )
        pnl_summary = {"invested_value": 0, "current_value": 0, "unrealized_pnl": 0}
        if holdings_path.exists():
            pnl_df = pd.read_csv(holdings_path)
            pnl_summary = {
                "invested_value": pnl_df["invested_value"].sum(),
                "current_value":  pnl_df["current_value"].sum(),
                "unrealized_pnl": pnl_df["unrealized_pnl"].sum(),
            }
        tax_summary = {}
        if tax_path.exists():
            tax_summary = json.loads(tax_path.read_text())

        briefing = generate_briefing(
            user_name=args.name,
            spend_summary=spend,
            pnl_summary=pnl_summary,
            tax_summary=tax_summary,
            sip_xirr=[],
        )
        print("\n" + "=" * 60)
        print(briefing)
        print("=" * 60)

    # -----------------------------------------------------------------------
    elif args.command == "simulate":
        if not txn_path.exists():
            print("No transactions found. Run 'ingest' first.")
            return
        txn_df = pd.read_csv(txn_path)
        result = simulate_savings(
            transactions_df=txn_df,
            category=args.category,
            cut_pct=args.cut_pct,
            target_savings=args.target_savings,
            current_savings=args.current_savings,
        )
        print(result["message"])

    # -----------------------------------------------------------------------
    elif args.command == "report":
        if not txn_path.exists():
            print("No transactions found. Run 'ingest' first.")
            return
        txn_df  = pd.read_csv(txn_path)
        pnl_df  = pd.read_csv(holdings_path) if holdings_path.exists() else pd.DataFrame()
        tax     = json.loads(tax_path.read_text()) if tax_path.exists() else {}
        from datetime import datetime
        month_label = datetime.today().strftime("%B %Y")
        out_path    = str(REPORT_DIR / f"report_{datetime.today().strftime('%Y%m')}.pdf")
        generate_pdf_report(
            user_name="Investor",
            month_label=month_label,
            spend_df=txn_df,
            pnl_df=pnl_df,
            tax_summary=tax,
            output_path=out_path,
        )

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
