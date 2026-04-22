# AI Engineer Roadmap — 5 Months to 18LPA+

**Profile:** Working professional · Python 3/10 · Basic Docker/K8s/Airflow/AWS · 2–4 hrs/day · Project-first
**Target roles:** AI/ML Engineer · AI Application Engineer

> Checkboxes are interactive on GitHub — click to mark complete when you view this file in your browser.

---

## Overview — 5 Projects · 5 Months

| Month | Theme | Project You Will Build |
|-------|-------|----------------------|
| 1 | Python Mastery + Data | AI-Powered Data Pipeline |
| 2 | LLMs + RAG | Document Intelligence System |
| 3 | AI Agents | AI Research Agent |
| 4 | ML Engineering + MLOps | End-to-End ML Pipeline |
| 5 | Production + Interview Prep | Production AI Platform on AWS |

---

## Daily Time Plan (Non-Negotiable)

```
Weekdays
  Morning  6:00 – 6:30 AM  →  Read concepts / theory (30 min)
  Evening  8:30 – 10:00 PM →  Code / build project (90 min)

Weekends
  Morning  8:00 – 10:00 AM →  Project work / build features (2 hrs)
  Evening  5:00 – 7:00 PM  →  Debug / deploy / document (2 hrs)
```

> **Why split?** Morning brain absorbs concepts best. Evening brain is better at hands-on problem solving. Never mix both in one session.

---

## Month 1 — Python Mastery + Data Foundations

> **Goal:** Take Python from 3/10 to 8/10. Every AI framework is Python. Weak Python = slow progress in every future month.

---

### Week 1 — Python Core Concepts

**Focus:** OOP, file handling, error handling, type hints
**Best time for theory:** Morning 6–6:30 AM
**Best time for coding:** Evening 8:30–10 PM
**Resource:** `Python-DSA-API-Mastery` → `python-complete-mastery`

#### Topics to Cover

**Object Oriented Programming**
- [ ] Classes and objects — `__init__`, instance vs class variables
- [ ] Inheritance — single, multiple, `super()`
- [ ] Dunder methods — `__str__`, `__repr__`, `__len__`, `__eq__`, `__iter__`
- [ ] `@classmethod`, `@staticmethod`, `@property`
- [ ] Abstract classes using `ABC`

**How to prepare OOP:**
Read the concept → immediately write a mini class (e.g. a `BankAccount` or `Employee` class) implementing what you just read. Never read without coding within 10 minutes.

**Error Handling + Logging**
- [ ] `try / except / finally` — multiple exception types
- [ ] Custom exception classes
- [ ] `logging` module — levels, formatters, file handlers
- [ ] `assert` statements for debugging

**Type Hints + Clean Code**
- [ ] Basic type hints — `int`, `str`, `list`, `dict`, `Optional`
- [ ] `dataclasses` — cleaner alternative to plain classes
- [ ] `pathlib` for file paths (never use raw strings for paths)
- [ ] `.env` files + `python-dotenv` for secrets

**File Handling**
- [ ] Read/write text files, JSON, CSV
- [ ] `with` statement and context managers
- [ ] Writing your own context manager using `__enter__` / `__exit__`

#### Weekly Coding Task
- [ ] Build a `ConfigManager` class that reads `.env` + JSON config, validates fields, and raises custom exceptions for missing values

---

### Week 2 — Advanced Python

**Focus:** Decorators, generators, async, functional patterns
**Best time for theory:** Morning 6–6:30 AM
**Best time for coding:** Evening 8:30–10 PM

#### Topics to Cover

**Decorators**
- [ ] What decorators are and how they work (function wrapping)
- [ ] Writing a simple `@timer` decorator
- [ ] Writing a `@retry(max=3)` decorator with arguments
- [ ] `functools.wraps` — why it matters

**How to prepare decorators:**
Decorators confuse everyone at first. Read once, then write 3 decorators from scratch without looking: `@timer`, `@log_calls`, `@cache`. Understand them by building, not by reading twice.

**Generators + Iterators**
- [ ] `yield` keyword — lazy evaluation
- [ ] Generator expressions vs list comprehensions
- [ ] `itertools` — `chain`, `islice`, `groupby`
- [ ] Writing a custom iterator with `__iter__` + `__next__`

**Async Python**
- [ ] `async def` and `await` — what they mean
- [ ] `asyncio.gather()` — running coroutines in parallel
- [ ] `httpx.AsyncClient` — async HTTP requests
- [ ] When to use async vs threading vs multiprocessing

**How to prepare async:**
Build a script that calls 5 different APIs at the same time using `asyncio.gather`. Compare it to calling them one by one. Seeing the speed difference makes async click immediately.

**Functional Patterns**
- [ ] `map`, `filter`, `reduce`
- [ ] List/dict/set comprehensions
- [ ] `lambda` functions — when to use, when to avoid
- [ ] `zip`, `enumerate`, `sorted` with key functions

#### Weekly Coding Task
- [ ] Build a `@retry` decorator with exponential backoff
- [ ] Build an async script that fetches data from 5 URLs simultaneously and measures total time

---

### Week 3 — Python for Data (NumPy + Pandas)

**Focus:** Data manipulation — the backbone of every ML and pipeline project
**Best time for theory:** Morning (read docs/examples)
**Best time for coding:** Evening (work on real datasets)
**Resource:** Download any CSV dataset from Kaggle for hands-on practice

#### Topics to Cover

**NumPy**
- [ ] Arrays vs Python lists — why NumPy is faster
- [ ] Creating arrays — `zeros`, `ones`, `arange`, `linspace`, `random`
- [ ] Array operations — element-wise math, broadcasting rules
- [ ] Indexing and slicing — 1D, 2D, boolean indexing
- [ ] Reshaping — `reshape`, `flatten`, `transpose`
- [ ] Aggregations — `sum`, `mean`, `std`, `min`, `max` along axes
- [ ] `np.where` — conditional logic on arrays

**How to prepare NumPy:**
Do not just read. Open a Jupyter notebook. Create arrays and experiment. The key concept to nail is **broadcasting** — practice it with 3-4 examples until it feels natural.

**Pandas**
- [ ] Series and DataFrame — creation, indexing, `.loc` vs `.iloc`
- [ ] Reading data — `read_csv`, `read_json`, `read_sql`
- [ ] Inspecting data — `head`, `info`, `describe`, `value_counts`
- [ ] Filtering rows — boolean conditions, `.query()`
- [ ] Adding / modifying columns
- [ ] Handling missing data — `isna`, `fillna`, `dropna`
- [ ] `groupby` — split-apply-combine pattern
- [ ] `merge` and `join` — left, right, inner, outer
- [ ] `apply` — applying functions to rows/columns
- [ ] String operations — `.str.contains`, `.str.split`, `.str.lower`
- [ ] Datetime handling — `pd.to_datetime`, `.dt.year`, `.dt.month`

**How to prepare Pandas:**
Take a messy real-world CSV (sales data, employee data, anything). Clean it, transform it, answer 10 questions from it using only Pandas. This is more effective than any tutorial.

#### Weekly Coding Task
- [ ] Take a raw CSV with missing values, wrong types, duplicates — clean it fully with Pandas
- [ ] Answer 5 business questions from the cleaned data using groupby + aggregations

---

### Week 4 — SQL with Python + REST APIs + Project Build

**Focus:** Connecting Python to databases and external APIs, then building Month 1 project
**Best time:** Both theory and project work — use full evening + both weekend sessions
**Resource:** `SQL-Mastery` repo for SQL side

#### Topics to Cover

**SQL with Python**
- [ ] `psycopg2` — connecting to PostgreSQL, executing queries
- [ ] `SQLAlchemy Core` — SQL expression language basics
- [ ] Parameterized queries — never use string formatting for SQL (SQL injection)
- [ ] Transactions — `commit`, `rollback`
- [ ] Connection pooling basics

**How to prepare SQL+Python:**
Set up a local PostgreSQL (Docker: `docker run -e POSTGRES_PASSWORD=pass -p 5432:5432 postgres`). Write Python scripts that insert, query, update, delete. Make it real.

**REST APIs with Python**
- [ ] `requests` library — GET, POST, headers, auth, timeouts
- [ ] Parsing JSON responses
- [ ] Calling OpenAI API manually (without SDK) to understand the raw request
- [ ] Error handling for API calls — status codes, retries
- [ ] Rate limiting — `time.sleep`, token buckets

**Environment + Project Structure**
- [ ] Virtual environments — `venv`, `pip freeze > requirements.txt`
- [ ] Project folder structure for production Python
- [ ] `.gitignore` — never commit `.env` or `__pycache__`

#### Month 1 Project — AI-Powered Data Pipeline

**Build this over the weekend (6–8 hrs total):**

```
Project: ai-data-pipeline

What it does:
  1. Reads raw employee/sales CSV files from a /data folder
  2. Cleans and validates with Pandas (handle nulls, wrong types, duplicates)
  3. Sends each record to OpenAI API to auto-generate a category/tag
  4. Stores cleaned + tagged data in PostgreSQL
  5. Airflow DAG runs steps 1-4 every day at 8 AM automatically

Folder structure:
  ai-data-pipeline/
  ├── dags/pipeline_dag.py
  ├── src/cleaner.py
  ├── src/tagger.py
  ├── src/db.py
  ├── docker-compose.yml   (Airflow + PostgreSQL)
  ├── requirements.txt
  └── README.md
```

- [ ] Set up docker-compose with Airflow + PostgreSQL
- [ ] Write `cleaner.py` — Pandas cleaning logic
- [ ] Write `tagger.py` — OpenAI API call with retry decorator
- [ ] Write `db.py` — SQLAlchemy insert logic
- [ ] Write `pipeline_dag.py` — Airflow DAG connecting all steps
- [ ] Test end-to-end locally
- [ ] Write README with architecture diagram

---

## Month 2 — LLMs + RAG + Vector Databases

> **Goal:** Become the person in the room who actually understands how RAG works end-to-end. This is asked in every AI interview.

---

### Week 5 — How LLMs Actually Work

**Focus:** Conceptual understanding of transformers, embeddings, and how LLMs generate text
**Best time for theory:** Morning — these are dense concepts, fresh brain is essential
**Best time for coding:** Evening — experiment with APIs
**Resource:** `AI-ENGINEERS-ATLAS` → sections 04, 05, 06

#### Topics to Cover

**Transformers — Conceptual (not math)**
- [ ] What a token is — how text becomes numbers
- [ ] Attention mechanism — why it matters (intuition only, no matrix math needed)
- [ ] Encoder vs decoder vs encoder-decoder models
- [ ] What "parameters" in a model mean
- [ ] Context window — what it is, why it limits models
- [ ] Temperature, top-p, top-k — what they control in generation

**How to prepare transformers:**
Watch Andrej Karpathy's "Intro to LLMs" (1 hr YouTube video). Do not take notes during — watch fully first. Then write a 1-page summary in your own words. If you can explain it simply, you understand it.

**Embeddings**
- [ ] What embeddings are — numbers that represent meaning
- [ ] Why similar sentences have similar embedding vectors
- [ ] Cosine similarity — the formula and intuition
- [ ] Embedding dimensions — what 1536-dim means
- [ ] Using `text-embedding-ada-002` or `text-embedding-3-small` via API

**How to prepare embeddings:**
Write code that embeds 10 sentences and computes cosine similarity between them. See that "dog" and "puppy" are close, "dog" and "rocket" are far. This makes the concept concrete in 20 minutes.

**OpenAI / Anthropic API**
- [ ] `chat.completions.create` — messages array, roles (system/user/assistant)
- [ ] System prompt design — how to control model behavior
- [ ] `max_tokens`, `temperature` parameters
- [ ] Function calling / tool use — passing JSON schema to model
- [ ] Streaming responses — `stream=True`
- [ ] Token counting — `tiktoken` library
- [ ] Cost estimation — tokens in + tokens out × price per 1K

#### Weekly Coding Task
- [ ] Write a function that takes any text, embeds it, and finds the most similar item from a list
- [ ] Build a simple chatbot with conversation memory (keep last 10 messages in context)

---

### Week 6 — Prompt Engineering + HuggingFace

**Focus:** Getting the best outputs from LLMs, and using open-source models
**Resource:** `AI-ENGINEERS-ATLAS` → section 14

#### Topics to Cover

**Prompt Engineering**
- [ ] Zero-shot prompting — plain instruction
- [ ] Few-shot prompting — give examples in the prompt
- [ ] Chain-of-thought (CoT) — "think step by step"
- [ ] ReAct prompting — reason + act pattern
- [ ] Structured output prompting — forcing JSON/specific format
- [ ] Prompt templating — using variables in prompts
- [ ] System prompt best practices — persona, constraints, output format

**How to prepare prompt engineering:**
Take one task (e.g. classify customer complaints). Write 5 different prompts for the same task. Compare outputs. This hands-on experimentation is the only way to learn prompting.

**HuggingFace**
- [ ] `transformers` library — what it provides
- [ ] `pipeline()` — the quickest way to run a model
- [ ] Available pipelines — `text-generation`, `sentiment-analysis`, `summarization`, `ner`
- [ ] Loading a model + tokenizer manually
- [ ] Running inference on CPU vs GPU
- [ ] HuggingFace Hub — browsing and downloading models
- [ ] `datasets` library — loading standard datasets

**How to prepare HuggingFace:**
Run 3 different pipelines locally — sentiment analysis, summarization, and text generation. Use a small model (DistilBERT, GPT-2) so it runs on CPU. Understand input → tokenize → model → decode → output flow.

#### Weekly Coding Task
- [ ] Build a prompt template class with variable substitution + few-shot examples
- [ ] Run a HuggingFace summarization pipeline on 5 news articles

---

### Week 7 — Vector Databases + Embeddings Pipeline

**Focus:** The storage layer of every RAG system
**Resource:** `AI-ENGINEERS-ATLAS` → section 09

#### Topics to Cover

**Vector Database Concepts**
- [ ] Why regular databases can't do semantic search
- [ ] HNSW index — what Hierarchical Navigable Small World means (intuition)
- [ ] Approximate Nearest Neighbor (ANN) vs exact search — tradeoff
- [ ] Metadata filtering — filter by date/category + semantic search together
- [ ] Collections, distance metrics — cosine, dot product, euclidean — when to use which

**ChromaDB (local)**
- [ ] Install and set up ChromaDB
- [ ] Create a collection
- [ ] Add documents with embeddings + metadata
- [ ] Query by embedding — get top-k results
- [ ] Query with metadata filter
- [ ] Persist to disk vs in-memory mode

**How to prepare ChromaDB:**
Build a mini search engine. Add 20 sentences to ChromaDB. Query it with 5 different questions. Print the results with similarity scores. Understand why some results are good and some are not.

**Chunking Strategies**
- [ ] Why chunking is needed — context window limits
- [ ] Fixed-size chunking — simple but loses context at boundaries
- [ ] Recursive character text splitter — smarter boundary detection
- [ ] Semantic chunking — split by meaning change
- [ ] Chunk overlap — why 10–20% overlap improves retrieval
- [ ] Optimal chunk size — 256–512 tokens for most use cases

#### Weekly Coding Task
- [ ] Build a script that takes a 10-page PDF → chunks it 3 different ways → stores all in ChromaDB → queries the same question against all 3 → compare quality

---

### Week 8 — RAG Systems + LangChain + Project Build

**Focus:** Full RAG pipeline and Month 2 project
**Resource:** `AI-ENGINEERS-ATLAS` → section 10

#### Topics to Cover

**RAG Architecture**
- [ ] Indexing pipeline — load → split → embed → store
- [ ] Retrieval pipeline — query → embed → search → rerank → pass to LLM
- [ ] Generation — prompt with context + question → LLM → answer
- [ ] Naive RAG problems — why retrieved chunks may be irrelevant
- [ ] Reranking — using a cross-encoder to re-score retrieved chunks
- [ ] Hybrid search — BM25 (keyword) + dense (semantic) combined

**LangChain**
- [ ] `Document` and `DocumentLoader` — load from PDF, web, CSV
- [ ] `TextSplitter` — `RecursiveCharacterTextSplitter`
- [ ] `Embeddings` — OpenAI embeddings wrapper
- [ ] `VectorStore` — Chroma wrapper
- [ ] `RetrievalQA` chain — simplest RAG in 10 lines
- [ ] `ConversationalRetrievalChain` — RAG with conversation memory
- [ ] LCEL (LangChain Expression Language) — pipe operator `|`

**How to prepare LangChain:**
Build the same RAG system twice — once with raw code (no LangChain) and once with LangChain. Understanding what LangChain abstracts away makes you a much stronger engineer.

**RAG Evaluation**
- [ ] Faithfulness — does the answer come from the retrieved context?
- [ ] Answer relevance — does the answer address the question?
- [ ] Context relevance — was the right context retrieved?
- [ ] `RAGAS` library — automated RAG evaluation

#### Month 2 Project — Document Intelligence System

```
Project: rag-document-intelligence

What it does:
  1. Upload any PDF via a /upload endpoint
  2. Chunks + embeds into ChromaDB automatically
  3. POST /ask with a question → get answer + source citation
  4. Conversation memory — follow-up questions work correctly
  5. Dockerized — docker-compose up and it runs

Folder structure:
  rag-document-intelligence/
  ├── app/main.py            (FastAPI app)
  ├── app/ingestion.py       (load → chunk → embed → store)
  ├── app/retrieval.py       (query → retrieve → rerank)
  ├── app/generation.py      (context + question → LLM → answer)
  ├── app/models.py          (Pydantic schemas)
  ├── docker-compose.yml
  └── README.md
```

- [ ] Build ingestion pipeline (PDF → chunks → ChromaDB)
- [ ] Build retrieval + reranking logic
- [ ] Build generation with source citation
- [ ] Add conversation memory
- [ ] Wrap in FastAPI with `/upload` and `/ask` endpoints
- [ ] Dockerize with docker-compose
- [ ] Write README with architecture diagram

---

## Month 3 — AI Agents + Advanced Application Patterns

> **Goal:** Build agents that can reason, use tools, and complete multi-step tasks. This is where AI engineering gets interesting.

---

### Week 9 — Agent Fundamentals

**Focus:** How agents work, tool use, memory patterns
**Best time for theory:** Morning — agent concepts build on each other sequentially
**Resource:** `AI-ENGINEERS-ATLAS` → section 11

#### Topics to Cover

**What Makes an Agent**
- [ ] Difference between LLM call and an agent
- [ ] ReAct pattern — Reason → Act → Observe → Repeat
- [ ] Agent loop — when does it stop?
- [ ] Tool / function calling — how the LLM decides which tool to use
- [ ] Tool schema — writing JSON schemas for tools
- [ ] Parsing tool calls from LLM output

**How to prepare agents:**
Build a minimal agent from scratch using raw OpenAI function calling — no LangChain, no framework. Just the loop: call LLM → if tool call → execute tool → append result → call LLM again. This understanding is essential before using any framework.

**Memory Types**
- [ ] In-context memory — conversation history in the prompt
- [ ] External short-term — Redis, storing conversation by session ID
- [ ] External long-term — vector store, retrieve relevant past interactions
- [ ] Entity memory — tracking specific entities across conversations
- [ ] Summary memory — summarizing old messages to save tokens

**Tools to Build**
- [ ] Calculator tool — Python `eval` safely
- [ ] Web search tool — Tavily API or SerpAPI
- [ ] Python REPL tool — run code and return output
- [ ] Database query tool — natural language → SQL → execute → return results
- [ ] File read/write tool

#### Weekly Coding Task
- [ ] Build a raw agent loop from scratch (no LangChain) with 3 tools: calculator, web search, file writer
- [ ] Test it with: "Search the web for today's NVIDIA stock price, multiply by 100, and save to a file"

---

### Week 10 — LangChain Agents + LangGraph

**Focus:** Production-ready agent frameworks
**Resource:** `AI-ENGINEERS-ATLAS` → section 12

#### Topics to Cover

**LangChain Agents**
- [ ] `create_react_agent` — the standard React agent
- [ ] `AgentExecutor` — runs the agent loop
- [ ] `Tool` class — wrapping Python functions as tools
- [ ] `create_structured_chat_agent` — forces JSON outputs
- [ ] Streaming agent output — yield tokens as they come
- [ ] Agent with memory — `ConversationBufferMemory`

**LangGraph**
- [ ] Why LangGraph exists — LangChain agents are too linear
- [ ] Nodes, edges, and state — the graph model
- [ ] `StateGraph` — defining the workflow
- [ ] Conditional edges — branching logic
- [ ] Cycles in graphs — how agents loop using LangGraph
- [ ] Checkpointing — save and resume agent state
- [ ] Human-in-the-loop — pause for approval before action

**How to prepare LangGraph:**
LangGraph is the future of agents. Build a simple 3-node graph: `plan → execute → review`. Add a conditional edge that loops back to `plan` if the review fails. This teaches the core pattern used in production agents.

**MCP — Model Context Protocol**
- [ ] What MCP is — standardized way to give LLMs access to tools/resources
- [ ] MCP server vs MCP client
- [ ] Why it matters — enables any LLM to use any tool through one standard
- [ ] Basic MCP server in Python

**Resource:** `AI-ENGINEERS-ATLAS` → section 12

#### Weekly Coding Task
- [ ] Rebuild Week 9 raw agent using LangGraph
- [ ] Add human-in-the-loop: pause before any file write and ask for confirmation

---

### Week 11 — Multi-Agent Systems + Production Patterns

**Focus:** Orchestrating multiple agents, making agents production-ready

#### Topics to Cover

**Multi-Agent Architecture**
- [ ] Why multi-agent — specialization, parallelism, reliability
- [ ] Supervisor pattern — one orchestrator agent delegates to worker agents
- [ ] Pipeline pattern — agent A output feeds agent B
- [ ] Debate pattern — multiple agents argue, best answer wins
- [ ] Handoff pattern — agents pass control based on domain

**How to prepare multi-agent:**
Build a 3-agent system: `ResearchAgent` searches the web, `WriterAgent` writes content, `ReviewerAgent` critiques it. The supervisor decides which to call. Start simple — 3 agents with 2 tools each is enough to understand the pattern.

**Structured Outputs**
- [ ] Pydantic models for LLM output validation
- [ ] `model.with_structured_output()` in LangChain
- [ ] Retry on invalid output — automatic re-prompting
- [ ] Output parsers — JSON parser, list parser, datetime parser

**Production Agent Patterns**
- [ ] Cost tracking — count tokens per agent run, log to DB
- [ ] Timeout handling — kill agents that run too long
- [ ] Rate limit handling — exponential backoff for API calls
- [ ] Fallback strategies — if primary LLM fails, use backup
- [ ] Guardrails — block harmful inputs before they reach the agent
- [ ] Prompt injection defense — detecting attempts to hijack agent

#### Weekly Coding Task
- [ ] Add cost tracking to your Month 2 or 3 agent — log tokens + cost per run to PostgreSQL

---

### Week 12 — Month 3 Project Build

**Focus:** Full week on project — use both morning and evening sessions for this
**Best time:** All available sessions this week go to the project

#### Month 3 Project — AI Research Agent

```
Project: ai-research-agent

What it does:
  1. User POSTs a research topic to /research endpoint
  2. PlannerAgent breaks topic into 4–5 sub-questions
  3. ResearcherAgent searches web for each sub-question (parallel)
  4. SynthesizerAgent combines findings into structured report
  5. Report saved to PostgreSQL with full token usage audit
  6. Response streams back in real-time via SSE

Folder structure:
  ai-research-agent/
  ├── app/main.py              (FastAPI + SSE streaming)
  ├── agents/planner.py
  ├── agents/researcher.py
  ├── agents/synthesizer.py
  ├── tools/web_search.py
  ├── tools/content_extractor.py
  ├── db/models.py
  ├── docker-compose.yml
  └── README.md
```

- [ ] Build PlannerAgent — takes topic, outputs sub-questions
- [ ] Build ResearcherAgent — searches + extracts content per sub-question
- [ ] Run ResearcherAgents in parallel with `asyncio.gather`
- [ ] Build SynthesizerAgent — merges all research into report
- [ ] Add cost tracking to all agents
- [ ] FastAPI + streaming response endpoint
- [ ] Dockerize
- [ ] Write README with architecture diagram

---

## Month 4 — ML Engineering + MLOps

> **Goal:** Understand how models are trained, fine-tuned, tracked, and deployed. Not just API calls — real ML engineering.

---

### Week 13 — PyTorch + ML Fundamentals

**Focus:** How neural networks actually learn
**Best time for theory:** Morning — ML math concepts need focus
**Best time for coding:** Evening — implement what you read in the morning
**Resource:** `AI-ENGINEERS-ATLAS` → sections 03, 04

#### Topics to Cover

**PyTorch Basics**
- [ ] Tensors — creating, reshaping, operations
- [ ] Autograd — how gradients work, `requires_grad=True`
- [ ] `backward()` — computing gradients
- [ ] `torch.no_grad()` — inference mode
- [ ] GPU vs CPU — `.to('cuda')`, checking `torch.cuda.is_available()`
- [ ] DataLoader + Dataset — how to feed data to a model

**Neural Network Basics**
- [ ] `nn.Module` — base class for all models
- [ ] Linear layers, activation functions (ReLU, Sigmoid, Softmax)
- [ ] Loss functions — CrossEntropyLoss, MSELoss
- [ ] Optimizers — SGD, Adam, learning rate
- [ ] Training loop — forward pass → loss → backward → optimizer step
- [ ] Validation loop — evaluate without updating weights
- [ ] Overfitting, underfitting — how to spot them
- [ ] Dropout, BatchNorm — regularization basics

**How to prepare PyTorch:**
Build a binary classifier from scratch — no pre-built models. Dataset: any simple tabular dataset from sklearn. Define model → training loop → plot loss curve. If your loss goes down and accuracy goes up, you understand the fundamentals.

**ML Metrics**
- [ ] Accuracy, Precision, Recall, F1 — when each matters
- [ ] Confusion matrix — reading it correctly
- [ ] ROC-AUC — for binary classification
- [ ] Mean Absolute Error, RMSE — for regression

#### Weekly Coding Task
- [ ] Build a text sentiment classifier from scratch in PyTorch (no HuggingFace) — train/val/test split, plot learning curves, report all 4 metrics

---

### Week 14 — HuggingFace Fine-Tuning + MLflow

**Focus:** Fine-tuning LLMs and tracking experiments properly
**Resource:** `AI-ENGINEERS-ATLAS` → sections 07, 08

#### Topics to Cover

**Fine-Tuning Concepts**
- [ ] When to fine-tune vs RAG vs prompt engineering
- [ ] Full fine-tuning vs parameter-efficient fine-tuning (PEFT)
- [ ] LoRA — Low Rank Adaptation — what it actually does
- [ ] QLoRA — quantized LoRA for running on smaller GPUs
- [ ] What "rank" means in LoRA (r=4, r=8, r=16)
- [ ] When fine-tuning helps — style, tone, domain-specific formats
- [ ] When fine-tuning doesn't help — knowledge gaps (use RAG instead)

**How to prepare fine-tuning:**
Use Google Colab free GPU. Fine-tune `distilbert-base-uncased` on a small classification dataset (IMDB reviews, 2000 samples). The goal is to run through the pipeline once end-to-end, not to get perfect accuracy.

**HuggingFace `Trainer` API**
- [ ] `AutoTokenizer` + `AutoModelForSequenceClassification`
- [ ] `TrainingArguments` — key parameters: `num_train_epochs`, `learning_rate`, `per_device_train_batch_size`
- [ ] `Trainer` class — pass model, args, datasets, compute_metrics
- [ ] Saving + loading fine-tuned models
- [ ] `peft` library — applying LoRA to a model

**MLflow**
- [ ] What MLflow solves — tracking experiments so you can compare runs
- [ ] `mlflow.start_run()` — creating a run
- [ ] `mlflow.log_param()` — log hyperparameters
- [ ] `mlflow.log_metric()` — log accuracy, loss per epoch
- [ ] `mlflow.log_artifact()` — save model files, plots
- [ ] Model registry — promoting a model from staging to production
- [ ] MLflow UI — viewing and comparing runs in browser

**How to prepare MLflow:**
Run the same model training 3 times with different learning rates. Log everything to MLflow. Open the UI and compare the 3 runs side by side. This is the exact workflow used in production ML teams.

#### Weekly Coding Task
- [ ] Fine-tune DistilBERT on a custom dataset with 3 different LoRA ranks, track all in MLflow, pick the best one from the UI

---

### Week 15 — Model Serving + Docker for ML + Kubernetes for ML

**Focus:** Getting models into production
**Resource:** `Container-Engineering` repo

#### Topics to Cover

**Model Serving with FastAPI**
- [ ] Loading model once at startup — `@app.on_event("startup")`
- [ ] `/predict` endpoint — input validation with Pydantic, return predictions
- [ ] Batch predictions — accept list of inputs, return list of outputs
- [ ] Async endpoints for non-blocking inference
- [ ] Response time logging middleware
- [ ] Health check endpoint — `/health`

**Docker for ML Models**
- [ ] Multi-stage builds — build stage vs runtime stage (smaller final image)
- [ ] Caching pip install — copy requirements.txt first, then copy code
- [ ] Model files in Docker — COPY vs mount vs download at startup
- [ ] Memory limits — `--memory=4g` for containers
- [ ] GPU access in Docker — `--gpus all` flag
- [ ] `.dockerignore` — exclude model checkpoints, data folders from build context

**Kubernetes for ML**
- [ ] Deploying a model as a `Deployment` with replicas
- [ ] `ResourceRequirements` — CPU/memory requests and limits
- [ ] `HorizontalPodAutoscaler` (HPA) — scale up when CPU > 70%
- [ ] `ConfigMap` for environment variables
- [ ] `Secret` for API keys
- [ ] Readiness probe — K8s won't send traffic until model is loaded
- [ ] Liveness probe — K8s restarts pod if model becomes unhealthy

**How to prepare K8s for ML:**
Deploy your FastAPI model server to minikube. Add an HPA. Use `kubectl top pods` to watch CPU. Send 100 requests and watch it scale. Seeing auto-scaling work in real-time makes it memorable.

#### Weekly Coding Task
- [ ] Containerize your Week 14 fine-tuned model as a FastAPI service
- [ ] Deploy to minikube with HPA — test that it scales under load

---

### Week 16 — Airflow ML Pipelines + Monitoring + Project Build

**Focus:** Automating ML retraining + monitoring model health
**Resource:** `Airflow` repo, `observability-zero-to-hero` repo

#### Topics to Cover

**Airflow for ML Pipelines**
- [ ] ML pipeline as a DAG — fetch data → preprocess → train → evaluate → register
- [ ] `BranchPythonOperator` — only promote model if new accuracy > current
- [ ] `TriggerDagRunOperator` — trigger downstream serving pipeline
- [ ] Sensors — wait for new data to arrive before training
- [ ] `XCom` — passing model metrics between tasks
- [ ] Backfill — rerun training on historical data

**Model Monitoring**
- [ ] Data drift — input distribution changes over time
- [ ] Concept drift — model accuracy degrades over time
- [ ] `evidently` library — automated drift detection reports
- [ ] Prediction logging — log every prediction to a database
- [ ] Prometheus custom metrics — `model_prediction_confidence` histogram
- [ ] Grafana alert — alert when average confidence drops below threshold

**How to prepare monitoring:**
Set up a Prometheus counter for your prediction endpoint. Every call increments it. Open Grafana and create a dashboard showing requests/sec and average latency. This is a 2-hr setup that looks very impressive in interviews.

#### Month 4 Project — End-to-End ML Pipeline

```
Project: ml-ops-pipeline

What it does:
  1. Fine-tunes DistilBERT for text classification on a custom dataset
  2. MLflow tracks all experiments, registers best model
  3. Airflow DAG: fetch new data weekly → retrain → evaluate →
     promote to production if accuracy improves → redeploy
  4. FastAPI serves the production model at /predict
  5. Kubernetes deployment with HPA auto-scaling
  6. Grafana dashboard: request rate, latency, prediction confidence

Folder structure:
  ml-ops-pipeline/
  ├── training/train.py          (HuggingFace + LoRA + MLflow)
  ├── serving/app.py             (FastAPI prediction service)
  ├── dags/retrain_dag.py        (Airflow retraining pipeline)
  ├── monitoring/dashboard.json  (Grafana dashboard export)
  ├── k8s/deployment.yaml
  ├── k8s/hpa.yaml
  ├── docker-compose.yml
  └── README.md
```

- [ ] Training script with MLflow logging
- [ ] Airflow DAG for automated retraining
- [ ] FastAPI prediction service
- [ ] Docker + K8s deployment manifests
- [ ] Prometheus metrics in FastAPI
- [ ] Grafana dashboard
- [ ] README with full architecture diagram

---

## Month 5 — Production + System Design + Interview Prep

> **Goal:** Deploy real systems on AWS. Master AI system design. Get hired.

---

### Week 17 — AWS for AI + CI/CD

**Focus:** Cloud deployment for production AI systems
**Resource:** `Linux-Terraform-AWS-Mastery` → sections 03, 04

#### Topics to Cover

**AWS Services for AI**
- [ ] S3 — store datasets, model checkpoints, artifacts
- [ ] ECR — Elastic Container Registry, push Docker images
- [ ] ECS Fargate — run containers without managing servers
- [ ] EC2 + Auto Scaling Group — for heavier GPU workloads
- [ ] RDS — managed PostgreSQL for metadata/predictions storage
- [ ] SageMaker basics — managed training and hosting (conceptual)
- [ ] Bedrock — AWS managed LLM API (Claude, Llama, etc.)
- [ ] CloudWatch — logs, metrics, alarms

**How to prepare AWS:**
Deploy your Month 2 RAG project to ECS Fargate. The steps are: build image → push to ECR → create ECS task definition → create service → add load balancer. The first time takes 3 hours. The second time takes 30 minutes.

**Terraform for AI Infrastructure**
- [ ] `aws_ecr_repository` — create ECR registry
- [ ] `aws_ecs_cluster` + `aws_ecs_service` — deploy containerized model
- [ ] `aws_s3_bucket` — model artifact storage
- [ ] `aws_rds_instance` — PostgreSQL for predictions
- [ ] Variables + outputs — reusable infrastructure code

**CI/CD for AI with GitHub Actions**
- [ ] Workflow trigger on push to `main`
- [ ] Steps: run tests → build Docker image → push to ECR → deploy to ECS
- [ ] Secrets management — AWS credentials in GitHub Secrets
- [ ] Model validation step — run eval before deployment, fail if accuracy drops

#### Weekly Coding Task
- [ ] Deploy Month 2 RAG project to AWS ECS using Terraform
- [ ] Add GitHub Actions CI/CD so every push to main auto-deploys

---

### Week 18 — Production Hardening + Month 5 Project

**Focus:** Making your best project production-grade with a live URL

#### Topics to Cover

**Production Best Practices**
- [ ] Environment separation — dev / staging / prod configs
- [ ] Secrets management — AWS Secrets Manager or Parameter Store
- [ ] Database migrations — Alembic for SQLAlchemy
- [ ] API versioning — `/v1/`, `/v2/` endpoints
- [ ] Request validation + rate limiting — `slowapi` for FastAPI
- [ ] CORS configuration
- [ ] Health check + readiness endpoints
- [ ] Graceful shutdown — handle SIGTERM to finish in-flight requests

**Cost Optimization**
- [ ] Model quantization — INT8/INT4 for faster, cheaper inference
- [ ] Caching frequent queries — Redis cache in front of LLM calls
- [ ] Spot instances — 70% cheaper than on-demand for training
- [ ] Auto-scaling to zero — scale ECS to 0 when no traffic

#### Month 5 Project — Production AI Platform

```
Project: production-ai-platform

What it does:
  Takes your best project (RAG or ML pipeline) and makes it
  fully production-grade with a live public URL.

  1. Deployed on AWS ECS with auto-scaling
  2. Terraform provisions all infrastructure
  3. GitHub Actions: push to main = tests → build → deploy
  4. Redis caches repeated LLM queries (saves cost)
  5. CloudWatch + Grafana monitors everything
  6. Public URL in resume and GitHub README

Stack: AWS ECS · Terraform · GitHub Actions · Redis · CloudWatch · Grafana
```

- [ ] Terraform all infrastructure (ECS, RDS, S3, ECR, ALB)
- [ ] GitHub Actions CI/CD pipeline
- [ ] Redis caching layer for LLM responses
- [ ] CloudWatch alarms for errors + latency
- [ ] Grafana dashboard connected to CloudWatch
- [ ] README with live URL, architecture diagram, setup guide

---

### Week 19 — AI System Design Mastery

**Focus:** The most important skill for 18LPA+ interviews
**Best time:** Evening — system design needs 90-min uninterrupted blocks
**How to prepare:** For each problem below — first try to design it yourself (30 min), then study the solution, then explain it out loud as if in an interview

#### System Design Problems to Master

**RAG Systems**
- [ ] Design a document Q&A system for 10 million PDFs
  - How do you handle indexing at scale? (batch embedding pipeline)
  - How do you handle updates when documents change?
  - How do you handle multi-tenancy (different users, different docs)?
  - How do you keep latency under 2 seconds?

**LLM Applications**
- [ ] Design a customer support AI that handles 10,000 conversations/day
  - When to use RAG vs fine-tuning vs plain prompting?
  - How do you handle escalation to human agents?
  - How do you prevent prompt injection from customers?
  - How do you monitor for quality degradation?

**ML Systems**
- [ ] Design an ML platform for training + serving 50 models
  - How do you manage model versions?
  - How do you handle A/B testing between model versions?
  - How do you detect and handle data drift?
  - How do you handle a model that suddenly starts failing?

**Agent Systems**
- [ ] Design a multi-agent coding assistant
  - How do you give agents access to code repositories safely?
  - How do you prevent agents from running dangerous code?
  - How do you maintain context across long coding sessions?

---

### Week 20 — DSA + Behavioral + Final Polish

**Focus:** Enough DSA to pass screening rounds + behavioral storytelling
**Resource:** `Python-DSA-API-Mastery` → DSA track

#### DSA Topics (Minimum Required for AI Engineer Roles)

**Must Know — High Frequency**
- [ ] Arrays — two pointers, sliding window
- [ ] Strings — reversal, palindrome, anagram
- [ ] HashMap — frequency counter, two sum pattern
- [ ] Linked List — reverse, detect cycle, merge two sorted
- [ ] Binary Search — find element, first/last position

**Should Know — Medium Frequency**
- [ ] Trees — BFS, DFS, level order traversal
- [ ] Graphs — BFS shortest path, DFS connected components
- [ ] Stack — valid parentheses, next greater element
- [ ] Queue — sliding window maximum

**Skip for Now**
- Dynamic programming (unless asked specifically)
- Segment trees, tries, advanced graph algorithms

**How to prepare DSA:**
Do 2 LeetCode problems per day — one Easy, one Medium. Time yourself: Easy should take under 15 min, Medium under 30 min. Focus on patterns, not memorization.

#### DSA Daily Tracker

- [ ] Day 1 — Two Sum · Valid Parentheses
- [ ] Day 2 — Best Time to Buy Stock · Longest Substring Without Repeat
- [ ] Day 3 — Merge Two Sorted Lists · Binary Search
- [ ] Day 4 — Maximum Subarray · Reverse Linked List
- [ ] Day 5 — Contains Duplicate · Number of Islands
- [ ] Day 6 — Valid Anagram · Climbing Stairs
- [ ] Day 7 — Product of Array Except Self · LRU Cache
- [ ] Day 8 — Top K Frequent Elements · Validate BST
- [ ] Day 9 — Course Schedule (graphs) · Word Search
- [ ] Day 10 — Merge K Sorted Lists · Serialize Binary Tree

#### Behavioral Prep

For every project you built, prepare this exact structure:

```
Situation: What problem were you solving?
Task:      What was your specific responsibility?
Action:    What did you build? What decisions did you make and why?
Result:    What was the outcome? What would you do differently?
```

- [ ] Prep STAR story for Month 1 project (data pipeline)
- [ ] Prep STAR story for Month 2 project (RAG system)
- [ ] Prep STAR story for Month 3 project (AI agent)
- [ ] Prep STAR story for Month 4 project (ML pipeline)
- [ ] Prep answer for: "Tell me about a time you had to learn something fast"
- [ ] Prep answer for: "Tell me about a technical decision you made that you later questioned"

---

## Interview Readiness Checklist

Check these off only when you can answer without looking anything up:

**LLM & RAG**
- [ ] Explain chunking strategies and when to use each
- [ ] What is embedding? How does cosine similarity work?
- [ ] What is RAG? Walk through the full pipeline
- [ ] What is reranking? Why does it improve RAG?
- [ ] How do you evaluate RAG quality?

**Agents**
- [ ] What is the ReAct pattern?
- [ ] How does function/tool calling work at the API level?
- [ ] What is LangGraph? How is it different from LangChain agents?
- [ ] What is MCP and why does it matter?
- [ ] How do you handle agents that loop forever?

**ML Engineering**
- [ ] What is LoRA? What does "rank" mean?
- [ ] When do you fine-tune vs use RAG?
- [ ] Explain the ML training loop step by step
- [ ] What is data drift? How do you detect it?
- [ ] How do you do A/B testing for models?

**System Design**
- [ ] Design a RAG system for 1M documents
- [ ] Design a multi-agent customer support system
- [ ] How would you reduce LLM API costs by 50%?
- [ ] How would you handle 10x traffic spike on a model serving endpoint?

**Production**
- [ ] How does your CI/CD pipeline work?
- [ ] How do you manage secrets in production?
- [ ] How do you monitor an LLM application?
- [ ] Walk me through your AWS deployment architecture

---

## Salary Expectation by Month

| Month | Level | Expected Range |
|-------|-------|---------------|
| End of Month 1 | Python-strong, entry AI | 6–8 LPA |
| End of Month 2 | Junior AI Developer | 10–14 LPA |
| End of Month 3 | Mid-Level AI Developer | 14–18 LPA |
| End of Month 4 | Mid-Senior AI Engineer | 16–22 LPA |
| End of Month 5 | Senior AI Engineer | 20–28 LPA |

---

## Resource Map — Your Own Repos

| Topic | Repo | Section |
|-------|------|---------|
| Python | `Python-DSA-API-Mastery` | `python-complete-mastery` |
| DSA | `Python-DSA-API-Mastery` | DSA track |
| FastAPI | `Python-DSA-API-Mastery` | `api-mastery` |
| SQL | `SQL-Mastery` | All sections |
| ML / Neural Networks | `AI-ENGINEERS-ATLAS` | Sections 03, 04 |
| LLMs / Transformers | `AI-ENGINEERS-ATLAS` | Sections 05, 06, 07 |
| RAG | `AI-ENGINEERS-ATLAS` | Sections 09, 10 |
| Agents / MCP | `AI-ENGINEERS-ATLAS` | Sections 11, 12 |
| HuggingFace | `AI-ENGINEERS-ATLAS` | Section 14 |
| Docker | `Container-Engineering` | Section 01 |
| Kubernetes | `Container-Engineering` | Section 02 |
| Linux / Bash | `Linux-Terraform-AWS-Mastery` | Sections 01, 02 |
| AWS | `Linux-Terraform-AWS-Mastery` | Section 03 |
| Terraform | `Linux-Terraform-AWS-Mastery` | Section 04 |
| Airflow | `Airflow` | All sections |
| Monitoring | `observability-zero-to-hero` | All sections |

---

## One Rule

> Every day — even 30 minutes of coding beats 2 hours of watching tutorials.
> The projects are the resume. The projects are the interview. Build first, read second.
