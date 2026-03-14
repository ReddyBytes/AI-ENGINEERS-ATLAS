# Research Agent — Step-by-Step Implementation

## Complete Working Code

```python
# research_agent.py
# Run: pip install langgraph
# Then: python research_agent.py

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, Annotated
import operator
import random


# ════════════════════════════════════════════════════════════
# STEP 1: DEFINE STATE
# ════════════════════════════════════════════════════════════

class ResearchState(TypedDict):
    # Input
    question: str

    # Search phase (raw_results and sources ACCUMULATE across iterations)
    search_queries: list
    raw_results: Annotated[list, operator.add]   # append reducer
    sources: Annotated[list, operator.add]       # append reducer

    # Synthesis phase
    current_answer: str

    # Reflection phase
    quality_score: float
    quality_feedback: str
    score_history: Annotated[list, operator.add] # append reducer

    # Control
    attempts: int
    max_attempts: int

    # Output
    final_answer: str


# ════════════════════════════════════════════════════════════
# STEP 2: DEFINE NODES
# ════════════════════════════════════════════════════════════

def generate_queries(state: ResearchState) -> dict:
    """
    Node 1: Generate search queries for the current iteration.
    On first run: broad queries based on the question.
    On subsequent runs: targeted queries based on quality_feedback.
    """
    question = state["question"]
    feedback = state.get("quality_feedback", "")
    attempt = state["attempts"]

    if attempt == 0 or not feedback:
        # First iteration: broad coverage queries
        queries = [
            f"{question} overview and definition",
            f"{question} key concepts and mechanisms",
            f"{question} practical applications",
        ]
        print(f"\n[generate_queries] Attempt {attempt + 1}: Generated 3 broad queries")
    else:
        # Subsequent iterations: targeted gap-filling based on feedback
        queries = [
            f"{question} {feedback.lower()} examples",
            f"{question} advanced details",
        ]
        print(f"\n[generate_queries] Attempt {attempt + 1}: Generated 2 gap-filling queries")
        print(f"  Targeting: '{feedback[:60]}'")

    return {"search_queries": queries}


def search(state: ResearchState) -> dict:
    """
    Node 2: Execute searches for each query.
    In production: call web search API, vector database, etc.
    Here we simulate results using a knowledge dictionary.
    """
    queries = state["search_queries"]
    question = state["question"].lower()

    # Simulated knowledge base
    knowledge = {
        "langgraph": [
            ("LangGraph is a library for building stateful, multi-actor applications with LLMs. "
             "It extends LangChain and supports cycles, branching, and persistence.",
             "docs.langchain.com/langgraph"),
            ("LangGraph uses a StateGraph architecture where nodes are Python functions and "
             "edges define control flow. State flows through the entire graph.",
             "blog.langchain.dev/langgraph-intro"),
            ("Key LangGraph features include: conditional edges for branching, "
             "checkpointers for persistence, and built-in support for human-in-the-loop.",
             "langchain.dev/blog/langgraph-v1"),
        ],
        "agent": [
            ("AI agents are autonomous systems that perceive their environment, "
             "make decisions, and take actions to achieve goals.",
             "arxiv.org/agents-survey"),
            ("ReAct agents combine reasoning and acting: they reason about what to do, "
             "act by calling tools, then reason again based on results.",
             "arxiv.org/react-paper"),
        ],
    }

    new_results = []
    new_sources = []

    for query in queries:
        # Find relevant knowledge
        matched = False
        for keyword, facts in knowledge.items():
            if keyword in question or keyword in query.lower():
                # Add a random fact from the matching category
                fact, source = random.choice(facts)
                new_results.append(f"[Query: '{query[:40]}'] {fact}")
                new_sources.append(source)
                matched = True
                break
        if not matched:
            new_results.append(f"[Query: '{query[:40]}'] General information retrieved.")
            new_sources.append("general-knowledge.com")

    print(f"\n[search] Retrieved {len(new_results)} results across {len(queries)} queries")
    print(f"[search] Total accumulated results will be: {len(state.get('raw_results', [])) + len(new_results)}")

    # These are APPENDED to existing state via operator.add reducer
    return {
        "raw_results": new_results,
        "sources": new_sources,
    }


def synthesize(state: ResearchState) -> dict:
    """
    Node 3: Synthesize all accumulated results into a coherent answer.
    In production: call LLM with all results as context.
    """
    question = state["question"]
    all_results = state.get("raw_results", [])
    previous_answer = state.get("current_answer", "")
    attempt = state["attempts"]

    print(f"\n[synthesize] Synthesizing {len(all_results)} total results (attempt {attempt + 1})")

    # Build answer from accumulated results
    if all_results:
        result_text = "\n".join([f"  - {r[:100]}" for r in all_results])
        answer = (
            f"Answer to: '{question}'\n\n"
            f"Based on {len(all_results)} research results across {attempt + 1} search iteration(s):\n\n"
            f"{result_text}\n\n"
            f"Summary: The research reveals comprehensive information about {question}. "
            f"{'This is an improved version based on additional research.' if previous_answer else 'This represents our initial research findings.'}"
        )
    else:
        answer = f"Insufficient information found for: {question}"

    print(f"[synthesize] Draft answer: {len(answer)} characters")
    return {"current_answer": answer}


def reflect(state: ResearchState) -> dict:
    """
    Node 4: Evaluate the quality of the current answer.
    In production: use an LLM-as-judge.
    Here we simulate improving quality scores.
    """
    attempt = state["attempts"]
    result_count = len(state.get("raw_results", []))
    answer_length = len(state.get("current_answer", ""))

    # Simulate quality improvement over iterations
    # Real implementation: LLM evaluates completeness, accuracy, clarity
    base_scores = [0.45, 0.72, 0.88, 0.93]
    base = base_scores[min(attempt, len(base_scores) - 1)]
    score = min(1.0, base + random.uniform(-0.03, 0.05))

    # Generate feedback based on score
    if score < 0.6:
        feedback = "Needs more specific examples and practical applications"
    elif score < 0.8:
        feedback = "Good foundation but lacks depth in advanced concepts"
    else:
        feedback = "Comprehensive and well-structured answer"

    new_attempts = attempt + 1

    print(f"\n[reflect] Quality score: {score:.2f} (attempt {new_attempts}/{state['max_attempts']})")
    print(f"[reflect] Feedback: '{feedback}'")
    print(f"[reflect] Results accumulated: {result_count}, Answer length: {answer_length}")

    return {
        "quality_score": score,
        "quality_feedback": feedback,
        "score_history": [round(score, 2)],  # appended via reducer
        "attempts": new_attempts,
    }


def format_output(state: ResearchState) -> dict:
    """
    Node 5: Polish the final answer and add metadata.
    """
    answer = state["current_answer"]
    sources = list(dict.fromkeys(state.get("sources", [])))  # deduplicate
    scores = state.get("score_history", [])
    final_score = state.get("quality_score", 0.0)
    attempts = state["attempts"]

    # Determine confidence label
    if final_score >= 0.85:
        confidence = "High"
    elif final_score >= 0.70:
        confidence = "Medium"
    else:
        confidence = "Low (max iterations reached)"

    print(f"\n[format_output] Polishing final answer...")
    print(f"[format_output] Quality journey: {' → '.join(str(s) for s in scores)}")
    print(f"[format_output] Final confidence: {confidence}")

    final = (
        f"{answer}\n\n"
        f"{'='*50}\n"
        f"Research Quality: {confidence} ({final_score:.2f}/1.0)\n"
        f"Iterations: {attempts}\n"
        f"Score progression: {' → '.join(str(s) for s in scores)}\n"
        f"Sources consulted ({len(sources)}):\n"
        + "\n".join(f"  - {s}" for s in sources[:5])
    )

    return {"final_answer": final}


# ════════════════════════════════════════════════════════════
# STEP 3: ROUTER
# ════════════════════════════════════════════════════════════

QUALITY_THRESHOLD = 0.80

def reflect_router(state: ResearchState) -> str:
    """
    After reflect node: decide whether to loop or finish.
    Hard limit always checked first to prevent infinite loops.
    """
    if state["attempts"] >= state["max_attempts"]:
        print(f"[router] Max attempts reached ({state['max_attempts']}) → format_output")
        return "format_output"

    if state["quality_score"] >= QUALITY_THRESHOLD:
        print(f"[router] Quality {state['quality_score']:.2f} >= {QUALITY_THRESHOLD} → format_output")
        return "format_output"

    print(f"[router] Quality {state['quality_score']:.2f} < {QUALITY_THRESHOLD} → loop back")
    return "generate_queries"


# ════════════════════════════════════════════════════════════
# STEP 4: BUILD THE GRAPH
# ════════════════════════════════════════════════════════════

graph = StateGraph(ResearchState)

# Add all nodes
graph.add_node("generate_queries", generate_queries)
graph.add_node("search", search)
graph.add_node("synthesize", synthesize)
graph.add_node("reflect", reflect)
graph.add_node("format_output", format_output)

# Wire the edges
graph.add_edge(START, "generate_queries")
graph.add_edge("generate_queries", "search")
graph.add_edge("search", "synthesize")
graph.add_edge("synthesize", "reflect")
graph.add_conditional_edges("reflect", reflect_router)  # loop or exit
graph.add_edge("format_output", END)


# ════════════════════════════════════════════════════════════
# STEP 5: COMPILE WITH CHECKPOINTING
# ════════════════════════════════════════════════════════════

memory = MemorySaver()
app = graph.compile(checkpointer=memory)


# ════════════════════════════════════════════════════════════
# STEP 6: RUN WITH STREAMING
# ════════════════════════════════════════════════════════════

def run_research_agent(question: str, max_attempts: int = 3):
    """
    Run the research agent with streaming output.
    Shows each node's completion in real time.
    """
    print("=" * 65)
    print(f"RESEARCH AGENT")
    print(f"Question: '{question}'")
    print(f"Max attempts: {max_attempts}")
    print("=" * 65)

    config = {"configurable": {"thread_id": f"research-{question[:20].replace(' ', '-')}"}}

    initial_state: ResearchState = {
        "question": question,
        "search_queries": [],
        "raw_results": [],
        "sources": [],
        "current_answer": "",
        "quality_score": 0.0,
        "quality_feedback": "",
        "score_history": [],
        "attempts": 0,
        "max_attempts": max_attempts,
        "final_answer": "",
    }

    print("\n--- STREAMING PROGRESS ---\n")

    # Stream progress — each chunk shows which node just completed
    final_state = None
    for chunk in app.stream(
        initial_state,
        config=config,
        stream_mode="updates"
    ):
        for node_name in chunk.keys():
            print(f"  ✓ [{node_name}] completed")
        final_state = None  # Reset to get final state after streaming

    # Get final state from checkpointer
    final_state = app.get_state(config).values

    print("\n" + "=" * 65)
    print("FINAL ANSWER")
    print("=" * 65)
    print(final_state["final_answer"])

    return final_state


# Run the agent
run_research_agent("What is LangGraph and how does it work?", max_attempts=3)
```

---

## Running the Agent

```bash
# Basic run
python research_agent.py

# The output will show:
# - Each iteration's node completions
# - Quality scores improving
# - The reflection loop (if quality is initially low)
# - The final polished answer with sources
```

---

## Upgrading to Use Real LLMs

Replace the simulation functions with actual LLM calls:

```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

llm = ChatOpenAI(model="gpt-4o-mini")

def generate_queries(state: ResearchState) -> dict:
    prompt = f"""
    Generate 3 specific search queries to research: "{state['question']}"

    {"Previous research gap: " + state['quality_feedback'] if state.get('quality_feedback') else ""}

    Return only the queries, one per line, no numbering.
    """
    response = llm.invoke([HumanMessage(content=prompt)])
    queries = [q.strip() for q in response.content.strip().split("\n") if q.strip()]
    return {"search_queries": queries[:3]}

def synthesize(state: ResearchState) -> dict:
    results_text = "\n".join(state["raw_results"])
    prompt = f"""
    Question: {state['question']}

    Research results:
    {results_text}

    {"Previous answer to improve: " + state['current_answer'] if state.get('current_answer') else ""}

    Write a comprehensive, well-structured answer based on these results.
    """
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"current_answer": response.content}

def reflect(state: ResearchState) -> dict:
    prompt = f"""
    Question: {state['question']}
    Answer: {state['current_answer']}

    Evaluate this answer on a scale of 0.0 to 1.0.
    Consider: completeness, accuracy, clarity, practical examples.

    Respond with JSON only:
    {{"score": 0.75, "feedback": "Needs more examples"}}
    """
    import json
    response = llm.invoke([HumanMessage(content=prompt)])
    result = json.loads(response.content)
    return {
        "quality_score": result["score"],
        "quality_feedback": result["feedback"],
        "score_history": [result["score"]],
        "attempts": state["attempts"] + 1,
    }
```

---

## 📂 Navigation

**In this folder:**

| File | |
|---|---|
| [📄 Project_Guide.md](./Project_Guide.md) | Project overview and spec |
| [📄 Architecture_Blueprint.md](./Architecture_Blueprint.md) | Detailed architecture |
| 📄 **Step_by_Step.md** | ← you are here |
| [📄 Troubleshooting.md](./Troubleshooting.md) | Debug help |

⬅️ **Prev:** [Streaming and Checkpointing](../07_Streaming_and_Checkpointing/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [LangGraph vs LangChain](../LangGraph_vs_LangChain.md)
