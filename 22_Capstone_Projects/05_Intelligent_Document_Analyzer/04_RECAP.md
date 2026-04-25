# Project 5 — Recap

## What You Built

A Python CLI application that accepts any text file and runs four analysis pipelines against it: summarization, structured entity extraction, grounded question answering, and comprehension quiz generation. Each pipeline is an independent LLM API call with its own engineered prompt and output contract. Structured outputs are validated with pydantic before reaching the user.

---

## Concepts Applied

| Concept | Where it appeared |
|---|---|
| Prompt chaining | Four separate API calls, each with a focused prompt — not one monolithic call |
| Prompt specificity | Explicit output constraints in every prompt: "3 to 5 sentences", "Return ONLY valid JSON" |
| Structured output | JSON schema embedded in the prompt; model must return a matching object |
| Pydantic validation | `DocumentEntities(**data)` and `Quiz(**data)` catch schema mismatches at parse time |
| Anti-hallucination | "Only use information from the document" and the three-case Q&A rule |
| JSON cleaning | `clean_json_response()` strips markdown code fences from model output |
| Context window management | `max_chars=100_000` truncation keeps documents within safe token limits |
| Graceful degradation | Failed JSON parsing returns empty pydantic objects instead of crashing |
| `max_tokens` budgeting | Different limits per task: 300 for summary, 1500 for quiz — controls cost and prevents runaway output |
| argparse | CLI file path argument with `os.path.exists()` validation before processing |

---

## Extension Ideas

1. **Document chunking**: For very long documents (books, large codebases), split the text into overlapping chunks, summarize each chunk independently, then summarize the summaries. This is the "map-reduce" summarization pattern used in production RAG systems.

2. **Comparative analysis**: Add a `--compare file1.txt file2.txt` mode that loads two documents and asks the model to generate a structured comparison report — agreements, contradictions, and unique points per document.

3. **Answer validation with citations**: Modify the quiz prompt to require the model to quote the exact sentence from the document that supports the correct answer. Display the quote alongside the explanation so learners can verify.

---

## Job Mapping

| Role | How this project maps |
|---|---|
| AI Application Developer | Prompt chaining, structured output, and pydantic validation are the backbone of every production LLM pipeline |
| NLP Engineer | Entity extraction, structured output schemas, and hallucination mitigation are core NLP engineering skills |
| Data Engineer | Parsing unstructured text into validated, typed data structures is a daily task in data pipelines |
| Product Engineer | Understanding why LLMs hallucinate and how to reduce it is essential for building trustworthy AI products |
| Prompt Engineer | Every technique in this project — output constraints, anti-hallucination instructions, schema embedding — is core prompt engineering |

---

## 📂 Navigation

| File | |
|---|---|
| [01_MISSION.md](./01_MISSION.md) | Context and objectives |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design and diagrams |
| [03_GUIDE.md](./03_GUIDE.md) | Step-by-step build guide |
| [src/starter.py](./src/starter.py) | Starter code with TODOs |
| **04_RECAP.md** | You are here |

**Project Series:** Project 5 of 5 — Beginner Projects
⬅️ **Previous:** [04 — LLM Chatbot with Memory](../04_LLM_Chatbot_with_Memory/01_MISSION.md)
➡️ **Next:** Intermediate Projects (coming soon)
