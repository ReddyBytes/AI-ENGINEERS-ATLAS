# 🔨 Build Guide — Budget Portfolio Agent

## How to Use This Guide

Each step tells you **what to build** and **why it matters**, shows partial scaffolding, and hides hints and full answers in expandable blocks. Work through each step before expanding anything — the struggle is where the learning happens.

Estimated total time: 6–10 hours.

---

## Step 1 — Project Skeleton and Environment

### What to build
Create the folder structure, a `.env` file for secrets, and a shared `config.py` that every agent imports. Define constants: `DATA_DIR`, `MEMORY_FILE`, `REPORT_DIR`.

### Partial scaffold
```python
# config.py
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR   = Path(__file__).parent
DATA_DIR   = BASE_DIR / "data"
MEMORY_FILE = BASE_DIR / "data" / "category_memory.json"
REPORT_DIR  = BASE_DIR / "reports"
API_KEY     = os.environ["ANTHROPIC_API_KEY"]

# TODO: create DATA_DIR and REPORT_DIR if they don't exist
```

<details><summary>💡 Hint</summary>

Use `Path.mkdir(parents=True, exist_ok=True)` so the script is idempotent — safe to run more than once.

</details>

<details><summary>✅ Answer</summary>

```python
# config.py
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR    = Path(__file__).parent
DATA_DIR    = BASE_DIR / "data"
MEMORY_FILE = BASE_DIR / "data" / "category_memory.json"
REPORT_DIR  = BASE_DIR / "reports"
API_KEY     = os.environ["ANTHROPIC_API_KEY"]

DATA_DIR.mkdir(parents=True, exist_ok=True)   # ← safe to call repeatedly
REPORT_DIR.mkdir(parents=True, exist_ok=True)
```

</details>

---

## Step 2 — Ingestion Agent: Bank Statements

### What to build
Write `ingestion.py` with a function `parse_bank_csv(path: str, bank: str) -> pd.DataFrame` that normalises HDFC, SBI, ICICI, and Axis CSV exports into a unified schema:

```
date | narration | amount | direction | source
```

Where `direction` is `"debit"` or `"credit"` and `source` is the bank name.

### Partial scaffold
```python
# ingestion.py
import pandas as pd
from pathlib import Path

BANK_SCHEMAS = {
    "hdfc": {
        "date_col": "Date",
        "narration_col": "Narration",
        "debit_col": "Withdrawal Amt.",
        "credit_col": "Deposit Amt.",
        "date_format": "%d/%m/%Y",
    },
    # TODO: add sbi, icici, axis schemas
}

def parse_bank_csv(path: str, bank: str) -> pd.DataFrame:
    schema = BANK_SCHEMAS[bank.lower()]
    # TODO: read CSV, rename columns, unify amount + direction
    ...
```

<details><summary>💡 Hint</summary>

HDFC and Axis have separate Withdrawal/Deposit columns. Melt them: wherever Withdrawal is non-NaN, direction = "debit" and amount = Withdrawal; otherwise "credit". Use `pd.to_numeric(..., errors="coerce")` to handle commas in numbers.

</details>

<details><summary>✅ Answer</summary>

```python
BANK_SCHEMAS = {
    "hdfc": {
        "date_col": "Date", "narration_col": "Narration",
        "debit_col": "Withdrawal Amt.", "credit_col": "Deposit Amt.",
        "date_format": "%d/%m/%Y",
    },
    "sbi": {
        "date_col": "Txn Date", "narration_col": "Description",
        "debit_col": "Debit", "credit_col": "Credit",
        "date_format": "%d %b %Y",
    },
    "icici": {
        "date_col": "Transaction Date", "narration_col": "Transaction Remarks",
        "debit_col": "Withdrawal Amount (INR )", "credit_col": "Deposit Amount (INR )",
        "date_format": "%d/%m/%Y",
    },
    "axis": {
        "date_col": "Tran Date", "narration_col": "PARTICULARS",
        "debit_col": "DR", "credit_col": "CR",
        "date_format": "%d-%m-%Y",
    },
}

def parse_bank_csv(path: str, bank: str) -> pd.DataFrame:
    schema = BANK_SCHEMAS[bank.lower()]
    df = pd.read_csv(path, skiprows=0)                         # ← some banks have header rows to skip
    df = df.rename(columns={
        schema["date_col"]: "date",
        schema["narration_col"]: "narration",
        schema["debit_col"]: "debit",
        schema["credit_col"]: "credit",
    })
    df["date"] = pd.to_datetime(df["date"], format=schema["date_format"], errors="coerce")
    df["debit"]  = pd.to_numeric(df["debit"].astype(str).str.replace(",", ""), errors="coerce").fillna(0)
    df["credit"] = pd.to_numeric(df["credit"].astype(str).str.replace(",", ""), errors="coerce").fillna(0)

    rows = []
    for _, row in df.iterrows():
        if row["debit"] > 0:
            rows.append({"date": row["date"], "narration": row["narration"],
                         "amount": row["debit"], "direction": "debit", "source": bank})
        elif row["credit"] > 0:
            rows.append({"date": row["date"], "narration": row["narration"],
                         "amount": row["credit"], "direction": "credit", "source": bank})
    return pd.DataFrame(rows)
```

</details>

---

## Step 3 — Ingestion Agent: Zerodha, Groww, and CDSL

### What to build
Extend `ingestion.py` with three more parsers:
- `parse_zerodha_csv(path)` — tradebook into `(date, symbol, trade_type, qty, price, exchange)`
- `parse_groww_csv(path)` — SIP/lumpsum into `(date, fund_name, units, nav, amount, type)`
- `parse_cdsl_pdf(path)` — CDSL CAS PDF into `(isin, company, qty, avg_cost)`

<details><summary>💡 Hint</summary>

For CDSL PDFs: use `pdfplumber.open(path)` then iterate `page.extract_tables()`. The holdings table usually has ISIN in the first column. Filter rows where the first cell matches the regex `r'^IN[A-Z0-9]{10}$'`.

</details>

<details><summary>✅ Answer</summary>

```python
import pdfplumber
import re

def parse_zerodha_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    return df[["trade_date", "tradingsymbol", "trade_type", "quantity", "price"]].rename(
        columns={"trade_date": "date", "tradingsymbol": "symbol",
                 "trade_type": "type", "quantity": "qty"}
    )

def parse_groww_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [c.strip().lower().replace(" ", "_").replace("/", "_") for c in df.columns]
    df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")
    df = df.rename(columns={"scheme_stock_name": "fund_name", "nav_price": "nav"})
    df["amount"] = pd.to_numeric(df["amount"].astype(str).str.replace(",", ""), errors="coerce")
    return df[["date", "type", "fund_name", "units", "nav", "amount"]]

ISIN_RE = re.compile(r"^IN[A-Z0-9]{10}$")   # ← ISIN always starts with IN and is 12 chars

def parse_cdsl_pdf(path: str) -> pd.DataFrame:
    rows = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables():
                for row in table:
                    if row and row[0] and ISIN_RE.match(str(row[0]).strip()):
                        rows.append({
                            "isin":     row[0].strip(),
                            "company":  row[1].strip() if len(row) > 1 else "",
                            "qty":      float(str(row[2]).replace(",", "") or 0) if len(row) > 2 else 0,
                            "avg_cost": float(str(row[3]).replace(",", "") or 0) if len(row) > 3 else 0,
                        })
    return pd.DataFrame(rows)
```

</details>

---

## Step 4 — Categorizer Agent

### What to build
Write `categorizer.py`. The agent:
1. Loads `category_memory.json` (a dict mapping `narration_fragment -> category`)
2. For each new transaction, checks if any known fragment is a substring of the narration
3. If not found, calls Claude to classify it into one of: `food`, `rent`, `sip`, `emi`, `subscription`, `shopping`, `salary`, `transfer`, `other`
4. Saves new mappings back to `category_memory.json`

### Partial scaffold
```python
# categorizer.py
import json
import anthropic
from config import MEMORY_FILE, API_KEY

CATEGORIES = ["food", "rent", "sip", "emi", "subscription",
              "shopping", "salary", "transfer", "other"]

client = anthropic.Anthropic(api_key=API_KEY)

def load_memory() -> dict:
    # TODO: load JSON or return empty dict
    ...

def save_memory(memory: dict) -> None:
    # TODO: write to MEMORY_FILE
    ...

def categorize_transaction(narration: str, memory: dict) -> str:
    narration_lower = narration.lower()
    # TODO: check memory for known fragments
    # TODO: if not found, call Claude
    ...
```

<details><summary>💡 Hint</summary>

For the memory lookup, iterate over memory keys and check `if key in narration_lower`. For the Claude call, ask it to reply with a single word from the CATEGORIES list — use a low `max_tokens` (16) to avoid verbose responses and strip/lower the output.

</details>

<details><summary>✅ Answer</summary>

```python
import json
import anthropic
from config import MEMORY_FILE, API_KEY

CATEGORIES = ["food", "rent", "sip", "emi", "subscription",
              "shopping", "salary", "transfer", "other"]

client = anthropic.Anthropic(api_key=API_KEY)

def load_memory() -> dict:
    if MEMORY_FILE.exists():
        return json.loads(MEMORY_FILE.read_text())
    return {}

def save_memory(memory: dict) -> None:
    MEMORY_FILE.write_text(json.dumps(memory, indent=2))

def categorize_transaction(narration: str, memory: dict) -> str:
    narration_lower = narration.lower()
    for fragment, category in memory.items():          # ← O(n) but memory stays small
        if fragment in narration_lower:
            return category

    prompt = (
        f"Classify this Indian bank transaction into exactly one category.\n"
        f"Categories: {', '.join(CATEGORIES)}\n"
        f"Transaction: {narration}\n"
        f"Reply with one word only."
    )
    resp = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=16,                                 # ← one word is enough
        messages=[{"role": "user", "content": prompt}]
    )
    category = resp.content[0].text.strip().lower()
    if category not in CATEGORIES:
        category = "other"

    # Persist a short key so future identical narrations skip the API call
    key = narration_lower[:40]                         # ← first 40 chars as memory key
    memory[key] = category
    return category

def categorize_all(df, memory: dict) -> list[str]:
    categories = []
    for narration in df["narration"]:
        categories.append(categorize_transaction(str(narration), memory))
    save_memory(memory)
    return categories
```

</details>

---

## Step 5 — Portfolio Agent: Live Prices and P&L

### What to build
Write `portfolio.py`. Given a DataFrame of trades (from Zerodha), compute:
- Average buy price per symbol
- Live price from yfinance
- Unrealized P&L = (live_price - avg_buy_price) * quantity_held

<details><summary>💡 Hint</summary>

Average buy price must account for multiple buys at different prices — use a weighted average. For sells, reduce the quantity held but do not recompute avg cost (FIFO would be more accurate but weighted-average is the simpler standard). Use `yf.download` in batch mode: `yf.download([...tickers...], period="1d")["Close"].iloc[-1]` to fetch all prices in one API call.

</details>

<details><summary>✅ Answer</summary>

```python
import pandas as pd
import yfinance as yf

def compute_holdings(trades: pd.DataFrame) -> pd.DataFrame:
    """
    trades columns: date, symbol, type (buy/sell), qty, price
    Returns: symbol, qty_held, avg_buy_price
    """
    holdings = {}
    for _, row in trades.sort_values("date").iterrows():
        sym = row["symbol"]
        qty = float(row["qty"])
        price = float(row["price"])
        if sym not in holdings:
            holdings[sym] = {"qty": 0.0, "total_cost": 0.0}

        if str(row["type"]).lower() == "buy":
            holdings[sym]["total_cost"] += qty * price   # ← accumulate cost basis
            holdings[sym]["qty"] += qty
        else:  # sell
            holdings[sym]["qty"] -= qty                  # ← reduce qty, keep avg cost

    rows = []
    for sym, h in holdings.items():
        if h["qty"] > 0:
            rows.append({
                "symbol": sym,
                "qty_held": h["qty"],
                "avg_buy_price": h["total_cost"] / h["qty"] if h["qty"] else 0,
            })
    return pd.DataFrame(rows)

def fetch_live_prices(symbols: list[str]) -> dict[str, float]:
    nse_tickers = [f"{s}.NS" for s in symbols]          # ← NSE suffix for yfinance
    raw = yf.download(nse_tickers, period="1d", auto_adjust=True, progress=False)
    if "Close" not in raw:
        return {}
    last_close = raw["Close"].iloc[-1]
    return {
        sym: float(last_close.get(f"{sym}.NS", 0) or 0)
        for sym in symbols
    }

def compute_pnl(holdings: pd.DataFrame) -> pd.DataFrame:
    symbols = holdings["symbol"].tolist()
    prices  = fetch_live_prices(symbols)
    holdings = holdings.copy()
    holdings["live_price"]     = holdings["symbol"].map(prices)
    holdings["invested_value"] = holdings["qty_held"] * holdings["avg_buy_price"]
    holdings["current_value"]  = holdings["qty_held"] * holdings["live_price"]
    holdings["unrealized_pnl"] = holdings["current_value"] - holdings["invested_value"]
    holdings["pnl_pct"]        = (holdings["unrealized_pnl"] / holdings["invested_value"] * 100).round(2)
    return holdings
```

</details>

---

## Step 6 — Portfolio Agent: XIRR on SIPs

### What to build
Write an `xirr(cashflows, dates)` function and use it to compute annualised returns for each Groww SIP scheme.

<details><summary>💡 Hint</summary>

XIRR convention: outflows (investments) are negative; the final inflow is `+current_value`. Use `scipy.optimize.brentq` to find the rate `r` where the NPV equals zero. The NPV formula is `sum(cf / (1+r)^((d - d0).days / 365))`.

</details>

<details><summary>✅ Answer</summary>

```python
from scipy.optimize import brentq
from datetime import date as date_type

def xirr(cashflows: list[float], dates: list[date_type]) -> float:
    """Return annualised XIRR as a decimal (e.g. 0.14 = 14%)."""
    if len(cashflows) < 2:
        return 0.0
    d0 = dates[0]

    def npv(rate):
        return sum(
            cf / (1 + rate) ** ((d - d0).days / 365)   # ← time-weighted discounting
            for cf, d in zip(cashflows, dates)
        )

    try:
        return brentq(npv, -0.999, 100.0, maxiter=1000)  # ← bracketed root finder
    except ValueError:
        return 0.0

def compute_sip_xirr(groww_df: pd.DataFrame) -> pd.DataFrame:
    results = []
    for fund, group in groww_df.groupby("fund_name"):
        group = group.sort_values("date")
        # All SIP investments are outflows
        cfs   = [-row["amount"] for _, row in group.iterrows()]
        dates = [row["date"].date() for _, row in group.iterrows()]

        # Approximate current value: latest units * latest NAV (simplified)
        total_units = group["units"].sum()
        latest_nav  = group.sort_values("date").iloc[-1]["nav"]
        cfs.append(total_units * latest_nav)             # ← final inflow = current value
        dates.append(date_type.today())

        rate = xirr(cfs, dates)
        results.append({"fund": fund, "xirr_pct": round(rate * 100, 2)})
    return pd.DataFrame(results)
```

</details>

---

## Step 7 — Tax Agent: STCG and LTCG

### What to build
Write `tax.py` with a function that takes the trade history and:
- Marks each sell as STCG (held < 12 months) or LTCG (held >= 12 months) for equity
- Estimates tax: STCG @ 20%, LTCG @ 12.5% on gains above ₹1.25L exemption (post Budget 2024)
- Returns a summary dict

<details><summary>💡 Hint</summary>

Build a buy queue per symbol (FIFO). For each sell, pop the earliest buy and measure the holding period. Use `relativedelta` or simple `.days >= 365` for the 12-month test. The ₹1.25L LTCG exemption applies to the aggregate LTCG across all stocks in the financial year.

</details>

<details><summary>✅ Answer</summary>

```python
import pandas as pd
from collections import deque
from datetime import date as date_type

STCG_RATE = 0.20    # ← flat 20% post July 2024
LTCG_RATE = 0.125   # ← 12.5% post Budget 2024
LTCG_EXEMPT = 125000  # ← ₹1.25L exemption per FY

def classify_gains(trades: pd.DataFrame) -> dict:
    buy_queues: dict[str, deque] = {}   # ← FIFO queue of (date, qty, price) per symbol
    stcg_total = 0.0
    ltcg_total = 0.0

    for _, row in trades.sort_values("date").iterrows():
        sym  = row["symbol"]
        qty  = float(row["qty"])
        price= float(row["price"])
        dt   = row["date"].date() if hasattr(row["date"], "date") else row["date"]

        if str(row["type"]).lower() == "buy":
            if sym not in buy_queues:
                buy_queues[sym] = deque()
            buy_queues[sym].append((dt, qty, price))

        elif str(row["type"]).lower() == "sell" and sym in buy_queues:
            remaining_sell = qty
            while remaining_sell > 0 and buy_queues[sym]:
                buy_date, buy_qty, buy_price = buy_queues[sym][0]
                matched = min(remaining_sell, buy_qty)
                gain = matched * (price - buy_price)
                holding_days = (dt - buy_date).days

                if holding_days >= 365:          # ← 12-month rule for equity LTCG
                    ltcg_total += gain
                else:
                    stcg_total += gain

                if matched == buy_qty:
                    buy_queues[sym].popleft()    # ← entire lot consumed
                else:
                    buy_queues[sym][0] = (buy_date, buy_qty - matched, buy_price)
                remaining_sell -= matched

    ltcg_taxable = max(0, ltcg_total - LTCG_EXEMPT)   # ← apply ₹1.25L exemption
    return {
        "stcg_gain":   round(stcg_total, 2),
        "ltcg_gain":   round(ltcg_total, 2),
        "stcg_tax":    round(max(0, stcg_total) * STCG_RATE, 2),
        "ltcg_tax":    round(ltcg_taxable * LTCG_RATE, 2),
        "total_tax_estimate": round(
            max(0, stcg_total) * STCG_RATE + ltcg_taxable * LTCG_RATE, 2
        ),
    }
```

</details>

---

## Step 8 — Advisor Agent

### What to build
Write `advisor.py`. Assemble a structured context string from all prior outputs (spend summary, portfolio P&L, tax estimate) and ask Claude to write a concise weekly briefing in plain English, addressing the user by name.

<details><summary>💡 Hint</summary>

Keep the context under 1000 tokens. Use bullet points in the prompt so Claude mirrors that structure. Ask for a ≤300-word response so it stays readable. Pass `user_name` as a variable so the greeting personalises.

</details>

<details><summary>✅ Answer</summary>

```python
import anthropic
from config import API_KEY

client = anthropic.Anthropic(api_key=API_KEY)

SYSTEM_PROMPT = """
You are a sharp, friendly personal finance advisor for Indian retail investors.
You write weekly briefings that are clear, specific, and actionable.
Use INR (₹) for all monetary values. Keep responses under 300 words.
Never use jargon without a brief explanation.
""".strip()

def generate_briefing(
    user_name: str,
    spend_summary: dict,
    pnl_summary: dict,
    tax_summary: dict,
    sip_xirr: list[dict],
) -> str:
    context = f"""
User: {user_name}

SPENDING THIS MONTH (₹):
{_fmt_dict(spend_summary)}

PORTFOLIO P&L:
  Total invested:  ₹{pnl_summary.get('invested_value', 0):,.0f}
  Current value:   ₹{pnl_summary.get('current_value', 0):,.0f}
  Unrealized P&L:  ₹{pnl_summary.get('unrealized_pnl', 0):,.0f}

SIP XIRR:
{_fmt_list(sip_xirr)}

TAX ESTIMATE (FY so far):
  STCG tax: ₹{tax_summary.get('stcg_tax', 0):,.0f}
  LTCG tax: ₹{tax_summary.get('ltcg_tax', 0):,.0f}
""".strip()

    resp = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"Write this week's financial briefing for {user_name}:\n\n{context}",
        }]
    )
    return resp.content[0].text

def _fmt_dict(d: dict) -> str:
    return "\n".join(f"  {k}: ₹{v:,.0f}" for k, v in d.items())

def _fmt_list(lst: list[dict]) -> str:
    return "\n".join(f"  {item.get('fund', item.get('symbol', '?'))}: {item.get('xirr_pct', item.get('pnl_pct', 0))}%" for item in lst)
```

</details>

---

## Step 9 — What-if Simulator

### What to build
Write `simulator.py` with a function:

```python
def simulate_savings(
    transactions_df: pd.DataFrame,
    category: str,
    cut_pct: float,
    target_savings: float,
    current_savings: float,
) -> dict:
```

It returns: `{"months_to_target": int, "monthly_saving_increase": float}`.

<details><summary>💡 Hint</summary>

Calculate the average monthly spend in the target category from the past 3 months. Multiply by `cut_pct/100` to get the monthly saving increase. Then `months = ceil((target_savings - current_savings) / monthly_saving_increase)`.

</details>

<details><summary>✅ Answer</summary>

```python
import math
import pandas as pd

def simulate_savings(
    transactions_df: pd.DataFrame,
    category: str,
    cut_pct: float,
    target_savings: float,
    current_savings: float,
) -> dict:
    df = transactions_df.copy()
    df["date"] = pd.to_datetime(df["date"])

    # Use the last 3 full months for a stable average
    cutoff = df["date"].max() - pd.DateOffset(months=3)
    recent = df[(df["date"] >= cutoff) & (df["category"] == category) & (df["direction"] == "debit")]

    monthly_avg = recent["amount"].sum() / 3              # ← 3-month average
    monthly_increase = monthly_avg * (cut_pct / 100)      # ← savings from the cut

    if monthly_increase <= 0:
        return {"months_to_target": None, "monthly_saving_increase": 0.0}

    gap = target_savings - current_savings
    if gap <= 0:
        return {"months_to_target": 0, "monthly_saving_increase": round(monthly_increase, 2)}

    months = math.ceil(gap / monthly_increase)
    return {
        "months_to_target": months,
        "monthly_saving_increase": round(monthly_increase, 2),
        "message": (
            f"Cutting {category} by {cut_pct}% saves ₹{monthly_increase:,.0f}/month. "
            f"You hit ₹{target_savings:,.0f} in {months} months."
        )
    }
```

</details>

---

## Step 10 — Report Generator and Orchestrator

### What to build
Write `report.py` to generate a monthly PDF using reportlab with:
- A header with user name, month, and date
- A spending breakdown table
- A portfolio P&L table
- A tax summary section

Then write `main.py` as the CLI orchestrator wiring all agents together.

<details><summary>💡 Hint</summary>

Use `reportlab.platypus.SimpleDocTemplate` with `Table` and `TableStyle`. For the CLI, use `argparse` with subcommands: `ingest`, `report`, `simulate`, `briefing`. The orchestrator should call agents in order and pass DataFrames/dicts between them.

</details>

<details><summary>✅ Answer</summary>

See `src/solution.py` for the complete integrated implementation.

</details>

---

## 📂 Navigation

| | Link |
|---|---|
| Back to Capstone Index | [22_Capstone_Projects README](../README.md) |
| Previous File | [02 — Architecture](./02_ARCHITECTURE.md) |
| Next File | [04 — Recap](./04_RECAP.md) |
| Starter Code | [src/starter.py](./src/starter.py) |
| Solution | [src/solution.py](./src/solution.py) |
