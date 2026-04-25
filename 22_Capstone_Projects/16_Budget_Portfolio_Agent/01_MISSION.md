# 🎯 Mission Briefing — Budget Portfolio Agent

## 🗺️ The Analogy

Imagine hiring a personal CFO who never sleeps. Every morning they sort through your bank statements, check your mutual fund NAVs, calculate whether you owe the taxman anything, and hand you a plain-English briefing over coffee. They also answer hypotheticals: "What if I stopped ordering Swiggy four times a week?" Today you are going to build that CFO — in Python.

---

## 🎯 What This Project Builds

A **multi-agent financial intelligence system** tailored for Indian investors that:

- Parses bank statements exported from HDFC, SBI, ICICI, and Axis Bank (CSV format)
- Parses Zerodha Console tradebook CSV exports
- Parses Groww transaction history CSV exports
- Parses CDSL Consolidated Account Statement (CAS) PDFs
- Categorizes every transaction using Claude (food / rent / SIP / EMI / subscriptions / shopping) with persistent memory so it learns your patterns
- Tracks your equity portfolio with live NSE/BSE prices via yfinance (e.g. `RELIANCE.NS`, `TCS.NS`)
- Computes unrealized P&L, XIRR on SIPs, and STCG/LTCG tax estimates
- Generates a weekly plain-English advisor briefing in INR
- Runs a what-if simulator: "If I cut Swiggy spend by 50%, when do I hit ₹10L savings?"
- Produces a polished monthly PDF report via reportlab

---

## 📋 Success Criteria

| Criterion | What "Done" Looks Like |
|-----------|----------------------|
| Ingestion | All four CSV formats parse without errors; CDSL PDF holdings extracted |
| Categorization | Transactions labelled with >90% accuracy; categories persist in JSON |
| Portfolio | Live prices fetched; unrealized P&L correct to the rupee |
| Tax | STCG (held <12 months) and LTCG (held ≥12 months) correctly classified |
| Advisor | Briefing is readable plain English, references actual INR figures |
| What-if | Simulator returns a realistic savings timeline |
| Report | PDF renders with tables, charts, and INR formatting |

---

## 🎓 Learning Tier

**Advanced — Partially Guided**

This project assumes you are comfortable with:
- Python async / multi-agent orchestration patterns
- The Anthropic Python SDK (messages API, system prompts)
- pandas DataFrames and datetime manipulation
- Basic investing concepts (SIP, NAV, XIRR, STCG, LTCG)

You will need to reason through architecture decisions. Step-level hints are available inside `03_GUIDE.md` but full code is only provided at the end of each step.

---

## 🇮🇳 Why This Matters

Most personal finance tools in India are either too generic (Mint) or locked inside a broker's app. A custom agent understands *your* specific combination of HDFC salary account + Zerodha equity + Groww SIPs + CDSL demat holdings — something no off-the-shelf product does today. Building this gives you a genuine, differentiated portfolio project that directly signals financial-domain AI skills to recruiters.

---

## 📂 Navigation

| | Link |
|---|---|
| Back to Capstone Index | [22_Capstone_Projects README](../README.md) |
| Previous Project | [15 — Fine-Tune, Evaluate & Deploy](../15_Fine_Tune_Evaluate_Deploy/) |
| Next Project | [17 — Personal Profile Builder Agent](../17_Personal_Profile_Builder_Agent/01_MISSION.md) |
| Next File | [02 — Architecture](./02_ARCHITECTURE.md) |
