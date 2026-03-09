# Data Flow Diagram
## Design Case 05: Multi-Agent Software Development Workflow

The complete pipeline from feature request to deployed configuration, with all human checkpoints shown explicitly.

---

## Full Pipeline Flow (Happy Path)

```mermaid
sequenceDiagram
    actor EM as Engineering Manager
    participant Orch as LangGraph Orchestrator
    participant PM as PM Agent
    participant GitHub as GitHub Repository
    participant Dev as Developer Agent
    participant Rev as Code Reviewer Agent
    participant QA as QA Agent
    participant DevOps as DevOps Agent
    participant Notif as Notification Service

    EM->>Orch: "Add OAuth login with Google and GitHub"
    Orch->>Orch: Create branch: feature/oauth-login-20240309
    Orch->>Orch: Initialize WorkflowState

    Note over Orch,PM: STAGE 1: Requirements

    Orch->>PM: Feature request + existing auth code
    PM->>PM: Generate spec with user stories\n+ acceptance criteria
    PM->>GitHub: Commit spec.md
    PM-->>Orch: spec.md (validated: 4 stories, 12 criteria)

    Orch->>Notif: Send to EM: "Spec ready for review"\n+ GitHub link + PR
    Notif-->>EM: Slack/email notification

    EM->>GitHub: Reviews spec.md in PR
    EM->>Orch: "Approve: looks good but add GitHub OAuth scope"
    Orch->>PM: "User requested addition: GitHub OAuth scope list"
    PM->>GitHub: Update spec.md with GitHub OAuth scopes
    PM-->>Orch: Updated spec.md (re-validated)
    EM->>Orch: "Approved"

    Note over Orch,Dev: STAGE 2: Implementation

    Orch->>Dev: spec.md + existing codebase (10 relevant files)
    Dev->>Dev: Write OAuth implementation\n+ unit tests
    Dev->>Dev: Run tests (pytest)
    Note over Dev: Tests: 12 passed, 0 failed
    Dev->>GitHub: Commit: src/auth/oauth.py, tests/test_oauth.py
    Dev-->>Orch: Implementation + test results

    Orch->>Notif: Notify EM: "Implementation ready"\n+ diff link
    EM->>Orch: "Approved"

    Note over Orch,Rev: STAGE 3: Code Review

    Orch->>Rev: spec.md + implementation diff + full auth module
    Rev->>Rev: Static analysis (ruff, bandit)
    Rev->>Rev: Review against spec
    Rev-->>Orch: "changes_requested: Missing CSRF protection\non OAuth callback endpoint"

    Orch->>Dev: Review feedback: "Add CSRF token validation\nto /auth/callback endpoint"
    Dev->>Dev: Fix CSRF issue
    Dev->>Dev: Run tests (13 passed now, 0 failed)
    Dev->>GitHub: Commit: CSRF protection added
    Dev-->>Orch: Updated implementation

    Orch->>Rev: Updated diff
    Rev-->>Orch: "approved: CSRF protection correctly added"

    Orch->>Notif: Notify EM: "Code review approved"\n+ reviewer summary
    EM->>Orch: "Approved"

    Note over Orch: STAGE 4+5: QA and DevOps run in PARALLEL

    par Parallel: QA + DevOps
        Orch->>QA: spec.md + implementation
        QA->>QA: Write integration tests\n+ e2e OAuth flow tests
        QA->>GitHub: Commit test files
        QA-->>Orch: Integration tests (8 tests, coverage 94%)
    and
        Orch->>DevOps: Implementation + language/framework
        DevOps->>DevOps: Write Dockerfile (multi-stage)\n+ CI config + K8s manifests
        DevOps->>DevOps: hadolint + kubeval validation
        DevOps->>GitHub: Commit deployment config
        DevOps-->>Orch: Deployment config (all linters passed)
    end

    Orch->>Notif: Notify EM: "Pipeline complete.\nAll artifacts ready for final review."
    EM->>GitHub: Reviews PR: spec, code, tests, deployment
    EM->>Orch: "Approved: merge to main"
    Orch->>GitHub: Merge PR to main
    Orch-->>EM: "Feature pipeline complete.\nPR merged. CI running."
```

---

## Retry Flow (Developer Agent Fails Review)

```mermaid
sequenceDiagram
    participant Orch as Orchestrator
    participant Dev as Developer Agent
    participant Rev as Code Reviewer Agent

    Orch->>Dev: spec.md + codebase
    Dev->>Dev: Generate implementation (attempt 1)
    Dev-->>Orch: Implementation

    Orch->>Rev: Review implementation
    Rev-->>Orch: "changes_requested": ["Missing error handling", "No rate limiting"]

    Note over Orch: retry_count[development] = 1

    Orch->>Dev: Original spec + attempt 1 code\n+ reviewer feedback:\n"Missing error handling on token exchange\nNo rate limiting on /auth/callback"
    Dev->>Dev: Fix issues (attempt 2)
    Dev-->>Orch: Updated implementation

    Orch->>Rev: Review updated implementation
    Rev-->>Orch: "changes_requested": ["Rate limiting still missing"]

    Note over Orch: retry_count[development] = 2

    Orch->>Dev: Original spec + attempt 2 code\n+ reviewer feedback:\n"Rate limiting still missing.\nExpected: max 5 attempts per IP per minute"
    Dev->>Dev: Add rate limiting (attempt 3)
    Dev-->>Orch: Updated implementation

    Orch->>Rev: Review
    Rev-->>Orch: "approved"

    Note over Orch: retry_count reset
```

---

## Escalation Flow (Agent Fails 3 Times)

```mermaid
sequenceDiagram
    participant Orch as Orchestrator
    participant Dev as Developer Agent
    participant Rev as Code Reviewer Agent
    participant Human as Human Engineer
    participant Notif as Notification Service

    Note over Orch: retry_count[development] = 3

    Orch->>Notif: ESCALATION ALERT\nSlack: "@oncall-engineer: Developer agent failed\n3 code review attempts. Manual intervention required."
    Orch->>Notif: Send package:\n- spec.md\n- All 3 implementation attempts\n- All 3 reviewer feedbacks\n- Summary of what was tried

    Notif-->>Human: Receives full context package

    Human->>Human: Reviews why agent is stuck\nIdentifies: spec is ambiguous on OAuth scope

    Human->>Orch: Update spec: "OAuth scope should be: openid, email, profile"\n+ partial implementation: "OAuth scope list is defined in config/oauth.py"

    Orch->>Dev: Updated spec + human partial implementation\n+ all previous context
    Dev->>Dev: Continue from human's starting point
    Dev-->>Orch: Complete implementation

    Orch->>Rev: Review
    Rev-->>Orch: "approved"

    Note over Orch: Pipeline continues normally
```

---

## State Transitions Diagram

```mermaid
stateDiagram-v2
    [*] --> planning: Feature request received

    planning --> planning_review: Spec generated
    planning_review --> planning: Human rejected (revise spec)
    planning_review --> development: Human approved

    development --> development: Tests failed (retry)
    development --> development_review: Tests passed
    development_review --> development: Human rejected
    development_review --> code_review: Human approved

    code_review --> development: Reviewer requested changes
    code_review --> code_review_checkpoint: Reviewer approved
    code_review_checkpoint --> qa_and_devops: Human approved
    code_review_checkpoint --> development: Human rejected

    qa_and_devops --> qa_and_devops: Running in parallel

    qa_and_devops --> final_review: Both QA and DevOps complete
    final_review --> final_review: Human reviews
    final_review --> [*]: Human approved (merge to main)
    final_review --> development: Human rejected (back to development)

    state escalation {
        [*] --> human_engineer_assigned
        human_engineer_assigned --> resolved
    }

    development --> escalation: 3 retries failed
    code_review --> escalation: 3 review cycles, still blocked
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Architecture_Blueprint.md](./Architecture_Blueprint.md) | System architecture blueprint |
| [📄 Build_Guide.md](./Build_Guide.md) | Step-by-step build guide |
| [📄 Component_Breakdown.md](./Component_Breakdown.md) | Component breakdown |
| 📄 **Data_Flow_Diagram.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Tech_Stack.md](./Tech_Stack.md) | Technology stack choices |

⬅️ **Prev:** [04 AI Research Assistant](../04_AI_Research_Assistant/Architecture_Blueprint.md)
