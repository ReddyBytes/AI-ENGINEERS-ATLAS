# Master Learning Path — All Repos

> A complete, step-by-step roadmap covering every repo in this folder.
> Targeted at: **Senior AI/ML/Backend Engineer — 20–30 LPA (4–5 years experience)**
> Total time: **5–6 months full-time | 9–12 months part-time**

---

## Repo Map

| Repo | What It Covers | When to Use |
|---|---|---|
| `Python-DSA-API-Mastery` | Python · DSA · APIs · System Design | Phases 1, 3, 5, 8 |
| `AI-ENGINEERS-ATLAS` | Math · ML · DL · LLMs · RAG · Agents · Production AI | Phases 2, 4, 6, 7 |
| `SQL-Mastery` | SQL fundamentals to production | Phase 3 |
| `Linux-Terraform-AWS-Mastery` | Linux · Bash · AWS · Terraform | Phase 9 |
| `Container-Engineering` | Docker · Kubernetes | Phase 9 |
| `observability-zero-to-hero` | Prometheus · Grafana · EFK · Jaeger · OTEL | Phase 10 |
| `Airflow` | Pipeline orchestration — beginner to cloud | Phase 10 |
| `linux-guide` | Linux quick reference | Ongoing reference |
| `devmastery` | AI Engineer career roadmap | Read at start — also available locally as `AI_ENGINEER_ROADMAP.md` |

---

## Before You Begin — Read These First

```
AI_ENGINEER_ROADMAP.md                            ← understand the destination (local copy)
Python-DSA-API-Mastery/QUICK_START.md          ← understand the Python repo structure
Python-DSA-API-Mastery/DAILY_JOB_GUIDE.md      ← understand what skills matter at work
00_Learning_Guide/How_to_Use_This_Repo.md
00_Learning_Guide/Learning_Path.md
```

---

## How to Use This Path

- **Reading order per module:** `theory.md` → `practice.py / Code_Example.md` → `cheatsheet.md` → `interview.md`
- **Do not skip practice files** — reading alone gives 30% retention, coding gives 90%
- **Mark progress** using `AI-ENGINEERS-ATLAS/00_Learning_Guide/Progress_Tracker.md`
- Each phase has a **target level** — if you already know it, skim the cheatsheet and move on

---

## Phase Overview

| Phase | Topic | Repo | Duration | Target Level |
|---|---|---|---|---|
| 1 | Python Core to Advanced | Python-DSA-API | 3 weeks | Gets you interview-ready on Python |
| 2 | Math + ML Foundations | AI-ENGINEERS-ATLAS | 3 weeks | Understand what the models are doing |
| 3 | SQL — Fundamentals to Production | SQL-Mastery | 2 weeks | Write production queries confidently |
| 4 | Deep Learning + NLP | AI-ENGINEERS-ATLAS | 3 weeks | Build and explain neural nets |
| 5 | APIs — REST to Production | Python-DSA-API | 3 weeks | Build and deploy real APIs |
| 6 | Transformers + LLMs + Prompt Engineering | AI-ENGINEERS-ATLAS | 3 weeks | Work fluently with LLMs |
| 7 | RAG Systems + AI Agents | AI-ENGINEERS-ATLAS | 4 weeks | Build production RAG + agent systems |
| 8 | Production AI + System Design | AI-ENGINEERS-ATLAS + Python-DSA-API | 4 weeks | Design scalable AI systems |
| 9 | Linux + AWS + Terraform + Docker + K8s | Linux-Terraform + Container | 3 weeks | Deploy and manage infrastructure |
| 10 | Observability + Airflow (Data Pipelines) | Observability + Airflow | 2 weeks | Operate production data systems |
| 11 | DSA + Interview Preparation | Python-DSA-API | 4 weeks | Crack coding + design interviews |
| 12 | Advanced AI Topics + Claude APIs | AI-ENGINEERS-ATLAS | 2 weeks | Stand out with cutting-edge skills |

---

---

# PHASE 1 — Python Core to Advanced

**Duration:** 3 weeks
**Repo:** `Python-DSA-API-Mastery/python-complete-mastery/`
**Goal:** Write clean, production-grade Python confidently

### Week 1 — Core Python

| Module | Folder | What You Learn |
|---|---|---|
| Python Fundamentals | `01_python_fundamentals/` | Variables, memory model, name binding, mutability |
| Control Flow | `02_control_flow/` | Loops, comprehensions, loop-else, walrus operator |
| Data Types | `03_data_types/` | Lists, dicts, sets, tuples — internals and performance |
| Functions | `04_functions/` | *args, **kwargs, closures, LEGB scope, mutable defaults trap |
| OOP | `05_oops/` | Classes, inheritance, super(), dunder methods, MRO |
| Exceptions | `06_exceptions_error_handling/` | try/except/else/finally, custom exceptions, re-raising |

### Week 2 — Intermediate Python

| Module | Folder | What You Learn |
|---|---|---|
| Modules & Packages | `07_modules_packages/` | Import system, __init__.py, __all__, importlib |
| File Handling | `08_file_handling/` | pathlib, CSV, JSON, binary, atomic writes |
| Logging & Debugging | `09_logging_debugging/` | Production logging setup, handlers, formatters, pdb |
| Decorators | `10_decorators/` | @wraps, stacked, class decorators, parametrized |
| Generators | `11_generators_iterators/` | yield, send(), pipelines, memory efficiency |
| Context Managers | `12_context_managers/` | __enter__/__exit__, contextlib, ExitStack |

### Week 3 — Advanced Python

| Module | Folder | What You Learn |
|---|---|---|
| Concurrency | `13_concurrency/` | GIL, threading, multiprocessing, asyncio, executors |
| Type Hints & Pydantic | `14_type_hints_and_pydantic/` | Annotations, Pydantic models, runtime validation |
| Advanced Python | `15_advanced_python/` | Metaclasses, descriptors, protocols, __slots__ |
| Design Patterns | `16_design_patterns/` | Singleton, Factory, Observer, Strategy |
| Testing | `17_testing/` | pytest, fixtures, Mock, parametrize, TDD |
| Memory Management | `01.1_memory_management/` | Reference counting, GC, slots, profiling |

### Phase 1 Interview Prep
```
99_interview_master/python_0_2_years.md
99_interview_master/tricky_edge_cases.md
```

### Phase 1 Practice Projects
```
00_Capstone_Projects/02_Data_Pipeline_CLI/     ← uses everything from Phase 1
```

---

---

# PHASE 2 — Math + Machine Learning Foundations

**Duration:** 3 weeks
**Repo:** `AI-ENGINEERS-ATLAS/`
**Goal:** Understand the math behind ML — explain models in interviews, not just use them

### Week 1 — Math for AI

| Section | Folder | Topics |
|---|---|---|
| Probability | `01_Math_for_AI/01_Probability/` | Bayes theorem, distributions, conditional probability |
| Statistics | `01_Math_for_AI/02_Statistics/` | Hypothesis testing, p-values, confidence intervals |
| Linear Algebra | `01_Math_for_AI/03_Linear_Algebra/` | Vectors, matrices, eigenvalues, SVD |
| Calculus | `01_Math_for_AI/04_Calculus_and_Optimization/` | Derivatives, chain rule, gradient descent |
| Information Theory | `01_Math_for_AI/05_Information_Theory/` | Entropy, cross-entropy, KL divergence |

### Week 2 — ML Foundations

| Topic | Folder | Why It Matters |
|---|---|---|
| What is ML | `02_ML_Foundations/01_What_is_ML/` | Get the mental model right |
| Supervised vs Unsupervised | `02_.../03_Supervised_Learning/` + `04_Unsupervised/` | Foundation for everything |
| Model Evaluation | `02_.../05_Model_Evaluation/` | Precision, recall, AUC — asked in every interview |
| Overfitting & Regularization | `02_.../06_Overfitting_and_Regularization/` | Bias-variance tradeoff |
| Gradient Descent | `02_.../08_Gradient_Descent/` | Understand how models actually learn |
| Feature Engineering | `02_.../07_Feature_Engineering/` | Encoding, scaling, selection |

### Week 3 — Classical ML Algorithms

| Algorithm | Folder | Interview Weight |
|---|---|---|
| Linear + Logistic Regression | `03_.../01_Linear_Regression/` + `02_Logistic/` | ⭐⭐⭐ Very high |
| Decision Trees + Random Forests | `03_.../03_Decision_Trees/` + `04_Random_Forests/` | ⭐⭐⭐ Very high |
| SVM | `03_.../05_SVM/` | ⭐⭐ High |
| XGBoost & Boosting | `03_.../09_XGBoost_and_Boosting/` | ⭐⭐⭐ Very high (industry standard) |
| K-Means + PCA | `03_.../06_K_Means/` + `07_PCA/` | ⭐⭐ High |
| Time Series | `03_.../10_Time_Series_Analysis/` | ⭐⭐ High (finance/e-commerce roles) |
| Recommendation Systems | `03_.../11_Recommendation_Systems/` | ⭐⭐ High |
| Anomaly Detection | `03_.../12_Anomaly_Detection/` | ⭐⭐ Medium-High |

**Must read:**
```
03_Classical_ML_Algorithms/Algorithm_Comparison.md     ← when to use which algorithm
```

### Phase 2 + Data Science Track (Python repo)
Run in parallel with Phase 2:
```
python-complete-mastery/22_numpy_for_ai/
python-complete-mastery/23_pandas_for_ai/
python-complete-mastery/26_statistics_and_probability/
python-complete-mastery/27_matplotlib_seaborn/
python-complete-mastery/28_eda_workflow/
```

---

---

# PHASE 3 — SQL Fundamentals to Production

**Duration:** 2 weeks
**Repo:** `SQL-Mastery/`
**Goal:** Write complex queries, optimize performance, design schemas

### Week 1 — Core SQL

| Module | Folder | Topics |
|---|---|---|
| Fundamentals | `01_fundamentals/` | SELECT, WHERE, ORDER BY, DISTINCT, LIMIT |
| Querying Basics | `02_querying_basics/` | Filtering, sorting, NULL handling |
| Aggregation | `03_aggregation/` | GROUP BY, HAVING, COUNT/SUM/AVG, window functions |
| Schema Design | `04_schema_design/` | Normalization, data types, constraints, indexes |
| Joins | `05_joins/` | INNER, LEFT, RIGHT, OUTER, self-joins, join patterns |

### Week 2 — Advanced SQL + Production

| Module | Folder | Topics |
|---|---|---|
| Advanced Queries | `06_advanced_queries/` | CTEs, subqueries, CASE, string/date functions |
| Data Modification | `07_data_modification/` | INSERT, UPDATE, DELETE, transactions, ACID |
| Performance | `08_performance/` | EXPLAIN ANALYZE, index strategy, query optimization |
| Real World | `09_real_world/` | Views, stored procedures, triggers, SQL with Python |

**Also cover from Python repo:**
```
python-complete-mastery/30_sql_with_python/     ← SQLAlchemy ORM + psycopg2
```

### Phase 3 Interview Prep
```
SQL-Mastery/99_interview_master/               ← 26 Q&As + 25 scenario questions
```

---

---

# PHASE 4 — Deep Learning + NLP

**Duration:** 3 weeks
**Repo:** `AI-ENGINEERS-ATLAS/`
**Goal:** Build and explain neural networks — ANN, CNN, RNN, LSTM, NLP pipeline

### Week 1 — Neural Network Foundations

| Topic | Folder | Focus |
|---|---|---|
| Perceptron | `04_.../01_Perceptron/` | Biological → mathematical model |
| MLPs | `04_.../02_MLPs/` | Hidden layers, universal approximation theorem |
| Activation Functions | `04_.../03_Activation_Functions/` | Sigmoid, ReLU, GELU — why each exists |
| Forward Propagation | `04_.../05_Forward_Propagation/` | Full matrix math walkthrough |
| Backpropagation | `04_.../06_Backpropagation/` | Chain rule, gradient flow — must understand deeply |
| Optimizers | `04_.../07_Optimizers/` | SGD → Adam — Comparison.md is essential |

### Week 2 — Deep Learning Architectures

| Topic | Folder | Focus |
|---|---|---|
| Regularization | `04_.../08_Regularization/` | Dropout, batch norm, weight decay |
| CNNs | `04_.../09_CNNs/` | Convolutions, pooling, ResNet — Architecture_Deep_Dive.md |
| RNNs + LSTMs | `04_.../10_RNNs/` | Sequential data, vanishing gradient fix |
| Training Techniques | `04_.../12_Training_Techniques/` | Transfer learning, mixed precision |

### Week 3 — NLP Foundations

| Topic | Folder | Focus |
|---|---|---|
| Text Preprocessing | `05_.../01_Text_Preprocessing/` | Cleaning, stemming, lemmatization |
| Tokenization | `05_.../02_Tokenization/` | BPE, sentencepiece — critical for LLM understanding |
| TF-IDF + Bag of Words | `05_.../03_Bag_of_Words_and_TF_IDF/` | Sparse representations |
| Word Embeddings | `05_.../04_Word_Embeddings/` | Word2Vec, GloVe, FastText |
| Semantic Similarity | `05_.../05_Semantic_Similarity/` | Cosine similarity, nearest neighbor |

**Also cover from Python repo:**
```
python-complete-mastery/25_python_ai_ecosystem/    ← ML library overview
python-complete-mastery/29_web_scraping/           ← data collection
```

---

---

# PHASE 5 — APIs — REST to Production

**Duration:** 3 weeks
**Repo:** `Python-DSA-API-Mastery/api-mastery/`
**Goal:** Build, secure, test, and deploy production-grade APIs

### Week 1 — REST Foundations + FastAPI

| Module | Folder | Topics |
|---|---|---|
| What is an API | `01_what_is_an_api/` | HTTP fundamentals, request/response anatomy |
| REST Fundamentals | `02_rest_fundamentals/` | 6 constraints, statelessness, idempotency |
| REST Best Practices | `03_rest_best_practices/` | URL naming, pagination, error formats |
| Data Formats | `04_data_formats/` | JSON, Pydantic validation, serialization |
| Authentication | `05_authentication/` | API keys, JWT, OAuth2, CORS |
| Error Handling | `06_error_handling_standards/` | RFC 7807, validation errors, retry logic |
| FastAPI | `07_fastapi/` | Routes, dependency injection, background tasks, WebSockets |

### Week 2 — API Advanced Patterns

| Module | Folder | Topics |
|---|---|---|
| Versioning | `08_versioning_standards/` | URL vs header versioning, breaking changes |
| Performance | `09_api_performance_scaling/` | N+1 problem, connection pooling, caching |
| Testing | `10_testing_documentation/` | TestClient, pytest fixtures, OpenAPI |
| Security | `11_api_security_production/` | OWASP Top 10, input validation, rate limiting |
| Deployment | `12_production_deployment/` | Docker + Gunicorn/Uvicorn, K8s, CI/CD |

### Week 3 — Advanced API Protocols

| Module | Folder | Topics |
|---|---|---|
| GraphQL | `13_graphql/` | Schema-first design, mutations, DataLoader |
| gRPC | `14_grpc/` | Protocol Buffers, streaming modes |
| API Gateway | `15_api_gateway/` | Rate limiting, BFF pattern |
| Design Patterns | `16_api_design_patterns/` | Idempotency, long-running ops, bulk operations |
| WebSockets | `17_websockets/` | Full-duplex, broadcast, reconnection |
| OpenTelemetry | `19_opentelemetry/` | Traces, metrics, OTEL collector |

### Phase 5 Capstone
```
00_Capstone_Projects/01_Ecommerce_API_FastAPI/     ← full production FastAPI project
```

### Phase 5 Interview Prep
```
api-mastery/99_interview_master/api_questions.md
api-mastery/99_interview_master/scenario_based_questions.md    ← 12 production scenarios
```

---

---

# PHASE 6 — Transformers + LLMs + Prompt Engineering

**Duration:** 3 weeks
**Repo:** `AI-ENGINEERS-ATLAS/`
**Goal:** Understand how LLMs work from architecture to API usage

### Week 1 — Transformer Architecture

| Topic | Folder | Must Read |
|---|---|---|
| Before Transformers | `06_.../01_Sequence_Models_Before_Transformers/` | Why RNNs failed |
| Attention Mechanism | `06_.../02_Attention_Mechanism/` | Visual_Guide.md + Math_Intuition.md |
| Self-Attention | `06_.../03_Self_Attention/` | How tokens attend to each other |
| Multi-Head Attention | `06_.../04_Multi_Head_Attention/` | Architecture_Deep_Dive.md — the core insight |
| Positional Encoding | `06_.../05_Positional_Encoding/` | RoPE vs sinusoidal |
| Full Architecture | `06_.../06_Transformer_Architecture/` | Encoder-decoder, layer norm, residuals |
| BERT vs GPT | `06_.../08_BERT/` + `09_GPT/` | Bidirectional vs autoregressive |

### Week 2 — LLM Internals

| Topic | Folder | Must Read |
|---|---|---|
| LLM Fundamentals | `07_.../01_LLM_Fundamentals/` | Scale, emergence, History_Timeline.md |
| Text Generation | `07_.../02_How_LLMs_Generate_Text/` | Temperature, top-p, top-k — Visual_Guide.md |
| Pretraining | `07_.../03_Pretraining/` | Data curation, scaling laws, Chinchilla |
| RLHF | `07_.../06_RLHF/` | Reward models, PPO, DPO — Architecture_Deep_Dive.md |
| Hallucination | `07_.../08_Hallucination_and_Alignment/` | Detection and mitigation |
| Ollama & Local LLMs | `07_.../10_Ollama_Local_LLMs/` | Run models locally, REST API |
| Reasoning Models | `07_.../11_Reasoning_Models/` | Chain-of-thought, o1/Claude extended thinking |

### Week 3 — LLM Applications + Prompt Engineering

| Topic | Folder | Must Read |
|---|---|---|
| Prompt Engineering | `08_.../01_Prompt_Engineering/` | Patterns.md + Common_Mistakes.md |
| Tool Calling | `08_.../02_Tool_Calling/` | Architecture_Deep_Dive.md + Code_Example.md |
| Structured Outputs | `08_.../03_Structured_Outputs/` | JSON mode, extraction pipelines |
| Embeddings | `08_.../04_Embeddings/` | Embedding models, batching |
| Vector Databases | `08_.../05_Vector_Databases/` | Pinecone, pgvector, FAISS — Comparison.md |
| Semantic Search | `08_.../06_Semantic_Search/` | Dense retrieval, re-ranking |

---

---

# PHASE 7 — RAG Systems + AI Agents

**Duration:** 4 weeks
**Repo:** `AI-ENGINEERS-ATLAS/`
**Goal:** Build production-grade RAG and agentic AI systems — the most hired skill in 2025–26

### Week 1 — RAG Fundamentals + Pipeline

| Topic | Folder | Focus |
|---|---|---|
| RAG Fundamentals | `09_.../01_RAG_Fundamentals/` | Why RAG, architecture overview |
| Document Ingestion | `09_.../02_Document_Ingestion/` | PDF, HTML, metadata extraction |
| Chunking Strategies | `09_.../03_Chunking_Strategies/` | Fixed vs recursive vs semantic — Comparison.md |
| Embedding & Indexing | `09_.../04_Embedding_and_Indexing/` | HNSW, IVF, indexing pipelines |
| Retrieval Pipeline | `09_.../05_Retrieval_Pipeline/` | Top-k, MMR, re-ranking, hybrid search |

### Week 2 — Advanced RAG + Build Project

| Topic | Folder | Focus |
|---|---|---|
| Context Assembly | `09_.../06_Context_Assembly/` | Prompt construction, deduplication |
| Advanced RAG | `09_.../07_Advanced_RAG_Techniques/` | HyDE, RAPTOR, multi-hop — Architecture_Deep_Dive.md |
| RAG Evaluation | `09_.../08_RAG_Evaluation/` | RAGAS, faithfulness, Evaluation_at_Scale.md |
| GraphRAG | `09_.../10_GraphRAG/` | Entity extraction, knowledge graphs |
| CAG | `09_.../11_CAG_Cache_Augmented_Generation/` | KV cache reuse, prompt caching API |
| Build a RAG App | `09_.../09_Build_a_RAG_App/` | Full end-to-end project |

### Week 3 — AI Agents

| Topic | Folder | Focus |
|---|---|---|
| Agent Fundamentals | `10_.../01_Agent_Fundamentals/` | Perception → reasoning → action loop |
| ReAct Pattern | `10_.../02_ReAct_Pattern/` | Thought/Action/Observation — Architecture_Deep_Dive.md |
| Tool Use | `10_.../03_Tool_Use/` | Schemas, execution, error recovery |
| Agent Memory | `10_.../04_Agent_Memory/` | Working, episodic, semantic, procedural |
| Planning | `10_.../05_Planning_and_Reasoning/` | Task decomposition, tree-of-thought |
| Reflection | `10_.../06_Reflection_and_Self_Correction/` | Error_Recovery_Patterns.md |

### Week 4 — Multi-Agent + MCP + LangGraph

| Topic | Folder | Focus |
|---|---|---|
| Multi-Agent Systems | `10_.../07_Multi_Agent_Systems/` | Orchestrator-worker, debate, specialization |
| Build an Agent | `10_.../09_Build_an_Agent/` | Full capstone project |
| MCP Protocol | `11_MCP_Model_Context_Protocol/` | All 9 topics — MCP is rapidly becoming industry standard |
| LangGraph | `15_LangGraph/` | All 8 topics — stateful agents, human-in-the-loop |

---

---

# PHASE 8 — Production AI + System Design

**Duration:** 4 weeks
**Repos:** `AI-ENGINEERS-ATLAS/` + `Python-DSA-API-Mastery/system-design-mastery/`
**Goal:** Design and operate scalable AI systems — what separates 15 LPA from 25 LPA

### Week 1 — Production AI

| Topic | Folder | Focus |
|---|---|---|
| Model Serving | `12_.../01_Model_Serving/` | REST vs gRPC, batching, replicas |
| Latency Optimization | `12_.../02_Latency_Optimization/` | Quantization, speculative decoding, KV cache |
| Cost Optimization | `12_.../03_Cost_Optimization/` | Cost_Case_Studies.md + Model_Routing_Guide.md |
| Caching Strategies | `12_.../04_Caching_Strategies/` | Exact-match, semantic, prompt caching |
| Observability | `12_.../05_Observability/` | LLM-specific telemetry, logs, traces |
| Evaluation Pipelines | `12_.../06_Evaluation_Pipelines/` | CI/CD for AI, regression testing |
| Safety & Guardrails | `12_.../07_Safety_and_Guardrails/` | Prompt injection defense, output validation |

**Must read:**
```
PRODUCTION_CHECKLIST.md     ← use before every deployment
```

### Week 2 — AI System Design Case Studies

All 8 case studies in `13_AI_System_Design/` — read each Architecture_Blueprint + Interview_QA:

| Case Study | Folder |
|---|---|
| Customer Support Agent | `01_Customer_Support_Agent/` |
| RAG Document Search | `02_RAG_Document_Search_System/` |
| AI Coding Assistant | `03_AI_Coding_Assistant/` |
| AI Research Assistant | `04_AI_Research_Assistant/` |
| Multi-Agent Workflow | `05_Multi_Agent_Workflow/` |
| Recommendation System with RAG | `06_Recommendation_System_with_RAG/` |
| AI Content Moderation | `07_AI_Content_Moderation_Pipeline/` |
| Cost-Aware AI Router | `08_Cost_Aware_AI_Router/` |

```
13_AI_System_Design/System_Design_Framework.md     ← 5-step framework for any design interview
```

### Week 3 — System Design Foundations

| Module | Folder | Topics |
|---|---|---|
| Computer Fundamentals | `system-design-mastery/00_computer_fundamentals/` | CPU, memory, I/O, syscalls |
| Networking | `01_networking_basics/` | TCP/UDP, HTTP/1–3, DNS, TLS |
| System Fundamentals | `02_system_fundamentals/` | Latency, throughput, CAP theorem, SLOs |
| Databases | `05_databases/` | SQL vs NoSQL, ACID, indexing |
| Caching | `06_caching/` | Redis patterns, eviction, cache-aside |
| Load Balancing | `08_load_balancing/` | Consistent hashing, health checks |
| Message Queues | `09_message_queues/` | Kafka, pub/sub, at-least-once delivery |
| Distributed Systems | `10_distributed_systems/` | Raft, replication, partition tolerance |

### Week 4 — Advanced System Design

| Module | Folder | Topics |
|---|---|---|
| Scalability Patterns | `11_scalability_patterns/` | CQRS, event sourcing, saga |
| Microservices | `12_microservices/` | Service mesh, circuit breakers |
| Security | `13_security/` | OAuth2, JWT, DDoS mitigation |
| Observability | `14_observability/` | Prometheus, ELK, Jaeger |
| Cloud Architecture | `15_cloud_architecture/` | AWS/GCP, serverless, multi-region |
| Case Studies | `22_case_studies/` | URL Shortener, Twitter, Netflix, Uber, WhatsApp |
| Interview Framework | `23_interview_framework/` | 45-minute structured approach |

---

---

# PHASE 9 — Linux + AWS + Terraform + Docker + Kubernetes

**Duration:** 3 weeks
**Repos:** `Linux-Terraform-AWS-Mastery/` + `Container-Engineering/` + `linux-guide/`
**Goal:** Deploy and manage AI/ML infrastructure — required at senior level

### Week 1 — Linux + Bash Scripting

| Module | Folder | Topics |
|---|---|---|
| Linux Fundamentals | `01_Linux/01_fundamentals/` | Filesystem, shell basics, package management |
| Users & Permissions | `01_Linux/04_users_permissions/` | chmod, chown, sudo, file permissions |
| Processes | `01_Linux/05_processes/` | ps, kill, signals, systemd |
| Networking | `01_Linux/06_networking/` | SSH, curl, netstat, port management |
| Bash Scripting | `02_Bash-Scripting/` | All 8 modules — automate everything |

**Quick reference:**
```
linux-guide/          ← use as daily reference for commands
```

### Week 2 — AWS + Terraform

| Module | Folder | Topics |
|---|---|---|
| Cloud Foundations | `03_AWS/01_cloud_foundations/` | IaaS/PaaS/SaaS, shared responsibility |
| EC2 + VPC | `03_AWS/03_compute/` + `05_networking/` | Instances, security groups, subnets |
| S3 + IAM | `03_AWS/04_storage/` + `06_security/` | Object storage, roles, least privilege |
| RDS + CloudWatch | `03_AWS/07_databases/` + `08_monitoring/` | Managed databases, metrics, alarms |
| ECS + Lambda | `03_AWS/10_containers/` + `11_serverless/` | Container services, functions |
| Terraform | `04_Terraform/` | All 9 modules — IaC from intro to AWS with Terraform |

### Week 3 — Docker + Kubernetes

| Module | Folder | Topics |
|---|---|---|
| Docker | `Container-Engineering/01_Docker/` | Dockerfile, volumes, networking, Compose, multi-stage |
| Kubernetes | `Container-Engineering/02_Kubernetes/` | Pods, Deployments, Services, Ingress, RBAC, HPA |
| Docker to K8s | `Container-Engineering/03_Docker_to_K8s/` | Migration workflow |
| Projects | `Container-Engineering/04_Projects/` | Dockerize + deploy a Python app end-to-end |

---

---

# PHASE 10 — Observability + Airflow

**Duration:** 2 weeks
**Repos:** `observability-zero-to-hero/` + `Airflow/`
**Goal:** Operate production data and AI systems with full visibility

### Week 1 — Observability Stack

| Day | Folder | Topics |
|---|---|---|
| Day 1 | `day-1/` | Metrics vs logs vs traces, why observability matters |
| Day 2 | `day-2/` | Prometheus + Grafana setup on K8s |
| Day 3 | `day-3/` | PromQL — write real queries |
| Day 4 | `day-4/` | Custom metrics, Alertmanager, alert rules |
| Day 5 | `day-5/` | EFK stack — centralized logging |
| Day 6 | `day-6/` | Jaeger — distributed tracing |
| Day 7 | `day-7/` | OpenTelemetry — unified stack |

### Week 2 — Apache Airflow (Pipeline Orchestration)

| Module | Folder | Topics |
|---|---|---|
| Beginner | `01_Beginner/` | Architecture, first DAG, core operators |
| Intermediate | `02_Intermediate/` | Sensors, executors, XComs, TaskFlow API |
| Advanced | `03_Advanced/` | Dynamic mapping, deferrable operators, testing |
| Airflow 3 Features | `05_Airflow_3_Features/` | Asset-driven scheduling, DAG versioning |
| Cloud Airflow | `06_Airflow_on_Cloud/` | AWS MWAA, EKS deployment |
| Integrations | `07_Integrations/` | dbt, Spark, Great Expectations |

---

---

# PHASE 11 — DSA + Interview Preparation

**Duration:** 4 weeks
**Repo:** `Python-DSA-API-Mastery/dsa-complete-mastery/`
**Goal:** Pass coding rounds at top companies, sharpen problem-solving

### Week 1 — Foundations + Linear Structures

| Module | Folder | Interview Weight |
|---|---|---|
| Complexity Analysis | `01_complexity_analysis/` | ⭐⭐⭐ Every answer needs Big-O |
| Arrays | `02_arrays/` | ⭐⭐⭐ Most common interview topic |
| Strings | `03_strings/` | ⭐⭐⭐ Anagrams, palindromes, sliding window |
| Recursion | `04_recursion/` | ⭐⭐⭐ Foundation for trees/graphs/DP |
| Sorting | `05_sorting/` | ⭐⭐ Merge sort + quick sort internals |
| Hashing | `10_hashing/` | ⭐⭐⭐ Most versatile technique |
| Two Pointers | `11_two_pointers/` | ⭐⭐⭐ Dozens of problems solved by this |
| Sliding Window | `12_sliding_window/` | ⭐⭐⭐ String + subarray problems |
| Binary Search | `13_binary_search/` | ⭐⭐⭐ Search + answer-space problems |

### Week 2 — Trees + Graphs

| Module | Folder | Interview Weight |
|---|---|---|
| Linked List | `07_linked_list/` | ⭐⭐ Fast-slow pointer, reversal |
| Stack + Queue | `08_stack/` + `09_queue/` | ⭐⭐ Monotonic stack problems |
| Trees | `14_trees/` | ⭐⭐⭐ BFS, DFS, LCA, path problems |
| Binary Search Trees | `15_binary_search_trees/` | ⭐⭐ Validation, kth element |
| Heaps | `16_heaps/` | ⭐⭐⭐ Top-K, median stream, task scheduling |
| Trie | `17_trie/` | ⭐⭐ Prefix search, autocomplete |
| Graphs | `18_graphs/` | ⭐⭐⭐ BFS/DFS, topological sort, union-find |

### Week 3 — Advanced Algorithms

| Module | Folder | Interview Weight |
|---|---|---|
| Greedy | `19_greedy/` | ⭐⭐ Interval scheduling, activity selection |
| Backtracking | `20_backtracking/` | ⭐⭐⭐ Subsets, permutations, N-Queens |
| Dynamic Programming | `21_dynamic_programming/` | ⭐⭐⭐ Most feared — 10 core patterns |
| Bit Manipulation | `22_bit_manipulation/` | ⭐⭐ XOR tricks, power of 2 checks |
| Advanced Graphs | `25_advanced_graphs/` | ⭐⭐ Dijkstra, Bellman-Ford, MST |
| DSU | `24_disjoint_set_union/` | ⭐⭐ Connected components, Kruskal's |
| System Design Patterns (DSA) | `26_system_design_patterns/` | ⭐⭐⭐ LRU cache, rate limiter — asked directly |

### Week 4 — Full Interview Simulation

```
dsa-complete-mastery/99_interview_master/dsa_0_2_years.md
dsa-complete-mastery/99_interview_master/dsa_3_5_years.md
dsa-complete-mastery/99_interview_master/dsa_faang_level.md
python-complete-mastery/99_interview_master/scenario_based_questions.md
python-complete-mastery/99_interview_master/tricky_edge_cases.md
system-design-mastery/99_interview_master/scenario_questions.md
system-design-mastery/99_interview_master/rapid_fire.md
api-mastery/99_interview_master/scenario_based_questions.md
```

---

---

# PHASE 12 — Advanced AI Topics + Claude APIs

**Duration:** 2 weeks
**Repo:** `AI-ENGINEERS-ATLAS/`
**Goal:** Stand out with cutting-edge skills — HuggingFace fine-tuning, evaluation, Claude API

### Week 1 — HuggingFace + Evaluation + RL

| Section | Folder | Topics |
|---|---|---|
| HuggingFace | `14_Hugging_Face_Ecosystem/` | Hub, Transformers, Datasets, PEFT/LoRA, Trainer API |
| AI Evaluation | `18_AI_Evaluation/` | Benchmarks, LLM-as-Judge, Adversarial_Test_Suite.md |
| Reinforcement Learning | `19_Reinforcement_Learning/` | MDPs, Q-learning, PPO, RL for LLMs |

**Most important file:**
```
14_.../04_PEFT_and_LoRA/When_to_Use.md     ← LoRA fine-tuning is asked in every AI interview
```

### Week 2 — Claude API + Agent SDK

| Track | Folder | Topics |
|---|---|---|
| Claude as AI Model | `21_Claude_Mastery/01_Claude_as_an_AI_Model/` | Architecture, RLHF, Constitutional AI, Extended Thinking |
| Claude API | `21_Claude_Mastery/03_Claude_API_and_SDK/` | Messages API, Tool Use, Streaming, Prompt Caching, Batching |
| Agent SDK | `21_Claude_Mastery/04_Claude_Agent_SDK/` | Build agents, multi-agent orchestration, safety |

---

---

# Build These 3 Projects (Portfolio That Gets Interviews)

| # | Project | When to Build | Repo Path |
|---|---|---|---|
| 1 | **Production RAG System** — document Q&A with chunking, re-ranking, RAGAS evaluation, monitoring | After Phase 7 | `AI-ENGINEERS-ATLAS/09_RAG_Systems/09_Build_a_RAG_App/` |
| 2 | **Multi-Agent Research Assistant** — LangGraph + tools + memory + human-in-the-loop | After Phase 7 | `AI-ENGINEERS-ATLAS/10_AI_Agents/09_Build_an_Agent/` + `15_LangGraph/08_Build_with_LangGraph/` |
| 3 | **E-Commerce FastAPI** — OOP + JWT + SQLAlchemy + Docker + GitHub Actions CI/CD | After Phase 5 | `Python-DSA-API-Mastery/00_Capstone_Projects/01_Ecommerce_API_FastAPI/` |

---

---

# Timeline — Choose Your Track

## 6-Month Full-Time (Recommended)

```
Month 1  │ Phase 1 (Python)       + Phase 2 (ML Foundations)
Month 2  │ Phase 3 (SQL)          + Phase 4 (Deep Learning + NLP)
Month 3  │ Phase 5 (APIs)         + Phase 6 (Transformers + LLMs)
Month 4  │ Phase 7 (RAG + Agents) — build Project 1 + 2
Month 5  │ Phase 8 (Production + System Design) + Phase 9 (Linux + AWS + K8s)
Month 6  │ Phase 10 (Observability + Airflow) + Phase 11 (DSA + Interview Prep)
          │ Phase 12 (Advanced AI) — build Project 3
          │ Start applying from Week 3 of Month 5
```

## 12-Month Part-Time (2–3 hrs/day)

```
Month 1–2   │ Phase 1 + Phase 2
Month 3     │ Phase 3 (SQL)
Month 4–5   │ Phase 4 + Phase 5
Month 6–7   │ Phase 6 + Phase 7
Month 8     │ Phase 8 (Production + System Design)
Month 9     │ Phase 9 (Linux + AWS + K8s)
Month 10    │ Phase 10 + Phase 12
Month 11–12 │ Phase 11 (DSA + Interview Prep) + Projects
```

---

---

# What Each Phase Unlocks (Salary Impact)

| After Completing | Role You Can Target | Expected Package |
|---|---|---|
| Phase 1 + 2 | Junior ML Engineer / Data Analyst | 6–10 LPA |
| Phase 1–4 + SQL | Data Scientist | 10–15 LPA |
| Phase 1–6 + Projects | ML Engineer / AI Engineer | 15–20 LPA |
| Phase 1–8 + Projects | Senior ML/AI Engineer | 20–25 LPA |
| Phase 1–12 + 3 Projects | Senior AI Engineer / Lead | 25–35 LPA |

---

---

# Interview Preparation Checklist

Before every interview round, review:

```
# Coding Round
dsa-complete-mastery/99_interview_master/          ← based on company level

# Python Depth
python-complete-mastery/99_interview_master/python_3_5_years.md
python-complete-mastery/99_interview_master/tricky_edge_cases.md

# ML/AI Conceptual
AI-ENGINEERS-ATLAS/02_ML_Foundations/05_Model_Evaluation/Interview_QA.md
AI-ENGINEERS-ATLAS/03_Classical_ML/Algorithm_Comparison.md
AI-ENGINEERS-ATLAS/09_RAG_Systems/Full_Pipeline_Overview.md

# System Design
system-design-mastery/23_interview_framework/        ← use this framework every time
system-design-mastery/99_interview_master/
AI-ENGINEERS-ATLAS/13_AI_System_Design/System_Design_Framework.md

# API Design
api-mastery/99_interview_master/scenario_based_questions.md

# Production/Cost
AI-ENGINEERS-ATLAS/PRODUCTION_CHECKLIST.md
AI-ENGINEERS-ATLAS/12_Production_AI/03_Cost_Optimization/Cost_Case_Studies.md
```

---

*All repos: `Python-DSA-API-Mastery` · `AI-ENGINEERS-ATLAS` · `SQL-Mastery` · `Linux-Terraform-AWS-Mastery` · `Container-Engineering` · `observability-zero-to-hero` · `Airflow` · `linux-guide` · `devmastery`*

*Last updated: 2026-04-22*
