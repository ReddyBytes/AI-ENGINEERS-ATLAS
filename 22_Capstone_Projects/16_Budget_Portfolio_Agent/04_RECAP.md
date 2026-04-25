# 📦 Recap — Budget Portfolio Agent

## What You Built

You assembled a six-agent financial intelligence system that mirrors a real fintech product — except it runs locally, understands your specific Indian broker formats, and costs nothing beyond API calls.

The pipeline flow you built:

```
Raw files (CSV/PDF)
        ↓  Ingestion Agent       — unified DataFrame
        ↓  Categorizer Agent     — LLM labels + persistent memory
        ↓  Portfolio Agent       — live prices + P&L + XIRR
        ↓  Tax Agent             — FIFO STCG/LTCG classification
        ↓  Advisor Agent         — plain-English weekly briefing
        ↓  Report Generator      — PDF with tables
        ↓
  Outputs: briefing / what-if / PDF report
```

---

## Concepts Applied

| Concept | Where You Used It |
|---------|-------------------|
| Multi-agent orchestration | Six independent agents sharing a common data store |
| LLM classification with memory | Categorizer Agent — reduces API calls after the first pass |
| yfinance live data | Portfolio Agent — `.NS` ticker format for NSE |
| XIRR via scipy | SIP returns — bracketed root finding with `brentq` |
| FIFO queue | Tax Agent — holding period classification for STCG/LTCG |
| PDF generation | reportlab `SimpleDocTemplate` + `Table` + `TableStyle` |
| CLI orchestration | `argparse` subcommands wiring all agents |
| Persistent JSON memory | Category memory that improves with each run |

---

## Three Extensions to Try

**Extension 1 — Slack / email delivery**
Add a `--notify` flag that sends the weekly briefing via the Slack Incoming Webhooks API or Python's `smtplib`. The advisor output is already a plain string — wrapping it in a POST request takes about 10 lines.

**Extension 2 — Streamlit dashboard**
Replace the CLI with a Streamlit app. Upload CSVs via `st.file_uploader`, render the P&L table with `st.dataframe`, and plot a spend pie chart with `st.plotly_chart`. This turns the tool into something non-technical users can actually use.

**Extension 3 — Goal-based planning agent**
Add a `goals.json` file where the user stores targets: `{"home_down_payment": 2000000, "emergency_fund": 600000}`. Write a Goal Agent that reads current savings, calculates monthly surplus from the advisor data, and projects when each goal will be hit — essentially an always-on financial planner.

---

## Job Mapping

| Skill Demonstrated | Role It Signals |
|--------------------|-----------------|
| Multi-agent system design | AI Engineer / Applied ML Engineer |
| Financial domain + LLM integration | FinTech AI Engineer |
| PDF parsing (pdfplumber) | Data Engineer / ETL |
| Tax calculation logic | Domain expert depth (Finance + Engineering) |
| CLI tool with argparse | Backend / Platform Engineer |
| LLM cost optimisation via persistent memory | Production AI Systems |

This project is strong enough to anchor a portfolio conversation at a Series B fintech or a data-focused bank (ICICI Securities, Zerodha, Groww, Smallcase). The Indian-specific formats (CDSL CAS, Zerodha tradebook, Groww CSV) demonstrate real domain knowledge that generic RAG chatbot projects do not.

---

## ✅ You Learned / 🔨 You Built / ➡️ Next Steps

✅ Multi-agent orchestration with shared state  
✅ LLM classification with persistent memory  
✅ Financial calculations: XIRR, STCG/LTCG, unrealized P&L  
✅ PDF parsing and PDF generation  

🔨 A complete CLI fintech tool with six specialised agents  
🔨 Real parsers for HDFC, SBI, ICICI, Axis, Zerodha, Groww, and CDSL  
🔨 A monthly PDF report and what-if simulator  

➡️ Add Streamlit UI for non-technical users  
➡️ Add Slack/email delivery for the weekly briefing  
➡️ Extend the Tax Agent with advance-tax quarterly reminders  

---

## 📂 Navigation

| | Link |
|---|---|
| Back to Capstone Index | [22_Capstone_Projects README](../README.md) |
| Previous File | [03 — Guide](./03_GUIDE.md) |
| Next Project | [17 — Personal Profile Builder Agent](../17_Personal_Profile_Builder_Agent/01_MISSION.md) |
