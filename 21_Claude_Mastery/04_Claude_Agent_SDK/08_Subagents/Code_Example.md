# Subagents — Code Example

## Basic Subagent Spawn Pattern

```python
"""
Subagent patterns: spawn, isolate, return results.
"""
import asyncio
import json
from claude_agent_sdk import Agent, tool


# ── SIMPLE SUBAGENT SPAWN ─────────────────────────────────────

@tool
def analyze_review(review_text: str, product_id: str) -> dict:
    """Spawn a specialized subagent to deeply analyze a product review.
    Returns structured analysis with sentiment, key points, and action items.
    Use for reviews longer than 3 sentences."""
    
    # Worker has only the analysis tool — no write access, no external calls
    worker = Agent(
        model="claude-haiku-4-5",
        tools=[],  # this worker uses no tools — pure reasoning task
        system="""You are a product review analyst. Analyze the given review and return JSON:
        {
          "sentiment": "positive|negative|neutral",
          "score": 1-10,
          "key_positives": ["..."],
          "key_negatives": ["..."],
          "action_items": ["..."],
          "summary": "one sentence summary"
        }
        Return ONLY valid JSON, no other text.""",
        max_steps=2
    )
    
    result = worker.run(f"Analyze this review for product {product_id}:\n\n{review_text}")
    
    try:
        return json.loads(result)
    except json.JSONDecodeError:
        return {"error": "Worker returned invalid JSON", "raw": result[:200]}

@tool
def batch_summarize(texts: list[str], focus: str = "main points") -> list[str]:
    """Spawn one subagent per text to summarize them in parallel.
    texts: list of text strings to summarize.
    focus: what aspect to focus on (default: 'main points').
    Returns list of summaries in the same order as input."""
    
    async def summarize_one(text: str, idx: int) -> tuple[int, str]:
        worker = Agent(
            model="claude-haiku-4-5",
            tools=[],
            system=f"Summarize text focusing on {focus}. Be concise (2-3 sentences max).",
            max_steps=2
        )
        summary = await worker.arun(text)
        return (idx, summary)
    
    async def run_all():
        results = await asyncio.gather(*[
            summarize_one(text, i) for i, text in enumerate(texts)
        ])
        return [r[1] for r in sorted(results, key=lambda x: x[0])]
    
    return asyncio.run(run_all())


# ── PARALLEL SPECIALIZED WORKERS ─────────────────────────────

@tool
def comprehensive_code_review(code: str, language: str) -> dict:
    """Spawn 3 specialized review workers to analyze code from different angles:
    - Security worker: finds vulnerabilities
    - Performance worker: finds bottlenecks  
    - Style worker: checks conventions
    
    Runs all 3 in parallel and returns combined findings."""
    
    async def security_worker() -> dict:
        agent = Agent(
            model="claude-sonnet-4-6",
            tools=[],
            system="You are a security expert. Review code for vulnerabilities only. "
                   "Return JSON: {issues: [{type, severity, description}]}",
            max_steps=3
        )
        result = await agent.arun(f"Review this {language} code for security:\n\n{code}")
        try:
            return {"type": "security", "findings": json.loads(result)}
        except:
            return {"type": "security", "findings": {"issues": [], "note": result[:200]}}
    
    async def performance_worker() -> dict:
        agent = Agent(
            model="claude-haiku-4-5",
            tools=[],
            system="You are a performance expert. Review code for performance issues only. "
                   "Return JSON: {issues: [{type, severity, description}]}",
            max_steps=3
        )
        result = await agent.arun(f"Review this {language} code for performance:\n\n{code}")
        try:
            return {"type": "performance", "findings": json.loads(result)}
        except:
            return {"type": "performance", "findings": {"issues": [], "note": result[:200]}}
    
    async def style_worker() -> dict:
        agent = Agent(
            model="claude-haiku-4-5",
            tools=[],
            system="You are a code style expert. Review code for style issues only. "
                   "Return JSON: {issues: [{type, severity, description}]}",
            max_steps=3
        )
        result = await agent.arun(f"Review this {language} code for style:\n\n{code}")
        try:
            return {"type": "style", "findings": json.loads(result)}
        except:
            return {"type": "style", "findings": {"issues": [], "note": result[:200]}}
    
    async def run_all_workers():
        results = await asyncio.gather(
            security_worker(),
            performance_worker(),
            style_worker()
        )
        return {r["type"]: r["findings"] for r in results}
    
    return asyncio.run(run_all_workers())


# ── ORCHESTRATOR THAT USES SUBAGENTS ─────────────────────────

orchestrator = Agent(
    model="claude-sonnet-4-6",
    tools=[analyze_review, batch_summarize, comprehensive_code_review],
    system="""You are a content analysis orchestrator.

    For review analysis tasks: use analyze_review() for each review.
    For bulk summarization: use batch_summarize() to process all texts at once.
    For code review: use comprehensive_code_review() for full analysis.
    
    Always present findings in a clear, structured format.""",
    max_steps=10
)


# ── MAIN ─────────────────────────────────────────────────────

if __name__ == "__main__":
    # Example 1: Review analysis via subagent
    reviews = [
        ("prod_001", "This product completely changed my workflow. The build quality is "
                     "exceptional, the documentation is clear, and customer support is "
                     "fantastic. Highly recommend to anyone in the field."),
        ("prod_002", "Disappointed. The product stopped working after two days. "
                     "Customer service was unhelpful. I want a refund."),
    ]
    
    for product_id, review_text in reviews:
        result = orchestrator.run(
            f"Analyze this review for product {product_id}:\n{review_text}"
        )
        print(f"\n=== {product_id} ===")
        print(result)
    
    # Example 2: Parallel code review
    sample_code = """
def get_user_data(user_id):
    query = "SELECT * FROM users WHERE id = " + user_id  # SQL injection!
    results = db.execute(query)
    for row in results:  # no limit on results
        data.append(row)
    return data
"""
    
    result = orchestrator.run(
        f"Do a comprehensive code review of this Python code:\n{sample_code}"
    )
    print("\n=== Code Review ===")
    print(result)
```

---

## Subagent with Context Passing

```python
"""
Show exactly what context to pass vs. leave out.
"""
from claude_agent_sdk import Agent, tool

# Simulated large dataset
FULL_DATASET = {
    "project_alpha": {
        "team": ["Alice", "Bob", "Carol"],
        "budget": 500000,
        "milestones": [
            {"name": "Design", "status": "complete", "date": "2026-01-15"},
            {"name": "Development", "status": "in_progress", "date": "2026-03-01"},
            {"name": "Testing", "status": "pending", "date": "2026-04-15"},
            {"name": "Launch", "status": "pending", "date": "2026-05-01"},
        ],
        "risks": ["Scope creep", "Key person dependency", "API integration delays"],
        "budget_spent": 180000,
        "notes": "..." * 500  # large irrelevant notes field
    }
    # ... 99 more projects
}

@tool
def assess_project_risk(project_name: str) -> dict:
    """Spawn a risk assessment subagent for a project.
    Only passes the relevant risk data — not the full project record.
    Returns: {overall_risk: low|medium|high, key_risks: [...], recommendation: str}"""
    
    if project_name not in FULL_DATASET:
        raise KeyError(f"Project not found: {project_name}")
    
    project = FULL_DATASET[project_name]
    
    # Only pass what the subagent needs — not the full project record
    relevant_context = {
        "name": project_name,
        "budget_utilization": f"{(project['budget_spent'] / project['budget']) * 100:.1f}%",
        "milestone_status": [
            {"name": m["name"], "status": m["status"]} 
            for m in project["milestones"]
        ],
        "known_risks": project["risks"]
    }
    
    risk_agent = Agent(
        model="claude-haiku-4-5",
        tools=[],
        system="""You are a project risk assessor. Given project context, return JSON:
        {
          "overall_risk": "low|medium|high",
          "risk_score": 1-10,
          "key_risks": ["specific risk 1", "specific risk 2"],
          "recommendation": "brief action recommendation"
        }""",
        max_steps=2
    )
    
    result = risk_agent.run(
        f"Assess risk for this project:\n{json.dumps(relevant_context, indent=2)}"
    )
    
    try:
        return json.loads(result)
    except:
        return {"overall_risk": "unknown", "error": "Could not parse assessment"}
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [Multi-Agent Orchestration](../07_Multi_Agent_Orchestration/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Handoffs](../09_Handoffs/Theory.md)
