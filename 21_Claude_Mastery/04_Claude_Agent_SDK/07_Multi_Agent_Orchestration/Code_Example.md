# Multi-Agent Orchestration — Code Example

## Basic Orchestrator + Worker Pattern

```python
"""
Orchestrator delegates parallel sub-tasks to specialized workers.
"""
import asyncio
import json
from claude_agent_sdk import Agent, tool


# ── SPECIALIZED WORKER TOOLS ──────────────────────────────────

@tool
def summarize_text(text: str, max_sentences: int = 3) -> str:
    """Summarize text in a specified number of sentences.
    Returns a concise summary."""
    # In production: use Claude or an NLP library
    words = text.split()[:50]  # simplified mock
    return f"Summary ({max_sentences} sentences): {' '.join(words)}..."

@tool
def extract_keywords(text: str, count: int = 5) -> list[str]:
    """Extract the most important keywords from text.
    Returns a list of keyword strings."""
    # Simplified mock - in production: use TF-IDF or KeyBERT
    words = [w.strip(".,!?") for w in text.split() if len(w) > 5]
    unique_words = list(dict.fromkeys(words))[:count]
    return unique_words

@tool
def classify_sentiment(text: str) -> dict:
    """Classify the sentiment of text.
    Returns: {sentiment: positive/negative/neutral, confidence: 0-1}"""
    # Simplified mock
    positive_words = ["good", "great", "excellent", "happy", "best"]
    negative_words = ["bad", "poor", "terrible", "worst", "fail"]
    
    text_lower = text.lower()
    pos_count = sum(1 for w in positive_words if w in text_lower)
    neg_count = sum(1 for w in negative_words if w in text_lower)
    
    if pos_count > neg_count:
        return {"sentiment": "positive", "confidence": 0.8}
    elif neg_count > pos_count:
        return {"sentiment": "negative", "confidence": 0.8}
    return {"sentiment": "neutral", "confidence": 0.6}


# ── PARALLEL WORKERS ─────────────────────────────────────────

async def run_summary_worker(document: str, doc_id: str) -> dict:
    """Worker: summarize one document."""
    worker = Agent(
        model="claude-haiku-4-5",  # cheaper model for workers
        tools=[summarize_text],
        system="You are a text summarization specialist. Summarize documents concisely.",
        max_steps=3
    )
    result = await worker.arun(f"Summarize this document:\n\n{document}")
    return {"doc_id": doc_id, "summary": result, "worker": "summary"}

async def run_keyword_worker(document: str, doc_id: str) -> dict:
    """Worker: extract keywords from one document."""
    worker = Agent(
        model="claude-haiku-4-5",
        tools=[extract_keywords],
        system="You are a keyword extraction specialist. Extract the most important terms.",
        max_steps=3
    )
    result = await worker.arun(f"Extract 5 key terms from:\n\n{document}")
    return {"doc_id": doc_id, "keywords": result, "worker": "keywords"}

async def run_sentiment_worker(document: str, doc_id: str) -> dict:
    """Worker: classify document sentiment."""
    worker = Agent(
        model="claude-haiku-4-5",
        tools=[classify_sentiment],
        system="You are a sentiment analysis specialist.",
        max_steps=3
    )
    result = await worker.arun(f"Classify the sentiment of:\n\n{document}")
    return {"doc_id": doc_id, "sentiment_analysis": result, "worker": "sentiment"}


# ── ORCHESTRATOR ──────────────────────────────────────────────

@tool
def analyze_document_parallel(document: str, doc_id: str) -> str:
    """Spawn three parallel worker agents to analyze a document:
    - Summary worker
    - Keyword extraction worker
    - Sentiment analysis worker
    
    Returns combined JSON analysis results."""
    results = asyncio.run(asyncio.gather(
        run_summary_worker(document, doc_id),
        run_keyword_worker(document, doc_id),
        run_sentiment_worker(document, doc_id)
    ))
    return json.dumps({
        "doc_id": doc_id,
        "analyses": {r["worker"]: r for r in results}
    }, indent=2)

@tool
def compile_report(analyses: list[str], title: str) -> str:
    """Compile multiple document analyses into a final report.
    analyses: list of JSON analysis strings (one per document).
    Returns a formatted Markdown report."""
    report_lines = [f"# {title}", ""]
    for analysis_json in analyses:
        analysis = json.loads(analysis_json)
        report_lines.append(f"## Document: {analysis['doc_id']}")
        report_lines.append(f"**Summary**: {analysis['analyses'].get('summary', {}).get('summary', 'N/A')}")
        report_lines.append(f"**Keywords**: {analysis['analyses'].get('keywords', {}).get('keywords', 'N/A')}")
        report_lines.append(f"**Sentiment**: {analysis['analyses'].get('sentiment', {}).get('sentiment_analysis', 'N/A')}")
        report_lines.append("")
    return "\n".join(report_lines)

orchestrator = Agent(
    model="claude-sonnet-4-6",
    tools=[analyze_document_parallel, compile_report],
    system="""You are a document analysis orchestrator.

For each document:
1. Call analyze_document_parallel() — this spawns 3 parallel workers automatically
2. Collect all results
3. Call compile_report() to generate the final report

Process all documents before compiling.""",
    max_steps=15
)


# ── MAIN ─────────────────────────────────────────────────────

if __name__ == "__main__":
    documents = [
        ("doc_001", "Our product launch was excellent this quarter. Sales exceeded all targets."),
        ("doc_002", "The deployment failed due to configuration errors. The team was frustrated."),
        ("doc_003", "Customer satisfaction scores remained neutral this month. No major changes."),
    ]
    
    task = "Analyze these documents and compile a report:\n\n"
    for doc_id, text in documents:
        task += f"Document {doc_id}:\n{text}\n\n"
    task += "Compile them into a final analysis report."
    
    result = orchestrator.run(task)
    print(result)
```

---

## Sequential Fan-Out with Rate Limit Control

```python
"""
Fan-out with concurrency control to respect API rate limits.
"""
import asyncio
from claude_agent_sdk import Agent, tool

MAX_CONCURRENT_WORKERS = 3  # Max parallel API calls

async def run_worker_bounded(
    semaphore: asyncio.Semaphore,
    task: str,
    worker_id: int
) -> dict:
    async with semaphore:
        worker = Agent(
            model="claude-haiku-4-5",
            tools=[],  # no tools for this example
            system="You are a classification specialist. Classify text into a category.",
            max_steps=2
        )
        result = await worker.arun(task)
        return {"worker_id": worker_id, "result": result}

async def fan_out(tasks: list[str]) -> list[dict]:
    """Process tasks in parallel, max MAX_CONCURRENT_WORKERS at once."""
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_WORKERS)
    results = await asyncio.gather(*[
        run_worker_bounded(semaphore, task, i)
        for i, task in enumerate(tasks)
    ])
    return list(results)

if __name__ == "__main__":
    tasks = [
        "Classify: 'The product broke after one use'",
        "Classify: 'Best purchase I've ever made!'",
        "Classify: 'It's okay, nothing special'",
        "Classify: 'Terrible customer service, never again'",
        "Classify: 'Works as advertised'",
    ]
    
    results = asyncio.run(fan_out(tasks))
    for r in results:
        print(f"Worker {r['worker_id']}: {r['result']}")
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | Orchestration patterns in depth |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [Agent Memory](../06_Agent_Memory/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Subagents](../08_Subagents/Theory.md)
