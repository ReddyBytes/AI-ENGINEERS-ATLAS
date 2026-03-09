# Component Breakdown
## Design Case 05: Multi-Agent Software Development Workflow

Deep dive into the five specialist agents, the orchestrator, the shared workspace, and the human-in-the-loop system that makes this pipeline safe to run autonomously.

---

## 1. Orchestrator Agent

The orchestrator is the most important architectural decision in this system. It is **not an LLM** — it is deterministic Python code using LangGraph.

**Why not an LLM orchestrator?**

An LLM orchestrator would decide dynamically which agent to run next, how to route failures, and when to escalate to humans. This sounds powerful but creates unpredictable failure modes:
- The orchestrator-LLM might decide to skip code review because "the code looks good"
- It might route to the wrong agent
- It might fail in ways that are hard to debug (the LLM's reasoning is not auditable)

A deterministic orchestrator:
- Always runs stages in the defined order (plan → implement → review → QA → deploy)
- Always enforces human checkpoints at defined points
- Always applies the same retry logic (3 attempts, then escalate)
- Is fully auditable (every decision is explicit code, every state change is logged)

**Orchestrator responsibilities:**
```
State management:
- Load/save pipeline state (persisted to PostgreSQL via LangGraph checkpointer)
- Track which stage is active, what artifacts have been produced
- Track retry counts per stage
- Track which human checkpoints have been approved

Agent invocation:
- Build the correct context for each agent (what spec, what code, what review feedback)
- Pass the previous agent's output as the next agent's input
- Validate that each agent's output meets the required contract
- Log all agent calls with timestamps and token counts

Human checkpoint handling:
- Pause execution and send notification (Slack, email, webhook)
- Wait for human response (polling or webhook callback)
- If approved: continue to next stage
- If rejected: return to previous stage with feedback
- If no response in 48 hours: escalate and alert

Failure handling:
- Catch agent errors (API failures, validation failures, test failures)
- Apply retry with enriched context
- After 3 failures: escalate to human with full context
- Never leave the pipeline in an undefined state
```

---

## 2. Product Manager Agent

The PM Agent translates a vague feature request into a precise technical specification that the Developer Agent can implement deterministically.

**System prompt design:**

The PM Agent's system prompt is the most important document in the pipeline. A poorly written spec will cause the Developer Agent to implement the wrong thing, which the Reviewer will catch, which means retry loops. Invest in the system prompt.

```
Role: You are a senior product manager at a software engineering company.
You write precise, implementable specifications for engineering teams.

When writing a spec, follow these exact rules:
1. User stories MUST be in format: "As a [specific user type], I want [specific capability], so that [specific benefit]"
2. Acceptance criteria MUST be testable boolean conditions: "GIVEN X WHEN Y THEN Z"
3. Out of scope section MUST list at least 3 things this feature does NOT do
4. Do NOT include implementation suggestions (that's the developer's job)
5. Every ambiguity in the feature request should be resolved explicitly in the spec (make a decision, don't leave it open)

Example of bad acceptance criterion: "The feature should work well"
Example of good acceptance criterion: "GIVEN a user with a verified email, WHEN they click 'Reset Password', THEN they receive an email within 60 seconds containing a reset link that expires in 1 hour"
```

**Tools available to the PM Agent:**
- `read_existing_specs(product_area)` — Read related existing specs for consistency
- `read_existing_features(product_area)` — Read what currently exists to avoid duplication
- `create_linear_ticket(spec_text)` — Optional: create tracking ticket
- No write access to code — this agent should not touch the implementation

**Validation contract:**
The orchestrator validates the spec before presenting it to the human reviewer:
- At least 3 user stories
- Every user story has at least 2 acceptance criteria in GIVEN-WHEN-THEN format
- Out-of-scope section exists and has at least 2 items
- No ambiguous terms (words like "fast", "simple", "good" trigger a validation warning)

---

## 3. Developer Agent

The Developer Agent reads the approved spec, reads the existing codebase, and produces an implementation that satisfies all acceptance criteria.

**The hardest challenge:** Code generation for a real codebase requires understanding context, conventions, and patterns that aren't explicitly stated in the spec.

**Context assembly for the Developer Agent:**

```python
async def build_developer_context(spec: str, workspace: GitHubWorkspace) -> str:
    # Read the spec
    context = f"SPECIFICATION:\n{spec}\n\n"

    # Read the most relevant existing code (not the entire repo)
    # Heuristic: read files that the spec's keywords appear in
    relevant_files = find_relevant_files(spec, workspace)
    for file_path in relevant_files[:10]:  # Limit to 10 most relevant files
        content = workspace.read_file(file_path)
        context += f"EXISTING FILE {file_path}:\n{content}\n\n"

    # Read style conventions
    if workspace.file_exists("CONTRIBUTING.md"):
        context += f"CONTRIBUTING GUIDE:\n{workspace.read_file('CONTRIBUTING.md')}\n\n"

    return context
```

**Output validation:**
The Developer Agent's output is validated by actually running the tests:
```python
async def validate_developer_output(implementation: dict) -> tuple[bool, str]:
    # Write all files to a temp directory
    with tempfile.TemporaryDirectory() as tmpdir:
        for file_path, content in implementation["files"].items():
            write_to_temp(tmpdir, file_path, content)

        # Run the test suite
        result = subprocess.run(
            ["python", "-m", "pytest", "--tb=short", "-q"],
            cwd=tmpdir, capture_output=True, text=True, timeout=120
        )

        passed = result.returncode == 0
        return passed, result.stdout + result.stderr
```

If tests fail, the orchestrator feeds the test output back to the Developer Agent: "Your implementation failed these tests: [test output]. Please fix the failing tests."

---

## 4. Code Reviewer Agent

The Reviewer Agent is the quality gate. It sees the implementation + the spec + the diff from the base branch, and produces structured review comments.

**What the Reviewer checks (prioritized):**

1. **Critical (blocks approval):**
   - Missing acceptance criteria implementation (spec says X, code doesn't do X)
   - Security vulnerabilities (SQL injection, unvalidated user input, hardcoded credentials)
   - Tests missing for critical paths
   - Obvious bugs (off-by-one errors, null pointer risks, uncaught exceptions)

2. **Major (requests changes):**
   - Poor error handling (swallowed exceptions, missing error messages)
   - Performance issues (N+1 queries, synchronous I/O in async context)
   - Missing edge case handling mentioned in spec
   - Code style significantly inconsistent with codebase

3. **Minor (suggestions, not blocking):**
   - Code could be simplified
   - Better variable names
   - Redundant code

4. **Nit (informational only):**
   - Typos in comments
   - Missing docstrings on internal functions
   - Small formatting issues

**Reviewer tools:**
- `run_static_analysis(language, code)` — ruff (Python), eslint (JS/TS)
- `run_security_scan(code)` — bandit (Python), semgrep
- `check_test_coverage(test_files, source_files)` — coverage.py, nyc

**Why have an AI reviewer if tests already passed?**
Tests only catch what they test. The Reviewer catches:
- Missing tests for edge cases (tests pass because the edge case wasn't tested)
- Security issues (tests rarely test for injection attacks)
- Design problems (the code works but is structured in a way that will be hard to maintain)
- Spec deviation (the code does something slightly different from what was specified)

---

## 5. QA Agent

The QA Agent writes tests that the Developer Agent didn't write — specifically, integration tests and end-to-end tests that test the feature as a user would experience it.

**Difference from Developer Agent's unit tests:**

| Test Type | Who Writes It | What It Tests |
|---|---|---|
| Unit tests | Developer Agent | Individual functions in isolation (mocked dependencies) |
| Integration tests | QA Agent | Functions working together with real dependencies (real DB, real queue) |
| E2E tests | QA Agent | Complete user workflows (simulate API calls, verify database state) |

**QA Agent's specific context needs:**

The QA Agent needs to know:
- All acceptance criteria (from spec.md)
- The API surface (what endpoints exist, what format they accept)
- Test fixtures and factories (how to create test data)
- Testing conventions in the codebase (pytest fixtures? test database setup?)

```python
QA_SYSTEM_PROMPT = """You are a senior QA engineer.
Write comprehensive integration and e2e tests for the implemented feature.

For each acceptance criterion in the spec:
1. Write a test that verifies the GIVEN-WHEN-THEN conditions exactly
2. Write a test for the error case (what happens if the GIVEN conditions aren't met?)
3. Write a test for edge cases mentioned in the spec

DO NOT write unit tests for internal functions - those are the developer's job.
Focus on testing behavior from the outside (API calls, database state, response format).

Use pytest with the existing test fixtures in conftest.py.
Use factories (UserFactory, etc.) for test data - don't hardcode test values."""
```

---

## 6. DevOps Agent

The DevOps Agent takes the working, tested implementation and creates the infrastructure configuration to deploy it.

**What it produces:**
- `Dockerfile` — containerizes the application
- `.github/workflows/ci.yml` — CI pipeline (lint, test, build, push)
- `k8s/deployment.yaml` — Kubernetes deployment manifest
- `k8s/service.yaml` — Kubernetes service manifest
- `k8s/hpa.yaml` — Horizontal Pod Autoscaler (for scalable services)

**Validation tools:**
- `hadolint Dockerfile` — Dockerfile linter (catches security issues, bad practices)
- `kubeval k8s/*.yaml` — Validates Kubernetes manifest schema
- `docker build --no-cache .` — Verify the Dockerfile actually builds

**DevOps Agent system prompt focus:**
```
You write production-ready deployment configuration.
Rules:
- Dockerfile: Use multi-stage builds. Production image contains only what's needed to run.
- Do NOT include dev dependencies in production image.
- Always set resource limits (CPU and memory) in K8s manifests.
- Always define readiness and liveness probes.
- Always set a non-root user in Dockerfile.
- Set LOG_LEVEL from environment variable, not hardcoded.
- Tag images with git SHA, not "latest".
```

---

## 7. Shared GitHub Workspace

Using GitHub as the shared workspace is a key architectural decision. Every artifact is a file in a branch, every change is a commit, every stage transition can be a PR comment.

**Branch-per-feature strategy:**
```
main
└── feature/ai-password-reset-20240309 (created by orchestrator)
    ├── spec.md                          (commit: "PM Agent: Add password reset spec")
    ├── src/auth/password_reset.py       (commit: "Developer Agent: Implement password reset")
    ├── tests/test_password_reset.py     (commit: "Developer Agent: Unit tests for password reset")
    ├── tests/integration/test_reset.py  (commit: "QA Agent: Integration tests")
    ├── Dockerfile                       (commit: "DevOps Agent: Containerization")
    └── .github/workflows/ci.yml         (commit: "DevOps Agent: CI pipeline")
```

**Human review via GitHub PRs:**
When the orchestrator reaches a human checkpoint, it creates or updates a PR comment with:
- Which stage just completed
- What was produced (with diff)
- What needs human approval
- A link to approve/reject via webhook

The human can review code in GitHub's native diff view, leave inline comments, and approve with a comment like `@ai-orchestrator approve` or `@ai-orchestrator reject: the spec missed the case where the user's email is unverified`.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Architecture_Blueprint.md](./Architecture_Blueprint.md) | System architecture blueprint |
| [📄 Build_Guide.md](./Build_Guide.md) | Step-by-step build guide |
| 📄 **Component_Breakdown.md** | ← you are here |
| [📄 Data_Flow_Diagram.md](./Data_Flow_Diagram.md) | Data flow diagram |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Tech_Stack.md](./Tech_Stack.md) | Technology stack choices |

⬅️ **Prev:** [04 AI Research Assistant](../04_AI_Research_Assistant/Architecture_Blueprint.md)
