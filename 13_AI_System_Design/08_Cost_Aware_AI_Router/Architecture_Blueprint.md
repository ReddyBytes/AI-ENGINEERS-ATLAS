# Architecture Blueprint
## Design Case 08: Cost-Aware AI Router

An intelligent API gateway that sits in front of multiple LLM providers and automatically dispatches each request to the cheapest model that can handle it correctly. The router enforces cost budgets, latency SLAs, and falls back gracefully through a model chain when cheaper models fail. New models are validated in shadow mode before carrying live traffic.

---

## System Overview

```mermaid
graph TB
    Client["Client Application\nSends: request + metadata\n(user tier, max_latency, budget_token)"]

    subgraph Router["Cost-Aware AI Router"]
        APIGateway["API Gateway\nAuth, rate limiting\nStandardized request schema"]
        BudgetEnforcer["Budget Enforcer\nCheck user / org monthly budget\nReject if exceeded"]
        ComplexityClassifier["Complexity Classifier\nFine-tuned Haiku\nClassify: nano / mid / frontier"]
        CapabilityRegistry["Model Capability Registry\nFor each model: cost, latency, capabilities, status"]
        RoutingEngine["Routing Engine\nSelect cheapest model that meets:\n- complexity tier\n- latency SLA\n- required capabilities"]
        FallbackChain["Fallback Chain Manager\nIf primary fails: try next tier\nMax 3 attempts"]
        ShadowRouter["Shadow Router\nMirror % of traffic to candidate models\n(doesn't affect primary response)"]
    end

    subgraph ModelPool["Model Pool"]
        Nano["Nano Tier\nClaude Haiku\nGPT-4o-mini\nGemini Flash"]
        Mid["Mid Tier\nClaude Sonnet\nGPT-4o\nGemini Pro"]
        Frontier["Frontier Tier\nClaude Opus\no1 / o3\nGemini Ultra"]
    end

    subgraph BudgetSystem["Budget Management"]
        BudgetDB[("Budget DB\nPostgreSQL\nUser, org, global budgets\nCurrent spend by period")]
        CostLedger[("Cost Ledger\nReal-time spend tracking\nRedis counter + Postgres batch write")]
        AlertService["Alert Service\n80% budget warning\n100% budget enforcement"]
    end

    subgraph Observability["Observability"]
        RoutingLog[("Routing Log\nEvery decision:\nmodel selected, reason, cost, latency")]
        ShadowAnalysis["Shadow Analysis Dashboard\nCandidate model quality vs production\nCost delta, latency delta"]
        CostDashboard["Cost Dashboard\nSpend by user/org/model/day\nProjected monthly cost"]
    end

    Client --> APIGateway
    APIGateway --> BudgetEnforcer
    BudgetEnforcer --> ComplexityClassifier
    ComplexityClassifier --> RoutingEngine
    CapabilityRegistry --> RoutingEngine
    RoutingEngine --> FallbackChain
    FallbackChain --> Nano
    FallbackChain --> Mid
    FallbackChain --> Frontier
    RoutingEngine --> ShadowRouter
    ShadowRouter -.->|"Shadow traffic (async)"| Nano
    ShadowRouter -.->|"Shadow traffic (async)"| Mid
    Nano --> CostLedger
    Mid --> CostLedger
    Frontier --> CostLedger
    CostLedger --> BudgetDB
    CostLedger --> AlertService
    RoutingEngine --> RoutingLog
    ShadowRouter --> ShadowAnalysis
    CostLedger --> CostDashboard
```

---

## Routing Decision Flow

```mermaid
flowchart TD
    Request["Incoming Request\n+ metadata: user_id, max_latency_ms, capabilities_required"]

    Request --> BudgetCheck{"Budget check\n(Redis counter)"}
    BudgetCheck -->|"Exceeded"| Reject["429: Budget Exceeded\nReturn budget reset time"]
    BudgetCheck -->|"OK"| Classify

    Classify["Complexity Classifier\n(~50ms, Haiku-powered)"]
    Classify -->|"nano"| SelectNano
    Classify -->|"mid"| SelectMid
    Classify -->|"frontier"| SelectFrontier

    SelectNano["Select cheapest available\nnano model that meets\nlatency SLA + capabilities"]
    SelectMid["Select cheapest available\nmid model"]
    SelectFrontier["Select cheapest available\nfrontier model"]

    SelectNano --> CallModel["Call selected model"]
    SelectMid --> CallModel
    SelectFrontier --> CallModel

    CallModel --> Success{"Response\nsuccessful?"}
    Success -->|"Yes + confidence OK"| Return["Return to client\nLog: model, tokens, cost, latency"]
    Success -->|"Timeout / rate limit"| Fallback1["Fallback: next model in tier\n(e.g., GPT-4o-mini if Haiku failed)"]
    Success -->|"Low confidence response\n(escalation flag)"| Fallback2["Escalate to next tier\nLog escalation event"]

    Fallback1 --> CallModel
    Fallback2 --> CallModel

    Return --> UpdateLedger["Update cost ledger\n(Redis increment + async Postgres)"]
```

---

## Model Capability Registry

The registry is the source of truth for what each model can do and what it costs. It's version-controlled and hot-reloadable without a deployment.

```yaml
models:
  claude-haiku-3-5:
    tier: nano
    provider: anthropic
    status: active          # active | shadow | deprecated | circuit_open
    pricing:
      input_per_1m:  0.08
      output_per_1m: 0.30
      cached_input_per_1m: 0.008
    latency_p50_ms: 400
    latency_p99_ms: 1200
    context_window_tokens: 200000
    capabilities:
      - classification
      - extraction
      - short_generation     # < 500 tokens output
      - structured_output
      - tool_use
      - vision
    not_suitable_for:
      - complex_reasoning
      - long_generation      # > 1000 tokens output
      - code_generation_hard
    max_concurrent_requests: 200

  claude-sonnet-4:
    tier: mid
    provider: anthropic
    status: active
    pricing:
      input_per_1m:  3.00
      output_per_1m: 15.00
      cached_input_per_1m: 0.30
    latency_p50_ms: 1500
    latency_p99_ms: 4000
    context_window_tokens: 200000
    capabilities:
      - classification
      - extraction
      - short_generation
      - long_generation
      - code_generation
      - complex_reasoning
      - structured_output
      - tool_use
      - vision
    max_concurrent_requests: 100

  claude-opus-4:
    tier: frontier
    provider: anthropic
    status: active
    pricing:
      input_per_1m:  15.00
      output_per_1m: 75.00
      cached_input_per_1m: 1.50
    latency_p50_ms: 3000
    latency_p99_ms: 12000
    context_window_tokens: 200000
    capabilities:
      - all
    max_concurrent_requests: 50
```

---

## Budget Enforcement Architecture

```mermaid
flowchart LR
    Request["Request arrives"] --> Redis{"Redis counter check\nuser:{id}:spend:{month}\n< user budget limit?"}
    Redis -->|"Under budget"| Route["Route to model"]
    Redis -->|"Over budget"| Reject["Reject with 429\nReturn: budget_reset_at, upgrade_url"]

    Route --> Model["Model call completes"]
    Model --> UpdateRedis["Increment Redis counter\nby actual token cost"]
    UpdateRedis --> BatchWrite["Async batch write\nto PostgreSQL\nevery 30 seconds"]

    BatchWrite --> BudgetDB[("PostgreSQL\nBudget records\nSpend history\nOrg hierarchy")]

    BudgetDB --> Alerts["Alert service\nAt 80%: warning email\nAt 95%: throttle to nano-only\nAt 100%: reject all"]
```

**Budget hierarchy:**
- Per-user budget (e.g., $10/month on free tier)
- Per-organization budget (e.g., $500/month on pro tier)
- Global platform budget (safety ceiling, protects against runaway costs)

When an organization's budget is hit, all users in the org are affected — this prevents one high-usage user from degrading service for others.

---

## Shadow Mode Testing

```mermaid
flowchart TD
    ProdRequest["Production Request"] --> ProdModel["Production Model\n(serves user)"]
    ProdRequest -->|"10% of requests\nasync copy"| ShadowModel["Candidate Model\n(not served to user)"]

    ProdModel --> UserResponse["User Response"]
    ProdModel --> ProdLog["Log production response"]
    ShadowModel --> ShadowLog["Log shadow response"]

    ProdLog --> Compare["Automated Comparison\n- Quality score (LLM judge)\n- Token count delta\n- Cost delta\n- Latency delta\n- Format compliance"]
    ShadowLog --> Compare

    Compare --> Dashboard["Shadow Dashboard\nPromotion readiness metrics"]
    Dashboard -->|"All metrics pass"| Promote["Gradual promotion:\n10% → 25% → 50% → 100%"]
    Dashboard -->|"Metrics fail"| Investigate["Do not promote\nFile investigation report"]
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| 📄 **Architecture_Blueprint.md** | ← you are here |
| [📄 Component_Breakdown.md](./Component_Breakdown.md) | Component deep dive |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |

⬅️ **Prev:** [07 AI Content Moderation Pipeline](../07_AI_Content_Moderation_Pipeline/Architecture_Blueprint.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Section 14 — Hugging Face Ecosystem](../../14_Hugging_Face_Ecosystem/01_Hub_and_Model_Cards/Theory.md)
