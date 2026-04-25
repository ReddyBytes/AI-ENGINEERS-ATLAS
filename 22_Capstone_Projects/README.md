# 🚀 AI Engineers Atlas — Capstone Projects

> Theory explains AI. Projects prove you can build it.

25 real systems — from probability explorers to multi-agent portfolio managers. Each project deploys working AI: RAG pipelines, LangGraph agents, LLM APIs, fine-tuned models, and production-grade inference systems.

---

## How This Series Works

Every project follows the **Mission Briefing Format**:

```
01_MISSION.md      — What you are building and why it matters
02_ARCHITECTURE.md — System design, data flow, tech stack
03_GUIDE.md        — Step-by-step build with hints and answers
src/starter.py     — Scaffolded code to get you started
src/solution.py    — Full reference solution
04_RECAP.md        — What you built, what you learned, what to extend
```

Difficulty progression across the 25 projects:

```
🟢 Fully Guided     — Concept → code → explanation at every step
🟡 Partially Guided — Steps explained, you write the code
🟠 Minimal Hints    — Requirements + one hint per step
🔴 Build Yourself   — Spec + acceptance criteria, solution at end
```

---

## Projects

### Track 1 — ML Foundations

| # | Project | Difficulty | Core Skills |
|---|---------|------------|-------------|
| 01 | [Data and Probability Explorer](./01_Data_and_Probability_Explorer/01_MISSION.md) | 🟢 Guided | pandas, matplotlib, scipy, probability distributions |
| 02 | [ML Model Comparison](./02_ML_Model_Comparison/01_MISSION.md) | 🟢 Guided | scikit-learn, cross-validation, bias-variance, confusion matrix |
| 03 | [Neural Net from Scratch](./03_Neural_Net_from_Scratch/01_MISSION.md) | 🟡 Partial | NumPy, backprop, gradient descent, no frameworks |
| 04 | [LLM Chatbot with Memory](./04_LLM_Chatbot_with_Memory/01_MISSION.md) | 🟡 Partial | Anthropic API, conversation history, streaming |
| 05 | [Intelligent Document Analyzer](./05_Intelligent_Document_Analyzer/01_MISSION.md) | 🟠 Hints | pdfplumber, Claude, structured extraction, Pydantic |

### Track 2 — Search and RAG

| # | Project | Difficulty | Core Skills |
|---|---------|------------|-------------|
| 06 | [Semantic Search Engine](./06_Semantic_Search_Engine/01_MISSION.md) | 🟡 Partial | embeddings, FAISS, cosine similarity, sentence-transformers |
| 07 | [Personal Knowledge Base RAG](./07_Personal_Knowledge_Base_RAG/01_MISSION.md) | 🟡 Partial | ChromaDB, chunking, retrieval pipeline, Claude |
| 08 | [Multi-Tool Research Agent](./08_Multi_Tool_Research_Agent/01_MISSION.md) | 🟠 Hints | tool calling, ReAct, web search, citation |
| 09 | [Custom LoRA Fine-Tuning](./09_Custom_LoRA_Fine_Tuning/01_MISSION.md) | 🟠 Hints | HuggingFace, PEFT, LoRA, dataset preparation |
| 10 | [Production RAG System](./10_Production_RAG_System/01_MISSION.md) | 🔴 Self | FastAPI, pgvector, async retrieval, evaluation |

### Track 3 — Agents and Orchestration

| # | Project | Difficulty | Core Skills |
|---|---------|------------|-------------|
| 11 | [Advanced RAG with Reranking](./11_Advanced_RAG_with_Reranking/01_MISSION.md) | 🔴 Self | hybrid search, cross-encoder reranking, HyDE |
| 12 | [LangGraph Support Bot](./12_LangGraph_Support_Bot/01_MISSION.md) | 🟠 Hints | LangGraph StateGraph, conditional edges, human-in-the-loop |
| 13 | [Automated Eval Pipeline](./13_Automated_Eval_Pipeline/01_MISSION.md) | 🟠 Hints | LLM-as-judge, faithfulness, RAGAS metrics |
| 14 | [Multi-Agent Research System](./14_Multi_Agent_Research_System/01_MISSION.md) | 🔴 Self | multi-agent orchestration, parallel agents, synthesis |
| 15 | [Fine-Tune Evaluate Deploy](./15_Fine_Tune_Evaluate_Deploy/01_MISSION.md) | 🔴 Self | full pipeline: fine-tune → evaluate → serve → monitor |

### Track 4 — Real-World AI Tools

| # | Project | Difficulty | Core Skills |
|---|---------|------------|-------------|
| 16 | [Budget Portfolio Agent](./16_Budget_Portfolio_Agent/01_MISSION.md) | 🟠 Hints | pdfplumber, yfinance, scipy XIRR, STCG/LTCG, reportlab |
| 17 | [Personal Profile Builder Agent](./17_Personal_Profile_Builder_Agent/01_MISSION.md) | 🟠 Hints | PyGithub, httpx, BeautifulSoup, Jinja2, Claude |
| 18 | [Daily Automation Agent](./18_Daily_Automation_Agent/01_MISSION.md) | 🟡 Partial | APScheduler, NewsAPI, yfinance, smtplib, Claude |
| 19 | [Research Paper to Podcast Agent](./19_Research_Paper_Podcast_Agent/01_MISSION.md) | 🟡 Partial | pdfplumber, Claude, gTTS, mp3 pipeline |
| 20 | [Stock Market Analysis Agent](./20_Stock_Market_Analysis_Agent/01_MISSION.md) | 🟠 Hints | yfinance, ta-lib, NewsAPI, RSI/MACD/Bollinger, Claude |

### Track 5 — Advanced Agent Systems

| # | Project | Difficulty | Core Skills |
|---|---------|------------|-------------|
| 21 | [Company Deep-Dive Agent](./21_Company_Deep_Dive_Agent/01_MISSION.md) | 🔴 Self | multi-agent, duckduckgo-search, yfinance, parallel Claude |
| 22 | [AI Job Application Agent](./22_AI_Job_Application_Agent/01_MISSION.md) | 🔴 Self | pdfplumber, BeautifulSoup, Claude, ATS optimization |
| 23 | [Codebase Review Agent](./23_Codebase_Review_Agent/01_MISSION.md) | 🔴 Self | Python AST, multi-agent, security analysis, architecture review |
| 24 | [Personal Knowledge Vault](./24_Personal_Knowledge_Vault/01_MISSION.md) | 🔴 Self | watchdog, ChromaDB, Claude RAG, CLI interface |
| 25 | [Multi-Agent Portfolio Manager](./25_Multi_Agent_Portfolio_Manager/01_MISSION.md) | 🔴 Self | LangGraph Send API, parallel agents, portfolio optimization |

---

## Learning Paths

**Path A — ML Foundations First**
```
01 → 02 → 03 → 04 → 05 → 06 → 07 → 10 → 14
Focus: understand the math before using APIs
```

**Path B — LLM/RAG Engineer**
```
04 → 06 → 07 → 08 → 10 → 11 → 12 → 13 → 14
Focus: production RAG + agent systems
```

**Path C — Real-World AI Tools (fastest to visible output)**
```
18 → 19 → 20 → 17 → 16 → 22 → 25
Focus: tools you can demo to anyone immediately
```

**Path D — Full Stack (complete the atlas)**
```
01–05 → 06–10 → 11–15 → 16–20 → 21–25
Focus: every track, every technique
```

---

## What You Can Build After Each Track

**Track 1 complete** — You understand the math behind every ML model. When someone says "the model is overfitting" or "gradient exploding", you know exactly what is happening and why.

**Track 2 complete** — You can build production-grade search and RAG systems. Vector databases, chunking strategies, retrieval evaluation — no longer black boxes.

**Track 3 complete** — You can design and orchestrate multi-agent systems. LangGraph, parallel execution, human-in-the-loop workflows, automated evaluation pipelines.

**Track 4 complete** — You have built real tools people actually use: portfolio analyzers, automation agents, podcast generators, stock analysis systems.

**Track 5 complete** — You can architect complex agent systems that combine search, memory, parallel execution, and multi-source data. Production-ready, extensible, observable.

---

## Navigation

| | |
|---|---|
| Back to AI-ENGINEERS-ATLAS | [README.md](../README.md) |
| Practice Questions | [ai_practice_questions_100.md](../ai_practice_questions_100.md) |
| Learning Guide | [00_Learning_Guide/](../00_Learning_Guide/) |
