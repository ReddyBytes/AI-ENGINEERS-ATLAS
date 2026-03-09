# Tech Stack
## Design Case 05: Multi-Agent Software Development Workflow

Technology choices for the orchestration layer, each specialist agent, the shared workspace, and the evaluation pipeline.

---

## Full Stack Table

| Component | Technology Choice | Why This Choice | Alternatives | When to Switch |
|---|---|---|---|---|
| **Orchestration Framework** | LangGraph | Stateful graph, deterministic routing, native human-in-the-loop interrupts, checkpointing/resume, production-ready. | CrewAI, AutoGen, Temporal, custom Python | Temporal for more complex workflow SLAs, durable execution guarantees, and enterprise retry/alerting needs. Custom Python if LangGraph's graph model doesn't fit your branching logic. |
| **PM Agent LLM** | Claude 3.5 Sonnet | Excellent at structured output, good at following formatting rules for specs, understands software project context. | GPT-4o | GPT-4o comparable quality. Claude tends to be more precise about following output format requirements. |
| **Developer Agent LLM** | Claude 3.5 Sonnet | Best code generation quality among API-available models. Strong at writing tests alongside implementation. 200K context handles large codebases. | GPT-4o, DeepSeek Coder V2 | GPT-4o for comparable quality. DeepSeek Coder V2 (self-hosted) for privacy requirements. |
| **Reviewer Agent LLM** | Claude 3.5 Sonnet | Strong at identifying code issues, security vulnerabilities, and spec deviations. Outputs structured JSON reviews reliably. | GPT-4o | Benchmark both on code review quality for your codebase. |
| **QA Agent LLM** | Claude 3.5 Sonnet | Good at reasoning about test coverage, understanding edge cases from acceptance criteria. | GPT-4o | Same — benchmark both. |
| **DevOps Agent LLM** | Claude 3.5 Haiku or GPT-4o-mini | Deployment config generation (Dockerfiles, CI YAML, K8s manifests) is more template-like than complex reasoning. Cheaper, faster model is sufficient. | Claude 3.5 Sonnet | Upgrade to Sonnet if Haiku produces frequent validation failures on complex K8s configurations. |
| **Shared Workspace** | GitHub (via REST API + PyGithub) | Industry standard, native PR-based review for human checkpoints, diff views, CI integration, version history, branch-per-feature pattern. | GitLab, Azure DevOps, local filesystem | GitLab if your organization uses GitLab. Azure DevOps for Microsoft-aligned organizations. Local filesystem only for development/testing. |
| **Static Analysis (Python)** | ruff (style) + bandit (security) | ruff: fastest Python linter, replaces flake8/isort/black. bandit: standard Python security scanner. Both are zero-config on most projects. | flake8 + pylint + semgrep | semgrep for more sophisticated semantic analysis (cross-file, custom rules). Replace bandit with semgrep for advanced security scanning. |
| **Static Analysis (JS/TS)** | ESLint + security-plugin + typescript-eslint | Standard ecosystem, excellent TypeScript support, security plugin adds common vulnerability detection. | Biome (faster, all-in-one), JSHint | Biome for faster linting in CI. |
| **Dockerfile Linting** | hadolint | Most comprehensive Dockerfile linter, detects 100+ common issues (non-root user, using latest tag, unnecessary RUN layers). | Docker Scout (paid) | Docker Scout for integrated CVE scanning beyond just linting. |
| **K8s Manifest Validation** | kubeval | Validates Kubernetes manifests against the official K8s JSON Schema. Catches invalid field names, wrong types, missing required fields. | kubeconform (faster, more maintained), Datree | kubeconform as a direct upgrade to kubeval (same concept, actively maintained). |
| **Test Runner** | pytest (Python) / jest (JS) in Docker | Standard test runners, Docker isolation prevents tests from affecting the local environment or each other. | unittest (Python), vitest (JS/TS) | vitest for new TypeScript projects (faster than jest, better ESM support). |
| **Human Notification** | Slack webhooks + email | Slack for immediate notification with approval buttons. Email for async notification with PR link. | PagerDuty (for high-priority escalations), JIRA transitions | Add PagerDuty for escalation flow when agents fail 3 times (these are high-priority situations requiring immediate human attention). |
| **Checkpoint Persistence** | PostgreSQL (via LangGraph SqliteSaver or custom) | Workflow state must survive crashes. Postgres gives durable, queryable checkpoint storage. For dev: MemorySaver (in-memory). | Redis (for speed), MongoDB (flexible schema) | Redis if checkpoint reads/writes become a latency concern (unlikely for this workflow duration). |
| **Cost Tracking** | LangSmith + custom token counter | LangSmith traces every agent call with token counts. Custom code aggregates per-pipeline cost. | Langfuse (self-hosted) | Langfuse for self-hosted observability if you can't send data to LangSmith. |

---

## LLM Assignment Rationale

Each agent gets the right model for its task complexity:

| Agent | Model | Why |
|---|---|---|
| PM Agent | Claude 3.5 Sonnet | Complex reasoning about requirements, structured output quality matters |
| Developer Agent | Claude 3.5 Sonnet | Code quality is paramount, 200K context for large codebase context |
| Reviewer Agent | Claude 3.5 Sonnet | Security and quality analysis requires careful reasoning |
| QA Agent | Claude 3.5 Sonnet | Test case reasoning requires understanding acceptance criteria edge cases |
| DevOps Agent | Claude 3.5 Haiku | Template-like output, fast validation, 10x cost savings |
| **Orchestrator** | **No LLM** | **Deterministic Python — no LLM in the control path** |

**Cost per pipeline run (5-agent feature, typical complexity):**

| Phase | Input Tokens | Output Tokens | Cost |
|---|---|---|---|
| PM Agent (spec) | 2,000 | 1,000 | $0.021 |
| Developer Agent (1 attempt) | 8,000 | 3,000 | $0.069 |
| Reviewer Agent (1 review cycle) | 6,000 | 800 | $0.030 |
| QA Agent | 5,000 | 2,000 | $0.045 |
| DevOps Agent (Haiku) | 3,000 | 1,500 | $0.005 |
| **Total (happy path, no retries)** | | | **~$0.17** |

With 2 retry cycles in development: add ~$0.14 → **~$0.31 total**

At 1,000 features/month: **~$310/month in LLM costs** for the entire pipeline. This is extraordinarily cheap compared to 1,000 developer-hours of manual development.

---

## GitHub API Usage Patterns

The GitHub integration is central to this design. Key API patterns:

```python
# Creating a feature branch
repo.create_git_ref(
    ref=f"refs/heads/feature/{feature_slug}",
    sha=repo.get_branch("main").commit.sha
)

# Writing a file (create or update)
def upsert_file(repo, path: str, content: str, branch: str, message: str):
    try:
        existing = repo.get_contents(path, ref=branch)
        repo.update_file(path, message, content, existing.sha, branch=branch)
    except GithubException as e:
        if e.status == 404:
            repo.create_file(path, message, content, branch=branch)

# Creating a PR for human review
pr = repo.create_pull(
    title=f"[AI Pipeline] {feature_name}",
    body=f"""## AI-Generated Feature: {feature_name}

**Feature Request:** {feature_request}

**Pipeline Status:** Awaiting human review at {current_stage} stage.

### Review Checklist
- [ ] Spec addresses the business requirement
- [ ] Implementation is correct and secure
- [ ] Tests cover acceptance criteria
- [ ] Deployment config is production-ready

**Approve by commenting:** `@ai-orchestrator approve`
**Request changes:** `@ai-orchestrator reject: <reason>`""",
    head=branch_name,
    base="main"
)

# Watching for human approval via PR comments
comments = pr.get_issue_comments()
for comment in comments:
    if "@ai-orchestrator approve" in comment.body:
        return "approved", ""
    if "@ai-orchestrator reject:" in comment.body:
        reason = comment.body.split("reject:")[1].strip()
        return "rejected", reason
```

---

## Alternative: GitLab Instead of GitHub

If your organization uses GitLab, the architecture is identical. Replace:
- PyGithub → `python-gitlab`
- GitHub PR comments → GitLab MR notes
- GitHub Actions → GitLab CI/CD (`.gitlab-ci.yml`)

The LangGraph orchestrator and all five agent implementations are unchanged. Only the workspace client changes.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Architecture_Blueprint.md](./Architecture_Blueprint.md) | System architecture blueprint |
| [📄 Build_Guide.md](./Build_Guide.md) | Step-by-step build guide |
| [📄 Component_Breakdown.md](./Component_Breakdown.md) | Component breakdown |
| [📄 Data_Flow_Diagram.md](./Data_Flow_Diagram.md) | Data flow diagram |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Tech_Stack.md** | ← you are here |

⬅️ **Prev:** [04 AI Research Assistant](../04_AI_Research_Assistant/Architecture_Blueprint.md)
