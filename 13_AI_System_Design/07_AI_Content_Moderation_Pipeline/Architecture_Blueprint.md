# Architecture Blueprint
## Design Case 07: AI Content Moderation Pipeline

A multi-stage content moderation system capable of processing **1 million posts per day** with sub-second latency SLAs for time-sensitive content. The architecture uses a staged funnel: cheap-and-fast classifiers handle clear-cut cases, LLMs handle ambiguous edge cases, and human reviewers handle appeals and high-stakes decisions. Each stage feeds a feedback loop that continuously improves upstream models.

---

## System Overview

```mermaid
graph TB
    Content["Incoming Content\n(text, image, video)\nvia API or message queue"]
    
    subgraph Ingestion["Ingestion Layer"]
        APIGateway["API Gateway\nContent validation\nMetadata extraction"]
        PriorityQueue["Priority Queue\n(Kafka)\nHigh: live streams, viral\nNormal: user posts\nLow: bulk/scheduled"]
    end

    subgraph Stage1["Stage 1: Fast Classifier (< 50ms)"]
        HashFilter["Hash Filter\nPreviously seen harmful hashes\n(photo DNA / text hash)"]
        RulesEngine["Rules Engine\nRegex + keyword blocklists\nURL scanning"]
        MLClassifier["ML Classifier\nFine-tuned Haiku / distilBERT\nMulti-label: spam/hate/nsfw/violence"]
    end

    subgraph Stage2["Stage 2: LLM Review (< 2s)"]
        LLMRouter["LLM Router\nRoute by content type + policy area"]
        HaikuReview["Haiku Review\nContext-aware moderation\n~80% of LLM-routed cases"]
        SonnetReview["Sonnet Review\nNuanced policy reasoning\n~20% of hard cases"]
    end

    subgraph Stage3["Stage 3: Human Review Queue"]
        HumanQueue["Human Review Queue\nPriority-sorted by risk score"]
        ReviewerDashboard["Reviewer Dashboard\nDecision UI + policy guide\nAudit trail"]
        AppealQueue["Appeal Queue\nUser-submitted appeals\nSLA: 24 hours"]
    end

    subgraph FeedbackLoop["Feedback Loop (Async)"]
        DecisionLogger["Decision Logger\nLog all decisions + signals"]
        TrainingDataCurator["Training Data Curator\nSample edge cases\nLabel disagreements"]
        ModelRetrainer["Model Retrainer\nWeekly fine-tune cycle\nA/B test new classifiers"]
    end

    subgraph Storage["Storage"]
        ContentDB[("PostgreSQL\nContent + decisions\nAudit trail")]
        PolicyDB[("Policy Version DB\nRules per jurisdiction\nVersion history")]
        ModelRegistry[("Model Registry\nMLflow / S3\nClassifier versions")]
    end

    Content --> APIGateway
    APIGateway --> PriorityQueue
    PriorityQueue --> HashFilter
    HashFilter -->|"Known hash match"| AutoRemove["Auto-remove\n(known CSAM / hash match)"]
    HashFilter -->|"No match"| RulesEngine
    RulesEngine -->|"Clear violation"| AutoAction["Auto-action\n(remove / warn / restrict)"]
    RulesEngine -->|"Uncertain"| MLClassifier
    MLClassifier -->|"High confidence violation\nscore > 0.95"| AutoAction
    MLClassifier -->|"High confidence clean\nscore < 0.05"| AutoApprove["Auto-approve"]
    MLClassifier -->|"Uncertain\n0.05 ≤ score ≤ 0.95"| LLMRouter

    LLMRouter --> HaikuReview
    HaikuReview -->|"Clear decision\nconfidence > 0.85"| AutoAction
    HaikuReview -->|"Hard case\nconfidence ≤ 0.85"| SonnetReview
    SonnetReview -->|"Clear decision"| AutoAction
    SonnetReview -->|"Requires human judgment"| HumanQueue

    HumanQueue --> ReviewerDashboard
    AppealQueue --> ReviewerDashboard
    ReviewerDashboard --> DecisionLogger

    DecisionLogger --> TrainingDataCurator
    TrainingDataCurator --> ModelRetrainer
    ModelRetrainer --> ModelRegistry
    ModelRegistry --> MLClassifier
```

---

## Throughput Design: 1M Posts/Day

At 1 million posts/day, the throughput math must be explicit:

```
1,000,000 posts/day
÷ 86,400 seconds/day
= 11.6 posts/second average

Peak factor: 3x during peak hours (8pm–midnight local)
Peak throughput: ~35 posts/second
```

**Stage distribution (based on typical social platform data):**

| Stage | % of Traffic | Posts/Day | Posts/Hour (avg) |
|---|---|---|---|
| Hash filter catches | 2% | 20,000 | 833 |
| Rules engine catches | 8% | 80,000 | 3,333 |
| ML classifier auto-action | 15% | 150,000 | 6,250 |
| ML classifier auto-approve | 65% | 650,000 | 27,083 |
| Routes to LLM (Haiku) | 8% | 80,000 | 3,333 |
| Routes to LLM (Sonnet) | 1.5% | 15,000 | 625 |
| Routes to human review | 0.5% | 5,000 | 208 |

**Human queue:** 5,000 posts/day ÷ 8 working hours = 625 posts/hour. At a reviewer throughput of 60 posts/hour per person, you need ~11 reviewers during business hours to keep up. Scale to 20 for peak days, coverage across time zones.

---

## Latency SLA by Content Type

Different content types carry different risk profiles and therefore different latency requirements:

| Content Type | SLA | Rationale |
|---|---|---|
| Live stream segments | < 100ms | Viral spread risk, real-time audience |
| Text posts from new accounts | < 500ms | Spam and coordinated campaigns |
| Standard text posts | < 2s | Users expect quick publish confirmation |
| Images (standard) | < 3s | Vision processing overhead |
| Videos (< 60s) | < 10s | Transcription + frame analysis |
| Appeals | < 24 hours | Human review window |

---

## Stage 1: Fast Classifier Architecture

```mermaid
flowchart LR
    Input["Content"] --> Parallel

    subgraph Parallel["Parallel Checks (all run simultaneously)"]
        Hash["PhotoDNA / Text Hash\nKnown-harmful content\n< 5ms"]
        URL["URL Scanner\nVirusTotal / Google SafeBrowsing\n< 100ms async"]
        Regex["Regex + Keyword\nBlocklisted terms\nJurisdiction-aware\n< 2ms"]
        ML["ML Classifier\nfine-tuned DistilBERT\nor Haiku batch mode\n< 50ms"]
    end

    Parallel --> Decision["Decision Aggregator\nFirst definitive signal wins\nUncertain → escalate"]
```

**Why parallel and not sequential?** Sequential checks add latency. Running all Stage 1 checks simultaneously means total Stage 1 latency equals the slowest check's latency, not the sum.

---

## Feedback Loop: The Self-Improving Pipeline

The feedback loop is what makes the system get better over time rather than degrading.

```mermaid
flowchart TD
    Decisions["All moderation decisions\n(auto + human)"] --> Logger["Decision Logger\nStore: content, signals, decision,\nconfidence, reviewer_id, time"]

    Logger --> Sampler["Smart Sampler\nSample strategy:\n- All human review decisions\n- LLM decisions where confidence 0.7–0.9\n- Random 1% of auto-decisions"]

    Sampler --> QualityCheck["Quality Check\nDisagreement detection:\n- Human overrides ML decision\n- Haiku vs Sonnet disagreement\n- Appeal reversal"]

    QualityCheck --> LabelCuration["Label Curation\nHuman expert labels\ndisagreement cases"]

    LabelCuration --> TrainingSet["Training Dataset\nNew examples added weekly\nBalanced across violation types"]

    TrainingSet --> Retrain["Fine-tune Cycle\nWeekly retraining\nof ML classifier"]

    Retrain --> ABTest["A/B Test\nNew model vs current\non held-out eval set"]

    ABTest -->|"Passes quality gates"| Deploy["Deploy to production\n(rolling, 10% → 50% → 100%)"]
    ABTest -->|"Fails"| Investigate["Investigate regression\nDo not deploy"]
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| 📄 **Architecture_Blueprint.md** | ← you are here |
| [📄 Component_Breakdown.md](./Component_Breakdown.md) | Component deep dive |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |

⬅️ **Prev:** [06 Recommendation System with RAG](../06_Recommendation_System_with_RAG/Architecture_Blueprint.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [08 Cost-Aware AI Router](../08_Cost_Aware_AI_Router/Architecture_Blueprint.md)
