# Eval Frameworks — Comparison

## At a Glance

| Dimension | Promptfoo | LangSmith | OpenAI Evals | Custom Build |
|-----------|-----------|-----------|--------------|--------------|
| **Setup time** | Minutes | Minutes | Hours | Days |
| **Code required** | No (YAML) | Minimal | Some | Full |
| **UI/Dashboard** | Yes (local) | Yes (cloud) | Basic | Build it |
| **Tracing/Observability** | No | Yes | No | Build it |
| **Human feedback** | No | Yes | No | Build it |
| **Multi-model comparison** | Yes | Yes | No | Build it |
| **CI/CD integration** | First-class | API-based | Manual | Custom |
| **Cost** | Free (OSS) | Free tier + paid | Free (OSS) | Engineering time |
| **Data ownership** | Full (local) | Cloud (SaaS) | Full (local) | Full |
| **Community/Ecosystem** | Growing | Large (LangChain) | Large (OpenAI) | N/A |
| **Enterprise features** | Limited | Yes | Limited | Custom |

---

## Detailed Feature Comparison

### Assertion / Evaluator Types

| Type | Promptfoo | LangSmith | OpenAI Evals | Custom |
|------|-----------|-----------|--------------|--------|
| String match | `contains` | Manual | `match` | Manual |
| Regex | `regex` | Manual | `includes` | Manual |
| JSON validity | `json` | Manual | Manual | Manual |
| Semantic similarity | `similar` | Embeddings API | Manual | Embeddings API |
| LLM-as-judge | `llm-rubric` | `LangChainStringEvaluator` | `model-graded-closedqa` | Build it |
| Cost threshold | `cost` | Manual | No | Manual |
| Latency threshold | `latency` | Manual | No | Manual |
| Custom Python | `python` | Python function | Python class | Native |
| Custom JavaScript | `javascript` | No | No | Node.js |

---

### Model Provider Support

| Provider | Promptfoo | LangSmith | OpenAI Evals |
|----------|-----------|-----------|--------------|
| OpenAI (GPT-4o, etc.) | Yes | Yes | Yes (native) |
| Anthropic (Claude) | Yes | Yes | No (manual) |
| Google (Gemini) | Yes | Yes | No |
| AWS Bedrock | Yes | Yes | No |
| Azure OpenAI | Yes | Yes | Yes |
| Local (Ollama) | Yes | Yes | Manual |
| Custom API | Yes | Yes | Manual |

---

### Observability Features

| Feature | Promptfoo | LangSmith | OpenAI Evals | Custom |
|---------|-----------|-----------|--------------|--------|
| Request/response logging | Results only | Full traces | Logs | Build it |
| Token usage tracking | Yes | Yes | Basic | API response |
| Error rate monitoring | Yes | Yes | No | Build it |
| Latency histograms | Yes | Yes | No | Build it |
| Conversation threads | No | Yes | No | Build it |
| Production monitoring | No | Yes | No | Build it |
| Alerts/notifications | Limited | Yes | No | Build it |

---

### Dataset Management

| Feature | Promptfoo | LangSmith | OpenAI Evals | Custom |
|---------|-----------|-----------|--------------|--------|
| Dataset versioning | YAML/Git | Built-in | JSON files | Git |
| Dataset sharing | No | Yes | GitHub | Git |
| Auto-add from failures | No | Yes | No | Build it |
| Import from CSV/JSON | Yes | Yes | JSONL | Manual |
| Production data capture | No | Yes | No | Build it |
| Human annotation UI | No | Yes | No | Build it |

---

## When to Choose Each

### Choose Promptfoo When:
- You want to compare 2+ models or prompts side by side
- You need CI/CD integration without writing custom code
- Your team prefers config-as-code (YAML checked into git)
- You don't need production monitoring or tracing
- You want everything local/private
- **Best for**: Prompt engineers, small teams, fast iteration

### Choose LangSmith When:
- You're already using LangChain or LangGraph
- You need both observability AND evaluation in one tool
- You want to capture human feedback from production users
- You need a team collaboration platform for reviewing outputs
- You require enterprise compliance features
- **Best for**: LangChain shops, teams with dedicated ML engineers

### Choose OpenAI Evals When:
- You primarily use OpenAI models
- You want access to community eval datasets (hundreds available)
- You're running standard benchmark comparisons
- You want to contribute evals back to the community
- **Best for**: OpenAI-centric teams, research use cases

### Choose Custom Build When:
- Your domain requires specialized evaluation logic
- You need full data ownership with no third-party services
- You have strict compliance requirements (HIPAA, SOC2, etc.)
- Your eval workflow is unique (e.g., running simulations)
- You need deep integration with internal systems
- **Best for**: Large enterprises, regulated industries, unique evaluation needs

---

## Integration Architecture Patterns

### Pattern 1: Promptfoo + Git (Simple)
```
Developer changes prompt
    → Commits to branch
    → GitHub Action runs: promptfoo eval
    → Results posted as PR comment
    → Merge blocked if pass rate < 85%
```

### Pattern 2: LangSmith + LangChain (Full Stack)
```
Production traffic
    → LangChain app (auto-traces to LangSmith)
    → Users give thumbs up/down
    → Failures auto-added to eval dataset
    → Nightly eval run compares with previous baseline
    → Slack alert if regression
```

### Pattern 3: Custom + CI (Enterprise)
```
Developer changes code/prompt
    → Runs unit tests (fast, no LLM calls)
    → Runs smoke eval (50 cases, ~2 min)
    → Merge to main triggers full eval (10k cases, async)
    → Results stored in internal DB
    → Dashboard shows trends over time
    → Weekly human review of 100 sampled outputs
```

---

## Cost Comparison

| Scenario | Promptfoo | LangSmith | Custom |
|----------|-----------|-----------|--------|
| Setup cost | Free | Free tier | Dev time (~2 weeks) |
| 1k test cases/day (LLM-as-judge) | LLM API cost only | LLM API + $0 (free tier) | LLM API cost only |
| 100k traces/month | N/A | ~$39/month | Server cost |
| Team of 10 + enterprise features | N/A | ~$300/month | Dev maintenance |
| Self-hosted | Yes | Enterprise plan | Yes |

---

## Verdict by Team Size

| Team Size | Recommended Stack |
|-----------|------------------|
| Solo developer | Promptfoo (fast, free) |
| 2–5 person startup | Promptfoo for CI + LangSmith free tier for tracing |
| 10–50 person team | LangSmith (paid) as single source of truth |
| 50+ enterprise | LangSmith Enterprise or custom build |
| Research lab | OpenAI Evals + custom domain benchmarks |

---

## 📂 Navigation

- Parent: [18_AI_Evaluation](../)
- Theory: [Theory.md](Theory.md)
- Cheatsheet: [Cheatsheet.md](Cheatsheet.md)
- Interview Q&A: [Interview_QA.md](Interview_QA.md)
- Code Example: [Code_Example.md](Code_Example.md)
- Next section: [08_Build_an_Eval_Pipeline](../08_Build_an_Eval_Pipeline/)
