# Build Guide
## Design Case 05: Multi-Agent Software Development Workflow

Four phases from a simple two-agent handoff to a full five-agent pipeline with human checkpoints, retry logic, and shared GitHub workspace.

---

## Phase 1: Two-Agent Handoff (PM → Developer) (Week 1-2)

**Goal:** Build the simplest possible two-agent pipeline. PM writes a spec, Developer implements it. One human checkpoint between them.

**What you build:**
- PM Agent that takes a feature request and produces a `spec.md`
- Developer Agent that reads `spec.md` and produces implementation code
- Simple human checkpoint: "Here's the spec. Approve? (yes/no/edit)"

**PM Agent implementation:**
```python
async def run_pm_agent(feature_request: str) -> str:
    """Generate a feature spec from a user's feature request."""
    response = await client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2000,
        system="""You are a senior product manager at a software company.
Given a feature request, write a clear technical specification with:
1. Summary (1 paragraph)
2. User stories (3-5, each with "As a [user], I want [goal], so that [reason]")
3. Acceptance criteria (testable conditions for each user story)
4. Out of scope (explicitly list what this feature does NOT include)
5. Technical notes (any important implementation constraints)

Format as Markdown.""",
        messages=[{"role": "user", "content": f"Feature request: {feature_request}"}]
    )
    return response.content[0].text
```

**Developer Agent implementation:**
```python
async def run_developer_agent(spec: str, existing_code: str) -> dict:
    """Implement a feature based on a spec."""
    tools = [
        {
            "name": "write_file",
            "description": "Write code to a file",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["path", "content"]
            }
        },
        {
            "name": "run_tests",
            "description": "Run the test suite and return results",
            "input_schema": {"type": "object", "properties": {}, "required": []}
        }
    ]

    response = await client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4000,
        system="""You are a senior software engineer. Implement the feature described in the spec.
Follow the existing code patterns. Write unit tests for every function.
When done, run the tests to verify everything passes.""",
        messages=[{
            "role": "user",
            "content": f"Spec:\n{spec}\n\nExisting codebase:\n{existing_code}"
        }],
        tools=tools
    )
    # Handle tool calls in execution loop
    return await execute_tool_loop(response, tools)
```

**Simple human checkpoint:**
```python
def human_checkpoint(artifact_name: str, artifact_content: str, message: str) -> bool:
    """Pause and ask human for approval. Returns True if approved."""
    print(f"\n{'='*60}")
    print(f"HUMAN CHECKPOINT: {message}")
    print(f"\n{artifact_name}:\n{artifact_content[:500]}...")
    print(f"\nFull artifact at: artifacts/{artifact_name}")
    decision = input("\nApprove? (yes/no/edit): ").strip().lower()
    return decision == "yes"
```

**Success criteria:** Given "Add a password reset feature", the PM produces a spec with 3 user stories, the Developer produces code that compiles, and the checkpoint correctly blocks progress until human approves.

---

## Phase 2: Add Code Review Agent and Retry Logic (Week 3-4)

**Goal:** Add a Code Reviewer that checks the Developer's output and can reject it, triggering a retry loop.

**Code Review Agent:**
```python
REVIEWER_SYSTEM_PROMPT = """You are a senior software engineer conducting a code review.
Review the implementation against the spec for:
1. Correctness: Does it implement all acceptance criteria?
2. Security: Are there any vulnerabilities? (SQL injection, XSS, unvalidated input, etc.)
3. Performance: Any obvious inefficiencies?
4. Test coverage: Are all acceptance criteria tested?
5. Code style: Does it match the existing codebase style?

Return a JSON response:
{
    "decision": "approved" | "changes_requested",
    "summary": "one sentence overall assessment",
    "comments": [
        {
            "file": "path/to/file.py",
            "line": 42,
            "severity": "critical" | "major" | "minor" | "nit",
            "comment": "Explanation of the issue"
        }
    ]
}
"""
```

**Retry logic when reviewer requests changes:**
```python
async def development_with_review(spec: str, existing_code: str, max_retries: int = 3) -> dict:
    for attempt in range(max_retries):
        # Developer implements (or addresses review feedback)
        implementation = await run_developer_agent(spec, existing_code,
            review_feedback=review_result.get("comments") if attempt > 0 else None)

        # Reviewer reviews
        review_result = await run_review_agent(spec, implementation)

        if review_result["decision"] == "approved":
            return implementation

        if attempt < max_retries - 1:
            print(f"Review requested changes (attempt {attempt + 1}/{max_retries})")
        else:
            # 3 attempts and still failing
            return escalate_to_human(
                reason="Developer agent failed to address review feedback after 3 attempts",
                spec=spec,
                implementation=implementation,
                review=review_result
            )
    return implementation
```

**Important:** When retrying after review feedback, pass the review comments to the Developer Agent. "Your last implementation was rejected. Here are the reviewer's specific comments: [comments]. Please address each one."

**Success criteria:** Developer produces code with a security vulnerability → Reviewer correctly identifies it → Developer fixes it on retry → Reviewer approves.

---

## Phase 3: QA Agent and Shared GitHub Workspace (Week 5-7)

**Goal:** Add QA Agent that writes integration tests. All artifacts are stored in a GitHub branch rather than local files.

**GitHub as shared workspace:**
All agents read and write through the GitHub API. This gives you:
- Version history for all artifacts
- Pull request-based human review (reviewers can leave inline comments)
- Branch-per-feature isolation
- CI integration runs on every push

```python
from github import Github

class GitHubWorkspace:
    def __init__(self, repo_name: str, branch_name: str):
        self.gh = Github(os.environ["GITHUB_TOKEN"])
        self.repo = self.gh.get_repo(repo_name)
        self.branch = branch_name

    def write_file(self, path: str, content: str, commit_message: str):
        try:
            # Update existing file
            existing = self.repo.get_contents(path, ref=self.branch)
            self.repo.update_file(path, commit_message, content, existing.sha, branch=self.branch)
        except Exception:
            # Create new file
            self.repo.create_file(path, commit_message, content, branch=self.branch)

    def read_file(self, path: str) -> str:
        contents = self.repo.get_contents(path, ref=self.branch)
        return contents.decoded_content.decode("utf-8")

    def create_pr(self, title: str, body: str) -> str:
        pr = self.repo.create_pull(
            title=title,
            body=body,
            head=self.branch,
            base="main"
        )
        return pr.html_url
```

**QA Agent integration:**
QA Agent reads `spec.md` and the implementation files, then writes comprehensive test files:
```python
QA_SYSTEM_PROMPT = """You are a senior QA engineer. Write integration tests and e2e tests.
For each acceptance criterion in the spec, write at least one test that:
1. Tests the happy path
2. Tests error conditions (invalid input, edge cases)
3. Verifies the response format

Use pytest for Python, jest for JavaScript. Write tests that are independent,
not relying on test execution order. Mock external dependencies."""
```

**Success criteria:** QA Agent correctly writes tests that cover all acceptance criteria. Human reviewer can see the spec, implementation, and tests side-by-side in a GitHub PR.

---

## Phase 4: Full Five-Agent Pipeline with LangGraph (Week 8-10)

**Goal:** Complete pipeline with all five agents, LangGraph orchestration, structured state, and proper handling of parallel vs sequential stages.

**LangGraph state definition:**
```python
from typing import TypedDict, Optional, Literal

class WorkflowState(TypedDict):
    # Input
    feature_request: str
    branch_name: str

    # Artifacts (populated as pipeline progresses)
    spec: Optional[str]
    implementation: Optional[dict]  # {files: {...}, test_results: str}
    review: Optional[dict]  # {decision, comments}
    qa_tests: Optional[dict]  # {files: {...}, coverage_report}
    deployment_config: Optional[dict]  # {dockerfile, ci_config, k8s_manifests}

    # Control flow
    current_stage: Literal["planning", "development", "review", "qa", "devops", "done"]
    retry_counts: dict  # {stage: count}
    human_approvals: dict  # {stage: bool}

    # Audit
    stage_timestamps: dict
    error_log: list[str]
```

**Agent that needs to handle parallel execution (QA and DevOps can run in parallel):**
```python
# After code review approval, QA and DevOps can run concurrently
workflow.add_node("qa_agent", run_qa_agent)
workflow.add_node("devops_agent", run_devops_agent)
workflow.add_node("parallel_join", wait_for_both)

# Route to both in parallel after review approval
workflow.add_conditional_edges(
    "review_checkpoint",
    lambda state: "parallel" if state["review"]["decision"] == "approved" else "developer",
    {"parallel": ["qa_agent", "devops_agent"], "developer": "developer"}
)
workflow.add_edge("qa_agent", "parallel_join")
workflow.add_edge("devops_agent", "parallel_join")
workflow.add_edge("parallel_join", "final_checkpoint")
```

**Human checkpoint with async wait:**
```python
from langgraph.checkpoint.memory import MemorySaver

# Checkpointer persists state across interrupts
checkpointer = MemorySaver()

# At human checkpoint, interrupt execution
workflow.add_node("spec_checkpoint", interrupt_for_human_review)

# Resume when human provides input
def resume_workflow(thread_id: str, human_decision: str, feedback: str = ""):
    config = {"configurable": {"thread_id": thread_id}}
    return app.invoke(
        {"human_decision": human_decision, "feedback": feedback},
        config=config
    )
```

**Success criteria:** Submit "Add OAuth login feature" → pipeline produces spec, implementation, passing tests, and deployment config autonomously with 5 human review checkpoints, completing the full software development cycle in under 30 minutes of automated work.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Architecture_Blueprint.md](./Architecture_Blueprint.md) | System architecture blueprint |
| 📄 **Build_Guide.md** | ← you are here |
| [📄 Component_Breakdown.md](./Component_Breakdown.md) | Component breakdown |
| [📄 Data_Flow_Diagram.md](./Data_Flow_Diagram.md) | Data flow diagram |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Tech_Stack.md](./Tech_Stack.md) | Technology stack choices |

⬅️ **Prev:** [04 AI Research Assistant](../04_AI_Research_Assistant/Architecture_Blueprint.md)
