# AI Engineer's Atlas — Topic Recap

> One-line summary of every topic across all 22 sections. Use this to quickly review what each concept covers before diving deeper.

---

## 00 — Learning Guide

| Topic | Summary |
|---|---|
| How to Use This Repo | Navigation guide — file types, how to read Theory/Cheatsheet/Interview files |
| Learning Path | Linear progression with visual flowchart from beginner to expert |
| Progress Tracker | Personal checklist to mark what you've covered |
| Beginner Path | Step-by-step learning guide for sections 00–03 |
| Intermediate Path | Step-by-step learning guide for sections 04–07 |
| Advanced Path | Step-by-step learning guide for sections 08–13 |
| AI Landscape Map | Visual map of how all AI subfields relate to each other |

---

## 01 — Math for AI

| Topic | Summary |
|---|---|
| Probability | Sample spaces, Bayes' theorem, distributions, conditional probability — the language of uncertainty |
| Statistics | Hypothesis testing, confidence intervals, p-values — how to draw conclusions from data |
| Linear Algebra | Vectors, matrices, dot products, eigenvalues, SVD — the math behind all ML computations |
| Calculus & Optimization | Derivatives, chain rule, gradient — how models minimize loss and learn |
| Information Theory | Entropy, cross-entropy, KL divergence — measuring information and uncertainty |

---

## 02 — Machine Learning Foundations

| Topic | Summary |
|---|---|
| What is ML | ML vs traditional programming, types of ML, the core mental model |
| Training vs Inference | The two phases of ML — expensive training once, fast inference many times |
| Supervised Learning | Learning from labeled data — regression (predict number) vs classification (predict class) |
| Unsupervised Learning | Finding structure without labels — clustering, dimensionality reduction, anomaly detection |
| Model Evaluation | Train/val/test splits, cross-validation, precision, recall, F1, AUC — measuring if it works |
| Overfitting & Regularization | Why models memorize instead of generalizing, and L1/L2/dropout fixes |
| Feature Engineering | Encoding, scaling, selection — turning raw data into model-ready inputs |
| Gradient Descent | SGD, mini-batch, learning rate — the optimization algorithm behind all neural networks |
| Loss Functions | MSE, cross-entropy, hinge loss — what the model is actually minimizing |
| Bias vs Variance | The fundamental tradeoff between underfitting and overfitting |

---

## 03 — Classical ML Algorithms

| Topic | Summary |
|---|---|
| Linear Regression | Fit a line to data — OLS, R², residuals, and when assumptions break |
| Logistic Regression | Binary classification using sigmoid — decision boundaries and multiclass extension |
| Decision Trees | Split data by feature thresholds — Gini impurity, entropy, pruning, CART |
| Random Forests | Ensemble of trees using bagging — reduces variance, gives feature importance |
| SVM | Find the widest margin hyperplane — kernels extend to non-linear boundaries |
| K-Means Clustering | Group data into K clusters by centroid distance — elbow method to pick K |
| PCA | Reduce dimensions by projecting onto directions of max variance — eigenvectors |
| Naive Bayes | Probabilistic classifier assuming feature independence — fast, great for text |
| XGBoost & Boosting | Sequential ensemble where each tree corrects the last — industry standard for tabular data |
| Time Series Analysis | ARIMA, Prophet, trend/seasonality decomposition — forecasting temporal data |
| Recommendation Systems | Collaborative filtering, content-based, matrix factorization, two-tower — how Netflix/Spotify recommend |
| Anomaly Detection | Isolation Forest, LOF, SMOTE — detect fraud and outliers in imbalanced data |

---

## 04 — Neural Networks & Deep Learning

| Topic | Summary |
|---|---|
| Perceptron | Simplest neural unit — linear classifier, why XOR requires hidden layers |
| Multi-Layer Perceptrons | Stack layers to approximate any function — universal approximation theorem |
| Activation Functions | Sigmoid, tanh, ReLU, GELU — non-linearity that lets networks learn complex patterns |
| Loss Functions | Cross-entropy, MSE, contrastive loss — what neural networks minimize during training |
| Forward Propagation | The full forward pass — input → layers → output, with matrix math |
| Backpropagation | Chain rule through the network — how gradients flow from output to input |
| Optimizers | SGD → Momentum → RMSProp → Adam — how to update weights to minimize loss |
| Regularization | Dropout, batch norm, weight decay, early stopping — preventing overfitting |
| CNNs | Convolutional layers learn spatial features — the backbone of computer vision |
| RNNs | Process sequences step-by-step — LSTMs/GRUs solve vanishing gradients |
| GANs | Generator vs discriminator in adversarial training — creates realistic synthetic data |
| Training Techniques | Transfer learning, mixed precision, gradient clipping — practical training at scale |

---

## 05 — NLP Foundations

| Topic | Summary |
|---|---|
| Text Preprocessing | Cleaning, stemming, lemmatization, stop words — preparing raw text for models |
| Tokenization | Splitting text into tokens — word, subword (BPE), sentencepiece for LLMs |
| Bag of Words & TF-IDF | Sparse vector representations — term frequency weighted by document rarity |
| Word Embeddings | Word2Vec, GloVe, FastText — dense vectors where similar words are close in space |
| Semantic Similarity | Cosine similarity, sentence embeddings — measuring meaning distance between texts |
| Hidden Markov Models | Probabilistic sequence labeling — Viterbi algorithm for POS tagging |
| Conditional Random Fields | Structured prediction for sequences — NER, better than HMM for labeling tasks |

---

## 06 — Transformers

| Topic | Summary |
|---|---|
| Before Transformers | RNN/LSTM bottlenecks, seq-to-seq limitations — why attention was invented |
| Attention Mechanism | Query/Key/Value — compute how much each token should attend to every other token |
| Self-Attention | Tokens attend to themselves — creates contextual representations |
| Multi-Head Attention | Parallel attention in different subspaces — captures multiple relationship types |
| Positional Encoding | Sinusoidal encoding, learned positions, RoPE — telling the model token order |
| Transformer Architecture | Full encoder-decoder with layer norm, residual connections, FFN — the complete picture |
| Encoder-Decoder Models | T5, BART — sequence-to-sequence tasks like translation and summarization |
| BERT | Masked language modeling, bidirectionality — fine-tuning for classification/NER |
| GPT | Autoregressive left-to-right generation — scaling laws and emergent capabilities |
| Vision Transformers | Image patches as tokens — ViT architecture, CLIP for vision-language alignment |

---

## 07 — Large Language Models

| Topic | Summary |
|---|---|
| LLM Fundamentals | What an LLM is, scale effects, emergent capabilities from size |
| How LLMs Generate Text | Tokenization → logits → sampling — temperature, top-p, top-k, greedy decoding |
| Pretraining | Self-supervised next-token prediction on massive datasets — the foundation |
| Fine-Tuning | Full fine-tune vs LoRA vs QLoRA — adapting pretrained models for specific tasks |
| Instruction Tuning | SFT on instruction-response pairs — making models follow natural language instructions |
| RLHF | Reward models + PPO/DPO — aligning models to human preferences and safety |
| Context Windows & Tokens | Context limits per model, long-context models, token counting for cost control |
| Hallucination & Alignment | Why LLMs confabulate, detection methods, mitigation strategies |
| Using LLM APIs | Anthropic & OpenAI APIs, streaming, error handling, rate limits |
| Ollama & Local LLMs | Run LLMs locally with Ollama — GGUF quantization, REST API, local RAG |
| Reasoning Models | Chain-of-thought, o1/o3/Claude extended thinking — when to pay for reasoning tokens |

---

## 08 — LLM Applications

| Topic | Summary |
|---|---|
| Prompt Engineering | Zero-shot, few-shot, CoT, system prompts — getting the right output from LLMs |
| Tool Calling | Function calling with JSON schemas — LLMs that trigger real actions in your code |
| Structured Outputs | JSON mode, schema enforcement — extracting data reliably from LLM responses |
| Embeddings | Dense vector representations — use cases, dimensionality, batching |
| Vector Databases | Pinecone, Weaviate, pgvector, FAISS — storing and querying embedding vectors |
| Semantic Search | Dense retrieval, hybrid search, re-ranking — finding relevant content by meaning |
| Memory Systems | In-context, external, episodic, semantic — giving LLMs persistent memory |
| Streaming Responses | SSE, streaming tokens, progressive UI — showing output as it generates |

---

## 09 — RAG Systems

| Topic | Summary |
|---|---|
| RAG Fundamentals | Retrieval-Augmented Generation — ground LLM responses in real documents |
| Document Ingestion | PDF, HTML, markdown parsing — extracting and cleaning content for indexing |
| Chunking Strategies | Fixed, recursive, semantic — splitting documents for optimal retrieval |
| Embedding & Indexing | Embed chunks into vectors, index with HNSW/IVF — building the searchable store |
| Retrieval Pipeline | Top-k, MMR, re-ranking, hybrid search — finding the most relevant chunks |
| Context Assembly | Build the prompt from retrieved chunks — deduplication and window management |
| Advanced RAG | HyDE, query rewriting, RAPTOR, multi-hop — techniques that improve retrieval quality |
| RAG Evaluation | RAGAS metrics — faithfulness, answer relevance, context recall |
| Build a RAG App | End-to-end project: architecture → code → deploy → troubleshoot |
| GraphRAG | Knowledge graph RAG — entity extraction, community detection, global vs local search |
| CAG — Cache-Augmented Generation | Reuse KV cache for long static context — cheaper than RAG for stable documents |

---

## 10 — AI Agents

| Topic | Summary |
|---|---|
| Agent Fundamentals | The agent loop — perception → reasoning → action → observation, repeated |
| ReAct Pattern | Thought → Action → Observation — chain-of-thought interleaved with tool calls |
| Tool Use | Define tool schemas, execute tools, recover from errors — agents acting in the world |
| Agent Memory | Working, episodic, semantic, procedural — the four memory types in an agent system |
| Planning & Reasoning | Tree-of-thought, task decomposition — breaking complex goals into executable steps |
| Reflection & Self-Correction | Self-evaluation and iterative refinement — critic agents improve output quality |
| Multi-Agent Systems | Orchestrator-worker, debate, specialization — multiple agents collaborating |
| Agent Frameworks | LangChain, CrewAI, AutoGen — when to use each framework |
| Build an Agent | Capstone: full ReAct agent from scratch with tools and memory |

---

## 11 — MCP — Model Context Protocol

| Topic | Summary |
|---|---|
| MCP Fundamentals | The USB-C analogy for AI — a standard for connecting any model to any tool |
| MCP Architecture | Host → Client → Server model — how the three layers communicate |
| Hosts, Clients, Servers | Roles and responsibilities — who initiates, who handles, who provides capabilities |
| Tools, Resources, Prompts | The three MCP primitives — functions, data sources, and reusable prompt templates |
| Transport Layer | stdio vs SSE — two ways to connect MCP clients and servers |
| Building an MCP Server | Full walkthrough: schema → handler → registration → test |
| Security & Permissions | OAuth, capability scoping, defending against prompt injection via MCP |
| MCP Ecosystem | Official servers, community tools, Claude Desktop, IDE integrations |
| Connect MCP to Agents | Wiring MCP tool servers into an agent loop |

---

## 12 — Production AI

| Topic | Summary |
|---|---|
| Model Serving | REST vs gRPC, batching, replicas, serverless vs dedicated — deploying models |
| Latency Optimization | Quantization, speculative decoding, KV cache, streaming — making inference fast |
| Cost Optimization | Token reduction, prompt caching, model routing — minimizing API spend |
| Caching Strategies | Exact-match, semantic, prompt caching — avoid redundant LLM calls |
| Observability | Logs, metrics, traces, LLM-specific telemetry — seeing what's happening in production |
| Evaluation Pipelines | LLM-as-judge, regression testing, CI/CD for AI — automated quality checking |
| Safety & Guardrails | Prompt injection defense, output validation, content filtering |
| Fine-Tuning in Production | LoRA, QLoRA, continuous retraining, dataset curation workflows |
| Scaling AI Apps | Horizontal scaling, queue architecture, auto-scaling under load |

---

## 13 — AI System Design

| Topic | Summary |
|---|---|
| Customer Support Agent | Intent detection, tool calling, escalation logic, persistent memory |
| RAG Document Search System | Ingestion pipeline, hybrid retrieval, ranking, end-to-end search UI |
| AI Coding Assistant | Context window management, repo indexing, tool use for a coding assistant |
| AI Research Assistant | Multi-step reasoning, web retrieval, citation tracking |
| Multi-Agent Workflow | Orchestration, inter-agent communication, fault tolerance |

---

## 14 — Hugging Face Ecosystem

| Topic | Summary |
|---|---|
| Hub & Model Cards | Download models, read model cards, manage versions and private repos |
| Transformers Library | `pipeline` API, AutoModel, AutoTokenizer — run any model in 3 lines |
| Datasets Library | Load, process, stream, create custom datasets |
| PEFT & LoRA | Parameter-efficient fine-tuning — LoRA/QLoRA adapters that update <1% of weights |
| Trainer API | TrainingArguments, callbacks, evaluation loop — managed training |
| Inference Optimization | Accelerate, BitsAndBytes, Optimum — quantize and speed up inference |
| Spaces & Gradio | Build demos and deploy them publicly on Hugging Face Spaces |

---

## 15 — LangGraph

| Topic | Summary |
|---|---|
| LangGraph Fundamentals | Graph-based agent orchestration — why state machines beat linear chains |
| Nodes & Edges | Define processing nodes, connect with conditional edges |
| State Management | TypedDict state, state reducers — persistent state flowing through the graph |
| Cycles & Loops | Looping agents with breakout conditions — iterative refinement workflows |
| Human in the Loop | Interrupt, checkpoint, resume — pause agent execution for human approval |
| Multi-Agent with LangGraph | Supervisor pattern, handoffs, parallel subgraphs for multi-agent systems |
| Streaming & Checkpointing | Real-time token streaming, persistent state for resumable workflows |
| Build with LangGraph | End-to-end: build a stateful agent with tools and memory from scratch |

---

## 16 — Diffusion Models

| Topic | Summary |
|---|---|
| Diffusion Fundamentals | Progressive denoising — learn to reverse a noise-addition process |
| How Diffusion Works | Forward noise schedule, reverse denoising, U-Net, DDPM algorithm |
| Stable Diffusion | CLIP text encoder + VAE + U-Net denoiser — the architecture behind SD |
| Guidance & Conditioning | Classifier-free guidance scale — how text steers the image generation |
| Modern Diffusion Models | SDXL, FLUX — improvements in quality, resolution, and speed |
| ControlNet & Adapters | ControlNet, LoRA, IP-Adapter — controlling generation with extra conditions |
| Diffusion vs GANs | Quality, speed, training stability comparison — when to use which |

---

## 17 — Multimodal AI

| Topic | Summary |
|---|---|
| Multimodal Fundamentals | Combining vision, text, audio — modality fusion architectures |
| Vision-Language Models | CLIP, LLaVA, PaLI — models that understand both images and text |
| Image Understanding | VQA, image captioning, OCR, visual reasoning tasks |
| Using Vision APIs | Claude Vision, GPT-4V, Gemini Vision — practical code for image analysis |
| Audio & Speech AI | Whisper STT, TTS systems, voice agents, audio embeddings |
| Multimodal Embeddings | CLIP embeddings for image search and cross-modal retrieval |
| Multimodal Agents | Agents that see, hear, and act — architectures for multi-sense AI |

---

## 18 — AI Evaluation

| Topic | Summary |
|---|---|
| Evaluation Fundamentals | Why evals matter, what to measure, designing an evaluation strategy |
| Benchmarks | MMLU, HumanEval, BIG-Bench, GSM8K — standardized tests for LLM capabilities |
| LLM-as-Judge | Use AI to evaluate AI — G-Eval, pairwise comparison, handling biases |
| RAG Evaluation | RAGAS — faithfulness, answer relevance, context recall metrics |
| Agent Evaluation | Task completion rate, tool use accuracy, trajectory evaluation |
| Red Teaming | Adversarial testing — jailbreaks, prompt injection, safety evaluations |
| Eval Frameworks | LMMS-eval, OpenAI Evals, Promptfoo — tools for systematic evaluation |
| Build an Eval Pipeline | End-to-end automated evaluation system with regression testing |

---

## 19 — Reinforcement Learning

| Topic | Summary |
|---|---|
| RL Fundamentals | Agent, environment, reward, policy, value function — the RL framework |
| Markov Decision Processes | States, actions, transitions, Bellman equation — the math of RL |
| Q-Learning | Q-values, epsilon-greedy exploration — tabular RL for small state spaces |
| Deep Q-Networks | DQN with experience replay and target networks — RL for Atari |
| Policy Gradients | REINFORCE, actor-critic, advantage estimation — learning policies directly |
| PPO | Proximal Policy Optimization — the algorithm behind RLHF and ChatGPT training |
| RL in Practice | OpenAI Gym, stable-baselines3, common pitfalls — getting RL running |
| RL for LLMs | RLHF connection, reward modeling, preference learning for language models |

---

## 20 — Projects

### Beginner Projects
| Project | Summary |
|---|---|
| Data & Probability Explorer | Load data, compute and visualize probability distributions |
| ML Model Comparison | Train multiple models, evaluate and compare with metrics |
| Neural Net from Scratch | Working neural network using only NumPy — no frameworks |
| LLM Chatbot with Memory | Streaming chatbot that remembers the conversation |
| Intelligent Document Analyzer | LLM-powered structured extraction from documents |

### Intermediate Projects
| Project | Summary |
|---|---|
| Semantic Search Engine | Dense retrieval + re-ranking over a document corpus |
| Personal Knowledge Base RAG | Full RAG system over your own notes and documents |
| Multi-Tool Research Agent | ReAct agent with web search, calculator, memory tools |
| Custom LoRA Fine-Tuning | Fine-tune a Hugging Face model on your dataset with LoRA |
| Production RAG System | RAG with eval pipeline, semantic caching, observability |

### Advanced Projects
| Project | Summary |
|---|---|
| Advanced RAG with Reranking | HyDE, multi-hop retrieval, cross-encoder reranking |
| LangGraph Support Bot | Stateful support bot with human-in-the-loop checkpointing |
| Automated Eval Pipeline | CI/CD pipeline for automated LLM regression testing |
| Multi-Agent Research System | Orchestrator + specialist agents built with LangGraph |
| Fine-Tune → Evaluate → Deploy | End-to-end: fine-tune, eval, deploy, monitor in production |

---

## 21 — Claude Mastery

### Track 1 — Claude as an AI Model
| Topic | Summary |
|---|---|
| What is Claude | Model family, capabilities, Haiku/Sonnet/Opus tiers, vs other LLMs |
| How Claude Generates Text | Autoregressive generation, logits, temperature, top-p sampling |
| Tokens & Context Window | Token ≠ word — counting, context limits per model, at-limit behavior |
| Transformer Architecture | Attention, self-attention, positional encoding — how Claude is built |
| Pretraining | Next-token prediction at scale — emergent capabilities and scaling laws |
| RLHF | Reward models, PPO, human preference data — how Claude learns to be helpful |
| Constitutional AI | Self-critique + principle sets — Anthropic's approach vs standard RLHF |
| Extended Thinking | Reasoning tokens, chain-of-thought — when to pay for deeper thinking |
| Claude Model Families | Haiku 4.5 / Sonnet 4.6 / Opus 4.6 — speed vs intelligence vs cost tradeoffs |
| Safety Layers | HHH (Harmless, Helpful, Honest), refusal patterns, red-teaming |

### Track 2 — Claude Code CLI
| Topic | Summary |
|---|---|
| What is Claude Code | CLI for Claude — agentic coding assistant, vs chat interface |
| Installation & Setup | npm install, authentication, first run, config files |
| Basic Usage & Commands | Ask questions, edit files, run commands — core workflow |
| Slash Commands | Built-in vs custom slash commands — invoking skills and actions |
| Memory System | MEMORY.md, auto-memory, project memory — persistence across sessions |
| CLAUDE.md & Settings | CLAUDE.md purpose, settings.json structure, global vs project config |
| Custom Skills | skills/ folder, SKILL.md format — packaging reusable agent behaviors |
| Hooks | PreToolUse/PostToolUse/Stop events — trigger shell scripts on agent actions |
| MCP Servers | Add MCP servers to Claude Code — tools, resources, prompts |
| Agents & Subagents | Agent tool, background agents, worktrees — parallelism and isolation |
| IDE Integration | VS Code extension, status bar, keyboard shortcuts, diff view |
| Permissions & Security | Permission modes, allowedTools, bash sandboxing — controlling what Claude can do |

### Track 3 — Claude API & SDK
| Topic | Summary |
|---|---|
| API Basics | REST API, base URL, authentication, API key management |
| Messages API | `messages.create`, roles, content blocks, response structure |
| First API Call | Python/JS SDK setup, hello world, reading the response |
| System Prompts | What they do, vs user messages, best practices, examples |
| Tool Use | Define tools, tool_choice, tool_result, multi-turn tool loops |
| Streaming | stream=True, delta events, SSE — handling partial responses |
| Vision | Image content blocks, base64 vs URL, supported formats, limits |
| Prompt Engineering | Zero-shot, few-shot, CoT, XML tags, structured output via API |
| Prompt Caching | Cache control headers, cache tokens — save cost on repeated context |
| Batching | Message Batches API — async processing, cost reduction at scale |
| Cost Optimization | Token counting, model routing, caching — minimizing spend |
| Error Handling | Rate limits, retries, error types, exponential backoff |
| Model Reference | All current model IDs, capabilities, context windows, pricing tiers |

### Track 4 — Claude Agent SDK
| Topic | Summary |
|---|---|
| What are Agents | Agent loop: perception → reasoning → action → observation |
| Why Agent SDK | Built-in loop and tool execution — vs building the loop manually |
| Simple Agent | Create agent, define tools, run loop, get result |
| Tool Calling in Agents | Tool schemas, execution, error recovery, retry logic |
| Multi-Step Reasoning | Planning, task decomposition, chain-of-tool-calls |
| Agent Memory | In-context memory, passing context between steps, limitations |
| Multi-Agent Orchestration | Orchestrator + subagent pattern — parallel agents, task delegation |
| Subagents | When to spawn, isolation, context passing, result aggregation |
| Handoffs | Agent-to-agent communication, shared state, coordination |
| Safety in Agents | Prompt injection defense, tool permission scoping, human-in-the-loop |
| Claude Code as Agent | How Claude Code uses the agent pattern internally |

---

*175+ topics · 22 sections · From math foundations to production deployment*
