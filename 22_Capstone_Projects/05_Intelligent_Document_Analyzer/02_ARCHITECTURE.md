# Project 5 — Architecture

## System Overview

This project is a **prompt chain pipeline** — multiple LLM API calls, each with a specific prompt and output format, wired together into a single application. The document acts as shared context across all 4 analysis tasks. Each task is a self-contained function with its own prompt and validation logic.

---

## Full System Diagram

```mermaid
flowchart TD
    A[Text File\ndocument.txt] --> B[load_document\nRead + truncate if needed]

    B --> C[Document String\nin memory as Python str]

    C --> D1[build_summary_prompt\n+ call_api]
    C --> D2[build_entity_prompt\n+ call_api]
    C --> D3[build_qa_prompt + question\n+ call_api]
    C --> D4[build_quiz_prompt\n+ call_api]

    D1 --> E1[Plain text summary\n3-5 sentences]
    D2 --> E2[clean_json_response\n+ json.loads\n+ DocumentEntities pydantic]
    D3 --> E3[Plain text answer\nwith grounding]
    D4 --> E4[clean_json_response\n+ json.loads\n+ Quiz pydantic]

    E1 --> F[Print to terminal]
    E2 --> F
    E3 --> F
    E4 --> F
```

---

## Prompt Chain Flow

```mermaid
sequenceDiagram
    participant User
    participant App as analyzer.py
    participant API as Claude API

    User->>App: Load document.txt
    App->>App: load_document (truncate if needed)

    User->>App: Choose "Summarize"
    App->>API: POST /messages\n{prompt: summary_prompt + document}
    API-->>App: Plain text summary
    App-->>User: Print summary

    User->>App: Choose "Extract Entities"
    App->>API: POST /messages\n{prompt: entity_prompt + document}
    API-->>App: JSON string
    App->>App: clean_json_response
    App->>App: json.loads + DocumentEntities(...)
    App-->>User: Print structured JSON

    User->>App: Ask a question
    App->>API: POST /messages\n{prompt: qa_prompt + document + question}
    API-->>App: Plain text answer
    App-->>User: Print answer

    User->>App: Choose "Generate Quiz"
    App->>API: POST /messages\n{prompt: quiz_prompt + document}
    API-->>App: Nested JSON string
    App->>App: clean_json_response
    App->>App: json.loads + Quiz(...)
    App-->>User: Print formatted quiz
```

---

## Structured Output Pipeline

```mermaid
flowchart LR
    A[API Response\nraw string] --> B{Contains\nmarkdown fences?}
    B -- yes --> C[clean_json_response\nExtract JSON from between backticks]
    B -- no --> D[raw_text.strip]
    C --> E[json.loads\nParse to Python dict]
    D --> E
    E --> F{Pydantic\nvalidation}
    F -- valid --> G[Return typed object\nDocumentEntities or Quiz]
    F -- invalid --> H[Log warning\nPrint raw output\nReturn safe fallback]
```

---

## Hallucination Reduction Strategy

```mermaid
flowchart TD
    Problem[LLM may use training knowledge\ninstead of document content] --> S1

    S1[Strategy 1: Explicit instruction\nOnly use information from the document] --> S2

    S2[Strategy 2: Three-case rule for Q&A\nExplicit answer / Inference / Cannot answer] --> S3

    S3[Strategy 3: Schema constraints\nEntities must be named in the document] --> S4

    S4[Strategy 4: Pydantic validation\nCatch structurally invalid outputs\nbefore they reach the user]
```

Note: These strategies reduce hallucination but cannot eliminate it. For high-stakes applications, answers should always be verified against source material.

---

## Pydantic Model Hierarchy

```mermaid
classDiagram
    class DocumentEntities {
        +people: List[str]
        +organizations: List[str]
        +dates: List[str]
        +key_topics: List[str]
    }

    class Quiz {
        +questions: List[QuizQuestion]
    }

    class QuizQuestion {
        +question: str
        +choices: List[str]
        +correct_answer: str
        +explanation: str
    }

    Quiz "1" --> "5" QuizQuestion : contains
```

---

## Component Table

| Component | File/Function | Role |
|---|---|---|
| Document Loader | `load_document()` | Reads file, truncates to context-safe length |
| Prompt Builders | `build_*_prompt()` | Construct task-specific prompts with document embedded |
| API Caller | `call_api()` | Single function for all non-streaming API calls |
| JSON Cleaner | `clean_json_response()` | Strips markdown code fences from LLM output |
| Entity Validator | `DocumentEntities` (pydantic) | Validates and types entity extraction result |
| Quiz Validator | `Quiz`, `QuizQuestion` (pydantic) | Validates nested quiz structure |
| Summary Display | `print()` | Plain text — no structure needed |
| Entity Display | `display_entities()` | Uses `model.model_dump_json(indent=2)` |
| Quiz Display | `display_quiz()` | Prints each question with choices and answer |
| Q&A Session | `run_qa_session()` | Interactive input loop |
| Main Menu | `run_analyzer()` | Orchestrates all components |

---

## Prompt Engineering Table

| Task | Anti-Hallucination Technique | Output Constraint | max_tokens |
|---|---|---|---|
| Summary | "Only information explicitly stated in the document" | "3 to 5 sentences" | 300 |
| Entity Extraction | "Do not add entities not mentioned in the document" | "Return ONLY valid JSON" + schema | 600 |
| Q&A | "Do not use knowledge outside the document", 3-case rule | Explicit fallback phrase | 400 |
| Quiz | "All questions must be based on content in the document" | "Return ONLY valid JSON" + schema | 1500 |

---

## Context Window Usage

```
Document:        ~1,000–100,000 chars = ~250–25,000 tokens
Prompt overhead: ~100–200 tokens per task
Max output:      300–1500 tokens per task

Total per call: document_tokens + ~300 overhead + max_output
Claude limit:   200,000 tokens

For a 10,000-word document (~13,000 tokens):
  Total per call ≈ 13,000 + 300 + 1,500 = ~14,800 tokens — well within limits
```

Very long documents (>100K words) would need chunking, not covered here.

---

## Tech Stack

| Layer | Tool | Why |
|---|---|---|
| Language | Python 3.9+ | f-strings, typing support |
| API client | `anthropic` SDK | Claude API calls |
| Validation | `pydantic` | Schema enforcement on LLM output |
| Parsing | `json` stdlib | Convert raw LLM string to Python dict |
| CLI | `argparse` stdlib | Accept file path as argument |

---

## Concepts Map

```mermaid
flowchart TD
    T26[Prompt Engineering] --> C1[4 task-specific prompts\nwith output constraints]
    T27[LLM APIs] --> C2[call_api function\nmessages format + max_tokens]
    T28[Structured Outputs] --> C3[JSON schema in prompt\npydantic validation]
    T25[Hallucination] --> C4[Grounding instructions\nin every prompt]
    C1 --> R[Full document analyzer\nwith 4 analysis modes]
    C2 --> R
    C3 --> R
    C4 --> R
```

---

## 📂 Navigation

| File | |
|---|---|
| [01_MISSION.md](./01_MISSION.md) | Context and objectives |
| **02_ARCHITECTURE.md** | You are here |
| [03_GUIDE.md](./03_GUIDE.md) | Step-by-step build guide |
| [src/starter.py](./src/starter.py) | Starter code with TODOs |
| [04_RECAP.md](./04_RECAP.md) | What you built and what comes next |
